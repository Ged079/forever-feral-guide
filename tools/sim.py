#!/usr/bin/env python3
"""Run WoWSims Forever Feral Cat sims from Python.

base()      the default setup (setup/defaults.json + the adaptive APL), as a dict
run(req)    sims one RaidSimRequest dict, returns (dps avg, stdev, full result)
runmany()   runs many in parallel
"""
import copy, hashlib, json, os, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
FOREVER = os.environ.get('FOREVER', os.path.expanduser('~/forever'))  # a wowsims/forever checkout
CLI = os.environ.get('WOWSIMCLI', os.path.join(FOREVER, 'bin/wowsimcli'))
APL = os.path.join(FOREVER, 'ui/specs/druid/feralcat/apls/adaptive.apl.json')
SETUP = os.path.join(HERE, '..', 'setup')  # sim inputs and results
DOCS = os.path.join(HERE, '..', 'docs')    # the built pages
# Links between the two pages: relative for the website (docs/ on GitHub Pages);
# LINKS=artifact builds the claude.ai copies, which need absolute URLs.
ARTIFACT = os.environ.get('LINKS') == 'artifact'
BIS_URL = 'https://claude.ai/artifact/Q7Lj3rf1dCzQSUYfb21RGK' if ARTIFACT else 'bis/'
GUIDE_URL = 'https://claude.ai/artifact/5gGGbyVEPBERj1fR2FMaqm' if ARTIFACT else '../'
NEW_TAB = ' target="_blank" rel="noopener"' if ARTIFACT else ''
CACHE = os.path.join(HERE, 'cache')
os.makedirs(CACHE, exist_ok=True)


def data(*p):
    """Path inside setup/."""
    return os.path.join(SETUP, *p)


ITER = 3000
SEED = 1


def base():
    d = json.load(open(data('defaults.json')))
    p = d['player']
    p['rotation'] = json.load(open(APL))
    return d


def request(setup, iterations=ITER, seed=SEED, debug=False):
    s = copy.deepcopy(setup)
    return {
        'raid': {
            'parties': [{'players': [s['player']]}],
            'buffs': s.get('raidBuffs', {}),
            'debuffs': s.get('debuffs', {}),
        },
        'encounter': s['encounter'],
        'simOptions': {'iterations': iterations, 'randomSeed': seed, 'debug': debug},
        'type': 'SimTypeIndividual',
    }


def run(setup, iterations=ITER, seed=SEED):
    req = request(setup, iterations, seed)
    blob = json.dumps(req, sort_keys=True)
    key = hashlib.sha1(blob.encode()).hexdigest()
    cp = os.path.join(CACHE, key + '.json')
    if not os.path.exists(cp):
        with tempfile.TemporaryDirectory() as td:
            i, o = os.path.join(td, 'in.json'), os.path.join(td, 'out.json')
            open(i, 'w').write(blob)
            r = subprocess.run([CLI, 'sim', '--infile', i, '--outfile', o], capture_output=True, text=True)
            if r.returncode or not os.path.exists(o):
                raise RuntimeError(r.stderr[-2000:] + r.stdout[-2000:])
            res = json.load(open(o))
        if res.get('error'):
            raise RuntimeError(json.dumps(res['error'])[:2000])
        json.dump(res, open(cp, 'w'))
    res = json.load(open(cp))
    dps = res['raidMetrics']['dps']
    return dps['avg'], dps.get('stdev', 0), res


def runmany(setups, workers=None, **kw):
    workers = workers or os.cpu_count()
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(lambda s: run(s, **kw), setups))
