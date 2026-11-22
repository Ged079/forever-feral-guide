#!/usr/bin/env python3
"""Rank every candidate item per slot against the best-in-slot set (Cat build, per faction).

Each option = DPS of the BiS set with only that slot swapped, minus the BiS set (same seed, 3000 iterations),
so the numbers compare cleanly within a slot. Writes rank/<faction>.json.
"""
import json, os, sys
import analyze as a
import gear as G
import sim

IT = 3000
G.PER_SLOT, G.PER_SLOT_EFFECT, G.PER_WEAPON = 30, 10, 45


def rank(faction):
    s = a.setup('cat', faction=faction)
    bis = G.gear_of(s)
    pools = G.candidates(faction)
    base = sim.run(s, iterations=IT)[0]
    out = {'faction': faction, 'base': round(base, 1), 'slots': {}}
    for slot in G.SLOTS:
        i = G.SLOTS.index(slot)
        cur = bis[i] if i < len(bis) else {}
        setups, opts = [], []
        for c in pools[slot]:
            if slot == 'off_hand' and G.ITEMS.get(bis[14].get('id'), {}).get('handType') == 4:
                break
            t = G.with_item(s, slot, c)
            if not G.legal(t):
                continue
            setups.append(t); opts.append(c)
        vals = [r[0] for r in sim.runmany(setups, iterations=IT)] if setups else []
        rows = []
        for c, v in zip(opts, vals):
            same = c['id'] == cur.get('id') and (c.get('suffix') or 0) == (cur.get('randomSuffix') or 0)
            rows.append({'id': c['id'], 'suffix': c.get('suffix'), 'delta': 0.0 if same else round(v - base, 1)})
        if cur.get('id') and not any(r['id'] == cur['id'] for r in rows):
            rows.append({'id': cur['id'], 'suffix': cur.get('randomSuffix'), 'delta': 0.0})
        rows.sort(key=lambda r: -r['delta'])
        out['slots'][slot] = {'bis': cur, 'options': rows}
        print(faction, slot, len(rows), rows[:2], flush=True)
    os.makedirs(sim.data('rank'), exist_ok=True)
    json.dump(out, open(sim.data(f'rank/{faction}.json'), 'w'), indent=1)


if __name__ == '__main__':
    for f in sys.argv[1:] or ['alliance', 'horde']:
        rank(f)
