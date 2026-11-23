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


# ---------- upgrade finder ----------
STAT_NAMES = {'Strength': 0, 'Agility': 1, 'Attack Power': 14, 'Hit Rating': 17, 'Crit Rating': 18, 'Haste Rating': 19,
              'Armor Penetration': 20, 'Expertise Rating': 21}
EXTRA_NAMES = {'Intellect': 3, 'Spirit': 13, 'Feral Attack Power': 16}
SLOT_GROUP = {'finger1': 'finger', 'finger2': 'finger', 'trinket1': 'trinket', 'trinket2': 'trinket'}
HIT_CAP = 40  # hit rating from gear that reaches the cap against a raid boss, with Nature's Reach 2/2


def slot_group(it):
    t = it.get('type')
    if t == 13:
        return 'off_hand' if it.get('weaponType') == 5 else 'main_hand'
    if t == 14:
        return 'ranged'
    return {1: 'head', 2: 'neck', 3: 'shoulder', 4: 'back', 5: 'chest', 6: 'wrist', 7: 'hands', 8: 'waist', 9: 'legs',
            10: 'feet', 11: 'finger', 12: 'trinket'}.get(t)


def set_bonuses():
    """Plain stat set bonuses from the sim's set table (procs are left to the sim's own numbers)."""
    import re
    src = open(os.path.join(sim.FOREVER, 'sim/common/forever/item_sets_auto_gen.go')).read()
    out = {}
    for chunk in src.split('NewParsedItemSet(')[1:]:
        sid = int(chunk.split(',', 1)[0])
        lines = chunk.split('\n')
        for i, line in enumerate(lines):
            m = re.match(r'\s*(\d+): \{', line)
            if not m:
                continue
            j = i
            while j > 0 and lines[j - 1].strip().startswith('//'):
                j -= 1
            text = ' '.join(x.strip().lstrip('/').strip() for x in lines[j:i] if 'http' not in x)
            st = {}
            for pat, idx, mul in ((r'chance to hit by ([\d.]+)%', 17, 10), (r'critical strike by ([\d.]+)%', 18, 14),
                                  (r'^\+(\d+) Attack Power\.', 14, 1), (r'^\+(\d+) Agility\.', 1, 1), (r'^\+(\d+) Strength\.', 0, 1)):
                mm = re.search(pat, text)
                if mm and 'spell' not in text.lower():
                    st[idx] = round(float(mm.group(1)) * mul)
            if st:
                out.setdefault(sid, {})[int(m.group(1))] = st
    return out


def finder():
    """Everything the upgrade finder needs: DPS per stat point, the items a player might wear, and the sim's own
    per-slot numbers for the items it ranked (procs, on-use and set effects included there)."""
    R = json.load(open(sim.data('results.json')))
    pp = R['stats']['cat']['perPoint']
    W = json.load(open(sim.data('extra_weights.json')))
    w = {STAT_NAMES[n]: v for n, v in pp.items() if n in STAT_NAMES}
    w.update({EXTRA_NAMES[n]: W[n] for n in EXTRA_NAMES})
    items, pool = {}, {}
    for it in a.DB['items']:
        if not G.wearable(it):
            continue
        so = it['scalingOptions'].get('0', {})
        if it.get('reqLvl', 0) < 40 and so.get('ilvl', 0) < 50:
            continue
        grp = slot_group(it)
        if not grp:
            continue
        st = {k: v for k, v in G.stats_of(it).items() if w.get(k)}
        if not st and it.get('type') != 13 and not it.get('itemEffects') and not it.get('randomSuffixOptions'):
            continue  # nothing a cat can use
        sufs = [x for x in (it.get('randomSuffixOptions') or []) if x in G.SUFFIX]
        avail = G.allowed_source(it)
        fac = 0 if G.faction_ok(it, 'alliance') and G.faction_ok(it, 'horde') else (1 if G.faction_ok(it, 'alliance') else 2)
        items[it['id']] = [it['name'], H.quality(it['id']), H.item_icon(it['id']), grp, st,
                           round(so.get('unroundedDps', 0), 2) if it.get('type') == 13 else 0,
                           it.get('setId') or 0, int(avail), int(H.hard_to_get(it['id'])), H.kinds(it['id']), fac,
                           sufs, so.get('randPropPoints', 0), int(bool(it.get('itemEffects'))), int(it.get('handType') == 4),
                           int(bool(it.get('unique')))] + ([H.source(it['id'])[:2]] if avail else [])
        pool.setdefault(grp, []).append(it['id'])
    sufs = {sid for v in items.values() for sid in v[11]}
    suffix = {sid: [G.SUFFIX[sid]['name'], {i: v for i, v in enumerate(G.SUFFIX[sid].get('stats', [])) if v and w.get(i)}]
              for sid in sufs}
    simmed = {}
    for fac in ('alliance', 'horde'):
        r = json.load(open(sim.data(f'rank/{fac}.json')))
        simmed[fac] = {}
        for slot, sd in r['slots'].items():
            grp = SLOT_GROUP.get(slot, slot)
            d = simmed[fac].setdefault(grp, {})
            for o in sd['options']:
                d.setdefault(f"{o['id']}:{o.get('suffix') or 0}", o['delta'])
    return {'w': w, 'wdps': W['Weapon DPS'], 'hitCap': HIT_CAP, 'items': items, 'suffix': suffix,
            'sets': set_bonuses(), 'simmed': simmed}


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
    data['meta'] = H.meta()
    data['err'] = 1.7  # 95% margin of a gap, ignoring the shared-seed benefit (sd ~33 DPS, 3000 iterations)
    data['suffixes'] = {s['id']: s['name'] for s in a.DB['randomSuffixes']}
    gw = json.load(open(sim.data('results.json')))['stats']['cat']['perPoint']
    data['ep'] = sorted([[n, round(v / gw['Agility'], 2)] for n, v in gw.items()], key=lambda x: -x[1])
    data['finder'] = finder()
    os.makedirs(os.path.join(sim.DOCS, 'bis'), exist_ok=True)
    html = open(os.path.join(sim.HERE, 'bis_template.html')).read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':')))
    html = html.replace('__HEAD__', H.head_tags('Feral Cat pre-raid BiS for WoW Forever',
                                                'Every slot ranked by WoWSims Forever, with filters and an upgrade finder for your own gear.',
                                                'bis/', 'bis/og.png'))
    open(os.path.join(sim.DOCS, 'bis', 'index.html'), 'w').write(html)
    print('ok', len(html) // 1024, 'KB', len(used), 'items', len(icons), 'icons')


if __name__ == '__main__':
    main()
