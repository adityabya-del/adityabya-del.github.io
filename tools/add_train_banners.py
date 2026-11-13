#!/usr/bin/env python3
"""Puts a banner image on every /train/<number>/ page, rotating through the 6 banners in
/shots/train-banner-1..6.jpg in train-number order (1,2,3,4,5,6,1,2...). Skips pages that already have one.
  python3 tools/add_train_banners.py --test | --write
Re-run after any rebuild of the train pages (see CLAUDE.md)."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITE = '--write' in sys.argv
ALT = ['ClearBerth: PNR status, live tracking and alerts for your train journey',
       'ClearBerth for AC 3 Tier: PNR status, live tracking and alerts',
       'ClearBerth for 1st AC Coupe: PNR status, live tracking and alerts',
       'ClearBerth for AC 2 Tier: PNR status, live tracking and alerts',
       'ClearBerth for 2nd Class: PNR status, live tracking and alerts',
       'ClearBerth for 2nd Sitting: PNR status, live tracking and alerts']
nums = sorted((d for d in os.listdir(os.path.join(ROOT, 'train')) if d.isdigit()), key=int)
done = skipped = 0
for i, n in enumerate(nums):
    p = os.path.join(ROOT, 'train', n, 'index.html')
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    if 'class="tb"' in s: skipped += 1; continue
    k = i % 6
    img = ('<img class="tb" src="/shots/train-banner-%d.jpg" alt="%s" width="1280" height="720" decoding="async" '
           'style="display:block;width:100%%;height:auto;border-radius:12px;margin:16px 0">\n') % (k + 1, ALT[k])
    m = re.search(r'<p class="lead">.*?</p>\n?', s, re.S)
    if not m: print('no lead paragraph:', n); continue
    s = s[:m.end()] + img + s[m.end():]
    if WRITE: open(p, 'w', encoding='utf-8').write(s)
    done += 1
print('trains:', len(nums), 'banners added:', done, 'already had one:', skipped, '(WRITTEN)' if WRITE else '(dry run)')
