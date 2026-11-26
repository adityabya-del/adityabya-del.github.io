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
        print('add', bid)
        if write: open(p, 'w', encoding='utf-8').write(h)

main('--write' in sys.argv)
