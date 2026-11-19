#!/usr/bin/env python3
"""Per-state template additions (19 Nov 2026), one state at a time.

For the chosen state(s):
  * STATION pages of stations in that state get the state colour accent
    (the regional photo section is added separately by add_region_sections.py).
  * TRAIN pages (English) of trains whose FIRST station is in that state get:
      - the state colour accent
      - "States on this route": the states its stops are in, in route order,
        worked out from tools/_station_states.json
      - "Tatkal for <train>": the opening day and times, counted from the
        train's start station, from IRCTC's Tatkal FAQ (see the Tatkal guide)
      - the start state's regional photo section (same block as station pages)

  python3 tools/add_state_templates.py --state "Uttar Pradesh" [--write]
Safe to run twice: it replaces its own blocks (<!--stx-...--> markers).
"""
import argparse, html as H, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import add_region_sections as RG  # noqa: E402

STATES = json.loads((ROOT / "tools" / "_station_states.json").read_text())

# one accent colour per state (design choice, not data)
ACCENT = {
    "Uttar Pradesh": "#0E7C66", "Rajasthan": "#B4531A", "Maharashtra": "#B23A48",
    "Madhya Pradesh": "#5E7D1E", "Bihar": "#A0522D", "Gujarat": "#C0392B",
    "West Bengal": "#1F6FB2", "Punjab": "#C97A00", "Andhra Pradesh": "#00838F",
    "Karnataka": "#B71C1C", "Haryana": "#6D8B00", "Jharkhand": "#2E7D32",
    "Odisha": "#AD5A00", "Assam": "#1B7F4C", "Tamil Nadu": "#8E24AA",
    "Kerala": "#2E8B57", "Telangana": "#D2691E", "Chhattisgarh": "#3E7B27",
    "Uttarakhand": "#2F6E8F", "Jammu & Kashmir": "#3949AB", "Himachal Pradesh": "#00796B",
    "Nagaland": "#8D3B2F", "Arunanchal Pradesh": "#5D4E9A", "Manipur": "#7B3F8C",
}

NOTE = ('<!--stx-note-start--><div class="stx-note"><b>Got a photo of this station?</b> '
        'Message us on X at <a href="https://x.com/ClearBerthApp" rel="noopener">@ClearBerthApp</a> '
        'and ask us to put your preferred photo on this page.</div><!--stx-note-end-->')

UA = 'style="text-decoration:underline"'
ROW = re.compile(r'<tr><td>(?:<a [^>]*>)?([^<]+?)(?:</a>)? <small>\(([A-Z0-9]+)\)</small></td><td>([^<]*)</td><td>([^<]*)</td><td>(\d+)</td></tr>')


def accent_css(state):
    c = ACCENT[state]
    return (f'<style id="stx-accent">:root{{--stx:{c}}}'
            '.top{border-bottom:4px solid var(--stx);padding-bottom:10px}'
            'h1{border-left:6px solid var(--stx);padding-left:12px}'
            '.stx h2{color:var(--stx)}.stx p{margin:0 0 12px}'
            '.stx-chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 4px}'
            '.stx-chips span{border:1.5px solid var(--stx);color:var(--ink);border-radius:999px;padding:6px 12px;font-size:14px}'
            '.stx-chips b{color:var(--stx)}'
            '.stx-note{background:#FFF7D6;border:2px solid var(--stx);border-radius:14px;padding:12px 16px;margin:12px 0 18px;font-size:15px;color:var(--ink)}'
            '.stx-note a{color:var(--stx);font-weight:600;text-decoration:underline}</style>')


def put_css(page, css):
    page = re.sub(r'<style id="stx-accent">.*?</style>', '', page, flags=re.S)
    return page.replace('</head>', css + '</head>', 1)


def train_blocks(page, no, name):
    rows = ROW.findall(page)
    if len(rows) < 2:
        return None, None
    stops = [dict(name=H.unescape(n).strip(), code=c.lower(), arr=a, dep=d, day=int(dy)) for n, c, a, d, dy in rows]
    start = stops[0]
    st_state = STATES.get(start["code"])
    # states in route order with stop counts
    order, count, unknown = [], {}, 0
    for s in stops:
        stt = STATES.get(s["code"])
        if not stt:
            unknown += 1
            continue
        if stt not in count:
            order.append(stt)
            count[stt] = 0
        count[stt] += 1
    show = lambda x: 'Arunachal Pradesh' if x == 'Arunanchal Pradesh' else x
    chips = ''.join(f'<span>{H.escape(show(x))} <b>{count[x]}</b></span>' for x in order)
    total = len(stops)
    if len(order) == 1:
        lead = f'The stops of {name} that we have placed on the map are all in {H.escape(show(order[0]))}.'
    else:
        ut = any(x in ('Delhi', 'Jammu & Kashmir') for x in order)
        kind = 'states and union territories' if ut else 'states'
        lead = (f'{name} has {total} scheduled stops. In route order, they are in these '
                f'{len(order)} {kind}. The number is how many stops fall in each.')
    note = ''
    if unknown:
        note = (f'<p style="font-size:14px;color:#7A819E">{unknown} stop{"s are" if unknown > 1 else " is"} '
                'not yet placed in a state in our records and not counted here.</p>')
    states_html = (f'<section class="stx" id="stx-states"><h2>States on this route</h2><p>{lead}</p>'
                   f'<div class="stx-chips">{chips}</div>{note}</section>')

    # Tatkal, counted from the start station (IRCTC Tatkal FAQ)
    dep = start["dep"]
    later = next((s for s in stops if s["day"] >= 2), None)
    extra = ''
    if later:
        extra = (f'<p>Boarding later on the route? The day still counts from {H.escape(start["name"])}. '
                 f'{name} reaches {H.escape(later["name"])} on day {later["day"]} of its run, so for a ticket from '
                 f'{H.escape(later["name"])}, Tatkal opens {later["day"]} days before the date you board there.</p>')
    tatkal_html = (
        f'<section class="stx" id="stx-tatkal"><h2>Tatkal for {no}</h2>'
        f'<p>IRCTC opens Tatkal one day before the train leaves its originating station. {name} starts from '
        f'{H.escape(start["name"])} at {dep}, so Tatkal for a run opens the day before that date: '
        f'at <b>10:00</b> for AC classes (2A, 3A, 3E, CC) and at <b>11:00</b> for non-AC classes (SL, 2S). '
        f'Whether this train has a Tatkal quota in your class and between your stations is shown on IRCTC when you book.</p>'
        f'{extra}<p><a {UA} href="/guides/tatkal-ticket-booking-rules/">Tatkal rules, charges and refunds</a></p></section>')
    return st_state, '<!--stx-start-->' + states_html + tatkal_html + '<!--stx-end-->'


def do_train(path, state, write):
    page = path.read_text()
    m = re.search(r'<h1>(\d+) (.*?): live running status</h1>', page)
    if not m:
        return 'nohead'
    no, name = m.group(1), m.group(2)
    st_state, blocks = train_blocks(page, no, name)
    if st_state != state or not blocks:
        return 'other'
    page = re.sub(r'<!--stx-start-->.*?<!--stx-end-->', '', page, flags=re.S)
    page = re.sub(r'<!--stx-rg-start-->.*?<!--stx-rg-end-->', '', page, flags=re.S)
    r = RG.STATE_TO_REGION.get(state)
    rg = ''
    if r:
        rg = ('<!--stx-rg-start-->' + RG.CSS_ONE.replace('id="rg-css"', 'id="rg-css-t"') +
              '<div class="rg-all">' + RG.section(r) + '</div><!--stx-rg-end-->')
    # after the "at a glance" paragraph
    g = re.search(r'<h2>\d+ at a glance</h2><p>.*?</p>', page, flags=re.S)
    if not g:
        return 'noglance'
    page = page[:g.end()] + blocks + rg + page[g.end():]
    page = put_css(page, accent_css(state))
    if write:
        path.write_text(page)
    return 'ok'


def do_station(path, state, write):
    page = path.read_text()
    page = re.sub(r'<!--stx-note-start-->.*?<!--stx-note-end-->', '', page, flags=re.S)
    if '<!--rg-end-->' in page:
        page = page.replace('<!--rg-end-->', '<!--rg-end-->' + NOTE, 1)
    else:
        m = re.search(r'<p class="crumb">.*?</p>', page, flags=re.S)
        if m:
            page = page[:m.end()] + NOTE + page[m.end():]
    page = put_css(page, accent_css(state))
    if write:
        path.write_text(page)
    return 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', required=True, help='a state name, or ALL')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--only')
    a = ap.parse_args()
    states = list(ACCENT) if a.state == 'ALL' else [a.state]
    for st in states:
        if st not in ACCENT:
            sys.exit('no accent colour set for ' + st)
        run(st, a)


def run(state, a):
    res = {}
    for p in sorted((ROOT / 'train').glob('*/index.html')):
        if a.only and p.parent.name not in a.only.split(','):
            continue
        k = do_train(p, state, a.write)
        res[k] = res.get(k, 0) + 1
    ns = 0
    if not a.only:
        for code, stt in STATES.items():
            p = ROOT / 'station' / code / 'index.html'
            if stt == state and p.exists():
                do_station(p, state, a.write); ns += 1
    print(state, ('written' if a.write else 'dry run'), 'trains:', res.get('ok', 0), 'stations:', ns)


if __name__ == '__main__':
    main()
