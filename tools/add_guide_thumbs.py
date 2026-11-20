#!/usr/bin/env python3
"""Small photo thumbnail on the right of each card on /guides/ (20 Nov 2026).
Makes /shots/guide-<slug>-t.webp (176x176, centre crop of the guide photo) and adds it to each card.
Safe to run twice. Re-run after any change to guides/index.html or a guide photo:
  python3 tools/add_guide_thumbs.py"""
import os, re
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = ('<style id="gthumb-css">.cards a{display:grid;grid-template-columns:1fr auto;column-gap:16px;align-items:center}'
       '.cards a b{grid-column:1;grid-row:1}.cards a span{grid-column:1;grid-row:2}'
       '.cards a .gthumb{grid-column:2;grid-row:1/3;width:88px;height:88px;border-radius:14px;object-fit:cover;display:block}'
       '@media(max-width:560px){.cards a .gthumb{width:64px;height:64px;border-radius:12px}}</style>')
p = os.path.join(ROOT, 'guides', 'index.html')
h = open(p, encoding='utf-8').read()
h = re.sub(r'<img class="gthumb"[^>]*>', '', h)
h = re.sub(r'<style id="gthumb-css">.*?</style>', '', h, flags=re.S)
n = 0
def card(m):
    global n
    slug = m.group(1)
    src = os.path.join(ROOT, 'shots', 'guide-%s.webp' % slug)
    if not os.path.exists(src):
        print('no photo', slug); return m.group(0)
    out = os.path.join(ROOT, 'shots', 'guide-%s-t.webp' % slug)
    ImageOps.fit(Image.open(src).convert('RGB'), (176, 176), Image.LANCZOS).save(out, 'WEBP', quality=78)
    n += 1
    return m.group(0) + '<img class="gthumb" src="/shots/guide-%s-t.webp" alt="" width="88" height="88" loading="lazy">' % slug
h = re.sub(r'<a href="/guides/([a-z0-9-]+)/"><b>.*?</b><span>.*?</span>', card, h)
h = h.replace('</head>', CSS + '</head>', 1)
open(p, 'w', encoding='utf-8').write(h)
print('thumbs on', n, 'cards')
