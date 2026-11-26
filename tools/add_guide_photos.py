#!/usr/bin/env python3
"""Owner's photos on the 17 guides made by build_guides_batch3.py (20 Nov 2026) and the 8 made by
build_guides_batch4.py (26 Nov 2026; images from the owner's Downloads).
Puts a <!--ghero--> block under the "Last checked" line and makes the photo the og:image.
Images: /shots/guide-<slug>.webp (1200 wide) and -m.webp (720 wide), made from the owner's files.
Safe to run twice (replaces its own block). Re-run after build_guides_batch3.py:
  python3 tools/add_guide_photos.py"""
import html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = '.ghero{margin:18px 0 22px}.ghero img{width:100%;height:auto;border-radius:18px;display:block}.ghero figcaption{font-size:14px;color:#5A6180;margin-top:8px}'

# slug: (alt text, caption) -- captions state facts from the guide itself
P = {
 'id-proof-for-train-travel': ('A woman in a train coach holds up her phone with the e-ticket and an ID card, with the ticket checker behind her',
   'One passenger on the ticket must show an original ID during the journey.'),
 'change-boarding-station-irctc': ('A man checks his phone in a taxi as it reaches a small railway station at dusk',
   'Since 1 April 2026 the boarding station can be changed up to the second reservation chart.'),
 'transfer-train-ticket-change-name': ('A father hands a printed train ticket to his son across the kitchen table',
   'A confirmed ticket can be moved to a listed family member through a reservation office, once only.'),
 'child-train-ticket-rules': ('A mother and her young son by the window of a train coach, passing green fields',
   'Under 5 travels free without a berth; from 5 to 11 you choose a berth at full fare, or no berth at half fare.'),
 'train-luggage-allowance-rules': ('A couple with suitcases boarding an AC coach on a busy platform',
   'Free allowance: 70 kg in AC First, 50 kg in AC 2-tier, 40 kg in AC 3-tier, Chair Car and Sleeper, 35 kg in Second Class.'),
 'travel-with-dog-on-train': ('A couple with a labrador sitting in a first-class train compartment',
   "A dog can travel in the brake van dog box, or in AC First or First Class with fellow passengers' consent."),
 'railway-quota-codes-explained': ('A woman checks train booking options on her phone at a table with tea and a notebook',
   'The quota code on a ticket shows which quota the berth was booked under.'),
 'rac-ticket-meaning-rules': ('A young man and an older man sitting together on a side lower berth in an AC coach',
   'An RAC passenger can travel, and may share a berth until a confirmed passenger cancels.'),
 'current-booking-after-chart': ('A man walks through a busy station concourse checking his phone, with the departure board behind',
   'After the chart is prepared, empty berths can still be booked on IRCTC as current booking.'),
 'foreign-tourist-quota-irctc': ('Two backpackers on an Indian railway platform, one holding a passport',
   'Foreign tourists and NRIs can book up to 365 days ahead under the Foreign Tourist quota.'),
 'e-ticket-on-phone-sms-printout': ('A ticket checker checks a passenger\'s e-ticket on her phone inside a train coach',
   'A printout, a screenshot or the booking SMS all work, with an original ID.'),
 'irctc-booking-limits-and-timings': ('A family at home in the evening planning a train trip on a laptop, with a calendar on the wall',
   'An IRCTC user can book 12 tickets a month, or 24 with Aadhaar verification.'),
 'senior-citizen-train-concession': ('An elderly couple sitting on lower berths in a train coach',
   'The senior citizen fare concession was withdrawn in 2020; lower berth priority continues.'),
 'divyangjan-railway-concession': ('A railway porter and an escort help a man in a wheelchair board a train',
   'Four categories of persons with disabilities get a fare concession, and one escort gets the same.'),
 'train-complaint-railmadad-139': ('A woman on a train speaks on her phone, looking out of the window at dusk',
   'For the journey, call 139 or use RailMadad; for an IRCTC booking, call 14646.'),
 'irctc-travel-insurance': ('A young couple booking a train journey on a laptop at home, with bags packed by the door',
   'Optional IRCTC travel insurance costs 45 paise per passenger.'),
 'luggage-stolen-on-train-complaint': ('A passenger in a sleeper coach at night reporting a theft to a railway police officer who writes on a form',
   'Ask the TTE, guard, coach attendant or GRP escort for the FIR form; you do not need to break your journey.'),
 'irctc-account-and-passenger-list-help': ('A woman at a home desk looks at her phone, with a laptop and a cup of tea beside her',
   'IRCTC allows one user registration per email ID and mobile number, and advises a master passenger list of at most six.'),
 'book-train-ticket-for-someone-else': ('A man and his elderly mother sit on a sofa and look at a phone together',
   'You can enter any passenger\'s details on the booking page; one passenger on the e-ticket must show an original ID.'),
 'irctc-payment-failed-money-deducted': ('A man in a hallway looks worried at his phone, one hand on his head, a bag at his feet',
   'If no ticket was issued, IRCTC says the full amount is credited back to the account you paid from.'),
 'lost-or-torn-train-ticket-duplicate': ('A woman on a railway platform searches her handbag, with a suitcase beside her and a train behind',
   'IRCTC does not issue duplicates for lost or torn tickets, but an e-ticket can be shown again from Booked Ticket History.'),
 'group-booking-train-tickets': ('A group of relatives and friends with bags talk and smile on a railway platform beside a train',
   'One booking holds at most six berths or seats, and four passengers on a Tatkal e-ticket, so a bigger group needs more than one booking.'),
 'train-food-irctc-ecatering': ('A family in a train compartment, a father passes a plate of food to his daughter by the window',
   'IRCTC eCatering takes orders against your PNR, for delivery at the station you choose, on its website or the Food on Track app.'),
 'train-class-codes-explained': ('The inside of a train carriage with rows of seats and a passenger walking down the aisle, with the text SL 3A 2A 1A CC EC 3E 2S, Class codes explained',
   'In IRCTC\'s Terms for Tatkal, the AC classes are 2A, 3A, CC, EC and 3E, and the non-AC classes are SL, FC and 2S.'),
 'train-concessions-students-and-patients': ('A young woman with a backpack and an older woman with a folder sit facing each other by a train window',
   'IRCTC says the student concession is not available on e-tickets; ask at a Railway reservation counter.'),
}


def main():
    import sys
    only = set(sys.argv[1:])  # optional: only these slugs
    n = 0
    for slug, (alt, cap) in P.items():
        if only and slug not in only:
            continue
        p = os.path.join(ROOT, 'guides', slug, 'index.html')
        img = os.path.join(ROOT, 'shots', 'guide-%s.webp' % slug)
        if not (os.path.exists(p) and os.path.exists(img)):
            print('missing', slug); continue
        h = open(p, encoding='utf-8').read()
        from PIL import Image
        W, H = Image.open(img).size
        fig = ('<!--ghero--><figure class="ghero"><img src="/shots/guide-{s}.webp" srcset="/shots/guide-{s}-m.webp 720w, '
               '/shots/guide-{s}.webp 1200w" sizes="(max-width:760px) 100vw, 720px" alt="{a}" width="{w}" height="{h}" '
               'fetchpriority="high"><figcaption>{c}</figcaption></figure><!--/ghero-->').format(
            s=slug, a=html.escape(alt, quote=True), w=W, h=H, c=html.escape(cap))
        h = re.sub(r'<!--ghero-->.*?<!--/ghero-->\n?', '', h, flags=re.S)
        h, k = re.subn(r'(<p class="meta">.*?</p>\n)', lambda m: m.group(1) + fig + '\n', h, count=1, flags=re.S)
        assert k == 1, slug
        if '.ghero{' not in h:
            h = h.replace('</style>', CSS + '</style>', 1)
        h = re.sub(r'<meta property="og:image" content="[^"]*">',
                   '<meta property="og:image" content="https://clearberth.app/shots/guide-%s.webp">' % slug, h, count=1)
        open(p, 'w', encoding='utf-8').write(h)
        n += 1
    print('photos on', n, 'guides')


if __name__ == '__main__':
    main()
