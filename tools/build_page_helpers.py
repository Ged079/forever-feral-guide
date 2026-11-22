"""Shared bits for the guide pages: item sources, enchant names, embedded icons."""
import base64, io, json, os, subprocess
from PIL import Image
import analyze as a
import content as C

ITEMS = {i['id']: i for i in a.DB['items']}
ZONES = {z['id']: z['name'] for z in a.DB['zones']}
FACS = {f['id']: f['name'] for f in a.DB['factions']}
REP = {4: 'Neutral', 5: 'Friendly', 6: 'Honored', 7: 'Revered', 8: 'Exalted'}
SLOTTYPE = {'head': 1, 'neck': 2, 'shoulder': 3, 'back': 4, 'chest': 5, 'wrist': 6, 'hands': 7, 'waist': 8, 'legs': 9,
            'feet': 10, 'finger1': 11, 'finger2': 11, 'trinket1': 12, 'trinket2': 12, 'main_hand': 13, 'off_hand': 13, 'ranged': 14}
AV_ZONES = ('Alterac Valley', 'Alterac Mountains')
ICON_REPO = os.environ.get('ICON_REPO', os.path.expanduser('~/wow-ui-textures'))  # sparse clone of github.com/Gethe/wow-ui-textures


def enchant_name(eid, slot):
    if not eid:
        return ''
    t = SLOTTYPE[slot]
    names = [e['name'] for e in a.DB['enchants'] if e['effectId'] == eid and (e.get('type') == t or t in e.get('extraTypes', []))]
    n = names[0] if names else next((e['name'] for e in a.DB['enchants'] if e['effectId'] == eid), '')
    return n.replace('Enchant ', '').replace('2H Weapon - ', '').replace('Weapon - ', '')


def source(iid):
    it = ITEMS[iid]
    out = []
    for src in it.get('sources', []):
        k, v = next(iter(src.items()))
        v = v or {}
        if k == 'drop':
            z = ZONES.get(v.get('zoneId'))
            out.append(f"Drop{': ' + z if z else ''}")
        elif k == 'quest':
            out.append(f"Quest: {v.get('name', '')}")
        elif k == 'soldBy':
            out.append(f"Vendor: {v.get('npcName', '')}" + (f" ({ZONES[v['zoneId']]})" if v.get('zoneId') in ZONES else ''))
        elif k == 'crafted':
            out.append(f"Crafted: {C.PROFESSIONS.get(v.get('profession'), 'profession')}")
        elif k == 'rep':
            out.append(f"Reputation: {FACS.get(v.get('repFactionId'), '')} {REP.get(v.get('repLevel'), '')}".strip())
    if not out:
        out = ['World drop (Auction House)' if it.get('randomSuffixOptions') or iid < 200000 else 'No source listed']
    return list(dict.fromkeys(out))[:2]


def kinds(iid):
    """Source groups for the page's filter chips."""
    ks = set()
    for src in ITEMS[iid].get('sources', []):
        k, v = next(iter(src.items()))
        v = v or {}
        if k == 'drop':
            ks.add('dungeon' if v.get('zoneId') else 'world')
        elif k == 'quest':
            ks.add('quest')
        elif k == 'crafted':
            ks.add('crafted')
        elif k == 'rep':
            ks.add('rep')
        elif k == 'soldBy':
            ks.add('av' if ZONES.get(v.get('zoneId')) in AV_ZONES else 'vendor')
    return sorted(ks or {'world'})


def hard_to_get(iid):
    """True when every way to get the item is Alterac Valley reputation or exalted reputation."""
    srcs = ITEMS[iid].get('sources', [])
    if not srcs:
        return False
    exalted = any(next(iter(x)) == 'rep' and (next(iter(x.values())) or {}).get('repLevel', 0) >= 8 for x in srcs)
    for src in srcs:
        k, v = next(iter(src.items()))
        v = v or {}
        if k == 'soldBy' and ZONES.get(v.get('zoneId')) in AV_ZONES:
            continue
        if k == 'rep' and v.get('repLevel', 0) >= 8:
            continue
        if k == 'soldBy' and exalted:
            continue  # the reputation's own vendor
        if k == 'pvp':
            continue
        return False
    return True


def load_icons(names, size=36, quality=78):
    names = {n.lower() for n in names if n}
    files = subprocess.run(['git', 'ls-tree', '--name-only', 'HEAD', 'ICONS/'], cwd=ICON_REPO, capture_output=True, text=True).stdout.split('\n')
    idx = {f.split('/', 1)[1].rsplit('.', 1)[0].lower(): f for f in files if '/' in f}
    want = [idx[n] for n in names if n in idx]
    cur = [c for c in open(os.path.join(ICON_REPO, '.git/info/sparse-checkout')).read().split('\n') if c]
    missing = [w for w in want if not os.path.exists(os.path.join(ICON_REPO, w))]
    if missing:
        p = subprocess.run(['git', 'sparse-checkout', 'set', '--no-cone', '--stdin'], cwd=ICON_REPO, input='\n'.join(cur + missing), text=True)
        subprocess.run(['git', 'checkout', '-q', 'HEAD'], cwd=ICON_REPO)
    out = {}
    for n in names:
        if n in idx and os.path.exists(os.path.join(ICON_REPO, idx[n])):
            im = Image.open(os.path.join(ICON_REPO, idx[n])).convert('RGB').resize((size, size), Image.LANCZOS)
            b = io.BytesIO(); im.save(b, 'JPEG', quality=quality)
            out[n] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    return out
