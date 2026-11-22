#!/usr/bin/env python3
"""Pre-raid BiS page: rank/<faction>.json + item data + icons -> bis/index.html."""
import json, os
import analyze as a
import gear as G
import build_page_helpers as H
import sim

TOPN_STORE = 15

ITEMS = G.ITEMS
SUFFIX = G.SUFFIX


def main():
    data = {'factions': {}, 'items': {}, 'enchants': {}}
    used = set()
    for fac in ('alliance', 'horde'):
        r = json.load(open(sim.data(f'rank/{fac}.json')))
        g = json.load(open(sim.data(f'gear/cat_{fac}.json')))
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
        data['factions'][fac] = {'race': g['race'], 'dps': r['base'], 'rankBase': r['base'], 'slots': slots,
                                 'easy': {k: v[0] for k, v in easy.items()}, 'easyDelta': round(easy_delta, 1), 'easySwaps': swaps,
                                 'enchants': g['enchants'], 'log': g['log']}
    icons = H.load_icons({H.item_icon(i) for i in used})
    data['icons'] = icons
    for iid in used:
        it = ITEMS[iid]
        data['items'][iid] = {'n': it['name'], 'q': H.quality(iid), 'i': H.item_icon(iid),
                              'src': H.source(iid), 'k': H.kinds(iid), 'r': H.hard_to_get(iid)}
    data['guideUrl'] = sim.GUIDE_URL
    data['err'] = 1.7  # 95% margin of a gap, ignoring the shared-seed benefit (sd ~33 DPS, 3000 iterations)
    data['suffixes'] = {s['id']: s['name'] for s in a.DB['randomSuffixes']}
    gw = json.load(open(sim.data('results.json')))['stats']['cat']['perPoint']
    data['ep'] = sorted([[n, round(v / gw['Agility'], 2)] for n, v in gw.items()], key=lambda x: -x[1])
    os.makedirs(os.path.join(sim.DOCS, 'bis'), exist_ok=True)
    html = open(os.path.join(sim.HERE, 'bis_template.html')).read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':')))
    open(os.path.join(sim.DOCS, 'bis', 'index.html'), 'w').write(html)
    print('ok', len(html) // 1024, 'KB', len(used), 'items', len(icons), 'icons')


if __name__ == '__main__':
    main()
