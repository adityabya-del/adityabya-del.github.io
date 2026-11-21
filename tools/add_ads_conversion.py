#!/usr/bin/env python3
"""Google Ads website conversion on every page (21 Nov 2026).

Adds the Google Ads tag (AW-18479728139) next to the existing GA4 config, and
a click listener: a tap on any App Store / Google Play link sends
  - GA4 event  store_click  {store: app_store | google_play}
  - Google Ads conversion "Website: App Store or Google Play tap"
Safe to run twice (skips pages that already have it). Run with --write.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = "gtag('config', 'G-J9D9G65GNJ');"
MARK = "/*adsconv*/"
NEW = OLD + (
    MARK + "gtag('config', 'AW-18479728139');"
    "document.addEventListener('click',function(e){"
    "var a=e.target&&e.target.closest&&e.target.closest('a[href*=\"apps.apple.com\"],a[href*=\"play.google.com\"]');"
    "if(!a)return;var s=a.href.indexOf('apple.com')>-1?'app_store':'google_play';"
    "gtag('event','store_click',{store:s});"
    "gtag('event','conversion',{send_to:'AW-18479728139/-2OGCNGux7wdEIuM6etE',value:1.0,currency:'INR'});"
    "},true);"
)
write = '--write' in sys.argv
done = skipped = 0
for dp, dn, fn in os.walk(ROOT):
    if '/.git' in dp or '/node_modules' in dp:
        continue
    for f in fn:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        s = open(p, encoding='utf-8').read()
        if MARK in s or OLD not in s:
            skipped += 1
            continue
        if write:
            open(p, 'w', encoding='utf-8').write(s.replace(OLD, NEW, 1))
        done += 1
print(f"{'updated' if write else 'would update'} {done} pages, skipped {skipped}")
