#!/usr/bin/env python3
"""
엑셀 → DBC 변환 스크립트
J1939 Specification 문서에 정의된 규칙에 따라 엑셀 사양서를 DBC 파일로 변환합니다.

주요 기능:
- 매니페스트 파일 읽기 및 상속 구조 처리
- 엑셀 파일 병합 (Level 0 → Level 4, Last Write Wins)
- CAN ID 생성 (PDU1/PDU2 로직)
- DBC 파일 생성 (Bus별 분리)
- can.conf 생성
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml

try:
    import pandas as pd
    import cantools
    from cantools.database import can
except ImportError as e:
    print(f"❌ 필수 라이브러리가 설치되지 않았습니다: {e}")
    print("다음 명령으로 설치하세요: pip install pandas openpyxl cantools pyyaml")
    sys.exit(1)


def parse_hex_or_int(val) -> int:
    """16진수 문자열 또는 정수를 정수로 변환"""
    if pd.isna(val) or str(val).strip() == "":
        return 0
    s = str(val).strip()
    if s.lower().startswith('0x'):
        return int(s, 16)
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def parse_value_table(vt_str) -> Optional[Dict[int, str]]:
    """ValTable 문자열을 딕셔너리로 변환: '0=Off;1=On' -> {0:'Off', 1:'On'}"""
    if pd.isna(vt_str) or str(vt_str).strip() == "":
        return None
    
    choices = {}
    for item in str(vt_str).split(';'):
        item = item.strip()
        if '=' in item:
            try:
                val, desc = item.split('=', 1)
                choices[int(val.strip())] = desc.strip()
            except (ValueError, TypeError):
                continue
    return choices if choices else None


def get_slot_val(row: pd.Series, slot_db: Dict, col_name: str, default=0.0):
    """SLOT 참조 또는 직접 값을 가져옴 (Manual Input > SLOT Ref > Default)"""
    val = row.get(col_name)
    if not pd.isna(val) and str(val).strip() != "":
        try:
            return float(val)
        except (ValueError, TypeError):
            return default
    
    slot_ref = row.get('SLOT Ref')
    if not pd.isna(slot_ref) and str(slot_ref) in slot_db:
        return slot_db[str(slot_ref)].get(col_name, default)
    return default


def calc_j1939_id(pgn: int, sa: int, da: int, prio: int = 6) -> int:
    """
    J1939 CAN ID 계산 (문서 3.2절 참조)
    
    PDU1 (PGN < 0xF000): (Prio << 26) | ((PGN & 0x3FF00) << 8) | (DA << 8) | SA
    PDU2 (PGN >= 0xF000): (Prio << 26) | (PGN << 8) | SA
    """
    if pgn < 0xF000:  # PDU1
        # PGN의 하위 8비트를 DA로 대체
        pf = (pgn >> 8) & 0xFF
        new_pgn = (pf << 8) | da
        return (prio << 26) | (new_pgn << 8) | sa
    else:  # PDU2
        return (prio << 26) | (pgn << 8) | sa


def load_manifest(manifest_path: Path) -> Dict:
    """매니페스트 파일 로드"""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
        return manifest
    except Exception as e:
        print(f"❌ 매니페스트 파일 로드 실패: {e}")
        sys.exit(1)


def merge_excel_files(manifest: Dict, base_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    상속 구조에 따라 엑셀 파일 병합 (Last Write Wins)
    
    Returns:
        (merged_slots, merged_messages, merged_valtables)
    """
    inheritance = manifest.get('inheritance', [])
    base_definitions = manifest.get('base_definitions', [])
    
    merged_slots = pd.DataFrame()
    merged_messages = pd.DataFrame()
    merged_valtables = pd.DataFrame()
    
    # base_definitions 먼저 로드 (전역 정의)
    for base_file in base_definitions:
        file_path = base_dir.parent / base_file
        if file_path.exists():
            try:
                df_slots = pd.read_excel(file_path, sheet_name='SLOT_Master', skiprows=[1])
                merged_slots = pd.concat([merged_slots, df_slots], ignore_index=True)
                
                df_valtables = pd.read_excel(file_path, sheet_name='ValTable_Master', skiprows=[1])
                merged_valtables = pd.concat([merged_valtables, df_valtables], ignore_index=True)
            except Exception as e:
                print(f"⚠️  전역 정의 파일 로드 실패 (무시): {file_path} - {e}")
    
    # inheritance 순서대로 로드 (뒤에 오는 파일이 앞의 내용을 덮어씀)
    for excel_file in inheritance:
        file_path = base_dir.parent / excel_file
        if not file_path.exists():
            print(f"⚠️  파일을 찾을 수 없습니다 (무시): {file_path}")
            continue
        
        try:
            # SLOT_Master 병합
            df_slots = pd.read_excel(file_path, sheet_name='SLOT_Master', skiprows=[1])
            if not df_slots.empty:
                # 중복 제거 (Last Write Wins)
                merged_slots = pd.concat([merged_slots, df_slots], ignore_index=True)
                merged_slots = merged_slots.drop_duplicates(subset=['SLOT Name'], keep='last')
            
            # Message_Spec 병합
            df_messages = pd.read_excel(file_path, sheet_name='Message_Spec', skiprows=[1])
            if not df_messages.empty:
                # 중복 제거 기준: Bus + PGN + SA + DA (문서 9.5.1절)
                df_messages['_merge_key'] = (
                    df_messages['Bus'].astype(str) + '_' +
                    df_messages['PGN (Hex)'].astype(str) + '_' +
                    df_messages['SA (Hex)'].astype(str) + '_' +
                    df_messages['DA (Hex)'].astype(str)
                )
                merged_messages = pd.concat([merged_messages, df_messages], ignore_index=True)
                merged_messages = merged_messages.drop_duplicates(subset=['_merge_key'], keep='last')
                merged_messages = merged_messages.drop(columns=['_merge_key'])
            
            # ValTable_Master 병합
            df_valtables = pd.read_excel(file_path, sheet_name='ValTable_Master', skiprows=[1])
            if not df_valtables.empty:
                merged_valtables = pd.concat([merged_valtables, df_valtables], ignore_index=True)
                merged_valtables = merged_valtables.drop_duplicates(subset=['Table Name'], keep='last')
        
        except Exception as e:
            print(f"❌ 엑셀 파일 로드 실패: {file_path} - {e}")
            sys.exit(1)
    
    return merged_slots, merged_messages, merged_valtables


def build_slot_database(df_slots: pd.DataFrame) -> Dict:
    """SLOT_Master를 딕셔너리로 변환"""
    slot_db = {}
    for _, row in df_slots.iterrows():
        name = str(row['SLOT Name']).strip()
        slot_db[name] = {
            'Factor': float(row['Factor']),
            'Offset': float(row['Offset']),
            'Min': float(row['Min']),
            'Max': float(row['Max']),
            'Unit': str(row['Unit']) if not pd.isna(row.get('Unit')) else ""
        }
    return slot_db


def build_valtable_database(df_valtables: pd.DataFrame) -> Dict:
    """ValTable_Master를 딕셔너리로 변환"""
    valtable_db = {}
    for _, row in df_valtables.iterrows():
        table_name = str(row['Table Name']).strip()
        definition = str(row['Definition']).strip()
        valtable_db[table_name] = parse_value_table(definition)
    return valtable_db


def create_dbc_for_bus(
    db_name: str,
    df_messages: pd.DataFrame,
    slot_db: Dict,
    valtable_db: Dict,
    bus_name: str
) -> cantools.database.Database:
    """특정 Bus에 대한 DBC 데이터베이스 생성"""
    db = cantools.database.Database()
    db.add_dbc_attribute_definition("ProtocolType", default="J1939")
    db.add_dbc_attribute_definition(
        "VFrameFormat",
        ["StandardCAN", "ExtendedCAN", "Reserved", "J1939PGN"],
        default="J1939PGN"
    )
    
    # 해당 Bus의 메시지만 필터링
    bus_messages = df_messages[df_messages['Bus'] == bus_name]
    
    # 메시지별 그룹핑
    for msg_name, rows in bus_messages.groupby("Message Name", sort=False):
        first = rows.iloc[0]
        
        # CAN ID 계산
        pgn = parse_hex_or_int(first['PGN (Hex)'])
        sa = parse_hex_or_int(first['SA (Hex)'])
        da = parse_hex_or_int(first.get('DA (Hex)', '0xFF'))
        prio = parse_hex_or_int(first.get('Prio', 7))
        frame_id = calc_j1939_id(pgn, sa, da, prio)
        
        # Multiplexor 스위치 찾기
        mux_sig_name = None
        for _, r in rows.iterrows():
            mux_val = str(r.get('Mux', '')).strip().upper()
            if mux_val == 'M':
                mux_sig_name = r['Signal Name']
                break
        
        # 신호 생성
        signals = []
        for _, row in rows.iterrows():
            sig_name = row['Signal Name']
            if pd.isna(sig_name):
                continue
            
            # SigType 처리
            sig_type = str(row.get('SigType', 'Float')).strip().title()
            is_float = (sig_type == 'Float')
            
            # SLOT 참조 또는 직접 값
            factor = get_slot_val(row, slot_db, 'Factor', 1.0)
            offset = get_slot_val(row, slot_db, 'Offset', 0.0)
            min_val = get_slot_val(row, slot_db, 'Min', 0.0)
            max_val = get_slot_val(row, slot_db, 'Max', 0.0)
            unit = str(get_slot_val(row, slot_db, 'Unit', ""))
            
            # Multiplexing 처리
            mux_val = str(row.get('Mux', '')).strip()
            is_mux = (mux_val.upper() == 'M')
            mux_ids = None
            if mux_val.lower().startswith('m') and len(mux_val) > 1:
                try:
                    mux_ids = [int(mux_val[1:])]
                except ValueError:
                    mux_ids = None
            
            # ValTable 참조 처리
            valtable_ref = row.get('ValTable Ref')
            choices = None
            if not pd.isna(valtable_ref) and str(valtable_ref) in valtable_db:
                choices = valtable_db[str(valtable_ref)]
            elif not pd.isna(valtable_ref):
                # 직접 정의된 경우 (예: "0=Off;1=On")
                choices = parse_value_table(valtable_ref)
            
            # Description 및 태그
            desc = str(row.get('Description', "")) if not pd.isna(row.get('Description')) else ""
            
            # String 타입 태깅
            if sig_type == 'String':
                desc = f"[TYPE: STRING] {desc}".strip()
            
            # VSS Hint 태깅
            vss_hint = row.get('VSS Hint')
            if not pd.isna(vss_hint) and str(vss_hint).strip():
                desc = f"{desc} [VSS: {vss_hint}]".strip()
            
            # Signal 생성
            signal = can.Signal(
                name=sig_name,
                start=int(float(row['Start Bit'])),
                length=int(float(row['Len (Bit)'])),
                byte_order='little_endian',
                is_signed=False,
                is_float=is_float,
                scale=factor,
                offset=offset,
                minimum=min_val,
                maximum=max_val,
                unit=unit,
                choices=choices,
                is_multiplexer=is_mux,
                multiplexer_ids=mux_ids,
                multiplexer_signal=mux_sig_name if mux_ids else None,
                comment=desc
            )
            signals.append(signal)
        
        # Tx Type 및 Cycle Time 처리 (문서 5.3절)
        tx_type_raw = str(first.get('Tx Type', 'Cyclic')).strip()
        cycle_time = parse_hex_or_int(first.get('Cycle Time', 0))
        
        # Tx Type 매핑 (문서 5.3절 표 참조)
        tx_type_mapping = {
            'Cyclic': 'Cyclic',
            'Event': 'Event',
            'Cyclic+Event': 'CyclicIfActive',
            'OnRequest': 'NoSendType'
        }
        gen_msg_send_type = tx_type_mapping.get(tx_type_raw, 'Cyclic')
        
        # Message 생성
        message = can.Message(
            frame_id=frame_id,
            name=msg_name,
            length=8,  # J1939는 항상 8바이트
            signals=signals,
            is_extended_frame=True,
            attributes={
                "VFrameFormat": "J1939PGN",
                "GenMsgSendType": gen_msg_send_type
            },
            comment=f"PGN: {pgn:#06X}, SA: {sa:#04X}, DA: {da:#04X}, TxType: {tx_type_raw}, Cycle: {cycle_time}ms"
        )
        db.add_message(message)
    
    return db


def create_can_conf(buses: List[str], output_dir: Path):
    """can.conf 파일 생성 (문서 6.2절 참조)"""
    conf_path = output_dir / "can.conf"
    
    lines = [
        "[default]",
        "interface = socketcan  # 제어기별 설정",
        "bitrate = 250000",
        ""
    ]
    
    for bus in buses:
        lines.extend([
            f"[{bus}]",
            f"# 엑셀의 'Bus' 컬럼이 섹션명이 됨",
            f"channel = can0  # 제어기별 설정",
            f"bitrate = 500000",
            f"dbc_file = {bus}.dbc",
            f"usage = {bus.lower()}_control",
            ""
        ])
    
    with open(conf_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ can.conf 생성 완료: {conf_path}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="엑셀 사양서를 DBC 파일로 변환",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python excel_to_dbc.py specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml
        """
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="매니페스트 파일 경로 (manifest.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="출력 디렉토리 (기본값: dist/[project_name]/[version]/)"
    )
    
    args = parser.parse_args()
    
    if not args.manifest.exists():
        print(f"❌ 매니페스트 파일을 찾을 수 없습니다: {args.manifest}")
        sys.exit(1)
    
    # 매니페스트 로드
    manifest = load_manifest(args.manifest)
    project_name = manifest.get('project_name', 'Unknown')
    version = manifest.get('version', '1.0.0')
    
    # 출력 디렉토리 설정
    if args.output:
        output_dir = args.output
    else:
        output_dir = Path("dist") / project_name / version
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📋 프로젝트: {project_name} v{version}")
    print(f"📁 출력 디렉토리: {output_dir}")
    
    # 엑셀 파일 병합
    print("\n📊 엑셀 파일 병합 중...")
    base_dir = args.manifest.parent
    merged_slots, merged_messages, merged_valtables = merge_excel_files(manifest, base_dir)
    
    if merged_messages.empty:
        print("❌ 병합된 메시지가 없습니다. inheritance 경로를 확인하세요.")
        sys.exit(1)
    
    print(f"  - SLOT: {len(merged_slots)}개")
    print(f"  - Message: {len(merged_messages)}개")
    print(f"  - ValTable: {len(merged_valtables)}개")
    
    # 데이터베이스 구축
    slot_db = build_slot_database(merged_slots)
    valtable_db = build_valtable_database(merged_valtables)
    
    # Bus별로 DBC 파일 생성
    buses = sorted(merged_messages['Bus'].unique())
    print(f"\n🔧 Bus별 DBC 파일 생성 중... ({len(buses)}개)")
    
    for bus in buses:
        db = create_dbc_for_bus(
            project_name,
            merged_messages,
            slot_db,
            valtable_db,
            bus
        )
        
        dbc_path = output_dir / f"{bus}.dbc"
        cantools.database.dump_file(db, str(dbc_path))
        print(f"  ✅ {bus}.dbc 생성 완료")
    
    # can.conf 생성
    create_can_conf(buses, output_dir)
    
    print(f"\n✅ 변환 완료! 출력 디렉토리: {output_dir}")


if __name__ == "__main__":
    main()

