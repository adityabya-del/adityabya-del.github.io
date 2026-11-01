#!/usr/bin/env python3
"""Rebuilds the content of every /station/<code>/ page from the full timetable catalog.

  python3 tools/build_station_pages.py --catalog catalog.json [--only umb,ee] [--dry]

The catalog is the JSON list of rows {number,name,train_type,timetable} from the
collect-trains edge function (?export=1, paged 300 at a time), the same file
tools/build_train_pages.py uses. Only trains that already have a /train/<n>/ page are
listed, so every link works. The page head, the footer and everything from
"Track your train live" onwards are kept exactly as they are; only the part between the
breadcrumb and that heading is rebuilt. Safe to run again: the output depends only on
the catalog and on which /train/ pages exist.

Facts shown (all from the timetable): the trains that stop, each train's start and end
station, arrival and departure, counts of starting/ending/passing trains, the busiest
hour, the longest halt, the train types, and where trains leaving / arriving here go to /
come from. Nothing is estimated.
"""
import argparse, ast, collections, glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP_UPPER = {'AC', 'KSR', 'MGR', 'SF', 'SMVT', 'CST', 'CSMT', 'LTT', 'DLI', 'NDLS', 'MMCT', 'HWH', 'SBC', 'YPR', 'TPTY'}
UA = 'style="text-decoration:underline"'
THIN_WORDS = 250          # station pages with fewer words are kept out of Google (noindex) and the sitemap
NOINDEX = '<meta name="robots" content="noindex,follow">'
TODAY = '2026-11-01'     # sitemap lastmod for the station pages this run rewrote


def tc(s):
    out = []
    for w in re.split(r'(\s+|-)', (s or '').strip()):
        if not w or w.isspace() or w == '-':
            out.append(w)
        elif w.upper() in KEEP_UPPER:
            out.append(w.upper())
        else:
            m = re.match(r'^(\W*)(.*)$', w)
            out.append(m.group(1) + m.group(2)[:1].upper() + m.group(2)[1:].lower())
    return ''.join(out)


def esc(s):
    return html.escape(s, quote=False)


def timetable(row):
    t = row.get('timetable')
    if isinstance(t, str):
        try:
            t = json.loads(t)
        except Exception:
            t = ast.literal_eval(t)
    return t or {}


def hm(t):
    """'02:08 21-Oct' -> minutes after midnight, None for Source/Destination/blank."""
    m = re.match(r'(\d\d):(\d\d)', t or '')
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def clock(mins):
    return '%02d:%02d' % (mins // 60, mins % 60)


def visible_words(h):
    h = re.sub(r'<(script|style|noscript|svg)[\s\S]*?</\1>', '', h, flags=re.I)
    h = re.sub(r'<(nav|header|footer)[\s\S]*?</\1>', '', h, flags=re.I)
    return len(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).split())


def set_noindex(h, thin):
    h = h.replace(NOINDEX, '')
    return h.replace('</head>', NOINDEX + '</head>', 1) if thin else h


def plural(n, one, many=None):
    return '%d %s' % (n, one if n == 1 else (many or one + 's'))


def load(catalog_path):
    rows = json.load(open(catalog_path))
    published = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, 'train/*/index.html'))}
    stations = {}   # code -> list of stops
    names = {}      # code -> proper-case station name (from the catalog)
    for r in rows:
        if r['number'] not in published:
            continue
        t = timetable(r)
        st = t.get('stations') or []
        if len(st) < 2:
            continue
        src = tc(t.get('source_name') or st[0]['station_name'])
        dst = tc(t.get('destination_name') or st[-1]['station_name'])
        seen = set()
        for i, s in enumerate(st):
            code = s['station_code'].upper()
            names.setdefault(code, tc(s['station_name']))
            if code in seen:   # a few timetables list a station twice; the first listing is the one used
                continue
            seen.add(code)
            arr, dep = s.get('arrival_time'), s.get('departure_time')
            stations.setdefault(code, []).append({
                'number': r['number'], 'name': tc(r['name']), 'type': (r.get('train_type') or '').strip(),
                'src': src, 'dst': dst, 'src_code': st[0]['station_code'].upper(), 'dst_code': st[-1]['station_code'].upper(),
                'starts': i == 0 or arr == 'Source', 'ends': i == len(st) - 1 or dep == 'Destination',
                'arr': hm(arr), 'dep': hm(dep),
            })
    return stations, names


def sort_key(x):
    t = x['arr'] if x['arr'] is not None else x['dep']
    return (t if t is not None else 0, x['number'])


def station_links(codes_present):
    def link(code, label):
        if code.lower() in codes_present:
            return '<a %s href="/station/%s/">%s</a>' % (UA, code.lower(), esc(label))
        return esc(label)
    return link


def build_body(code, sname, trains, link):
    trains = sorted(trains, key=sort_key)
    n = len(trains)
    starts = sum(1 for x in trains if x['starts'])
    ends = sum(1 for x in trains if x['ends'])
    passing = n - starts - ends
    cap = sname
    parts = []
    parts.append('<p class="lead">%s stop%s at %s (%s). Tap a train for live running status and its full timetable. '
                 'This list covers the trains ClearBerth has timetables for, so it may not include every train at this station.</p>'
                 % (plural(n, 'train'), 's' if n == 1 else '', esc(sname), code))
    rows = []
    for x in trains:
        a = 'Start' if x['starts'] else (clock(x['arr']) if x['arr'] is not None else '')
        d = 'End' if x['ends'] else (clock(x['dep']) if x['dep'] is not None else '')
        sub = '<br><span style="font-size:13px;opacity:.75">%s to %s</span>' % (esc(x['src']), esc(x['dst'])) if x['src'] and x['dst'] else ''
        rows.append('<tr><td><a %s href="/train/%s/">%s</a> %s%s</td><td>%s</td><td>%s</td></tr>'
                    % (UA, x['number'], x['number'], esc(x['name']), sub, a, d))
    parts.append('<div class="tt"><table><thead><tr><th>Train</th><th>Arrives</th><th>Departs</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows))
    parts.append('<p style="margin-top:10px;font-size:14px">Times are the scheduled timetable. On the day, use live status: trains often run late.</p>')

    # ---- at a glance
    s1 = 'Of the %d trains listed here, %d pass through %s' % (n, passing, esc(cap)) if n != 1 else 'The one train listed here %s' % (
        'starts its journey at %s' % esc(cap) if starts else ('ends its journey at %s' % esc(cap) if ends else 'passes through %s' % esc(cap)))
    if n != 1:
        bits = []
        if starts:
            bits.append('%d start%s their journey here' % (starts, 's' if starts == 1 else ''))
        if ends:
            bits.append('%d end%s it here' % (ends, 's' if ends == 1 else ''))
        if bits:
            s1 += ', ' + ' and '.join(bits)
        s1 += '.'
    else:
        s1 += '.'
    hours = collections.Counter()
    times = []
    for x in trains:
        hs = set()
        for t in (x['arr'], x['dep']):
            if t is not None:
                hs.add(t // 60)
                times.append(t)
        for h in hs:
            hours[h] += 1
    glance = [s1]
    if hours:
        top = max(hours.values())
        h0 = min(h for h, c in hours.items() if c == top)
        if top >= 3:
            glance.append('The busiest hour in the timetable is %02d:00 to %02d:59, with %d trains arriving or leaving.' % (h0, h0, top))
        elif times:
            glance.append('Trains are spread across the day here, from %s to %s.' % (clock(min(times)), clock(max(times))))
    best = None
    for x in trains:
        if x['arr'] is not None and x['dep'] is not None and not x['starts'] and not x['ends']:
            m = (x['dep'] - x['arr']) % 1440
            if best is None or m > best[0]:
                best = (m, x)
    if best and best[0] >= 10:
        glance.append('The longest scheduled stop is %s %s, about %d minutes.' % (best[1]['number'], esc(best[1]['name']), best[0]))
    glance.append('Timetable figures only; trains often run late, so check live status for your train.')
    parts.append('<h2>%s at a glance</h2><p>%s</p>' % (esc(sname), ' '.join(glance)))

    # ---- where trains go / come from (only trains that leave / arrive here)
    leaving = collections.Counter()
    arriving = collections.Counter()
    dst_code, src_code = {}, {}
    for x in trains:
        if not x['ends'] and x['dst']:
            leaving[x['dst']] += 1
            dst_code[x['dst']] = x['dst_code']
        if not x['starts'] and x['src']:
            arriving[x['src']] += 1
            src_code[x['src']] = x['src_code']

    def listing(counter, codes, limit=8):
        items = []
        for name, c in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]:
            items.append('%s (%s)' % (link(codes[name], name), plural(c, 'train')))
        extra = len(counter) - limit
        return ', '.join(items) + ('; and %d more' % extra if extra > 0 else '') + '.'

    if leaving:
        parts.append('<h2>Where trains from %s end their journey</h2><p>%s</p>' % (esc(sname), listing(leaving, dst_code)))
    if arriving:
        parts.append('<h2>Where trains reaching %s begin their journey</h2><p>%s</p>' % (esc(sname), listing(arriving, src_code)))

    # ---- train types
    types = collections.Counter(x['type'] for x in trains if x['type'])
    if len(types) >= 1:
        t = ', '.join('%s (%d)' % (esc(k), v) for k, v in sorted(types.items(), key=lambda kv: (-kv[1], kv[0])))
        parts.append('<h2>Train types at %s</h2><p>By the trains listed above: %s.</p>' % (esc(sname), t))
    return '\n'.join(parts) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--only', default='')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    stations, names = load(a.catalog)
    present = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, 'station/*/index.html'))}
    link = station_links(present)
    only = {s.strip().lower() for s in a.only.split(',') if s.strip()}
    done = skipped = 0
    thin_pages, rewritten = [], []
    for d in sorted(present):
        if only and d not in only:
            continue
        code = d.upper()
        path = os.path.join(ROOT, 'station', d, 'index.html')
        old = open(path, encoding='utf-8').read()
        m_h1 = re.search(r'<h1>(.*?)</h1>', old)
        m_tail = old.find('<h2>Track your train live</h2>')
        if not m_h1 or m_tail < 0 or code not in stations:
            skipped += 1
            continue
        sname = re.sub(r'^Trains at ', '', html.unescape(m_h1.group(1)))
        sname = re.sub(r'\s*\(%s\)$' % re.escape(code), '', sname)
        trains = list(stations[code])
        have = {x['number'] for x in trains}
        # Keep the times the page already showed for a train it already listed: the
        # /train/ pages still carry those times, and the site must not contradict itself
        # (the catalog can be newer than the train pages; regenerate those separately).
        oldt = {m[0]: (m[1], m[2]) for m in re.findall(r'<tr><td><a [^>]*href="/train/(\d+)/">\d+</a>.*?</td><td>(.*?)</td><td>(.*?)</td></tr>', old, re.S)}
        for x in trains:
            if x['number'] in oldt:
                ar, dp = oldt[x['number']]
                x['arr'], x['dep'] = hm(ar), hm(dp)
                x['starts'], x['ends'] = ar == 'Start', dp == 'End'
        # Trains that have a /train/ page but are not in the catalog export: keep their
        # row from the existing page (number, name, times) so no timetable row is lost.
        for num, nm, ar, dp in re.findall(r'<tr><td><a [^>]*href="/train/(\d+)/">\d+</a> ([^<]*)(?:<br>.*?)?</td><td>(.*?)</td><td>(.*?)</td></tr>', old, re.S):
            if num in have:
                continue
            trains.append({'number': num, 'name': html.unescape(nm), 'type': '', 'src': None, 'dst': None, 'src_code': '', 'dst_code': '',
                           'starts': ar == 'Start', 'ends': dp == 'End',
                           'arr': hm(ar), 'dep': hm(dp)})
        body = build_body(code, sname, trains, link)
        new = old[:m_h1.end()] + '\n' + body + '\n' + old[m_tail:]
        thin = visible_words(new) < THIN_WORDS
        new = set_noindex(new, thin)
        if thin:
            thin_pages.append(d)
        if new != old and not a.dry:
            open(path, 'w', encoding='utf-8').write(new)
        rewritten.append(d)
        done += 1
    # sitemap: drop the thin (noindex) stations, date the others as rewritten today
    sm_path = os.path.join(ROOT, 'sitemap.xml')
    if not a.dry and not only and os.path.exists(sm_path):
        sm = open(sm_path, encoding='utf-8').read()
        thin_set, done_set = set(thin_pages), set(rewritten)

        def fix(m):
            slug = m.group(1)
            if slug in thin_set:
                return ''
            if slug in done_set:
                return m.group(0).replace(m.group(2), TODAY)
            return m.group(0)
        sm = re.sub(r'  <url><loc>https://clearberth\.app/station/([^/]+)/</loc><lastmod>([^<]*)</lastmod></url>\n', fix, sm)
        open(sm_path, 'w', encoding='utf-8').write(sm)
    print('rebuilt %d station pages, skipped %d, %d kept out of Google (under %d words): %s'
          % (done, skipped, len(thin_pages), THIN_WORDS, ', '.join(thin_pages)))


if __name__ == '__main__':
    main()
