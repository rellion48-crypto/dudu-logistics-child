import csv
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

PROHIBITED_KEYWORDS = [
    '현금', '상품권', '유가증권', '금', '은', '보석', '시계',
    '라이터', '부탄가스', '페인트', '신나', '알코올', '스프레이',
    '보조배터리', '리튬배터리', '배터리', '동물', '식물',
    '냉장', '냉동', '주류', '술', '의약품', '약', '총포', '도검'
]

def check_deferred():
    with open('data/shipments.csv', 'r', encoding='utf-8-sig') as f:
        shipments = list(csv.DictReader(f))
        
    print("=== 1. PROHIBITED ITEMS AUDIT ===")
    prohibited_rows = []
    for r in shipments:
        iname = r['item_name'].strip()
        matched = [kw for kw in PROHIBITED_KEYWORDS if kw in iname]
        if matched:
            prohibited_rows.append((r['tracking_no'], iname, matched))
            
    print(f"Found {len(prohibited_rows)} prohibited item registrations:")
    for tno, iname, kw in prohibited_rows[:20]:
        print(f"  TNO: {tno} | Item: {iname} | Matched: {kw}")
        
    print("\n=== 2. DUPLICATE TRACKING NO AUDIT ===")
    tno_counts = {}
    for r in shipments:
        tno = r['tracking_no'].strip()
        tno_counts[tno] = tno_counts.get(tno, 0) + 1
    dups = {k: v for k, v in tno_counts.items() if v > 1}
    print(f"Duplicate tracking numbers: {len(dups)} unique numbers, total {sum(dups.values())} rows")
    
    print("\n=== 3. MISSING PHONE AUDIT ===")
    missing_phone = [r for r in shipments if not r['receiver_phone'].strip()]
    print(f"Missing phone numbers: {len(missing_phone)} rows")

if __name__ == '__main__':
    check_deferred()
