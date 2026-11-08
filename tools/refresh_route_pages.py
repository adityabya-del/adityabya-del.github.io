#!/usr/bin/env python3
"""Rebuilds the train table / lead / at-a-glance of every /route/ page from the CURRENT
/train/ pages (route pages were built when the site had 766 trains; it now has 2,000+).
Also restores route pages that Google reported as 404.

  python3 tools/refresh_route_pages.py --test      # only report how many existing pages are reproduced exactly
  python3 tools/refresh_route_pages.py --write     # rewrite pages
"""
import glob, html, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = 'style="text-decoration:underline"'
e = html.escape


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def mins(t):
    return int(t[:2]) * 60 + int(t[3:5])


def dur(m):
    return '%dh %02dm' % (m // 60, m % 60)


def load_trains():
    T = {}
    for f in glob.glob(os.path.join(ROOT, 'train', '*', 'index.html')):
        n = os.path.basename(os.path.dirname(f))
        s = open(f, encoding='utf-8').read()
        h = re.search(r'<h1>(\d+) (.*?): live running status</h1>', s)
        if not h:
            continue
        rows = re.findall(r'<tr><td>(.*?) <small>\((.*?)\)</small></td><td>(.*?)</td><td>(.*?)</td><td>(\d+)</td></tr>', s)
        st = []
        for a, c, ar, dp, d in rows:
            st.append(dict(name=html.unescape(a), code=c, arr=None if ar == 'Start' else ar,
                           dep=None if dp == 'End' else dp, day=int(d)))
        T[n] = (html.unescape(h.group(2)), st)
    return T


def pair_trains(T):
    """(slugA, slugB) -> list of (number, trainname, dep_hm, arr_hm, minutes)"""
    P = collections.defaultdict(list)
    names = {}
    for n, (nm, st) in T.items():
        sl = [slug(x['name']) for x in st]
        for x, s in zip(st, sl):
            names[s] = x['name']
        for i in range(len(st) - 1):
            a = st[i]
            if a['dep'] is None:
                continue
            dep = a['day'] * 1440 + mins(a['dep'])
            if a['arr'] is not None and mins(a['dep']) < mins(a['arr']):
                dep += 1440
            for j in range(i + 1, len(st)):
                b = st[j]
                if b['arr'] is None or sl[i] == sl[j]:
                    continue
                arr = b['day'] * 1440 + mins(b['arr'])
                P[(sl[i], sl[j])].append((n, nm, a['dep'], b['arr'], arr - dep))
    return P, names


def bucket(hm):
    m = mins(hm)
    if m < 5 * 60: return 'at night'
    if m < 12 * 60: return 'in the morning'
    if m < 17 * 60: return 'in the afternoon'
    return 'in the evening'


def build(A, B, trains, km):
    trains = sorted(trains, key=lambda t: (mins(t[2]), t[0]))
    n = len(trains)
    rows = ''.join('<tr><td><a %s href="/train/%s/">%s</a> %s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                   % (UA, t[0], t[0], e(t[1]), t[2], t[3], dur(t[4])) for t in trains)
    lead = ('<p class="lead">%d trains run from %s to %s. Departure is from %s, arrival at %s, and Time is the scheduled journey time. '
            'Tap a train for its live running status and full timetable. This list covers the trains ClearBerth has timetables for, '
            'so it may not include every train on this route.</p>') % (n, e(A), e(B), e(A), e(B))
    fast = min(trains, key=lambda t: t[4])
    slow = max(trains, key=lambda t: t[4])
    g = 'The rail distance from %s to %s is about %d km. ' % (e(A), e(B), km) if km else ''
    if km:
        g += 'The fastest listed train is %s %s, scheduled at %s (about %d km/h), while the slowest, %s %s, takes %s. ' % (
            fast[0], e(fast[1]), dur(fast[4]), round(km / (fast[4] / 60)), slow[0], e(slow[1]), dur(slow[4]))
    else:
        g += 'The fastest listed train is %s %s, scheduled at %s, while the slowest, %s %s, takes %s. ' % (
            fast[0], e(fast[1]), dur(fast[4]), slow[0], e(slow[1]), dur(slow[4]))
    g += 'The first departure from %s is at %s and the last at %s. ' % (e(A), trains[0][2], trains[-1][2])
    c = collections.Counter(bucket(t[2]) for t in trains)
    g += 'By time of day: %s. ' % ', '.join('%d %s' % (v, k) for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
    g += 'Timetable figures only; check live status on the day because trains often run late.'
    return lead, rows, g


def refresh_page(s, A, B, trains, km):
    lead, rows, g = build(A, B, trains, km)
    n = len(trains)
    s = re.sub(r'<p class="lead">.*?</p>', lambda m: lead, s, count=1, flags=re.S)
    s = re.sub(r'<tbody>.*?</tbody>', lambda m: '<tbody>%s</tbody>' % rows, s, count=1, flags=re.S)
    s = re.sub(r'(<h2>[^<]* at a glance</h2><p>).*?(</p>)', lambda m: m.group(1) + g + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'content="\d+ trains? from', 'content="%d trains from' % n, s)
    return s


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--test'
    T = load_trains()
    P, names = pair_trains(T)
    same = diff = 0
    bad = []
    base = os.path.join(ROOT, '_gen', 'baseline_routes.txt')  # routes that existed before the 8 Nov restore
    only = set(open(base).read().split()) if os.path.exists(base) else None
    for f in sorted(glob.glob(os.path.join(ROOT, 'route', '*', 'index.html'))):
        sl = os.path.basename(os.path.dirname(f))
        if only is not None and sl not in only:
            continue
        s = open(f, encoding='utf-8').read()
        a, b = None, None
        for k in range(1, len(sl.split('-'))):
            parts = sl.split('-')
            for i in range(1, len(parts)):
                if parts[i] == 'to':
                    x, y = '-'.join(parts[:i]), '-'.join(parts[i + 1:])
                    if (x, y) in P:
                        a, b = x, y
        if not a:
            bad.append(sl); continue
        km = int(re.search(r'is about (\d+) km', s).group(1))
        old_n = int(re.search(r'content="(\d+) trains? from', s).group(1))
        new = refresh_page(s, names[a], names[b], P[(a, b)], km)
        if mode == '--test':
            if len(P[(a, b)]) == old_n:
                if new == s: same += 1
                else:
                    diff += 1
                    if diff <= 3:
                        import difflib
                        for x, y in zip(s.split('\n'), new.split('\n')):
                            if x != y:
                                sm = difflib.SequenceMatcher(None, x, y)
                                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                                    if tag != 'equal':
                                        print(sl, tag, repr(x[max(0, i1 - 60):i2 + 60]), '=>', repr(y[max(0, j1 - 60):j2 + 60])); break
                                break
        else:
            if new != s:
                open(f, 'w', encoding='utf-8').write(new)
    if mode == '--test':
        print('same-count pages reproduced exactly:', same, 'differ:', diff, 'unparsed:', len(bad), bad[:3])


if __name__ == '__main__':
    main()
