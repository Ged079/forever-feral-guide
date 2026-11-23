# Forever Feral Guide

A Feral Cat guide for WoW Forever (Phase 1, level 60): builds, talent values, the rotation as plain steps,
consumables, raid buffs, races, stat weights and the hit cap. Every number is a WoWSims Forever sim.

Website: https://ged079.github.io/forever-feral-guide/ (GitHub Pages from `docs/` on `main`), with the pre-raid BiS
page at `/bis/`. Both pages are single self-contained HTML files, so `docs/index.html` and `docs/bis/index.html` also open
straight from disk.

## Where the numbers come from

WoWSims Forever master `a73af71` (2026-11-22), the sim's Adaptive Cat APL:
full raid buffs and consumables, Greater Blessing of Kings as the only blessing, a level 63 Dragonkin boss,
150–350 ms reaction time, a 180 s fight, 3000 iterations on seed 1. Gear is the searched pre-raid set (`setup/gear/cat_alliance.json`, Night Elf). A talent's, consumable's or buff's worth is the
build's DPS minus the same build without it. Stat weights use ±steps at 20,000 iterations.

## How the builds and rotation were found

- `tools/search.py` hill-climbs talent builds: every legal move of 1, 2, 3 or 5 points (row requirements, prerequisites,
  51 points) is simmed at 1,000 iterations, and the best is kept only if it still wins at 6,000 on another seed.
  Cat and Hybrid start from the sim's presets (Hybrid must keep Thick Hide, Lacerate and Primal Bite);
  `tools/restart.py` scrambles a build first and climbs back. Logs in `setup/search/`.
- `tools/tune.py` sweeps the Adaptive Cat APL's numeric variables and tries reorderings. The sim's values were
  already the best; skipping Innervate helps only on fights of 3 minutes or less. Logs in `setup/tune/`.
- `tools/gear.py` searches pre-raid gear per faction: Phase 1 cloth/leather, druid weapons and idols, no raid loot,
  raid reputation, Onyxia-head quests or PvP rank gear; one-slot swaps until nothing helps, then every pair of slots,
  then the weapon enchant. Results in `setup/gear/`. Both builds were searched again on the new gear and held.
- `tools/alternatives.py` sims the other builds shown on the page.
- `tools/rank.py` ranks every shortlisted item per slot against the BiS set (3,000 iterations, same seed); `tools/build_bis.py` turns that into the BiS page. Icons come from a sparse clone of github.com/Gethe/wow-ui-textures (`ICON_REPO`).
- `setup/results_presets.json` and `setup/results_presetgear.json` hold the earlier runs (preset builds; found builds on preset gear).

## Rebuilding

Needs a `wowsims/forever` checkout with its CLI built (`make bin/wowsimcli`) and, for the item and talent icons,
a sparse clone of github.com/Gethe/wow-ui-textures (the scripts check out the icons they need).

```sh
export FOREVER=~/forever                  # the sim checkout
export WOWSIMCLI=$FOREVER/bin/wowsimcli   # optional, this is the default
export ICON_REPO=~/wow-ui-textures        # optional, this is the default
cd tools
python3 search.py cat cat      # optional: redo the talent search      -> ../setup/search/
python3 tune.py cat <talents>  # optional: redo the rotation sweep     -> ../setup/tune/
python3 gear.py cat_alliance alliance cat   # optional: redo the gear search (and cat_horde horde cat) -> ../setup/gear/
python3 analyze.py             # values, weights, hit curve            -> ../setup/results.json
python3 extra_weights.py       # Int, Spirit, MP5, Feral AP, weapon DPS -> ../setup/extra_weights.json
python3 alternatives.py        # the other builds on the page          -> ../setup/alternatives.json
python3 rank.py                # per-slot ranking, both factions       -> ../setup/rank/
python3 talent_ranks.py        # every rank of every talent on Cat     -> ../setup/talent_ranks.json (talent calculator)
python3 extra_sims.py          # side questions, not on the page: bear-weave, powershift, fight length, AoE -> ../setup/extra_sims.json
python3 og_image.py            # link-preview images (needs Playwright) -> ../docs/og.png, ../docs/bis/og.png
python3 build_page.py          # the guide   -> ../docs/index.html
python3 build_bis.py           # the BiS page -> ../docs/bis/index.html
```

`LINKS=artifact python3 build_page.py` (and the same for `build_bis.py`) builds the copies hosted on claude.ai, whose
links to each other need absolute URLs; the default build links them relatively, for the website.

Sim results are cached in `tools/cache/` by request, so rebuilding the pages without changing a setup runs no sims.
All paths are relative to the scripts (`sim.SETUP`, `sim.DOCS`), so they run from any folder.

- `setup/SIM_VERSION` is the wowsims/forever commit the current numbers come from; update it after a re-run.
- `setup/defaults.siml` is the full setup; `setup/defaults.json` is what `wowsimcli siml parse -json` makes of it.
  `setup/prebis.gear.siml` is the sim's own pre-raid gear, used for `results_presetgear.json`.
- The BiS page's upgrade finder reads every wearable item from the sim's item data, the per-slot ranking and the stat
  weights; plain set bonuses come from the sim's set table.
- `tools/content.py` holds the prose; numbers come only from the JSON in `setup/`.
- `tools/template.html` and `tools/bis_template.html` are the two pages; the build scripts embed the data and icons,
  so each output is one self-contained file.
- `tools/gosum_check.py` and `tools/make_file_proxy.py` build the sim's Go dependencies from GitHub when
  proxy.golang.org is unreachable, checking each against the sim's own `go.sum` first.
