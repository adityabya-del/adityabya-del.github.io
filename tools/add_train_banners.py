#!/usr/bin/env python3
"""Puts a banner image on every /train/<number>/ page, every /hi/train/<number>/ page (same banner as its English page) and the /train/ list page (banner 1), rotating through the 6 banners in
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
ALT_HI = ['ClearBerth: PNR स्टेटस, लाइव ट्रैकिंग और अलर्ट',
          'ClearBerth AC 3 Tier: PNR स्टेटस, लाइव ट्रैकिंग और अलर्ट',
          'ClearBerth 1st AC Coupe: PNR स्टेटस, लाइव ट्रैकिंग और अलर्ट',
          'ClearBerth AC 2 Tier: PNR स्टेटस, लाइव ट्रैकिंग और अलर्ट',
          'ClearBerth 2nd Class: PNR स्टेटस, लाइव ट्रैकिंग और अलर्ट',
          'ClearBerth 2nd Sitting: PNR स्टेटस, लाइव ट्रैकिंग और अलर्ट']
nums = sorted((d for d in os.listdir(os.path.join(ROOT, 'train')) if d.isdigit()), key=int)
done = skipped = 0
def add(path, k, alts, label):
    global done, skipped
    if not os.path.exists(path): return
    s = open(path, encoding='utf-8').read()
    if 'class="tb"' in s: skipped += 1; return
    img = ('<img class="tb" src="/shots/train-banner-%d.jpg" alt="%s" width="1280" height="720" decoding="async" '
           'style="display:block;width:100%%;height:auto;border-radius:12px;margin:16px 0">\n') % (k + 1, alts[k])
    m = re.search(r'<p class="lead"[^>]*>.*?</p>\n?', s, re.S)
    if not m: print('no lead paragraph:', label); return
    s = s[:m.end()] + img + s[m.end():]
    if WRITE: open(path, 'w', encoding='utf-8').write(s)
    done += 1
for i, n in enumerate(nums):
    k = i % 6
    add(os.path.join(ROOT, 'train', n, 'index.html'), k, ALT, n)
    add(os.path.join(ROOT, 'hi', 'train', n, 'index.html'), k, ALT_HI, 'hi/' + n)
add(os.path.join(ROOT, 'train', 'index.html'), 0, ALT, 'train list')
print('trains:', len(nums), 'banners added:', done, 'already had one:', skipped, '(WRITTEN)' if WRITE else '(dry run)')
