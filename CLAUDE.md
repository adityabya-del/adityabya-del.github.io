# Notes for Claude: clearberth.app website

## Station name fixes: re-apply after ANY rebuild of train / route / station pages

On 11 Nov 2026 the station name "Jammutavi" was changed by hand to "Jammu Tawi" (two words) in all 671 HTML pages, because people search "Jammu Tawi". The script that generates these pages was NOT changed.

Whenever the train, route or station pages are rebuilt or regenerated:
1. Make the generator output "Jammu Tawi" (display text only), or re-run the replacement on the output:
   `grep -rlZ "Jammutavi" . --exclude-dir=.git --include=*.html | xargs -0 sed -i 's/Jammutavi/Jammu Tawi/g'`
2. Do NOT change the URLs. They stay lowercase `jammutavi` (e.g. /route/jammutavi-to-new-delhi/) so no page gives a 404.
3. Check: `grep -ro "Jammutavi" . --exclude-dir=.git | wc -l` must be 0.

Same for "Sri Nagar": on 11 Nov 2026 it was changed by hand to "Srinagar" (one word) in all pages. Re-apply after any rebuild:
   `grep -rlZ "Sri Nagar" . --exclude-dir=.git --include=*.html | xargs -0 sed -i 's/Sri Nagar/Srinagar/g'`

## Trains added by hand: keep them after ANY rebuild

On 11 Nov 2026 three trains that start at Jammu Tawi were missing (their pages gave 404) and were added by hand, using ClearBerth's own timetable data (the web-check function, action "live"):
- 12588 Gorakhpur Amarnath Express (Jammu Tawi to Gorakhpur Jn)
- 19028 Bandra Terminus Vivek Express (Jammu Tawi to Bandra Terminus)
- 22706 Jammu Tawi - Tirupati Humsafar Express (Jammu Tawi to Tirupati)

Added: /train/<no>/ and /hi/train/<no>/ pages, rows on 61 station pages and 93 route pages along their routes, links on /train/, and sitemap entries.
If the pages are rebuilt, make sure the generator includes these three trains (add them to its train list), or they will disappear again and give 404s.

## Internal links: re-run after ANY rebuild of train / route / station / guide pages

On 13 Nov 2026 `tools/add_internal_links.py` added internal links so Google can find unindexed pages: guide links on train, Hindi train, route, station and hub pages and between guides; station links in every train timetable; links to routes that no train page linked to; English <-> Hindi links between the two versions of a train page. The page generators were NOT changed, so a rebuild removes these links. After any rebuild run:
   `python3 tools/add_internal_links.py --write`
It skips what is already there, so running it twice is safe.

## Train page banners: re-run after ANY rebuild of the train pages

On 13 Nov 2026 `tools/add_train_banners.py` put a banner image (made by the site owner, saved as /shots/train-banner-1.jpg to 6.jpg) under the first paragraph of every /train/<number>/ page, rotating 1,2,3,4,5,6,1,2... in train-number order. The same banners are on the Hindi /hi/train/<number>/ pages (same banner as the English page) and on the /train/ list page (banner 1). The generators were NOT changed, so a rebuild removes the banners. After any rebuild run:
   `python3 tools/add_train_banners.py --write`
It skips pages that already have one.

## Regional sections on station pages: re-run after ANY rebuild of the station pages

On 13 Nov 2026 `tools/add_region_sections.py` added a regional section (the owner's photo with a white box, an India map with the state highlighted, short text, in the style of Amtrak's regional pages) to 488 station pages in Rajasthan, Uttar Pradesh, Odisha, West Bengal, Chhattisgarh, Kerala, Maharashtra, Telangana, Tamil Nadu, Andhra Pradesh, Jammu & Kashmir, Karnataka, Madhya Pradesh, Punjab, Gujarat, Haryana, Bihar, Jharkhand, Himachal Pradesh, Arunachal Pradesh, Manipur, Nagaland, Uttarakhand and Assam, right under the breadcrumb at the top. Station-to-state list: `tools/_station_states.json`. Map: `/shots/india-map.svg`. Photos: `/shots/region-*.jpg`. The generators were NOT changed, so a rebuild removes them. After any rebuild run:
   `python3 tools/add_region_sections.py --write`
Safe to run twice (it replaces its own block). Station pages only, on the owner's instruction.

## Stations added by hand: Naharlagun (NHLN) and Gumto (GMTO)

On 13 Nov 2026 `tools/add_northeast_stations.py` created /station/nhln/ and /station/gmto/ (Arunachal Pradesh), built from the timetables on the /train/ pages, so the Arunachal regional section has pages. The owner also asked for Jiribam, Vangaichungpao, Khongsang, Ranigaidinliu, Thingou (Manipur) and Bhalukpong: no /train/ page lists them, so no page was made. build_station_pages.py only rewrites existing pages, so these two survive a rebuild; re-run `python3 tools/add_northeast_stations.py --write`, then add_region_sections.py and add_internal_links.py, if they are lost.
