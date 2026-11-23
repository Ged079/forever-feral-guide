#!/usr/bin/env python3
"""What every rank of every talent is worth on top of the Cat build, for the guide's talent calculator.

For each talent and each rank 0..max, the Cat build with only that talent set to that rank (point totals and tier
rules ignored, so each number is that talent alone). The calculator adds the differences for a player's build, so
its total is an estimate: talents that feed each other are counted one at a time.

    talent_ranks.py     -> ../setup/talent_ranks.json
"""
import json
import analyze as a
import sim

IT, SEED = 3000, 1


def main():
    base_str = a.TALENTS['cat']
    base = a.parse_talents(base_str)
    jobs, keys = [], []
    for ti, tree in enumerate(a.TREES):
        for i, t in enumerate(a.tree_order(tree)):
            for r in range(t['maxPoints'] + 1):
                if r == base[ti][i]:
                    continue
                pts = [p[:] for p in base]
                pts[ti][i] = r
                jobs.append(a.setup(a.talent_string(pts)))
                keys.append((t['fancyName'], r))
    res = sim.runmany(jobs, iterations=IT, seed=SEED)
    cat = sim.run(a.setup(base_str), iterations=IT, seed=SEED)[0]
    out = {}
    for ti, tree in enumerate(a.TREES):
        for i, t in enumerate(a.tree_order(tree)):
            out[t['fancyName']] = [round(cat, 1) if r == base[ti][i] else None for r in range(t['maxPoints'] + 1)]
    for (name, r), x in zip(keys, res):
        out[name][r] = round(x[0], 1)
    json.dump({'base': round(cat, 1), 'talents': base_str, 'iterations': IT, 'ranks': out},
              open(sim.data('talent_ranks.json'), 'w'), indent=1)
    print('cat', round(cat, 1), 'sims', len(jobs))


if __name__ == '__main__':
    main()
