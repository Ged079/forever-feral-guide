#!/usr/bin/env python3
"""Join results.json, the sim's damage breakdown and content.py into page/index.html."""
import json, os
import analyze as a
import sim
import content as C

R = json.load(open('../setup/results.json'))
TT = json.load(open('../setup/talent_text.json'))
GEAR = json.load(open('../setup/gear.json'))
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
                             **breakdown(b))

cons = R['consumables']
data['consumables'] = sorted([{'name': c['name'], 'id': c['id'], 'v': c['v']} for c in cons['list']], key=lambda c: -c['v'])
data['swaps'] = [s for s in cons['alts'] if abs(s['v']) >= 0.5]
bl = R['buffs']['list']
data['buffs'] = sorted([{'name': C.BUFF_NAMES[x['key']], 'v': x['v']} for x in bl
                        if x['kind'] in ('raid', 'blessing', 'debuff') and x['key'] not in
                        ('sunderArmor', 'exposeArmor', 'faerieFire', 'curseOfRecklessness')], key=lambda x: -x['v'])
data['armor'] = {x['key']: x['v'] for x in bl if x['kind'] == 'armorAlone'}
data['armorAll'] = next(x['v'] for x in bl if x['key'] == 'allArmorDebuffs')
data['otherBleed'] = next(x['v'] for x in bl if x['key'] == 'otherBleed')
data['totals'] = R['buffs']['totals']
data['races'] = [[n, f, rac] for n, f, rac in C.RACES.values()]
data['gear'] = [dict(g, enchant=C.ENCHANTS.get(g['slot'])) for g in GEAR]
data['gearHit'] = R['gear']['Hit Rating']
data['opener'] = C.OPENER
data['loopEnd'] = C.LOOP_END
data['cooldowns'] = C.COOLDOWNS

os.makedirs('../docs', exist_ok=True)
html = open('template.html').read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':')))
open('../docs/index.html', 'w').write(html)
print('ok', len(html), 'bytes; hit caps', {b: v['hitCap'] for b, v in data['builds'].items()})
print(json.dumps({b: v['casts'] for b, v in data['builds'].items()}))
