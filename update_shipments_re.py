import csv
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_dt(s):
    if not s: return None
    s = s.strip()
    if not s: return None
    # Remove any tags before parsing if present
    s_clean = re.sub(r'\[.*?\]', '', s).strip()
    for fmt in [
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
        '%Y.%m.%d %H시%M분', '%y-%m-%d %H:%M', '%m/%d/%Y %H:%M',
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'
    ]:
        try: return datetime.strptime(s_clean, fmt)
        except ValueError: pass
    return None

def fix_phone(p):
    if not p or p == '000-0000-0000':
        return '000-0000-0000'
    p_str = str(p).strip()
    digits = re.sub(r'[^\d]', '', p_str)
    
    # 001090559028 -> 01090559028
    if digits.startswith('0010') and len(digits) == 12:
        digits = digits[2:]
    # 1076737143 -> 01076737143
    elif digits.startswith('10') and len(digits) == 10:
        digits = '0' + digits
    elif digits.startswith('10') and len(digits) == 11:
        digits = '0' + digits
        
    if len(digits) == 11 and digits.startswith('010'):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10 and digits.startswith('010'):
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 10 and (digits.startswith('02') or digits.startswith('03') or digits.startswith('05') or digits.startswith('07')):
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    
    return p_str

def apply_refinements():
    with open('data/shipments_re.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    stats = {
        'total': len(rows),
        'nim_removed': 0,
        'phone_fixed': 0,
        'time_inversion_flagged': 0,
        'status_mismatch_flagged': 0,
        'dimension_anomaly_flagged': 0,
    }

    processed_rows = []

    for r in rows:
        row = dict(r)

        # 1. '님' honorific suffix removal
        rname = row['receiver_name'].strip()
        clean_rname = re.sub(r'\s*님$', '', rname)
        if rname != clean_rname:
            stats['nim_removed'] += 1
        row['receiver_name'] = clean_rname

        # 2. Phone number correction
        orig_p = row['receiver_phone']
        fixed_p = fix_phone(orig_p)
        if fixed_p != orig_p:
            stats['phone_fixed'] += 1
        row['receiver_phone'] = fixed_p

        # 3 & 4. Anomaly flags for delivered_at
        dt_acc = parse_dt(row['accepted_at'])
        dt_deliv = parse_dt(row['delivered_at'])
        st = row['status'].strip()
        deliv_str = row['delivered_at'].strip()

        flags_deliv = []
        if dt_acc and dt_deliv and dt_deliv < dt_acc:
            flags_deliv.append('[시점역전]')
            stats['time_inversion_flagged'] += 1

        if st != '배송완료' and deliv_str:
            flags_deliv.append('[시각어긋남]')
            stats['status_mismatch_flagged'] += 1

        if flags_deliv:
            # Clean existing flags if any to avoid duplication
            clean_deliv_val = re.sub(r'\[.*?\]', '', deliv_str).strip()
            row['delivered_at'] = f"{''.join(flags_deliv)} {clean_deliv_val}".strip()

        # 5. Dimension anomaly flag
        w = float(row['width_cm'])
        h = float(row['height_cm'])
        d = float(row['depth_cm'])
        bw = float(row['billed_weight_kg'])
        sum_dim = w + h + d

        if sum_dim > 160 or bw > 25:
            iname = row['item_name'].strip()
            if '[치수이상]' not in iname:
                row['item_name'] = f"[치수이상] {iname}"
                stats['dimension_anomaly_flagged'] += 1

        # 6. Item 6 (Sender ID not in customers.csv) is IGNORED as requested.

        processed_rows.append(row)

    fieldnames = list(rows[0].keys())
    with open('data/shipments_re.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)

    print("=== Update Complete ===")
    print(f"Total rows processed: {stats['total']}")
    print(f"1. '님' suffix removed: {stats['nim_removed']} rows")
    print(f"2. Phone numbers corrected: {stats['phone_fixed']} rows")
    print(f"3. Time inversions flagged [시점역전]: {stats['time_inversion_flagged']} rows")
    print(f"4. Status mismatches flagged [시각어긋남]: {stats['status_mismatch_flagged']} rows")
    print(f"5. Dimension anomalies flagged [치수이상]: {stats['dimension_anomaly_flagged']} rows")
    print("6. Sender ID foreign key check: IGNORED as requested")

if __name__ == '__main__':
    apply_refinements()
