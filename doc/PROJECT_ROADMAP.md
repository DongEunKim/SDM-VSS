# 프로젝트 로드맵 (Project Roadmap)

## 현재 상태 (Current Status)

### ✅ 완료된 작업
1. **문서 작성**
   - J1939 Specification and DBC Conversion Technical Standard.md 작성
   - 논리적 정합성 분석 및 개선
   - work_flow.md, File Tree.md 정리

2. **프로젝트 구조**
   - 기본 폴더 구조 생성 (`specs/`, `data_sources/`, `build/`, `dist/`, `tools/`)
   - `.gitignore`, `README.md` 작성

### 🔄 진행 중
- 없음

### ⏳ 다음 단계 (Next Steps)

## Phase 1: 핵심 빌드 시스템 구축 (우선순위: 높음)

### 1.1. 매니페스트 파일 템플릿 생성
**목적:** 각 레벨별 `manifest.yaml` 템플릿 제공

**작업:**
- [ ] `specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml` 예시 파일 생성
- [ ] 매니페스트 스키마 검증 로직 정의

**예상 산출물:**
```yaml
# specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml
project_name: "Excavator_CEABC"
version: "1.0.0"
base_definitions:
  - "specs/slot_master.xlsx"
  - "specs/valtable_master.xlsx"
inheritance:
  - "specs/j1939_standard.xlsx"
  - "specs/00_common/common_spec.xlsx"
  - "specs/00_common/10_excavator/excavator_spec.xlsx"
  - "specs/00_common/10_excavator/12_electric/electric_spec.xlsx"
  - "specs/00_common/10_excavator/12_electric/01_CEABC/CEABC_spec.xlsx"
```

### 1.2. 엑셀 템플릿 생성
**목적:** 표준에 맞는 엑셀 사양서 템플릿 제공

**작업:**
- [ ] `SLOT_Master` 시트 템플릿 (예시 데이터 포함)
- [ ] `Message_Spec` 시트 템플릿 (예시 데이터 포함)
- [ ] `ValTable_Master` 시트 템플릿 (예시 데이터 포함)
- [ ] 템플릿 파일을 `specs/templates/` 폴더에 배치

**도구:** Python `openpyxl` 또는 `pandas` 사용

### 1.3. 검증 스크립트 구현 (`tools/validator.py`)
**목적:** 문서 8절에 정의된 검증 규칙 자동화

**구현할 검증 규칙:**
- [ ] 구조적 무결성 (비트 중복, 멀티플렉서 구조)
- [ ] 프로토콜 준수 (PDU1/PDU2 DA 적합성, 주소 범위)
- [ ] 데이터 무결성 (초기값, SLOT 참조, ValTable 참조)
- [ ] 명명 규칙 (메시지/신호 이름 중복, Bus 명명)
- [ ] 타이밍 (필수 타이밍 누락)

**기술 스택:** Python, `pandas` (엑셀 읽기), `pydantic` (스키마 검증)

### 1.4. 엑셀 → DBC 변환 스크립트 (`tools/excel_to_dbc.py`)
**목적:** 엑셀 사양서를 DBC 파일로 변환

**주요 기능:**
- [ ] 매니페스트 파일 읽기 및 상속 구조 처리
- [ ] 엑셀 파일 병합 (Level 0 → Level 4)
- [ ] CAN ID 생성 (PDU1/PDU2 로직)
- [ ] DBC 파일 생성 (Bus별 분리)
- [ ] `can.conf` 생성

**기술 스택:** Python, `cantools` (DBC 생성), `openpyxl` (엑셀 읽기)

## Phase 2: 빌드 오케스트레이터 (우선순위: 중간)

### 2.1. 빌드 스크립트 (`build.py`)
**목적:** 전체 빌드 프로세스 자동화

**기능:**
- [ ] `specs/` 하위 모든 `manifest.yaml` 감지
- [ ] 각 모델별 빌드 실행
- [ ] 검증 → 변환 → 배포 파이프라인
- [ ] 에러 처리 및 로깅

### 2.2. 통합 사양서 생성
**목적:** 문서 6.3절 - 상속 구조가 반영된 통합 엑셀 생성

**기능:**
- [ ] 모든 레벨의 엑셀 파일 병합
- [ ] Cover Sheet 생성 (빌드 정보, 경고 문구)
- [ ] 스타일링 적용 (헤더 색상, 시트 보호)

## Phase 3: VSS 통합 준비 (우선순위: 중간)

### 3.1. VSS Overlay 생성 도구
**목적:** `VSS Hint` 컬럼을 기반으로 VSS Overlay 자동 생성

**기능:**
- [ ] `Message_Spec`의 `VSS Hint` 읽기
- [ ] `oem_overlay.vspec` 파일 생성
- [ ] VSS 경로 유효성 검증

### 3.2. VSS 매핑 파일 생성
**목적:** Kuksa CAN Provider용 `vss_dbc.json` 생성

**기능:**
- [ ] DBC 신호와 VSS 경로 매핑
- [ ] 변환 규칙 적용 (math, mapping)
- [ ] `vss_dbc.json` 생성

## Phase 4: 테스트 및 문서화 (우선순위: 낮음)

### 4.1. 테스트 데이터 준비
- [ ] 샘플 엑셀 파일 생성 (모든 규칙 포함)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 시나리오

### 4.2. 사용자 가이드 작성
- [ ] 엑셀 작성 가이드
- [ ] 빌드 실행 가이드
- [ ] 트러블슈팅 가이드

## 권장 작업 순서

### 즉시 시작 가능 (Quick Wins)
1. **매니페스트 템플릿 생성** (30분)
   - 문서의 예시를 그대로 파일로 생성

2. **엑셀 템플릿 생성** (1-2시간)
   - Python 스크립트로 기본 템플릿 생성

3. **검증 스크립트 기본 구조** (2-3시간)
   - 엑셀 파일 읽기
   - 기본 검증 규칙 2-3개 구현

### 중기 작업 (1-2주)
4. **검증 스크립트 완성** (문서 8절 모든 규칙)
5. **엑셀 → DBC 변환 기본 기능**
6. **빌드 오케스트레이터 기본 버전**

### 장기 작업 (1개월+)
7. **VSS 통합**
8. **테스트 및 문서화**
9. **CI/CD 파이프라인 구축**

## 기술 스택 제안

### 필수 라이브러리
```python
# requirements.txt
pandas>=2.0.0          # 엑셀 파일 처리
openpyxl>=3.1.0        # 엑셀 읽기/쓰기
cantools>=39.0.0       # DBC 파일 생성/읽기
pydantic>=2.0.0        # 데이터 검증
pyyaml>=6.0            # YAML 파일 처리
```

### 선택 라이브러리
```python
click>=8.0.0           # CLI 인터페이스
rich>=13.0.0           # 터미널 출력 개선
pytest>=7.0.0          # 테스트 프레임워크
```

## 다음 단계 제안

**추천:** Phase 1.1 (매니페스트 템플릿)부터 시작

이유:
1. 가장 간단하고 빠르게 완료 가능
2. 프로젝트 구조를 명확히 함
3. 이후 작업의 기반이 됨

