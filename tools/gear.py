#!/usr/bin/env python3
"""Pre-raid gear search for Feral Cat in WoWSims Forever.

Candidates: Phase 1 items a druid can wear (cloth/leather, druid weapons, idols), level 60 or lower, minus raid
loot (Molten Core, Onyxia, ZG, BWL, AQ, Naxx), raid reputation (The Watchers), PvP gear and Forever items the game
files give no source for. Random-suffix items are expanded per suffix. Faction: 'horde' or 'alliance'.

Search: from the start set, every single-slot swap among each slot's candidates is simmed at SCREEN iterations;
the best is kept only if it wins at CONFIRM iterations on another seed; repeat. Then every two-slot combination of
each slot's top 3 is tried, then weapon enchants. Writes gear/<name>.json.

    gear.py NAME FACTION TALENTS [START_GEAR_JSON]
"""
import copy, itertools, json, os, sys, time
import analyze as a
import sim

SCREEN, CONFIRM, SEED2 = 1000, 6000, 900000
MARGIN = 1.0
PER_SLOT = 14          # EP prefilter, non-weapon slots
PER_SLOT_EFFECT = 6    # plus this many items with use/proc effects or set bonuses (EP can't see those)
PER_WEAPON = 30

DB = a.DB
ITEMS = {i['id']: i for i in DB['items']}
SUFFIX = {s['id']: s for s in DB['randomSuffixes']}
ZONES = {z['id']: z['name'] for z in DB['zones']}
RAID_ZONES = {'Molten Core', "Onyxia's Lair", "Zul'Gurub", 'Blackwing Lair', "Ahn'Qiraj", "Ruins of Ahn'Qiraj",
              'Naxxramas', "Temple of Ahn'Qiraj"}
WATCHERS = 2819
RAID_QUESTS = {7490, 7491, 7495, 7496}  # Onyxia head turn-ins: the rewards need a raid kill
SLOTS = ['head', 'neck', 'shoulder', 'back', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet',
         'finger1', 'finger2', 'trinket1', 'trinket2', 'main_hand', 'off_hand', 'ranged']
TYPE_OF = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 11, 12: 12, 13: 12}
DRUID_WEAPONS = {2, 3, 4, 6, 8}  # dagger, fist, mace, polearm, staff
TWO_HAND_OK = {4, 6, 8}
WEAPON_ENCHANTS_2H = [2646, 1896, 8215, 7940]   # 2H Agility, Superior Impact, 2H Strength, Grand Crusader
WEAPON_ENCHANTS_1H = [2564, 7940, 1900, 2563, 1897]  # Agility, Grand Crusader, Crusader, Strength, Superior Striking

W = json.load(open(sim.data('extra_weights.json')))
EP = {0: 0.658, 1: 0.74, 14: 0.272, 16: 0.27, 17: 0.45, 18: 0.575, 19: 0.30, 20: 0.09, 21: 0.53,
      3: W['Intellect'], 13: W['Spirit'], 31: W['MP5'], 2: 0.002}
WEAPON_DPS = W['Weapon DPS']


def faction_ok(it, faction):
    want = {'alliance': 1, 'horde': 2}[faction]
    if it.get('factionRestriction') and it['factionRestriction'] != want:
        return False
    fs = set()
    for s in it.get('sources', []):
        v = next(iter(s.values())) or {}
        fs.add(v.get('faction') or v.get('factionId') or 0)
    return not fs or 0 in fs or want in fs


def allowed_source(it):
    srcs = it.get('sources', [])
    if not srcs:
        return it['id'] < 200000  # classic world drops; new Forever items with no source are left out
    for s in srcs:
        k, v = next(iter(s.items()))
        v = v or {}
        if k == 'pvp':
            continue
        if k == 'rep' and v.get('repFactionId') == WATCHERS:
            continue
        if k == 'quest' and v.get('id') in RAID_QUESTS:
            continue
        if k == 'drop' and ZONES.get(v.get('zoneId')) in RAID_ZONES:
            continue
        return True
    return False


def stats_of(it, suffix=None):
    st = {int(k): v for k, v in it['scalingOptions'].get('0', {}).get('stats', {}).items()}
    if suffix:
        rpp = it['scalingOptions'].get('0', {}).get('randPropPoints', 0)
        for k, v in enumerate(SUFFIX[suffix].get('stats', [])):
            if v:
                st[k] = st.get(k, 0) + int(v * rpp / 10000 + 0.5)  # as the sim rounds it
    ps = it.get('pseudoStats') or []
    if len(ps) > 14 and ps[14]:
        st[18] = st.get(18, 0) + ps[14] * 14  # "+1% critical strike" is a pseudo stat; 14 rating is 1%
    return st


def ep(it, suffix=None):
    v = sum(EP.get(k, 0) * x for k, x in stats_of(it, suffix).items())
    if it.get('type') == 13:
        v += WEAPON_DPS * it['scalingOptions'].get('0', {}).get('unroundedDps', 0)
    return v


def wearable(it):
    if it.get('phase', 1) > 1 or it.get('reqLvl', 0) > 60:
        return False
    if it.get('classAllowlist') and 11 not in it['classAllowlist']:  # 11 = Class_ClassDruid
        return False
    t = it.get('type')
    if t in (1, 3, 4, 5, 6, 7, 8, 9, 10) and it.get('armorType', 0) not in (0, 1, 2):
        return False
    if t == 13:
        wt, ht = it.get('weaponType'), it.get('handType')
        if wt == 5:
            return True  # held in off-hand
        if wt not in DRUID_WEAPONS:
            return False
        if ht == 4 and wt not in TWO_HAND_OK:
            return False
        return ht in (1, 2, 4)
    if t == 14:
        return it.get('rangedWeaponType') == 6
    return t in range(1, 13)


def candidates(faction):
    pools = {s: [] for s in SLOTS}
    for it in DB['items']:
        if not (wearable(it) and allowed_source(it) and faction_ok(it, faction)):
            continue
        sufs = it.get('randomSuffixOptions') or [None]
        for suf in sufs:
            if suf is not None and suf not in SUFFIX:
                continue
            c = {'id': it['id'], 'suffix': suf, 'ep': ep(it, suf), 'special': bool(it.get('itemEffects') or it.get('setId') or it.get('pseudoStats')),
                 'pseudo': bool(it.get('pseudoStats'))}
            t = it.get('type')
            if t == 13:
                pools['off_hand' if it.get('weaponType') == 5 else 'main_hand'].append(c)
            elif t == 14:
                pools['ranged'].append(c)
            else:
                for i, s in enumerate(SLOTS[:14]):
                    if TYPE_OF[i] == t:
                        pools[s].append(c)
    out = {}
    for s, lst in pools.items():
        lst.sort(key=lambda c: -c['ep'])
        # one entry per item: its best suffix
        seen, sigs, uniq = set(), set(), []
        for c in lst:
            it = ITEMS[c['id']]
            sig = (tuple(sorted(stats_of(it, c['suffix']).items())), it['scalingOptions'].get('0', {}).get('unroundedDps'),
                   it.get('weaponType'), it.get('handType'))
            if c['id'] in seen or (sig in sigs and not c['special']):
                continue  # same item, or identical stats to one already listed
            seen.add(c['id']); sigs.add(sig); uniq.append(c)
        n = PER_WEAPON if s == 'main_hand' else PER_SLOT
        top = uniq[:n]
        top += [c for c in uniq[n:] if c['special']][:PER_SLOT_EFFECT]
        top += [c for c in uniq[n:] if c.get('pseudo') and c not in top]  # hidden equip stats: always sim them
        out[s] = top
    return out


def gear_of(setup):
    return setup['player']['equipment']['items']


def with_item(setup, slot, c, enchant=None):
    t = copy.deepcopy(setup)
    items = gear_of(t)
    i = SLOTS.index(slot)
    old = items[i] if i < len(items) else {}
    spec = {'id': c['id']}
    if c.get('suffix'):
        spec['randomSuffix'] = c['suffix']
    ench = enchant if enchant is not None else old.get('enchant')
    if slot == 'main_hand':
        ht = ITEMS[c['id']].get('handType')
        if enchant is None:
            ench = WEAPON_ENCHANTS_2H[0] if ht == 4 else WEAPON_ENCHANTS_1H[0]
        if ht == 4 and len(items) > 15:
            items[15] = {}
    if ench:
        spec['enchant'] = ench
    while len(items) <= i:
        items.append({})
    items[i] = spec
    return t


def legal(setup):
    items = gear_of(setup)
    ids = [x.get('id') for x in items]
    for a_, b_ in ((10, 11), (12, 13)):
        if ids[a_] and ids[a_] == ids[b_] and ITEMS[ids[a_]].get('unique'):
            return False
    mh = ITEMS.get(ids[14]) if len(ids) > 14 and ids[14] else None
    if mh and mh.get('handType') == 4 and len(ids) > 15 and ids[15]:
        return False
    return True


def swaps(setup, pools):
    cur = gear_of(setup)
    for s in SLOTS:
        i = SLOTS.index(s)
        now = cur[i] if i < len(cur) else {}
        for c in pools[s]:
            if c['id'] == now.get('id') and (c.get('suffix') or 0) == (now.get('randomSuffix') or 0):
                continue
            if s == 'off_hand' and ITEMS.get(cur[14].get('id'), {}).get('handType') == 4:
                continue
            t = with_item(setup, s, c)
            if legal(t):
                yield f"{s}: {ITEMS[c['id']]['name']}", t


def dpss(setups, it, seed=sim.SEED):
    return [r[0] for r in sim.runmany(setups, iterations=it, seed=seed)]


def describe(setup):
    out = []
    for s, x in zip(SLOTS, gear_of(setup)):
        if x.get('id'):
            n = ITEMS[x['id']]['name']
            if x.get('randomSuffix'):
                n += ' ' + SUFFIX[x['randomSuffix']]['name']
            out.append({'slot': s, 'id': x['id'], 'suffix': x.get('randomSuffix'), 'enchant': x.get('enchant'), 'name': n})
    return out


def search(name, faction, talents, start=None):
    race = {'horde': 'RaceTauren', 'alliance': 'RaceNightElf'}[faction]
    setup = a.setup(talents)
    setup['player']['race'] = race
    if start:
        setup['player']['equipment']['items'] = json.load(open(start))
    pools = candidates(faction)
    print(f'[{name}] candidates per slot:', {s: len(v) for s, v in pools.items()}, flush=True)
    # drop start items the rules exclude (raid loot etc.): swap them for the slot's best EP pick first
    for i, s in enumerate(SLOTS):
        x = gear_of(setup)[i] if i < len(gear_of(setup)) else {}
        if x.get('id') and not any(c['id'] == x['id'] for c in pools[s]):
            it = ITEMS[x['id']]
            if not (allowed_source(it) and faction_ok(it, faction)):
                print(f'[{name}] start item not allowed: {it["name"]} ({s})', flush=True)
                setup = next(t for t in (with_item(setup, s, c) for c in pools[s]) if legal(t))
    cur = dpss([setup], SCREEN)[0]
    log = [{'move': 'start', 'dps': round(cur, 1)}]
    print(f'[{name}] start {cur:.1f}', flush=True)
    while True:
        t0 = time.time()
        cand = list(swaps(setup, pools))
        vals = dpss([t for _, t in cand], SCREEN)
        ranked = sorted(zip(vals, range(len(cand))), key=lambda x: -x[0])
        moved = False
        for v, k in ranked[:4]:
            if v - cur <= MARGIN:
                break
            new, old = dpss([cand[k][1], setup], CONFIRM, SEED2)
            if new - old > MARGIN * 0.5:
                setup = cand[k][1]
                cur = dpss([setup], SCREEN)[0]
                log.append({'move': cand[k][0], 'gain': round(new - old, 1)})
                print(f'[{name}] {cand[k][0]}  +{new - old:.1f}  ({len(cand)} swaps, {time.time() - t0:.0f}s)', flush=True)
                moved = True
                break
        if not moved:
            break
    # per-slot top 3 from the last screen, then every two-slot pair
    by_slot = {}
    for v, k in ranked:
        s = cand[k][0].split(':')[0]
        by_slot.setdefault(s, [])
        if len(by_slot[s]) < 3:
            by_slot[s].append(k)
    pairs = []
    for s1, s2 in itertools.combinations(by_slot, 2):
        for k1 in by_slot[s1]:
            for k2 in by_slot[s2]:
                t = copy.deepcopy(cand[k1][1])
                i2 = SLOTS.index(s2)
                gear_of(t)[i2] = gear_of(cand[k2][1])[i2]
                if s2 == 'main_hand' and ITEMS[gear_of(t)[i2]['id']].get('handType') == 4:
                    gear_of(t)[15] = {}
                if legal(t):
                    pairs.append((f'{cand[k1][0]} + {cand[k2][0]}', t))
    if pairs:
        pv = dpss([t for _, t in pairs], SCREEN)
        best = max(zip(pv, range(len(pairs))), key=lambda x: x[0])
        print(f'[{name}] {len(pairs)} pairs, best screen {best[0]:.1f} vs {cur:.1f}', flush=True)
        if best[0] - cur > MARGIN:
            new, old = dpss([pairs[best[1]][1], setup], CONFIRM, SEED2)
            if new - old > MARGIN * 0.5:
                setup = pairs[best[1]][1]
                log.append({'move': pairs[best[1]][0], 'gain': round(new - old, 1)})
                print(f'[{name}] pair {pairs[best[1]][0]} +{new - old:.1f}', flush=True)
    # weapon enchant
    mh = gear_of(setup)[14]
    ht = ITEMS[mh['id']].get('handType')
    opts = WEAPON_ENCHANTS_2H if ht == 4 else WEAPON_ENCHANTS_1H
    es = []
    for e in opts:
        t = copy.deepcopy(setup); gear_of(t)[14]['enchant'] = e; es.append(t)
    ev = dpss(es, CONFIRM, SEED2)
    enchants = {next(x['name'] for x in DB['enchants'] if x['effectId'] == e): round(v, 1) for e, v in zip(opts, ev)}
    setup = es[max(range(len(ev)), key=lambda i: ev[i])]
    print(f'[{name}] weapon enchants: {enchants}', flush=True)
    final = dpss([setup], CONFIRM, SEED2)[0]
    # runners-up per slot for the page
    alts = {}
    for v, k in ranked:
        s = cand[k][0].split(':')[0]
        alts.setdefault(s, [])
        if len(alts[s]) < 3:
            alts[s].append({'name': cand[k][0].split(': ', 1)[1], 'id': gear_of(cand[k][1])[SLOTS.index(s)]['id'],
                            'delta': round(v - cur, 1)})
    res = {'name': name, 'faction': faction, 'race': race, 'talents': talents, 'dps': round(final, 1), 'log': log,
           'gear': describe(setup), 'items': gear_of(setup), 'enchants': enchants, 'alternatives': alts}
    os.makedirs(sim.data('gear'), exist_ok=True)
    json.dump(res, open(sim.data(f'gear/{name}.json'), 'w'), indent=1)
    json.dump(gear_of(setup), open(sim.data(f'gear/{name}.items.json'), 'w'))
    print(f'[{name}] done {final:.1f}', flush=True)
    return res


if __name__ == '__main__':
    search(sys.argv[1], sys.argv[2], a.TALENTS.get(sys.argv[3], sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else None)
