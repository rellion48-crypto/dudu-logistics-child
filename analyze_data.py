import csv
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

def audit_file(filepath):
    print(f"==================================================")
    print(f"ANALYSIS OF {filepath}")
    print(f"==================================================")
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total Rows: {len(rows)}")
    headers = reader.fieldnames
    print(f"Headers ({len(headers)}): {headers}\n")
    
    # 1. Null / Empty Counts
    empty_counts = {h: 0 for h in headers}
    for r in rows:
        for h in headers:
            if not r[h] or r[h].strip() == '':
                empty_counts[h] += 1
                
    print("--- Empty / Null Counts ---")
    for k, v in empty_counts.items():
        if v > 0:
            print(f"  {k}: {v} empty ({v/len(rows)*100:.2f}%)")
            
    # 2. Categorical Column Distributions
    cat_cols = ['receiver_area', 'region_type', 'size_grade', 'status', 'channel', 'branch_name', 'category']
    print("\n--- Categorical Distributions ---")
    for col in cat_cols:
        if col in headers:
            counts = {}
            for r in rows:
                v = r[col].strip() if r[col] else '(empty)'
                counts[v] = counts.get(v, 0) + 1
            print(f"Column [{col}] ({len(counts)} distinct values):")
            for k, val in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   '{k}': {val}")
                
    # 3. Numeric / Format checks
    print("\n--- Numeric / Format Checks ---")
    # Check invalid weight/dimensions
    unit_issues = {'weight_kg': 0, 'width_cm': 0, 'height_cm': 0, 'depth_cm': 0, 'price': 0}
    zero_or_neg_weight = 0
    oversized = 0
    
    for r in rows:
        for k in unit_issues.keys():
            if k in r and r[k]:
                v_str = str(r[k]).strip()
                if any(unit in v_str.lower() for unit in ['kg', 'cm', '원']):
                    unit_issues[k] += 1
                    
        # check weight float conversion
        w_val = r.get('weight_kg', '').replace('kg','').strip()
        try:
            w_num = float(w_val)
            if w_num <= 0:
                zero_or_neg_weight += 1
        except ValueError:
            pass
            
        # check dimensions
        try:
            w = float(r.get('width_cm','').replace('cm','').strip())
            h = float(r.get('height_cm','').replace('cm','').strip())
            d = float(r.get('depth_cm','').replace('cm','').strip())
            if w + h + d > 160 or w > 200 or h > 200 or d > 200:
                oversized += 1
        except ValueError:
            pass

    print(f"  Rows with unit characters in numeric columns: {unit_issues}")
    print(f"  Rows with weight <= 0: {zero_or_neg_weight}")
    print(f"  Rows with oversized dimensions (sum > 160cm or single > 200cm): {oversized}")
    
    # 4. Duplicate tracking_no
    tno_counts = {}
    for r in rows:
        tno = r['tracking_no'].strip()
        tno_counts[tno] = tno_counts.get(tno, 0) + 1
    dups = {k: v for k, v in tno_counts.items() if v > 1}
    print(f"\nDuplicate tracking_no count: {len(dups)} tracking numbers duplicated (total {sum(dups.values())} rows)")

if __name__ == '__main__':
    audit_file('data/shipments.csv')
    audit_file('data/shipments_re.csv')
