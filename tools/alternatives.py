import json, analyze as a, sim
R4 = json.load(open('../setup/search/restart4.json'))['final']
B = [
    ('Cat', a.TALENTS['cat'], 'The main build. Most DPS.'),
    ('Cat, bear-ready', R4, 'Furor down to 1/5; the 4 points go to Thick Hide 2/3 and Brutal Impact 2/2 for off-tanking. A tie with Cat; found by a search that started from a scrambled build.'),
    ('Cat with Feral Charge', '050021-55000032123012125001-055', 'Feral Charge for a gap closer or interrupt, paid with a point of Nature’s Reach (2% hit).'),
    ('Hybrid', a.TALENTS['hybrid'], 'Thick Hide 3/3, Lacerate and Primal Bite for real tanking.'),
    ('Sim preset: Cat', a.PRESETS['cat'], 'The sim’s own Cat build, for comparison.'),
    ('Sim preset: Hybrid', a.PRESETS['hybrid'], 'The sim’s own Hybrid build, for comparison.'),
]
v = [r[0] for r in sim.runmany([a.setup(t) for _, t, _ in B], iterations=10000, seed=3_000_000)]
out = [{'name': n, 'talents': t, 'note': note, 'dps': round(d, 1), 'delta': round(d - v[0], 1) if i else 0}
       for i, ((n, t, note), d) in enumerate(zip(B, v))]
for o in out: print(o['name'], o['dps'], o['delta'])
json.dump(out, open('../setup/alternatives.json', 'w'), indent=1)
