import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

def compare_verified():
    with open('data/shipments.csv', 'r', encoding='utf-8-sig') as f:
        shipments = {r['tracking_no'].strip(): r for r in csv.DictReader(f)}
        
    with open('data/verified_300.csv', 'r', encoding='utf-8-sig') as f:
        verified = list(csv.DictReader(f))
        
    print(f"Verified rows: {len(verified)}")
    diff_counts = {}
    
    for v_row in verified:
        tno = v_row['tracking_no'].strip()
        if tno not in shipments:
            print(f"Tracking no {tno} not in shipments!")
            continue
        orig = shipments[tno]
        
        for k in v_row.keys():
            v_val = (v_row[k] or '').strip()
            o_val = (orig[k] or '').strip()
            if v_val != o_val:
                diff_counts[k] = diff_counts.get(k, 0) + 1
                
    print("\nField differences between shipments.csv and verified_300.csv for 299 sample rows:")
    for k, v in sorted(diff_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {v} differences ({v/len(verified)*100:.1f}%)")

if __name__ == '__main__':
    compare_verified()
