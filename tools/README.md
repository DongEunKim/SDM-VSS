# Tools 디렉토리

빌드 및 변환 도구들이 위치한 디렉토리입니다.

## 도구 목록

### 1. `create_excel_template.py`
**목적:** J1939 사양서 엑셀 템플릿 생성

**사용법:**
```bash
python3 tools/create_excel_template.py
```

**산출물:**
- `specs/templates/j1939_spec_template.xlsx`
  - SLOT_Master 시트 (예시 데이터 포함)
  - Message_Spec 시트 (예시 데이터 포함)
  - ValTable_Master 시트 (예시 데이터 포함)

### 2. `validator.py`
**목적:** 엑셀 사양서 검증 (문서 8절 규칙)

**사용법:**
```bash
python3 tools/validator.py <엑셀_파일_경로>
```

**검증 항목:**
- 구조적 무결성 (SLOT/ValTable 참조)
- 프로토콜 준수 (PDU1/PDU2 DA 적합성)
- 명명 규칙 (Bus 명명, 중복 검사)
- 데이터 무결성

**예시:**
```bash
python3 tools/validator.py specs/templates/j1939_spec_template.xlsx
```

### 3. `excel_to_dbc.py`
**목적:** 엑셀 사양서를 DBC 파일로 변환

**사용법:**
```bash
python3 tools/excel_to_dbc.py <manifest.yaml> [-o <출력_디렉토리>]
```

**주요 기능:**
- 매니페스트 파일 읽기 및 상속 구조 처리
- 엑셀 파일 병합 (Level 0 → Level 4, Last Write Wins)
- CAN ID 생성 (PDU1/PDU2 로직)
- DBC 파일 생성 (Bus별 분리)
- can.conf 생성

**예시:**
```bash
# 기본 출력 (dist/[project_name]/[version]/)
python3 tools/excel_to_dbc.py specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml

# 출력 디렉토리 지정
python3 tools/excel_to_dbc.py specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml -o custom_output/
```

**산출물:**
- `[Bus].dbc` - Bus별 DBC 파일 (예: `PCAN.dbc`, `BCAN.dbc`)
- `can.conf` - 런타임 설정 파일

## 작업 흐름

1. **템플릿 생성**
   ```bash
   python3 tools/create_excel_template.py
   ```

2. **엑셀 작성**
   - 템플릿을 복사하여 각 레벨별 사양서 작성
   - 매니페스트 파일 작성

3. **검증**
   ```bash
   python3 tools/validator.py specs/00_common/common_spec.xlsx
   ```

4. **변환**
   ```bash
   python3 tools/excel_to_dbc.py specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml
   ```

## 의존성

필수 라이브러리는 `requirements.txt`에 정의되어 있습니다:

```bash
pip install -r requirements.txt
```

필수 라이브러리:
- `pandas` - 엑셀 파일 처리
- `openpyxl` - 엑셀 읽기/쓰기
- `cantools` - DBC 파일 생성
- `pyyaml` - YAML 파일 처리

