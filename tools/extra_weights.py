import copy, json, analyze as a, sim
s = a.setup('cat')
def bonus(idx=None, amt=0, pidx=None):
    t = copy.deepcopy(s); st = [0]*a.NSTATS
    if idx is not None: st[idx] = amt
    b = {'stats': st}
    if pidx is not None:
        ps = [0]*40; ps[pidx] = amt; b['pseudoStats'] = ps
    t['player']['bonusStats'] = b; return t
IT = 20000
out = {}
for name, idx, step in [('Intellect',3,40), ('Spirit',13,40), ('MP5',31,10), ('Feral Attack Power',16,80), ('Agility',1,40)]:
    up, dn = sim.runmany([bonus(idx, step), bonus(idx, -step)], iterations=IT)
    out[name] = round((up[0]-dn[0])/(2*step), 4)
up, dn = sim.runmany([bonus(pidx=0, amt=5), bonus(pidx=0, amt=-5)], iterations=IT)
out['Weapon DPS'] = round((up[0]-dn[0])/10, 4)
print(out)
json.dump(out, open('../setup/extra_weights.json','w'))
