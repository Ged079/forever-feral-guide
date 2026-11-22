# Forever Feral Guide

A Feral Cat guide for WoW Forever (Phase 1, level 60): builds, talent values, the rotation as plain steps,
consumables, raid buffs, races, stat weights and the hit cap. Every number is a WoWSims Forever sim.

Open `docs/index.html` in a browser. It is one self-contained page.

## Where the numbers come from

WoWSims Forever master `a73af71` (2026-11-22), the sim's Adaptive Cat APL and its pre-raid preset gear: a Tauren,
full raid buffs and consumables, Greater Blessing of Kings as the only blessing, a level 63 Dragonkin boss,
150–350 ms reaction time, a 180 s fight, 3000 iterations on seed 1. A talent's, consumable's or buff's worth is the
build's DPS minus the same build without it. Stat weights use ±steps at 20,000 iterations.

## Rebuilding

Needs a `wowsims/forever` checkout with its CLI built (`make bin/wowsimcli`).

```sh
export FOREVER=~/forever                  # the checkout
export WOWSIMCLI=$FOREVER/bin/wowsimcli   # optional, this is the default
cd tools
python3 analyze.py            # all sims -> ../setup/results.json (or name parts: builds talents cons buffs races stats hit)
python3 build_page.py         # ../setup/*.json + content.py + template.html -> ../docs/index.html
```

- `setup/defaults.siml` is the full setup; `setup/defaults.json` is what `wowsimcli siml parse -json` makes of it.
- `tools/content.py` holds the prose; numbers come only from `results.json`.
- `tools/gosum_check.py` and `tools/make_file_proxy.py` build the sim's Go dependencies from GitHub when
  proxy.golang.org is unreachable, checking each against the sim's own `go.sum` first.
