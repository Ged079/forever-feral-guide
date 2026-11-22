import random, sys, json, os
import search as S, analyze as a, sim
seed, steps = int(sys.argv[1]), int(sys.argv[2])
random.seed(seed)
pts = a.parse_talents(sys.argv[3])
for _ in range(steps):
    ms = list(S.moves(pts, []))
    s, d = random.choice(ms)
    pts = a.parse_talents(s)
start = a.talent_string(pts)
r = S.search(f'restart{seed}', start, [])
os.makedirs(sim.data('search'), exist_ok=True)
json.dump(r, open(sim.data(f'search/restart{seed}.json'), 'w'), indent=1)
