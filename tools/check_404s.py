#!/usr/bin/env python3
"""Weekly 404 check. Requests every URL in the LIVE sitemap.xml plus every internal link
found on the site's own pages, and reports anything that is not HTTP 200.

  python3 tools/check_404s.py            # checks https://clearberth.app
Exit code 0 = all fine, 1 = problems found (listed, with which pages link to each broken URL).
"""
import concurrent.futures as cf, glob, os, re, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://clearberth.app'


def status(url):
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'ClearBerth-link-check'})
    for attempt in range(2):
        try:
            return urllib.request.urlopen(req, timeout=15).status
        except urllib.error.HTTPError as ex:
            if ex.code in (403, 405, 429, 500, 502, 503) and attempt == 0:
                continue
            return ex.code
        except Exception:
            if attempt == 1:
                return 0
    return 0


def main():
    sm = urllib.request.urlopen(urllib.request.Request(BASE + '/sitemap.xml', headers={'User-Agent': 'ClearBerth-link-check'}), timeout=30).read().decode()
    urls = set(re.findall(r'<loc>([^<]+)</loc>', sm))
    linked = {}
    for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        rel = os.path.relpath(f, ROOT)
        if rel.startswith(('_gen', 'tools', 'node_modules')):
            continue
        for h in re.findall(r'href="(/[^"#?]*)"', open(f, encoding='utf-8', errors='ignore').read()):
            if re.search(r'\.(png|svg|jpg|webp|woff2|css|js|txt|xml|htm|ico|mp4)$', h):
                continue
            u = BASE + h
            urls.add(u)
            linked.setdefault(u, set()).add(rel)
    urls = sorted(urls)
    if '--part' in sys.argv:  # --part K/N: check every Nth URL starting at K (to fit short time limits)
        k, n = map(int, sys.argv[sys.argv.index('--part') + 1].split('/'))
        urls = urls[k::n]
    print('URLs to check:', len(urls), flush=True)
    res = []
    with cf.ThreadPoolExecutor(12) as ex:
        for i, c in enumerate(ex.map(status, urls), 1):
            res.append(c)
            if i % 500 == 0:
                print('progress', i, 'of', len(urls), 'not-ok so far', sum(1 for r in res if r != 200), flush=True)
    bad = [(u, c) for u, c in zip(urls, res) if c != 200]
    print('checked %d URLs, %d not OK' % (len(urls), len(bad)))
    for u, c in bad[:200]:
        print(c, u, '<- linked from', sorted(linked.get(u, []))[:3])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
