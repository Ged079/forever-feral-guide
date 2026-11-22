#!/usr/bin/env python3
"""Lay out local module checkouts as a GOPROXY=file:// directory (<mod>/@v/{list,<ver>.info,<ver>.mod,<ver>.zip}).
Go checks every zip and go.mod it fetches from here against go.sum as usual.

    make_file_proxy.py OUT  MODULE VERSION DIR  [MODULE VERSION DIR ...]
"""
import json, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gosum_check import files  # noqa: E402

out, rest = sys.argv[1], sys.argv[2:]

for i in range(0, len(rest), 3):
    mod, ver, root = rest[i:i + 3]
    d = os.path.join(out, mod, '@v')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'list'), 'a') as f:
        f.write(ver + '\n')
    json.dump({'Version': ver, 'Time': '2020-01-01T00:00:00Z'}, open(os.path.join(d, ver + '.info'), 'w'))
    open(os.path.join(d, ver + '.mod'), 'wb').write(open(os.path.join(root, 'go.mod'), 'rb').read())
    with zipfile.ZipFile(os.path.join(d, ver + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(files(root)):
            z.write(os.path.join(root, rel), f'{mod}@{ver}/{rel}')
    print('added', mod, ver)
