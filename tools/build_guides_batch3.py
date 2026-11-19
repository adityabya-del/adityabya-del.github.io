#!/usr/bin/env python3
"""17 more guides (19 Nov 2026), same layout as the other /guides/ pages, so there are 25 in all.
Facts come only from the IRCTC, Indian Railways, Railway Board and PIB (Ministry of Railways) pages cited
on each guide. Links them from /guides/ and the sitemap. Safe to run again.
Run from the repo root: python3 tools/build_guides_batch3.py
Then refresh the guide link blocks: python3 tools/add_internal_links.py --write --refresh-guides"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = open(os.path.join(ROOT, 'guides/tatkal-ticket-booking-rules/index.html'), encoding='utf-8').read()
HEAD = TPL[:TPL.index('</head>') + 7]
TAIL = TPL[TPL.index('<h2>Check your ticket in the app</h2>'):]
TAIL = re.sub(r'<h2 id="il-guides">.*?</div>\n', '', TAIL, flags=re.S)   # refreshed by add_internal_links.py
CHECKED = '19 November 2026'
TODAY = '2026-11-19'
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
    h = re.sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="https://clearberth.app/shots/og.png">', h)
    if '.tt.wr' not in h:
        h = h.replace('</style>', '.tt.wr th,.tt.wr td{white-space:normal;vertical-align:top}</style>', 1)
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
           '<p class="meta">Last checked: %s. Railway rules change, so confirm on IRCTC before you book or travel.</p>\n') % (
        E(short), E(h1), E(lead), CHECKED)
    out = h + top + body.replace('@@A@@', A) + '\n' + src + TAIL
    d = os.path.join(ROOT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


def ul(*x):
    return '<ul>' + ''.join('<li>%s</li>' % i for i in x) + '</ul>'


def table(head, rows):
    return ('<div class="tt wr"><table><thead><tr>' + ''.join('<th>%s</th>' % c for c in head) + '</tr></thead><tbody>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')


def link(path, text):
    return '<a @@A@@ href="%s">%s</a>' % (path, text)


R = '&#8377;'

# ---------------- sources ----------------
S_TC = ("IRCTC: Terms and Conditions", "https://contents.irctc.co.in/en/Terms%20and%20conditions.pdf")
S_FAQ = ("IRCTC: E-ticket FAQ", "https://contents.irctc.co.in/en/etktfaq.html")
S_AMEND = ("IRCTC: Amendment in e-ticket scheme (name and boarding station change)", "https://contents.irctc.co.in/en/Eticket_new_cancel.html")
S_ID21 = ("Railway Board circular, 16 November 2021: carrying proof of identity during journey", "https://contents.irctc.co.in/en/RailwayBoardCircularOnProofOfIdentity_16112021.pdf")
S_FT = ("IRCTC: Foreign Tourist quota terms and conditions", "https://contents.irctc.co.in/en/FtTermCondition.pdf")
S_FTB = ("IRCTC: Foreign Tourist quota booking", "https://contents.irctc.co.in/en/ForeignTouristQuotaBooking.pdf")
S_PIB_FT = ("PIB, 15 December 2017: easing of train travel for foreign nationals and NRIs", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=1512779")
S_SR_BPC = ("Southern Railway press release, 2 April 2026: change of boarding point up to the second reservation chart", "https://sr.indianrailways.gov.in/view_detail.jsp?lang=0&dcd=19594&id=0%2C4%2C268")
S_BPC = ("IRCTC: Online change of boarding point", "https://contents.irctc.co.in/en/boardingPointChange.html")
S_BPC2 = ("IRCTC: Guidelines for changing the boarding station", "https://contents.irctc.co.in/en/BoardingPointChangeEnglish.pdf")
S_BPC3 = ("IRCTC: Change of boarding point on e-ticket (steps)", "https://contents.irctc.co.in/en/changeBoardingPointOnEticket.pdf")
S_CTR = ("IRCTC: Counter ticket cancellation and boarding point change", "https://www.operations.irctc.co.in/ctcan/SystemTktCanLogin.jsf")
S_CUR = ("IRCTC: Current booking guidelines", "https://contents.irctc.co.in/en/Current_Booking.pdf")
S_TATB = ("IRCTC: Tatkal booking (rules page)", "https://www.services.irctc.co.in/beta_htmls/tatkal.html")
S_TATF = ("IRCTC: Tatkal FAQ", "https://contents.irctc.co.in/en/TatkalFaq.html")
S_PIB_CHILD = ("PIB, 31 March 2016: revised child fare rule from 21 April 2016", "https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=138458")
S_IRCTC_TR = ("IRCTC: Salient features of IRCTC trains", "https://contents.irctc.co.in/en/IRCTC_Train_Salient_Features.pdf")
S_LUG = ("Indian Railways: Rules for luggage", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=luggage_Rule.html")
S_INS = ("IRCTC: Optional travel insurance for e-ticket passengers", "https://contents.irctc.co.in/en/InsuranceTermCondition.pdf")
S_QUOTA = ("Indian Railways: Quota codes", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=quota_Code.html")
S_REF = ("Indian Railways: Revised refund rules from 12.11.2015", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=refund_Rules.html")
S_CAN = ("IRCTC: E-ticket cancellation", "https://contents.irctc.co.in/en/eticketCancel.html")
S_PIB_RAC = ("PIB, 11 November 2009: bedrolls for RAC passengers in AC classes", "https://www.pib.gov.in/newsite/erelcontent.aspx?relid=54001")
S_RB_BED = ("Railway Board, Environment & Housekeeping circulars (18.12.2023: complete bedroll kit to RAC passengers)", "https://indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,1,304,366,1539,2855")
S_PIB_2026 = ("PIB, 11 March 2026: Lok Sabha reply on fares, concessions and lower berths", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238430")
S_PIB_SR20 = ("PIB, 19 March 2020: withdrawal of senior citizen concessions", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=1607179")
S_PIB_SR16 = ("PIB, 2 December 2016: concessions to railway passengers in various categories", "https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=154835")
S_PIB_LB25 = ("PIB, 19 March 2025: lower berths for senior citizens, women and persons with disabilities", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2112957")
S_PIB_DIV = ("PIB, 3 December 2019: facilities for Divyangjan passengers", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=1594758")
S_DIVF = ("IRCTC: Facilities for persons with disability on IRCTC", "https://contents.irctc.co.in/en/Facilities_for_Divyaang_Users_English.pdf")
S_SR_DIV = ("Southern Railway press release: online Divyangjan ID card application", "https://sr.indianrailways.gov.in/view_detail.jsp?lang=0&id=0,4,268&dcd=17088&did=17327858974165693C1AA3C62161A537E7AC53FCF05CB")
S_PIB_RM = ("PIB, 25 March 2026: RailMadad grievance redressal across helpline 139, web, app and SMS", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2245210")
S_PIB_112 = ("PIB: Railways and GRP on safety of women passengers (139 integrated with 112)", "https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2078095")
S_CAT = ("Indian Railways: Catering charges", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=CateringCharge.html")
S_PIB_LIM = ("PIB, 6 June 2022: limit of online booking raised to 12 and 24 tickets a month", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=1831478")
S_AAD24 = ("IRCTC: Book up to 24 tickets in a month by linking Aadhaar", "https://contents.irctc.co.in/en/BookUpto12tickets.pdf")

G = []   # (path, title, desc, short, h1, lead, blurb, body, sources)

# 1 ---------------- ID proof
G.append(('/guides/id-proof-for-train-travel/',
  'Valid ID proof for train travel on an IRCTC e-ticket',
  'The identity cards IRCTC accepts on an e-ticket journey, DigiLocker and m-Aadhaar, what happens with no ID, and the rule for foreign passengers.',
  'ID proof for travel', 'Valid ID proof for train travel on an IRCTC e-ticket',
  'You do not type any ID details when you book an e-ticket, but one passenger on the ticket must show an original ID during the journey. This guide lists what IRCTC accepts.',
  'The IDs IRCTC accepts, DigiLocker, and what happens without one.', '''
<h2>Do you need an ID to book?</h2>
<p>No. IRCTC says the user does not have to enter the photo identity card details of any passenger while booking an e-ticket. Instead, one of the passengers on the ticket has to carry one of the listed identity cards in original and show it during the journey.</p>
<h2>The IDs IRCTC accepts</h2>
<p>IRCTC's Terms and Conditions list these as authorised IDs for travel on an e-ticket:</p>
''' + ul('Passport', 'Voter photo identity card issued by the Election Commission of India',
         'Driving licence issued by an RTO', 'PAN card issued by the Income Tax Department',
         'Photo identity card with a serial number issued by the Central or State Government',
         'Student identity card with photograph issued by a recognised school or college',
         'Nationalised bank passbook with photograph', 'Credit card issued by a bank with a laminated photograph',
         'Printed Aadhaar card or downloaded Aadhaar (e-Aadhaar)',
         'm-Aadhaar, shown in the m-Aadhaar app on the passenger\'s phone after entering the password',
         'Photo identity card with a serial number issued by a Central or State public sector undertaking, a District Administration, a municipal body or a Panchayat Administration',
         'Aadhaar or driving licence shown from the "Issued Documents" section of the passenger\'s DigiLocker account') + '''
<h2>DigiLocker: issued, not uploaded</h2>
<p>IRCTC accepts an Aadhaar or driving licence shown from the <b>Issued Documents</b> section after logging into DigiLocker. A document the user uploaded themselves, in the <b>Uploaded Documents</b> section, is not accepted as proof of identity.</p>
<h2>One ID covers the whole ticket</h2>
<p>The ID of any one passenger booked on the ticket is enough. A Railway Board circular of 16 November 2021 repeats the rule: in a reserved class, one passenger on the ticket has to produce one of the prescribed IDs in original, failing which all the passengers on that ticket are treated as travelling without a ticket.</p>
<h2>Concession and quota passengers need proof too</h2>
<p>The same circular says anyone travelling on a concession, or on a quota kept for a particular group, must carry valid proof that they qualify. Its examples are the concession certificate for Divyangjan passengers, a doctor's certificate for pregnant women booked on the quota kept for them, and age proof for senior citizens booked on the senior citizen quota.</p>
<h2>Foreign passengers</h2>
<p>For passengers who are not Indian, IRCTC says their own country's passport is the only accepted ID. On a Foreign Tourist quota ticket, the original passport and a valid visa must be shown; IRCTC says a passenger who cannot show them is treated as travelling without a ticket and charged a penalty of three times the fare. See our ''' + link('/guides/foreign-tourist-quota-irctc/', 'Foreign Tourist quota guide') + '''.</p>
<h2>ID but no ticket on your phone?</h2>
<p>If you cannot show the e-ticket (for example, the phone is lost or its battery is dead) but you do have the original ID, IRCTC says a penalty under Railway rules is charged and the ticket checking staff issue an Excess Fare Ticket. More in our guide on ''' + link('/guides/e-ticket-on-phone-sms-printout/', 'showing an e-ticket on your phone') + '''.</p>
<h2>In short</h2>
''' + ul('No ID is entered at booking, but one passenger on the ticket must show an original ID on the train.',
         'DigiLocker counts only from "Issued Documents".', 'Without any accepted ID, everyone on the ticket is treated as ticketless.'),
  [S_TC, S_FAQ, S_ID21, S_FT]))

# 2 ---------------- boarding station
G.append(('/guides/change-boarding-station-irctc/',
  'How to change the boarding station on a train ticket',
  'Since 1 April 2026 the boarding station can be changed until the second reservation chart. The steps on IRCTC, the limits and the refund rule.',
  'Change boarding station', 'How to change the boarding station on a train ticket',
  'If you will board at a different station on the train\'s route, you can change the boarding station on your ticket. Here is the current rule, how to do it and what you give up.',
  'The 2026 rule, the IRCTC steps and what you lose at the old station.', '''
<h2>The rule since 1 April 2026</h2>
<p>A Southern Railway press release dated 2 April 2026 says that from 1 April 2026 passengers can change their boarding station up to the preparation of the second (final) reservation chart. It says the change can be made at PRS counters and on IRCTC.</p>
<div class="note">IRCTC's own boarding-point pages, checked on 19 November 2026, still describe the older limit of 24 hours before the train's scheduled departure. The press release above is the newer rule.</div>
<h2>How to change it on IRCTC</h2>
<p>IRCTC's steps: log in to IRCTC, open <b>Booked Ticket History</b>, select the PNR and choose the new boarding station.</p>
<h2>Counter tickets</h2>
<p>IRCTC also lets you change the boarding point of a ticket bought at a reservation counter: on its counter-ticket page you choose "Boarding Point Change", enter the PNR and train number, and confirm with an OTP sent to the mobile number given at the time of booking. IRCTC says this may be possible only if a valid mobile number was given when the ticket was booked.</p>
<h2>Rules that still apply</h2>
''' + ul('Once you change the boarding station, you lose the right to board from the original station. IRCTC says a passenger found travelling without authority between the original and the new station pays the fare with a penalty for that stretch.',
         'IRCTC allows the change only once. If the boarding station was already changed at the time of booking, it can be changed one more time from Booked Ticket History.',
         'It is not allowed if the ticket has been seized.',
         'It is not allowed on a PNR with the VIKALP option.',
         'It is not allowed on a ticket booked under ' + link('/guides/current-booking-after-chart/', 'current booking') + '.',
         'The online change is not allowed for an I-ticket.',
         'On a Foreign Tourist quota ticket, it is allowed only after a berth has been allotted.') + '''
<h2>Refund after a change</h2>
<p>IRCTC says that if the boarding station is changed within 24 hours of the train's departure, no refund is allowed in normal circumstances. In exceptional cases, such as the train being cancelled, the coach not being attached or the train running more than three hours late, the normal refund rules apply.</p>
<h2>In short</h2>
''' + ul('Since 1 April 2026: change it up to the second chart, on IRCTC or at a counter.',
         'Online: Booked Ticket History, select the PNR, pick the new station.',
         'You cannot then board at the original station.'),
  [S_SR_BPC, S_BPC, S_BPC2, S_BPC3, S_CTR, S_FT]))

# 3 ---------------- transfer / name change
G.append(('/guides/transfer-train-ticket-change-name/',
  'Can you transfer a train ticket or change the passenger name?',
  "When a confirmed ticket can be moved to a family member, the documents needed, and why an e-ticket's date or train cannot be changed.",
  'Transfer a ticket', 'Can you transfer a train ticket or change the passenger name?',
  'A reserved train ticket is not transferable as a rule, but Railway rules allow a name change in a few cases. This guide sets out who qualifies and how.',
  'Who can take over a confirmed ticket, and what cannot be changed.', '''
<h2>The basic rule</h2>
<p>IRCTC says accommodation booked on an e-ticket is not transferable. It is valid only if one of the passengers booked on it shows one of the accepted ID cards in original during the journey (see our ''' + link('/guides/id-proof-for-train-travel/', 'ID proof guide') + ''').</p>
<h2>When the name can be changed</h2>
<p>IRCTC lists two cases, for a passenger holding a confirmed e-reservation:</p>
''' + ul('<b>To a family member.</b> The passenger makes a written request at the nearest Railway Reservation Office at least 24 hours before the train\'s scheduled departure. The ticket can go to a father, mother, brother, sister, son, daughter, husband or wife.',
         '<b>Government servants on duty.</b> The appropriate authority makes the written request at least 24 hours before the scheduled departure.') + '''
<p>IRCTC says such a request is granted once only.</p>
<h2>What to take to the counter</h2>
''' + ul("The printout of the Electronic Reservation Slip (ERS)", "Original photo identity proof of one of the passengers on the ticket", "Proof of the blood relation with the person who will travel") + '''
<p>The name change is done at a reservation office, not online.</p>
<h2>Tickets where the name cannot be changed</h2>
''' + ul('A ticket booked under current booking: IRCTC does not allow any name, age or gender change.',
         'A Foreign Tourist quota ticket: IRCTC says no change of name is allowed under any circumstances.',
         'A Tatkal ticket: IRCTC\'s Tatkal page says modification of a Tatkal ticket in any form is not permitted.') + '''
<h2>Changing the date or train</h2>
<p>IRCTC says changing the journey date or train of an e-ticket is not available. Its FAQ says to cancel the original ticket online and book a fresh one. Cancellation charges apply; see our ''' + link('/guides/cancel-irctc-e-ticket/', 'cancellation guide') + '''.</p>
<h2>In short</h2>
''' + ul('Not transferable, except to listed family members or for government servants on duty.',
         'Written request at a reservation office, at least 24 hours before departure, once only.',
         'For a new date or train: cancel and rebook.'),
  [S_AMEND, S_FAQ, S_TC, S_CUR, S_FT, S_TATB]))

# 4 ---------------- children
G.append(('/guides/child-train-ticket-rules/',
  'Train tickets for children: fares and age rules',
  'Children under 5 travel free, 5 to 11 pay half or full fare depending on whether you take a berth. The rules, plus luggage and insurance for children.',
  'Children\'s tickets', 'Train tickets for children: fares and age rules',
  'What a child pays on Indian Railways depends on age and on whether you book a separate berth or seat. Here are the rules as the Ministry of Railways and IRCTC publish them.',
  'Free under 5; half or full fare from 5 to 11.', '''
<h2>The fare rule</h2>
<p>The Ministry of Railways revised the child fare rule for journeys from 21 April 2016 (PIB release, 31 March 2016):</p>
''' + table(['Child\'s age', 'Reserved class', 'Unreserved'],
            [['Under 5', 'Free, without a berth or seat', 'Free'],
             ['5 to under 12, with a separate berth or seat', 'Full adult fare', '&ndash;'],
             ['5 to under 12, without a separate berth or seat', 'Half the adult fare, subject to the minimum distance for charging', 'Half the adult fare, subject to the minimum distance for charging']]) + '''
<p style="margin-top:10px">So for a child aged 5 to 11 you choose at booking: a berth at the full fare, or no berth at half fare.</p>
<h2>Proof of age</h2>
<p>A Railway Board circular of 16 November 2021 notes that doubts arise about the age of children up to 12, and says that any passenger availing a concession must produce valid proof to establish the claim.</p>
<h2>IRCTC's own trains</h2>
<p>On the trains IRCTC runs itself (the Tejas trains), IRCTC says there are no concession tickets. Children below 5 travel free and are booked with their parents, and their names do not appear on the chart. Children of 5 and above pay the full fare and get a seat.</p>
<h2>Luggage for children</h2>
<p>Indian Railways' luggage rules give children aged 5 and below 12 half of the free luggage allowance, up to a maximum of 50 kg. See our ''' + link('/guides/train-luggage-allowance-rules/', 'luggage guide') + ''' for the allowance by class.</p>
<h2>Travel insurance for children</h2>
<p>IRCTC's optional travel insurance does not cover children below 5 booked without a berth or seat. It does cover children aged 5 to 11, with or without a berth. More in our ''' + link('/guides/irctc-travel-insurance/', 'travel insurance guide') + '''.</p>
<h2>Foreign Tourist quota</h2>
<p>On a Foreign Tourist quota ticket, IRCTC says a child without a berth pays half the adult base fare, which on that quota is 1.5 times the normal base fare.</p>
<h2>In short</h2>
''' + ul('Under 5: free, no berth.', '5 to 11: full fare with a berth, half fare without one.', 'Half luggage allowance (up to 50 kg) from 5 to below 12.'),
  [S_PIB_CHILD, S_ID21, S_IRCTC_TR, S_LUG, S_INS, S_FT]))

# 5 ---------------- luggage
G.append(('/guides/train-luggage-allowance-rules/',
  'Train luggage allowance by class: how much you can carry free',
  'The free luggage allowance in each class, the maximum you can carry in the coach, charges for extra weight, and the size limit for suitcases.',
  'Luggage allowance', 'Train luggage allowance by class: how much you can carry free',
  'Every passenger can carry some luggage in the coach for free. The amount depends on the class. This guide sets out the limits from Indian Railways\' luggage rules.',
  'Free allowance per class, maximum weight and suitcase size.', '''
<h2>Allowance by class</h2>
<p>Indian Railways' luggage rules give each passenger a free allowance, a small marginal allowance on top, and a maximum that can be carried in the compartment (the maximum includes the free allowance):</p>
''' + table(['Class', 'Free allowance', 'Marginal allowance', 'Maximum in the coach'],
            [['AC First Class', '70 kg', '15 kg', '150 kg'],
             ['AC 2-tier / First Class', '50 kg', '10 kg', '100 kg'],
             ['AC 3-tier / AC Chair Car', '40 kg', '10 kg', '40 kg'],
             ['Sleeper', '40 kg', '10 kg', '80 kg'],
             ['Second Class', '35 kg', '10 kg', '70 kg']]) + '''
<p style="margin-top:10px">Children aged 5 and below 12 get half the free allowance, up to 50 kg.</p>
<h2>Carrying more than the free allowance</h2>
''' + ul('You can carry excess luggage in the compartment up to the maximum for your class if you book it at the luggage office and pay 1.5 times the luggage rate. The rules ask you to get your ticket endorsed with the luggage ticket details before the journey.',
         'Luggage beyond the maximum can be booked in advance and carried in the brake van.',
         'Luggage that must go on the same train as you should be presented at the luggage office of the booking station at least 30 minutes before departure.',
         'The minimum charge for luggage is ' + R + '30.') + '''
<h2>If extra luggage is found unbooked</h2>
''' + ul('Above the free allowance but within the marginal allowance: charged at 1.5 times the luggage rate.',
         'Above the marginal allowance, or above the maximum: the weight above the free allowance is charged at six times the luggage rate, with a minimum of ' + R + '50.') + '''
<h2>Suitcase size</h2>
<p>Trunks, suitcases and boxes up to 100 cm &times; 60 cm &times; 25 cm (length &times; breadth &times; height) may be carried in the compartment. Anything larger in any one dimension has to be booked and carried in the brake van. In AC 3-tier and AC Chair Car, the maximum suitcase size is 55 cm &times; 45 cm &times; 22.5 cm.</p>
<h2>What cannot be carried</h2>
<p>The rules say offensive, explosive, dangerous and inflammable articles, empty gas cylinders, dead poultry and game, acids and other corrosive substances are not accepted as luggage. Merchandise is not allowed as personal luggage in the compartment. Scooters, cycles and similar articles get no free allowance.</p>
<h2>Medical oxygen</h2>
<p>An oxygen cylinder with its stand, for a patient travelling under a medical certificate, may be carried in all classes, and the free allowance applies to it.</p>
<div class="note">The Indian Railways luggage page shows no date, so the date these limits took effect cannot be confirmed from it.</div>
<h2>In short</h2>
''' + ul('Free: 70 kg (1A), 50 kg (2A), 40 kg (3A, CC, SL), 35 kg (second class).', 'Book extra weight at the luggage office; unbooked excess can cost six times the rate.', 'Suitcases up to 100 &times; 60 &times; 25 cm in the coach; 55 &times; 45 &times; 22.5 cm in 3A and CC.'),
  [S_LUG]))

# 6 ---------------- dogs
G.append(('/guides/travel-with-dog-on-train/',
  'Taking a dog on an Indian train: the rules',
  'Where a dog can travel on a train, the charges, the classes where dogs are not allowed, and what happens if a dog is found unbooked.',
  'Travelling with a dog', 'Taking a dog on an Indian train: the rules',
  'A dog can travel by train in the brake van, or with you in a few first-class compartments. Here are the rules from Indian Railways\' published luggage rules.',
  'Where a dog can travel, the charges and the classes it cannot enter.', '''
<h2>Where a dog can travel</h2>
''' + ul('<b>In the brake van</b>, in the dog box.',
         '<b>With you in AC First Class or First Class</b>, only with the agreement of your fellow passengers. If they later object, the dog is moved to the guard\'s van and no refund is given.',
         '<b>A lady travelling alone with children under 12 in a First Class compartment</b> may take one dog with her at the dog-box rate (minimum ' + R + '10). If another lady enters the compartment, the dog may stay only with her consent.',
         '<b>Large dogs</b> that do not fit the dog box are carried in a special vehicle at the same rates and conditions as horses.') + '''
<h2>Where a dog is not allowed</h2>
<p>Dogs are not allowed in AC sleeper coaches, AC chair car coaches, sleeper class or second class. A dog found there is moved to the brake van at once and charged at six times the luggage scale rate, with a minimum of ''' + R + '''50.</p>
<h2>Charges</h2>
<p>Dogs are charged at luggage rates (Scale L) on these weights: 30 kg when carried in the brake van dog box and 60 kg when carried in a passenger compartment. The minimum charge is ''' + R + '''10 per dog and the charge is paid in advance. A "Seeing Eye" dog travelling with a blind person in a First Class compartment is charged the same as a dog in the brake van.</p>
<h2>Your responsibilities</h2>
''' + ul('The dog must have a collar and chain.', 'The owner arranges food and water for the dog during the journey.') + '''
<h2>If a dog is found unbooked</h2>
<p>An unbooked dog is charged at six times the luggage scale rate, with a minimum of ''' + R + '''50.</p>
<h2>Railway liability</h2>
<p>Unless the owner declares a higher value and pays the percentage charge on it, the Railway's liability for dogs (along with donkeys, sheep, goats, other animals and birds) is limited to ''' + R + '''30 per head.</p>
<div class="note">The Indian Railways page these rules come from shows no date. Ask at the parcel or luggage office of your station before you travel.</div>
<h2>In short</h2>
''' + ul('Brake van dog box, or First Class / AC First with fellow passengers\' consent.', 'Not in AC sleeper, AC chair car, sleeper or second class.', 'Book in advance; unbooked dogs cost six times the rate (minimum ' + R + '50).'),
  [S_LUG]))

# 7 ---------------- quota codes
G.append(('/guides/railway-quota-codes-explained/',
  'Railway quota codes explained: GN, TQ, LD, SS and the rest',
  'What each Indian Railways quota code means, which quotas you can book on IRCTC, and how the Ladies and Tatkal quotas work.',
  'Quota codes', 'Railway quota codes explained: GN, TQ, LD, SS and the rest',
  'Berths on Indian trains are split into quotas, each with a short code that shows up on tickets and booking screens. This guide decodes them.',
  'What GN, TQ, PT, LD, SS, HP and the other codes mean.', '''
<h2>The quota codes</h2>
<p>Indian Railways publishes this list of quotas:</p>
''' + table(['Code', 'Quota'],
            [['GN', 'General quota'], ['LD', 'Ladies quota'], ['HO', 'Headquarters / high official quota'], ['DF', 'Defence quota'],
             ['PH', 'Parliament House quota'], ['FT', 'Foreign Tourist quota'], ['DP', 'Duty Pass quota'], ['TQ', 'Tatkal quota'],
             ['PT', 'Premium Tatkal quota'], ['SS', 'Female (above 45) / Senior Citizen / travelling alone'], ['HP', 'Physically handicapped quota'],
             ['RE', 'Railway employee staff on duty for the train'], ['GNRS', 'General quota road side'], ['OS', 'Out station'],
             ['PQ', 'Pooled quota'], ['RC (RAC)', 'Reservation Against Cancellation'], ['RS', 'Road side'], ['YU', 'Yuva'], ['LB', 'Lower berth']]) + '''
<h2>Quotas you can book on IRCTC</h2>
<p>IRCTC's Terms and Conditions list these quotas on its website and app: General, Tatkal, Premium Tatkal, Ladies, Lower Berth / Senior Citizen, Divyaang and Foreign Tourist.</p>
<h2>Ladies quota</h2>
<p>IRCTC says the Ladies quota is generally earmarked in Sleeper (SL) and Second Sitting (2S). A woman travelling alone, or with children under 12, can choose "Ladies" as the quota. If Ladies quota berths are available she gets a berth in the ladies cabin; otherwise a berth is given from the General quota, if available.</p>
<h2>Tatkal quota</h2>
<p>IRCTC says Tatkal quota berths are kept in important trains in all classes except First AC (1A), and that the Ladies or General quota cannot be chosen together with Tatkal. Timings and charges are in our ''' + link('/guides/tatkal-ticket-booking-rules/', 'Tatkal guide') + '''.</p>
<h2>RAC is not really a quota</h2>
<p>Indian Railways notes that RAC is a special provision to split a berth into two or more seats. It is listed with the quotas but is a predefined allocation rather than a quota. See our ''' + link('/guides/rac-ticket-meaning-rules/', 'RAC guide') + '''.</p>
<h2>Road side quotas</h2>
<p>Indian Railways explains that berths in a road-side quota are booked from the originating station only up to that road-side station, without distance restriction. A through passenger cannot be given such a berth. Its example: a passenger from New Delhi to Chennai cannot get a berth defined as GNRS up to Bhopal and then as GN from Bhopal to Chennai.</p>
<h2>In short</h2>
''' + ul('GN is general; TQ and PT are Tatkal and Premium Tatkal; LD is Ladies; SS is the lower berth quota for senior citizens and women above 45.',
         'On IRCTC you can book General, Tatkal, Premium Tatkal, Ladies, Lower Berth/Senior Citizen, Divyaang and Foreign Tourist.'),
  [S_QUOTA, S_TC, S_TATF]))

# 8 ---------------- RAC
G.append(('/guides/rac-ticket-meaning-rules/',
  'RAC ticket meaning: can you travel, and what you get',
  'What RAC (Reservation Against Cancellation) means, sharing a berth, bedrolls in AC classes, and the cancellation and refund rules for RAC tickets.',
  'RAC tickets', 'RAC ticket meaning: can you travel, and what you get',
  'RAC stands for Reservation Against Cancellation. An RAC ticket lets you board, but you may share a berth until a confirmed passenger cancels. Here is what the rules say.',
  'Sharing a berth, bedrolls, and the cancellation deadline.', '''
<h2>What RAC means</h2>
<p>Indian Railways describes RAC as a special provision to split a berth into two or more seats. The Ministry of Railways has described one berth being shared by two RAC passengers. An RAC passenger travels in the coach, unlike a fully waitlisted e-ticket holder (see our ''' + link('/guides/waitlisted-e-ticket-after-chart/', 'waitlist guide') + ''').</p>
<h2>Bedrolls in AC classes</h2>
<p>In 2009 the Ministry of Railways decided that RAC passengers in AC classes (except AC Chair Car) get a blanket and a bedsheet, since bedroll charges are included in their fare. A Railway Board circular dated 18 December 2023 is titled "Complete bedroll kit (linen &amp; blanket) to RAC passengers".</p>
<h2>Cancelling an RAC ticket</h2>
''' + ul('IRCTC says no refund is given on an RAC e-ticket unless it is cancelled, or a TDR is filed online, up to 30 minutes before the train\'s scheduled departure.',
         'Indian Railways\' refund rules (from 12 November 2015) charge clerkage when an RAC or waitlisted ticket is cancelled: ' + R + '60 per passenger, or ' + R + '30 for unreserved second class.') + '''
<p>More in our guide to ''' + link('/guides/cancel-irctc-e-ticket/', 'cancelling an e-ticket') + '''.</p>
<h2>Mixed tickets</h2>
<p>IRCTC says that if some passengers on a ticket are confirmed and others are on RAC or the waitlist, the confirmed passengers still get a full refund minus clerkage, provided all passengers are cancelled or TDRs filed online up to 30 minutes before departure.</p>
<h2>Trains without RAC</h2>
<p>The Ministry of Railways told the Lok Sabha on 11 March 2026 that the Vande Bharat Sleeper has no provision of RAC tickets: waitlisted passengers are confirmed when confirmed passengers cancel.</p>
<h2>Insurance</h2>
<p>IRCTC's optional travel insurance can be taken on confirmed, RAC and partly confirmed tickets at booking. See our ''' + link('/guides/irctc-travel-insurance/', 'insurance guide') + '''.</p>
<h2>In short</h2>
''' + ul('RAC lets you travel; you may share a berth.', 'AC RAC passengers get bedding.', 'Cancel or file a TDR at least 30 minutes before departure, or there is no refund.'),
  [S_QUOTA, S_PIB_RAC, S_RB_BED, S_CAN, S_REF, S_PIB_2026, S_INS]))

# 9 ---------------- current booking
G.append(('/guides/current-booking-after-chart/',
  'Current booking: buying a vacant berth after the chart is made',
  'How IRCTC current booking works: who can book, confirmed tickets only, and the changes that are not allowed on a current booking ticket.',
  'Current booking', 'Current booking: buying a vacant berth after the chart is made',
  'After the reservation chart is prepared, berths that are still empty can be booked as "current booking". This guide sets out IRCTC\'s rules.',
  'Booking empty berths after charting, and its limits.', '''
<h2>What current booking is</h2>
<p>IRCTC describes current booking as booking against vacant accommodation after charting, within the booking time limit set by Railways.</p>
<h2>IRCTC's rules</h2>
''' + ul('All users, normal and agents, can book.', 'Only e-tickets can be booked.', 'Only confirmed tickets are booked.',
         'Only the senior citizen and disabled concessions are allowed. (The senior citizen concession itself was withdrawn by Railways from 20 March 2020; see our ' + link('/guides/senior-citizen-train-concession/', 'senior citizen guide') + '.)',
         'The boarding point cannot be changed.', 'The name, age and gender cannot be changed.',
         'In Premium and Suvidha trains, booking is allowed at the last booking fare.') + '''
<h2>IRCTC's own trains</h2>
<p>For the trains IRCTC runs itself, IRCTC says current booking opens after the first chart and stays open until 5 minutes before the scheduled departure.</p>
<h2>Where to see empty berths</h2>
<p>Current booking only works if a berth is still empty after the chart. ClearBerth's Book tab shows seats class by class for a date; tickets are booked on IRCTC.</p>
<h2>In short</h2>
''' + ul('After charting, empty berths can be bought on IRCTC as confirmed e-tickets.', 'No boarding point, name, age or gender change on these tickets.'),
  [S_CUR, S_TC, S_IRCTC_TR, S_PIB_SR20]))

# 10 ---------------- foreign tourist
G.append(('/guides/foreign-tourist-quota-irctc/',
  'Foreign Tourist quota on IRCTC: booking, fare and passport rules',
  'How foreign tourists and NRIs book Indian train tickets on IRCTC: the 365-day window, 1.5 times fare, fees, passport and visa checks, and cancellation.',
  'Foreign Tourist quota', 'Foreign Tourist quota on IRCTC: booking, fare and passport rules',
  'Foreign tourists and NRIs with a valid passport can book train tickets online on IRCTC under the Foreign Tourist (FT) quota. These are IRCTC\'s rules for it.',
  'Who can book, the fare and fees, and the passport rule.', '''
<h2>Who can use it</h2>
<p>IRCTC says Foreign Tourists, including NRIs, holding a valid passport can book under the Foreign Tourist quota on the IRCTC website. Users from outside India register as international users and pay a registration fee of ''' + R + '''100 + GST. They must verify an international mobile number in their IRCTC profile with an OTP.</p>
<h2>How far ahead</h2>
<p>FT quota tickets can be booked up to 365 days in advance. If you book within the normal Advance Reservation Period (60 days), the berth is allotted at booking; if you book earlier, the berth is allotted when the period opens, and you are told by international SMS. If no berth is allotted, the ticket is cancelled automatically.</p>
<h2>Classes and fare</h2>
''' + ul('Classes: Executive (EC), 1st AC, 2nd AC, 3rd AC, AC Chair Car, Sleeper and Second Sitting, in all trains including Shatabdi, Rajdhani, Duronto and Gatimaan. IRCTC says FT booking is not allowed in Suvidha trains.',
         'The fare is 1.5 times the normal fare. A child without a berth pays half the adult base fare, which on this quota is 1.5 times the normal base fare.',
         'IRCTC charges a service charge of ' + R + '200 + GST per ticket.',
         'Payment is only by international debit or credit card.', 'No concession is allowed.') + '''
<h2>Passport and visa on the train</h2>
<p>The passport number and nationality of every passenger must be entered at booking. Each passenger must carry the original passport given at booking, with a valid visa. IRCTC says a passenger who cannot show them is treated as travelling without a ticket and charged a penalty of three times the fare.</p>
<h2>Cancellation</h2>
<p>When an FT quota ticket is cancelled, a flat 50% of the fare is deducted in addition to the normal cancellation charges, up to 4 hours before the scheduled departure and through the website only. Waitlisted and RAC FT tickets follow the General quota cancellation rules.</p>
<h2>Not allowed on FT quota tickets</h2>
''' + ul('Change of name', 'Booking by agents', 'I-tickets', 'Travel insurance', 'VIKALP') + '''
<p>The boarding point can be changed, and the ERS printed, only after a berth has been allotted.</p>
<h2>In short</h2>
''' + ul('Up to 365 days ahead, 1.5 times fare, ' + R + '200 + GST per ticket.', 'Carry the original passport and visa for every passenger.', '50% of the fare is deducted on cancellation, plus normal charges.'),
  [S_FTB, S_FT, S_PIB_FT, S_TC]))

# 11 ---------------- e-ticket on phone
G.append(('/guides/e-ticket-on-phone-sms-printout/',
  'Do you need a printout of your IRCTC e-ticket?',
  'IRCTC accepts the e-ticket on a phone or laptop, or the booking SMS, with an original ID. What counts, platform entry, and what happens if you cannot show it.',
  'E-ticket on phone', 'Do you need a printout of your IRCTC e-ticket?',
  'No printout is needed. IRCTC accepts the e-ticket on a screen or the booking SMS, as long as you also carry an original ID. Here are the exact rules.',
  'ERS, the screen version (VRM) and the SMS, with ID.', '''
<h2>Three forms that are accepted</h2>
<p>IRCTC's Terms and Conditions name three forms of an e-ticket:</p>
''' + ul('<b>ERS (Electronic Reservation Slip)</b>: the printout of the e-ticket.',
         '<b>VRM (Virtual Reservation Message)</b>: a screenshot of the e-ticket shown on a laptop or mobile device.',
         '<b>SMS</b>: the text message with the PNR and journey details sent to your contact number.') + '''
<p>Any one of these, with one of the prescribed ID proofs in original and the passenger's name in the reservation chart, authorises the passenger to travel.</p>
<h2>No platform ticket needed</h2>
<p>IRCTC says the ERS, VRM or SMS, with an original ID, also lets the passenger enter the platform on the day of the journey without buying a platform ticket. Ticket checking staff can ask for both on the platform, and the TTE checks them against the name and PNR on the chart.</p>
<h2>If you cannot show the ticket</h2>
<p>If a passenger cannot show the ERS, VRM or SMS for any reason, such as a lost or discharged phone or laptop, but has the prescribed ID in original, IRCTC says a penalty is charged under Railway rules and the ticket checking staff issue an EFT (Excess Fare Ticket).</p>
<h2>After a partial cancellation</h2>
<p>If some passengers on a ticket are cancelled, IRCTC asks that the modified ERS be printed separately for the passengers still travelling.</p>
<h2>The ID still matters</h2>
<p>The ticket on screen is not enough on its own: one passenger on the ticket must carry an accepted ID in original. See our ''' + link('/guides/id-proof-for-train-travel/', 'ID proof guide') + '''. You can check your PNR status on ClearBerth's ''' + link('/pnr-status/', 'PNR status page') + '''.</p>
<h2>In short</h2>
''' + ul('Printout, screenshot or the booking SMS all work.', 'Carry an original ID for one passenger on the ticket.', 'No platform ticket needed with an e-ticket and ID.'),
  [S_TC, S_FAQ]))

# 12 ---------------- limits & timings
G.append(('/guides/irctc-booking-limits-and-timings/',
  'IRCTC booking limits and timings: tickets per month, passengers and hours',
  'How many tickets an IRCTC user can book in a month (12, or 24 with Aadhaar), passengers per ticket, booking hours and opening times.',
  'Booking limits and hours', 'IRCTC booking limits and timings: tickets per month, passengers and hours',
  'IRCTC limits how many tickets one user ID can book, how many passengers fit on one ticket and when booking is open. Here are the current numbers from IRCTC and the Ministry of Railways.',
  'Tickets per month, passengers per ticket and booking hours.', '''
<h2>Tickets per month</h2>
''' + table(['User ID', 'Limit per month'],
            [['Not Aadhaar-verified', '12 tickets'],
             ['Aadhaar-verified, with at least one passenger on the ticket Aadhaar-verified', '24 tickets']]) + '''
<p style="margin-top:10px">These limits were raised from 6 and 12 by the Ministry of Railways in June 2022. IRCTC's guide says that to book more than 12 tickets in a month, the user must complete Aadhaar KYC in the profile and add at least one Aadhaar-verified passenger. IRCTC also says an Aadhaar-authenticated user can book Tatkal and Premium Tatkal tickets; see our ''' + link('/guides/aadhaar-train-ticket-booking-rules/', 'Aadhaar guide') + '''.</p>
<h2>Passengers per ticket</h2>
''' + ul('A normal booking: up to six berths or seats at a time for one journey.', 'A Tatkal e-ticket: up to four passengers per PNR.') + '''
<h2>Booking hours</h2>
''' + ul('IRCTC\'s Terms and Conditions say internet booking is allowed from 00:20 to 23:45 IST every day, including Sundays, and that the hours can change without notice.',
         'On the opening day (60 days ahead, not counting the journey date), booking opens only after 8 AM. Some intercity day trains have a shorter booking window. See our ' + link('/guides/advance-reservation-period-60-days/', '60-day guide') + '.',
         'Tatkal opens at 10:00 for AC classes and 11:00 for non-AC classes, one day before the train leaves its starting station.') + '''
<h2>One account per person</h2>
''' + ul('Only one user registration is allowed on each email ID and mobile number. IRCTC says more than one user ID on the same email or mobile may lead to deactivation.',
         'IRCTC advises keeping at most six passengers in the Master Passenger List; more than six makes the list inaccessible, though you can still type passengers in directly.',
         'Automation and scripting software are prohibited. IRCTC can deactivate such users and release tickets booked through them without refund.') + '''
<h2>Convenience fee</h2>
<p>IRCTC says its convenience fee on a successful e-ticket booking is not refundable under any circumstances.</p>
<h2>In short</h2>
''' + ul('12 tickets a month, or 24 with Aadhaar verification.', 'Up to 6 passengers per booking, 4 on Tatkal.', 'Booking open 00:20 to 23:45; opening day after 8 AM.'),
  [S_PIB_LIM, S_AAD24, S_TC]))

# 13 ---------------- senior citizen
G.append(('/guides/senior-citizen-train-concession/',
  'Senior citizen train concession in 2026: what is still available',
  'The senior citizen fare concession was withdrawn in March 2020. What the Ministry of Railways says senior citizens still get, such as lower berths.',
  'Senior citizens', 'Senior citizen train concession in 2026: what is still available',
  'Indian Railways withdrew the senior citizen fare concession in March 2020. This guide sets out what that means and the facilities that continue, from Ministry of Railways statements.',
  'The fare concession and the lower berth facilities that continue.', '''
<h2>The fare concession was withdrawn in 2020</h2>
<p>The Ministry of Railways withdrew concessional tickets for senior citizens, on both reserved and unreserved tickets, from 00:00 hours on 20 March 2020 (PIB release, 19 March 2020). It said the withdrawal was until further advisory.</p>
<h2>What the concession used to be</h2>
<p>Before that, men of Indian nationality aged 60 and above got 40% off, and women aged 58 and above got 50% off, in all classes, including Rajdhani, Shatabdi and Duronto trains (PIB, 2 December 2016). The concession applied to the basic fare.</p>
<h2>What the Ministry said in March 2026</h2>
<p>In a Lok Sabha reply on 11 March 2026, the Ministry of Railways said it gave a subsidy of ''' + R + '''60,239 crore on passenger tickets in 2024-25, an average concession of 43% to every passenger, and that this subsidy continues for all passengers. It said concessions beyond this continue for 4 categories of persons with disabilities, 11 categories of patients and 8 categories of students. Senior citizens are not in that list.</p>
<div class="note">Some older IRCTC pages still mention the senior citizen concession. The Ministry's 2020 withdrawal above is the rule that applies.</div>
<h2>Facilities that continue for senior citizens</h2>
<p>From the same March 2026 reply:</p>
''' + ul('Senior citizens, persons with disabilities and women aged 45 and above are allotted lower berths automatically, even if no choice is given, subject to availability.',
         'A combined quota of six to seven lower berths per coach in Sleeper, four to five in 3AC and three to four in 2AC (depending on how many coaches of that class the train has) is kept for senior citizens, women aged 45 and above and pregnant women.',
         'Lower berths that fall vacant during the journey go first to senior citizens, persons with disabilities and pregnant women who were given a middle or upper berth.') + '''
<p>More on these in our ''' + link('/guides/lower-berth-and-ladies-quota-rules/', 'lower berth guide') + '''. A senior citizen booked on the senior citizen quota must carry proof of age (Railway Board circular, 16 November 2021).</p>
<h2>In short</h2>
''' + ul('No senior citizen fare concession since 20 March 2020.', 'Lower berth priority and a lower berth quota continue.'),
  [S_PIB_SR20, S_PIB_SR16, S_PIB_2026, S_ID21]))

# 14 ---------------- divyangjan
G.append(('/guides/divyangjan-railway-concession/',
  'Railway concession for persons with disabilities (Divyangjan)',
  'The four categories of Divyangjan who get a train fare concession, the rates, the Railway photo ID card, booking online on IRCTC and the reserved berths.',
  'Divyangjan concession', 'Railway concession for persons with disabilities (Divyangjan)',
  'Indian Railways gives fare concessions to four categories of persons with disabilities, and keeps berths for them. This guide sets out the rules from the Ministry of Railways and IRCTC.',
  'Who qualifies, the rates, the ID card and online booking.', '''
<h2>The concession continues</h2>
<p>In a Lok Sabha reply on 11 March 2026 the Ministry of Railways said concessions continue for 4 categories of persons with disabilities (Divyangjans).</p>
<h2>Who qualifies and how much</h2>
<p>A Ministry of Railways release of 3 December 2019 sets out the four categories and the concession on single journey tickets:</p>
''' + table(['Category', 'Concession'],
            [['Orthopedically handicapped or paraplegic persons who cannot travel without an escort', '75% in Second, Sleeper, First Class, AC Chair Car and AC 3-tier; 50% in AC 2-tier and AC First; 25% in 3AC and AC Chair Car of Rajdhani/Shatabdi. One escort gets the same concession.'],
             ['Mentally challenged persons who cannot travel without an escort', 'Same as above'],
             ['Persons with visual impairment with total absence of sight, travelling alone or with an escort', 'Same as above'],
             ['Persons with total hearing and speech impairment (both in the same person), travelling alone or with an escort', '50% in Second, Sleeper and First Class. One escort gets the same concession.']]) + '''
<div class="note">These rates are from the 2019 release. Check the fare shown on IRCTC when you book.</div>
<h2>The Railway photo ID card</h2>
<p>To book a concessional ticket online, the passenger needs the photo identity card issued by Railways for persons with disabilities. A Southern Railway release says these ID cards can be applied for and renewed online at divyangjanid.indianrail.gov.in.</p>
<h2>Booking on IRCTC</h2>
<p>IRCTC says the booking form asks for the details on the Railway photo ID card: name, age, gender, concession type, ID card number, date of birth and the "valid up to" date. The passenger must carry the card for checking on and off the train, and an escort must carry the photo ID given at booking. Passengers can be saved in the IRCTC Master List.</p>
<h2>Reserved berths</h2>
<p>In the March 2026 reply, the Ministry said a quota for persons with disabilities and their attendants is kept in mail/express trains, including Rajdhani and Shatabdi type trains:</p>
''' + ul('Four berths in Sleeper (two lower and two middle)', 'Four berths in 3AC/3E (two lower and two middle)', 'Four seats in Second Sitting (2S) or AC Chair Car (CC), where the train has more than two coaches of that class') + '''
<p>Persons with disabilities are also allotted lower berths automatically, subject to availability, and get priority for lower berths that fall vacant during the journey.</p>
<h2>In short</h2>
''' + ul('Four categories qualify; the escort gets the same concession.', 'Book online with the Railway photo ID card and carry it on the train.', 'Four berths per class are kept in mail/express trains.'),
  [S_PIB_2026, S_PIB_DIV, S_DIVF, S_SR_DIV, S_ID21]))

# 15 ---------------- complaints
G.append(('/guides/train-complaint-railmadad-139/',
  'How to complain about a train journey: RailMadad, 139 and IRCTC',
  'Where to complain about a train journey (RailMadad and helpline 139) and about an IRCTC booking (14646 and equery), plus food complaints.',
  'Complaints and helplines', 'How to complain about a train journey: RailMadad, 139 and IRCTC',
  'Complaints about the train and complaints about an IRCTC booking go to different places. This guide lists the official channels.',
  'RailMadad and 139 for the journey; IRCTC for the booking.', '''
<h2>Journey problems: RailMadad</h2>
<p>The Ministry of Railways describes RailMadad as Indian Railways' grievance redressal system, an integrated platform for grievances, assistance and enquiry (PIB, 25 March 2026). You can reach it through:</p>
''' + ul('Helpline <b>139</b>', 'The RailMadad website', 'The RailMadad app', 'SMS') + '''
<p>RailMadad also lets passengers give feedback on how their complaint was resolved.</p>
<h2>Emergencies on the train</h2>
<p>The Ministry says passengers needing immediate help can complain on the RailMadad portal or call helpline 139, which is integrated with the Emergency Response Support System number 112.</p>
<h2>Booking problems: IRCTC</h2>
<p>IRCTC's Terms and Conditions list these channels for railway tickets booked on IRCTC:</p>
''' + ul('Customer care: <b>14646</b>, 24x7, in Hindi, English, Punjabi, Bengali, Assamese, Odia, Marathi, Gujarati, Tamil, Telugu, Kannada and Malayalam',
         'From outside India: +91-8044647999 or +91-8035734999',
         'General queries: equery.irctc.co.in',
         'E-ticket cancellation problems: etickets@irctc.co.in') + '''
<p>IRCTC also says you should check your ticket for errors as soon as you get it and report any error straight away on 14646.</p>
<h2>Food on the train</h2>
<p>Indian Railways' catering page says complaint books are available with the TTE, the pantry car manager and the station manager. The Ministry's March 2026 release lists steps against overcharging, including an SMS to passengers with a link to the menu and tariff, and POS machines for billing.</p>
<h2>In short</h2>
''' + ul('Train journey: RailMadad, or call 139.', 'IRCTC booking: 14646 or equery.irctc.co.in.', 'Food: ask for the complaint book.'),
  [S_PIB_RM, S_PIB_112, S_TC, S_CAT]))

# 16 ---------------- insurance
G.append(('/guides/irctc-travel-insurance/',
  'IRCTC travel insurance: 45 paise cover and what it pays',
  "IRCTC's optional travel insurance for e-ticket passengers: the premium, who can take it, the sums insured, and how to claim.",
  'Travel insurance', 'IRCTC travel insurance: 45 paise cover and what it pays',
  'When you book an e-ticket on IRCTC you can add optional travel insurance for a few paise. Here is what IRCTC\'s terms say it covers.',
  'The premium, the sums insured and who can take it.', '''
<h2>Premium and who can take it</h2>
''' + ul('The premium is <b>45 paise per passenger</b>, including all taxes, from 17 February 2024.',
         'It is optional, but if you choose it, it applies to every passenger on the PNR.',
         'It is offered only on confirmed, RAC and partly confirmed tickets, at the time of booking.',
         'It is only for Indian citizens booking e-tickets on IRCTC. Foreign citizens are not eligible, and it is not available on Foreign Tourist quota tickets.') + '''
<h2>What it pays</h2>
<p>IRCTC says the cover is the same for all classes:</p>
''' + table(['Event', 'Sum insured'],
            [['Death', R + '10,00,000'], ['Permanent total disability', R + '10,00,000'], ['Permanent partial disability', 'Up to ' + R + '7,50,000'],
             ['Hospitalisation expenses for injury', R + '2,00,000'], ['Transportation of mortal remains', R + '10,000']]) + '''
<p style="margin-top:10px">Hospitalisation cover is in addition to the death or disability cover.</p>
<h2>What it covers</h2>
<p>The cover is for a train accident or an "untoward incident" as defined in the Railways Act, 1989 (for example a violent attack, robbery or the accidental falling of a passenger from a train), from the train's actual departure to its actual arrival, including getting on and off. It also covers:</p>
''' + ul('Road transport arranged by the railway if the train is terminated short of the destination', 'The diverted route if the train is diverted', 'The alternative train under VIKALP') + '''
<h2>Children</h2>
<p>Children below 5 booked without a berth or seat are not covered. Children aged 5 to 11 are covered, with or without a berth.</p>
<h2>Nominee and claims</h2>
<p>The insurance company sends the policy details by SMS and email, with a link to fill in nomination details; the policy number is also shown in IRCTC's booked ticket history. If no nominee is filled in, a claim is settled with the legal heirs. IRCTC says the contract is between the passenger and the insurance company, and all correspondence and claims go directly to the insurer.</p>
<h2>In short</h2>
''' + ul('45 paise per passenger, for confirmed, RAC and partly confirmed e-tickets.', 'Up to ' + R + '10 lakh for death or permanent total disability.', 'Fill in the nominee on the insurer\'s site after booking.'),
  [S_INS, S_FT]))

# 17 ---------------- theft
G.append(('/guides/luggage-stolen-on-train-complaint/',
  'Luggage stolen on a train: how to report it',
  'What to do if your luggage is stolen on a train: the FIR form with the TTE or guard, RailMadad and 139, RPF help, and the railway\'s liability for booked luggage.',
  'Theft on a train', 'Luggage stolen on a train: how to report it',
  'You do not have to get off the train to report a theft. Here is the procedure Indian Railways publishes, and the help line to call.',
  'Reporting a theft without breaking your journey.', '''
<h2>Report it on the train</h2>
<p>Indian Railways' rules say that in a case of theft, robbery or dacoity on a running train, you can approach the train conductor, coach attendant, guard or the GRP (Government Railway Police) escort. They give you an FIR form. You fill it in and hand it back, and the complaint is forwarded to the police station for action. You do not need to break your journey to lodge the complaint.</p>
<p>The rules say the FIR form is available in English, Hindi and the regional language with the TTE, guard or GRP escort.</p>
<h2>Call 139</h2>
<p>The Ministry of Railways says passengers needing immediate help can complain on the RailMadad portal or call helpline <b>139</b>, which is integrated with the emergency number 112. See our ''' + link('/guides/train-complaint-railmadad-139/', 'complaints guide') + '''.</p>
<h2>At the station</h2>
<p>You can also go to the RPF (Railway Protection Force) assistance posts at major stations for help in lodging the complaint.</p>
<h2>Booked luggage that is lost or damaged</h2>
<p>For luggage booked with the railway (not carried with you), the rules say that if its value was not declared and the percentage charge was not paid, the railway's liability is limited to ''' + R + '''100 per kg. If the value was declared and the charge paid, the claim can be up to the declared value. Ask at the luggage office about the percentage charge before booking.</p>
<h2>Travel insurance</h2>
<p>IRCTC's optional travel insurance covers death, disability and injury from an "untoward incident", which includes robbery and a violent attack on a train. See our ''' + link('/guides/irctc-travel-insurance/', 'insurance guide') + '''.</p>
<h2>In short</h2>
''' + ul('Ask the TTE, guard, coach attendant or GRP escort for the FIR form.', 'Call 139 for immediate help.', 'Booked luggage: liability is ' + R + '100 per kg unless you declared the value.'),
  [S_LUG, S_PIB_112, S_INS]))

for p, t, d, s, h1, lead, _b, body, srcs in G:
    build(p, t, d, s, h1, lead, body, srcs)

# guides index + sitemap (idempotent)
ip = os.path.join(ROOT, 'guides/index.html')
ix = open(ip, encoding='utf-8').read()
for p, t, d, s, h1, lead, blurb, body, srcs in G:
    if 'href="%s"' % p in ix:
        continue
    card = '<a href="%s"><b>%s</b><span>%s</span></a>' % (p, E(h1), E(blurb))
    ix = ix.replace('</div><div class="note">', card + '</div><div class="note">', 1)
open(ip, 'w', encoding='utf-8').write(ix)
sp = os.path.join(ROOT, 'sitemap.xml')
sm = open(sp, encoding='utf-8').read()
for p, *_ in G:
    if p not in sm:
        sm = sm.replace('</urlset>', '  <url><loc>https://clearberth.app%s</loc><lastmod>%s</lastmod></url>\n</urlset>' % (p, TODAY))
sm = re.sub(r'(/guides/</loc><lastmod>)[0-9-]+', r'\g<1>' + TODAY, sm)
open(sp, 'w', encoding='utf-8').write(sm)
print('built', len(G), 'guides')
