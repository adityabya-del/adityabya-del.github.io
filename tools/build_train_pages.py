#!/usr/bin/env python3
"""Builds /train/<n>/ pages (English) from the collector's timetable export.

  python3 tools/build_train_pages.py --catalog catalog.json --out DIR [--only 12301,12302]

The catalog is the JSON list of rows {number,name,train_type,timetable} from the
collect-trains edge function (?export=1, paged 300 at a time). The existing /route/
pages decide which route links a train page may show. The layout was reverse-engineered
from the live pages; tools/check_train_pages.py regenerates live pages and diffs them.
"""
import argparse, glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
UA = 'style="text-decoration:underline"'
KEEP_UPPER = {'AC', 'KSR', 'MGR'}
NOTCH = 120  # unused


def tc(s):
    out = []
    for w in re.split(r'(\s+|-)', s.strip()):
        if not w or w.isspace() or w == '-':
            out.append(w)
        elif w.upper() in KEEP_UPPER:
            out.append(w.upper())
        else:
            m = re.match(r'^(\W*)(.*)$', w)
            out.append(m.group(1) + m.group(2)[:1].upper() + m.group(2)[1:].lower())
    return ''.join(out)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def parse(t):
    m = re.match(r'(\d\d):(\d\d) (\d\d)-(\w{3})', t or '')
    return None if not m else (int(m.group(1)) * 60 + int(m.group(2)), int(m.group(3)), MON[m.group(4)])


def hm(x):
    return '%02d:%02d' % (x // 60, x % 60)


def dur(m):
    return '%dh %02dm' % (m // 60, m % 60)


class Train:
    def __init__(self, row):
        self.no = row['number']
        self.name = tc(row['name'])
        st = row['timetable']['stations']
        self.n = n = len(st)
        self.codes = [s['station_code'] for s in st]
        self.names = [tc(s['station_name']) for s in st]
        self.dist = [int(s['distance']) for s in st]
        arr = [parse(s['arrival_time']) if i else None for i, s in enumerate(st)]
        dep = [parse(s['departure_time']) if i < n - 1 else None for i, s in enumerate(st)]
        o0 = dep[0][2] * 31 + dep[0][1]
        absm = lambda p: None if p is None else (p[2] * 31 + p[1] - o0) * 1440 + p[0]
        self.arr_abs = [absm(p) for p in arr]
        self.dep_abs = [absm(p) for p in dep]
        self.arr_hm = [None if p is None else hm(p[0]) for p in arr]
        self.dep_hm = [None if p is None else hm(p[0]) for p in dep]
        self.day = [(self.arr_abs[i] if self.arr_abs[i] is not None else self.dep_abs[i]) // 1440 + 1 for i in range(n)]
        self.total = self.arr_abs[-1] - self.dep_abs[0]
        self.km = self.dist[-1]
        self.src, self.dst = self.names[0], self.names[-1]

    def glance(self):
        n = self.n
        speed = round(self.km / (self.total / 60)) if self.total else 0
        s = '%s covers %d km from %s to %s in %s, an average speed of about %d km/h including stops. ' % (
            self.name, self.km, self.src, self.dst, dur(self.total), speed)
        d = self.day[-1]
        when = 'on day %d of the journey' % d if d > 1 else 'the same day'
        s += 'It leaves %s at %s and reaches %s at %s %s, with %d stops in between. ' % (
            self.src, self.dep_hm[0], self.dst, self.arr_hm[-1], when, n - 2)
        best, bi = -1, 0
        for i in range(n - 1):
            g = self.dist[i + 1] - self.dist[i]
            if g > best:
                best, bi = g, i
        s += 'The longest stretch without a halt is %s to %s, %d km. ' % (self.names[bi], self.names[bi + 1], best)
        hb, hi = -1, 0
        for i in range(1, n - 1):
            h = self.dep_abs[i] - self.arr_abs[i]
            if h > hb:
                hb, hi = h, i
        if n > 2 and hb >= 5:
            s += 'The longest scheduled halt is at %s, about %d minutes. ' % (self.names[hi], hb)
        s += ('These are timetable figures. Real running times change with delays, so check '
              '<a %s href="/?train=%s#check">train %s live in ClearBerth</a> before you leave.') % (UA, self.no, self.no)
        return s


def load_routes(site):
    routes = {}
    for p in glob.glob(os.path.join(site, 'route', '*', 'index.html')):
        s = open(p, encoding='utf-8').read()
        m = re.search(r'content="(\d+) trains? from', s)
        routes[os.path.basename(os.path.dirname(p))] = int(m.group(1)) if m else 0
    return routes


def route_links(tr, routes):
    cand = []
    for i in range(tr.n):
        for j in range(i + 1, tr.n):
            sl = slug(tr.names[i]) + '-to-' + slug(tr.names[j])
            if sl in routes:
                cand.append((routes[sl], i, j, sl))
    cand.sort(key=lambda c: (-c[0], -(tr.dist[c[2]] - tr.dist[c[1]]), c[1], c[2]))
    return cand[:12]


POPULAR = ['12301', '12302', '12951', '12952', '12423', '12424', '12627', '12841', '12723', '12615', '12259', '22691', '12433', '12621']


def add_order(site):
    """Order in which train pages were first added (git history); unknown trains sort last, by number."""
    import subprocess
    try:
        out = subprocess.check_output(['git', '-C', site, 'log', '--diff-filter=A', '--name-only', '--format=@@%H', '--reverse', '--', 'train/*/index.html'], text=True)
    except Exception:
        return {}
    order, k = {}, 0
    for line in out.split('\n'):
        m = re.match(r'train/(\d+)/index.html', line)
        if m and m.group(1) not in order:
            order[m.group(1)] = k
            k += 1
    return order


def other_trains(tr, endpoints, names, order, limit=14):
    """Trains running the opposite way between the same two end stations, then popular trains."""
    rel = [m for m, (a, b) in endpoints.items() if m != tr.no and a == tr.codes[-1] and b == tr.codes[0]]
    rel.sort(key=lambda m: (order.get(m, 10 ** 9), m))
    rel = rel[:6]
    fill = [m for m in POPULAR if m != tr.no and m not in rel][:limit - len(rel)]
    links = ''.join('<a href="/train/%s/">%s %s</a>' % (m, m, html.escape(names[m])) for m in rel + fill)
    return '<h2>Other trains</h2><div class="links">%s<a href="/train/">All trains</a></div>\n' % links


def template_parts(site):
    s = open(os.path.join(site, 'train/12301/index.html'), encoding='utf-8').read()
    h = s[:s.index('</head>')]
    font = re.search(r'<style>@font-face.*?</style>\n', h, re.S).group(0)
    main = h[h.index('</script>\n', h.index('application/ld+json')) + len('</script>\n'):]
    css = (font, main)
    return css, None


def page(tr, routes, css, other, site):
    # `other` is rendered by the caller
    n = tr.no
    title = '%s %s Live Running Status | ClearBerth' % (n, tr.name)
    desc = ('Where is train %s %s right now? Live running status, delay and next station for %s to %s. Free on ClearBerth.'
            % (n, tr.name, tr.src, tr.dst))
    e = html.escape
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ClearBerth", "item": "https://clearberth.app/"},
        {"@type": "ListItem", "position": 2, "name": '%s %s' % (n, tr.name), "item": "https://clearberth.app/train/%s/" % n}]}
    head = ('<!DOCTYPE html>\n<html lang="en"><head>\n<!-- Google tag (gtag.js) -->\n'
            '<script async src="https://www.googletagmanager.com/gtag/js?id=G-J9D9G65GNJ"></script>\n<script>\n'
            '  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n'
            "  gtag('js', new Date());\n  gtag('config', 'G-J9D9G65GNJ');\n</script>\n"
            '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="apple-itunes-app" content="app-id=6802574946">\n'
            '<title>%s</title>\n<meta name="description" content="%s">\n<link rel="canonical" href="https://clearberth.app/train/%s/">\n'
            '<link rel="alternate" hreflang="en" href="https://clearberth.app/train/%s/"><link rel="alternate" hreflang="hi" href="https://clearberth.app/hi/train/%s/"><link rel="alternate" hreflang="x-default" href="https://clearberth.app/train/%s/">\n'
            '<meta property="og:type" content="website"><meta property="og:site_name" content="ClearBerth">\n'
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s">\n'
            '<meta property="og:url" content="https://clearberth.app/train/%s/"><meta property="og:image" content="https://clearberth.app/shots/og.png">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            '<link rel="icon" type="image/png" href="/shots/favicon.png"><link rel="apple-touch-icon" href="/shots/apple-touch-icon.png">\n'
            '<link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
            '%s<script type="application/ld+json">%s</script>\n%s</head>\n') % (
        e(title, quote=False), e(desc), n, n, n, n, e(title), e(desc), n, css[0], json.dumps(ld), css[1])
    rows = ''
    for i in range(tr.n):
        a = 'Start' if i == 0 else tr.arr_hm[i]
        d = 'End' if i == tr.n - 1 else tr.dep_hm[i]
        rows += '<tr><td>%s <small>(%s)</small></td><td>%s</td><td>%s</td><td>%d</td></tr>' % (e(tr.names[i]), tr.codes[i], a, d, tr.day[i])
    rl = ''.join('<a href="/route/%s/">%s to %s</a>' % (sl, e(tr.names[i]), e(tr.names[j])) for _, i, j, sl in route_links(tr, routes))
    routes_h = '<h2>Routes this train runs</h2><div class="links">%s</div>\n' % rl if rl else ''
    body = ('<body><div class="wrap">\n'
            '<div class="top"><a class="logo" href="/"><img src="/shots/icon.png" alt="" width="30" height="30">ClearBerth</a><a class="btn sm" href="/#get-app">Get the app</a></div>\n'
            '<p class="crumb"><a href="/">ClearBerth</a> / Trains / %s &nbsp;·&nbsp; <a href="/hi/train/%s/">हिंदी में देखें</a></p>\n'
            '<h1>%s %s: live running status</h1>\n'
            '<p class="lead">%s (%s) runs from %s to %s. Check where it is right now, how late it is and which station comes next.</p>\n'
            '<a class="btn" href="/?train=%s#check">Track train %s live</a>\n'
            '<div class="facts"><div><small>Train number</small><b>%s</b></div><div><small>From</small><b>%s</b></div><div><small>To</small><b>%s</b></div>'
            '<div><small>Stops</small><b>%d</b></div><div><small>Distance</small><b>%d km</b></div><div><small>Journey time</small><b>%s</b></div></div>\n'
            '<h2>%s at a glance</h2><p>%s</p>\n'
            '<h2>How to check %s live status</h2>\n'
            '<ol><li>Tap <b>Track train %s live</b>. The number is already filled in.</li><li>Choose the day the train left its first station, %s. This is the start date printed on your ticket.</li><li>Tap <b>Track train</b>. You see a route map, how late the train is, the station it just left and the next stop.</li></ol>\n'
            '<h2>%s stations and timetable</h2><p>Scheduled stops of %s. Live times can differ, so use live status on the day.</p>'
            '<div class="tt"><table><thead><tr><th>Station</th><th>Arrives</th><th>Departs</th><th>Day</th></tr></thead><tbody>%s</tbody></table></div>\n'
            % (n, n, n, e(tr.name), e(tr.name), n, e(tr.src), e(tr.dst), n, n, n, e(tr.src), e(tr.dst), tr.n, tr.km, dur(tr.total),
               n, tr.glance().replace(e(tr.name), e(tr.name)), n, n, e(tr.src), n, e(tr.name), rows))
    return head, body, routes_h, other


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only')
    a = ap.parse_args()
    site = ROOT
    routes = load_routes(site)
    css, other = template_parts(site)
    rows = json.load(open(a.catalog))
    only = set(a.only.split(',')) if a.only else None
    order = add_order(site)
    publish = set(os.listdir(os.path.join(site, 'train'))) - {'index.html'}
    if os.environ.get('INCLUDE_ALL') == '1':
        publish |= {r['number'] for r in rows}
    if os.environ.get('NEWLIST'):
        publish |= set(json.load(open(os.environ['NEWLIST'])))
    endpoints, names = {}, {}
    for r in rows:
        if r['number'] in publish or (only and r['number'] in only):
            try:
                t = Train(r)
                endpoints[t.no] = (t.codes[0], t.codes[-1]); names[t.no] = t.name
            except (TypeError, ValueError, IndexError, KeyError):
                pass
    for r in rows:
        if only and r['number'] not in only:
            continue
        try:
            tr = Train(r)
            head, body, routes_h, oth = page(tr, routes, css, other, site)
            oth = other_trains(tr, endpoints, names, order)
        except (TypeError, ValueError, IndexError, KeyError):
            print('skipped (incomplete timetable):', r['number'])
            continue
        # store block (identical on every page), footer
        stores = open(os.path.join(site, 'train/12301/index.html'), encoding='utf-8').read()
        stores = stores[stores.index('<h2>Easier in the app</h2>'):stores.index('<h2>Routes this train runs</h2>')]
        foot = ('<p style="margin-top:22px"><a %s href="/pnr-status/">Check PNR status</a> &nbsp;·&nbsp; <a %s href="/train-kahan-hai/">Train kahan hai?</a> &nbsp;·&nbsp; <a %s href="/#check">Check seats</a></p>\n</div>\n'
                '<footer><div class="wrap">&copy; 2026 ClearBerth. An independent app for Indian Railways travellers. <a href="https://clearberth.app/clearberth/privacy.htm">Privacy policy</a> &nbsp;·&nbsp; <a href="/about/">About</a> &nbsp;·&nbsp; <a href="/guides/">Guides</a></div></footer>\n</body></html>') % (UA, UA, UA)
        d = os.path.join(a.out, 'train', tr.no)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(head + body + stores + routes_h + oth + foot)


if __name__ == '__main__':
    main()
