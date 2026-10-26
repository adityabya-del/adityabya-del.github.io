#!/usr/bin/env python3
"""Builds /hi/train/<n>/ (Hindi) pages. Same data and rules as build_train_pages.py.

  [NEWLIST=file.json] python3 tools/build_hi_pages.py --catalog catalog.json --out DIR [--only a,b]
"""
import argparse, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_train_pages as B

e = html.escape


def hdur(m):
    return '%d घंटे %02d मिनट' % (m // 60, m % 60)


def glance(tr):
    n = tr.n
    speed = round(tr.km / (tr.total / 60)) if tr.total else 0
    s = '%s %s से %s तक %d किमी का सफ़र %s में तय करती है। स्टॉप समेत औसत रफ़्तार लगभग %d किमी/घंटा है। ' % (
        tr.name, tr.src, tr.dst, tr.km, hdur(tr.total), speed)
    d = tr.day[-1]
    when = 'यात्रा का दिन %d' % d if d > 1 else 'उसी दिन'
    s += 'यह %s से %s पर चलती है और %s %s पर पहुँचती है (%s)। बीच में %d स्टॉप हैं। ' % (
        tr.src, tr.dep_hm[0], tr.dst, tr.arr_hm[-1], when, n - 2)
    best, bi = -1, 0
    for i in range(n - 1):
        g = tr.dist[i + 1] - tr.dist[i]
        if g > best:
            best, bi = g, i
    s += 'सबसे लंबा बिना रुके हिस्सा %s से %s तक, %d किमी का है। ' % (tr.names[bi], tr.names[bi + 1], best)
    hb, hi = -1, 0
    for i in range(1, n - 1):
        h = tr.dep_abs[i] - tr.arr_abs[i]
        if h > hb:
            hb, hi = h, i
    if n > 2 and hb >= 5:
        s += 'सबसे लंबा निर्धारित ठहराव %s पर, लगभग %d मिनट का है। ' % (tr.names[hi], hb)
    s += ('ये टाइमटेबल के आँकड़े हैं। असली समय देरी से बदलता है, इसलिए निकलने से पहले '
          '<a %s href="/?train=%s#check">ट्रेन %s को ClearBerth में लाइव देखें</a>।') % (B.UA, tr.no, tr.no)
    return s


def build(tr, routes, css, site, endpoints, names, order, stores):
    n = tr.no
    head, _, _, _ = B.page(tr, routes, css, None, site)
    title = '%s %s लाइव स्टेटस, ट्रेन कहाँ है | ClearBerth' % (n, tr.name)
    desc = 'ट्रेन %s %s अभी कहाँ है? %s से %s तक लाइव रनिंग स्टेटस, देरी और अगला स्टेशन। ClearBerth पर मुफ़्त।' % (n, tr.name, tr.src, tr.dst)
    en_title = '%s %s Live Running Status | ClearBerth' % (n, tr.name)
    en_desc = ('Where is train %s %s right now? Live running status, delay and next station for %s to %s. Free on ClearBerth.' % (n, tr.name, tr.src, tr.dst))
    h = head.replace('<html lang="en">', '<html lang="hi">')
    h = h.replace(e(en_title, quote=False), e(title, quote=False)).replace(e(en_title), e(title))
    h = h.replace(e(en_desc), e(desc))
    h = h.replace('<link rel="canonical" href="https://clearberth.app/train/%s/">' % n, '<link rel="canonical" href="https://clearberth.app/hi/train/%s/">' % n)
    h = h.replace('<meta property="og:url" content="https://clearberth.app/train/%s/">' % n, '<meta property="og:url" content="https://clearberth.app/hi/train/%s/">' % n)
    h = h.replace('"item": "https://clearberth.app/train/%s/"' % n, '"item": "https://clearberth.app/hi/train/%s/"' % n)
    rows = ''
    for i in range(tr.n):
        a = 'शुरू' if i == 0 else tr.arr_hm[i]
        d = 'अंत' if i == tr.n - 1 else tr.dep_hm[i]
        rows += '<tr><td>%s <small>(%s)</small></td><td>%s</td><td>%s</td><td>%d</td></tr>' % (e(tr.names[i]), tr.codes[i], a, d, tr.day[i])
    rl = ''.join('<a href="/route/%s/">%s से %s</a>' % (sl, e(tr.names[i]), e(tr.names[j])) for _, i, j, sl in B.route_links(tr, routes))
    routes_h = '<h2>इस ट्रेन के रूट</h2><div class="links">%s</div>\n' % rl if rl else '\n'
    nm = e(tr.name)
    body = ('<body><div class="wrap">\n'
            '<div class="top"><a class="logo" href="/"><img src="/shots/icon.png" alt="" width="30" height="30">ClearBerth</a><a class="btn sm" href="/#get-app">ऐप पाएँ</a></div>\n'
            '<p class="crumb"><a href="/">ClearBerth</a> / ट्रेनें / %s &nbsp;·&nbsp; <a href="/train/%s/">View in English</a></p>\n'
            '<h1>%s %s: लाइव रनिंग स्टेटस (ट्रेन कहाँ है)</h1>\n'
            '<p class="lead">%s (%s) %s से %s तक चलती है। देखें कि ट्रेन अभी कहाँ है, कितनी लेट है और अगला स्टेशन कौन सा है।</p>\n'
            '<a class="btn" href="/?train=%s#check">ट्रेन %s लाइव ट्रैक करें</a>\n'
            '<div class="facts"><div><small>ट्रेन नंबर</small><b>%s</b></div><div><small>कहाँ से</small><b>%s</b></div><div><small>कहाँ तक</small><b>%s</b></div>'
            '<div><small>स्टॉप</small><b>%d</b></div><div><small>दूरी</small><b>%d किमी</b></div><div><small>सफ़र का समय</small><b>%s</b></div></div>\n'
            '<h2>%s एक नज़र में</h2><p>%s</p>\n'
            '<h2>%s का लाइव स्टेटस कैसे देखें</h2>\n'
            '<ol><li><b>ट्रेन %s लाइव ट्रैक करें</b> दबाएँ। नंबर पहले से भरा होगा।</li><li>वह दिन चुनें जब ट्रेन अपने पहले स्टेशन %s से चली थी। यह आपके टिकट पर छपी शुरुआती तारीख है।</li><li><b>Track train</b> दबाएँ। आपको रूट मैप, ट्रेन की देरी, अभी छोड़ा हुआ स्टेशन और अगला स्टॉप दिखेगा।</li></ol>\n'
            '<h2>%s के स्टेशन और टाइमटेबल</h2><p>%s के निर्धारित स्टॉप। असली समय अलग हो सकता है, इसलिए यात्रा वाले दिन लाइव स्टेटस देखें।</p>'
            '<div class="tt"><table><thead><tr><th>स्टेशन</th><th>पहुँचता है</th><th>छूटता है</th><th>दिन</th></tr></thead><tbody>%s</tbody></table></div>\n'
            % (n, n, n, nm, nm, n, e(tr.src), e(tr.dst), n, n, n, e(tr.src), e(tr.dst), tr.n, tr.km, hdur(tr.total),
               n, glance(tr), n, n, e(tr.src), n, nm, rows))
    rel = []
    fill = [m for m in B.POPULAR + ['12009'] if m != n][:14]
    links = ''.join('<a href="/hi/train/%s/">%s %s</a>' % (m, m, e(names[m])) for m in rel + fill)
    oth = '<h2>दूसरी ट्रेनें</h2><div class="links">%s<a href="/train/">सभी ट्रेनें</a></div>\n' % links
    foot = ('<p style="margin-top:22px"><a %s href="/hi/pnr-status/">PNR स्टेटस चेक करें</a> &nbsp;·&nbsp; <a %s href="/train-kahan-hai/">ट्रेन कहाँ है?</a></p>\n</div>\n'
            '<footer><div class="wrap">&copy; 2026 ClearBerth. An independent app for Indian Railways travellers. <a href="https://clearberth.app/clearberth/privacy.htm">Privacy policy</a> &nbsp;·&nbsp; <a href="/about/">About</a> &nbsp;·&nbsp; <a href="/guides/">Guides</a></div></footer>\n</body></html>') % (B.UA, B.UA)
    return h + body + routes_h + stores + oth + foot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only')
    a = ap.parse_args()
    site = B.ROOT
    routes = B.load_routes(site)
    css, _ = B.template_parts(site)
    rows = json.load(open(a.catalog))
    only = set(a.only.split(',')) if a.only else None
    order = B.add_order(site)
    publish = set(os.listdir(os.path.join(site, 'hi/train'))) - {'index.html'}
    if os.environ.get('NEWLIST'):
        publish |= set(json.load(open(os.environ['NEWLIST'])))
    s = open(os.path.join(site, 'hi/train/12301/index.html'), encoding='utf-8').read()
    stores = s[s.index('<h2>ऐप में और आसान</h2>'):s.index('<h2>दूसरी ट्रेनें</h2>')]
    endpoints, names = {}, {}
    for r in rows:
        if r['number'] in publish:
            try:
                t = B.Train(r)
                endpoints[t.no] = (t.codes[0], t.codes[-1]); names[t.no] = t.name
            except (TypeError, ValueError, IndexError, KeyError):
                pass
    for r in rows:
        if only and r['number'] not in only:
            continue
        try:
            tr = B.Train(r)
            out = build(tr, routes, css, site, endpoints, names, order, stores)
        except (TypeError, ValueError, IndexError, KeyError):
            print('skipped (incomplete timetable):', r['number'])
            continue
        d = os.path.join(a.out, 'hi', 'train', tr.no)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


if __name__ == '__main__':
    main()
