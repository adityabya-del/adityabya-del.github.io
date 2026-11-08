# Builds the About, Contact and Guides pages in the same style as the existing station pages.
import re, os, html, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(ROOT)
DATE = '2026-10-26'
DATE_H = '26 October 2026'
base = open('station/aji/index.html', encoding='utf-8').read()
styles = re.findall(r'<style>.*?</style>', base, flags=re.S)
STYLE = ''.join(styles)
STYLE += '''<style>
.art p{margin:0 0 14px}.art ul,.art ol{margin:0 0 16px;padding-left:22px;display:grid;gap:8px}
.art h2{margin:34px 0 10px}
.note{border:1.5px solid var(--line);background:var(--mist);border-radius:16px;padding:14px 16px;font-size:15px;margin:22px 0}
.src{font-size:14.5px}.src li{overflow-wrap:anywhere}
.meta{font-size:14px;color:#7A819E;margin:0 0 20px}
.cards{display:grid;gap:14px;margin:22px 0}.cards a{display:block;border:1.5px solid var(--line);border-radius:16px;padding:16px 18px}.cards a:hover{border-color:var(--indigo)}.cards b{display:block;color:var(--ink);font:600 18px var(--font-head);margin-bottom:4px}.cards span{font-size:15px}
.fnav{display:flex;flex-wrap:wrap;gap:6px 18px;margin-bottom:10px}
</style>'''
HEAD_GA = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-J9D9G65GNJ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-J9D9G65GNJ');
</script>'''
STORES = '''<div class="stores"><a href="https://apps.apple.com/in/app/clearberth/id6802574946" rel="noopener"><img src="/shots/app-store-badge.svg" alt="Download on the App Store" height="52"></a><a href="https://play.google.com/store/apps/details?id=com.aditya.clearberth" rel="noopener"><img src="/shots/google-play-badge.png" alt="Get it on Google Play" height="52"></a></div>'''
FOOT = '''<footer><div class="wrap"><div class="fnav"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/guides/">Guides</a><a href="/pnr-status/">PNR status</a><a href="https://clearberth.app/clearberth/privacy.htm">Privacy policy</a></div>&copy; 2026 ClearBerth. An independent app for Indian Railways travellers. Not affiliated with IRCTC or Indian Railways.</div></footer>'''
e = html.escape

def page(path, title, desc, crumbs, h1, lead, body, article=False, sources=None):
    url = 'https://clearberth.app/' + path.strip('/') + '/'
    url = url.replace('//', '/').replace('https:/', 'https://')
    bc = [{"@type": "ListItem", "position": 1, "name": "ClearBerth", "item": "https://clearberth.app/"}]
    for i, (name, href) in enumerate(crumbs, start=2):
        bc.append({"@type": "ListItem", "position": i, "name": name, "item": "https://clearberth.app" + href})
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": bc}]
    if article:
        ld.append({"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc,
                   "datePublished": DATE, "dateModified": DATE,
                   "author": {"@type": "Organization", "name": "ClearBerth", "url": "https://clearberth.app/"},
                   "publisher": {"@type": "Organization", "name": "ClearBerth", "url": "https://clearberth.app/"},
                   "mainEntityOfPage": url})
    crumb_html = '<a href="/">ClearBerth</a>' + ''.join(
        (' / <a href="%s">%s</a>' % (h, e(n)) if i < len(crumbs) - 1 else ' / ' + e(n)) for i, (n, h) in enumerate(crumbs))
    src_html = ''
    if sources:
        src_html = '<h2>Sources</h2><ul class="src">' + ''.join(
            '<li><a style="text-decoration:underline" href="%s" rel="noopener">%s</a></li>' % (u, e(t)) for t, u in sources) + '</ul>'
    meta = '<p class="meta">Last checked: %s. Railway rules change, so confirm on IRCTC before you book or cancel.</p>' % DATE_H if article else ''
    cta = '''<h2>Check your ticket in the app</h2><p>ClearBerth shows your PNR status with a berth diagram, tracks your train live and alerts you when your waitlist moves. Tickets are booked on IRCTC, not in ClearBerth.</p>''' + STORES if article else ''
    return '''<!DOCTYPE html>
<html lang="en"><head>
%s
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="apple-itunes-app" content="app-id=6802574946">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="%s"><meta property="og:site_name" content="ClearBerth">
<meta property="og:title" content="%s"><meta property="og:description" content="%s">
<meta property="og:url" content="%s"><meta property="og:image" content="https://clearberth.app/shots/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/shots/favicon.png"><link rel="apple-touch-icon" href="/shots/apple-touch-icon.png">
<link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
%s
%s</head>
<body><div class="wrap art">
<div class="top"><a class="logo" href="/"><img src="/shots/icon.png" alt="" width="30" height="30">ClearBerth</a><a class="btn sm" href="/#get-app">Get the app</a></div>
<p class="crumb">%s</p>
<h1>%s</h1>
<p class="lead">%s</p>
%s%s%s%s
</div>
%s
</body></html>
''' % (HEAD_GA, e(title), e(desc), url, 'article' if article else 'website', e(title), e(desc), url, STYLE,
       ''.join('<script type="application/ld+json">%s</script>\n' % json.dumps(x) for x in ld),
       crumb_html, e(h1), lead, meta, body, src_html, cta, FOOT)

def write(path, content):
    d = os.path.join(ROOT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(content)

IRCTC_TATKAL_FAQ = ('IRCTC: Tatkal frequently asked questions', 'https://contents.irctc.co.in/en/TatkalFaq.html')
PIB_TATKAL = ('PIB, 11 June 2025: Only Aadhaar authenticated user can book Tatkal tickets on IRCTC website and app from July 1', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2135694&reg=48&lang=2')
PIB_GEN = ('PIB, 15 September 2025: From October 1, Aadhaar authentication mandatory for booking general reserved tickets online during first 15 minutes', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2166889&reg=48&lang=2')
PIB_ARP = ('PIB, October 2024: Indian Railways cuts Advance Reservation Period from 120 days to 60 days w.e.f. 01.11.2024', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2065879&reg=48&lang=2')
IRCTC_REFUND = ('IRCTC: Refund rules and TDR filing, effective 12 November 2015', 'https://contents.irctc.co.in/en/REFUND%20RULES%20wef%2012-Nov-15.pdf')
IRCTC_DIVERSION = ('IRCTC: Diversion / cancellation of trains (notice)', 'https://contents.irctc.co.in/en/Important%20Message_Diversion.pdf')
IRCTC_WL = ('IRCTC: Scheme for issue of waitlisted e-tickets', 'https://contents.irctc.co.in/en/Waitlisted_E-Ticket.html')
IRCTC_RULES = ('IRCTC: Reservation rules', 'https://contents.irctc.co.in/en/term_src1.html')
PIB_BERTH25 = ('PIB, 5 December 2025: Automatic lower berth allotment for senior citizens and women aged 45 and above, subject to availability', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2199435&reg=1&lang=1')
PIB_WOMEN21 = ('PIB, 17 December 2021: Earmarking of accommodation for women passengers in long distance trains', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=1782695')

GUIDES = []  # (slug, title, short)

# ---------------- 1. Tatkal ----------------
slug = 'tatkal-ticket-booking-rules'
t = 'Tatkal ticket booking: timings, charges and rules'
body = '''
<h2>When does Tatkal open?</h2>
<p>IRCTC's Tatkal FAQ says Tatkal e-tickets open one day before the journey, not counting the journey date itself. On that opening day, AC classes (2A, 3A, CC, EC and 3E) open at 10:00 and non-AC classes (SL, FC and 2S) open at 11:00.</p>
<h2>Which classes have Tatkal?</h2>
<p>IRCTC states that Tatkal bookings are allowed in all classes except First AC and Executive Class. Whether a train offers Tatkal in a class still depends on the train and your stations, so the booking screen is the final word. Tatkal is issued for the distance you actually travel, subject to the train's distance restriction, so it is not limited to end-to-end journeys.</p>
<p>Ladies quota and general quota cannot be selected together with Tatkal. No concessions apply to Tatkal bookings.</p>
<h2>What does Tatkal cost?</h2>
<p>The Tatkal charge is added per passenger on top of the normal fare. It is 10% of the basic fare for second class and 30% for the other classes, but never below the minimum or above the maximum for the class:</p>
<div class="tt"><table><thead><tr><th>Class</th><th>Minimum</th><th>Maximum</th></tr></thead><tbody>
<tr><td>Second (sitting)</td><td>&#8377;10</td><td>&#8377;15</td></tr>
<tr><td>Sleeper</td><td>&#8377;100</td><td>&#8377;200</td></tr>
<tr><td>AC Chair Car</td><td>&#8377;125</td><td>&#8377;225</td></tr>
<tr><td>AC 3 Tier</td><td>&#8377;300</td><td>&#8377;400</td></tr>
<tr><td>AC 2 Tier</td><td>&#8377;400</td><td>&#8377;500</td></tr>
<tr><td>Executive</td><td>&#8377;400</td><td>&#8377;500</td></tr></tbody></table></div>
<p style="margin-top:10px;font-size:14px">IRCTC's page lists Executive in this table, although the same page says Tatkal is not allowed in Executive Class.</p>
<h2>Who can book Tatkal?</h2>
<p>A Ministry of Railways release dated 11 June 2025 set these rules. From 1 July 2025, Tatkal tickets booked on IRCTC's website and mobile app are available only to users authenticated with Aadhaar. From 15 July 2025, an Aadhaar-based OTP is mandatory for online Tatkal bookings. At reservation counters and with authorised agents, Tatkal bookings from 15 July 2025 need an OTP sent to the mobile number given at the time of booking.</p>
<p>Authorised agents cannot book opening-day Tatkal tickets in the first 30 minutes of the window: 10:00 to 10:30 for AC classes and 11:00 to 11:30 for non-AC classes. Read more in our guide to <a style="text-decoration:underline" href="/guides/aadhaar-train-ticket-booking-rules/">Aadhaar and train ticket booking</a>.</p>
<h2>If you cancel a Tatkal ticket</h2>
<p>IRCTC says confirmed Tatkal tickets are not refunded on cancellation. For waitlisted and contingent Tatkal tickets, cancellation charges apply under the existing railway rules.</p>
<h2>In short</h2>
<ul><li>Opens one day before the journey: 10:00 for AC, 11:00 for non-AC.</li><li>Online booking needs an Aadhaar-authenticated IRCTC account.</li><li>The Tatkal charge is 10% or 30% of the basic fare, within a minimum and maximum per class.</li><li>No concessions, and no refund on a confirmed ticket.</li></ul>
'''
write('guides/' + slug, page('guides/' + slug, t + ' | ClearBerth',
      'Tatkal opening times, charges per class, who can book and what happens on cancellation, from IRCTC and Ministry of Railways pages.',
      [('Guides', '/guides/'), ('Tatkal rules', '/guides/' + slug + '/')], t,
      'Tatkal is the railway\'s last-minute booking scheme. This guide sets out what IRCTC and the Ministry of Railways have published: when it opens, what it costs, who can book and what happens if you cancel.',
      body, True, [IRCTC_TATKAL_FAQ, PIB_TATKAL]))
GUIDES.append((slug, t, 'Opening times, charges per class, who can book, and cancellation.'))

# ---------------- 2. Aadhaar ----------------
slug = 'aadhaar-train-ticket-booking-rules'
t = 'Aadhaar and online train ticket booking: what the rules say'
body = '''
<h2>Tatkal tickets</h2>
<p>From 1 July 2025, Tatkal tickets booked through IRCTC's website and mobile app are available only to users authenticated with Aadhaar. From 15 July 2025, an Aadhaar-based OTP is mandatory for online Tatkal bookings. The Ministry of Railways announced both on 11 June 2025.</p>
<p>The same release covers counters and agents. From 15 July 2025, Tatkal bookings at reservation counters and through authorised agents need an OTP sent to the mobile number given at the time of booking. Authorised agents cannot book opening-day Tatkal tickets in the first 30 minutes: 10:00 to 10:30 for AC classes and 11:00 to 11:30 for non-AC classes.</p>
<h2>General reserved tickets</h2>
<p>A second release, dated 15 September 2025, extended the idea to general reserved tickets. From 1 October 2025, during the first 15 minutes after general reservation opens, tickets can be booked on IRCTC's website or app only by Aadhaar-authenticated users.</p>
<p>The release says booking timings at computerised reservation counters stay unchanged, and that the existing restriction on authorised agents stays: they cannot book opening-day reserved tickets in the first 10 minutes after general reservation opens. It does not state a clock time for the opening of general reservation.</p>
<h2>How to authenticate your IRCTC account</h2>
<p>IRCTC publishes a user guide titled "Authenticate IRCTC User Profile with Aadhaar". It is linked in the sources below. Do it before the day you plan to book, because the rules above apply from the first minute the window opens.</p>
<div class="note"><b>What this page does not cover.</b> We only describe changes that appear in official Ministry of Railways or IRCTC documents. If the railway announces a longer Aadhaar window or any other change later, this page will be updated with the new notice and its date.</div>
<h2>Related guides</h2>
<ul><li><a style="text-decoration:underline" href="/guides/tatkal-ticket-booking-rules/">Tatkal ticket booking: timings, charges and rules</a></li><li><a style="text-decoration:underline" href="/guides/advance-reservation-period-60-days/">How far ahead can you book a train ticket?</a></li></ul>
'''
write('guides/' + slug, page('guides/' + slug, t + ' | ClearBerth',
      'Which IRCTC bookings need Aadhaar authentication, from which dates, and the time windows for agents, from Ministry of Railways releases.',
      [('Guides', '/guides/'), ('Aadhaar and booking', '/guides/' + slug + '/')], t,
      'Two Ministry of Railways releases changed who can book tickets online in the first minutes after booking opens. Here is what each one says, with its date.',
      body, True, [PIB_TATKAL, PIB_GEN, ('IRCTC: User guide, Authenticate IRCTC User Profile with Aadhaar', 'https://contents.irctc.co.in/en/BookUpto12ticketsinamonthbylinkingAadhaar.pdf')]))
GUIDES.append((slug, t, 'Which bookings need Aadhaar, from which date, and the agent time limits.'))

# ---------------- 3. ARP ----------------
slug = 'advance-reservation-period-60-days'
t = 'How far ahead can you book a train ticket? The 60-day rule'
body = '''
<h2>The rule</h2>
<p>Indian Railways reduced the Advance Reservation Period (ARP) from 120 days to 60 days with effect from 1 November 2024. The Ministry of Railways release says the 60 days are counted excluding the date of the journey.</p>
<h2>What that means for your date</h2>
<p>Count back 60 days from your journey date to find the first day you can book. For a journey on 6 December, that day is 7 October. The release does not give a clock time at which booking opens each day, so check IRCTC's booking screen for the time.</p>
<h2>Tickets booked before the change</h2>
<p>Bookings made under the 120-day limit up to 31 October 2024 remain valid. Reservations made beyond the new 60-day limit can still be cancelled.</p>
<h2>Exceptions</h2>
<ul><li>Some daytime express trains, such as the Taj Express and the Gomti Express, keep shorter advance booking limits. The release does not state those limits, so check the train on IRCTC.</li><li>The 365-day advance period for foreign tourists did not change.</li></ul>
<h2>Why it matters on booking day</h2>
<p>Tatkal opens one day before the journey, and from October 2025 the first minutes of general reservation need an Aadhaar-authenticated account. See the guides on <a style="text-decoration:underline" href="/guides/tatkal-ticket-booking-rules/">Tatkal</a> and <a style="text-decoration:underline" href="/guides/aadhaar-train-ticket-booking-rules/">Aadhaar and booking</a>.</p>
'''
write('guides/' + slug, page('guides/' + slug, t + ' | ClearBerth',
      'Indian Railways advance reservation period is 60 days since 1 November 2024. How days are counted, what changed and the exceptions.',
      [('Guides', '/guides/'), ('60-day booking rule', '/guides/' + slug + '/')], t,
      'Train tickets can be booked up to 60 days ahead. This guide explains how the days are counted and which trains and passengers are exceptions.',
      body, True, [PIB_ARP]))
GUIDES.append((slug, t, 'How the 60 days are counted, and the exceptions.'))

# ---------------- 4. Refund / TDR ----------------
slug = 'train-cancelled-diverted-late-refund-tdr'
t = 'Train cancelled, diverted or late: refunds and how to file a TDR'
body = '''
<p>A TDR (ticket deposit receipt) is the request you file with IRCTC to claim a refund when you did not travel for a reason covered by the rules. This guide follows IRCTC's published refund rules, which are dated 12 November 2015 on IRCTC's site. Check IRCTC for any newer version.</p>
<h2>If the railway cancels your train</h2>
<p>For an e-ticket, IRCTC's rules say online cancellation or filing of a TDR is not required. The refund goes to the account you paid from. For a ticket bought at a counter, the rules say it can be cancelled at a computerised reservation counter up to 72 hours after the scheduled departure of the train.</p>
<h2>If your train is more than three hours late</h2>
<p>If the train runs more than three hours late from its starting station and you decide not to travel, no cancellation charge applies and the full fare is refunded. For an e-ticket the TDR must be filed online before the actual departure of the train. After the train has departed, the rules say no refund is admissible.</p>
<h2>If your train is diverted</h2>
<p>IRCTC lists three diversion reasons in the TDR form: "Train Diverted And Passenger Not Travelled", "Train Diverted And Train Not Touching Boarding Station" and "Train Diverted And Train Not Touching Destination Station". For the two "not touching" reasons, the TDR can be filed up to 72 hours after the scheduled departure of the train from your boarding station.</p>
<h2>Other TDR reasons and their time limits</h2>
<ul>
<li><b>Train terminated short of destination:</b> up to 72 hours after the scheduled arrival at your destination. The original certificate from the ticket checking staff is sent to IRCTC by post.</li>
<li><b>AC failure:</b> within 20 hours of the actual arrival at your destination, with the original certificate posted to IRCTC.</li>
<li><b>Travelled in a lower class than booked:</b> for an e-ticket, the fare difference is refunded automatically when a lower class is given at the first chart. After the first chart, the TDR must be filed within two days of the date the certificate is issued.</li>
<li><b>Missed a connecting train because the first train ran late:</b> within 3 hours of the actual arrival of the train you travelled by.</li>
</ul>
<h2>If the IRCTC site will not accept your TDR</h2>
<p>IRCTC's notice says to send an email from your registered email ID to etickets@irctc.co.in. Include your PNR and the reason.</p>
<div class="note"><b>Good to know.</b> Some of these cases need a certificate from the ticket checking staff, sent to IRCTC by post. The refund is processed only after IRCTC receives it.</div>
<p>Also see <a style="text-decoration:underline" href="/guides/waitlisted-e-ticket-after-chart/">what happens to a waitlisted e-ticket after the chart</a>.</p>
'''
write('guides/' + slug, page('guides/' + slug, t + ' | ClearBerth',
      'Refund rules for cancelled, diverted and late trains, the TDR reasons and their time limits, from IRCTC\'s published refund rules.',
      [('Guides', '/guides/'), ('Refunds and TDR', '/guides/' + slug + '/')], t,
      'What to do when the railway cancels, diverts or delays your train: when a refund is automatic, which TDR reason to choose and how long you have.',
      body, True, [IRCTC_REFUND, IRCTC_DIVERSION]))
GUIDES.append((slug, t, 'When a refund is automatic, the TDR reasons, and the time limits.'))

# ---------------- 5. Waitlisted e-ticket ----------------
slug = 'waitlisted-e-ticket-after-chart'
t = 'Waitlisted e-ticket after the chart: can you travel?'
body = '''
<h2>If every passenger is still waitlisted</h2>
<p>IRCTC's scheme for waitlisted e-tickets says that after the chart is prepared, passengers who are still on the waiting list are dropped from the charts, and IRCTC cancels the booking. They are not allowed to board the train. A person found on the train with such a ticket is treated as travelling without a ticket.</p>
<p>The refund is arranged from the railway by IRCTC and credited to your account electronically. IRCTC's refund rules say the amount is credited after deducting clerkage.</p>
<h2>If you are confirmed or in RAC</h2>
<p>Passengers with confirmed or RAC status keep their names on the chart and can undertake the journey.</p>
<h2>If only some passengers are confirmed</h2>
<p>On a partially confirmed ticket, the names of all passengers, including the waitlisted ones, remain on the chart. If the waitlisted passengers do not travel, IRCTC lists TDR reasons for this, for example "Party Partially Confirmed/Waitlisted And Waitlisted Passengers Did Not Travel". A certificate from the ticket checking staff is needed, and the TDR is filed up to 72 hours after the actual arrival of the train at the destination.</p>
<p>If a confirmed berth is given to a RAC or waitlisted passenger up to the final chart, the ticket is treated as a reserved ticket.</p>
<h2>Cancelling before the chart</h2>
<p>IRCTC says an e-ticket can be cancelled online only until the chart of the train is prepared. After that, use the TDR route described in our guide to <a style="text-decoration:underline" href="/guides/train-cancelled-diverted-late-refund-tdr/">refunds and TDR</a>.</p>
<h2>When is the chart prepared?</h2>
<p>The IRCTC pages we read do not state a time. They refer only to "chart preparation". Check the status of your PNR in ClearBerth or on IRCTC after the chart is made.</p>
'''
write('guides/' + slug, page('guides/' + slug, t + ' | ClearBerth',
      'What IRCTC does with a fully waitlisted e-ticket after the chart is prepared, who can still travel, and how refunds work.',
      [('Guides', '/guides/'), ('Waitlisted e-ticket', '/guides/' + slug + '/')], t,
      'If your e-ticket is still on the waiting list when the chart is prepared, IRCTC cancels it. Here is what the rules say about boarding, refunds and partly confirmed tickets.',
      body, True, [IRCTC_WL, IRCTC_REFUND]))
GUIDES.append((slug, t, 'What happens to a waitlisted e-ticket once the chart is made.'))

# ---------------- 6. Lower berth / ladies ----------------
slug = 'lower-berth-and-ladies-quota-rules'
t = 'Lower berths for senior citizens and women, and the Ladies quota'
body = '''
<h2>Automatic lower berth allotment</h2>
<p>In a written reply in the Rajya Sabha, summarised in a Ministry of Railways release dated 5 December 2025, the Minister said lower berths are allotted automatically to senior citizens and female passengers aged 45 and above, even if no choice is given, subject to availability. The release does not give an age for senior citizens.</p>
<p>The release adds that lower berths that fall vacant are given on priority to senior citizens, persons with disabilities or pregnant women who were assigned middle or upper berths.</p>
<h2>How many lower berths are kept aside?</h2>
<p>A Ministry of Railways release dated 17 December 2021 describes a combined quota for senior citizens, women aged 45 and above and pregnant women: six to seven lower berths per coach in Sleeper, four to five per coach in 3AC and three to four per coach in 2AC, depending on the number of coaches of that class in the train.</p>
<h2>Berths for women travelling alone or in groups</h2>
<p>The same 2021 release says six berths are earmarked for women travelling alone or in groups in sleeper class on long-distance Mail and Express trains, and six berths in 3AC on Garib Rath, Rajdhani, Duronto and fully air-conditioned Express trains. Age does not matter for this quota.</p>
<h2>Ladies quota when you book</h2>
<p>IRCTC's reservation rules describe it this way: a lady passenger travelling alone, or with children under 12, who wants to reserve in the Ladies quota gets accommodation from that quota if it is available. If not, accommodation comes from the general quota. IRCTC says the Ladies quota is generally earmarked in Sleeper class and Second Sitting (2S). IRCTC's Tatkal FAQ adds that Ladies quota cannot be selected together with Tatkal.</p>
<h2>Help on the train</h2>
<p>The 2021 release says the Railway Help Line 139 is operational 24 hours a day for security assistance to passengers in distress.</p>
<div class="note"><b>Numbers can change.</b> The berth counts above are from 2021, and the 2025 release does not restate them. Check IRCTC or ask at a reservation counter if the exact number matters for your trip.</div>
'''
write('guides/' + slug, page('guides/' + slug, t + ' | ClearBerth',
      'Automatic lower berth allotment, the combined quota per coach, berths for women travelling alone and Ladies quota rules, from railway releases.',
      [('Guides', '/guides/'), ('Lower berth and Ladies quota', '/guides/' + slug + '/')], t,
      'Which passengers get lower berths without asking, how many berths are kept aside, and how the Ladies quota works when you book.',
      body, True, [PIB_BERTH25, PIB_WOMEN21, IRCTC_RULES, IRCTC_TATKAL_FAQ]))
GUIDES.append((slug, t, 'Automatic lower berths, the quotas, and how Ladies quota works.'))

# ---------------- Guides hub ----------------
cards = ''.join('<a href="/guides/%s/"><b>%s</b><span>%s</span></a>' % (s, e(tt), e(sh)) for s, tt, sh in GUIDES)
hub_body = '<div class="cards">' + cards + '</div><div class="note">Every guide names the official page it comes from, with its date. When a rule changes, we update the guide and the "last checked" date at the top. Spotted a mistake? <a style="text-decoration:underline" href="/contact/">Tell us</a>.</div>'
write('guides', page('guides', 'Indian Railways rules explained: guides for train travellers | ClearBerth',
      'Plain-language guides to Tatkal, Aadhaar booking, refunds and TDR, waitlisted e-tickets and lower berths, each linked to IRCTC or Ministry of Railways pages.',
      [('Guides', '/guides/')], 'Guides for Indian train travellers',
      'Plain-language explanations of railway booking and refund rules. Each guide links to the IRCTC or Ministry of Railways page it is based on.',
      hub_body, False))

# ---------------- About ----------------
about = '''
<h2>Our vision</h2>
<p>Every train traveller actively uses ClearBerth every day.</p>
<h2>Our mission</h2>
<p>To keep improving ClearBerth based on the feedback we receive from the people who use it. Tell us what works and what does not on the <a style="text-decoration:underline" href="/contact/">contact page</a>.</p>
<h2>What ClearBerth is</h2>
<p>ClearBerth is an app for Indian Railways travellers. It shows your PNR status with a diagram of your coach and berth, tracks your train live and tells you how late it is, and sends alerts when your waitlist moves or your train nears your station. It also has pages for trains, stations and routes on this website.</p>
<h2>Independent of the railway</h2>
<p>ClearBerth is not IRCTC and not part of Indian Railways. You book and cancel tickets on IRCTC. ClearBerth helps you find trains and seats, and then takes you to IRCTC to book.</p>
<h2>Where the information comes from</h2>
<ul>
<li><b>Trains, stations and routes:</b> the pages on this site show scheduled timings. Trains often run late, so use live tracking in the app on the day.</li>
<li><b>Live running status and PNR status:</b> live times are estimates, so confirm with the railway enquiry service before you leave for the station.</li>
<li><b>Rules and guides:</b> taken from IRCTC and Ministry of Railways pages, with the source and date shown on each <a style="text-decoration:underline" href="/guides/">guide</a>.</li>
</ul>
<h2>Corrections</h2>
<p>If something on ClearBerth is wrong, email <a style="text-decoration:underline" href="mailto:clearberth.support@gmail.com?subject=ClearBerth%20correction">clearberth.support@gmail.com</a> or see the <a style="text-decoration:underline" href="/contact/">contact page</a>. Corrections to the guides are dated.</p>
<h2>Who is behind ClearBerth</h2>
<p>ClearBerth is built and run by its co-founders, Neha Haflongbar and Aditya Bhattacharya. We travel by Indian Railways ourselves, and that is why the app focuses on the questions we kept asking: will my waitlist clear, which berth is mine, and where is my train right now.</p>
<figure style="margin:18px 0"><img src="/shots/founders.jpg" alt="Neha Haflongbar and Aditya Bhattacharya, the co-founders of ClearBerth" width="1200" height="900" loading="lazy" style="width:100%;height:auto;border-radius:16px;display:block"><figcaption style="font-size:14px;color:#7A819E;margin-top:8px">Neha Haflongbar and Aditya Bhattacharya, co-founders of ClearBerth.</figcaption></figure>
'''
write('about', page('about', 'About ClearBerth: an independent app for Indian Railways travellers',
      'ClearBerth shows PNR status with a berth diagram, tracks trains live and alerts you when your waitlist moves. Independent of IRCTC and Indian Railways.',
      [('About', '/about/')], 'About ClearBerth',
      'ClearBerth is built by a regular train traveller, for train travellers.', about, False))

# ---------------- Contact ----------------
contact = '''
<h2>Email</h2>
<p><a style="text-decoration:underline" href="mailto:clearberth.support@gmail.com?subject=ClearBerth%20support">clearberth.support@gmail.com</a></p>
<p>For app problems, say which phone and app version you use and what you saw on screen. Please do not email passwords or payment details.</p>
<h2>On X</h2>
<p><a style="text-decoration:underline" href="https://x.com/ClearBerthApp" rel="noopener">@ClearBerthApp on X</a>. Message or reply to us there with feedback, or to ask for a new question or an updated answer in the app's FAQ.</p>
<h2>What ClearBerth cannot do</h2>
<p>ClearBerth does not book, cancel or refund tickets. Those are handled by IRCTC. For a refund, a TDR or a problem with a booking, use <a style="text-decoration:underline" href="/guides/train-cancelled-diverted-late-refund-tdr/">our refund guide</a> and IRCTC's own support. IRCTC's Tatkal FAQ gives care@irctc.co.in as its support email.</p>
<h2>Help on a journey</h2>
<p>The Railway Help Line 139 is operational 24 hours a day for security assistance to passengers in distress, according to a Ministry of Railways release.</p>
<h2>Corrections to our guides</h2>
<p>If a guide is out of date or wrong, email us with the page and the official notice that says otherwise. We will update the page and its "last checked" date.</p>
'''
write('contact', page('contact', 'Contact ClearBerth | support email and help',
      'Email ClearBerth support, report a correction, and find out what ClearBerth can and cannot help with.',
      [('Contact', '/contact/')], 'Contact ClearBerth',
      'Questions about the app, a correction to a guide, or feedback: here is how to reach us.', contact, False))

# ---------------- Sitemap ----------------
sm = open('sitemap.xml', encoding='utf-8').read()
new_urls = ['about/', 'contact/', 'guides/'] + ['guides/%s/' % s for s, _, _ in GUIDES]
add = ''
for u in new_urls:
    loc = 'https://clearberth.app/' + u
    if loc not in sm:
        add += '  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (loc, DATE)
if add:
    sm = sm.replace('</urlset>', add + '</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('pages written:', len(new_urls), '| sitemap entries added:', add.count('<url>'))
