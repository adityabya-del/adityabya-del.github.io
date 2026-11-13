#!/usr/bin/env python3
"""Adds internal links so Google can find pages it has not indexed. Safe to run again (skips what is already there).
  python3 tools/add_internal_links.py --test    # only count
  python3 tools/add_internal_links.py --write
Adds: (1) guide links on train / Hindi train / route / station / hub pages and between guides,
(2) station links in every train timetable, (3) links to routes that no train page links to,
(4) English <-> Hindi links between the two versions of each train page.
Re-run after ANY rebuild of train / route / station pages (see CLAUDE.md)."""
import os, re, sys, html, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITE = '--write' in sys.argv
U = 'style="text-decoration:underline"'
def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s):
    if WRITE: open(p, 'w', encoding='utf-8').write(s)
def pg(rel): return os.path.join(ROOT, rel, 'index.html')

guides = []
for g in sorted(os.listdir(os.path.join(ROOT, 'guides'))):
    if os.path.exists(pg('guides/' + g)):
        h = re.search(r'<h1>([^<]*)</h1>', rd(pg('guides/' + g)))
        if h: guides.append((g, h.group(1)))

def guide_block(hi, skip=None):
    items = ''.join('<a href="/guides/%s/">%s</a>' % (g, t) for g, t in guides if g != skip)
    head = 'टिकट बुकिंग और रिफंड गाइड (अंग्रेज़ी में)' if hi else ('More guides' if skip else 'Booking and refund guides')
    return '<h2 id="il-guides">%s</h2><div class="links">%s</div>\n' % (head, items)

def insert_before_footer(s, block):
    k = s.rfind('</div>\n<footer>')
    return s if k < 0 else s[:k] + block + s[k:]

stats = collections.Counter()
station_ok = set(os.listdir(os.path.join(ROOT, 'station')))
trains = sorted(d for d in os.listdir(os.path.join(ROOT, 'train')) if os.path.exists(pg('train/' + d)))
hitrains = set(d for d in os.listdir(os.path.join(ROOT, 'hi', 'train')) if os.path.exists(pg('hi/train/' + d)))

# --- routes that no train page links to, and the trains that run them
routes = {}
for d in os.listdir(os.path.join(ROOT, 'route')):
    if not os.path.exists(pg('route/' + d)): continue
    s = rd(pg('route/' + d))
    h = re.search(r'<h1>Trains from (.*?) to (.*?)</h1>', s)
    if not h: continue
    routes[d] = (html.unescape(h.group(1)), html.unescape(h.group(2)), re.findall(r'href="/train/(\d+)/"', s.split('</table>')[0]))
linked = set()
for t in trains:
    linked.update(re.findall(r'href="/route/([^/"]+)/"', rd(pg('train/' + t))))
missing = {d: v for d, v in routes.items() if d not in linked}
add_for = collections.defaultdict(list)   # train -> [(slug, from, to)]
for d, (a, b, ts) in missing.items():
    for t in ts: add_for[t].append((d, a, b))
print('routes:', len(routes), 'not linked from any train page:', len(missing), 'trains to receive route links:', len(add_for))

def process(path, kind, num=None):
    s = rd(path); o = s
    hi = kind == 'hi'
    if kind in ('train', 'hi'):
        # station links in timetable
        def st(m):
            code = m.group(2).lower()
            if code in station_ok:
                stats['station links'] += 1
                return '<td><a %s href="/station/%s/">%s</a> <small>(%s)</small></td>' % (U, code, m.group(1), m.group(2))
            return m.group(0)
        s = re.sub(r'<td>([^<]+) <small>\(([A-Za-z0-9]+)\)</small></td>', st, s)
        # extra route links
        hd = '<h2>इस ट्रेन के रूट</h2><div class="links">' if hi else '<h2>Routes this train runs</h2><div class="links">'
        i = s.find(hd)
        if i >= 0:
            j = s.find('</div>', i)
            blk = s[i:j]
            new = ''.join('<a href="/route/%s/">%s</a>' % (d, ('%s से %s' if hi else '%s to %s') % (e(a), e(b)))
                          for d, a, b in add_for.get(num, []) if '/route/%s/' % d not in blk)
            if new:
                stats['route links'] += new.count('<a ')
                s = s[:j] + new + s[j:]
        # language link
        if 'il-lang' not in s:
            other = ('/train/%s/' % num, 'View this page in English') if hi else ('/hi/train/%s/' % num, 'इस पेज को हिंदी में देखें')
            if (not hi and num in hitrains) or hi:
                m = re.search(r'<a class="btn"[^>]*>[^<]*</a>', s)
                if m:
                    s = s[:m.end()] + '\n<p class="il-lang" style="margin:10px 0 0"><a %s href="%s">%s</a></p>' % (U, other[0], other[1]) + s[m.end():]
                    stats['language links'] += 1
    if kind != 'guide' and 'id="il-guides"' not in s:
        s = insert_before_footer(s, guide_block(hi)); stats['guide blocks'] += 1
    if s != o: wr(path, s); stats['pages changed'] += 1
e = html.escape
for t in trains: process(pg('train/' + t), 'train', t)
for t in hitrains: process(pg('hi/train/' + t), 'hi', t)
for d in routes: process(pg('route/' + d), 'route')
for d in os.listdir(os.path.join(ROOT, 'station')):
    if os.path.exists(pg('station/' + d)): process(pg('station/' + d), 'station')
process(pg('train'), 'hub')
for g, _ in guides:
    p = pg('guides/' + g); s = rd(p)
    if 'id="il-guides"' not in s:
        wr(p, insert_before_footer(s, guide_block(False, skip=g))); stats['pages changed'] += 1; stats['guide blocks'] += 1
print(dict(stats), '(WRITTEN)' if WRITE else '(dry run, nothing written)')
