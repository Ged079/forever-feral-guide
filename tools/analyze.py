#!/usr/bin/env python3
"""Every Feral Cat sim the guide needs, written to results.json.

Setup: setup/defaults.json (pre-raid BiS, full raid buffs and consumables, level 63 Dragonkin boss, 150-350 ms
reaction) with Kings as the only blessing, the sim's Adaptive Cat APL, 3000 iterations on seed 1.
A thing's worth = DPS with it - DPS without it (leave-one-out), everything else on.
"""
import copy, json, os, sys
import sim

DB = json.load(open(os.path.join(sim.FOREVER, 'assets/database/db.json')))
TREES = json.load(open(os.path.join(sim.FOREVER, 'ui/sim/talents/trees/druid.json')))
CONS = {c['id']: c for c in DB['consumables']}
TALENTS = {  # found by search.py (hill climb from the presets and a random start)
    'cat': '050022-55000032023012125001-055',
    'hybrid': '050022-52000332023110125011-055',
}
PRESETS = {  # the sim's own presets, for comparison
    'cat': '050021-53200032123012125001-055',
    'hybrid': '050012-50230302123110125011-055',
}
LENGTHS = [90, 180, 300]
NSTATS = 39


FACTION_RACE = {'alliance': 'RaceNightElf', 'horde': 'RaceTauren'}
GEAR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../setup/gear')


def setup(talents='cat', duration=180, faction='alliance'):
    b = sim.base()
    p = b['player']
    gp = os.path.join(GEAR_DIR, f'cat_{faction}.items.json')
    if faction and os.path.exists(gp):
        p['equipment']['items'] = json.load(open(gp))
        p['race'] = FACTION_RACE[faction]
    p['buffs'] = {'greaterBlessingOfKings': True}  # one blessing per player, as on Forever
    p['talentsString'] = TALENTS.get(talents, talents)
    b['encounter']['duration'] = duration
    b['raidBuffs'].pop('leaderOfThePack', None)  # the cat brings its own
    return b


def dps(s, **kw):
    return sim.run(s, **kw)[0]


# ---------- talents ----------
def tree_order(tree):
    return sorted(tree['talents'], key=lambda t: (t['location']['rowIdx'], t['location']['colIdx']))


def parse_talents(s):
    out = []
    for tree, part in zip(TREES, s.split('-')):
        tal = tree_order(tree)
        pts = [int(c) for c in part] + [0] * (len(tal) - len(part))
        out.append(pts)
    return out


def talent_string(pts):
    return '-'.join(''.join(map(str, p)).rstrip('0') for p in pts).rstrip('-')


def talent_list(s):
    pts = parse_talents(s)
    res = []
    for ti, tree in enumerate(TREES):
        for i, t in enumerate(tree_order(tree)):
            if pts[ti][i]:
                res.append((ti, i, t['fancyName'], pts[ti][i], t['maxPoints'], t['spellId']))
    return res


def talent_values(build):
    base_s = TALENTS[build]
    base = dps(setup(base_s))
    pts = parse_talents(base_s)
    out = []
    for ti, i, name, n, mx, spell in talent_list(base_s):
        p0 = copy.deepcopy(pts); p0[ti][i] = 0
        all_pts = base - dps(setup(talent_string(p0)))
        last = None
        if n > 1:
            p1 = copy.deepcopy(pts); p1[ti][i] = n - 1
            last = base - dps(setup(talent_string(p1)))
        out.append({'name': name, 'tree': TREES[ti]['name'], 'points': n, 'max': mx, 'spell': spell,
                    'all': round(all_pts, 1), 'last': None if last is None else round(last, 1)})
    return base, out


# ---------- consumables ----------
SLOTS = ['flaskId', 'foodId', 'conjuredId', 'explosiveId', 'mhImbueId', 'resourcePotId', 'offensivePotId']


def consumable_values(build='cat'):
    s = setup(build)
    base = dps(s)
    c = s['player']['consumables']
    out = []
    for slot in SLOTS:
        if slot in c:
            t = copy.deepcopy(s); del t['player']['consumables'][slot]
            if slot == 'mhImbueId':
                t['player']['consumables'].pop('swapMhImbueId', None)
            out.append({'id': c[slot], 'slot': slot, 'v': round(base - dps(t), 1)})
    for lst in ['extraIds', 'elixirIds']:
        for x in c.get(lst, []):
            t = copy.deepcopy(s); t['player']['consumables'][lst] = [y for y in c[lst] if y != x]
            out.append({'id': x, 'slot': lst, 'v': round(base - dps(t), 1)})
    for o in out:
        o['name'] = CONS[o['id']]['name']
    # swaps: (slot, current id, replacement id)
    swaps = [
        ('flaskId', 274274, 274273), ('flaskId', 274274, 274275), ('flaskId', 274274, 274276),
        ('foodId', 250072, 20452), ('foodId', 250072, 13934),
        ('mhImbueId', 12643, 18262),
        ('offensivePotId', 13442, 250943),
        ('elixirIds', 250328, 13452), ('elixirIds', 250328, 250350),
        ('elixirIds', 250351, 13453), ('elixirIds', 250351, 9206),
        ('extraIds', 12460, 12820),
        ('explosiveId', 260817, 18641),
        ('offensivePotId', 13442, 250942),
        ('foodId', 250072, 250070),
    ]
    alts = []
    for slot, cur, new in swaps:
        if new not in CONS:
            continue
        t = copy.deepcopy(s); tc = t['player']['consumables']
        if isinstance(tc.get(slot), list):
            tc[slot] = [new if y == cur else y for y in tc[slot]]
        else:
            tc[slot] = new
        alts.append({'slot': slot, 'from': CONS[cur]['name'], 'to': CONS[new]['name'], 'toId': new,
                     'v': round(dps(t) - base, 1)})
    # adds: does it stack with the full set, and what is it worth on top?
    adds = []
    for lst, new in [('extraIds', 12451), ('extraIds', 12820), ('extraIds', 246948), ('elixirIds', 13452),
                     ('elixirIds', 250350), ('elixirIds', 9206), ('extraIds', 10309), ('extraIds', 10310)]:
        t = copy.deepcopy(s); t['player']['consumables'].setdefault(lst, []).append(new)
        v = dps(t) - base
        adds.append({'name': CONS[new]['name'], 'id': new, 'v': round(v, 1), 'stacks': v != 0.0})
    return base, out, alts, adds


# ---------- buffs ----------
def buff_values():
    s = setup()
    base = dps(s)
    out = []
    for k in list(s['raidBuffs']):
        t = copy.deepcopy(s); del t['raidBuffs'][k]
        out.append({'kind': 'raid', 'key': k, 'v': round(base - dps(t), 1)})
    t = copy.deepcopy(s); t['player']['buffs'] = {}
    out.append({'kind': 'blessing', 'key': 'greaterBlessingOfKings', 'v': round(base - dps(t), 1)})
    for k in list(s['debuffs']):
        t = copy.deepcopy(s); del t['debuffs'][k]
        out.append({'kind': 'debuff', 'key': k, 'v': round(base - dps(t), 1)})
    # armor debuffs overlap, so also the group
    t = copy.deepcopy(s)
    for k in ['sunderArmor', 'exposeArmor', 'faerieFire', 'curseOfRecklessness']:
        t['debuffs'].pop(k, None)
    out.append({'kind': 'group', 'key': 'allArmorDebuffs', 'v': round(base - dps(t), 1)})
    none = dps(t)
    for k in ['sunderArmor', 'exposeArmor', 'faerieFire', 'curseOfRecklessness']:
        u = copy.deepcopy(t); u['debuffs'][k] = True
        out.append({'kind': 'armorAlone', 'key': k, 'v': round(dps(u) - none, 1)})
    u = copy.deepcopy(s); u['player']['feralCatDruid']['options']['assumeBleedActive'] = False
    out.append({'kind': 'assumption', 'key': 'otherBleed', 'v': round(base - dps(u), 1)})
    # totals
    t = copy.deepcopy(s); t['player']['consumables'] = {}
    no_cons = dps(t)
    t = copy.deepcopy(s); t['raidBuffs'] = {}; t['debuffs'] = {}; t['player']['buffs'] = {}
    no_buffs = dps(t)
    return base, out, {'base': round(base, 1), 'consumables': round(base - no_cons, 1), 'buffs': round(base - no_buffs, 1)}


# ---------- races ----------
RACES = ['RaceNightElf', 'RaceTauren', 'RaceHighOrderSkyborne', 'RaceWindshaperSkyborne']


def race_values():
    out = {}
    for build in TALENTS:
        for r in RACES:
            s = setup(build, faction='horde' if r in ('RaceTauren', 'RaceWindshaperSkyborne') else 'alliance'); s['player']['race'] = r
            out.setdefault(r, {})[build] = round(dps(s), 1)
    return out


# ---------- stats ----------
STAT = {'Strength': 0, 'Agility': 1, 'Attack Power': 14, 'Hit Rating': 17, 'Crit Rating': 18, 'Haste Rating': 19,
        'Armor Penetration': 20, 'Expertise Rating': 21}
STEP = {'Strength': 40, 'Agility': 40, 'Attack Power': 80, 'Hit Rating': 20, 'Crit Rating': 28, 'Haste Rating': 20,
        'Armor Penetration': 100, 'Expertise Rating': 20}


def with_bonus(s, idx, amt):
    t = copy.deepcopy(s)
    st = [0] * NSTATS
    st[idx] = amt
    t['player']['bonusStats'] = {'stats': st}
    return t


def stat_weights(build='cat', it=20000):
    s = setup(build)
    base = dps(s, iterations=it)
    out = {}
    for n, idx in STAT.items():
        up = dps(with_bonus(s, idx, STEP[n]), iterations=it)
        down = dps(with_bonus(s, idx, -STEP[n]), iterations=it)
        out[n] = round((up - down) / (2 * STEP[n]), 4)  # DPS per point, central difference
    return base, out


def hit_curve(build='cat', it=10000):
    s = setup(build)
    return [(h, round(dps(with_bonus(s, 17, h), iterations=it), 1)) for h in range(-80, 81, 10)]


def gear_hit():
    """Hit rating the gear gives, so the curve can be read as total hit."""
    items = {i['id']: i for i in DB['items']}
    ench = {e['effectId']: e for e in DB['enchants']}
    s = setup()
    tot = [0] * NSTATS
    for it in s['player']['equipment']['items']:
        if not it.get('id'):
            continue
        x = items.get(it['id'])
        if x:
            for k, v in (x.get('scalingOptions', {}).get('0', {}).get('stats', {}) or {}).items():
                tot[int(k)] += v
        e = ench.get(it.get('enchant'))
        if e:
            for k, v in enumerate(e.get('stats', [])):
                tot[k] += v
    return {n: tot[i] for n, i in STAT.items()}


def main():
    R = {'meta': {'iterations': sim.ITER, 'seed': sim.SEED}}
    which = sys.argv[1:] or ['builds', 'talents', 'cons', 'buffs', 'races', 'stats', 'hit']
    if os.path.exists('../setup/results.json'):
        R = json.load(open('../setup/results.json'))
    if 'builds' in which:
        R['builds'] = {b: {L: round(dps(setup(b, L)), 1) for L in LENGTHS} for b in TALENTS}
        R['presets'] = {b: {L: round(dps(setup(PRESETS[b], L)), 1) for L in LENGTHS} for b in PRESETS}
        print('builds', R['builds'], flush=True)
    if 'talents' in which:
        R['talents'] = {}
        for b in TALENTS:
            base, vals = talent_values(b)
            R['talents'][b] = vals
            print('talents', b, base, flush=True)
    if 'cons' in which:
        R['consumables'] = {}
        for b in TALENTS:
            base, out, alts, adds = consumable_values(b)
            R['consumables'][b] = {'base': base, 'list': out, 'alts': alts, 'adds': adds}
        print('cons done', flush=True)
    if 'buffs' in which:
        base, out, totals = buff_values()
        R['buffs'] = {'list': out, 'totals': totals}
        print('buffs', totals, flush=True)
    if 'races' in which:
        R['races'] = race_values()
        print('races', R['races'], flush=True)
    if 'stats' in which:
        R['stats'] = {}
        for b in TALENTS:
            base, w = stat_weights(b)
            R['stats'][b] = {'base': base, 'perPoint': w}
            print('stats', b, w, flush=True)
    if 'hit' in which:
        R['gear'] = gear_hit()
        R['hit'] = {b: hit_curve(b) for b in TALENTS}
        print('hit', R['gear'], flush=True)
    json.dump(R, open('../setup/results.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
