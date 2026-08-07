#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verified_300.csv를 Supabase shipments 테이블에 삽입할 SQL로 변환
"""

import csv
import sys

# stdout을 UTF-8로 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def escape_sql_string(s):
    """SQL 문자열 이스케이프"""
    if s is None or s == '':
        return 'NULL'
    # 작은따옴표를 두 개로 이스케이프
    s = str(s).replace("'", "''")
    return f"'{s}'"

def convert_csv_to_sql(csv_file, output_file=None):
    """CSV 파일을 SQL INSERT 문으로 변환"""
    try:
        # BOM 제거하고 UTF-8로 읽기
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print("[ERROR] CSV file is empty")
            return False

        print(f"[OK] Found {len(rows)} rows")

        # SQL VALUES 생성
        values_list = []
        for i, row in enumerate(rows):
            try:
                # 필요한 컬럼만 추출
                tno = row.get('tracking_no', '').strip()
                if not tno:
                    print(f"[SKIP] Row {i + 1} has empty tracking_no")
                    continue
                tracking_no = escape_sql_string(tno)
                sender_name = escape_sql_string(row.get('sender_name', ''))
                receiver_name = escape_sql_string(row.get('receiver_name', ''))
                receiver_area = escape_sql_string(row.get('receiver_area', ''))
                region_type = escape_sql_string(row.get('region_type', ''))
                item_name = escape_sql_string(row.get('item_name', ''))
                weight_kg = row.get('weight_kg', '0').strip() or '0'
                width_cm = row.get('width_cm', '0').strip() or '0'
                height_cm = row.get('height_cm', '0').strip() or '0'
                depth_cm = row.get('depth_cm', '0').strip() or '0'
                billed_weight_kg = row.get('billed_weight_kg', '0').strip() or '0'
                size_grade = escape_sql_string(row.get('size_grade', ''))
                price = row.get('price', '0').strip() or '0'
                eta_date = escape_sql_string(row.get('eta_date', ''))
                status = escape_sql_string(row.get('status', ''))

                # VALUES 행 생성
                value_row = (
                    f"({tracking_no},"
                    f"{sender_name},{receiver_name},"
                    f"{receiver_area},{region_type},"
                    f"{item_name},{weight_kg},"
                    f"{width_cm},{height_cm},{depth_cm},"
                    f"{billed_weight_kg},{size_grade},"
                    f"{price},{eta_date},{status})"
                )
                values_list.append(value_row)

                if (i + 1) % 50 == 0:
                    print(f"  Processing... {i + 1}/{len(rows)}")

            except Exception as e:
                print(f"[ERROR] Row {i + 1} error: {e}")
                continue

        # 완전한 SQL 생성
        sql = f"""-- verified_300.csv INSERT ({len(values_list)} rows)
INSERT INTO shipments (
  tracking_no, sender_name, receiver_name, receiver_area, region_type,
  item_name, weight_kg, width_cm, height_cm, depth_cm,
  billed_weight_kg, size_grade, price, eta_date, status
) VALUES
{','.join(values_list)}
ON CONFLICT (tracking_no) DO NOTHING;
"""

        # 파일에 저장
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql)
            print(f"\n[OK] SQL file created: {output_file}")

        # 첫 부분 출력
        print(f"\n[PREVIEW] SQL (first 500 chars):")
        print("=" * 80)
        print(sql[:500] + "...")
        print("=" * 80)

        return True

    except FileNotFoundError:
        print(f"[ERROR] File not found: {csv_file}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == '__main__':
    csv_path = 'data/verified_300.csv'
    output_path = 'verified_300_insert.sql'

    print("Converting CSV to SQL...\n")
    success = convert_csv_to_sql(csv_path, output_path)

    if success:
        print(f"\nNext steps:")
        print(f"1. Open file: {output_path}")
        print(f"2. Copy to Supabase SQL Editor")
        print(f"3. Click Run")
        sys.exit(0)
    else:
        sys.exit(1)
