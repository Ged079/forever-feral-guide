#!/usr/bin/env python3
"""Pre-raid BiS page: rank/<faction>.json + item data + icons -> bis/index.html."""
import json, os
import analyze as a
import gear as G
import build_page_helpers as H

TOPN_STORE = 15
RANK_DIR = os.environ.get('RANK_DIR', '../setup/rank')
GUIDE_URL = 'https://claude.ai/artifact/5gGGbyVEPBERj1fR2FMaqm'  # options kept per slot

ITEMS = G.ITEMS
SUFFIX = G.SUFFIX
QUALITY = {0: '#9d9d9d', 1: '#e6e6e6', 2: '#1eff00', 3: '#0070dd', 4: '#a335ee', 5: '#ff8000'}
II = {i['id']: i.get('icon') for i in a.DB['items']}
II.update({x['id']: x.get('icon') for x in a.DB['itemIcons'] if x.get('icon') and not II.get(x['id'])})
FALLBACK = {1: 'inv_helmet_04', 2: 'inv_jewelry_necklace_07', 3: 'inv_shoulder_02', 4: 'inv_misc_cape_02', 5: 'inv_chest_leather_01',
            6: 'inv_bracer_02', 7: 'inv_gauntlets_05', 8: 'inv_belt_04', 9: 'inv_pants_leather_01', 10: 'inv_boots_01',
            11: 'inv_jewelry_ring_01', 13: 'inv_mace_04'}
for _i, _it in G.ITEMS.items():
    if not II.get(_i):
        II[_i] = FALLBACK.get(_it.get('type'), 'inv_misc_questionmark')


def main():
    data = {'factions': {}, 'items': {}, 'enchants': {}}
    used = set()
    for fac in ('alliance', 'horde'):
        r = json.load(open(f'{RANK_DIR}/{fac}.json'))
        g = json.load(open(f'../setup/gear/cat_{fac}.json'))
        slots = {}
        for slot, sd in r['slots'].items():
            seen, opts = set(), []
            for o in sd['options']:
                n = ITEMS[o['id']]['name'] + str(o.get('suffix') or '')
                if n in seen:
                    continue  # another version of an item already listed higher
                seen.add(n); opts.append(o)
            opts = opts[:TOPN_STORE]
            bis = sd['bis']
            slots[slot] = {'bis': bis.get('id'), 'bisSuffix': bis.get('randomSuffix'),
                           'enchant': H.enchant_name(bis.get('enchant'), slot) if bis.get('id') else '',
                           'options': [[o['id'], o.get('suffix') or 0, o['delta']] for o in opts]}
            used |= {o['id'] for o in opts}
            if bis.get('id'):
                used.add(bis['id'])
        # easy budget: swap restricted BiS pieces for the best unrestricted option in that slot
        easy, easy_delta, swaps = {}, 0.0, []
        taken = set()
        for slot in G.SLOTS:
            sd = slots.get(slot)
            if not sd or not sd['bis']:
                continue
            pick = sd['bis']
            if H.hard_to_get(pick):
                for iid, suf, d in sd['options']:
                    pair = {'finger1': 'finger2', 'finger2': 'finger1', 'trinket1': 'trinket2', 'trinket2': 'trinket1'}.get(slot)
                    other = easy.get(pair, [None])[0] if pair else None
                    if not H.hard_to_get(iid) and iid != other:
                        swaps.append([slot, sd['bis'], iid, d])
                        easy_delta += d
                        pick = iid
                        break
            easy[slot] = [pick]
        data['factions'][fac] = {'race': g['race'], 'dps': g['dps'], 'rankBase': r['base'], 'slots': slots,
                                 'easy': {k: v[0] for k, v in easy.items()}, 'easyDelta': round(easy_delta, 1), 'easySwaps': swaps,
                                 'enchants': g['enchants'], 'log': g['log']}
    icons = H.load_icons({II.get(i) for i in used if II.get(i)})
    data['icons'] = icons
    for iid in used:
        it = ITEMS[iid]
        data['items'][iid] = {'n': it['name'], 'q': QUALITY.get(it.get('quality', 1), '#e6e6e6'), 'i': (II.get(iid) or '').lower(),
                              'src': H.source(iid), 'k': H.kinds(iid), 'r': H.hard_to_get(iid)}
    data['guideUrl'] = GUIDE_URL
    data['suffixes'] = {s['id']: s['name'] for s in a.DB['randomSuffixes']}
    gw = json.load(open('../setup/results.json'))['stats']['cat']['perPoint']
    data['ep'] = sorted([[n, round(v / gw['Agility'], 2)] for n, v in gw.items()], key=lambda x: -x[1])
    os.makedirs('../docs/bis', exist_ok=True)
    html = open('bis_template.html').read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':')))
    open('../docs/bis/index.html', 'w').write(html)
    print('ok', len(html) // 1024, 'KB', len(used), 'items', len(icons), 'icons')


if __name__ == '__main__':
    main()
