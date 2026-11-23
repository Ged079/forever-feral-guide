#!/usr/bin/env python3
"""The link-preview images (1200x630) for the guide and the BiS page: ../docs/og.png and ../docs/bis/og.png.

Needs Playwright with Chromium. FONT_DIR is an npm folder with @fontsource/barlow and @fontsource/barlow-condensed
(npm i @fontsource/barlow @fontsource/barlow-condensed); without it the card falls back to the system sans.

    og_image.py
"""
import json, os
from playwright.sync_api import sync_playwright
import build_page_helpers as H
import sim

FONT_DIR = os.environ.get('FONT_DIR', os.path.expanduser('~/fonts/node_modules/@fontsource'))
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')


def fonts():
    out = []
    for fam, pkg, ws in (('Barlow', 'barlow', (400, 600)), ('Barlow Condensed', 'barlow-condensed', (600, 700))):
        for w in ws:
            f = os.path.join(FONT_DIR, pkg, 'files', f'{pkg}-latin-{w}-normal.woff2')
            if os.path.exists(f):
                out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(file://{f})}}")
    return ''.join(out)


CSS = """
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#17181c;color:#eceae5;font-family:Barlow,system-ui,sans-serif;overflow:hidden}
.card{position:absolute;inset:0;padding:64px 72px;display:grid;grid-template-columns:1fr 360px;gap:48px;align-items:center}
.card:before{content:"";position:absolute;inset:0;border-top:10px solid #ec7a50}
.k{font:600 26px 'Barlow Condensed',sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#ec7a50}
h1{font:700 96px/0.95 'Barlow Condensed',sans-serif;margin:14px 0 22px;letter-spacing:-.01em}
p{font-size:30px;line-height:1.3;color:#b9b6ae;max-width:620px}
.tiles{display:flex;gap:14px;margin-top:34px;white-space:nowrap}
.t{border:2px solid #34363d;border-radius:14px;padding:12px 18px}
.t b{display:block;font:700 40px 'Barlow Condensed',sans-serif;color:#fff}.t span{font-size:20px;color:#9c9a93}
.art{display:grid;place-items:center}
.big{width:300px;height:300px;border-radius:36px;border:4px solid #ec7a50;display:block}
.grid{display:grid;grid-template-columns:repeat(4,78px);gap:12px}
.grid img{width:78px;height:78px;border-radius:12px;border:2px solid #4a4d55;display:block}
.site{position:absolute;right:72px;bottom:40px;font-size:22px;color:#7d7b75}
"""


def page(kicker, title, sub, tiles, art):
    t = ''.join(f'<div class="t"><b>{v}</b><span>{l}</span></div>' for v, l in tiles)
    return (f'<html><head><style>{fonts()}{CSS}</style></head><body><div class="card"><div><div class="k">{kicker}</div>'
            f'<h1>{title}</h1><p>{sub}</p><div class="tiles">{t}</div></div><div class="art">{art}</div></div>'
            f'<div class="site">ged079.github.io/forever-feral-guide</div></body></html>')


def main():
    rank = json.load(open(sim.data('rank/alliance.json')))
    gear = json.load(open(sim.data('gear/cat_alliance.json')))['gear']
    icons = H.load_icons({'ability_druid_catform'} | {H.item_icon(g['id']) for g in gear})
    guide = page('WoW Forever · Feral Cat', 'Forever Feral Guide',
                 'Talents, rotation, consumables and gear. Every number simmed in WoWSims Forever.',
                 [(f'{round(rank["base"])} DPS', 'Cat build'), ('Every', 'talent tested'), ('16', 'gear slots ranked')],
                 f'<img class="big" src="{icons["ability_druid_catform"]}">')
    tiles = ''.join(f'<img src="{icons[H.item_icon(g["id"])]}">' for g in gear[:16])
    bis = page('WoW Forever · Feral Cat', 'Pre-raid best in slot',
               'Every slot ranked by the sim, with faction, budget and source filters, plus an upgrade finder for your gear.',
               [(f'{round(rank["base"])} DPS', 'best-in-slot set'), ('±1.7', 'sim margin')],
               f'<div class="grid">{tiles}</div>')
    os.makedirs(os.path.join(sim.DOCS, 'bis'), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1200, 'height': 630})
        for html, out in ((guide, 'og.png'), (bis, 'bis/og.png')):
            tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.og.html')  # a file page may load the local fonts
            open(tmp, 'w').write(html)
            pg.goto('file://' + tmp)
            pg.wait_for_timeout(500)
            pg.screenshot(path=os.path.join(sim.DOCS, out))
            os.remove(tmp)
        b.close()


if __name__ == '__main__':
    main()
