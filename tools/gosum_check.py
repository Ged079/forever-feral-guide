#!/usr/bin/env python3
"""Compute Go's h1: module hash (golang.org/x/mod/sumdb/dirhash Hash1 over the module zip file set)
for a local checkout, and compare it with the entry in a go.sum.

    gosum_check.py GO_SUM MODULE VERSION DIR
"""
import base64, hashlib, os, sys

VCS = {'.git', '.hg', '.svn', '.bzr'}


def files(root):
    out = []
    for d, dirs, fs in os.walk(root):
        rel_d = os.path.relpath(d, root)
        if rel_d != '.' and os.path.exists(os.path.join(d, 'go.mod')):
            dirs[:] = []  # nested module
            continue
        dirs[:] = [x for x in dirs if x not in VCS]
        for f in fs:
            p = os.path.join(d, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            rel = os.path.relpath(p, root).replace(os.sep, '/')
            parts = rel.split('/')
            # vendored packages are left out of module zips (vendor/modules.txt at the root stays)
            if 'vendor' in parts[:-1]:
                i = parts.index('vendor')
                if not (i == 0 and len(parts) == 2 and parts[1] == 'modules.txt') and len(parts) - i > 2:
                    continue
            out.append(rel)
    return out


def h1(prefix, root, names):
    lines = []
    for n in sorted(prefix + x for x in names):
        with open(os.path.join(root, n[len(prefix):]), 'rb') as fh:
            lines.append(f'{hashlib.sha256(fh.read()).hexdigest()}  {n}\n')
    return 'h1:' + base64.b64encode(hashlib.sha256(''.join(lines).encode()).digest()).decode()


def main():
    gosum, mod, ver, root = sys.argv[1:5]
    want = {}
    for line in open(gosum):
        m, v, h = line.split()
        if m == mod and v in (ver, ver + '/go.mod'):
            want[v] = h
    got_zip = h1(f'{mod}@{ver}/', root, files(root))
    # the go.mod hash covers just go.mod, named "<mod>@<ver>/go.mod"
    lines = f'{hashlib.sha256(open(os.path.join(root, "go.mod"), "rb").read()).hexdigest()}  go.mod\n'
    got_mod = 'h1:' + base64.b64encode(hashlib.sha256(lines.encode()).digest()).decode()
    ok = want.get(ver) == got_zip and want.get(ver + '/go.mod') == got_mod
    print(f"{'OK  ' if ok else 'FAIL'} {mod}@{ver}  zip {got_zip} (go.sum {want.get(ver)})  go.mod {'match' if want.get(ver + '/go.mod') == got_mod else 'MISMATCH'}")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
