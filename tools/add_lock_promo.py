"""Insert a lock-screen alerts block between the lead paragraph and the checker
on /train-kahan-hai/, /pnr-status/ and /hi/pnr-status/. Safe to run twice."""
import re, sys, pathlib

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
        img='/shots/lock-pnr-en.webp', w=200, hgt=157,
        alt='ClearBerth PNR Update notification on the lock screen: PNR status RLWL 3 now (was RLWL 6)',
        h='Your PNR status, on your lock screen',
        p='A notification every time your PNR status changes. When it is confirmed, you see your coach and berth.',
        price='₹29 per PNR · pay once · no subscription',
        b1='See how it works', b1href='/lock-screen-train-alerts/#pnr',
        b2='Get the app'),
    'hi/pnr-status/index.html': dict(
        img='/shots/lock-pnr-en.webp', w=200, hgt=157,
        alt='ClearBerth का PNR Update नोटिफ़िकेशन लॉक स्क्रीन पर: PNR स्टेटस RLWL 6 से RLWL 3',
        h='आपका PNR स्टेटस, आपकी लॉक स्क्रीन पर',
        p='PNR स्टेटस बदलते ही हर बार नोटिफ़िकेशन। कन्फ़र्म होने पर कोच और बर्थ भी दिखते हैं।',
        price='एक PNR ₹29 · एक बार पेमेंट · कोई सब्सक्रिप्शन नहीं',
        b1='देखें कैसे काम करता है', b1href='/hi/lock-screen-train-alerts/#pnr',
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
             f'<img src="{d["img"]}" alt="{d["alt"]}" width="{d.get("w",200)}" height="{d.get("hgt",168)}" loading="eager">'
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


# --- PNR section on the lock-screen pages (20 Nov 2026), target of the PNR pages' "See how it works"
PNR = {
    'lock-screen-train-alerts/index.html': dict(
        h='Your PNR status on your lock screen',
        p='Every time your PNR status changes, ClearBerth sends a <b>PNR Update</b> notification to your lock screen. When your ticket is confirmed, it shows your coach and berth.',
        alt='ClearBerth PNR Update notification on the lock screen: PNR status RLWL 3 now (was RLWL 6)',
        gal='<div class="pnrgal"><figure><img src="/shots/lock-pnr-en.webp" alt="iPhone lock screen: PNR Update, PNR status RLWL 3 now (was RLWL 6)" width="920" height="720" loading="lazy"><figcaption><b>iPhone:</b> your waitlist moved, RLWL 6 to RLWL 3</figcaption></figure><figure><img src="/shots/pnr-iphone-confirmed.webp" alt="iPhone: PNR Update, PNR status CNF S1 73 now (was RLWL 12), Coach S1, Berth 73" width="648" height="303" loading="lazy"><figcaption><b>iPhone:</b> confirmed, with your coach and berth</figcaption></figure><figure><img src="/shots/pnr-android.webp" alt="Android notification panel: two ClearBerth PNR Update alerts" width="720" height="688" loading="lazy"><figcaption><b>Android:</b> the same PNR Update alerts in your notifications</figcaption></figure></div>', how2='<div class="pnrhow"><div class="pnrshots"><figure><img src="/shots/pnr-app-check.webp" alt="ClearBerth PNR screen: enter your 10-digit PNR and tap Check status" width="720" height="1386" loading="lazy"><figcaption>1. Enter your PNR, tap <b>Check status</b></figcaption></figure><figure><img src="/shots/pnr-app-result-rlwl8.webp" alt="ClearBerth PNR result: passenger 6 on RLWL 8, with the Get PNR Status Alerts (₹29) button" width="720" height="1386" loading="lazy"><figcaption>2. Your status (here RLWL 8), then <b>Get PNR Status Alerts</b></figcaption></figure></div><div><h3>Turn it on</h3><ol><li>Open ClearBerth and tap <b>PNR</b>.</li><li>Enter your 10-digit PNR and tap <b>Check status</b>.</li><li>Your current status shows (in this example, RLWL 8). Select the date of journey, as printed on your ticket or SMS.</li><li>Tap <b>Get PNR Status Alerts (₹29)</b>.</li></ol></div></div>',
        how='<b>Turn it on:</b> open ClearBerth, tap <b>PNR</b>, enter your PNR and tap <b>Get PNR Status Alerts (₹29)</b>.',
        sched='<h3 id="pnr-timing">When ClearBerth checks your PNR</h3><div class="tt wr"><table><thead><tr><th>Time left before your train leaves</th><th>ClearBerth checks your PNR</th></tr></thead><tbody><tr><td>The moment you turn on the alert</td><td>Once, straight away. You get your current status.</td></tr><tr><td>More than 7 days</td><td>Every 2 days, at 6 PM</td></tr><tr><td>7 days or less</td><td>Every day, at 6 PM</td></tr><tr><td>Last 24 hours</td><td>Every 2 hours</td></tr><tr><td>Last 24 hours, in the hours around chart preparation</td><td>Every 30 minutes</td></tr><tr><td>After that, until departure</td><td>Every hour</td></tr><tr><td>About 90 to 30 minutes before departure (final chart)</td><td>Every 30 minutes</td></tr></tbody></table></div><p>You get a notification only when your status <b>changes</b>; if nothing changed at a check, no message is sent. Checks stop when every passenger on the ticket is confirmed, or when the train leaves.</p>',
        steps=('<h2>Turn it on in 3 steps</h2>', '<h2>Turn on the live train card in 3 steps</h2>')),
    'hi/lock-screen-train-alerts/index.html': dict(
        h='आपका PNR स्टेटस, आपकी लॉक स्क्रीन पर',
        p='जब भी आपका PNR स्टेटस बदलता है, ClearBerth आपकी लॉक स्क्रीन पर <b>PNR Update</b> नोटिफ़िकेशन भेजता है। टिकट कन्फ़र्म होने पर कोच और बर्थ भी दिखते हैं।',
        alt='ClearBerth का PNR Update नोटिफ़िकेशन लॉक स्क्रीन पर: PNR स्टेटस RLWL 6 से RLWL 3',
        gal='<div class="pnrgal"><figure><img src="/shots/lock-pnr-en.webp" alt="iPhone लॉक स्क्रीन: PNR Update, PNR स्टेटस RLWL 6 से RLWL 3" width="920" height="720" loading="lazy"><figcaption><b>iPhone:</b> वेटिंग लिस्ट आगे बढ़ी, RLWL 6 से RLWL 3</figcaption></figure><figure><img src="/shots/pnr-iphone-confirmed.webp" alt="iPhone: PNR Update, PNR स्टेटस CNF S1 73 (पहले RLWL 12), कोच S1, बर्थ 73" width="648" height="303" loading="lazy"><figcaption><b>iPhone:</b> कन्फ़र्म, कोच और बर्थ के साथ</figcaption></figure><figure><img src="/shots/pnr-android.webp" alt="Android नोटिफ़िकेशन पैनल: ClearBerth के दो PNR Update अलर्ट" width="720" height="688" loading="lazy"><figcaption><b>Android:</b> वही PNR Update अलर्ट आपके नोटिफ़िकेशन में</figcaption></figure></div>', how2='<div class="pnrhow"><div class="pnrshots"><figure><img src="/shots/pnr-app-check.webp" alt="ClearBerth PNR स्क्रीन: 10 अंकों का PNR डालें और Check status दबाएँ" width="720" height="1386" loading="lazy"><figcaption>1. PNR डालें, <b>Check status</b> दबाएँ</figcaption></figure><figure><img src="/shots/pnr-app-result-rlwl8.webp" alt="ClearBerth PNR नतीजा: यात्री 6 RLWL 8 पर, Get PNR Status Alerts (₹29) बटन के साथ" width="720" height="1386" loading="lazy"><figcaption>2. आपका स्टेटस (यहाँ RLWL 8), फिर <b>Get PNR Status Alerts</b></figcaption></figure></div><div><h3>चालू करें</h3><ol><li>ClearBerth खोलें और <b>PNR</b> दबाएँ।</li><li>अपना 10 अंकों का PNR डालें और <b>Check status</b> दबाएँ।</li><li>आपका अभी का स्टेटस दिखेगा (इस उदाहरण में RLWL 8)। यात्रा की तारीख़ चुनें, जैसी टिकट या SMS पर छपी है।</li><li><b>PNR स्थिति अलर्ट पाएं (₹29)</b> दबाएँ।</li></ol></div></div>',
        how='<b>चालू करें:</b> ClearBerth खोलें, <b>PNR</b> दबाएँ, अपना PNR डालें और <b>PNR स्थिति अलर्ट पाएं (₹29)</b> दबाएँ।',
        sched='<h3 id="pnr-timing">ClearBerth आपका PNR कब चेक करता है</h3><div class="tt wr"><table><thead><tr><th>ट्रेन छूटने में बचा समय</th><th>ClearBerth आपका PNR चेक करता है</th></tr></thead><tbody><tr><td>अलर्ट चालू करते ही</td><td>तुरंत एक बार। आपको अभी का स्टेटस मिल जाता है।</td></tr><tr><td>7 दिन से ज़्यादा</td><td>हर 2 दिन में, शाम 6 बजे</td></tr><tr><td>7 दिन या उससे कम</td><td>रोज़, शाम 6 बजे</td></tr><tr><td>आख़िरी 24 घंटे</td><td>हर 2 घंटे में</td></tr><tr><td>आख़िरी 24 घंटों में, चार्ट बनने के आसपास के घंटे</td><td>हर 30 मिनट में</td></tr><tr><td>उसके बाद, ट्रेन छूटने तक</td><td>हर घंटे</td></tr><tr><td>ट्रेन छूटने से लगभग 90 से 30 मिनट पहले (फ़ाइनल चार्ट)</td><td>हर 30 मिनट में</td></tr></tbody></table></div><p>नोटिफ़िकेशन तभी आता है जब आपका स्टेटस <b>बदलता</b> है; चेक में कुछ न बदले तो कोई मैसेज नहीं आता। टिकट के सभी यात्री कन्फ़र्म होने पर, या ट्रेन छूटने पर, चेक बंद हो जाते हैं।</p>',
        steps=('<h2>3 कदम में चालू करें</h2>', '<h2>लाइव ट्रेन कार्ड 3 कदम में चालू करें</h2>')),
}
for rel, d in PNR.items():
    f = ROOT / rel
    s = f.read_text(encoding='utf-8')
    if '<!--pnrlock-->' in s:
        a = s.index('<!--pnrlock-->'); b = s.index('<!--/pnrlock-->') + len('<!--/pnrlock-->')
        s = s[:a] + s[b:]
    s = s.replace(d['steps'][0], d['steps'][1])
    block = (f'<!--pnrlock--><h2 id="pnr">{d["h"]}</h2><p>{d["p"]}</p>'
             f'{d["gal"]}{d["sched"]}{d["how2"]}<!--/pnrlock-->')
    k = s.index(d['steps'][1])
    s = s[:k] + block + '\n' + s[k:]
    tcss = '<style id="pnrlock-css">.tt{overflow-x:auto;margin:14px 0}.tt table{border-collapse:collapse;width:100%;font-size:15px}.tt th,.tt td{border:1px solid var(--line,#E3E6F0);padding:9px 12px;text-align:left;vertical-align:top}.tt th{background:#F4F6FC}.tt.wr th,.tt.wr td{white-space:normal}.tt.wr table{table-layout:fixed}.pnrgal{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:18px 0;align-items:start}.pnrgal figure{margin:0}.pnrgal img{width:100%;height:auto;border-radius:16px;display:block}.pnrgal figcaption{font-size:14px;color:#5A6180;margin-top:6px}.pnrhow{display:flex;gap:24px;align-items:center;margin:22px 0}.pnrshots{display:flex;gap:12px;flex:none}.pnrshots figure{margin:0;width:200px}.pnrshots img{width:100%;height:auto;border-radius:18px;border:1px solid var(--line,#E3E6F0);display:block}.pnrshots figcaption{font-size:13px;color:#5A6180;margin-top:6px}.pnrhow h3{margin:0 0 8px}@media(max-width:700px){.pnrhow{flex-direction:column;align-items:flex-start}.pnrshots{width:100%}.pnrshots figure{width:auto;flex:1}}</style>'
    s = re.sub(r'<style id="pnrlock-css">.*?</style>', '', s, flags=re.S)
    s = s.replace('</head>', tcss + '</head>', 1)
    assert s.count('<!--pnrlock-->') == 1
    print(rel, 'pnr section ok')
    if WRITE:
        f.write_text(s, encoding='utf-8')
