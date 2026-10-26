#!/usr/bin/env python3
"""Builds /about/ and /guides/* from the shared page template (head + footer of an
existing page). Run from the repo root: python3 tools/build_content_pages.py
Facts in the guides come only from the IRCTC pages cited on each page."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = open(os.path.join(ROOT, 'train/12301/index.html'), encoding='utf-8').read()
HEAD_TPL = TPL[:TPL.index('</head>') + len('</head>')]
FOOTER = ('<footer><div class="wrap">&copy; 2026 ClearBerth. An independent app for Indian Railways travellers. '
          '<a href="https://clearberth.app/clearberth/privacy.htm">Privacy policy</a> &nbsp;·&nbsp; '
          '<a href="/about/">About</a> &nbsp;·&nbsp; <a href="/guides/">Guides</a></div></footer>')
READ_DATE = '25 October 2026'
STORES = ('<div class="stores"><a href="https://apps.apple.com/in/app/clearberth/id6802574946?ppid=f3449268-d660-4e16-ad6a-6d4030b3b2e4" rel="noopener"><img src="/shots/app-store-badge.svg" alt="Download on the App Store" height="52"></a>'
          '<a href="https://play.google.com/store/apps/details?id=com.aditya.clearberth&listing=tracking" rel="noopener"><img src="/shots/google-play-badge.png" alt="Get it on Google Play" height="52"></a></div>')
A = 'style="text-decoration:underline"'


def head(title, desc, path, crumbs):
    h = HEAD_TPL
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % html.escape(title), h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % html.escape(desc, quote=True), h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://clearberth.app%s">' % path, h)
    h = re.sub(r'<link rel="alternate" hreflang[^\n]*\n', '', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % html.escape(title, quote=True), h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % html.escape(desc, quote=True), h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="https://clearberth.app%s">' % path, h)
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": "https://clearberth.app" + u} for i, (n, u) in enumerate(crumbs)]
    ld = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: ld, h, flags=re.S)
    h = h.replace('</head>', '<style>.tt th,.tt td{white-space:normal;vertical-align:top}</style></head>')
    return h


def page(path, title, desc, crumbs, crumb_html, h1, lead, body):
    out = head(title, desc, path, crumbs)
    out += ('\n<body><div class="wrap">\n'
            '<div class="top"><a class="logo" href="/"><img src="/shots/icon.png" alt="" width="30" height="30">ClearBerth</a><a class="btn sm" href="/#get-app">Get the app</a></div>\n'
            '<p class="crumb">%s</p>\n<h1>%s</h1>\n<p class="lead">%s</p>\n%s\n'
            '<h2>Easier in the app</h2>\n<p>ClearBerth shows your berth on a diagram, tracks your PNR and alerts you when your waitlist moves.</p>\n%s\n'
            '<p style="margin-top:22px"><a %s href="/pnr-status/">Check PNR status</a> &nbsp;·&nbsp; <a %s href="/train-kahan-hai/">Train kahan hai?</a> &nbsp;·&nbsp; <a %s href="/guides/">All guides</a></p>\n'
            '</div>\n%s\n</body></html>\n') % (crumb_html, h1, lead, body, STORES, A, A, A, FOOTER)
    d = os.path.join(ROOT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


def sources(items):
    li = ''.join('<li><a %s href="%s" rel="noopener">%s</a>: %s</li>' % (A, u, html.escape(t), html.escape(n)) for t, u, n in items)
    return '<h2>Source</h2><p>Everything above comes from the IRCTC pages below, read on %s. Rules can change, so confirm on IRCTC before you act.</p><ul style="padding-left:22px;display:grid;gap:6px">%s</ul>' % (READ_DATE, li)


# ---------- About ----------
about_body = '''
<h2>What ClearBerth does</h2>
<p>ClearBerth is an app for people who travel on Indian Railways. It shows PNR status, draws your berth on a coach diagram, tracks where your train is and how late it runs, sends alerts when a waitlist number changes, and lets you search seat availability. The same app also has food and parcel tabs.</p>
<h2>Why it exists</h2>
<p>I built ClearBerth because I was the person refreshing my PNR every few minutes and doing delay maths in my head. I wanted one calm screen that answers the two questions that matter: where do I sit, and when does the train reach me.</p>
<h2>It is not the official IRCTC app</h2>
<p>ClearBerth is an independent app made for travellers. It is not run by IRCTC or Indian Railways. Use it alongside IRCTC for the things only IRCTC does. Our <a @@A@@ href="/guides/">guides</a> explain IRCTC&rsquo;s own rules and link to the IRCTC page each one comes from.</p>
<h2>What it costs</h2>
<p>PNR status, the berth diagram and live train tracking are free and supported by short ads. If you want alerts, you pay once per journey. The price is shown in the app before you buy. There is no subscription.</p>
<h2>About the train data</h2>
<p>Train data comes from railway data providers. Live running data can lag or change, so treat times as best estimates and follow station announcements for anything critical. The train, route and station pages on this site show scheduled timetable figures. Real running times change with delays.</p>
<h2>Languages</h2>
<p>ClearBerth works in English and Hindi, including alerts. This site has Hindi pages for PNR status and for each train page.</p>
<h2>Contact</h2>
<p>Write to <a @@A@@ href="mailto:clearberth.support@gmail.com?subject=ClearBerth%20support">clearberth.support@gmail.com</a>. Ideas and corrections are welcome. Read the <a @@A@@ href="https://clearberth.app/clearberth/privacy.htm">privacy policy</a> to see what the app stores.</p>
'''.replace('@@A@@', A)
page('/about/', 'About ClearBerth: an independent app for Indian Railways travellers',
     'What ClearBerth is, why it was built, what it costs and where its train data comes from. An independent app, not the official IRCTC app.',
     [("ClearBerth", "/"), ("About", "/about/")],
     '<a href="/">ClearBerth</a> / About', 'About ClearBerth',
     'ClearBerth is an independent app that makes an Indian train journey easier to follow, from the first waitlist check to the last station.', about_body)

# ---------- Guides ----------
IRCTC_WL = 'https://contents.irctc.co.in/en/New_Facilities_Waitlisted_E-Tkt.pdf'
IRCTC_CAN = 'https://contents.irctc.co.in/en/eticketCancel.html'
IRCTC_VIK = 'https://contents.irctc.co.in/en/VIKALP_Scheme.pdf'

g1 = '''
<h2>The short answer</h2>
<p>If every passenger on an e-ticket is still waitlisted after the chart is prepared, IRCTC cancels the ticket, the names are dropped from the chart and the passengers are not allowed to board.</p>
<h2>What IRCTC says happens, by ticket status</h2>
<div class="tt"><table><thead><tr><th>Status after the chart is prepared</th><th>What happens</th></tr></thead><tbody>
<tr><td>Fully confirmed, or fully RAC</td><td>The passenger&rsquo;s name appears in the chart and they can travel.</td></tr>
<tr><td>Partly confirmed or partly RAC, with the rest waitlisted</td><td>The names appear in the charts, including the waitlisted passengers.</td></tr>
<tr><td>Fully waitlisted (every passenger in the booking)</td><td>The names are dropped from the charts and IRCTC cancels the ticket.</td></tr>
</tbody></table></div>
<h2>If your ticket is cancelled</h2>
<ul style="padding-left:22px;display:grid;gap:8px">
<li>The passenger is &ldquo;not allowed to board the train&rdquo;. A person found travelling is treated as a passenger travelling without a ticket under Railway Rules.</li>
<li>IRCTC arranges the refund from the Railways and credits it electronically to the customer&rsquo;s account (or the agent&rsquo;s account for an agent booking).</li>
</ul>
<h2>What you can do before the chart</h2>
<p>Check your PNR status often as the journey date gets close. ClearBerth&rsquo;s <a @@A@@ href="/pnr-status/">PNR status page</a> shows it and the app can alert you when the waitlist number changes. IRCTC also offers an option to move a waitlisted ticket to another train, described in our <a @@A@@ href="/guides/vikalp-alternate-trains/">VIKALP guide</a>. To cancel a ticket yourself, see <a @@A@@ href="/guides/cancel-irctc-e-ticket/">how IRCTC e-ticket cancellation works</a>.</p>
<h2>A note on dates</h2>
<p>The IRCTC page this guide is based on carries a 2019 copyright line and no other date. IRCTC may have changed its rules since, so check IRCTC before relying on it.</p>
'''.replace('@@A@@', A) + sources([("IRCTC: New facilities in waitlisted e-ticket", IRCTC_WL, "what happens to waitlisted, RAC and confirmed passengers after the chart is prepared")])

g2 = '''
<h2>The short answer</h2>
<p>A confirmed IRCTC e-ticket can be cancelled online until the chart is prepared, not at a counter. The charge depends on how long before departure you cancel. After the chart, you file a TDR (Ticket Deposit Receipt) online instead.</p>
<h2>Charges for a confirmed ticket</h2>
<p>IRCTC&rsquo;s page lists these charges per passenger.</p>
<div class="tt"><table><thead><tr><th>When you cancel</th><th>Charge</th></tr></thead><tbody>
<tr><td>More than 48 hours before departure</td><td>Flat amount by class: AC First/Executive Rs.240, AC 2 Tier/First Class Rs.200, AC 3 Tier/AC Chair Car/AC 3 Economy Rs.180, Sleeper Rs.120, Second Class Rs.60</td></tr>
<tr><td>Within 48 hours and up to 12 hours before departure</td><td>25% of the fare, subject to the flat minimum above</td></tr>
<tr><td>Less than 12 hours and up to 4 hours before departure (or until chart preparation, if earlier)</td><td>50% of the fare, subject to minimum charges</td></tr>
</tbody></table></div>
<p>For trains that depart before noon, the chart is usually prepared the previous night.</p>
<h2>After the chart is prepared</h2>
<ul style="padding-left:22px;display:grid;gap:8px">
<li>A normal user cannot cancel online after chart preparation and must file a TDR online.</li>
<li>A confirmed ticket gets no refund if it is neither cancelled nor has a TDR filed online up to 4 hours before departure.</li>
<li>An RAC e-ticket gets no refund if it is not cancelled, or the TDR is not filed online, up to 30 minutes before departure.</li>
<li>Agents cannot cancel after chart preparation. They email etickets@irctc.co.in with the PNR, transaction ID and passenger details, and IRCTC files the TDR.</li>
</ul>
<h2>Party and family tickets</h2>
<p>If some passengers on a ticket are confirmed and others are on RAC or the waitlist, the confirmed passengers still get a full refund minus clerkage. This needs cancelling, or filing TDRs online, for all passengers up to 30 minutes before departure.</p>
<h2>Tatkal tickets</h2>
<p>There is no refund on a confirmed Tatkal e-ticket. Cancelling a contingent or waitlisted Tatkal ticket carries charges under Railway rules. Partial cancellation is allowed.</p>
<h2>If the train is cancelled</h2>
<p>If the train is marked CANCELLED in the reservation system because of breaches, floods or accidents, a full refund is allowed when the ticket is cancelled within three days of the scheduled departure.</p>
<h2>Waitlisted tickets</h2>
<p>The IRCTC cancellation page gives no separate refund rule for ordinary waitlisted tickets. What happens to a ticket that is still waitlisted at charting is on another IRCTC page, summarised in <a @@A@@ href="/guides/waitlisted-ticket-after-chart/">our waitlist guide</a>.</p>
<h2>A note on dates</h2>
<p>The IRCTC page shows no date, so the effective date of these charges cannot be confirmed from it. Check IRCTC for the current figures before you cancel.</p>
'''.replace('@@A@@', A) + sources([("IRCTC: E-ticket cancel", IRCTC_CAN, "cancellation charges, TDR timing, party tickets, Tatkal and cancelled trains")])

g3 = '''
<h2>The short answer</h2>
<p>VIKALP is an IRCTC option for waitlisted passengers. You pick up to seven alternate trains, and if you are still fully waitlisted after charting, IRCTC may move the whole booking to one of them. It does not guarantee a confirmed berth.</p>
<h2>Who can use it</h2>
<p>Waitlisted passengers on any train type and class, whatever the booking quota or concession. Opting in does not guarantee a confirmed berth, which depends on train and berth availability.</p>
<h2>How the alternate train is chosen</h2>
<ul style="padding-left:22px;display:grid;gap:8px">
<li>You can select up to seven alternate trains.</li>
<li>The alternate train must depart between 30 minutes and 72 hours after the original train&rsquo;s scheduled departure.</li>
<li>Passengers who remain fully waitlisted after charting are considered for allotment.</li>
<li>You can also opt in later, before charting, through the booked ticket history link.</li>
</ul>
<h2>What happens to the original ticket</h2>
<ul style="padding-left:22px;display:grid;gap:8px">
<li>All passengers on a PNR are moved together, or none are, and the class stays the same.</li>
<li>Boarding or destination stations may shift to nearby cluster stations.</li>
<li>Transferred passengers appear on a separate list, not the original waitlist charts.</li>
<li>If you are allotted an alternate berth, you cannot board the original train.</li>
<li>Journey changes are not allowed after allotment. You would need to cancel and rebook.</li>
</ul>
<h2>Charges</h2>
<p>No extra charge applies, and there is no refund for any fare difference, including Tatkal charges. Cancellation charges follow the berth and train status on the alternate train. A passenger who cancels after allotment is treated as confirmed, so the standard cancellation rules apply. If you do not travel on the alternate train, you can claim a refund by filing a TDR.</p>
<h2>Check your PNR twice</h2>
<p>IRCTC advises checking PNR status after charting, and again after the alternate train&rsquo;s chart is prepared, because last-minute changes can happen. Once a train list is selected it can be updated only once, and the scheme cannot be changed after you opt in.</p>
<p>See also: <a @@A@@ href="/guides/waitlisted-ticket-after-chart/">what happens to a waitlisted ticket after the chart</a>.</p>
<h2>A note on dates</h2>
<p>The IRCTC document shows no date. Check IRCTC for the current terms before you opt in.</p>
'''.replace('@@A@@', A) + sources([("IRCTC: VIKALP scheme", IRCTC_VIK, "who can opt in, alternate trains, what happens to the original ticket, charges")])

guides = [
    ('/guides/waitlisted-ticket-after-chart/', 'What happens to a waitlisted IRCTC e-ticket after the chart is prepared',
     'IRCTC says a fully waitlisted e-ticket is cancelled at charting and the passenger cannot board. Partly confirmed and RAC cases, and the refund, explained from the IRCTC page.',
     'Waitlisted e-ticket after the chart', 'What happens to a waitlisted e-ticket after the chart is prepared',
     'The chart is the deadline for a waitlisted ticket. Here is what IRCTC says happens at that point.', g1),
    ('/guides/cancel-irctc-e-ticket/', 'How to cancel an IRCTC e-ticket: charges, TDR and refund timing',
     'Cancellation charges by time before departure, what a TDR is, and the rules for RAC, party, Tatkal and cancelled trains, from IRCTC&rsquo;s own cancellation page.'.replace('&rsquo;', "'"),
     'Cancel an IRCTC e-ticket', 'How to cancel an IRCTC e-ticket: charges, TDR and refund timing',
     'What it costs to cancel an e-ticket on IRCTC, how the charge changes as departure gets closer, and what to do once the chart is prepared.', g2),
    ('/guides/vikalp-alternate-trains/', 'IRCTC VIKALP: how waitlisted passengers are moved to another train',
     'How IRCTC&rsquo;s VIKALP scheme works: who can opt in, how alternate trains are allotted, what happens to the original ticket and the charges.'.replace('&rsquo;', "'"),
     'VIKALP alternate trains', 'IRCTC VIKALP: moving a waitlisted ticket to another train',
     'VIKALP lets a waitlisted passenger ask IRCTC to try other trains if the original one does not confirm. This guide sets out the rules IRCTC publishes.', g3),
]
for path, title, desc, short, h1, lead, body in guides:
    page(path, title + ' | ClearBerth', desc, [("ClearBerth", "/"), ("Guides", "/guides/"), (short, path)],
         '<a href="/">ClearBerth</a> / <a href="/guides/">Guides</a> / ' + html.escape(short), h1, lead, body)

idx = '<div class="links" style="margin-top:20px;display:grid;gap:12px">' + ''.join(
    '<a href="%s" style="border-radius:16px;padding:14px 18px"><b>%s</b><br><span style="font-size:14px;color:#7A819E">%s</span></a>' % (p, html.escape(h), html.escape(l))
    for p, t, d, s, h, l, b in guides) + '</div>'
page('/guides/', 'Indian Railways ticket guides: waitlist, cancellation and VIKALP | ClearBerth',
     'Plain-language guides to IRCTC ticket rules. Each one links to the IRCTC page it is based on.',
     [("ClearBerth", "/"), ("Guides", "/guides/")], '<a href="/">ClearBerth</a> / Guides', 'Guides to IRCTC ticket rules',
     'Short guides on waitlists, cancellation and refunds. Each one names the IRCTC page it is based on and the date we read it, because rules change.', idx)
print('built about + guides')
