#!/usr/bin/env python3
"""City banners for the four metro cities (19 Nov 2026): Delhi, Mumbai, Kolkata, Chennai.

STATION pages of the city's stations get, under the breadcrumb:
  a coloured city banner (city name, counts from our timetables), cards
  linking every station of that city, then the "Got a photo?" note.
  The state photo section (rg block) is removed on these pages.
TRAIN pages whose first station is in one of these cities get the same
  banner after the "at a glance" paragraph, plus "States on this route" and
  "Tatkal for <no>" (from add_state_templates.py), in the city colour.

Run AFTER add_region_sections.py and add_state_templates.py:
  python3 tools/add_metro_sections.py [--write]
Safe to run twice (it replaces its own <!--mx-...--> blocks).
"""
import html as H, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import add_state_templates as ST  # noqa: E402

CITIES = {
    "Delhi": dict(codes=["ndls", "dli", "nzm", "anvt", "dee", "dsj", "dec", "dkz", "dsa", "andi"],
                  kicker="Capital of India", c1="#B71C1C", c2="#4A148C", state="Delhi"),
    "Mumbai": dict(codes=["csmt", "mmct", "ltt", "bdts", "dr", "bvi", "adh"],
                   kicker="Capital of Maharashtra", c1="#0D47A1", c2="#00695C", state="Maharashtra"),
    "Kolkata": dict(codes=["hwh", "sdah", "koaa", "src", "shm"],
                    kicker="Capital of West Bengal", c1="#D84315", c2="#4E342E", state="West Bengal"),
    "Chennai": dict(codes=["mas", "ms", "tbm", "per"],
                    kicker="Capital of Tamil Nadu", c1="#00838F", c2="#1A237E", state="Tamil Nadu"),
}
CITY_OF = {c: city for city, d in CITIES.items() for c in d["codes"]}
# Delhi is not one of the 23 states in _station_states.json; place its stations for the route chips
for _c in CITIES["Delhi"]["codes"]:
    ST.STATES.setdefault(_c, "Delhi")

CSS = ('<style id="mx-css">'
       '.mx{margin:16px 0 8px}'
       '.mx-hero{position:relative;overflow:hidden;border-radius:22px;padding:26px 22px 22px;color:#fff;'
       'background:linear-gradient(135deg,var(--mx1),var(--mx2))}'
       '.mx-hero svg{position:absolute;right:-20px;bottom:-10px;width:300px;height:auto;opacity:.18;pointer-events:none}'
       '.mx-kicker{font:600 12px var(--font-head,sans-serif);letter-spacing:.14em;text-transform:uppercase;opacity:.85}'
       '.mx-city{font:700 clamp(44px,11vw,72px)/1 var(--font-head,sans-serif);margin:6px 0 10px;letter-spacing:-.02em}'
       '.mx-sub{font-size:16px;line-height:1.5;max-width:520px;opacity:.95;margin:0}'
       '.mx-stats{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;position:relative}'
       '.mx-stats div{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);border-radius:14px;padding:10px 14px;min-width:92px}'
       '.mx-stats b{display:block;font:700 26px/1.1 var(--font-head,sans-serif)}'
       '.mx-stats span{font-size:13px;opacity:.9}'
       '.mx-foot{font-size:12px;opacity:.75;margin:12px 0 0;position:relative}'
       '.mx-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:12px}'
       '.mx-card{display:block;border:1.5px solid var(--line,#E3E6F0);border-radius:14px;padding:12px 14px;text-decoration:none;color:var(--ink,#141A33);background:#fff}'
       '.mx-card b{display:block;font-size:15px}.mx-card small{color:var(--mx1);font-weight:700;letter-spacing:.05em}'
       '.mx-card span{display:block;font-size:13px;color:#5A6180;margin-top:4px}'
       '.mx-card.here{border-color:var(--mx1);box-shadow:0 0 0 2px var(--mx1) inset}'
       '.mx-card:hover{border-color:var(--mx1)}'
       '</style>')

TRACKS = ('<svg viewBox="0 0 300 160" aria-hidden="true"><g fill="none" stroke="#fff" stroke-width="3">'
          '<path d="M0 150 C120 150 180 90 300 40"/><path d="M0 128 C110 128 170 70 300 18"/>'
          '<path d="M30 160 L48 120M70 158 L90 117M112 152 L134 110M152 140 L176 98M190 122 L214 82M226 100 L250 62M262 76 L284 42" stroke-width="2"/>'
          '</g></svg>')

GLANCE = re.compile(r'Of the (\d+) trains? listed here')
STARTS = re.compile(r'(\d+) starts? their journey here')


def station_info(code):
    p = ROOT / "station" / code / "index.html"
    if not p.exists():
        return None
    h = p.read_text()
    name = re.search(r'<h1>Trains at (.*?) \(([A-Z0-9]+)\)</h1>', h)
    g = GLANCE.search(h)
    if not name or not g:
        return None
    nm = H.unescape(name.group(1)).replace("Mumbai Csmt", "Mumbai CSMT").replace("Mumbai Ltt", "Mumbai LTT")
    s = STARTS.search(h)
    nm = nm.replace("Kolkatta", "Kolkata")
    return dict(code=code, name=nm, total=int(g.group(1)), start=int(s.group(1)) if s else 0)


def city_stats():
    """Trains starting in each city and the states on their routes, from the train pages."""
    out = {c: dict(trains=0, states=set()) for c in CITIES}
    for p in sorted((ROOT / "train").glob("*/index.html")):
        rows = ST.ROW.findall(p.read_text())
        if len(rows) < 2:
            continue
        city = CITY_OF.get(rows[0][1].lower())
        if not city:
            continue
        out[city]["trains"] += 1
        for r in rows:
            s = ST.STATES.get(r[1].lower())
            if s and s != CITIES[city]["state"]:
                out[city]["states"].add("Arunachal Pradesh" if s == "Arunanchal Pradesh" else s)
    return out


def hero(city, sub, infos, stats, here=None):
    d = CITIES[city]
    cards = ''.join(
        f'<a class="mx-card{" here" if i["code"] == here else ""}" href="/station/{i["code"]}/">'
        f'<b>{H.escape(i["name"])}</b><small>{i["code"].upper()}</small>'
        f'<span>{i["total"]} trains{", " + str(i["start"]) + " start here" if i["start"] else " stop here"}</span></a>' for i in infos)
    n_states = len(stats["states"])
    return (f'<!--mx-start--><section class="mx" style="--mx1:{d["c1"]};--mx2:{d["c2"]}" aria-label="{city}">'
            f'<div class="mx-hero">{TRACKS}<div class="mx-kicker">{d["kicker"]}</div>'
            f'<div class="mx-city">{city}</div><p class="mx-sub">{sub}</p>'
            f'<div class="mx-stats"><div><b>{len(infos)}</b><span>stations</span></div>'
            f'<div><b>{stats["trains"]}</b><span>trains start here</span></div>'
            f'<div><b>{n_states}</b><span>other states and UTs on their routes</span></div></div>'
            f'<p class="mx-foot">Counted from the timetables on ClearBerth.</p></div>'
            f'<div class="mx-grid">{cards}</div></section><!--mx-end-->')


def accent(city):
    ST.ACCENT["_" + city] = CITIES[city]["c1"]
    return ST.accent_css("_" + city)


def put(page, css_block):
    page = re.sub(r'<style id="mx-css">.*?</style>', '', page, flags=re.S)
    page = ST.put_css(page, css_block)
    return page.replace('</head>', CSS + '</head>', 1)


def main():
    write = "--write" in sys.argv
    stats = city_stats()
    infos = {c: [i for i in (station_info(x) for x in d["codes"]) if i] for c, d in CITIES.items()}
    ns = nt = 0
    for city, lst in infos.items():
        for i in lst:
            p = ROOT / "station" / i["code"] / "index.html"
            h = p.read_text()
            for m in ('rg', 'mx', 'stx-note'):
                h = re.sub(rf'<!--{m}-start-->.*?<!--{m}-end-->', '', h, flags=re.S)
            h = re.sub(r'<style id="rg-css">.*?</style>', '', h, flags=re.S)
            cm = re.search(r'<p class="crumb">.*?</p>', h, flags=re.S)
            sub = (f'You are at {H.escape(i["name"])} ({i["code"].upper()}), one of {len(lst)} {city} stations '
                   f'on ClearBerth. Tap any station below for its trains.')
            h = h[:cm.end()] + hero(city, sub, lst, stats[city], here=i["code"]) + ST.NOTE + h[cm.end():]
            h = put(h, accent(city))
            ns += 1
            if write:
                p.write_text(h)
    for p in sorted((ROOT / "train").glob("*/index.html")):
        h = p.read_text()
        rows = ST.ROW.findall(h)
        if len(rows) < 2:
            continue
        city = CITY_OF.get(rows[0][1].lower())
        if not city:
            continue
        m = re.search(r'<h1>(\d+) (.*?): live running status</h1>', h)
        if not m:
            continue
        no, name = m.group(1), m.group(2)
        _, blocks = ST.train_blocks(h, no, name)
        for k in ('stx', 'stx-rg', 'mx'):
            h = re.sub(rf'<!--{k}-start-->.*?<!--{k}-end-->', '', h, flags=re.S)
        g = re.search(r'<h2>\d+ at a glance</h2><p>.*?</p>', h, flags=re.S)
        if not g or not blocks:
            continue
        start = H.unescape(rows[0][0]).strip()
        sub = f'{name} starts its journey at {H.escape(start)} ({rows[0][1]}), one of {len(infos[city])} {city} stations on ClearBerth.'
        h = h[:g.end()] + blocks + hero(city, sub, infos[city], stats[city]) + h[g.end():]
        h = put(h, accent(city))
        nt += 1
        if write:
            p.write_text(h)
    for c in CITIES:
        print(c, 'stations', len(infos[c]), 'trains starting', stats[c]['trains'], 'states', len(stats[c]['states']))
    print(('written' if write else 'dry run'), 'station pages', ns, 'train pages', nt)


if __name__ == "__main__":
    main()
