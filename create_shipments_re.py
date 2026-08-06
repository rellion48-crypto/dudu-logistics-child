import csv
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_datetime(val):
    if not val:
        return None
    val = val.strip()
    if not val:
        return None
    
    # Try various datetime patterns
    # 1. YYYY-MM-DD HH:MM:SS
    try: return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
    except ValueError: pass
    
    # 2. YYYY-MM-DD HH:MM
    try: return datetime.strptime(val, '%Y-%m-%d %H:%M')
    except ValueError: pass

    # 3. YYYY/MM/DD HH:MM
    try: return datetime.strptime(val, '%Y/%m/%d %H:%M')
    except ValueError: pass

    # 4. YYYY.MM.DD HH시MM분
    try: return datetime.strptime(val, '%Y.%m.%d %H시%M분')
    except ValueError: pass

    # 5. YY-MM-DD HH:MM (e.g. 26-05-19 16:00 -> 2026-05-19 16:00:00)
    try: return datetime.strptime(val, '%y-%m-%d %H:%M')
    except ValueError: pass

    # 6. MM/DD/YYYY HH:MM (e.g. 05/25/2026 14:04)
    try: return datetime.strptime(val, '%m/%d/%Y %H:%M')
    except ValueError: pass

    # 7. YYYY-MM-DD
    try: return datetime.strptime(val, '%Y-%m-%d')
    except ValueError: pass

    # 8. YYYY/MM/DD
    try: return datetime.strptime(val, '%Y/%m/%d')
    except ValueError: pass

    # 9. YYYY.MM.DD
    try: return datetime.strptime(val, '%Y.%m.%d')
    except ValueError: pass

    raise ValueError(f"Unrecognized date format: '{val}'")

def parse_date(val):
    if not val:
        return ""
    dt = parse_datetime(val)
    return dt.strftime('%Y-%m-%d') if dt else ""

def parse_timestamp(val):
    if not val:
        return ""
    dt = parse_datetime(val)
    return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ""

def main():
    input_file = 'data/shipments.csv'
    output_file = 'data/shipments_re.csv'
    tracking_events_file = 'data/tracking_events.csv'

    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        shipments = list(reader)

    with open(tracking_events_file, 'r', encoding='utf-8-sig') as f:
        events = list(csv.DictReader(f))

    events_by_no = {}
    for e in events:
        tno = e['tracking_no']
        if tno not in events_by_no:
            events_by_no[tno] = []
        events_by_no[tno].append(e)

    delivered_statuses = {'배송완료', '배송 완료', '배달완료', '완료'}

    modified_rows = []
    acc_changed = 0
    eta_changed = 0
    deliv_filled = 0
    status_changed = 0

    for r in shipments:
        new_r = dict(r)
        
        # 1. accepted_at formatting (YYYY-MM-DD HH:MM:SS)
        orig_acc = r['accepted_at'].strip()
        formatted_acc = parse_timestamp(orig_acc)
        if orig_acc != formatted_acc:
            acc_changed += 1
            new_r['accepted_at'] = formatted_acc
        else:
            new_r['accepted_at'] = orig_acc

        # 2. eta_date formatting (YYYY-MM-DD)
        orig_eta = r['eta_date'].strip()
        if orig_eta:
            formatted_eta = parse_date(orig_eta)
            if orig_eta != formatted_eta:
                eta_changed += 1
                new_r['eta_date'] = formatted_eta
            else:
                new_r['eta_date'] = orig_eta
        else:
            new_r['eta_date'] = ""

        # 3. delivered_at & status
        orig_deliv = r['delivered_at'].strip()
        orig_status = r['status'].strip()
        
        if orig_status in delivered_statuses and not orig_deliv:
            tno = r['tracking_no']
            t_evts = events_by_no.get(tno, [])
            
            # find '배송완료' or related event
            deliv_evts = [e for e in t_evts if e['event'].strip() in delivered_statuses]
            if deliv_evts:
                # fill delivered_at from tracking event
                evt_time = deliv_evts[-1]['event_at'].strip()
                new_deliv = parse_timestamp(evt_time)
                new_r['delivered_at'] = new_deliv
                deliv_filled += 1
            else:
                # no delivered event, update status to last event
                if t_evts:
                    last_evt = t_evts[-1]['event'].strip()
                    new_r['status'] = last_evt
                    status_changed += 1
                else:
                    print(f"Warning: TNO {tno} has no tracking events!")
        else:
            if orig_deliv:
                new_r['delivered_at'] = parse_timestamp(orig_deliv)
            else:
                new_r['delivered_at'] = ""
                
        modified_rows.append(new_r)

    # Write output to data/shipments_re.csv with UTF-8-SIG encoding
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(modified_rows)

    print("=== Transformation Complete ===")
    print(f"Input file: {input_file} ({len(shipments)} rows)")
    print(f"Output file: {output_file} ({len(modified_rows)} rows)")
    print(f"1. accepted_at reformatted: {acc_changed} rows")
    print(f"2. eta_date reformatted: {eta_changed} rows")
    print(f"3. delivered_at filled from tracking_events: {deliv_filled} rows")
    print(f"4. status corrected (no delivery event): {status_changed} rows")

if __name__ == '__main__':
    main()
