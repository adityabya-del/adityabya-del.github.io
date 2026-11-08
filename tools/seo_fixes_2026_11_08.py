#!/usr/bin/env python3
"""One-off SEO pass from the 8 Nov 2026 Search Console review (run from repo root after
tools/refresh_route_pages.py --write):
  1. restore 404'd route pages that have >=9 trains (the site's rule for a route page)
  2. station pages with 3 or fewer trains -> noindex,follow and out of the sitemap
  3. station pages link to their busiest route pages
  4. train page title/description use the searched wording ("<number> train running status")
  5. WhatsApp share link on train and route pages
  6. sitemap: new routes, lastmod for changed pages
"""
import glob, html, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refresh_route_pages as R

ROOT = R.ROOT
TODAY = '2026-11-08'
e = html.escape
UA = R.UA
T = R.load_trains()
P, NAMES = R.pair_trains(T)
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf-8').read()


def wr(p, s):
    open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def split_slug(sl):
    parts = sl.split('-')
    for i in range(1, len(parts)):
        if parts[i] == 'to' and ('-'.join(parts[:i]), '-'.join(parts[i + 1:])) in P:
            return '-'.join(parts[:i]), '-'.join(parts[i + 1:])
    return None


existing = set(open(os.path.join(ROOT, '_gen/baseline_routes.txt')).read().split())  # routes that existed before this pass
want = [s for s in open(os.path.join(ROOT, '_gen/gsc_404_routes.txt')).read().split() if s not in existing]
new = []
for sl in want:
    ab = split_slug(sl)
    if ab and len(P[ab]) >= 1:
        new.append((sl, ab))
THIN_NEW = {sl for sl, ab in new if len(P[ab]) < 9}
final = existing | {s for s, _ in new}
count = {}
by_from = {}
for sl in final:
    ab = split_slug(sl)
    if ab:
        count[sl] = len(P[ab])
        by_from.setdefault(ab[0], []).append(sl)

# 1. restore routes ---------------------------------------------------------------
TPL_SLUG = 'new-delhi-to-bhopal-jn'
tpl = re.sub(r'<p style="margin-top:18px"><a [^>]*href="https://wa.me/[^"]*"[^>]*>Share on WhatsApp</a></p>\n', '', rd('route/%s/index.html' % TPL_SLUG))
# the template page may already carry a share link from an earlier run; strip it so each page gets its own
TA, TB = 'New Delhi', 'Bhopal Jn'


def more_routes(a_slug, A, self_sl):
    cand = sorted((s for s in by_from.get(a_slug, []) if s != self_sl), key=lambda s: (-count[s], s))[:8]
    links = ''.join('<a href="/route/%s/">%s to %s</a>' % (s, e(A), e(NAMES[split_slug(s)[1]])) for s in cand)
    return '<h2>More routes from %s</h2><div class="links">%s</div>' % (e(A), links) if cand else ''


for sl, (a, b) in new:
    A, B = NAMES[a], NAMES[b]
    km = 0
    rev = rd('route/%s-to-%s/index.html' % (b, a)) if os.path.exists(os.path.join(ROOT, 'route/%s-to-%s/index.html' % (b, a))) else ''
    m = re.search(r'is about (\d+) km', rev)
    km = int(m.group(1)) if m else 0
    s = tpl
    n = len(P[(a, b)])
    title = '%s to %s Trains: Timetable and Live Status | ClearBerth' % (A, B)
    desc = '%d trains from %s to %s: departure and arrival times, journey time and live running status for each. Free on ClearBerth.' % (n, A, B)
    s = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % e(title, quote=False), s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + e(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + e(title), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + e(desc), s, count=1)
    s = re.sub(r'(<link rel="canonical" href="https://clearberth.app/route/)[^"]*', lambda m: m.group(1) + sl + '/', s, count=1)
    s = re.sub(r'(<meta property="og:url" content="https://clearberth.app/route/)[^"]*', lambda m: m.group(1) + sl + '/', s, count=1)
    ld = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['
          '{"@type": "ListItem", "position": 1, "name": "ClearBerth", "item": "https://clearberth.app/"}, '
          '{"@type": "ListItem", "position": 2, "name": "Trains", "item": "https://clearberth.app/train/"}, '
          '{"@type": "ListItem", "position": 3, "name": "%s to %s", "item": "https://clearberth.app/route/%s/"}]}</script>') % (A, B, sl)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: ld, s, count=1, flags=re.S)
    s = re.sub(r'(<p class="crumb">.*?/ )[^<]*(</p>)', lambda m: m.group(1) + '%s to %s' % (e(A), e(B)) + m.group(2), s, count=1)
    s = re.sub(r'<h1>.*?</h1>', lambda m: '<h1>Trains from %s to %s</h1>' % (e(A), e(B)), s, count=1)
    if (b + '-to-' + a) in final:
        rp = '<p style="margin-top:14px"><a %s href="/route/%s-to-%s/">Trains from %s to %s</a></p>' % (UA, b, a, e(B), e(A))
    else:
        rp = ''
    s = re.sub(r'<p style="margin-top:14px"><a [^>]*href="/route/[^"]*">Trains from [^<]*</a></p>', lambda m: rp, s, count=1)
    mr = more_routes(a, A, sl)
    s = re.sub(r'<h2>More routes from .*?</div>', lambda m: mr, s, count=1, flags=re.S)
    s = R.refresh_page(s, A, B, P[(a, b)], km)
    if not (TPL_SLUG not in s and 'bhopal-jn-to-new-delhi' not in s or sl == TPL_SLUG):
        print(sl, [m.start() for m in re.finditer('bhopal-jn', s)][:3], s[s.index('bhopal-jn')-150:s.index('bhopal-jn')+60]); sys.exit(1)
    os.makedirs(os.path.join(ROOT, 'route', sl), exist_ok=True)
    if sl in THIN_NEW and 'name="robots"' not in s:
        s = s.replace('<title>', '<meta name="robots" content="noindex,follow">\n<title>', 1)
    wr('route/%s/index.html' % sl, s)
print('restored route pages:', len(new))

# 2+3+5 stations ------------------------------------------------------------------
thin = set()
name_slug = {}
for f in []:  # station pages are rebuilt by tools/build_station_pages.py (noindex rule lives there); not touched here
    code = os.path.basename(os.path.dirname(f))
    s = open(f, encoding='utf-8').read()
    nt = int(re.search(r'<p class="lead">(\d+) trains? stop', s).group(1))
    nm = html.unescape(re.search(r'<h1>Trains at (.*?) \([A-Z0-9]+\)</h1>', s).group(1))
    changed = False
    if nt <= 3 and 'name="robots"' not in s:
        s = s.replace('<title>', '<meta name="robots" content="noindex,follow">\n<title>', 1); changed = True
    if nt <= 3:
        thin.add(code)
    a = R.slug(nm)
    if nt > 3 and 'Popular routes from' not in s:
        cand = sorted(by_from.get(a, []), key=lambda x: (-count[x], x))[:10]
        if cand:
            links = ''.join('<a href="/route/%s/">%s to %s</a>' % (x, e(nm), e(NAMES[split_slug(x)[1]])) for x in cand)
            s = s.replace('<h2>Track your train live</h2>', '<h2>Popular routes from %s</h2><div class="links">%s</div>\n<h2>Track your train live</h2>' % (e(nm), links), 1)
            changed = True
    if changed:
        wr('station/%s/index.html' % code, s)
print('thin stations noindexed:', len(thin))

# 4+5 trains and routes -------------------------------------------------------------
WA = '<p style="margin-top:18px"><a %s href="https://wa.me/?text=%s" rel="noopener">Share on WhatsApp</a></p>\n'
def add_wa(s, text):
    if 'wa.me' in s: return s
    return s.replace('<h2>Easier in the app</h2>', (WA % (UA, urllib.parse.quote(text))) + '<h2>Easier in the app</h2>', 1)

nt_ = 0
for n, (nm, st) in T.items():
    p = 'train/%s/index.html' % n
    s = rd(p)
    src, dst = st[0]['name'], st[-1]['name']
    title = '%s Train Running Status: %s Live | ClearBerth' % (n, nm)
    desc = 'Live running status of train %s %s: where it is now, how late it is and the next station, %s to %s. Free on ClearBerth.' % (n, nm, src, dst)
    s = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % e(title, quote=False), s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + e(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + e(title), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + e(desc), s, count=1)
    s = add_wa(s, '%s %s live running status: https://clearberth.app/train/%s/' % (n, nm, n))
    wr(p, s); nt_ += 1
for sl in final:
    p = 'route/%s/index.html' % sl
    s = rd(p)
    a, b = split_slug(sl)
    s = add_wa(s, 'Trains from %s to %s: https://clearberth.app/route/%s/' % (NAMES[a], NAMES[b], sl))
    wr(p, s)
print('train pages updated:', nt_)

# 6 sitemap -----------------------------------------------------------------------
sm = rd('sitemap.xml')
out = []
for line in sm.split('\n'):
    m = re.search(r'<loc>https://clearberth.app/(station|train|route)/([^/]+)/</loc>', line)
    if m:
        kind, key = m.groups()
        if kind == 'station' and key in thin:
            continue
        line = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>%s</lastmod>' % TODAY, line)
    out.append(line)
idx = max(i for i, l in enumerate(out) if '/route/' in l)
have = set(re.findall(r'<loc>https://clearberth.app/route/([^/]+)/</loc>', sm))
add = ['  <url><loc>https://clearberth.app/route/%s/</loc><lastmod>%s</lastmod></url>' % (sl, TODAY) for sl, _ in new if sl not in THIN_NEW and sl not in have]
out[idx + 1:idx + 1] = add
wr('sitemap.xml', '\n'.join(out))
print('sitemap urls:', len(re.findall('<loc>', '\n'.join(out))))
