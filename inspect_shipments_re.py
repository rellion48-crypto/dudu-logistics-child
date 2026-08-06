import csv
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_dt(s):
    if not s: return None
    s = s.strip()
    if not s: return None
    for fmt in [
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
        '%Y.%m.%d %H시%M분', '%y-%m-%d %H:%M', '%m/%d/%Y %H:%M',
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'
    ]:
        try: return datetime.strptime(s, fmt)
        except ValueError: pass
    return None

def inspect_re():
    with open('data/shipments_re.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    with open('data/customers.csv', 'r', encoding='utf-8-sig') as f:
        customers = list(csv.DictReader(f))
    with open('data/tracking_events.csv', 'r', encoding='utf-8-sig') as f:
        events = list(csv.DictReader(f))

    print(f"=== DETAILED AUDIT OF shipments_re.csv ({len(rows)} rows) ===")

    # 1. Receiver Name artifacts (e.g., ' 님' or remaining notes/spaces)
    rname_suffix_nim = []
    for i, r in enumerate(rows):
        rn = r['receiver_name']
        if '님' in rn or ' 님' in rn:
            rname_suffix_nim.append((i+2, r['tracking_no'], rn))
    print(f"\n1. Receiver names with '님' honorific suffix: {len(rname_suffix_nim)} rows")
    for row_idx, tno, rn in rname_suffix_nim[:5]:
        print(f"   Line {row_idx} | TNO {tno} | Name: '{rn}'")

    # 2. Receiver phone length/format anomalies in shipments_re.csv
    phone_len_anomalies = []
    for i, r in enumerate(rows):
        p = r['receiver_phone']
        if p != '000-0000-0000':
            digits = re.sub(r'[^\d]', '', p)
            if len(digits) != 11 and len(digits) != 10:
                phone_len_anomalies.append((i+2, r['tracking_no'], p))
            elif len(digits) == 10 and not (p.startswith('010') or p.startswith('02') or p.startswith('03') or p.startswith('05') or p.startswith('07')):
                phone_len_anomalies.append((i+2, r['tracking_no'], p))
    print(f"\n2. Receiver phone abnormal formats (excluding 000-0000-0000): {len(phone_len_anomalies)} rows")
    for row_idx, tno, p in phone_len_anomalies[:5]:
        print(f"   Line {row_idx} | TNO {tno} | Phone: '{p}'")

    # 3. Delivered_at < Accepted_at (Temporal Inversion in shipments_re.csv)
    time_inversions = []
    for i, r in enumerate(rows):
        dt_acc = parse_dt(r['accepted_at'])
        dt_deliv = parse_dt(r['delivered_at'])
        if dt_acc and dt_deliv and dt_deliv < dt_acc:
            time_inversions.append((i+2, r['tracking_no'], r['accepted_at'], r['delivered_at']))
    print(f"\n3. delivered_at earlier than accepted_at (time inversion): {len(time_inversions)} rows")
    for row_idx, tno, acc, deliv in time_inversions[:5]:
        print(f"   Line {row_idx} | TNO {tno} | accepted: '{acc}' | delivered: '{deliv}'")

    # 4. Status = '배송완료' but delivered_at is empty, OR Status != '배송완료' but delivered_at exists
    deliv_status_mismatch = []
    for i, r in enumerate(rows):
        st = r['status']
        deliv = r['delivered_at'].strip()
        if st == '배송완료' and not deliv:
            deliv_status_mismatch.append((i+2, r['tracking_no'], st, 'empty delivered_at'))
        elif st != '배송완료' and deliv:
            deliv_status_mismatch.append((i+2, r['tracking_no'], st, f'has delivered_at: {deliv}'))
    print(f"\n4. Status and delivered_at mismatches: {len(deliv_status_mismatch)} rows")
    for row_idx, tno, st, msg in deliv_status_mismatch[:5]:
        print(f"   Line {row_idx} | TNO {tno} | Status: '{st}' | Issue: {msg}")

    # 5. Orphan sender_id not in customers.csv
    cust_ids = {c['customer_id'].strip() for c in customers if c.get('customer_id')}
    orphan_senders = []
    for i, r in enumerate(rows):
        sid = r['sender_id'].strip()
        if sid and sid not in cust_ids:
            orphan_senders.append((i+2, r['tracking_no'], sid))
    print(f"\n5. Sender IDs not registered in customers.csv: {len(orphan_senders)} rows")
    for row_idx, tno, sid in orphan_senders[:5]:
        print(f"   Line {row_idx} | TNO {tno} | Sender ID: '{sid}'")

    # 6. Branch code vs Branch Name integrity
    branch_map = {'11': '서울지점', '12': '용산지점', '21': '대전지점', '31': '진주지점', '32': '거제지점', '41': '울산지점'}
    branch_mismatches = []
    for i, r in enumerate(rows):
        bcode = r['branch_code'].strip()
        bname = r['branch_name'].strip()
        tno = r['tracking_no'].strip()
        tno_prefix = tno[:2]
        if branch_map.get(bcode) != bname or bcode != tno_prefix:
            branch_mismatches.append((i+2, tno, bcode, bname))
    print(f"\n6. Branch Code / Branch Name / Tracking Prefix mismatches: {len(branch_mismatches)} rows")
    for row_idx, tno, bcode, bname in branch_mismatches[:5]:
        print(f"   Line {row_idx} | TNO {tno} | Code: '{bcode}' | Name: '{bname}'")

    # 7. Item name Prohibited Items count in shipments_re.csv
    prohibited_count = sum(1 for r in rows if r['item_name'].startswith('[금지품목]'))
    print(f"\n7. Prohibited items tagged with [금지품목]: {prohibited_count} rows")

    # 8. Duplicate tracking_no (-DUP) count in shipments_re.csv
    dup_count = sum(1 for r in rows if '-DUP' in r['tracking_no'])
    print(f"\n8. Reassigned duplicate tracking numbers (-DUP): {dup_count} rows")

    # 9. Phone number 000-0000-0000 placeholder count in shipments_re.csv
    missing_phone_count = sum(1 for r in rows if r['receiver_phone'] == '000-0000-0000')
    print(f"\n9. Missing phone placeholders (000-0000-0000): {missing_phone_count} rows")

    # 10. Oversized dimensions (> 160cm sum or > 25kg billed_weight) in shipments_re.csv
    oversized_rows = []
    for i, r in enumerate(rows):
        w = float(r['width_cm'])
        h = float(r['height_cm'])
        d = float(r['depth_cm'])
        bw = float(r['billed_weight_kg'])
        sum_dim = w + h + d
        if sum_dim > 160 or bw > 25:
            oversized_rows.append((i+2, r['tracking_no'], sum_dim, bw))
    print(f"\n10. Oversized dimensions (>160cm sum or >25kg weight): {len(oversized_rows)} rows")
    for row_idx, tno, sdim, bw in oversized_rows[:5]:
        print(f"   Line {row_idx} | TNO {tno} | Sum dim: {sdim}cm | Billed weight: {bw}kg")

if __name__ == '__main__':
    inspect_re()
