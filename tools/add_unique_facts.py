#!/usr/bin/env python3
"""Adds a block of page-specific, timetable-derived facts to every /train/, /hi/train/,
/route/ and /station/ page (23 Nov 2026, for the AdSense "low value content" rejection).

  python3 tools/add_unique_facts.py --catalog DIR_OR_FILE [--only train,hi,route,station] [--limit N] [--write]

Catalog = the collect-trains export (?export=1, 300 rows per page, files p0.json, p300.json ...;
a directory of those files or one merged JSON list). Only trains that already have a /train/<n>/
page are used, so every number matches the site. Everything is computed from the timetable:
distances, leg times, halts, counts, ranks. Nothing is estimated.

The block sits between <!--uf-start--> and <!--uf-end-->; running again replaces it.
Run it AFTER any rebuild (see CLAUDE.md) and before add_internal_links.py.
"""
import argparse, collections, datetime as dt, glob, html, json, os, re, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = 'style="text-decoration:underline"'
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
S, E = '<!--uf-start-->', '<!--uf-end-->'
esc = lambda x: html.escape(x, quote=False)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def dur(m, hi=False):
    m = int(round(m))
    return ('%d घंटे %02d मिनट' % (m // 60, m % 60)) if hi else '%dh %02dm' % (m // 60, m % 60)


def clock(m):
    m = int(m) % 1440
    return '%02d:%02d' % (m // 60, m % 60)


# ---------------------------------------------------------------- data
def load_catalog(path):
    rows = []
    files = [path] if os.path.isfile(path) else sorted(glob.glob(os.path.join(path, 'p*.json')))
    for f in files:
        j = json.load(open(f, encoding='utf-8'))
        rows += j['rows'] if isinstance(j, dict) else j
    return rows


def stamp(t, base_year=2026):
    m = re.match(r'(\d\d):(\d\d) (\d\d)-(\w{3})', t or '')
    if not m:
        return None
    return dt.datetime(base_year, MON[m.group(4)], int(m.group(3)), int(m.group(1)), int(m.group(2)))


class Tr:
    pass


def build_trains(rows, page_names):
    """page_names: train number -> (title, [(name, code)]) from the live /train/ pages."""
    T = {}
    for r in rows:
        n = r['number']
        if n not in page_names:
            continue
        title, pst = page_names[n]
        st = (r.get('timetable') or {}).get('stations') or []
        if len(st) < 2 or len(st) != len(pst):
            continue
        t = Tr()
        t.no, t.name, t.type = n, title, (r.get('train_type') or '').strip()
        t.codes = [s['station_code'] for s in st]
        t.names = [p[0] for p in pst]
        t.dist = [int(s['distance']) for s in st]
        arr = [stamp(s['arrival_time']) for s in st]
        dep = [stamp(s['departure_time']) for s in st]
        if dep[0] is None:
            continue
        t0 = dep[0]
        prev = 0
        A, D = [], []
        ok = True
        for i in range(len(st)):
            a = arr[i]; d = dep[i]
            am = None if a is None else int((a - t0).total_seconds() // 60)
            dm = None if d is None else int((d - t0).total_seconds() // 60)
            for v in (am, dm):
                if v is not None and v < -60:
                    ok = False
            A.append(am); D.append(dm)
        if not ok:
            continue
        for i in range(1, len(st) - 1):          # a stop with one missing time: use the other
            if A[i] is None and D[i] is not None: A[i] = D[i]
            if D[i] is None and A[i] is not None: D[i] = A[i]
        if any((A[i] is None and D[i] is None) for i in range(1, len(st) - 1)) or A[-1] is None:
            continue
        t.arr, t.dep = A, D
        t.start_min = t0.hour * 60 + t0.minute          # clock minute of the first departure
        t.day = [((t0.hour * 60 + t0.minute) + (a if a is not None else d)) // 1440 + 1 for a, d in zip(A, D)]
        # clock minutes of day for arrival and departure at each stop
        t.arr_clock = [None if a is None else (t.start_min + a) % 1440 for a in A]
        t.dep_clock = [None if d is None else (t.start_min + d) % 1440 for d in D]
        t.n = len(st)
        t.total = A[-1]
        t.km = t.dist[-1]
        if t.total is None or t.total <= 0 or t.km <= 0:
            continue
        T[n] = t
    return T


def load_page_names(root):
    out = {}
    for f in glob.glob(os.path.join(root, 'train', '*', 'index.html')):
        n = os.path.basename(os.path.dirname(f))
        s = open(f, encoding='utf-8').read()
        h = re.search(r'<h1>(\d+) (.*?): live running status</h1>', s)
        if not h:
            continue
        rows = re.findall(r'<tr><td>(.*?) <small>\((.*?)\)</small></td>', s)
        out[n] = (html.unescape(h.group(2)), [(html.unescape(re.sub(r'<[^>]+>', '', a)).strip(), c) for a, c in rows])
    return out


def leg_speed(km, mins):
    return round(km / (mins / 60.0)) if mins > 0 else 0


# ---------------------------------------------------------------- shared stats
class World:
    def __init__(self, T):
        self.T = T
        self.stop_count = collections.Counter()
        self.pair = collections.defaultdict(list)       # (slugA, slugB) -> [(train, i, j)]
        self.names = {}
        self.byend = collections.defaultdict(list)      # (first_code, last_code) -> trains
        for t in T.values():
            for c, nme in zip(t.codes, t.names):
                self.stop_count[c] += 1
                self.names[c] = nme
            self.byend[(t.codes[0], t.codes[-1])].append(t)
            sl = [slug(x) for x in t.names]
            for i in range(t.n - 1):
                if t.dep[i] is None:
                    continue
                for j in range(i + 1, t.n):
                    if t.arr[j] is None or sl[i] == sl[j]:
                        continue
                    self.pair[(sl[i], sl[j])].append((t, i, j))


# ---------------------------------------------------------------- train block
L = {
    'en': dict(
        h='%s stop by stop', stop='Stop', km='Km from start', leg='Leg', legtime='Leg time', spd='Avg speed',
        halt='Halt', trains='Trains stopping here', start='Start', end='End', min='min', kmh='km/h', kmu='km',
        note='Distances are rail kilometres from %s. Leg is the stretch from the previous stop. "Trains stopping here" counts the trains ClearBerth has timetables for.'),
    'hi': dict(
        h='%s: हर स्टॉप की जानकारी', stop='स्टॉप', km='शुरू से किमी', leg='हिस्सा', legtime='हिस्से का समय', spd='औसत रफ़्तार',
        halt='ठहराव', trains='यहाँ रुकने वाली ट्रेनें', start='शुरू', end='अंत', min='मिनट', kmh='किमी/घंटा', kmu='किमी',
        note='दूरी %s से रेल किलोमीटर में है। "हिस्सा" पिछले स्टॉप से इस स्टॉप तक का सफ़र है। "यहाँ रुकने वाली ट्रेनें" में वही ट्रेनें गिनी गई हैं जिनका टाइमटेबल ClearBerth के पास है।'),
}


def train_block(t, W, lang):
    hi = lang == 'hi'
    X = L[lang]
    n = t.n
    legs = []
    for i in range(1, n):
        dk = t.dist[i] - t.dist[i - 1]
        dm = t.arr[i] - t.dep[i - 1]
        legs.append((i, dk, dm))
    real = [l for l in legs if l[1] >= 20 and l[2] > 0]
    halts = [(i, t.dep[i] - t.arr[i]) for i in range(1, n - 1) if t.arr[i] is not None and t.dep[i] is not None]
    halt_total = sum(h for _, h in halts)
    P = []
    # 1 fastest / slowest leg
    if real:
        f = max(real, key=lambda l: l[1] / l[2])
        s = min(real, key=lambda l: l[1] / l[2])
        if hi:
            P.append('सबसे तेज़ हिस्सा %s से %s तक है: %d किमी, %s में, यानी लगभग %d किमी/घंटा। सबसे धीमा हिस्सा %s से %s तक है: %d किमी, %s में, लगभग %d किमी/घंटा।' % (
                t.names[f[0] - 1], t.names[f[0]], f[1], dur(f[2], 1), leg_speed(f[1], f[2]),
                t.names[s[0] - 1], t.names[s[0]], s[1], dur(s[2], 1), leg_speed(s[1], s[2])))
        else:
            P.append('The fastest stretch is %s to %s: %d km in %s, about %d km/h. The slowest is %s to %s: %d km in %s, about %d km/h.' % (
                t.names[f[0] - 1], t.names[f[0]], f[1], dur(f[2]), leg_speed(f[1], f[2]),
                t.names[s[0] - 1], t.names[s[0]], s[1], dur(s[2]), leg_speed(s[1], s[2])))
    # 2 time standing
    if halts:
        pct = 100.0 * halt_total / t.total
        if hi:
            P.append('बीच के %d स्टॉप पर ट्रेन कुल %s खड़ी रहती है, जो पूरे सफ़र का लगभग %d%% है। चलने का समय लगभग %s है।' % (
                len(halts), dur(halt_total, 1), round(pct), dur(t.total - halt_total, 1)))
        else:
            P.append('At its %d intermediate stops the train stands for %s in total, about %d%% of the journey. Time actually moving is about %s.' % (
                len(halts), dur(halt_total), round(pct), dur(t.total - halt_total)))
    # 3 night calls
    night = [(i, t.arr_clock[i] if t.arr_clock[i] is not None else t.dep_clock[i]) for i in range(n)]
    night = [(i, c) for i, c in night if c is not None and c < 300]
    if night:
        show = ', '.join('%s (%s)' % (t.names[i], clock(c)) for i, c in night[:5])
        more = (' and %d more' % (len(night) - 5)) if len(night) > 5 and not hi else ((' और %d' % (len(night) - 5)) if len(night) > 5 else '')
        if hi:
            P.append('रात 00:00 से 05:00 के बीच ट्रेन इन स्टेशनों पर होती है: %s%s।' % (show, more))
        else:
            P.append('Between midnight and 05:00 the train is at: %s%s.' % (show, more))
    else:
        P.append('इस ट्रेन का रात 00:00 से 05:00 के बीच किसी स्टेशन पर निर्धारित ठहराव नहीं है।' if hi
                 else 'No stop on this train is scheduled between midnight and 05:00.')
    # 4 days
    dd = max(t.day)
    if hi:
        P.append('यह ट्रेन %s पर %s बजे पहुँचती है, यात्रा के दिन %d पर, और रास्ते में %d बार आधी रात पार करती है।' % (
            t.names[-1], clock(t.arr_clock[-1]), dd, dd - 1))
    else:
        P.append('It reaches %s at %s on day %d of the run, crossing midnight %d time%s on the way.' % (
            t.names[-1], clock(t.arr_clock[-1]), dd, dd - 1, '' if dd == 2 else 's'))
    # 5 rank among trains with same endpoints
    sib = sorted(W.byend[(t.codes[0], t.codes[-1])], key=lambda x: (x.total, x.no))
    rev = W.byend.get((t.codes[-1], t.codes[0]), [])
    if len(sib) > 1:
        r = sib.index(t) + 1
        fastest = sib[0]
        if hi:
            if r == 1:
                P.append('हमारे टाइमटेबल में %s से %s के बीच %d ट्रेनें हैं (शुरू से अंत तक)। इनमें यह सबसे तेज़ है।' % (t.names[0], t.names[-1], len(sib)))
            else:
                P.append('हमारे टाइमटेबल में %s से %s के बीच %d ट्रेनें हैं। रफ़्तार में यह %d नंबर पर है; सबसे तेज़ %s (%s) है, जो %s कम समय लेती है।' % (
                    t.names[0], t.names[-1], len(sib), r, fastest.no, fastest.name, dur(t.total - fastest.total, 1)))
        else:
            if r == 1:
                P.append('ClearBerth has %d trains running end to end from %s to %s. This is the fastest of them.' % (len(sib), t.names[0], t.names[-1]))
            else:
                P.append('ClearBerth has %d trains running end to end from %s to %s. This is number %d by journey time; the fastest, %s %s, takes %s less.' % (
                    len(sib), t.names[0], t.names[-1], r, fastest.no, fastest.name, dur(t.total - fastest.total)))
    else:
        if hi:
            P.append('हमारे टाइमटेबल में %s से %s तक पूरा सफ़र करने वाली यह अकेली ट्रेन है।' % (t.names[0], t.names[-1]))
        else:
            P.append('This is the only train in our timetables that runs the full way from %s to %s.' % (t.names[0], t.names[-1]))
    if rev:
        nums = ', '.join('<a %s href="%s/train/%s/">%s</a>' % (UA, '/hi' if hi else '', x.no, x.no) for x in sorted(rev, key=lambda x: x.no)[:4])
        P.append(('वापसी की दिशा (%s से %s) में चलने वाली ट्रेनें: %s।' % (t.names[-1], t.names[0], nums)) if hi
                 else 'Trains running the other way, %s to %s: %s.' % (t.names[-1], t.names[0], nums))
    # 6 busiest / quietest stop
    cnt = [(W.stop_count[c], i) for i, c in enumerate(t.codes)]
    bc = max(cnt, key=lambda x: (x[0], -x[1]))
    qc = min(cnt, key=lambda x: (x[0], x[1]))
    if bc[1] != qc[1]:
        if hi:
            P.append('इस रूट का सबसे व्यस्त स्टॉप %s है, जहाँ हमारे टाइमटेबल की %d ट्रेनें रुकती हैं। सबसे शांत स्टॉप %s है (%d ट्रेनें)।' % (t.names[bc[1]], bc[0], t.names[qc[1]], qc[0]))
        else:
            P.append('The busiest stop on this route is %s, where %d trains in our timetables stop. The quietest is %s, with %d.' % (t.names[bc[1]], bc[0], t.names[qc[1]], qc[0]))
    # table
    rows = []
    for i in range(n):
        if i == 0:
            leg = legtime = spd = '-'
            halt = '-'
        else:
            dk = t.dist[i] - t.dist[i - 1]
            dm = t.arr[i] - t.dep[i - 1]
            leg = '%d %s' % (dk, X['kmu'])
            legtime = dur(dm, hi)
            spd = ('%d %s' % (leg_speed(dk, dm), X['kmh'])) if dk >= 20 and dm > 0 else '-'
            halt = ('%d %s' % (t.dep[i] - t.arr[i], X['min'])) if 0 < i < n - 1 and t.dep[i] is not None and t.arr[i] is not None else '-'
        rows.append('<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td></tr>' % (
            esc(t.names[i]), t.dist[i], leg, legtime, spd, halt, W.stop_count[t.codes[i]]))
    tab = ('<div class="tt"><table><thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>'
           % (X['stop'], X['km'], X['leg'], X['legtime'], X['spd'], X['halt'], X['trains'], ''.join(rows)))
    h = X['h'] % t.no
    return '%s<section class="uf" id="uf"><h2>%s</h2>%s%s<p><small>%s</small></p></section>%s' % (
        S, h, ''.join('<p>%s</p>' % p for p in P), tab, X['note'] % esc(t.names[0]), E)


# ---------------------------------------------------------------- route block
BUCK = [('at night (00:00 to 04:59)', 0, 300), ('in the morning (05:00 to 11:59)', 300, 720),
        ('in the afternoon (12:00 to 16:59)', 720, 1020), ('in the evening (17:00 to 23:59)', 1020, 1440)]


def route_block(A, B, items, W, rev_exists, rev_slug, rev_n):
    """items: [(train, i, j)] with train going from stop i to stop j."""
    rows = []
    for t, i, j in items:
        km = t.dist[j] - t.dist[i]
        mins = t.arr[j] - t.dep[i]
        stops = j - i - 1
        days = (t.start_min + t.dep[i]) // 1440
        arrd = (t.start_min + t.arr[j]) // 1440 - days
        rows.append(dict(t=t, km=km, mins=mins, stops=stops, arrd=arrd, dep=t.dep_clock[i], arr=t.arr_clock[j], i=i, j=j))
    n = len(rows)
    kms = [r['km'] for r in rows if r['km'] > 0]
    km = int(statistics.median(kms)) if kms else 0
    rows.sort(key=lambda r: (r['dep'], r['t'].no))
    fast = min(rows, key=lambda r: r['mins'])
    P = []
    ts = [r['mins'] for r in rows]
    if n > 1:
        P.append('Journey times between %s and %s range from %s to %s, with a median of %s. Trains make between %d and %d intermediate stops.' % (
            esc(A), esc(B), dur(min(ts)), dur(max(ts)), dur(statistics.median(ts)), min(r['stops'] for r in rows), max(r['stops'] for r in rows)))
    else:
        r = rows[0]
        P.append('%s %s is the only train in our timetables between %s and %s. It takes %s and makes %d intermediate stop%s.' % (
            r['t'].no, esc(r['t'].name), esc(A), esc(B), dur(r['mins']), r['stops'], '' if r['stops'] == 1 else 's'))
    ov = sum(1 for r in rows if r['arrd'] >= 1)
    if n > 1:
        P.append('%d of the %d trains reach %s on a later calendar day than they leave %s; the rest arrive the same day.' % (ov, n, esc(B), esc(A)) if 0 < ov < n
                 else ('All %d trains reach %s the next day or later.' % (n, esc(B)) if ov == n else 'All %d trains reach %s the same day they leave %s.' % (n, esc(B), esc(A))))
    arrs = sorted(rows, key=lambda r: (r['arr'], r['t'].no))
    P.append('The earliest arrival at %s is %s (%s %s) and the latest is %s (%s %s).' % (
        esc(B), clock(arrs[0]['arr']), arrs[0]['t'].no, esc(arrs[0]['t'].name), clock(arrs[-1]['arr']), arrs[-1]['t'].no, esc(arrs[-1]['t'].name)) if n > 1 else
        'It leaves %s at %s and reaches %s at %s.' % (esc(A), clock(rows[0]['dep']), esc(B), clock(rows[0]['arr'])))
    types = collections.Counter(r['t'].type for r in rows if r['t'].type)
    if len(types) > 0:
        P.append('Train types on this route: %s.' % ', '.join('%s (%d)' % (esc(k), v) for k, v in types.most_common()))
    # intermediate stations common to the trains
    mid = collections.Counter()
    for r in rows:
        t = r['t']
        for k in range(r['i'] + 1, r['j']):
            mid[(t.codes[k], t.names[k])] += 1
    if mid:
        top = mid.most_common(5)
        P.append('Stations these trains stop at between %s and %s, with how many of the %d trains call there: %s.' % (
            esc(A), esc(B), n, '; '.join('%s %d' % (esc(nm), c) for (_, nm), c in top)))
    else:
        P.append('None of these trains makes an intermediate stop between %s and %s.' % (esc(A), esc(B)))
    if rev_n:
        P.append('Going back, %d train%s run%s %s to %s%s.' % (
            rev_n, '' if rev_n == 1 else 's', 's' if rev_n == 1 else '', esc(B), esc(A),
            (': <a %s href="/route/%s/">%s to %s timetable</a>' % (UA, rev_slug, esc(B), esc(A))) if rev_exists else ''))
    body = []
    for r in rows:
        t = r['t']
        body.append('<tr><td><a %s href="/train/%s/">%s</a></td><td>%s</td><td>%d</td><td>%d km</td><td>%s km/h</td><td>%s%s</td></tr>' % (
            UA, t.no, t.no, esc(t.type or '-'), r['stops'], r['km'], leg_speed(r['km'], r['mins']) if r['km'] else '-',
            clock(r['arr']), (' (+%d day%s)' % (r['arrd'], '' if r['arrd'] == 1 else 's')) if r['arrd'] else ''))
    tab = ('<div class="tt"><table><thead><tr><th>Train</th><th>Type</th><th>Stops between</th><th>Distance</th><th>Average speed</th><th>Arrives at %s</th></tr></thead><tbody>%s</tbody></table></div>'
           % (esc(B), ''.join(body)))
    return '%s<section class="uf" id="uf"><h2>%s to %s: stops, speed and arrival</h2>%s%s</section>%s' % (
        S, esc(A), esc(B), ''.join('<p>%s</p>' % p for p in P), tab, E)


# ---------------------------------------------------------------- station block
def station_block(code, name, W):
    ev = []   # (train, index)
    for t in W.T.values():
        for i, c in enumerate(t.codes):
            if c == code:
                ev.append((t, i))
    if not ev:
        return None
    n = len(ev)
    P = []
    times = []
    for t, i in ev:
        times.append(t.arr_clock[i] if t.arr_clock[i] is not None else t.dep_clock[i])
        if t.arr_clock[i] is not None and t.dep_clock[i] is not None and t.dep_clock[i] != t.arr_clock[i]:
            pass
    times.sort()
    # windows
    wc = []
    for lbl, a, b in BUCK:
        k = sum(1 for x in times if a <= x < b)
        wc.append((lbl, k))
    P.append('By time of day, trains reach %s: %s.' % (esc(name), '; '.join('%d %s' % (k, l) for l, k in wc if k) or 'none'))
    # first / last, longest gap
    P.append('The first scheduled arrival of the day is at %s and the last at %s.' % (clock(times[0]), clock(times[-1])) if n > 1 else
             'The only scheduled arrival is at %s.' % clock(times[0]))
    if n > 1:
        gaps = [(times[k + 1] - times[k], times[k], times[k + 1]) for k in range(n - 1)]
        gaps.append((1440 - times[-1] + times[0], times[-1], times[0]))
        g = max(gaps)
        if g[0] >= 30:
            P.append('The longest stretch of the day with no train arriving is %s, from %s to %s.' % (dur(g[0]), clock(g[1]), clock(g[2])))
    # halts
    hs = [(t.dep[i] - t.arr[i], t) for t, i in ev if 0 < i < t.n - 1 and t.arr[i] is not None and t.dep[i] is not None]
    if hs:
        vals = [h for h, _ in hs]
        med = int(statistics.median(vals))
        P.append('A typical scheduled halt here is %d minute%s. %d of the %d through trains stop for 2 minutes or less, and %d stop for 10 minutes or more.' % (
            med, '' if med == 1 else 's', sum(1 for v in vals if v <= 2), len(vals), sum(1 for v in vals if v >= 10)))
    # next / previous stops
    nxt = collections.Counter(); prv = collections.Counter()
    for t, i in ev:
        if i + 1 < t.n: nxt[t.names[i + 1]] += 1
        if i > 0: prv[t.names[i - 1]] += 1
    if nxt:
        a, c = nxt.most_common(1)[0]
        P.append('The most common next stop after %s is %s (%d train%s).' % (esc(name), esc(a), c, '' if c == 1 else 's'))
    if prv:
        a, c = prv.most_common(1)[0]
        P.append('The most common stop before %s is %s (%d train%s).' % (esc(name), esc(a), c, '' if c == 1 else 's'))
    # farthest ride out / in
    far = None; farin = None
    for t, i in ev:
        if i < t.n - 1:
            d = t.dist[-1] - t.dist[i]
            if far is None or d > far[0]: far = (d, t)
        if i > 0:
            d = t.dist[i]
            if farin is None or d > farin[0]: farin = (d, t)
    if far and far[0] > 0:
        t = far[1]
        P.append('The longest ride on from %s without changing trains is %d km to %s, on %s %s.' % (esc(name), far[0], esc(t.names[-1]), t.no, esc(t.name)))
    if farin and farin[0] > 0:
        t = farin[1]
        P.append('The longest ride in is %d km from %s, on %s %s.' % (farin[0], esc(t.names[0]), t.no, esc(t.name)))
    # fastest non-stop leg leaving
    best = None
    for t, i in ev:
        if i < t.n - 1:
            dk = t.dist[i + 1] - t.dist[i]
            dm = t.arr[i + 1] - t.dep[i]
            if dk >= 30 and dm > 0:
                sp = dk / (dm / 60.0)
                if best is None or sp > best[0]: best = (sp, dk, t, i)
    if best:
        sp, dk, t, i = best
        P.append('The fastest scheduled run out of %s to the next stop is %s %s to %s: %d km at about %d km/h.' % (
            esc(name), t.no, esc(t.name), esc(t.names[i + 1]), dk, round(sp)))
    return '%s<section class="uf" id="uf"><h2>%s timetable patterns</h2>%s</section>%s' % (
        S, esc(name), ''.join('<p>%s</p>' % p for p in P), E)


# ---------------------------------------------------------------- insertion
def put(s, block, anchor_re):
    s = re.sub(re.escape(S) + r'.*?' + re.escape(E), '', s, flags=re.S)
    m = re.search(anchor_re, s, flags=re.S)
    if not m:
        return None
    return s[:m.end()] + block + s[m.end():]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--only', default='train,hi,route,station')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--out', default='', help='write changed pages here instead (sample)')
    a = ap.parse_args()
    only = set(a.only.split(','))
    pn = load_page_names(ROOT)
    T = build_trains(load_catalog(a.catalog), pn)
    W = World(T)
    print('trains usable:', len(T), 'of', len(pn), file=sys.stderr)
    stats = collections.Counter()

    def save(f, s):
        if a.write:
            open(f, 'w', encoding='utf-8').write(s)
        elif a.out:
            o = os.path.join(a.out, os.path.relpath(f, ROOT)); os.makedirs(os.path.dirname(o), exist_ok=True)
            open(o, 'w', encoding='utf-8').write(s)

    def lim(lst):
        return lst[:a.limit] if a.limit else lst

    if 'train' in only:
        for n in lim(sorted(T)):
            f = os.path.join(ROOT, 'train', n, 'index.html')
            s = open(f, encoding='utf-8').read()
            r = put(s, train_block(T[n], W, 'en'), r'<h2>%s at a glance</h2><p>.*?</p>' % n)
            if r is None: stats['train-noanchor'] += 1; continue
            save(f, r); stats['train'] += 1
    if 'hi' in only:
        for n in lim(sorted(T)):
            f = os.path.join(ROOT, 'hi', 'train', n, 'index.html')
            if not os.path.exists(f): stats['hi-missing'] += 1; continue
            s = open(f, encoding='utf-8').read()
            r = put(s, train_block(T[n], W, 'hi'), r'<h2>%s एक नज़र में</h2><p>.*?</p>' % n)
            if r is None: stats['hi-noanchor'] += 1; continue
            save(f, r); stats['hi'] += 1
    if 'route' in only:
        for f in lim(sorted(glob.glob(os.path.join(ROOT, 'route', '*', 'index.html')))):
            sl = os.path.basename(os.path.dirname(f))
            s = open(f, encoding='utf-8').read()
            h = re.search(r'<h1>Trains from (.*?) to (.*?)</h1>', s)
            if not h: stats['route-noh1'] += 1; continue
            A, B = html.unescape(h.group(1)), html.unescape(h.group(2))
            key = None
            parts = sl.split('-')
            for i in range(1, len(parts)):
                if parts[i] == 'to' and (('-'.join(parts[:i]), '-'.join(parts[i + 1:])) in W.pair):
                    key = ('-'.join(parts[:i]), '-'.join(parts[i + 1:]))
            if not key: stats['route-nodata'] += 1; continue
            items = W.pair[key]
            rs = '%s-to-%s' % (key[1], key[0])
            blk = route_block(A, B, items, W, os.path.exists(os.path.join(ROOT, 'route', rs, 'index.html')), rs, len(W.pair.get((key[1], key[0]), [])))
            r = put(s, blk, r'<h2>[^<]* at a glance</h2><p>.*?</p>')
            if r is None: stats['route-noanchor'] += 1; continue
            r = re.sub(r'<h2>[^<]* at a glance</h2>', lambda m: '<h2>%s to %s at a glance</h2>' % (esc(A), esc(B)), r, count=1)
            save(f, r); stats['route'] += 1
    if 'station' in only:
        for f in lim(sorted(glob.glob(os.path.join(ROOT, 'station', '*', 'index.html')))):
            code = os.path.basename(os.path.dirname(f)).upper()
            s = open(f, encoding='utf-8').read()
            h = re.search(r'<h1>Trains at (.*?) \(', s)
            if not h: stats['station-noh1'] += 1; continue
            name = html.unescape(h.group(1))
            blk = station_block(code, name, W)
            if not blk: stats['station-nodata'] += 1; continue
            r = put(s, blk, r'<h2>[^<]* at a glance</h2><p>.*?</p>')
            if r is None: stats['station-noanchor'] += 1; continue
            save(f, r); stats['station'] += 1
    print(dict(stats))


if __name__ == '__main__':
    main()
