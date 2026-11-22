#!/usr/bin/env python3
"""Tune the Adaptive Cat APL for one talent build.

1. Knobs: coordinate descent over the APL's numeric variables (each value screened at SCREEN iterations,
   a gain kept only if it holds at CONFIRM on another seed), until a full pass changes nothing.
2. Variants: structural edits (drop / move priority entries), each confirmed the same way.
3. Robustness: the final APL against the original at 90/180/300 s and at slow reactions.

    tune.py NAME TALENTS
"""
import copy, json, os, sys
import analyze as a
import sim

SCREEN, CONFIRM, SEED2 = 2000, 8000, 700000
MARGIN = 0.8

KNOBS = {
    'Shifting Power energy ceiling': [20, 30, 40, 45, 50, 53, 56, 60, 65, 70, 80],
    'Rip target CP': [3, 4, 5],
    'Preferred Rip CP with zero or two Blood Frenzy points': [4, 5],
    'Rip minimum fight left': ['4s', '6s', '8s', '10s', '12s', '15s'],
    'Bite minimum CP without Blood Frenzy': [3, 4, 5],
    'Bite minimum CP with Blood Frenzy': [3, 4, 5],
    'Bite energy target': [35, 45, 55, 65, 75, 85, 100],
    'Reduced Bite energy target': [35, 45, 50, 60, 70, 80],
    'Bite energy target with Clearcasting': [0, 25, 35, 45, 55, 65],
    'Bite minimum Rip remaining without Blood Frenzy': ['1s', '2s', '3s', '4s', '5s', '6s', '8s'],
    'Bite minimum Rip remaining with Blood Frenzy': ['1s', '2s', '3s', '4s', '5s', '6s', '8s'],
    'Paid-builder energy threshold': [40, 50, 60, 70, 80],
    'Paid-builder pooling CP': [2, 3, 4, 5],
    'Paid-builder pooling CP with two Blood Frenzy points': [2, 3, 4, 5],
    'Fight-end Bite CP': [3, 4, 5],
}

BASE_APL = json.load(open(sim.APL))


def get(apl, name):
    for v in apl['valueVariables']:
        if v['name'] == name:
            return v['value']['const']['val']


def put(apl, name, val):
    apl = copy.deepcopy(apl)
    for v in apl['valueVariables']:
        if v['name'] == name:
            v['value']['const']['val'] = str(val)
    return apl


def setup(talents, apl, **kw):
    s = a.setup(talents, **kw)
    s['player']['rotation'] = apl
    return s


def dps(talents, apls, it, seed=sim.SEED, **kw):
    return [r[0] for r in sim.runmany([setup(talents, x, **kw) for x in apls], iterations=it, seed=seed)]


def confirmed(talents, new, old):
    n, o = dps(talents, [new, old], CONFIRM, SEED2)
    return n - o, n, o


# ---- structural variants: functions APL -> APL ----
def find(apl, text):
    return next(i for i, x in enumerate(apl['priorityList']) if text in x.get('notes', ''))


def drop(text):
    def f(apl):
        apl = copy.deepcopy(apl); del apl['priorityList'][find(apl, text)]; return apl
    return f


def move_before(text, before):
    def f(apl):
        apl = copy.deepcopy(apl); pl = apl['priorityList']
        x = pl.pop(find(apl, text)); pl.insert(find(apl, before), x); return apl
    return f


VARIANTS = {
    'no mid-fight Bite': drop('Bite while Rip has time left'),
    'no Rake': drop('Refresh Rake'),
    'no Clearcasting Shred step': drop('Spend Clearcasting on Shred'),
    'no Innervate': drop('Innervate when mana is low'),
    'Rip before Bite': move_before('Refresh Rip', 'Bite while Rip has time left'),
    'Rake before Rip': move_before('Refresh Rake', 'Refresh Rip'),
    'Shifting Power first': move_before('Shifting Power is ready', 'Bite before this target dies with enough'),
    'Shifting Power after builders': move_before('Shifting Power is ready', 'Innervate when mana is low'),
    'Clearcasting Shred before Bite': move_before('Spend Clearcasting on Shred', 'Bite while Rip has time left'),
}


def tune(name, talents):
    apl = BASE_APL
    log = []
    cur = dps(talents, [apl], SCREEN)[0]
    print(f'[{name}] start {cur:.1f}', flush=True)
    changed = True
    passes = 0
    while changed and passes < 4:
        changed, passes = False, passes + 1
        for k, vals in KNOBS.items():
            now = get(apl, k)
            cands = [v for v in vals if str(v) != now]
            res = dps(talents, [put(apl, k, v) for v in cands], SCREEN)
            best = max(zip(res, cands), key=lambda x: x[0])
            if best[0] - cur > MARGIN:
                new = put(apl, k, best[1])
                g, n, o = confirmed(talents, new, apl)
                if g > MARGIN * 0.5:
                    print(f'[{name}] {k}: {now} → {best[1]}  +{g:.1f} (confirm {o:.1f} → {n:.1f})', flush=True)
                    log.append({'knob': k, 'from': now, 'to': str(best[1]), 'gain': round(g, 1)})
                    apl, cur, changed = new, dps(talents, [new], SCREEN)[0], True
    vlog = []
    for vn, f in VARIANTS.items():
        try:
            v = f(apl)
        except StopIteration:
            continue
        g, n, o = confirmed(talents, v, apl)
        vlog.append({'variant': vn, 'gain': round(g, 1)})
        print(f'[{name}] variant {vn}: {g:+.1f}', flush=True)
    best = max(vlog, key=lambda x: x['gain'])
    if best['gain'] > MARGIN:
        apl = VARIANTS[best['variant']](apl)
        log.append({'variant': best['variant'], 'gain': best['gain']})
        print(f'[{name}] kept variant {best["variant"]}', flush=True)
    # robustness against the untouched APL
    rob = {}
    for L in (90, 180, 300):
        n, o = dps(talents, [apl, BASE_APL], CONFIRM, SEED2, duration=L)
        rob[f'{L}s'] = [round(o, 1), round(n, 1)]
    slow = []
    for x in (apl, BASE_APL):
        s = setup(talents, x); s['player']['reactionTimeMs'] = 300; s['player']['reactionTimeMaxMs'] = 600
        slow.append(sim.run(s, iterations=CONFIRM, seed=SEED2)[0])
    rob['slow reactions'] = [round(slow[1], 1), round(slow[0], 1)]
    print(f'[{name}] robustness (original → tuned): {rob}', flush=True)
    os.makedirs(sim.data('tune'), exist_ok=True)
    json.dump(apl, open(sim.data(f'tune/{name}.apl.json'), 'w'), indent=1)
    return {'name': name, 'talents': talents, 'log': log, 'variants': vlog, 'robust': rob}


if __name__ == '__main__':
    name, talents = sys.argv[1], sys.argv[2]
    r = tune(name, a.TALENTS.get(talents, talents))
    json.dump(r, open(sim.data(f'tune/{name}.json'), 'w'), indent=1)
