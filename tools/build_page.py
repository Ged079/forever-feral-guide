#!/usr/bin/env python3
"""Join setup/*.json, the sim's damage breakdown and content.py into docs/index.html."""
import json, os, re
import analyze as a
import sim
import content as C
import build_page_helpers as H
from build_page_helpers import ITEMS, source

R = json.load(open(sim.data('results.json')))
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


SEARCH = {n: json.load(open(sim.data(f'search_v1/{n}.json'))) for n in ('cat', 'hybrid', 'restart1')}
SEARCH['restart4'] = json.load(open(sim.data('search/restart4.json')))
data = {'builds': {}, 'meta': H.meta(), 'siteUrl': H.SITE}
for b, info in C.BUILDS.items():
    _rf = sim.data('talent_ranks.json' if b == 'cat' else f'talent_ranks_{b}.json')
    _rk = json.load(open(_rf))['ranks'] if os.path.exists(_rf) else {}

    def _per_point(t):
        """What each point of the talent adds, first to last, from the per-rank sims; None where a rank is missing."""
        row = _rk.get(t['name'])
        if not row or any(row[k] is None for k in range(t['points'] + 1)):
            return None
        return [round(row[k] - row[k - 1], 1) for k in range(1, t['points'] + 1)]
    talents = [dict(t, text=C.TALENT_TEXT.get(t['name'], ''), per=_per_point(t)) for t in R['talents'][b]]
    talents.sort(key=lambda t: -t['all'])
    sw = R['stats'][b]['perPoint']
    xw = json.load(open(sim.data('extra_weights.json')))
    sw = dict(sw, **{k: xw[k] for k in ('Intellect', 'MP5', 'Feral Attack Power')})
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
data['alternatives'] = json.load(open(sim.data('alternatives.json')))
bl = R['buffs']['list']
data['buffRaw'] = {x['key']: x['v'] for x in bl}
data['buffs'] = sorted([{'name': C.BUFF_NAMES[x['key']], 'v': x['v']} for x in bl
                        if x['kind'] in ('raid', 'blessing', 'debuff') and x['key'] not in
                        ('sunderArmor', 'exposeArmor', 'faerieFire', 'curseOfRecklessness')], key=lambda x: -x['v'])
data['armor'] = {x['key']: x['v'] for x in bl if x['kind'] == 'armorAlone'}
data['armorAll'] = next(x['v'] for x in bl if x['key'] == 'allArmorDebuffs')
data['otherBleed'] = next(x['v'] for x in bl if x['key'] == 'otherBleed')
data['totals'] = R['buffs']['totals']
data['races'] = [[n, f, rac] for n, f, rac in C.RACES.values()]
SLOTNAME = {'head': 'Head', 'neck': 'Neck', 'shoulder': 'Shoulder', 'back': 'Back', 'chest': 'Chest', 'wrist': 'Wrist',
            'hands': 'Hands', 'waist': 'Waist', 'legs': 'Legs', 'feet': 'Feet', 'finger1': 'Ring', 'finger2': 'Ring',
            'trinket1': 'Trinket', 'trinket2': 'Trinket', 'main_hand': 'Weapon', 'off_hand': 'Off hand', 'ranged': 'Idol'}
_SFX = {x['id']: x['name'] for x in a.DB['randomSuffixes']}
RANK = {f: json.load(open(sim.data(f'rank/{f}.json'))) for f in ('alliance', 'horde')}


def gear_card(fac):
    g = json.load(open(sim.data(f'gear/cat_{fac}.json')))
    rows = [{'slot': SLOTNAME[x['slot']], 'id': x['id'], 'name': x['name'], 'src': source(x['id'], fac)} for x in g['gear']]
    return {'race': g['race'], 'dps': RANK[fac]['base'], 'rows': rows}


data['gear'] = {f: gear_card(f) for f in ('alliance', 'horde')}
for _f in data['gear'].values():
    for _r in _f['rows']:
        _r['icon'] = H.item_icon(_r['id']); _r['q'] = H.quality(_r['id']); _r['hard'] = H.hard_to_get(_r['id'])
data['gearIcons'] = H.load_icons({r['icon'] for f in data['gear'].values() for r in f['rows']})
data['gearHit'] = R['gear']['Hit Rating']
data['trees'] = json.load(open(sim.data('trees.json')))


def _curves():
    """Per-rank values of every talent effect, from the sim's game data: {spell id: [[rank values] per effect]}."""
    src = open(os.path.join(sim.FOREVER, 'sim/core/spelldata/spells_auto_gen.go')).read()
    out = {}
    for m in re.finditer(r"^\t(\d+):\s+\{(\{.*\})\},\s*$", src, re.M):
        out[int(m.group(1))] = [[float(v) for v in row.split(',')] for row in re.findall(r"\{([^{}]*)\}", m.group(2))]
    return out


def _fmt(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') if v != int(v) else str(int(v))


_CURVES = _curves()
data['talentRanks'] = json.load(open(sim.data('talent_ranks.json'))) if os.path.exists(sim.data('talent_ranks.json')) else None
data['tips'] = {}
for _tr in data['trees']:
    for _t in _tr['talents']:
        _text, _units = C.TALENT_TIPS[_t['n']]
        _cv = _CURVES.get(_t['s'], [])
        _cols = [(u.split('@')[0], int(u.split('@')[1]) if '@' in u else i) for i, u in enumerate(_units)]
        assert all(i < len(_cv) for _, i in _cols), (_t['n'], _cv)
        data['tips'][_t['n']] = [_text.format(*[_fmt(C.TIP_UNITS[u](_cv[i][r])) for u, i in _cols]) for r in range(_t['m'])]
        _t.pop('g', None)
_alt = {x['name']: x['dps'] for x in data['alternatives']}
_fc = round(_alt['Cat'] - _alt['Cat with Feral Charge'])
data['talentText'] = {k: v.replace('{fc}', str(_fc))
                      for k, v in C.TALENT_TEXT.items()}
_TA = json.load(open(sim.data('talent_assets.json')))
data['icons'] = _TA['icons']
data['treeBg'] = _TA['bg']
_ir = [o for o in RANK['alliance']['slots']['ranged']['options'] if o['delta'] < 0][0]
_idol = (ITEMS[_ir['id']]['name'], _ir['delta'])
xw = json.load(open(sim.data('extra_weights.json')))
wd = round(xw['Weapon DPS'] / xw['Agility'], 1)
def _itm(o):
    i = o['id']; ic = H.item_icon(i)
    return {'id': i, 'name': ITEMS[i]['name'] + (' ' + _SFX[o['suffix']] if o.get('suffix') in _SFX else ''), 'icon': ic,
            'q': H.quality(i), 'src': source(i, 'alliance'), 'delta': round(o['delta'], 1), 'hard': H.hard_to_get(i)}
_mh = RANK['alliance']['slots']['main_hand']['options']
_seen, _ws = set(), []
for o in _mh:
    if ITEMS[o['id']]['name'] in _seen: continue
    _seen.add(ITEMS[o['id']]['name']); _ws.append(_itm(o))
    if len(_ws) == 3: break
_rg = RANK['alliance']['slots']['ranged']['options']
_en = json.load(open(sim.data('gear/cat_alliance.json')))['enchants']
_eb = max(_en.values())
_EN = {'Enchant 2H Weapon - Superior Impact': ('Superior Impact', '+9 weapon damage'), 'Enchant 2H Weapon - Agility': ('Agility', '+25 Agility'),
       'Enchant 2H Weapon - Strength': ('Strength', '+9 Strength'), 'Enchant Weapon - Grand Crusader': ('Grand Crusader', 'proc')}
data['weaponCard'] = {
    'wdAgi': wd,
    'weapons': _ws,
    'idols': [_itm(o) for o in _rg[:2]],
    'enchants': [{'name': _EN.get(k, (k, ''))[0], 'what': _EN.get(k, ('', ''))[1], 'delta': round(v - _eb, 1)} for k, v in sorted(_en.items(), key=lambda x: -x[1])][:3],
}
data['gearIcons'].update(H.load_icons({x['icon'] for x in _ws + data['weaponCard']['idols']} - set(data['gearIcons'])))
data['buffIcon'] = json.load(open(sim.data('buff_icons.json')))
data['macros'] = C.MACROS
data['macroNote'] = C.MACRO_NOTE
data['opener'] = C.OPENER
data['openerChips'] = C.OPENER_CHIPS
_II = {x['id']: x.get('icon') for x in a.DB['itemIcons']}
_CN = {c['name']: c['id'] for c in a.DB['consumables']}
data['consIcon'] = {}
for _b, _c in R['consumables'].items():
    for x in _c['list'] + _c['adds']:
        data['consIcon'][x['name']] = _II.get(x['id'])
    for x in _c['alts']:
        data['consIcon'][x['to']] = _II.get(x['toId'])
        if x['from'] in _CN:
            data['consIcon'][x['from']] = _II.get(_CN[x['from']])
data['loopIcons'] = C.LOOP_ICONS
data['loopEnd'] = C.LOOP_END
data['cooldowns'] = C.COOLDOWNS
data['restart'] = [{'start': SEARCH[r]['log'][0]['dps'], 'steps': len(SEARCH[r]['log']) - 1, 'final': SEARCH[r]['final']} for r in ('restart1', 'restart4')]

os.makedirs(sim.DOCS, exist_ok=True)
html = open(os.path.join(sim.HERE, 'template.html')).read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':'))).replace('__BIS_URL__', sim.BIS_URL).replace('__XT__', sim.NEW_TAB).replace('__HEAD__', H.head_tags('Forever Feral Guide: Feral Cat for WoW Forever',
                                                     'Talents, rotation, consumables and pre-raid gear for Feral Cat in WoW Forever. Every number is simmed.',
                                                     '', 'og.png'))
open(os.path.join(sim.DOCS, 'index.html'), 'w').write(html)
print('ok', len(html), 'bytes; hit caps', {b: v['hitCap'] for b, v in data['builds'].items()})
print(json.dumps({b: v['casts'] for b, v in data['builds'].items()}))
