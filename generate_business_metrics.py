import csv
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_dt(s):
    if not s: return None
    try: return datetime.strptime(s.strip(), '%Y-%m-%d %H:%M:%S')
    except: pass
    try: return datetime.strptime(s.strip(), '%Y-%m-%d')
    except: pass
    return None

def analyze_business():
    with open('data/shipments.csv', 'r', encoding='utf-8-sig') as f:
        orig = list(csv.DictReader(f))
    with open('data/shipments_re.csv', 'r', encoding='utf-8-sig') as f:
        cleaned = list(csv.DictReader(f))
        
    print("=== MANAGEMENT QUESTION 1: UN-DELIVERED RATE BY BRANCH ===")
    branch_stats = {}
    for r in cleaned:
        bname = r['branch_name']
        st = r['status']
        if bname not in branch_stats:
            branch_stats[bname] = {'total': 0, 'undelivered': 0, 'returned': 0, 'delivered': 0}
        branch_stats[bname]['total'] += 1
        if st == '미배송':
            branch_stats[bname]['undelivered'] += 1
        elif st == '반품':
            branch_stats[bname]['returned'] += 1
        elif st == '배송완료':
            branch_stats[bname]['delivered'] += 1

    print(f"{'Branch Name':<12} | {'Total':<8} | {'Undelivered':<12} | {'Returned':<10} | {'Undeliv Rate (%)'}")
    print("-" * 65)
    for bname, s in sorted(branch_stats.items(), key=lambda x: x[1]['undelivered']/x[1]['total'], reverse=True):
        u_rate = (s['undelivered'] / s['total']) * 100
        print(f"{bname:<12} | {s['total']:<8} | {s['undelivered']:<12} | {s['returned']:<10} | {u_rate:6.2f}%")

    print("\n=== MANAGEMENT QUESTION 2: ACTUAL DELIVERY DAYS BY BRANCH ===")
    branch_days = {}
    for r in cleaned:
        bname = r['branch_name']
        dt_acc = parse_dt(r['accepted_at'])
        dt_deliv = parse_dt(r['delivered_at'])
        if dt_acc and dt_deliv and r['status'] == '배송완료':
            days = (dt_deliv - dt_acc).total_seconds() / 86400.0
            branch_days.setdefault(bname, []).append(days)

    print(f"{'Branch Name':<12} | {'Completed Orders':<16} | {'Avg Delivery Days':<18} | {'Max Days'}")
    print("-" * 65)
    for bname, dlist in sorted(branch_days.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
        avg_d = sum(dlist) / len(dlist)
        max_d = max(dlist)
        print(f"{bname:<12} | {len(dlist):<16} | {avg_d:6.2f} days        | {max_d:6.2f} days")

    print("\n=== MANAGEMENT QUESTION 3: PRICING DISCREPANCY ANALYSIS ===")
    overcharged = 0
    undercharged = 0
    overcharged_cnt = 0
    undercharged_cnt = 0
    exact_cnt = 0
    zero_price_cnt = 0

    for o, c in zip(orig, cleaned):
        try:
            o_price = float(o['price'].strip()) if o['price'].strip() else 0.0
        except ValueError:
            o_price = 0.0
        c_price = float(c['price'].strip())

        if o_price == 0.0:
            zero_price_cnt += 1

        diff = o_price - c_price
        if diff > 0:
            overcharged += diff
            overcharged_cnt += 1
        elif diff < 0:
            undercharged += abs(diff)
            undercharged_cnt += 1
        else:
            exact_cnt += 1

    print(f"Total shipments: {len(orig)}")
    print(f"Empty/Zero price orders in legacy: {zero_price_cnt} rows")
    print(f"Exact price matches: {exact_cnt} rows")
    print(f"Overcharged orders: {overcharged_cnt} rows, Total overcharged amount: {overcharged:,.0f} KRW")
    print(f"Undercharged orders: {undercharged_cnt} rows, Total undercharged amount: {undercharged:,.0f} KRW")
    print(f"Net Revenue Impact (Undercharged - Overcharged): {undercharged - overcharged:,.0f} KRW (Lost revenue)")

if __name__ == '__main__':
    analyze_business()
