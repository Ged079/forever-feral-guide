#!/usr/bin/env python3
"""Join results.json, the sim's damage breakdown and content.py into page/index.html."""
import json, os
import analyze as a
import sim
import content as C
import gear as G

R = json.load(open('../setup/results.json'))
TT = json.load(open('../setup/talent_text.json'))
SPELL = {s['id']: s['name'] for s in a.DB['spellIcons']}
ITEM = {i['id']: i['name'] for i in a.DB['itemIcons']}
AGI = 'Agility'


def breakdown(build):
    _, _, r = sim.run(a.setup(build))
    pm = r['raidMetrics']['parties'][0]['players'][0]
    rows, casts = {}, {}
    for x in pm['actions']:
        i = x['id']
        n = SPELL.get(i.get('spellId')) or ITEM.get(i.get('itemId')) or ('Melee swings' if i.get('otherId') == 'OtherActionAttack' else None)
        if not n:
            continue
        dmg = sum(t.get('damage', 0) for t in x.get('targets', []))
        c = sum(t.get('casts', 0) for t in x.get('targets', []))
        rows[n] = rows.get(n, 0) + dmg
        casts[n] = casts.get(n, 0) + c
    tot = sum(rows.values())
    main = [(n, v / tot * 100) for n, v in sorted(rows.items(), key=lambda kv: -kv[1]) if v / tot > 0.02]
    other = 100 - sum(v for _, v in main)
    if other > 0.05:
        main.append(('Other', other))
    it = a.sim.ITER
    return {'parts': [[n, round(v, 1)] for n, v in main],
            'casts': {n: round(casts[n] / it, 1) for n in ['Shred', 'Claw', 'Rip', 'Rake', 'Ferocious Bite', 'Shifting Power'] if casts.get(n, 0) / it >= 0.5}}


SEARCH = {n: json.load(open(f'../setup/search_v1/{n}.json')) for n in ('cat', 'hybrid', 'restart1')}
SEARCH['restart4'] = json.load(open('../setup/search/restart4.json'))
data = {'builds': {}, 'meta': {'iterations': a.sim.ITER, 'forever': 'a73af71', 'date': '2026-11-22'}}
for b, info in C.BUILDS.items():
    talents = [dict(t, text=C.TALENT_TEXT.get(t['name'], '')) for t in R['talents'][b]]
    talents.sort(key=lambda t: -t['all'])
    sw = R['stats'][b]['perPoint']
    ep = sorted(((n, round(v / sw[AGI], 2), v) for n, v in sw.items()), key=lambda x: -x[1])
    hit = R['hit'][b]
    gh = R['gear']['Hit Rating']
    i0 = next(i for i, (h, _) in enumerate(hit) if h == 0)
    slope = (hit[i0][1] - hit[i0 - 2][1]) / 20  # DPS per hit rating below the cap
    top = hit[-1][1]
    k = next(i for i in range(i0, len(hit)) if hit[i][1] >= top - 1.0)
    cap = round((hit[k - 1][0] + (top - hit[k - 1][1]) / slope + gh) / 5) * 5  # to the nearest 5 rating
    fill = C.LOOP_FILL[b]
    data['builds'][b] = dict(info, talentsString=a.TALENTS[b], dps=R['builds'][b], talents=talents,
                             ep=[[n, e] for n, e, _ in ep], hitCap=cap,
                             hitCurve=[[h + R['gear']['Hit Rating'], d] for h, d in hit],
                             loop=[[t.format(**fill), x.format(**fill)] for t, x, bs in C.LOOP if b in bs],
                             races={C.RACES[r][0]: v[b] for r, v in R['races'].items()},
                             preset=R['presets'][b], presetString=a.PRESETS[b],
                             path=[[x['move'], x['confirm'][1] - x['confirm'][0]] for x in SEARCH[b]['log'][1:]],
                             **breakdown(b))

data['consumables'] = {}
for b, cons in R['consumables'].items():
    data['consumables'][b] = {
        'list': sorted([{'name': c['name'], 'id': c['id'], 'v': c['v']} for c in cons['list']], key=lambda c: -c['v']),
        'swaps': [x for x in cons['alts'] if abs(x['v']) >= 0.5],
        'adds': cons['adds']}
data['alternatives'] = json.load(open('../setup/alternatives.json')) if os.path.exists('../setup/alternatives.json') else []
bl = R['buffs']['list']
data['buffs'] = sorted([{'name': C.BUFF_NAMES[x['key']], 'v': x['v']} for x in bl
                        if x['kind'] in ('raid', 'blessing', 'debuff') and x['key'] not in
                        ('sunderArmor', 'exposeArmor', 'faerieFire', 'curseOfRecklessness')], key=lambda x: -x['v'])
data['armor'] = {x['key']: x['v'] for x in bl if x['kind'] == 'armorAlone'}
data['armorAll'] = next(x['v'] for x in bl if x['key'] == 'allArmorDebuffs')
data['otherBleed'] = next(x['v'] for x in bl if x['key'] == 'otherBleed')
data['totals'] = R['buffs']['totals']
data['races'] = [[n, f, rac] for n, f, rac in C.RACES.values()]
ITEMS = {i['id']: i for i in a.DB['items']}
ZONES = {z['id']: z['name'] for z in a.DB['zones']}
FACS = {f['id']: f['name'] for f in a.DB['factions']}
REP = {4: 'Neutral', 5: 'Friendly', 6: 'Honored', 7: 'Revered', 8: 'Exalted'}
SLOTTYPE = {'head': 1, 'neck': 2, 'shoulder': 3, 'back': 4, 'chest': 5, 'wrist': 6, 'hands': 7, 'waist': 8, 'legs': 9,
            'feet': 10, 'finger1': 11, 'finger2': 11, 'trinket1': 12, 'trinket2': 12, 'main_hand': 13, 'off_hand': 13, 'ranged': 14}
SLOTNAME = {'head': 'Head', 'neck': 'Neck', 'shoulder': 'Shoulder', 'back': 'Back', 'chest': 'Chest', 'wrist': 'Wrist',
            'hands': 'Hands', 'waist': 'Waist', 'legs': 'Legs', 'feet': 'Feet', 'finger1': 'Ring', 'finger2': 'Ring',
            'trinket1': 'Trinket', 'trinket2': 'Trinket', 'main_hand': 'Weapon', 'off_hand': 'Off hand', 'ranged': 'Idol'}


def enchant_name(eid, slot):
    if not eid:
        return ''
    t = SLOTTYPE[slot]
    names = [e['name'] for e in a.DB['enchants'] if e['effectId'] == eid and (e.get('type') == t or t in e.get('extraTypes', []))]
    n = names[0] if names else next((e['name'] for e in a.DB['enchants'] if e['effectId'] == eid), '')
    return n.replace('Enchant ', '').replace('2H Weapon - ', '').replace('Weapon - ', '')


def source(iid):
    it = ITEMS[iid]
    out = []
    for src in it.get('sources', []):
        k, v = next(iter(src.items()))
        v = v or {}
        if k == 'drop':
            z = ZONES.get(v.get('zoneId'))
            out.append(f"Drop{': ' + z if z else ''}")
        elif k == 'quest':
            out.append(f"Quest: {v.get('name', '')}")
        elif k == 'soldBy':
            out.append(f"Vendor: {v.get('npcName', '')}" + (f" ({ZONES[v['zoneId']]})" if v.get('zoneId') in ZONES else ''))
        elif k == 'crafted':
            out.append(f"Crafted: {C.PROFESSIONS.get(v.get('profession'), 'profession')}")
        elif k == 'rep':
            out.append(f"Reputation: {FACS.get(v.get('repFactionId'), '')} {REP.get(v.get('repLevel'), '')}".strip())
    if not out:
        out = ['World drop (Auction House)' if it.get('randomSuffixOptions') or iid < 200000 else 'No source listed']
    return list(dict.fromkeys(out))[:2]


def gear_card(fac):
    g = json.load(open(f'../setup/gear/cat_{fac}.json'))
    rows = []
    for x in g['gear']:
        rows.append({'slot': SLOTNAME[x['slot']], 'id': x['id'], 'name': x['name'], 'enchant': enchant_name(x.get('enchant'), x['slot']),
                     'src': source(x['id']), 'alts': [dict(y, src=source(y['id'])) for y in g['alternatives'].get(x['slot'], [])
                                                     if y['id'] != x['id'] and G.allowed_source(ITEMS[y['id']])][:3]})
    return {'race': g['race'], 'dps': g['dps'], 'rows': rows, 'log': g['log'], 'enchants': g['enchants']}


data['gear'] = {f: gear_card(f) for f in ('alliance', 'horde')}
data['gearHit'] = R['gear']['Hit Rating']
data['trees'] = json.load(open('../setup/trees.json'))
data['talentText'] = C.TALENT_TEXT
data['macros'] = C.MACROS
data['macroNote'] = C.MACRO_NOTE
data['opener'] = C.OPENER
data['loopEnd'] = C.LOOP_END
data['cooldowns'] = C.COOLDOWNS
data['restart'] = [{'start': SEARCH[r]['log'][0]['dps'], 'steps': len(SEARCH[r]['log']) - 1, 'final': SEARCH[r]['final']} for r in ('restart1', 'restart4')]

os.makedirs('../docs', exist_ok=True)
html = open('template.html').read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':')))
open('../docs/index.html', 'w').write(html)
print('ok', len(html), 'bytes; hit caps', {b: v['hitCap'] for b, v in data['builds'].items()})
print(json.dumps({b: v['casts'] for b, v in data['builds'].items()}))
