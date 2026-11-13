#!/usr/bin/env python3
"""Add a regional section (photo + white box in the style of Amtrak's regional pages,
India map with the state highlighted, short text) to every STATION page whose station
is in Rajasthan, Uttar Pradesh, Odisha, West Bengal, Chhattisgarh or Kerala.
It goes at the very top, right under the breadcrumb, so the photo is visible when the page opens.

Station -> state: tools/_station_states.json (made by point-in-polygon of datameet
station coordinates against datameet state outlines, plus a few by-hand overrides).
Map: /shots/india-map.svg (state outlines, ids st-<state>, group in-all).

Photos: /shots/region-<slug>.jpg (desktop, white box baked in) and
/shots/region-<slug>-m.jpg (square crop for phones, box cropped out).
Map data: tools/_india_paths.svgfrag (Survey of India based state outlines, simplified).

Run:  python3 tools/add_region_sections.py --write      (--test = dry run)
Idempotent: it replaces the block between the two region markers if it exists.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
import json
STATES = json.loads((ROOT / "tools" / "_station_states.json").read_text())

# box = white rectangle baked into the 1920x1080 photo: x0, y0, x1, y1
REGIONS = [
    dict(slug="west-india", name="West India", state="Rajasthan", st="rajasthan",
         box=(103, 253, 796, 726),
         alt="A hill fort above a city in Rajasthan",
         text="Trains link Rajasthan&rsquo;s forts, palaces and desert cities with Delhi, Mumbai and Gujarat. "
              "Jaipur Jn lies on the main line between Delhi and Ahmedabad, and many long-distance trains stop there. "
              "Check a train&rsquo;s live status and its station-by-station timetable before you travel.",
         links=[("/station/jp/", "Trains at Jaipur Jn")]),
    dict(slug="north-india", name="North India", state="Uttar Pradesh", st="uttar-pradesh",
         box=(116, 272, 808, 737),
         alt="Temple town on the river bank at sunrise in Uttar Pradesh",
         text="Uttar Pradesh lies between Delhi and eastern India, so many long-distance trains pass through it. "
              "Ayodhya Dham Jn is the main station for the temple town of Ayodhya, and Ayodhya Cantt is a nearby station. "
              "Open a station to see every train that stops there.",
         links=[("/station/ay/", "Trains at Ayodhya Dham Jn"), ("/station/ayc/", "Trains at Ayodhya Cantt")]),
    dict(slug="east-india", name="East India", state="Odisha", st="odisha",
         box=(112, 279, 815, 729),
         alt="Sun Temple at Konark in Odisha",
         text="Odisha&rsquo;s coastal rail line connects Bhubaneswar and Puri with Kolkata, Chennai and Delhi. "
              "The Sun Temple at Konark, a UNESCO World Heritage Site, has no station of its own; "
              "Puri, roughly 35 km away, is the nearest railhead.",
         links=[("/station/bbs/", "Trains at Bhubaneswar"), ("/station/puri/", "Trains at Puri")]),
    dict(slug="north-east-india", name="North East India gateway", state="West Bengal", st="west-bengal",
         box=(100, 265, 799, 735),
         alt="Darjeeling Himalayan Railway steam train above tea gardens, with snow peaks behind",
         text="New Jalpaiguri, near Siliguri in West Bengal, is the main railhead for the Darjeeling hills, Sikkim and the North East. "
              "The narrow-gauge Darjeeling Himalayan Railway, a UNESCO World Heritage Site, runs from New Jalpaiguri up to Darjeeling.",
         links=[("/station/njp/", "Trains at New Jalpaiguri")]),
    dict(slug="central-india", name="Central India", state="Chhattisgarh", st="chhattisgarh",
         box=(100, 298, 739, 728),
         alt="A wide waterfall surrounded by forest in Chhattisgarh",
         text="Chhattisgarh sits on the Mumbai&ndash;Howrah main line, so trains between western and eastern India pass through Raipur Jn and Bilaspur Jn. "
              "Bilaspur is also the headquarters of South East Central Railway.",
         links=[("/station/r/", "Trains at Raipur Jn"), ("/station/bsp/", "Trains at Bilaspur Jn")]),
    dict(slug="south-india", name="South India", state="Kerala", st="kerala",
         box=(115, 279, 798, 742),
         alt="A temple tower and coconut palms in Kerala",
         text="Kerala&rsquo;s main rail line runs north to south through the state, from Thiruvananthapuram Central in the south "
              "through Ernakulam Jn in Kochi. Open a station to see its trains.",
         links=[("/station/tvc/", "Thiruvananthapuram Central"), ("/station/ers/", "Ernakulam Jn")]),
    dict(k=1.25, slug="maharashtra", name="Maharashtra", sub="West India", state="Maharashtra", st="maharashtra",
         box=(57, 161, 939, 891), mw=719, mh=800,
         alt="Gateway of India arch on the Mumbai waterfront",
         text="Mumbai is served by several terminals, including Mumbai CSMT, Mumbai Central, Dadar, Lokmanya Tilak Terminus and Bandra Terminus, "
              "and each handles different long-distance trains. Pune Jn and Nagpur Jn are other major stations in the state.",
         links=[("/station/csmt/", "Mumbai CSMT"), ("/station/pune/", "Pune Jn"), ("/station/ngp/", "Nagpur Jn")]),
    dict(k=1.55, slug="telangana", name="Telangana", sub="South India", state="Telangana", st="telangana",
         box=(42, 102, 905, 942), mw=744, mh=800,
         alt="Charminar, the four-minaret monument in Hyderabad",
         text="Hyderabad is served by three main stations: Secunderabad Jn, Hyderabad Deccan (Nampally) and Kacheguda. "
              "Open a station to see which trains stop there, and check live running status before you travel.",
         links=[("/station/sc/", "Secunderabad Jn"), ("/station/hyb/", "Hyderabad Deccan"), ("/station/kcg/", "Kacheguda")]),
    dict(k=1.25, slug="tamil-nadu", name="Tamil Nadu", sub="South India", state="Tamil Nadu", st="tamil-nadu",
         box=(36, 155, 833, 877), mw=798, mh=800,
         alt="A rock memorial on the sea at sunset on the Tamil Nadu coast",
         text="Chennai has two main long-distance stations, MGR Chennai Central and Chennai Egmore. "
              "Trains run on from there to the far south of Tamil Nadu and to Kanniyakumari, the southern tip of the mainland.",
         links=[("/station/mas/", "MGR Chennai Central"), ("/station/ms/", "Chennai Egmore")]),
    dict(k=1.45, slug="andhra-pradesh", name="Andhra Pradesh", sub="South India", state="Andhra Pradesh", st="andhra-pradesh",
         box=(31, 84, 828, 958), mw=800, mh=800,
         alt="A large carved stone bull statue with bells among boulders",
         text="Vijayawada Jn is a major junction where main lines between Howrah, Chennai and Hyderabad meet. "
              "Visakhapatnam is the main station on the east coast line, and Tirupati serves the temple town.",
         links=[("/station/bza/", "Vijayawada Jn"), ("/station/vskp/", "Visakhapatnam"), ("/station/tpty/", "Tirupati")]),
    dict(k=1.55, slug="kashmir", name="Kashmir", sub="North India", state="Jammu & Kashmir", st="jammu-and-kashmir",
         box=(45, 93, 890, 944), mw=756, mh=800,
         alt="Shikara boats and wooden houseboats on a lake in Kashmir, with snow mountains behind",
         text="Jammu Tawi is a main railhead for the Jammu region, and Shri Mata Vaishno Devi Katra is the station for the Vaishno Devi pilgrimage. "
              "Further north, Srinagar and Baramulla stations serve the Kashmir Valley.",
         links=[("/station/jat/", "Jammu Tawi"), ("/station/svdk/", "Katra")]),
    dict(k=1.25, slug="karnataka", name="Karnataka", sub="South India", state="Karnataka", st="karnataka",
         box=(62, 105, 835, 942), mw=796, mh=800,
         alt="A temple tower and ruins beside a river among boulders in Karnataka",
         text="Bengaluru is served by KSR Bengaluru City, Yesvantpur Jn and SMVT Bengaluru, among other stations. "
              "Mysuru Jn and Hubballi Jn are other major stations, and Hosapete Jn is the nearest railhead for Hampi.",
         links=[("/station/sbc/", "KSR Bengaluru"), ("/station/mys/", "Mysore Jn"), ("/station/hpt/", "Hosapete Jn")]),
    dict(k=0.9, m=8.5, slug="madhya-pradesh", name="Madhya Pradesh", sub="Central India", state="Madhya Pradesh", st="madhya-pradesh",
         box=(48, 306, 723, 687),
         alt="The Great Stupa and its carved stone gateway at Sanchi",
         text="Bhopal Jn is the main station for the state capital. Sanchi Stupa, a UNESCO World Heritage Site, is served by Sanchi station on the Bhopal&ndash;Bina line.",
         links=[("/station/bpl/", "Bhopal Jn"), ("/station/sci/", "Sanchi")]),
    dict(k=0.9, m=8.5, slug="punjab", name="Punjab", sub="North India", state="Punjab", st="punjab",
         box=(56, 316, 730, 725),
         alt="The Golden Temple in Amritsar lit up at dusk and reflected in the sarovar",
         text="Amritsar is the main station for the Golden Temple (Harmandir Sahib). Ludhiana Jn and Jalandhar City lie on the Delhi&ndash;Amritsar line.",
         links=[("/station/asr/", "Amritsar"), ("/station/ldh/", "Ludhiana Jn")]),
    dict(k=0.9, m=8.5, slug="gujarat", name="Gujarat", sub="West India", state="Gujarat", st="gujarat",
         box=(46, 337, 743, 712),
         alt="Camels walking across the white salt flats of the Rann of Kutch at sunset",
         text="Bhuj is the main railhead for Kutch and the Great Rann of Kutch. Ahmedabad Jn, Vadodara Jn and Surat are on the Mumbai&ndash;Ahmedabad main line.",
         links=[("/station/bhuj/", "Bhuj"), ("/station/adi/", "Ahmedabad Jn")]),
    dict(k=0.9, m=8.5, slug="haryana", name="Haryana", sub="North India", state="Haryana", st="haryana",
         box=(70, 353, 686, 705),
         alt="A calm lake with forested hills in the Morni Hills area of Haryana",
         text="Ambala Cantt Jn is a major junction towards Delhi, Punjab and the hills. Kalka, near the Morni Hills and Tikkar Taal, is where the narrow-gauge Kalka&ndash;Shimla Railway begins.",
         links=[("/station/umb/", "Ambala Cantt Jn"), ("/station/klk/", "Kalka")]),
    dict(k=0.9, m=8.5, slug="bihar", name="Bihar", sub="East India", state="Bihar", st="bihar",
         box=(33, 288, 745, 672),
         alt="The Mahabodhi Temple at Bodh Gaya in Bihar",
         text="Gaya Jn is the nearest main station for Bodh Gaya and the Mahabodhi Temple, a UNESCO World Heritage Site. Patna Jn serves the state capital.",
         links=[("/station/gaya/", "Gaya Jn"), ("/station/pnbe/", "Patna Jn")]),
    dict(k=0.74, m=6.5, slug="jharkhand", name="Jharkhand", sub="East India", state="Jharkhand", st="jharkhand",
         box=(48, 390, 591, 647),
         alt="A lake and forested hills at sunset seen from a viewpoint in Jharkhand",
         text="Ranchi is the state capital and main hub. Patratu Valley is a short drive away.",
         links=[("/station/rnc/", "Ranchi"), ("/station/tata/", "Tatanagar Jn")]),
    dict(k=1.2, slug="himachal-pradesh", name="Himachal Pradesh", sub="North India", state="Himachal Pradesh", st="himachal-pradesh",
         box=(39, 74, 743, 968),
         alt="Rock-cut temples carved into a cliff above a river valley in Himachal Pradesh",
         text="Una Himachal and Amb Andaura are broad-gauge stations in the state. Further into the hills, the narrow-gauge Kangra Valley Railway "
              "runs from Pathankot to Joginder Nagar, and the Masroor rock-cut temples stand in Kangra district.",
         links=[("/station/uhl/", "Una Himachal"), ("/station/ptk/", "Pathankot")]),
    dict(k=1.2, slug="arunachal-pradesh", name="Arunachal Pradesh", sub="North East India", state="Arunanchal Pradesh", st="arunachal-pradesh",
         box=(44, 94, 721, 942),
         alt="Tawang Monastery on a hillside with snow peaks and prayer flags",
         text="Tawang Monastery is reached by road; the nearest railheads are in Assam. "
              "Check live running status for the train that brings you to the Northeast.",
         links=[("/station/ghy/", "Guwahati")]),
    dict(k=1.2, slug="manipur", name="Manipur", sub="North East India", state="Manipur", st="manipur",
         box=(24, 25, 735, 1008),
         alt="The moat and brick wall of Kangla Fort in Imphal, Manipur",
         text="Kangla Fort stands in Imphal, the capital of Manipur. "
              "Trains into the Northeast arrive at Guwahati and other stations in Assam.",
         links=[("/station/ghy/", "Guwahati")]),
    dict(k=1.2, slug="nagaland", name="Nagaland", sub="North East India", state="Nagaland", st="nagaland",
         box=(58, 101, 754, 930),
         alt="A green valley with a stream and wildflowers in the hills of Nagaland",
         text="Dimapur is the railway station for Nagaland. Kohima and the Dzukou Valley are reached by road from there.",
         links=[("/station/dmv/", "Dimapur")]),
    dict(k=1.4, slug="uttarakhand", name="Uttarakhand", sub="North India", state="Uttarakhand", st="uttarakhand",
         box=(32, 107, 846, 933), mw=788,
         alt="A tiger and elephants by a river in the forest of Jim Corbett National Park",
         text="Ramnagar is the nearest railway station to Jim Corbett National Park. "
              "Kathgodam, Haridwar Jn and Dehradun are other major stations in Uttarakhand.",
         links=[("/station/kgm/", "Kathgodam"), ("/station/hw/", "Haridwar Jn"), ("/station/ddn/", "Dehradun")]),
    dict(k=1.2, slug="assam", name="Assam", sub="North East India", state="Assam", st="assam",
         box=(40, 96, 759, 959),
         alt="Rang Ghar, an oval brick pavilion beside a pond in Assam",
         text="Guwahati is the main hub in Assam, and Dibrugarh and Simaluguri Jn serve upper Assam, "
              "where the Ahom-era Rang Ghar stands near Sivasagar.",
         links=[("/station/ghy/", "Guwahati"), ("/station/dbrg/", "Dibrugarh"), ("/station/slgr/", "Simaluguri Jn")]),
]

CSS = """<style id="rg-css">
.rg-all{width:min(1200px,100vw - 40px);position:relative;left:50%;transform:translateX(-50%);display:grid;gap:22px;margin:14px 0 6px}
.rg{container-type:inline-size;position:relative;border-radius:14px;overflow:hidden;background:#fff;border:1.5px solid var(--line)}
.rg picture,.rg img{display:block;width:100%;height:auto}
.rg-card{padding:18px 18px 20px;background:#fff}
.rg-card h2{font:600 20px var(--font-head);color:var(--ink);line-height:1.2;margin:0}
.rg-card .st{font-size:13px;color:#7A819E;margin:2px 0 10px}
.rg-body{display:flex;gap:16px;align-items:flex-start}
.rg-body svg{flex:0 0 112px;width:112px;height:auto}
.rg-body p{font-size:15px;line-height:1.55;color:var(--text)}
.rg-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.rg-links a{border:1.5px solid var(--line);border-radius:999px;padding:6px 12px;font-size:13px;color:var(--ink)}
.rg-links a:hover{border-color:var(--indigo);color:var(--indigo)}
@media(min-width:1140px){
.rg-card{position:absolute;left:var(--l);top:var(--t);width:var(--w);height:var(--h);padding:calc(var(--k,1)*1.3cqw) calc(var(--k,1)*1.6cqw);overflow:hidden;display:flex;flex-direction:column}
.rg-card h2{font-size:calc(var(--k,1)*1.75cqw)}
.rg-card .st{font-size:calc(var(--k,1)*1.05cqw);margin:calc(var(--k,1)*.15cqw) 0 calc(var(--k,1)*.7cqw)}
.rg-body{gap:calc(var(--k,1)*1.2cqw)}
.rg-body svg{flex:0 0 calc(var(--k,1)*var(--m,12)*1cqw);width:calc(var(--k,1)*var(--m,12)*1cqw)}
.rg-body p{font-size:calc(var(--k,1)*1.1cqw);line-height:1.45}
.rg-links{gap:calc(var(--k,1)*.5cqw);margin-top:calc(var(--k,1)*.8cqw)}
.rg-links a{padding:calc(var(--k,1)*.35cqw) calc(var(--k,1)*.9cqw);font-size:calc(var(--k,1)*1cqw);border-width:1px}
}
</style>"""


def section(r):
    x0, y0, x1, y1 = r["box"]
    # cover the baked box by 1px on every side so no edge shows
    l, t = (x0 - 1) / 1920 * 100, (y0 - 1) / 1080 * 100
    w, h = (x1 - x0 + 3) / 1920 * 100, (y1 - y0 + 3) / 1080 * 100
    style = f"--l:{l:.3f}%;--t:{t:.3f}%;--w:{w:.3f}%;--h:{h:.3f}%;--k:{r.get('k',1)};--m:{r.get('m',12)}"
    links = "".join(f'<a href="{u}">{t_}</a>' for u, t_ in r["links"])
    s = r["slug"]
    return (
        f'<section class="rg" id="rg-{s}" aria-labelledby="rg-{s}-h">'
        f'<picture><source media="(max-width:1139px)" srcset="/shots/region-{s}-m.jpg" width="{r.get('mw',800)}" height="{r.get('mh',800)}">'
        f'<img src="/shots/region-{s}.jpg" alt="{r["alt"]}" width="1600" height="900" loading="lazy" decoding="async"></picture>'
        f'<div class="rg-card" style="{style}">'
        f'<h2 id="rg-{s}-h">{r["name"]} train routes</h2><p class="st">{r.get("sub", r["state"])}</p>'
        f'<div class="rg-body"><svg viewBox="0 0 1000 1118" role="img" aria-label="Map of India with {r["state"]} highlighted">'
        f'<use href="/shots/india-map.svg#in-all" fill="#DDE3F6" stroke="#fff" stroke-width="3"/>'
        f'<use href="/shots/india-map.svg#st-{r["st"]}" fill="#3654FF" stroke="#2339C9" stroke-width="6"/></svg>'
        f'<p>{r["text"]}</p></div>'
        f'<div class="rg-links">{links}</div></div></section>'
    )


def section_for(r, code):
    r = dict(r)
    r["links"] = [l for l in r["links"] if l[0] != f"/station/{code}/"]
    html = section(r)
    if not r["links"]:
        html = html.replace('<div class="rg-links"></div>', "")
    return html


STATE_TO_REGION = {r["state"]: r for r in REGIONS}
CSS_ONE = CSS.replace('<style id="rg-css">', '<style id="rg-css">')


def main():
    write = "--write" in sys.argv
    n = skipped = 0
    for code, state in sorted(STATES.items()):
        r = STATE_TO_REGION.get(state)
        page = ROOT / "station" / code / "index.html"
        if not r or not page.exists():
            continue
        html = page.read_text()
        new = "<!--rg-start-->" + CSS_ONE + '<div class="rg-all">' + section_for(r, code) + "</div><!--rg-end-->"
        html = re.sub(r"<!--rg-start-->.*?<!--rg-end-->", "", html, flags=re.S)
        m = re.search(r'<p class="crumb">.*?</p>', html, flags=re.S)
        if not m:
            skipped += 1
            continue
        out = html[:m.end()] + new + html[m.end():]
        n += 1
        if write:
            page.write_text(out)
    print(("written" if write else "dry run"), n, "pages; anchor missing on", skipped)


if __name__ == "__main__":
    main()
