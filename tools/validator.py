#!/usr/bin/env python3
"""
J1939 사양서 검증 스크립트
문서 8절에 정의된 검증 규칙을 자동으로 검사합니다.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    import pandas as pd
    import openpyxl
except ImportError as e:
    print(f"❌ 필수 라이브러리가 설치되지 않았습니다: {e}")
    print("다음 명령으로 설치하세요: pip install pandas openpyxl")
    sys.exit(1)


class Severity(Enum):
    """심각도 레벨"""
    ERROR = "Error"
    WARN = "Warning"


@dataclass
class ValidationResult:
    """검증 결과"""
    rule_name: str
    severity: Severity
    message: str
    row: int = None
    column: str = None


class J1939Validator:
    """J1939 사양서 검증기"""
    
    def __init__(self, excel_path: Path):
        self.excel_path = excel_path
        self.errors: List[ValidationResult] = []
        self.warnings: List[ValidationResult] = []
        self.slot_master = None
        self.message_spec = None
        self.valtable_master = None
        
    def load_excel(self) -> bool:
        """엑셀 파일 로드"""
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            
            # 필수 시트 확인
            required_sheets = ["SLOT_Master", "Message_Spec", "ValTable_Master"]
            missing_sheets = [s for s in required_sheets if s not in excel_file.sheet_names]
            
            if missing_sheets:
                self.errors.append(ValidationResult(
                    "Missing Sheets",
                    Severity.ERROR,
                    f"필수 시트가 없습니다: {', '.join(missing_sheets)}"
                ))
                return False
            
            # 시트 로드 (헤더는 0번째 행, 설명 행은 1번째 행이므로 skiprows=[1])
            self.slot_master = pd.read_excel(excel_file, sheet_name="SLOT_Master", skiprows=[1])
            self.message_spec = pd.read_excel(excel_file, sheet_name="Message_Spec", skiprows=[1])
            self.valtable_master = pd.read_excel(excel_file, sheet_name="ValTable_Master", skiprows=[1])
            
            print(f"✅ 엑셀 파일 로드 완료: {self.excel_path}")
            return True
            
        except Exception as e:
            self.errors.append(ValidationResult(
                "File Load Error",
                Severity.ERROR,
                f"엑셀 파일을 읽는 중 오류 발생: {e}"
            ))
            return False
    
    def validate_slot_master(self):
        """SLOT_Master 시트 검증"""
        if self.slot_master is None:
            return
        
        # 필수 컬럼 확인
        required_columns = ["SLOT Name", "Factor", "Offset", "Min", "Max"]
        missing_columns = [c for c in required_columns if c not in self.slot_master.columns]
        
        if missing_columns:
            self.errors.append(ValidationResult(
                "SLOT_Master Missing Columns",
                Severity.ERROR,
                f"필수 컬럼이 없습니다: {', '.join(missing_columns)}"
            ))
            return
        
        # SLOT Name 중복 확인
        duplicates = self.slot_master[self.slot_master["SLOT Name"].duplicated()]
        if not duplicates.empty:
            for idx, row in duplicates.iterrows():
                self.errors.append(ValidationResult(
                    "SLOT Name Duplicate",
                    Severity.ERROR,
                    f"중복된 SLOT Name: {row['SLOT Name']}",
                    row=idx + 2  # 헤더 + 설명 행 고려 (skiprows=1이므로 +2)
                ))
        
        # Min < Max 검증
        invalid_range = self.slot_master[
            self.slot_master["Min"] >= self.slot_master["Max"]
        ]
        if not invalid_range.empty:
            for idx, row in invalid_range.iterrows():
                self.warnings.append(ValidationResult(
                    "SLOT Min/Max Range",
                    Severity.WARN,
                    f"Min >= Max: SLOT={row['SLOT Name']}, Min={row['Min']}, Max={row['Max']}",
                    row=idx + 2
                ))
    
    def validate_message_spec(self):
        """Message_Spec 시트 검증"""
        if self.message_spec is None:
            return
        
        # 필수 컬럼 확인
        required_columns = [
            "Bus", "Message Name", "PGN (Hex)", "SA (Hex)", 
            "Tx Type", "SPN", "Signal Name", "Start Bit", "Len (Bit)", "SigType"
        ]
        missing_columns = [c for c in required_columns if c not in self.message_spec.columns]
        
        if missing_columns:
            self.errors.append(ValidationResult(
                "Message_Spec Missing Columns",
                Severity.ERROR,
                f"필수 컬럼이 없습니다: {', '.join(missing_columns)}"
            ))
            return
        
        # 메시지 이름 중복 확인
        duplicates = self.message_spec[self.message_spec["Message Name"].duplicated()]
        if not duplicates.empty:
            for idx, row in duplicates.iterrows():
                self.warnings.append(ValidationResult(
                    "Message Name Duplicate",
                    Severity.WARN,
                    f"중복된 Message Name: {row['Message Name']}",
                    row=idx + 2
                ))
        
        # Bus 명명 규칙 검증
        standard_buses = ["PCAN", "BCAN", "ICAN", "CCAN"]
        invalid_buses = self.message_spec[
            ~self.message_spec["Bus"].isin(standard_buses) &
            self.message_spec["Bus"].notna()
        ]
        if not invalid_buses.empty:
            for idx, row in invalid_buses.iterrows():
                bus = row["Bus"]
                if any(os_name in str(bus).lower() for os_name in ["can0", "can1", "eth0"]):
                    self.warnings.append(ValidationResult(
                        "Bus Naming Rule",
                        Severity.WARN,
                        f"OS 의존적 이름 사용: Bus={bus} (표준 도메인 사용 권장: PCAN, BCAN, ICAN, CCAN)",
                        row=idx + 2,
                        column="Bus"
                    ))
        
        # PDU1/PDU2 DA 적합성 검증
        for idx, row in self.message_spec.iterrows():
            pgn_hex = str(row.get("PGN (Hex)", "")).strip()
            da_hex = str(row.get("DA (Hex)", "")).strip()
            
            if not pgn_hex or not da_hex:
                continue
            
            try:
                # 16진수 문자열을 정수로 변환
                pgn = int(pgn_hex.replace("0x", "").replace("0X", ""), 16)
                da = int(da_hex.replace("0x", "").replace("0X", ""), 16)
                
                if pgn < 0xF000:  # PDU1
                    if da == 0xFF:
                        self.warnings.append(ValidationResult(
                            "PDU1 DA Validity",
                            Severity.WARN,
                            f"PDU1 메시지(PGN={pgn_hex})에서 DA는 0x00~0xFE이어야 합니다. 현재: {da_hex}",
                            row=idx + 2,
                            column="DA (Hex)"
                        ))
                else:  # PDU2
                    if da != 0xFF:
                        self.warnings.append(ValidationResult(
                            "PDU2 DA Validity",
                            Severity.WARN,
                            f"PDU2 메시지(PGN={pgn_hex})에서 DA는 0xFF이어야 합니다. 현재: {da_hex}",
                            row=idx + 2,
                            column="DA (Hex)"
                        ))
            except (ValueError, AttributeError):
                # 변환 실패는 무시 (다른 검증에서 처리)
                pass
    
    def validate_references(self):
        """참조 무결성 검증"""
        if self.message_spec is None or self.slot_master is None or self.valtable_master is None:
            return
        
        # SLOT 참조 검증
        if "SLOT Ref" in self.message_spec.columns:
            slot_refs = self.message_spec["SLOT Ref"].dropna()
            valid_slots = set(self.slot_master["SLOT Name"].astype(str))
            
            for idx, row in self.message_spec.iterrows():
                slot_ref = row.get("SLOT Ref")
                if pd.notna(slot_ref) and str(slot_ref) not in valid_slots:
                    self.errors.append(ValidationResult(
                        "SLOT Reference Error",
                        Severity.ERROR,
                        f"존재하지 않는 SLOT 참조: {slot_ref}",
                        row=idx + 2,
                        column="SLOT Ref"
                    ))
        
        # ValTable 참조 검증
        if "ValTable Ref" in self.message_spec.columns:
            valid_tables = set(self.valtable_master["Table Name"].astype(str))
            
            for idx, row in self.message_spec.iterrows():
                valtable_ref = row.get("ValTable Ref")
                if pd.notna(valtable_ref) and str(valtable_ref) not in valid_tables:
                    self.errors.append(ValidationResult(
                        "ValTable Reference Error",
                        Severity.ERROR,
                        f"존재하지 않는 ValTable 참조: {valtable_ref}",
                        row=idx + 2,
                        column="ValTable Ref"
                    ))
        
        # Enum 타입인데 ValTable Ref가 없는 경우
        if "SigType" in self.message_spec.columns and "ValTable Ref" in self.message_spec.columns:
            enum_without_table = self.message_spec[
                (self.message_spec["SigType"] == "Enum") &
                (self.message_spec["ValTable Ref"].isna())
            ]
            if not enum_without_table.empty:
                for idx, row in enum_without_table.iterrows():
                    self.errors.append(ValidationResult(
                        "Enum Definition Missing",
                        Severity.ERROR,
                        f"Enum 타입인데 ValTable Ref가 없습니다: Signal={row.get('Signal Name', 'N/A')}",
                        row=idx + 2
                    ))
    
    def validate_all(self) -> bool:
        """모든 검증 수행"""
        if not self.load_excel():
            return False
        
        print("\n🔍 검증 시작...")
        self.validate_slot_master()
        self.validate_message_spec()
        self.validate_references()
        
        return True
    
    def print_results(self):
        """검증 결과 출력"""
        print("\n" + "="*70)
        print("검증 결과")
        print("="*70)
        
        if not self.errors and not self.warnings:
            print("✅ 모든 검증을 통과했습니다!")
            return True
        
        # 에러 출력
        if self.errors:
            print(f"\n❌ 에러 ({len(self.errors)}개):")
            for i, error in enumerate(self.errors, 1):
                location = ""
                if error.row:
                    location = f" (행: {error.row}"
                    if error.column:
                        location += f", 컬럼: {error.column}"
                    location += ")"
                print(f"  {i}. [{error.rule_name}] {error.message}{location}")
        
        # 경고 출력
        if self.warnings:
            print(f"\n⚠️  경고 ({len(self.warnings)}개):")
            for i, warning in enumerate(self.warnings, 1):
                location = ""
                if warning.row:
                    location = f" (행: {warning.row}"
                    if warning.column:
                        location += f", 컬럼: {warning.column}"
                    location += ")"
                print(f"  {i}. [{warning.rule_name}] {warning.message}{location}")
        
        print("\n" + "="*70)
        
        # 에러가 있으면 실패
        return len(self.errors) == 0


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="J1939 사양서 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python validator.py specs/00_common/common_spec.xlsx
  python validator.py specs/templates/j1939_spec_template.xlsx
        """
    )
    parser.add_argument(
        "excel_file",
        type=Path,
        help="검증할 엑셀 파일 경로"
    )
    
    args = parser.parse_args()
    
    if not args.excel_file.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {args.excel_file}")
        sys.exit(1)
    
    validator = J1939Validator(args.excel_file)
    
    if validator.validate_all():
        success = validator.print_results()
        sys.exit(0 if success else 1)
    else:
        validator.print_results()
        sys.exit(1)


if __name__ == "__main__":
    main()

