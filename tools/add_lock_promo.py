"""Insert a lock-screen alerts block between the lead paragraph and the checker
on /train-kahan-hai/, /pnr-status/ and /hi/pnr-status/. Safe to run twice."""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WRITE = '--write' in sys.argv

CSS = ('<style id="lockpromo-css">'
       '.lockpromo{display:flex;gap:22px;align-items:center;background:var(--night);color:#fff;'
       'border-radius:var(--radius);padding:18px 22px;margin:22px 0 6px;max-width:760px}'
       '.lockpromo img{width:200px;height:auto;border-radius:14px;flex:none}'
       '.lockpromo h2{color:#fff;font-size:clamp(20px,2.2vw,26px);margin:0 0 6px;line-height:1.25}'
       '.lockpromo p{margin:0 0 4px;color:#C9CFF0;font-size:15px}'
       '.lockpromo .lp-price{color:#FFB4A3;font-weight:600}'
       '.lockpromo .lp-btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}'
       '.lockpromo .btn{padding:11px 20px;font-size:15px}'
       '.lockpromo .btn-ghost{background:transparent;color:#fff;border:1.5px solid rgba(255,255,255,.5)}'
       '@media(max-width:560px){.lockpromo{flex-direction:column;align-items:flex-start}'
       '.lockpromo{padding:16px;gap:14px}.lockpromo img{width:100%;max-width:230px}}'
       '</style>')

PAGES = {
    'train-kahan-hai/index.html': dict(
        img='/shots/lock-card-en.webp',
        alt='ClearBerth lock-screen card: train ki live position, aapka station aur platform',
        h='Train aapki lock screen par, live',
        p='App kholne ki zarurat nahi. Refresh nahi.',
        price='₹29 per journey · ek baar payment · koi subscription nahi',
        b1='Kaise kaam karta hai', b1href='/lock-screen-train-alerts/',
        b2='App lein'),
    'pnr-status/index.html': dict(
        img='/shots/lock-card-en.webp',
        alt='ClearBerth lock-screen card: your station and time, your stop, the train moving and your platform',
        h='Your train, live on your lock screen',
        p='No app to open. No refreshing.',
        price='₹29 per journey · pay once · no subscription',
        b1='See how it works', b1href='/lock-screen-train-alerts/',
        b2='Get the app'),
    'hi/pnr-status/index.html': dict(
        img='/shots/lock-card-hi.webp',
        alt='ClearBerth लॉक स्क्रीन कार्ड: आपका स्टेशन, समय, ट्रेन की लाइव स्थिति और प्लेटफ़ॉर्म',
        h='आपकी ट्रेन, लाइव, आपकी लॉक स्क्रीन पर',
        p='न ऐप खोलना, न रिफ़्रेश करना।',
        price='एक यात्रा ₹29 · एक बार पेमेंट · कोई सब्सक्रिप्शन नहीं',
        b1='देखें कैसे काम करता है', b1href='/hi/lock-screen-train-alerts/',
        b2='ऐप लें'),
}

START, END = '<!--lockpromo-->', '<!--/lockpromo-->'

for rel, d in PAGES.items():
    f = ROOT / rel
    s = f.read_text(encoding='utf-8')
    # remove an earlier copy so the script can run twice
    if START in s:
        a = s.index(START); b = s.index(END) + len(END)
        s = s[:a] + s[b:]
    if 'id="lockpromo-css"' in s:
        a = s.index('<style id="lockpromo-css">'); b = s.index('</style>', a) + len('</style>')
        s = s[:a] + s[b:]
    block = (f'{START}<div class="lockpromo">'
             f'<img src="{d["img"]}" alt="{d["alt"]}" width="200" height="168" loading="eager">'
             f'<div><h2>{d["h"]}</h2><p>{d["p"]}</p><p class="lp-price">{d["price"]}</p>'
             f'<div class="lp-btns"><a class="btn btn-coral" href="{d["b1href"]}">{d["b1"]}</a>'
             f'<a class="btn btn-ghost" href="/#get-app">{d["b2"]}</a></div></div></div>{END}')
    # anchor: the lead paragraph inside the first .wrap.pg, before the checker section
    i = s.index('<div class="wrap pg">')
    lead = s.index('<p class="lead">', i)
    lead_end = s.index('</p>', lead) + len('</p>')
    assert lead_end < s.index('<section class="check"'), rel
    s = s[:lead_end] + '\n  ' + block + s[lead_end:]
    s = s.replace('</head>', CSS + '</head>', 1)
    assert s.count(START) == 1 and s.count('id="lockpromo-css"') == 1
    print(rel, 'ok')
    if WRITE:
        f.write_text(s, encoding='utf-8')
