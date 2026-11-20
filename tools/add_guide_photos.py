#!/usr/bin/env python3
"""Owner's photos on the 17 guides made by build_guides_batch3.py (20 Nov 2026).
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
}


def main():
    n = 0
    for slug, (alt, cap) in P.items():
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
