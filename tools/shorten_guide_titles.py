"""Shortens the <title>, og:title and twitter:title of guides to 60 characters or less (27 Nov 2026).
The H1, link lists and /guides/ cards keep the full title. Idempotent. Run: python3 tools/shorten_guide_titles.py --write"""
import sys,re,os
T={
'aadhaar-train-ticket-booking-rules':'Aadhaar and IRCTC ticket booking rules',
'advance-reservation-period-60-days':'Train ticket booking: the 60-day rule',
'cancel-irctc-e-ticket':'Cancel an IRCTC e-ticket: charges and TDR',
'change-boarding-station-irctc':'Change boarding station on a train ticket',
'current-booking-after-chart':'Current booking: vacant berths after the chart',
'divyangjan-railway-concession':'Railway concession for Divyangjan',
'foreign-tourist-quota-irctc':'Foreign Tourist quota on IRCTC: rules',
'book-train-ticket-for-someone-else':'Booking a train ticket for someone else',
'group-booking-train-tickets':'Group booking of train tickets on IRCTC',
'id-proof-for-train-travel':'Valid ID proof for train travel',
'irctc-account-and-passenger-list-help':'IRCTC account rules: one ID, deactivation',
'irctc-booking-limits-and-timings':'IRCTC booking limits and timings',
'irctc-payment-failed-money-deducted':'IRCTC payment failed, money deducted',
'irctc-travel-insurance':'IRCTC travel insurance: 45 paise cover',
'lost-or-torn-train-ticket-duplicate':'Lost or torn train ticket: duplicate rules',
'lower-berth-and-ladies-quota-rules':'Lower berth and Ladies quota rules',
'rac-ticket-meaning-rules':'RAC ticket: can you travel?',
'railway-quota-codes-explained':'Railway quota codes: GN, TQ, LD, SS',
'senior-citizen-train-concession':'Senior citizen train concession in 2026',
'tatkal-ticket-booking-rules':'Tatkal booking: timings, charges, rules',
'train-cancelled-diverted-late-refund-tdr':'Train cancelled or late: refund and TDR',
'train-class-codes-explained':'Train class codes: SL, 3A, 2A, 1A, CC',
'train-complaint-railmadad-139':'Train complaint: RailMadad, 139, IRCTC',
'train-food-irctc-ecatering':'Train food: IRCTC eCatering and complaints',
'train-luggage-allowance-rules':'Train luggage allowance by class',
'transfer-train-ticket-change-name':'Transfer a train ticket or change name',
'vikalp-alternate-trains':'IRCTC VIKALP: waitlist to another train',
'waitlisted-e-ticket-after-chart':'Waitlisted e-ticket after the chart',
}
write='--write' in sys.argv
for slug,t in T.items():
    f=f'guides/{slug}/index.html'
    h=open(f,encoding='utf-8').read();o=h
    h=re.sub(r'<title>.*?</title>',f'<title>{t} | ClearBerth</title>',h,count=1,flags=re.S)
    h=re.sub(r'(<meta (?:property|name)="(?:og|twitter):title" content=")[^"]*(")',lambda m:m.group(1)+t+m.group(2),h)
    assert len(t)+12<=60,(slug,len(t)+12)
    if h!=o:
        print('shorten',slug)
        if write: open(f,'w',encoding='utf-8').write(h)
