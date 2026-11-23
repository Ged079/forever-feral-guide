#!/usr/bin/env python3
"""The guide's extra questions, each against the Cat build on the best-in-slot set.

weave     Pure Cat against powershifting and bear-weaving, at a few energy thresholds.
length    Cat and Hybrid DPS by fight length, and whether the self-Innervate pays at each.
aoe       Cat (single target) against Dire Bear Swipe on 1, 2, 3 and 5 targets.

    extra_sims.py [weave|length|aoe ...]     -> ../setup/extra_sims.json (merged per part)
"""
import copy, json, os, sys
import analyze as a
import sim

IT, SEED, SEED2 = 3000, sim.SEED, 100000
OUT = sim.data('extra_sims.json')
BASE_APL = json.load(open(sim.APL))

CAT, DIRE_BEAR, MAUL, SWIPE, SHIFTING_POWER, INNERVATE = 768, 9634, 9881, 9908, 1322605, 29166


def const(v):
    return {'const': {'val': str(v)}}


def aura(spell):
    return {'auraIsActive': {'auraId': {'spellId': spell}}}


def cast(spell, cond=None, notes=''):
    act = {'castSpell': {'spellId': {'spellId': spell}}}
    if cond:
        act['condition'] = cond
    return {'notes': notes, 'action': act}


def AND(*v):
    return {'and': {'vals': list(v)}}


def NOT(v):
    return {'not': {'val': v}}


def cmp(op, lhs, rhs):
    return {'cmp': {'op': op, 'lhs': lhs, 'rhs': rhs}}


ENERGY, RAGE = {'currentEnergy': {}}, {'currentRage': {}}


def sp_not_soon(sec):
    return cmp('OpGt', {'spellTimeToReady': {'spellId': {'spellId': SHIFTING_POWER}}}, const(f'{sec}s'))


def dots_safe():
    # Rip and Rake both have time left, so a few seconds out of Cat Form lets nothing fall off.
    tgt = {'type': 'CurrentTarget'}
    return AND(cmp('OpGt', {'auraRemainingTime': {'sourceUnit': tgt, 'auraId': {'spellId': 9896}}}, const('5s')),
               cmp('OpGt', {'auraRemainingTime': {'sourceUnit': tgt, 'auraId': {'spellId': 9904}}}, const('4s')))


def find(apl, prefix):
    for i, it in enumerate(apl['priorityList']):
        if it.get('notes', '').startswith(prefix):
            return i
    raise KeyError(prefix)


def powershift_apl(threshold):
    apl = copy.deepcopy(BASE_APL)
    # Cat Form cannot be recast in Cat Form, so a powershift drops the form and the row that returns to Cat recasts it.
    row = {'notes': f'Powershift below {threshold} energy', 'action': {
        'condition': AND(aura(CAT), cmp('OpLt', ENERGY, const(threshold)), sp_not_soon(1.5), NOT(aura(16870))),
        'cancelAura': {'auraId': {'spellId': CAT}}}}
    apl['priorityList'].insert(find(apl, 'Use Shred with Shredding Attacks'), row)
    return apl


def bearweave_apl(threshold):
    """Shift to Dire Bear when energy is low and the bleeds are safe, Maul once on Furor's rage, come back."""
    apl = copy.deepcopy(BASE_APL)
    pl = apl['priorityList']
    # In Dire Bear: Swipe on 15 rage, else queue Maul on 10, and stay until the queued swing spends it.
    bear = [
        cast(SWIPE, AND(aura(DIRE_BEAR), cmp('OpGe', RAGE, const(15))), 'Bear: Swipe'),
        cast(MAUL, AND(aura(DIRE_BEAR), cmp('OpGe', RAGE, const(10))), 'Bear: Maul'),
        {'notes': 'Bear: wait for the Maul swing', 'action': {
            'condition': AND(aura(DIRE_BEAR), cmp('OpGe', RAGE, const(10))), 'wait': {'duration': const('0.1s')}}},
    ]
    back = find(apl, 'Outside Cat Form')
    for r in reversed(bear):
        pl.insert(back, r)
    go = cast(DIRE_BEAR, AND(aura(CAT), cmp('OpLt', ENERGY, const(threshold)), sp_not_soon(4), dots_safe(), NOT(aura(16870))),
              f'Bear-weave below {threshold} energy')
    pl.insert(find(apl, 'Use Shred with Shredding Attacks'), go)
    return apl


def without(apl, prefix):
    apl = copy.deepcopy(apl)
    apl['priorityList'].pop(find(apl, prefix))
    return apl


def setup(talents='cat', apl=None, **kw):
    s = a.setup(talents, **kw)
    if apl is not None:
        s['player']['rotation'] = apl
    return s


def dps_of(setups, it=IT, seed=SEED):
    return [round(r[0], 1) for r in sim.runmany(setups, iterations=it, seed=seed)]


def casts(res, spell, it=IT):
    """Casts per fight: the metrics count every iteration's casts."""
    for p in res['raidMetrics']['parties'][0]['players']:
        for act in p.get('actions', []):
            if act.get('id', {}).get('spellId') == spell:
                return round(sum(t.get('casts', 0) for t in act.get('targets', [])) / it, 1)
    return 0


def weave():
    variants = [('Pure Cat', BASE_APL)]
    variants += [(f'Powershift under {t} energy', powershift_apl(t)) for t in (10, 20, 30)]
    variants += [(f'Bear-weave under {t} energy', bearweave_apl(t)) for t in (10, 20, 30)]
    out = []
    for build in ('cat', 'hybrid'):
        rs = sim.runmany([setup(build, apl) for _, apl in variants], iterations=IT, seed=SEED)
        rs2 = sim.runmany([setup(build, apl) for _, apl in variants], iterations=IT, seed=SEED2)
        for (name, _), r, r2 in zip(variants, rs, rs2):
            res = r[2]
            out.append({'build': build, 'name': name, 'dps': round(r[0], 1), 'dps2': round(r2[0], 1),
                        'shifts': {'cat': casts(res, CAT), 'bear': casts(res, DIRE_BEAR)},
                        'maul': casts(res, MAUL), 'swipe': casts(res, SWIPE)})
    return out


LENGTHS = [60, 90, 120, 180, 240, 300, 420]


def length():
    out = []
    no_inn = without(BASE_APL, 'Innervate when mana is low')
    for build in ('cat', 'hybrid'):
        rs = sim.runmany([setup(build, BASE_APL, duration=d) for d in LENGTHS], iterations=IT, seed=SEED)
        rn = sim.runmany([setup(build, no_inn, duration=d) for d in LENGTHS], iterations=IT, seed=SEED)
        for d, r, n in zip(LENGTHS, rs, rn):
            out.append({'build': build, 'duration': d, 'dps': round(r[0], 1), 'noInnervate': round(n[0], 1),
                        'shiftingPower': casts(r[2], SHIFTING_POWER), 'innervate': casts(r[2], INNERVATE)})
    return out


def swipe_apl():
    return {'type': 'TypeAPL',
            'prepullActions': [{'action': {'castSpell': {'spellId': {'spellId': DIRE_BEAR}}}, 'doAtValue': const('-1.6s')}],
            'priorityList': [
                {'action': {'condition': cmp('OpGt', {'unitDistance': {}}, const(5)), 'move': {'rangeFromTarget': const(5)}}},
                {'action': {'autocastOtherCooldowns': {}}},
                cast(SWIPE, cmp('OpGe', RAGE, const(15)), 'Swipe'),
                cast(MAUL, cmp('OpGe', RAGE, const(40)), 'Maul with spare rage'),
            ]}


def aoe():
    out = []
    for n in (1, 2, 3, 5):
        cat = setup('cat', BASE_APL)
        bear = setup('cat', swipe_apl())
        for s in (cat, bear):
            t0 = s['encounter']['targets'][0]
            s['encounter']['targets'] = [copy.deepcopy(t0) for _ in range(n)]
        rc, rb = sim.runmany([cat, bear], iterations=IT, seed=SEED)
        out.append({'targets': n, 'cat': round(rc[0], 1), 'bearSwipe': round(rb[0], 1)})
    return out


if __name__ == '__main__':
    parts = sys.argv[1:] or ['weave', 'length', 'aoe']
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for p in parts:
        res[p] = globals()[p]()
        print(p, json.dumps(res[p], indent=1))
        json.dump(res, open(OUT, 'w'), indent=1)
