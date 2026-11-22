#!/usr/bin/env python3
"""Hill-climb Feral Cat talent builds in WoWSims Forever.

Moves: take k points (1..5) from one talent and put them in another, keeping the build legal
(row N needs 5*N points above it in its tree, a prerequisite must be maxed, 51 points in all).
Each round screens every move at SCREEN iterations and keeps the best if it beats the current build
by more than MARGIN, re-checked at CONFIRM iterations on another seed. Ends when no move helps.

    search.py NAME START_STRING [--keep Talent,Talent]   (--keep: talents that must stay maxed)
"""
import argparse, copy, json, os, sys, time
import analyze as a
import sim

TOTAL = 51
SCREEN, CONFIRM, SEED2 = 1000, 6000, 500000
MARGIN = 1.0

TREES = [a.tree_order(t) for t in a.TREES]
NAMES = [[t['fancyName'] for t in tree] for tree in TREES]
ROW = [[t['location']['rowIdx'] for t in tree] for tree in TREES]
MAX = [[t['maxPoints'] for t in tree] for tree in TREES]
LOC = [{(t['location']['rowIdx'], t['location']['colIdx']): i for i, t in enumerate(tree)} for tree in TREES]
PRE = [[LOC[ti].get((t['prereqLocation']['rowIdx'], t['prereqLocation']['colIdx'])) if 'prereqLocation' in t else None
        for t in tree] for ti, tree in enumerate(TREES)]


def legal(pts):
    if sum(map(sum, pts)) != TOTAL:
        return False
    for ti, p in enumerate(pts):
        for i, n in enumerate(p):
            if n < 0 or n > MAX[ti][i]:
                return False
            if n:
                above = sum(p[j] for j in range(len(p)) if ROW[ti][j] < ROW[ti][i])
                if above < 5 * ROW[ti][i]:
                    return False
                pre = PRE[ti][i]
                if pre is not None and p[pre] < MAX[ti][pre]:
                    return False
    return True


def moves(pts, keep):
    seen = set()
    for ta, pa in enumerate(pts):
        for ia, na in enumerate(pa):
            if not na:
                continue
            for tb, pb in enumerate(pts):
                for ib, nb in enumerate(pb):
                    if (ta, ia) == (tb, ib):
                        continue
                    for k in (1, 2, 3, 5):
                        if k > na or nb + k > MAX[tb][ib]:
                            continue
                        q = copy.deepcopy(pts)
                        q[ta][ia] -= k
                        q[tb][ib] += k
                        if any(q[t][i] < MAX[t][i] for t, i in keep):
                            continue
                        s = a.talent_string(q)
                        if s not in seen and legal(q):
                            seen.add(s)
                            yield s, f'{NAMES[ta][ia]} -{k} → {NAMES[tb][ib]} +{k}'


def score(strings, it, seed=sim.SEED):
    return [r[0] for r in sim.runmany([a.setup(s) for s in strings], iterations=it, seed=seed)]


def search(name, start, keep_names):
    keep = [(ti, i) for ti in range(3) for i, n in enumerate(NAMES[ti]) if n in keep_names]
    cur = start
    assert legal(a.parse_talents(cur)), 'start build is not legal'
    cur_dps = score([cur], SCREEN)[0]
    log = [{'build': cur, 'dps': round(cur_dps, 1), 'move': 'start'}]
    print(f'[{name}] start {cur} {cur_dps:.1f}', flush=True)
    tried_confirm = set()
    while True:
        t0 = time.time()
        cand = list(moves(a.parse_talents(cur), keep))
        vals = score([s for s, _ in cand], SCREEN)
        ranked = sorted(zip(vals, cand), key=lambda x: -x[0])
        improved = False
        for v, (s, desc) in ranked[:4]:
            if v - cur_dps <= MARGIN or s in tried_confirm:
                break
            tried_confirm.add(s)
            new, old = score([s, cur], CONFIRM, seed=SEED2)
            if new - old > MARGIN * 0.5:
                print(f'[{name}] {desc}: {old:.1f} → {new:.1f} ({len(cand)} moves, {time.time() - t0:.0f}s)', flush=True)
                cur, cur_dps = s, score([s], SCREEN)[0]
                log.append({'build': cur, 'dps': round(cur_dps, 1), 'move': desc, 'confirm': [round(old, 1), round(new, 1)]})
                improved = True
                break
        if not improved:
            print(f'[{name}] done: {cur} ({len(cand)} moves checked, best screen {ranked[0][0]:.1f} vs {cur_dps:.1f})', flush=True)
            top = [{'build': s, 'move': d, 'screen': round(v, 1)} for v, (s, d) in ranked[:8]]
            return {'name': name, 'start': start, 'final': cur, 'log': log, 'neighbours': top}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('start')
    ap.add_argument('--keep', default='')
    x = ap.parse_args()
    res = search(x.name, a.TALENTS.get(x.start, x.start), [k for k in x.keep.split(',') if k])
    os.makedirs('../setup/search', exist_ok=True)
    json.dump(res, open(f'../setup/search/{x.name}.json', 'w'), indent=1)
