#!/usr/bin/env python3
"""8 more guides (24 Nov 2026), same layout as the other /guides/ pages, so there are 33 in all.
Facts come only from the IRCTC, Indian Railways, Railway Board and PIB (Ministry of Railways) pages cited
on each guide. Links them from /guides/ and the sitemap. Safe to run again.
Run from the repo root: python3 tools/build_guides_batch4.py
Then refresh the guide link blocks: python3 tools/add_internal_links.py --write --refresh-guides"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = open(os.path.join(ROOT, 'guides/tatkal-ticket-booking-rules/index.html'), encoding='utf-8').read()
HEAD = TPL[:TPL.index('</head>') + 7]
TAIL = TPL[TPL.index('<h2>Check your ticket in the app</h2>'):]
TAIL = re.sub(r'<h2 id="il-guides">.*?</div>\n', '', TAIL, flags=re.S)   # refreshed by add_internal_links.py
CHECKED = '24 November 2026'
TODAY = '2026-11-24'
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
           '<div class="top"><a class="logo" href="/"><img src="/shots/icon.png?v=2" alt="" width="30" height="30">ClearBerth</a><a class="btn sm" href="/#get-app">Get the app</a></div>\n'
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
S_CAN = ("IRCTC: E-ticket cancellation", "https://contents.irctc.co.in/en/eticketCancel.html")
S_QUOTA = ("Indian Railways: Quota codes", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=quota_Code.html")
S_TATS = ("Indian Railways: Tatkal scheme", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=tatkal_Scheme.html")
S_CATIR = ("Indian Railways: Catering charges and complaints", "https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=CateringCharge.html")
S_MR_M = ("IRCTC menu rates: standard meals", "https://menurates.irctc.co.in/standared_meal.html")
S_MR_B = ("IRCTC menu rates: standard breakfast", "https://menurates.irctc.co.in/standared_breakfast.html")
S_MR_V = ("IRCTC menu rates: beverages", "https://menurates.irctc.co.in/standared_beverages.html")
S_PIB_FOOD = ("PIB, 15 November 2019: catering menu and rates", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=1591774&reg=48&lang=2")
S_ECAT = ("IRCTC eCatering", "https://www.ecatering.irctc.co.in/")
S_PIB_CONC = ("PIB, 2 December 2016: concession to railway passengers in various categories", "https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=154835")
S_PIB_2026 = ("PIB, 11 March 2026: Lok Sabha reply on fares, concessions and lower berths", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238430")

G = []   # (path, title, desc, short, h1, lead, blurb, body, sources)

# 1 ---------------- account and passenger list
G.append(('/guides/irctc-account-and-passenger-list-help/',
  'IRCTC account rules: one ID, passenger list and deactivation',
  'What IRCTC\'s Terms say about registering one user ID, the six-passenger master list, why an ID can be deactivated and what to do if someone misuses your account.',
  'IRCTC account help', 'IRCTC account rules: one ID, the passenger list and deactivation',
  'Most IRCTC account problems come from a few rules in its Terms and Conditions: one ID per person, a short passenger list and no automation. Here is what they say.',
  'One ID per person, the six-passenger list and what gets an ID deactivated.', '''
<h2>One user ID per email and mobile number</h2>
<p>IRCTC says no user can register more than once on the site, and only one user registration is allowed on each unique email ID and mobile number. More than one user ID on an email ID and mobile number may lead to deactivation of the ID. If a user registers more than one ID or books tickets on such multiple IDs, IRCTC reserves the right to deactivate all of those registrations and cancel any or all tickets booked on them without notice.</p>
<h2>The master passenger list</h2>
<p>IRCTC advises users to keep a maximum of six passengers in their Master Passengers List. If you keep more than six, the Master List becomes inaccessible to you. You can still book for other passengers by typing their details directly on the Passenger Reservation page.</p>
<h2>What can get an ID deactivated</h2>
''' + ul('Registering more than once, or booking on several IDs.',
         'Incomplete or incorrect registration details, or junk values.',
         'An address that was entered incorrectly at registration.',
         'Suspicious booking activity, including scripting tools or Tatkal software. IRCTC may also release the tickets booked on such IDs, and no refund of fare is admissible in cases of misuse.',
         'Payment that the payment gateway does not authorise more than once for tickets you booked, which is liable to result in deregistration without notice.') + '''
<p>IRCTC says its website and apps are for personal and non-commercial use, and that automation or scripting software is strictly prohibited.</p>
<h2>Keep your login safe</h2>
<p>You are responsible for keeping your password and account confidential, and for all activity under it. IRCTC asks you to log out at the end of each session and to report unauthorised use of your password or account straight away at <b>equery.irctc.co.in</b>. IRCTC may also ask you from time to time to provide and verify your email ID and mobile number. You confirm when registering that you are 18 or above. IRCTC says it is not responsible for financial loss from misuse of your ID, password or card details.</p>
<h2>Foreign users</h2>
<p>People from countries other than India, and NRIs, can register as Foreign Users by paying a registration fee. They can then book under the Foreign Tourist quota and the General quota. See our ''' + link('/guides/foreign-tourist-quota-irctc/', 'foreign tourist quota guide') + '''.</p>
<h2>Who to contact</h2>
<p>IRCTC's customer care number is <b>14646</b>, open 24 hours. For general information, IRCTC lists equery.irctc.co.in.</p>
<h2>In short</h2>
''' + ul('One user ID per email ID and mobile number.', 'Keep at most six people in the master list; type any others on the booking page.', 'Never use scripts or tools to book, and report misuse of your account at once.'),
  [S_TC]))

# 2 ---------------- booking for someone else
G.append(('/guides/book-train-ticket-for-someone-else/',
  'Booking a train ticket for someone else on IRCTC',
  'You can book for family and friends from your own IRCTC login. What IRCTC says about the ID, the six-berth limit, Tatkal limits and why a ticket cannot be resold.',
  'Booking for someone else', 'Booking a train ticket for someone else on IRCTC',
  'You can use your own IRCTC login to book for other people. The rules to know are about who must show ID, how many people one booking can hold and what you cannot do.',
  'Booking for family and friends: ID, limits and what is not allowed.', '''
<h2>Yes, you can book for other passengers</h2>
<p>IRCTC says you can enter any passenger's details directly on the Passenger Reservation page, even if that person is not in your master passenger list. The ticket is booked in the names you enter.</p>
<h2>Who has to show ID</h2>
<p>IRCTC says the accommodation booked is not transferable. It is valid only if one of the passengers on the e-ticket presents one of the authorised IDs in original during the journey. That person does not have to be the one who booked. If nobody can show an ID, the passengers are treated as travelling without a ticket under the Railway rules. See our ''' + link('/guides/id-proof-for-train-travel/', 'ID proof guide') + '''.</p>
<p>For passengers who are not Indian, their country's passport is the only authorised ID for travel.</p>
<h2>How many people on one booking</h2>
''' + ul('A maximum of six berths or seats can be booked at a time for a journey between any two stations on the train, subject to the distance restrictions in force.',
         'On a Tatkal e-ticket, a maximum of four passengers can be booked on one PNR.') + '''
<p>For the monthly limit of tickets per user ID, see our ''' + link('/guides/irctc-booking-limits-and-timings/', 'booking limits guide') + '''.</p>
<h2>What you may not do</h2>
<p>IRCTC says you may use the service only for legitimate bookings and not to book tickets for commercial resale and profit. It also says any speculative, false or fraudulent reservation, or any reservation in anticipation of demand, is prohibited.</p>
<h2>If plans change</h2>
<p>IRCTC's FAQ points to a name-change procedure, and our ''' + link('/guides/transfer-train-ticket-change-name/', 'transfer and name change guide') + ''' covers it. The Tatkal rules say change of name is not permitted on Tatkal bookings.</p>
<h2>Who gets the cancellation refund</h2>
<p>Cancellation is done through the booking user's IRCTC login. IRCTC says the refund is credited to the account used for booking.</p>
<h2>In short</h2>
''' + ul('Type the traveller\'s details on the booking page; they need not be in your list.', 'One passenger on the ticket must show an original ID on the journey.', 'Six berths per booking, four passengers per Tatkal PNR, and no resale for profit.'),
  [S_TC, S_FAQ, S_TATS, S_CAN]))

# 3 ---------------- payment failed
G.append(('/guides/irctc-payment-failed-money-deducted/',
  'IRCTC payment failed but money was deducted: what to check',
  'What IRCTC\'s Terms say when a payment fails or the confirmation page does not appear: Booked Ticket History, the automatic refund, repeat bookings and who to contact.',
  'Payment failed, money deducted', 'IRCTC payment failed but money was deducted: what to check',
  'If the page froze after you paid, do not pay again straight away. IRCTC\'s Terms describe the checks to make first and what happens to the money if no ticket was issued.',
  'What to check first when the payment page fails after money is deducted.', '''
<h2>First, check whether the ticket was booked</h2>
<p>IRCTC says that after a successful payment a Ticket Confirmation Page shows your PNR details. If that page does not appear because of a power failure, an internet failure or any other reason, open <b>Booked Ticket History</b> under My Account, then My Transactions. That page lists every ticket booked by you. If your reservation is there, note the transaction ID, the PNR and the other details. IRCTC also advises you to check your email.</p>
<h2>If no ticket was issued</h2>
<p>IRCTC says that if the reservation does not materialise for any reason, the entire amount debited from your card, bank or wallet account is credited back to your source account. If you want to try for the same reservation again, it is treated as a fresh booking.</p>
<p>Booking is subject to the fare and the convenience fee (including GST) being received from the bank through the payment gateway. IRCTC says that if one payment gateway is not working, you can try the other one.</p>
<h2>Do not pay twice for the same ticket</h2>
<p>IRCTC says that if a user does not check Booked Tickets, makes a repeated transaction and also fails to cancel the ticket, the user has no right to claim the amount, and the loss is not borne by IRCTC or by the banks and payment gateways. If you ended up with two tickets for the same journey, cancel the extra one before the chart is prepared. See our ''' + link('/guides/cancel-irctc-e-ticket/', 'cancellation guide') + '''.</p>
<h2>How long does a refund take?</h2>
<p>IRCTC says its payment reconciliation team works round the clock, but it gives no guarantee about how accurate or timely refunds reaching your card or bank account will be. It gives the reason as the many organisations involved in processing online payments, internet problems and bank holidays. The pages we read do not give a number of days.</p>
<h2>If money is still missing</h2>
<ul>
<li>Call IRCTC customer care on <b>14646</b>, open 24 hours.</li>
<li>For general information, IRCTC lists <b>equery.irctc.co.in</b>.</li>
<li>For an e-ticket you could not cancel online, IRCTC says to email the e-ticket details to <b>etickets@irctc.co.in</b>.</li>
</ul>
<h2>Two warnings from the Terms</h2>
''' + ul('Payment that the gateway does not authorise more than once for tickets booked by you can lead to deregistration of your account without notice.', 'The IRCTC convenience fee collected on a successful booking is non-refundable under any circumstances.') + '''
<h2>In short</h2>
''' + ul('Open Booked Ticket History before you pay again.', 'If no ticket was issued, the full amount goes back to the source account.', 'IRCTC gives no guaranteed refund time; call 14646 if it does not arrive.'),
  [S_TC]))

# 4 ---------------- lost / torn ticket
G.append(('/guides/lost-or-torn-train-ticket-duplicate/',
  'Lost or torn train ticket: can you get a duplicate?',
  'What IRCTC and Indian Railways say about duplicate tickets, reprinting an e-ticket, the ERS, VRM and SMS, and the penalty if you cannot show your ticket.',
  'Lost or torn ticket', 'Lost or torn train ticket: can you get a duplicate?',
  'An e-ticket cannot really be lost, because you can show it again from your account. A paper counter ticket is different. Here is what the published rules say.',
  'Reprinting an e-ticket and what a duplicate ticket means.', '''
<h2>E-tickets: show it again</h2>
<p>IRCTC says the Electronic Reservation Slip (ERS), the Virtual Reservation Message (VRM, a screenshot of the e-ticket shown on a phone or laptop) or the SMS sent by IRCTC, together with one of the prescribed IDs in original, authorises you to travel. The name must appear in the reservation chart. If you lose the printout or the phone message, open <b>Booked Ticket History</b> under My Account, then My Transactions, to see the ticket again. See our ''' + link('/guides/e-ticket-on-phone-sms-printout/', 'guide to showing an e-ticket on your phone') + '''.</p>
<h2>If you cannot show the ticket</h2>
<p>IRCTC's Terms say that if a passenger cannot produce or display the ERS, VRM or SMS because of loss or a discharged phone or laptop, but does have the prescribed original proof of identity, the penalty applicable under Railway rules is charged. The ticket checking staff on the train or at the station give an Excess Fare Ticket (EFT) for it.</p>
<h2>Duplicate tickets are not issued on IRCTC</h2>
<p>IRCTC lists "issue of duplicate tickets for lost, mutilated or torn tickets" among the services that are <b>not</b> available on its portal. For a paper ticket bought at a counter, the pages we read do not describe the duplicate procedure, so ask at a Railway reservation counter.</p>
<h2>Tatkal tickets</h2>
<p>Indian Railways' Tatkal scheme page says no duplicate Tatkal tickets are issued. They are issued only in exceptional cases, on payment of full fare including the Tatkal charges.</p>
<h2>Platform entry</h2>
<p>IRCTC says the ERS, VRM or SMS along with the original ID also authorises you to enter the platform on the day of the journey, so you do not need to buy a platform ticket.</p>
<h2>In short</h2>
''' + ul('E-ticket: open Booked Ticket History and show it again with an original ID.', 'No ID or no ticket on the journey means a penalty under Railway rules.', 'IRCTC does not issue duplicates; a duplicate Tatkal ticket needs full fare and is only for exceptional cases.'),
  [S_TC, S_TATS]))

# 5 ---------------- group booking
G.append(('/guides/group-booking-train-tickets/',
  'Group booking of train tickets on IRCTC: what is allowed',
  'IRCTC says bulk booking for families and groups is not available on its portal. The limits per booking, the party ticket refund rule and how groups can order food.',
  'Group booking', 'Group booking of train tickets on IRCTC: what is allowed',
  'Booking for a big family or a group is limited by how many people one booking can hold. This guide lists the limits IRCTC publishes and the one service that does take group orders.',
  'The limits on booking for a group and the group order for food.', '''
<h2>IRCTC does not offer bulk booking</h2>
<p>IRCTC's Terms list "bulk booking for families and groups" among the services that are <b>not</b> available on its portal. A group has to book through ordinary e-ticket bookings.</p>
<h2>How many can go on one booking</h2>
''' + ul('A maximum of six berths or seats at a time for a journey between any two stations on the train, subject to the distance restrictions in force.', 'A maximum of four passengers per PNR on a Tatkal e-ticket.') + '''
<p>A group of more than six therefore needs more than one booking. For the number of tickets one user ID can book in a month, see our ''' + link('/guides/irctc-booking-limits-and-timings/', 'booking limits guide') + '''. Keep in mind that IRCTC says it may deactivate IDs and cancel tickets if a person uses several IDs.</p>
<h2>Seats together are not guaranteed</h2>
<p>IRCTC says berths and seats are allotted by the allocation logic of the Railway reservation system, and that it does not guarantee a berth or seat of your choice. A group booked as several tickets may therefore not sit together. The pages we read do not describe a way to request this.</p>
<h2>A party ticket with mixed status</h2>
<p>If a ticket for more than one passenger has some passengers confirmed and others on RAC or the waiting list, IRCTC's cancellation page says the confirmed passengers get a full refund less clerkage if the ticket is cancelled, or an online TDR is filed, for all the passengers up to 30 minutes before departure. See our ''' + link('/guides/cancel-irctc-e-ticket/', 'cancellation guide') + '''.</p>
<h2>Food for a group</h2>
<p>IRCTC eCatering says passengers travelling in a group of 15 or more can request its group order service for breakfast, lunch or dinner, with prices discussed with them. It warns about unauthorised suppliers who claim to be linked to IRCTC eCatering when they are not. See our ''' + link('/guides/train-food-irctc-ecatering/', 'train food guide') + '''.</p>
<h2>In short</h2>
''' + ul('No bulk booking on IRCTC; split a group into bookings of up to six.', 'Seats together are not guaranteed.', 'Groups of 15 or more can ask IRCTC eCatering for a group food order.'),
  [S_TC, S_CAN, S_ECAT]))

# 6 ---------------- food
G.append(('/guides/train-food-irctc-ecatering/',
  'Food on a train: IRCTC eCatering and how to complain',
  'How to order food to your seat with IRCTC eCatering using your PNR, what happens to the order if the ticket is cancelled, and where to complain about train food.',
  'Food on a train', 'Food on a train: IRCTC eCatering and how to complain',
  'IRCTC runs an official service for ordering food to your seat at a station on your route. This guide covers how it works and where to send a complaint about food.',
  'Ordering food with your PNR and complaining about train food.', '''
<h2>Ordering with IRCTC eCatering</h2>
<p>IRCTC eCatering says you enter your PNR, view the restaurants and food available for your journey, place the order and pay online or pay on delivery, and the food is delivered at the station you choose. You can order on the eCatering website or on its Food on Track app. </p>
<p>IRCTC eCatering says it delivers at over 300 railway stations. Check the station list on its site for your route.</p>
<h2>Other ways to order</h2>
''' + ul('Call <b>1323</b>.', 'WhatsApp: IRCTC eCatering says it has a dedicated business WhatsApp number, +91-8750001323, for orders.', 'Groups of 15 or more can ask for its group order service.') + '''
<p>IRCTC eCatering warns about unauthorised suppliers who claim to be linked to it. Use the official website or the Food on Track app.</p>
<h2>If your ticket is cancelled</h2>
<p>IRCTC eCatering lists automatic cancellation of an order if the PNR gets cancelled as one of the benefits of ordering through it.</p>
<h2>Meals served by the railway</h2>
<p>Indian Railways publishes catering charges for Rajdhani, Shatabdi and Duronto Express trains, with a revised tariff for tea or coffee, breakfast and standard meals. Check the tariff on the <a href="https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=CateringCharge.html" rel="noopener">Indian Railways catering charges page</a>, as the figures are shown there.</p>
<p>IRCTC lists these menu rates for standard items, one rate for food bought at a station and one for food served in the train.</p>
''' + table(['Item','At station','In train'], [['Tea (standard)','&#8377;5','&#8377;5'],['Tea with tea bag, or instant coffee','&#8377;10','&#8377;10'],['Vegetarian breakfast','&#8377;35','&#8377;40'],['Non-vegetarian breakfast (egg omelette)','&#8377;45','&#8377;50'],['Vegetarian standard meal','&#8377;70','&#8377;80'],['Egg curry meal','&#8377;80','&#8377;90'],['Chicken curry meal','&#8377;120','&#8377;130']]) + '''
<p>The Press Information Bureau (15 November 2019) also lists a Janta meal at &#8377;20, a snack meal at &#8377;50 and biryani at &#8377;80 (vegetarian), &#8377;90 (egg) and &#8377;110 (chicken). Catering on Rajdhani, Shatabdi and Duronto Express trains is included in the ticket fare, so there is no separate rate for it. Rates can change, so confirm on the <a href="https://menurates.irctc.co.in/standared_meal.html" rel="noopener">IRCTC menu rate pages</a> or the ordering screen before you pay.</p>
<p style="display:flex;flex-wrap:wrap;align-items:center;gap:12px"><b>Order inside the ClearBerth app for something extra.</b> <a class="btn sm" href="/#get-app">Get the app</a></p>
<h2>How to complain about food</h2>
''' + ul('Call the toll-free number <b>1800111321</b>.', 'Ask for the complaint book, which Indian Railways says is available with the TTE, the Pantry Car Manager and the Station Manager.', 'For any other complaint, Indian Railways gives its customer care site, <b>customercare.indianrailways.gov.in</b>.') + '''
<p>For a wider complaint such as cleanliness or staff, see our ''' + link('/guides/train-complaint-railmadad-139/', 'RailMadad and 139 guide') + '''.</p>
<h2>In short</h2>
''' + ul('Use the official IRCTC eCatering site or app with your PNR.', 'The order cancels automatically if the PNR is cancelled.', 'Food complaints: 1800111321 or the complaint book.'),
  [S_ECAT, S_CATIR, S_MR_M, S_MR_B, S_MR_V, S_PIB_FOOD]))

# 7 ---------------- class codes
G.append(('/guides/train-class-codes-explained/',
  'Train class codes: SL, 3A, 2A, 1A, CC, EC, 3E and 2S',
  'What the class codes on an Indian Railways ticket stand for, which classes are AC and non-AC, and how the official pages name each class.',
  'Class codes', 'Train class codes: SL, 3A, 2A, 1A, CC, EC, 3E and 2S',
  'Your ticket shows a short class code. This guide lists the codes used on IRCTC and Indian Railways pages and the full name each page gives.',
  'What SL, 3A, 2A, 1A, CC, EC, 3E and 2S mean.', '''
<h2>AC and non-AC classes</h2>
<p>IRCTC's Terms group the classes this way for Tatkal booking: the AC classes are <b>2A, 3A, CC, EC and 3E</b>, and the non-AC classes are <b>SL, FC and 2S</b>. First Class Air-conditioned is written <b>1A</b> in the same Terms.</p>
<h2>What each code stands for</h2>
''' + table(['Code', 'Class name used by Indian Railways and IRCTC', 'Where it is named'], [
  ['1A', 'First Class Air-conditioned (AC First Class)', 'IRCTC Terms; IRCTC cancellation page'],
  ['2A', 'AC 2 Tier (2AC)', 'IRCTC cancellation page; PIB'],
  ['3A', 'AC 3 Tier (3AC)', 'IRCTC cancellation page; PIB'],
  ['3E', 'AC 3 Economy', 'IRCTC cancellation page; PIB'],
  ['CC', 'AC Chair Car', 'IRCTC cancellation page; PIB'],
  ['EC', 'Executive Class', 'IRCTC cancellation page; Tatkal scheme page'],
  ['FC', 'First Class', 'IRCTC cancellation page'],
  ['SL', 'Sleeper', 'IRCTC cancellation page; Tatkal scheme page'],
  ['2S', 'Second Sitting (reserved)', 'Tatkal scheme page; PIB'],
]) + '''
<p>Some official pages write the AC classes as 2AC and 3AC and others as 2A and 3A. They are the same classes.</p>
<h2>Things the class decides</h2>
''' + ul('<b>Cancellation charges.</b> The flat minimum is set by class. IRCTC lists ' + R + '240 for AC First Class/Executive Class, ' + R + '200 for AC 2 Tier/First Class, ' + R + '180 for AC 3 Tier/AC Chair Car/AC 3 Economy, ' + R + '120 for Sleeper and ' + R + '60 for Second Class. See our ' + link('/guides/cancel-irctc-e-ticket/', 'cancellation guide') + '.',
         '<b>Tatkal.</b> IRCTC says Tatkal berths are earmarked in all important trains in different classes except 1A. AC Tatkal opens at 10:00 and non-AC Tatkal at 11:00 on the day before departure. See our ' + link('/guides/tatkal-ticket-booking-rules/', 'Tatkal guide') + '.',
         '<b>Ladies quota.</b> IRCTC says it is generally earmarked in Sleeper (SL) and Second Sitting (2S).',
         '<b>Lower berths.</b> The Ministry of Railways says lower berths are earmarked for senior citizens, women of 45 years and above and pregnant women in Sleeper, 3AC and 2AC. See our ' + link('/guides/lower-berth-and-ladies-quota-rules/', 'lower berth guide') + '.',
         '<b>Seats for persons with disabilities.</b> Four berths in Sleeper and in 3AC/3E, and four seats in 2S or CC on trains with more than two coaches of that class.') + '''
<h2>In short</h2>
''' + ul('AC classes: 1A, 2A, 3A, 3E, CC, EC. Non-AC: SL, FC, 2S.', 'The class sets the cancellation charge and whether Tatkal is available.'),
  [S_TC, S_CAN, S_TATS, S_PIB_2026]))

# 8 ---------------- concessions students & patients
G.append(('/guides/train-concessions-students-and-patients/',
  'Railway concessions for students and patients',
  'The student and patient categories that get a railway fare concession, as published by the Ministry of Railways, and why IRCTC e-tickets do not carry student concessions.',
  'Student and patient concessions', 'Railway concessions for students and patients',
  'Indian Railways gives fare concessions to some students and to patients with listed illnesses. The list below follows the Ministry of Railways\' published table, so check the current terms before you travel.',
  'Which students and patients get a railway fare concession.', '''
<h2>What the Ministry says</h2>
<p>A Ministry of Railways release of 2 December 2016 lists 53 categories of passengers who get a concession of 25% to 100%. In a Lok Sabha reply on 11 March 2026 the Ministry said concessions continue for 4 categories of persons with disabilities, 11 categories of patients and 8 categories of students. The table below is the 2016 list. The categories and percentages can change, so ask a reservation counter for the current terms.</p>
<h2>Can you book these online on IRCTC?</h2>
<p>IRCTC's FAQ says the student concession facility is not available for e-tickets. IRCTC's Terms list the concessions available on its platform as Divyaang, Journalist, Senior Citizen and Railway Pass, and add that concessions are governed by Indian Railways' instructions and may change. Student and patient concessions are not on that list. The pages we read do not say how to claim them, so ask at a Railway reservation counter. For the ones on IRCTC, see our ''' + link('/guides/senior-citizen-train-concession/', 'senior citizen guide') + ' and ' + link('/guides/divyangjan-railway-concession/', 'Divyangjan guide') + '''.</p>
<h2>Students (2016 table)</h2>
''' + table(['Category', 'Concession listed'], [
  ['Students going to hometown and on educational tours', 'General category: 50% in 2nd and Sleeper class, and 50% in MST/QST. SC/ST: 75% in 2nd and Sleeper, and 75% in MST/QST.'],
  ['Girls up to graduation and boys up to 12th standard (including Madrasa students), between home and school', 'Free second class MST'],
  ['Students of Government schools in rural areas, study tour once a year', '75% in 2nd class'],
  ['Girls of Government schools in rural areas, for national level medical, engineering and similar entrance exams', '75% in 2nd class'],
  ['Students appearing in the main written examination of UPSC and Central Staff Selection Commissions', '50% in 2nd class'],
  ['Foreign students studying in India, going to Government of India camps and seminars and places of importance in vacations', '50% in 2nd and Sleeper class'],
  ['Research scholars up to the age of 35, for research-related journeys', '50% in 2nd and Sleeper class'],
  ['Cadets and Marine Engineer apprentices in Mercantile Marine training, between home and training ship', '50% in 2nd and Sleeper class'],
]) + '''
<p>The 2016 table also lists students and non-students participating in work camps (25% in 2nd and Sleeper), under a separate line.</p>
<h2>Patients (2016 table)</h2>
<p>The Ministry lists these categories of patients, travelling alone or with an escort for treatment or periodic check-up (kidney patients for the transplant operation or dialysis, heart patients for heart surgery):</p>
''' + ul('Cancer patients', 'Thalassemia patients', 'Heart patients (for heart surgery)', 'Kidney patients (for transplant operation or dialysis)', 'Haemophilia patients (severe and moderate)', 'TB or lupus vulgaris patients', 'Non-infectious leprosy patients', 'AIDS patients, for treatment at nominated ART centres', 'Ostomy patients', 'Sickle cell anaemia patients', 'Aplastic anaemia patients') + '''
<p>As one example from the table, a cancer patient gets 75% in 2nd, 1st class and AC Chair Car, 100% in Sleeper and 3AC, and 50% in 1AC and 2AC, and one escort gets the same concession, except that in Sleeper and 3AC the escort gets 75%. The percentages for the other illnesses differ by class, so read the full table on the PIB page below.</p>
<h2>In short</h2>
''' + ul('Student and patient concessions exist, but IRCTC e-tickets do not carry student concessions.', 'The percentages are in the Ministry of Railways table linked below; confirm the current terms at a counter.'),
  [S_PIB_CONC, S_PIB_2026, S_FAQ, S_TC]))

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
