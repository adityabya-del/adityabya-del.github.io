#!/usr/bin/env python3
"""Adds extra official facts to guides (sections found missing in the 27 Nov 2026 review).
Run after any rebuild of the guides:  python3 tools/add_guide_facts.py --write
Safe to run twice (each block has a <!--gf:id--> marker)."""
import re, sys, os
R = '&#8377;'
A = 'style="text-decoration:underline" '
CHECKED = '27 November 2026'
IRCTC_REF = ('IRCTC: Refund rules and TDR filing, effective 12 November 2015', 'https://contents.irctc.co.in/en/REFUND%20RULES%20wef%2012-Nov-15.pdf')
IR_REF = ('Indian Railways: Refund rules', 'https://www.indianrail.gov.in/refund_Rules.html')
IRCTC_PET = ('IRCTC: Online ticket booking of dogs and cats', 'https://contents.irctc.co.in/en/PetBookingInTrains.pdf')
PIB_CHILD22 = ('PIB: No change in the rule for booking tickets for children', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=1852502&reg=48&lang=2')
PIB_139A = ('PIB, 8 March 2021: integrated RailMadad helpline 139', 'https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1703201&reg=48&lang=2')
PIB_139B = ('PIB, 6 August 2021: RailMadad, one-stop solution for grievance, enquiry and assistance', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=1743174')
WR_139 = ('Western Railway: Helpline numbers', 'https://wr.indianrailways.gov.in/view_section.jsp?lang=0&id=0%2C7%2C570')
IR_CONC = ('Indian Railways: Concession rules', 'https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=conc_Rules.html')
RB_CONC = ('Railway Board: General rules for concession', 'https://indianrailways.gov.in/railwayboard/uploads/directorate/traffic_comm/Comm_Cir_2025/ANNEXURE%204%20%20%20%20%20%20%20General%20Rules%20for%20Concession.pdf')


PIB_REFORM = ('PIB, 24 March 2026: Indian Railways announces five new reforms under Reform Express', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2244597&reg=48&lang=2')
BLOCKS = [
 ('cancel-rac', 'cancel-irctc-e-ticket', '<h2>In short</h2>',
  '<h2>Waitlisted and RAC tickets</h2><p>IRCTC\'s refund rules (12 November 2015) say a waitlisted or RAC ticket can be cancelled up to 30 minutes before the scheduled departure of the train, with clerkage deducted: %s60 per passenger, plus GST for AC classes. After that, no refund is given on an RAC or waitlisted ticket.</p>'
  '<h2>GST and the Vande Bharat Sleeper Express</h2><p>IRCTC\'s refund rules add GST to the cancellation charges for AC classes; for example, the AC Chair Car and AC 3 Tier flat charge is written as "Rs.180 plus GST". For the Vande Bharat Sleeper Express the rules set an eight-hour limit: a ticket cancelled less than eight hours before departure gets no refund, and a ticket that is neither cancelled nor has a TDR filed online up to eight hours before departure gets no refund.</p>' % R,
  [IRCTC_REF, IR_REF]),
 ('dog-irctc', 'travel-with-dog-on-train', '<h2>In short</h2>',
  '<h2>Booking a dog or cat on IRCTC</h2><p>IRCTC\'s terms for online pet booking add these points:</p><ul>'
  '<li>Dogs and cats travelling with their owners can be carried in First AC or First Class only when the entire 4-berth cabin or 2-berth coupe is allotted to a single PNR. A request for the cabin or coupe can be made at the divisional railway manager\'s or the General Manager\'s office.</li>'
  '<li>Puppies or kittens that can be carried in a basket can be carried by the owner in any class after paying the usual booking charges.</li>'
  '<li>Pet booking can be done on the IRCTC e-ticketing website, for both e-tickets and counter tickets. It is allowed only after the first chart is prepared and up to the time the final chart is prepared.</li>'
  '<li>Booking needs a login on the Railway Parcel website with a mobile OTP and email ID, then the PNR and an ID card number.</li>'
  '<li>No refund of the freight charges is given on the luggage ticket, including when the PNR is cancelled, the train is cancelled or the train runs late.</li></ul>'
  '<p>These terms and the luggage rules above describe travel in First Class differently, so ask at the parcel or luggage office of your station before you travel.</p>',
  [IRCTC_PET]),
 ('child-under5', 'child-train-ticket-rules', "<h2>IRCTC's own trains</h2>",
  '<h2>Under 5: a berth is optional</h2><p>A Ministry of Railways release says Indian Railways has not changed the booking rule for children. Children below 5 travel free if no berth is booked, and passengers have the option to buy a ticket and book a berth for a child under 5 if they want. The release cites a Ministry of Railways circular dated 6 March 2020.</p>',
  [PIB_CHILD22]),
 ('rm-139', 'train-complaint-railmadad-139', '<h2>Emergencies on the train</h2>',
  '<h2>What helpline 139 offers</h2><ul>'
  '<li>139 is available round the clock in 12 languages, and it replaced more than 15 earlier helplines. The security helpline 182 was merged into 139 from 1 April 2021.</li>'
  '<li>Menu of 139: press 1 for security and medical assistance, which connects straight to a call centre executive; press 2 for enquiries (PNR status, train running, fares, wheelchair booking, meal booking and more); press 3 for catering complaints; press 4 for general complaints; press 5 for bribery and corruption; press 9 for the status of your complaint.</li>'
  '<li>Passengers without a smartphone can call 139 and talk to an executive, who helps lodge the grievance.</li></ul>',
  [PIB_139A, PIB_139B, WR_139]),
 ('conc-general', 'train-concessions-students-and-patients', '<h2>Students (2016 table)</h2>',
  '<h2>General rules for concessions</h2><ul>'
  '<li>The concession is given on the basic fare only. No concession is given on other charges such as the superfast surcharge or the reservation fee.</li>'
  '<li>It is subject to a minimum distance of 300 km, with exceptions for some categories, including students.</li>'
  '<li>No concession is given for a journey whose cost is borne by the Central or a State Government, a local authority, a statutory body, a corporation, a Government undertaking or a university. Students taking part in tournaments held or recognised by schools or universities are eligible.</li></ul>',
  [IR_CONC, RB_CONC]),
 ('lug-brake', 'train-luggage-allowance-rules', '<h2>Suitcase size</h2>',
  '<h2>Luggage in the brake van</h2><p>Indian Railways\' luggage rules say there is no restriction on the quantity or type (personal or merchandise) of luggage offered for booking in the brake van of passenger trains.</p>',
  []),
]


PIB_TATKAL_A = ('PIB, December 2025: Indian Railways strengthens ticket reservation system with cyber security', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2202197&reg=3&lang=2')
PIB_TATKAL_B = ('PIB: RailOne app and Aadhaar-based OTP for Tatkal', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2287719&reg=48&lang=2')
ER_NAME = ('Eastern Railway: Change in name of passenger holding confirmed reservation', 'https://er.indianrailways.gov.in/view_section.jsp?fontColor=black&backgroundColor=LIGHTSTEELBLUE&lang=0&id=0,2,279')
SER_NAME = ('South Eastern Railway: Change of name of passengers on confirmed tickets', 'https://ser.indianrailways.gov.in/view_section.jsp?lang=0&id=0,2,406,453,564,1155,1183')
PIB_VIK_A = ('PIB: More than 43,000 passengers provided accommodation under Vikalp during 2022-23', 'https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1910035')
PIB_VIK_B = ('PIB, 2017: Alternate Train Accommodation Scheme (VIKALP)', 'https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1485240')

BLOCKS += [
 ('aadhaar-rollout', 'aadhaar-train-ticket-booking-rules', '<h2>General reserved tickets</h2>',
  '<h2>The OTP is being rolled out train by train</h2><p>Later releases from the Ministry of Railways say the Aadhaar-based OTP for online Tatkal booking was introduced in a phased manner, and was working in 322 trains as on 4 December 2025. The OTP for Tatkal bookings at reservation counters was in 211 trains on the same date. A later release still describes the online OTP as introduced on selected trains.</p>',
  [PIB_TATKAL_A, PIB_TATKAL_B]),
 ('name-others', 'transfer-train-ticket-change-name', '<h2>What to take to the counter</h2>',
  '<h2>Other cases on Railway pages</h2><p>Indian Railways zone pages list more cases than the two above. A reservation can also be transferred for students of a recognised educational institution, on a request from the head of the institution, and from one National Cadet Corps cadet to another, on a written request by the head of the group made 24 hours before the scheduled departure.</p>',
  [ER_NAME, SER_NAME]),
 ('vikalp-later', 'vikalp-alternate-trains', '<h2>Check your PNR twice</h2>',
  '<h2>Opting in later, and boarding the original train</h2><p>A Press Information Bureau release says passengers who did not opt for VIKALP at the time of booking can also opt for it up to 24 hours before the scheduled departure. Waitlisted passengers who are allotted alternate accommodation are not allowed to board the original train; if found travelling, they are treated as travelling without a ticket and charged accordingly.</p>',
  [PIB_VIK_A, PIB_VIK_B]),
]


PIB_REFUND23 = ('PIB: Refund of cancelled tickets', 'https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1945094&reg=48&lang=2')
PIB_LIMIT_A = ('PIB: Various measures for fast, safe and transparent e-ticketing', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=1896104&reg=48&lang=2')
PIB_LIMIT_B = ('PIB: Opening of reservation centres round the clock', 'https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=1602083&reg=3&lang=2')
IR_CONC2 = ('Indian Railways: Lost, misplaced, torn or mutilated tickets (refund rules)', 'https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=conc_Rules.html')
SER_LOST = ('South Eastern Railway: Lost, misplaced, torn or mutilated tickets', 'https://ser.indianrailways.gov.in/view_section.jsp?lang=0&id=0,2,406,1611,1612,1624,1650')
WCR_DUP = ('West Central Railway: Duplicate ticket', 'https://wcr.indianrailways.gov.in/view_section.jsp?lang=0&id=0,2,393,395,856')
IRCTC_TC2 = ('IRCTC: Terms and Conditions (user registration)', 'https://www.pmf.irctc.co.in/cn/TermsAndConditions.html')
RB_ADV = ('Railway Board: Advance reservation through internet', 'https://indianrailways.gov.in/railwayboard/uploads/directorate/coaching/pdf/AdvanceReservation_Internet.pdf')
PIB_SMS12 = ('PIB: SMS sent by IRCTC accepted on par with the ERS', 'https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=80101&reg=3&lang=2')

BLOCKS += [
 ('pay-days', 'irctc-payment-failed-money-deducted', '<h2>Do not pay twice for the same ticket</h2>',
  '<h2>What the Ministry of Railways says about timing</h2><p>A Ministry of Railways release says that if money is debited and the ticket is not booked, IRCTC starts an automatic refund on the following day, and the refund is advised to the payment gateway or bank. It then takes 3 to 4 business days for net banking, wallet or cash card payments, and 6 to 7 business days for credit or debit card payments.</p>',
  [PIB_REFUND23]),
 ('limits-checks', 'irctc-booking-limits-and-timings', '<h2>One account per person</h2>',
  '<h2>Checks while you book</h2><ul><li>Press Information Bureau releases say individual users are logged out if their enquiries exceed 25 per session during the opening hours of 08:00 to 12:00.</li><li>Checks are applied on the minimum time needed to enter the passenger details and the CAPTCHA, and a ticket cannot be booked before 35 seconds.</li></ul>',
  [PIB_LIMIT_A, PIB_LIMIT_B]),
 ('acct-rpf', 'irctc-account-and-passenger-list-help', '<h2>Who to contact</h2>',
  '<h2>Multiple user IDs</h2><p>IRCTC\'s Terms and Conditions say that if a user registers more than one user ID, or books tickets on such multiple IDs, IRCTC can deactivate all those registrations, refer the case to the Railway Protection Force for prosecution under the relevant section of law, and cancel any or all tickets booked with them.</p>',
  [IRCTC_TC2]),
 ('lost-counter', 'lost-or-torn-train-ticket-duplicate', '<h2>Tatkal tickets</h2>',
  '<h2>Paper tickets: what the Railway rules say</h2><ul>'
  '<li>No refund of fare is given for a lost or misplaced ticket. A refund is given for a torn or mutilated ticket after the due cancellation charge, if its genuineness can be verified from the ticket.</li>'
  '<li>If a reserved or RAC ticket is lost, misplaced, torn or mutilated and a duplicate is sought before the reservation chart is prepared, the station master issues a duplicate ticket on collection of the clerkage charge per passenger.</li>'
  '<li>After the chart is prepared, a duplicate for a lost or misplaced reserved ticket is issued on collection of 50% of the total fare. For a torn or mutilated reserved or RAC ticket it is 25% of the total fare.</li>'
  '<li>Duplicate tickets are not issued for RAC tickets after the chart is prepared.</li></ul>',
  [IR_CONC2, SER_LOST, WCR_DUP]),
 ('cur-chart', 'current-booking-after-chart', "<h2>IRCTC's own trains</h2>",
  '<h2>When the chart is prepared</h2><p>The Railway Board\'s booking page says reservation charts are normally prepared 4 hours before the departure of the train from its originating station. A Ministry of Railways release of 24 March 2026 says charts now happen 9 to 18 hours before departure instead of 4 hours. Current booking starts after the chart.</p>',
  [RB_ADV, PIB_REFORM]),
 ('id-tatkal', 'id-proof-for-train-travel', '<h2>One ID covers the whole ticket</h2>',
  '<h2>Tatkal tickets, and what if you cannot show the ID</h2><p>The Railway Board says that for a Tatkal ticket, the same identity card that was mentioned at the time of booking has to be presented during the journey. IRCTC says that if the prescribed ID is not shown in original, the passengers are treated as travelling without a ticket and dealt with as per Railway rules.</p>',
  [RB_ADV]),
 ('sms-2012', 'e-ticket-on-phone-sms-printout', '<h2>The ID still matters</h2>',
  '<h2>Since when SMS is accepted</h2><p>A Ministry of Railways release says the SMS sent by IRCTC was accepted on par with the Electronic Reservation Slip from 1 February 2012. It lists a valid authority to travel as the ERS, SMS or VRM along with a confirmed or RAC reservation, a valid ID proof, and the passenger\'s name on the chart.</p>',
  [PIB_SMS12]),
]


BLOCKS += [
 ('reform-cancel', 'cancel-irctc-e-ticket', '<h2>Can you cancel an e-ticket online?</h2>',
  '<div class="note"><b>Newer announcement.</b> A Ministry of Railways release of 24 March 2026 says the earlier cancellation windows of 48, 12 and 4 hours before departure have been revised to 72, 24 and 8 hours, linked to reservation charts now being prepared 9 to 18 hours before departure instead of 4 hours. It also says the requirement to file a TDR for e-tickets has been removed and refunds will be processed automatically on cancellation. The release gives no effective date, and the IRCTC cancellation page we read still lists the 48, 12 and 4 hour windows below. Check the timings IRCTC shows when you cancel.</div>',
  [PIB_REFORM]),
 ('reform-tdr', 'train-cancelled-diverted-late-refund-tdr', '<h2>If the railway cancels your train</h2>',
  '<div class="note"><b>Newer announcement.</b> A Ministry of Railways release of 24 March 2026 says the requirement to file a TDR for e-tickets has been removed and refunds will be processed automatically on cancellation. It gives no effective date. The IRCTC refund rules this guide follows are dated 12 November 2015, so check what IRCTC shows for your ticket.</div>',
  [PIB_REFORM]),
 ('reform-chart', 'waitlisted-e-ticket-after-chart', '<h2>When is the chart prepared?</h2>',
  '<div class="note"><b>Newer announcement.</b> A Ministry of Railways release of 24 March 2026 says reservation charts are now prepared 9 to 18 hours before departure instead of 4 hours. The IRCTC pages we read do not state a time.</div>',
  [PIB_REFORM]),
 ('reform-board', 'change-boarding-station-irctc', '<h2>How to change it on IRCTC</h2>',
  '<div class="note"><b>Newer announcement.</b> A Ministry of Railways release of 24 March 2026 says passengers will be able to change their boarding station digitally up to 30 minutes before the train departs from its origin station, where earlier changes were allowed only before chart preparation. Its headline says "soon" and it gives no date. Check the time limit IRCTC shows when you change.</div>',
  [PIB_REFORM]),
]


IR_TATKAL = ('Indian Railways: Tatkal scheme', 'https://www.indianrail.gov.in/enquiry/StaticPages/StaticEnquiry.jsp?StaticPage=tatkal_Scheme.html')
PIB_QUOTA = ('PIB, 4 January 2019: categories of reservation quotas in Indian Railways', 'https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=187186&reg=48&lang=2')
PIB_SEC = ('PIB: Measures to improve safety and security in Railways', 'https://pib.gov.in/PressReleasePage.aspx?PRID=1657352')

BLOCKS += [
 ('tatkal-other', 'tatkal-ticket-booking-rules', '<h2>Questions people ask</h2>',
  '<h2>Other Tatkal rules</h2><ul>'
  '<li>A maximum of four passengers can be booked on one PNR for Tatkal tickets.</li>'
  '<li>Change of name is not permitted on bookings made under the Tatkal scheme.</li>'
  '<li>No duplicate Tatkal tickets are issued. They are issued only in exceptional cases, on payment of the full fare including the Tatkal charges.</li>'
  '<li>Premium Tatkal is a separate quota that the Ministry of Railways lists alongside Tatkal.</li></ul>',
  [IR_TATKAL, PIB_QUOTA]),
 ('quota-cancer', 'railway-quota-codes-explained', '<h2>In short</h2>',
  '<h2>Other quotas the Ministry lists</h2><p>A Ministry of Railways release of 4 January 2019 also lists a Cancer Patient quota, for cancer patients.</p>',
  [PIB_QUOTA]),
 ('stolen-zero', 'luggage-stolen-on-train-complaint', '<h2>At the station</h2>',
  '<h2>If the crime happened somewhere else</h2><p>A Ministry of Railways release says policing on the railways is handled by the Government Railway Police or the district police of each State. If the place where the crime happened is not in the jurisdiction of the police station where you report it, the case is registered as a Zero FIR and transferred to the Government Railway Police station that has jurisdiction.</p>',
  [PIB_SEC]),
]

def main(write):
    for bid, slug, anchor, html, srcs in BLOCKS:
        p = 'guides/%s/index.html' % slug
        h = open(p, encoding='utf-8').read()
        mark = '<!--gf:%s-->' % bid
        if mark in h:
            print('skip', bid); continue
        assert h.count(anchor) == 1, (bid, h.count(anchor))
        h = h.replace(anchor, mark + html + anchor)
        if srcs:
            i = h.find('<h2>Sources</h2>'); j = h.find('</ul>', i)
            add = ''.join('<li><a %shref="%s" rel="noopener">%s</a></li>' % (A, u.replace('&', '&amp;'), t) for t, u in srcs)
            h = h[:j] + add + h[j:]
        h = re.sub(r'Last checked: \d+ \w+ 2026', 'Last checked: ' + CHECKED, h, count=1)
        if slug == 'cancel-irctc-e-ticket':
            old = 'The cancellation page gives no separate refund rule for ordinary waitlisted tickets.'
            if old in h:
                h = h.replace(old, 'The cancellation page gives no separate rule for ordinary waitlisted tickets; the refund rules are in the next section.')
        if slug == 'irctc-payment-failed-money-deducted':
            h = h.replace('The pages we read do not give a number of days.', 'IRCTC\'s own pages give no number of days; the Ministry of Railways release below does.')
        print('add', bid)
        if write: open(p, 'w', encoding='utf-8').write(h)

main('--write' in sys.argv)
