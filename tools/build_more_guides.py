#!/usr/bin/env python3
"""Adds the cancellation and VIKALP guides (same layout as the other /guides/ pages),
links them from /guides/ and the sitemap. Facts come only from the IRCTC pages cited.
Run from the repo root: python3 tools/build_more_guides.py"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = open(os.path.join(ROOT, 'guides/tatkal-ticket-booking-rules/index.html'), encoding='utf-8').read()
HEAD = TPL[:TPL.index('</head>') + 7]
TAIL = TPL[TPL.index('<h2>Check your ticket in the app</h2>'):]
CHECKED = '25 October 2026'      # date the IRCTC pages were read
TODAY = '2026-11-01'
A = 'style="text-decoration:underline"'
E = html.escape


def build(path, title, desc, short, h1, lead, body, srcs):
    h = HEAD
    h = re.sub(r'<title>.*?</title>', lambda m: '<title>%s | ClearBerth</title>' % E(title), h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', lambda m: '<meta name="description" content="%s">' % E(desc, quote=True), h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', lambda m: '<link rel="canonical" href="https://clearberth.app%s">' % path, h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: '<meta property="og:title" content="%s">' % E(title, quote=True), h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: '<meta property="og:description" content="%s">' % E(desc, quote=True), h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', lambda m: '<meta property="og:url" content="https://clearberth.app%s">' % path, h)
    crumbs = [("ClearBerth", "/"), ("Guides", "/guides/"), (short, path)]
    bc = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": "https://clearberth.app" + u} for i, (n, u) in enumerate(crumbs)]})
    art = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
                      "datePublished": TODAY, "dateModified": TODAY,
                      "author": {"@type": "Organization", "name": "ClearBerth", "url": "https://clearberth.app/"},
                      "publisher": {"@type": "Organization", "name": "ClearBerth", "url": "https://clearberth.app/"},
                      "mainEntityOfPage": "https://clearberth.app" + path})
    lds = iter([bc, art])
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">%s</script>' % next(lds), h, flags=re.S)
    src = '<h2>Sources</h2><ul class="src">' + ''.join('<li><a %s href="%s" rel="noopener">%s</a></li>' % (A, u, E(t)) for t, u in srcs) + '</ul>'
    top = ('\n<body><div class="wrap art">\n'
           '<div class="top"><a class="logo" href="/"><img src="/shots/icon.png" alt="" width="30" height="30">ClearBerth</a><a class="btn sm" href="/#get-app">Get the app</a></div>\n'
           '<p class="crumb"><a href="/">ClearBerth</a> / <a href="/guides/">Guides</a> / %s</p>\n<h1>%s</h1>\n<p class="lead">%s</p>\n'
           '<p class="meta">Last checked: %s. Railway rules change, so confirm on IRCTC before you book or cancel.</p>\n') % (
        E(short), E(h1), E(lead), CHECKED)
    out = h + top + body.replace('@@A@@', A) + '\n' + src + TAIL
    d = os.path.join(ROOT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


UL = '<ul>%s</ul>'
li = lambda *x: ''.join('<li>%s</li>' % i for i in x)
R = '&#8377;'

cancel = '''
<h2>Can you cancel an e-ticket online?</h2>
<p>IRCTC says an e-ticket can be cancelled online until the chart is prepared; cancellations are not allowed at railway counters. A cancelled ticket's refund goes back to the account used for booking. How much you lose depends on how long before departure you cancel. Once the chart is prepared, a normal user cannot cancel online and must file a TDR (Ticket Deposit Receipt) online instead.</p>
<h2>Charges for a confirmed ticket</h2>
<p>IRCTC's cancellation page lists these charges per passenger.</p>
<div class="tt"><table><thead><tr><th>When you cancel</th><th>Charge</th></tr></thead><tbody>
<tr><td>More than 48 hours before departure</td><td>A flat amount by class: AC First/Executive %(R)s240, AC 2 Tier/First Class %(R)s200, AC 3 Tier/AC Chair Car/AC 3 Economy %(R)s180, Sleeper %(R)s120, Second Class %(R)s60</td></tr>
<tr><td>Within 48 hours and up to 12 hours before departure</td><td>25%% of the fare, subject to the flat minimum above</td></tr>
<tr><td>Less than 12 hours and up to 4 hours before departure (or until chart preparation, if earlier)</td><td>50%% of the fare, subject to minimum charges</td></tr>
</tbody></table></div>
<p style="margin-top:10px;font-size:14px">For trains starting up to 12 noon, IRCTC says the chart is usually prepared the previous night.</p>
<h2>After the chart is prepared</h2>
%(after)s
<h2>Party and family tickets</h2>
<p>If some passengers on a ticket are confirmed and others are on RAC or the waitlist, the confirmed passengers still get a full refund minus clerkage. This needs all passengers to be cancelled, or TDRs filed online, up to 30 minutes before departure.</p>
<h2>Tatkal tickets</h2>
<p>IRCTC says there is no refund on a confirmed Tatkal e-ticket. Cancelling a contingent or waitlisted Tatkal ticket carries charges under Railway rules. Partial cancellation is allowed. See our <a @@A@@ href="/guides/tatkal-ticket-booking-rules/">Tatkal guide</a>.</p>
<h2>If the train is cancelled</h2>
<p>If the train is marked CANCELLED in the reservation system because of breaches, floods or accidents, IRCTC allows a full refund when the ticket is cancelled within three days of the scheduled departure. Other cases are in our guide to <a @@A@@ href="/guides/train-cancelled-diverted-late-refund-tdr/">cancelled, diverted and late trains</a>.</p>
<h2>Waitlisted tickets</h2>
<p>The cancellation page gives no separate refund rule for ordinary waitlisted tickets. What happens to a ticket that is still waitlisted at charting is in our <a @@A@@ href="/guides/waitlisted-e-ticket-after-chart/">waitlist guide</a>.</p>
<h2>In short</h2>
%(short)s
<div class="note">The IRCTC cancellation page shows no date, so the date these charges took effect cannot be confirmed from it. Check IRCTC for the current figures before you cancel.</div>
''' % {'R': R,
       'after': UL % li('A normal user cannot cancel online after chart preparation and must file a TDR online.',
                         'A confirmed ticket gets no refund if it is neither cancelled nor has a TDR filed online up to 4 hours before departure.',
                         'An RAC e-ticket gets no refund if it is not cancelled, or the TDR is not filed online, up to 30 minutes before departure.',
                         'Agents cannot cancel after chart preparation. They email etickets@irctc.co.in with the PNR, transaction ID and passenger details, and IRCTC files the TDR.'),
       'short': UL % li('Cancel online before the chart; after it, file a TDR.',
                         'The charge rises from a flat amount to 25% and then 50% as departure gets closer.',
                         'A confirmed ticket gets nothing back if neither cancelled nor TDR-filed up to 4 hours before departure.')}

vikalp = '''
<h2>What is VIKALP?</h2>
<p>VIKALP is an IRCTC option for waitlisted passengers. You pick alternate trains when you book, and if every passenger on the ticket is still waitlisted after charting, IRCTC may move the booking to one of them. IRCTC says opting in does not guarantee a confirmed berth, which depends on train and berth availability.</p>
<h2>Who can use it</h2>
<p>Waitlisted passengers on any train type and class, whatever the booking quota or concession.</p>
<h2>How the alternate train is chosen</h2>
%(choose)s
<h2>What happens to the original ticket</h2>
%(orig)s
<h2>Charges</h2>
<p>IRCTC says no extra charge applies, and there is no refund for any fare difference, Tatkal charges included. Cancellation charges follow the berth and train status on the alternate train. A passenger who cancels after allotment is treated as confirmed, so the standard cancellation rules apply (see <a @@A@@ href="/guides/cancel-irctc-e-ticket/">how IRCTC e-ticket cancellation works</a>). If you do not travel on the alternate train, you can claim a refund by filing a TDR.</p>
<h2>Check your PNR twice</h2>
<p>IRCTC advises checking PNR status after charting, and again after the alternate train's chart is prepared, because last-minute changes can happen. Once a train list is selected it can be updated only once, and the scheme cannot be changed after you opt in. What happens to a ticket that stays waitlisted is in our <a @@A@@ href="/guides/waitlisted-e-ticket-after-chart/">waitlist guide</a>.</p>
<h2>In short</h2>
%(short)s
<div class="note">The IRCTC VIKALP document shows no date. Check IRCTC for the current terms before you opt in.</div>
''' % {'choose': UL % li('You can select up to seven alternate trains.',
                          "The alternate train must depart between 30 minutes and 72 hours after the original train's scheduled departure.",
                          'Passengers who remain fully waitlisted after charting are considered for allotment.',
                          'You can also opt in later, before charting, through the booked ticket history link.'),
       'orig': UL % li('All passengers on a PNR are moved together, or none are, and the class stays the same.',
                        'Boarding or destination stations may shift to nearby cluster stations.',
                        'Transferred passengers appear on a separate list, not the original waitlist charts.',
                        'If you are allotted an alternate berth, you cannot board the original train.',
                        'Journey changes are not allowed after allotment. You would need to cancel and rebook.'),
       'short': UL % li('Up to seven alternate trains, departing 30 minutes to 72 hours after the original.',
                         'The whole PNR moves together, in the same class, or not at all.',
                         'No extra charge and no refund of any fare difference; a confirmed berth is not guaranteed.')}

GUIDES = [
    ('/guides/cancel-irctc-e-ticket/', 'How to cancel an IRCTC e-ticket: charges, TDR and deadlines',
     "Cancellation charges by time before departure, what a TDR is, and the rules for RAC, party, Tatkal and cancelled trains, from IRCTC's cancellation page.",
     'Cancel an e-ticket', 'How to cancel an IRCTC e-ticket: charges, TDR and deadlines',
     'What it costs to cancel an e-ticket on IRCTC, how the charge changes as departure gets closer, and what to do once the chart is prepared.',
     'Charges by time before departure, and the rules after the chart.', cancel,
     [("IRCTC: E-ticket cancellation", "https://contents.irctc.co.in/en/eticketCancel.html")]),
    ('/guides/vikalp-alternate-trains/', 'IRCTC VIKALP: how a waitlisted ticket is moved to another train',
     "How IRCTC's VIKALP scheme works: who can opt in, how alternate trains are allotted, what happens to the original ticket and the charges.",
     'VIKALP scheme', 'IRCTC VIKALP: moving a waitlisted ticket to another train',
     'VIKALP lets a waitlisted passenger ask IRCTC to try other trains if the original one does not confirm. This guide sets out the rules IRCTC publishes.',
     'Who can opt in, how trains are allotted, and the charges.', vikalp,
     [("IRCTC: VIKALP scheme", "https://contents.irctc.co.in/en/VIKALP_Scheme.pdf")]),
]
for p, t, d, s, h1, lead, _blurb, body, srcs in GUIDES:
    build(p, t, d, s, h1, lead, body, srcs)

# guides index + sitemap (idempotent)
ip = os.path.join(ROOT, 'guides/index.html')
ix = open(ip, encoding='utf-8').read()
for p, t, d, s, h1, lead, blurb, body, srcs in GUIDES:
    if 'href="%s"' % p in ix:
        continue
    card = '<a href="%s"><b>%s</b><span>%s</span></a>' % (p, E(h1), E(blurb))
    ix = ix.replace('</div><div class="note">', card + '</div><div class="note">', 1)
open(ip, 'w', encoding='utf-8').write(ix)
sp = os.path.join(ROOT, 'sitemap.xml')
sm = open(sp, encoding='utf-8').read()
for p, *_ in GUIDES:
    if p not in sm:
        sm = sm.replace('</urlset>', '  <url><loc>https://clearberth.app%s</loc><lastmod>%s</lastmod></url>\n</urlset>' % (p, TODAY))
sm = sm.replace('/guides/</loc><lastmod>2026-10-26', '/guides/</loc><lastmod>' + TODAY)
open(sp, 'w', encoding='utf-8').write(sm)
print('built', len(GUIDES), 'guides')
