#!/usr/bin/env python3
"""Create /station/<code>/ pages for stations in Manipur and Arunachal Pradesh that had no page.

On 13 Nov 2026 the site owner asked for these stations to be added so the Manipur and
Arunachal regional sections have pages to sit on:
  Manipur: JRBM Jiribam, VNGP Vangaichungpao, KGBP Khongsang, RGBP Ranigaidinliu, TGBP Thingou
  Arunachal Pradesh: NHLN Naharlagun, GMTO Gumto, BHNG Bhalukpong
The trains that stop at each station are read from the timetables already printed on the
/train/<number>/ pages (name, code, arrival, departure), so nothing is made up. A station
that no train page lists gets no page. The page text comes from build_station_pages.build_body.

  python3 tools/add_northeast_stations.py --write       (--test = dry run)
Then run, in this order:
  python3 tools/add_region_sections.py --write
  python3 tools/add_internal_links.py --write
"""
import glob, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_station_pages as bsp  # noqa: E402

WANT = ['RMR', 'SHKV', 'JRBM', 'VNGP', 'KGBP', 'RGBP', 'TGBP', 'NHLN', 'GMTO', 'BHNG']
TEMPLATE = 'aadr'   # an existing small station page used for the head / footer


def clean(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def read_trains():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'train/*/index.html'))):
        num = os.path.basename(os.path.dirname(p))
        h = open(p, encoding='utf-8').read()
        m = re.search(r'<h1>%s (.*?): live running status</h1>' % num, h)
        if not m:
            continue
        rows = re.findall(r'<tr><td>(.*?) <small>\(([A-Z0-9]+)\)</small></td><td>(.*?)</td><td>(.*?)</td><td>\d+</td></tr>', h)
        if len(rows) < 2:
            continue
        out.append((num, html.unescape(m.group(1)), [(clean(a), b, c, d) for a, b, c, d in rows]))
    return out


def main():
    write = '--write' in sys.argv
    trains = read_trains()
    stops = {c: [] for c in WANT}
    for num, name, rows in trains:
        src, dst = bsp.tc(rows[0][0]), bsp.tc(rows[-1][0])
        for i, (nm, code, arr, dep) in enumerate(rows):
            if code in stops:
                stops[code].append({
                    'number': num, 'name': bsp.tc(name), 'type': '', 'src': src, 'dst': dst,
                    'src_code': rows[0][1], 'dst_code': rows[-1][1],
                    'starts': arr == 'Start' or i == 0, 'ends': dep == 'End' or i == len(rows) - 1,
                    'arr': bsp.hm(arr), 'dep': bsp.hm(dep), '_nm': bsp.tc(nm)})
    tpl = open(os.path.join(ROOT, 'station', TEMPLATE, 'index.html'), encoding='utf-8').read()
    tpl_name = re.sub(r'^Trains at ', '', html.unescape(re.search(r'<h1>(.*?)</h1>', tpl).group(1)))
    tpl_name = re.sub(r'\s*\(%s\)$' % TEMPLATE.upper(), '', tpl_name)
    present = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, 'station/*/index.html'))}
    present |= {c.lower() for c in WANT if stops[c]}
    link = bsp.station_links(present)
    made, thin = [], []
    for code in WANT:
        t = stops[code]
        if not t:
            print('no train page lists', code, '- no page made')
            continue
        sname = t[0]['_nm']
        page = tpl.replace(tpl_name, sname).replace(TEMPLATE.upper(), code).replace('/station/%s/' % TEMPLATE, '/station/%s/' % code.lower())
        page = re.sub(r'<!--rg-start-->.*?<!--rg-end-->', '', page, flags=re.S)
        n = len(t)
        page = re.sub(r'content="\d+ trains? stops? at', 'content="%d train%s stop%s at' % (n, '' if n == 1 else 's', 's' if n == 1 else ''), page)
        page = re.sub(r'content="\d+ trains? stop at', 'content="%d train%s stop%s at' % (n, '' if n == 1 else 's', 's' if n == 1 else ''), page)
        h1 = re.search(r'<h1>.*?</h1>', page)
        tail = page.find('<h2>Track your train live</h2>')
        body = bsp.build_body(code, sname, t, link)
        page = page[:h1.end()] + '\n' + body + '\n' + page[tail:]
        is_thin = bsp.visible_words(page) < bsp.THIN_WORDS
        page = bsp.set_noindex(page, is_thin)
        d = os.path.join(ROOT, 'station', code.lower())
        print(code, sname, n, 'trains', 'thin(noindex)' if is_thin else '')
        if write:
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page)
        made.append(code.lower())
        if is_thin:
            thin.append(code.lower())
    sm = os.path.join(ROOT, 'sitemap.xml')
    if write and os.path.exists(sm):
        s = open(sm, encoding='utf-8').read()
        add = ''.join('  <url><loc>https://clearberth.app/station/%s/</loc><lastmod>2026-11-13</lastmod></url>\n' % c
                      for c in made if c not in thin and '/station/%s/<' % c not in s)
        if add:
            s = s.replace('</urlset>', add + '</urlset>')
            open(sm, 'w', encoding='utf-8').write(s)
    print('made', len(made), 'pages;', len(thin), 'kept out of Google (thin)')


if __name__ == '__main__':
    main()
