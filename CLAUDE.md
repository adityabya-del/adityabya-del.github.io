# Notes for Claude: clearberth.app website

## Station name fixes: re-apply after ANY rebuild of train / route / station pages

On 11 Nov 2026 the station name "Jammutavi" was changed by hand to "Jammu Tawi" (two words) in all 671 HTML pages, because people search "Jammu Tawi". The script that generates these pages was NOT changed.

Whenever the train, route or station pages are rebuilt or regenerated:
1. Make the generator output "Jammu Tawi" (display text only), or re-run the replacement on the output:
   `grep -rlZ "Jammutavi" . --exclude-dir=.git --include=*.html | xargs -0 sed -i 's/Jammutavi/Jammu Tawi/g'`
2. Do NOT change the URLs. They stay lowercase `jammutavi` (e.g. /route/jammutavi-to-new-delhi/) so no page gives a 404.
3. Check: `grep -ro "Jammutavi" . --exclude-dir=.git | wc -l` must be 0.
