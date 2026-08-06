import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

def evaluate():
    with open('data/verified_300.csv', 'r', encoding='utf-8-sig') as f:
        verified = list(csv.DictReader(f))
        
    with open('data/shipments.csv', 'r', encoding='utf-8-sig') as f:
        orig = {r['tracking_no'].strip(): r for r in csv.DictReader(f)}
        
    with open('data/shipments_re.csv', 'r', encoding='utf-8-sig') as f:
        cleaned = {r['tracking_no'].strip(): r for r in csv.DictReader(f)}

    fields = list(verified[0].keys())
    
    orig_matches = {k: 0 for k in fields}
    clean_matches = {k: 0 for k in fields}
    
    total = len(verified)
    
    for v in verified:
        tno = v['tracking_no'].strip()
        o = orig.get(tno, {})
        c = cleaned.get(tno, {})
        
        for k in fields:
            v_val = (v[k] or '').strip()
            o_val = (o.get(k) or '').strip()
            c_val = (c.get(k) or '').strip()
            
            if v_val == o_val:
                orig_matches[k] += 1
            if v_val == c_val:
                clean_matches[k] += 1
                
    print(f"=== EVALUATION AGAINST VERIFIED 299 SET ===")
    print(f"{'Field':<20} | {'Orig Match':<12} | {'Cleaned Match':<14} | {'Improvement'}")
    print("-" * 60)
    for k in fields:
        om = orig_matches[k]
        cm = clean_matches[k]
        diff = cm - om
        diff_str = f"+{diff}" if diff > 0 else (str(diff) if diff < 0 else "0")
        print(f"{k:<20} | {om:>4}/{total} ({om/total*100:4.1f}%) | {cm:>6}/{total} ({cm/total*100:4.1f}%) | {diff_str:>6}")

if __name__ == '__main__':
    evaluate()
