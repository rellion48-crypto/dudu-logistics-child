import csv
import sys
import re
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

PROHIBITED_KEYWORDS = [
    '현금', '상품권', '유가증권', '금', '은', '보석', '시계',
    '라이터', '부탄가스', '페인트', '신나', '알코올', '스프레이',
    '보조배터리', '리튬배터리', '배터리', '동물', '식물',
    '냉장', '냉동', '주류', '의약품', '약', '총포', '도검'
]

def parse_datetime(val):
    if not val:
        return None
    val = val.strip()
    if not val:
        return None
    for fmt in [
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
        '%Y.%m.%d %H시%M분', '%y-%m-%d %H:%M', '%m/%d/%Y %H:%M',
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'
    ]:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass
    return None

def clean_phone(phone_str):
    if not phone_str or not phone_str.strip():
        return "000-0000-0000"  # Classified missing phone placeholder
    digits = re.sub(r'[^\d]', '', str(phone_str))
    if len(digits) == 11 and digits.startswith('010'):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10 and digits.startswith('010'):
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 10 and (digits.startswith('02') or digits.startswith('03') or digits.startswith('05') or digits.startswith('07')):
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 0:
        return "000-0000-0000"
    return phone_str.strip()

def clean_area(area_str):
    if not area_str:
        return ""
    area = area_str.strip()
    mapping = {
        'SEOUL': '서울', '서울특별시': '서울', '서울시': '서울',
        '대전시': '대전', '대전광역시': '대전',
        '울산시': '울산', '울산광역시': '울산',
        '부산광역시': '부산', '대구광역시': '대구', '인천광역시': '인천', '광주광역시': '광주',
        '경상남도': '경남', '경상북도': '경북', '충청남도': '충남', '충청북도': '충북',
        '전라남도': '전남', '전라북도': '전북', '강원도': '강원', '제주도': '제주', '제주특별자치도': '제주'
    }
    return mapping.get(area, area)

def clean_status(status_str):
    if not status_str:
        return ""
    st = status_str.strip()
    mapping = {
        '배송 완료': '배송완료', '배달완료': '배송완료', '완료': '배송완료',
        '배송중': '배송출발', '배달중': '배송출발', '간선상차': '간선상차', '간선하차': '간선하차', '집화처리': '집화처리',
        '미 배송': '미배송', '미배달': '미배송', '배송실패': '미배송',
        '반송': '반품', '회수': '반품'
    }
    return mapping.get(st, st)

def clean_channel(channel_str):
    if not channel_str:
        return ""
    ch = channel_str.strip()
    mapping = {
        '편의점 접수': '편의점접수', '편의접수': '편의점접수',
        '인터넷': '인터넷접수', '온라인': '인터넷접수',
        '방문': '방문접수',
        '대리점접수': '대리점'
    }
    return mapping.get(ch, ch)

def calculate_business_days(start_date, days):
    cur = start_date
    added = 0
    while added < days:
        cur += timedelta(days=1)
        if cur.weekday() < 5:  # Mon-Fri
            added += 1
    return cur

def determine_region_type(area, dong):
    area_clean = clean_area(area)
    if area_clean == '제주':
        return '제주'
    elif area_clean == '도서산간' or '울릉' in (dong or '') or '백령' in (dong or '') or '흑산' in (dong or '') or '거문' in (dong or '') or '추자' in (dong or ''):
        return '도서산간'
    else:
        return '일반'

PRICE_TABLE = {
    '극소형': {'일반': 3500, '제주': 6500, '도서산간': 8500},
    '소형': {'일반': 4000, '제주': 7000, '도서산간': 9000},
    '중형': {'일반': 6000, '제주': 9000, '도서산간': 11000},
    '대형': {'일반': 9000, '제주': 12000, '도서산간': 14000},
}

def determine_size_grade(sum_cm, billed_weight):
    if sum_cm > 160 or billed_weight > 25:
        return '대형'
    if sum_cm <= 60 and billed_weight <= 2:
        return '극소형'
    elif sum_cm <= 80 and billed_weight <= 5:
        return '소형'
    elif sum_cm <= 120 and billed_weight <= 15:
        return '중형'
    elif sum_cm <= 160 and billed_weight <= 25:
        return '대형'
    return '대형'

def clean_float(val_str):
    if not val_str:
        return None
    s = re.sub(r'[^\d.]', '', str(val_str))
    try:
        return float(s)
    except ValueError:
        return None

def format_dim(val):
    if val is None:
        return ""
    if val == int(val):
        return str(int(val))
    return f"{val:.1f}"

def format_price(val):
    if val is None:
        return ""
    return f"{float(val):.1f}"

def process_data():
    with open('data/shipments.csv', 'r', encoding='utf-8-sig') as f:
        shipments = list(csv.DictReader(f))
        
    with open('data/tracking_events.csv', 'r', encoding='utf-8-sig') as f:
        events = list(csv.DictReader(f))
        
    events_by_no = {}
    for e in events:
        tno = e['tracking_no'].strip()
        events_by_no.setdefault(tno, []).append(e)

    stats = {
        'total': len(shipments),
        'dup_tracking_reassigned': 0,
        'missing_phone_tagged': 0,
        'prohibited_item_tagged': 0,
        'accepted_at_fixed': 0,
        'phone_fixed': 0,
        'area_fixed': 0,
        'status_fixed': 0,
        'channel_fixed': 0,
        'weight_unit_fixed': 0,
        'dim_unit_fixed': 0,
        'volume_weight_calc': 0,
        'size_grade_std': 0,
        'price_calc_fixed': 0,
        'delivered_at_filled': 0,
        'eta_calculated': 0,
        'name_cleaned': 0,
    }

    seen_tnos = {}
    processed_rows = []
    
    for r in shipments:
        row = dict(r)
        
        # Action A: Unique Tracking Number Reassignment for Duplicates
        orig_tno = row['tracking_no'].strip()
        if orig_tno in seen_tnos:
            seen_tnos[orig_tno] += 1
            row['tracking_no'] = f"{orig_tno}-DUP{seen_tnos[orig_tno]}"
            stats['dup_tracking_reassigned'] += 1
        else:
            seen_tnos[orig_tno] = 1
            row['tracking_no'] = orig_tno

        # Action B: Prohibited Item Classification Tagging
        orig_iname = row['item_name'].strip()
        matched_kw = [kw for kw in PROHIBITED_KEYWORDS if kw in orig_iname]
        if matched_kw and not orig_iname.startswith('[금지품목]'):
            row['item_name'] = f"[금지품목] {orig_iname}"
            stats['prohibited_item_tagged'] += 1
        else:
            row['item_name'] = orig_iname
            
        # Action C: Clean names
        orig_rname = row['receiver_name']
        clean_rname = re.sub(r'\s*\([^)]*\)', '', orig_rname).strip()
        if orig_rname != clean_rname:
            row['receiver_name'] = clean_rname
            stats['name_cleaned'] += 1
        row['sender_name'] = row['sender_name'].strip()
        
        # Action D: Phone number classification & format
        orig_phone = row['receiver_phone']
        clean_p = clean_phone(orig_phone)
        if clean_p != orig_phone:
            stats['phone_fixed'] += 1
        if clean_p == "000-0000-0000":
            stats['missing_phone_tagged'] += 1
        row['receiver_phone'] = clean_p
        
        # Accepted at
        dt_acc = parse_datetime(row['accepted_at'])
        if dt_acc:
            formatted_acc = dt_acc.strftime('%Y-%m-%d %H:%M:%S')
            if formatted_acc != row['accepted_at'].strip():
                stats['accepted_at_fixed'] += 1
            row['accepted_at'] = formatted_acc
            
        # Receiver Area & Region Type
        orig_area = row['receiver_area']
        c_area = clean_area(orig_area)
        if c_area != orig_area.strip():
            stats['area_fixed'] += 1
        row['receiver_area'] = c_area
        
        c_region = determine_region_type(c_area, row.get('receiver_dong'))
        row['region_type'] = c_region
        
        # Status & Channel
        orig_st = row['status']
        c_st = clean_status(orig_st)
        if c_st != orig_st.strip():
            stats['status_fixed'] += 1
        row['status'] = c_st
        
        orig_ch = row['channel']
        c_ch = clean_channel(orig_ch)
        if c_ch != orig_ch.strip():
            stats['channel_fixed'] += 1
        row['channel'] = c_ch
        
        # Weight & Dimensions
        w_val = clean_float(row['weight_kg']) or 0.0
        width_val = clean_float(row['width_cm']) or 0.0
        height_val = clean_float(row['height_cm']) or 0.0
        depth_val = clean_float(row['depth_cm']) or 0.0
        
        if 'kg' in row['weight_kg']:
            stats['weight_unit_fixed'] += 1
        if 'cm' in row['width_cm'] or 'cm' in row['height_cm'] or 'cm' in row['depth_cm']:
            stats['dim_unit_fixed'] += 1
            
        row['weight_kg'] = f"{w_val:.1f}" if w_val > 0 else "1.0"
        row['width_cm'] = format_dim(width_val)
        row['height_cm'] = format_dim(height_val)
        row['depth_cm'] = format_dim(depth_val)
        
        # Volume weight & billed weight
        vol_w = (width_val * height_val * depth_val) / 6000.0
        billed_w = max(w_val if w_val > 0 else 1.0, vol_w)
        row['volume_weight_kg'] = f"{vol_w:.1f}"
        row['billed_weight_kg'] = f"{billed_w:.1f}"
        stats['volume_weight_calc'] += 1
        
        # Size Grade
        sum_dim = width_val + height_val + depth_val
        grade = determine_size_grade(sum_dim, billed_w)
        if grade != row['size_grade'].strip():
            stats['size_grade_std'] += 1
        row['size_grade'] = grade
        
        # Price
        std_price = PRICE_TABLE.get(grade, {}).get(c_region, 4000)
        curr_price_str = row['price'].strip()
        try:
            curr_price = float(curr_price_str)
            if curr_price <= 0 or curr_price != float(std_price):
                row['price'] = format_price(std_price)
                stats['price_calc_fixed'] += 1
            else:
                row['price'] = format_price(curr_price)
        except ValueError:
            row['price'] = format_price(std_price)
            stats['price_calc_fixed'] += 1
            
        # Delivered at & Event sync
        t_evts = events_by_no.get(orig_tno, [])
        delivered_evts = [e for e in t_evts if clean_status(e['event']) == '배송완료']
        
        if c_st == '배송완료' and not row['delivered_at'].strip():
            if delivered_evts:
                dt_deliv = parse_datetime(delivered_evts[-1]['event_at'])
                if dt_deliv:
                    row['delivered_at'] = dt_deliv.strftime('%Y-%m-%d %H:%M:%S')
                    stats['delivered_at_filled'] += 1
        elif row['delivered_at'].strip():
            dt_deliv = parse_datetime(row['delivered_at'])
            if dt_deliv:
                row['delivered_at'] = dt_deliv.strftime('%Y-%m-%d %H:%M:%S')
                
        # ETA Date
        dt_eta = parse_datetime(row['eta_date'])
        if not dt_eta and dt_acc:
            days_needed = 1 if c_region == '일반' else (2 if c_region == '제주' else 3)
            eta_dt = calculate_business_days(dt_acc, days_needed)
            row['eta_date'] = eta_dt.strftime('%Y-%m-%d')
            stats['eta_calculated'] += 1
        elif dt_eta:
            row['eta_date'] = dt_eta.strftime('%Y-%m-%d')
            
        processed_rows.append(row)
        
    fieldnames = list(shipments[0].keys())
    with open('data/shipments_re.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)
        
    print("Enhanced processing complete! Statistics:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

if __name__ == '__main__':
    process_data()
