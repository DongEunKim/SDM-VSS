# IDL-Sample.idl 문제점 및 해결 방안

표준 VSS에서 자동 생성된 `IDL-Sample.idl`의 세 가지 문제점에 대한 해결 방안을 제시합니다.

---

## 문제점 요약

| # | 문제 | 원인 |
|---|------|------|
| 1 | Databroker용 mapping.yaml 없음 | vspec2ddsidl은 IDL만 생성, 매핑 산출물 없음 |
| 2 | 리프까지 모듈화로 인한 과도한 복잡도 | 브랜치당 module, 리프당 struct → 1,900+ struct/module |
| 3 | Float 처리 방식 차이로 인한 호환성 부족 | VSS float vs J1939-71 SLOT(Factor/Offset) 변환 메타데이터 없음 |

---

## 1. mapping.yaml 자동 생성

### 1.1 현재 상황

- kuksa-dds-provider는 `mapping.yml`에서 VSS 경로 ↔ DDS 토픽 ↔ typename ↔ element를 수동 정의
- IDL-Sample.idl 구조는 결정적이므로, 매핑은 **자동 생성 가능**

### 1.2 해결 방안 A: 매핑 자동 생성 스크립트

VSS 스펙 또는 IDL 파싱 결과에서 `mapping.yaml`을 생성하는 변환기를 추가한다.

**입력:** VSS vspec(또는 vss.json) + IDL 파일  
**출력:** kuksa-dds-provider 호환 `mapping.yml`

```yaml
# 자동 생성 예시 (리프당 1 struct인 현재 구조)
Vehicle.Powertrain.CombustionEngine.Speed:
  description: "Engine speed measured as rotations per minute."
  databroker:
    datatype: UINT16
  source:
    Vehicle_Powertrain_CombustionEngine_Speed:  # 토픽명 (경로 기반)
      typename: Vehicle::Powertrain::CombustionEngine::Speed
      element: value
      transform:
        formula: { nominator: 1, denominator: 1, offset: 0 }
```

**구현 포인트:**
- VSS 경로 → typename: module 경로를 `::`로, struct명과 조합
- element: 현재 구조는 모두 `value` 단일 필드
- databroker.datatype: VSS datatype → types_pb2 매핑 (uint8→INT8, float→FLOAT 등)

### 1.3 해결 방안 B: 토픽 중심 구조로 전환 후 매핑 불필요

**토픽명 = VSS 브랜치 경로**, **IDL 필드 = 해당 브랜치 하위 리프** 구조로 변경하면,
SDM-API/Databroker에서 VSS 경로만으로 토픽·필드를 유도할 수 있어 별도 mapping.yaml 없이 동작 가능하다.

→ **문제 2 해결(구조 단순화)**과 함께 적용 시 시너지.

---

## 2. 과도한 모듈화 완화

### 2.1 현재 구조 (vspec2ddsidl 기본 동작)

```
module Vehicle {
  module Powertrain {
    module CombustionEngine {
      struct EngineCode { string value; };
      struct Displacement { unsigned short value; };
      struct Speed { unsigned short value; };
      ...
      module EngineOil {
        struct Capacity { float value; };
        struct Level { ... };
      };
    };
  };
}
```

- **리프당 1 struct** → 토픽 수 = 리프 수 (수백~수천)
- **모든 브랜치가 module** → 깊은 중첩, 긴 typename

### 2.2 해결 방안 A: 브랜치 단위 struct 병합 (후처리)

**원칙:** VSS 브랜치(리프를 가진 노드)를 하나의 struct로 병합.

```
// Before: 리프당 struct
struct EngineCode { string value; };
struct Speed { unsigned short value; };
struct ECT { float value; };

// After: 브랜치 단위 struct
struct Vehicle_Powertrain_CombustionEngine {
    string engine_code;      // VSS 리프명 → snake_case
    unsigned short speed;
    float ect;
    ...
};
```

**토픽:** `Vehicle.Powertrain.CombustionEngine` (1개)  
**IDL:** `Vehicle_Powertrain_CombustionEngine` (1개 struct)

**구현:** 
- vss-tools `ddsidl.py` 포크 또는 **후처리 스크립트** 작성
- VSS 트리 순회 → 리프가 있는 브랜치 단위로 그룹핑 → 단일 struct 생성
- instances(Row1, DriverSide 등)는 토픽 경로에 key로 포함: `Vehicle.Cabin.Door.Row1.DriverSide`

### 2.3 해결 방안 B: vspec2ddsidl 옵션 추가 (업스트림 기여)

vss-tools에 `--aggregate-by-branch` 또는 `--flat-struct` 옵션을 제안:

```
vspec export ddsidl --aggregate-by-branch -o vss_flat.idl
```

- `false` (기본): 현재 동작 유지
- `true`: 브랜치 단위로 struct 병합

### 2.4 예상 효과

| 항목 | 현재 | 개선 후 |
|------|------|---------|
| struct 수 | ~1,900 | ~200~400 (브랜치 수) |
| 토픽 수 | ~1,900 | ~200~400 |
| typename 길이 | `Vehicle::Powertrain::CombustionEngine::EngineOil::Temperature` | `Vehicle_Powertrain_CombustionEngine` |

---

## 3. Float 및 J1939-71 SLOT 정형화

### 3.1 문제 요약

| 구분 | VSS IDL | J1939-71 |
|------|---------|----------|
| 표현 | `float value` (물리값) | raw int + SLOT(Factor, Offset) |
| 변환 | 없음 | `physical = raw * Factor + Offset` |
| 메타데이터 | unit, min, max (주석/옵션) | SLOT_Master에 명시 |

J1939 제어기에서 DBC 기반으로 raw→physical 변환을 수행하는데, DDS IDL에는 **변환 규칙이 없어** 호환 불가.

### 3.2 해결 방안 A: 변환 메타데이터 별도 파일

IDL과 분리된 **변환 규칙 파일**을 생성·관리한다.

**파일:** `transforms.yaml` (또는 `slot_mapping.yaml`)

```yaml
# VSS 경로별 변환 규칙 (J1939 SLOT 매핑)
Vehicle.Powertrain.CombustionEngine.Speed:
  source_protocol: J1939
  slot_ref: SLOT_Speed
  factor: 0.125
  offset: 0
  min: 0
  max: 8031.875
  unit: rpm

Vehicle.Powertrain.CombustionEngine.ECT:
  source_protocol: J1939
  slot_ref: SLOT_Temp
  factor: 1
  offset: -273
  min: -273
  max: 1735
  unit: Celsius
```

**연동:**
- DBC/J1939 → DDS 변환 시: raw 수신 → SLOT 적용 → float로 DDS 발행
- DDS → DBC/J1939 변환 시: float 수신 → 역변환 → raw로 CAN 전송

**생성:**
- Message_Spec의 `VSS Hint` + `SLOT Ref`와 SLOT_Master를 결합해 자동 생성
- 또는 VSS unit/min/max와 SLOT 정의를 매칭하는 도구

### 3.3 해결 방안 B: IDL 어노테이션 확장 (DDS XTypes)

DDS IDL 4.2/XTypes는 `@key`, `@range` 등 어노테이션을 지원한다. 프로젝트별 확장으로 변환 규칙을 추가할 수 있다.

```idl
@transform(factor=0.125, offset=0, unit="rpm")
struct Speed {
    unsigned short value;  // raw (J1939) 또는 physical (VSS) 구분 필요
};
```

**주의:** 비표준 확장이므로 DDS 구현체별 지원 여부 확인 필요. 범용성보다는 **내부 도구 전용**으로 사용하는 편이 안전하다.

### 3.4 해결 방안 C: 이중 표현 (Raw + Physical)

J1939 등 레거시 프로토콜 연동이 필요한 신호에 대해 **raw와 physical 값을 모두** IDL에 포함한다.

```idl
struct Speed {
    unsigned short raw;      // J1939 raw value (0~0xFF)
    float physical;          // 변환된 물리값 (rpm)
};
```

- **장점:** DDS 구독자 입장에서 변환 로직 불필요
- **단점:** 페이로드 증가, 발행 측에서 변환 구현 필요

### 3.5 권장 조합

1. **transforms.yaml** (해결 방안 A): J1939 SLOT 및 기타 프로토콜 변환 규칙을 중앙 관리
2. **SDM-API/Provider 계층**에서 transforms.yaml을 로드하여 DBC/J1939 ↔ DDS 변환 수행
3. IDL은 **물리값(float)** 기준으로 유지하고, 변환은 변환 레이어에서 처리

---

## 4. 통합 제안: SDM-DDS 변환 파이프라인

위 방안들을 종합한 **변환 파이프라인**을 제안한다.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ VSS vspec       │     │ 변환 도구          │     │ 산출물           │
│ + Overlay       │────▶│ (converts/ddsidl) │────▶│ - IDL (병합)     │
│                 │     │                  │     │ - mapping.yaml   │
│ J1939 사양      │     │                  │     │ - transforms.yaml│
│ (Excel/DBC)     │────▶│                  │     │ - topics.yaml    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### 4.1 도구 역할

| 도구 | 입력 | 출력 | 비고 |
|------|------|------|------|
| vspec2ddsidl (수정/후처리) | VSS vspec | 병합된 IDL | 브랜치 단위 struct |
| vss2mapping | VSS + IDL | mapping.yaml | kuksa-dds-provider 호환 |
| vss2transforms | VSS + J1939 SLOT_Master + VSS Hint | transforms.yaml | J1939 등 변환 규칙 |
| vss2topics | VSS | topics.yaml | 토픽명·IDL·VSS 매핑 (SDM-API용) |

### 4.2 topics.yaml (토픽 중심 정의, 매핑 대체)

```yaml
topics:
  - name: Vehicle.Powertrain.CombustionEngine
    idl_type: Vehicle_Powertrain_CombustionEngine
    vss_paths:
      - Vehicle.Powertrain.CombustionEngine.Speed
      - Vehicle.Powertrain.CombustionEngine.ECT
      - Vehicle.Powertrain.CombustionEngine.EOT
      # ...
```

---

## 5. 구현 우선순위

| 순위 | 항목 | 작업 | 난이도 |
|------|------|------|--------|
| 1 | mapping.yaml 자동 생성 | vss2mapping 스크립트 | 중 |
| 2 | IDL 구조 단순화 | vspec2ddsidl 후처리 또는 포크 | 중 |
| 3 | **DDS transform 확장** | vss2ddsmapper에 math, mapping 추가 | 하 |
| 4 | transforms.yaml | J1939 SLOT + VSS Hint 연동 | 중 |
| 5 | topics.yaml | VSS 트리 기반 토픽 정의 생성 | 하 |

---

## 6. DBC dbc2val 스타일 transform을 DDS에 적용

DBC/CAN의 kuksa-can-provider는 mapping에 **math**, **mapping** transform을 지원한다. 동일한 방식을 DDS 매핑에도 적용할 수 있다.

### 6.1 DBC vs DDS transform 비교

| 변환 유형 | DBC (dbc2vss) | DDS (kuksa-dds-provider) |
|----------|---------------|---------------------------|
| **formula** | 없음 (DBC가 scale/offset 자동 적용) | `nominator`, `denominator`, `offset` (선형: `x*n/d+o`) |
| **math** | `py-expression-eval` 수식 (`x` 사용) | 구조에 `math: {}` 존재하나 **미구현** |
| **mapping** | `from`/`to` 열거형 매핑 | **미지원** |

**DBC transform 예시** (math, mapping):

```yaml
# DBC - math: 수식 기반 변환
Vehicle.Body.Mirrors.DriverSide.Tilt:
  dbc2vss:
    signal: VCLEFT_mirrorTiltYPosition
    transform:
      math: "floor((x*40)-100)"

# DBC - mapping: 열거형/문자열 매핑
Vehicle.Powertrain.Transmission.CurrentGear:
  dbc:
    signal: DI_gear
    transform:
      mapping:
        - from: DI_GEAR_D
          to: 1
        - from: DI_GEAR_P
          to: 0
```

**DDS transform 현황** (formula만 사용):

```yaml
# DDS - formula만 적용됨 (vss2ddsmapper.transform)
source:
  Nav_Sat_Fix:
    transform:
      formula:
        nominator: 1
        denominator: 1
        offset: 0
```

### 6.2 DDS에 dbc2val 스타일 transform 적용 방안

#### 방안 1: vss2ddsmapper 확장 (권장)

kuksa-dds-provider의 `Vss2DdsMapper.transform()`에 **math**, **mapping** 분기 추가.

```python
# vss2ddsmapper.py 확장 예시 (처리 순서: mapping → math → formula)
def transform(self, ddstopic, vsssignal, value):
    entry = self._get_entry(ddstopic, vsssignal)
    t = entry.get("transform") or {}
    if not t:
        return value

    # 1. mapping: 매칭 시 해당 값 반환 (에러값 0xFE/0xFF → null 등)
    if "mapping" in t:
        for item in t["mapping"]:
            if item["from"] == value:
                return item["to"]
        # 매칭 없을 때: formula/math로 폴백하거나 None (정책에 따라)

    # 2. math: py-expression-eval 수식
    if "math" in t and t["math"]:
        return Parser().parse(t["math"]).evaluate({"x": value})

    # 3. formula: nominator/denominator/offset (J1939 SLOT 호환)
    if "formula" in t:
        return formula(t["formula"], value)

    return value
```

**J1939 에러값 처리:** mapping에서 0xFE, 0xFF를 먼저 검사하고, 매칭되면 null 반환. 매칭 없으면 formula 적용.

#### 방안 2: 통합 transform 스키마 (DBC/DDS 공통)

DBC mapping(vss_dbc.json)과 DDS mapping(mapping.yml)이 **동일한 transform 스키마**를 사용하도록 정의한다.

```yaml
# 통합 transform 스키마 (source/dbc2vss 내 transform에 적용)
transform:
  # 옵션 1: 선형 변환 (J1939 SLOT 호환)
  formula:
    nominator: 0.125
    denominator: 1
    offset: 0

  # 옵션 2: 수식 (py-expression-eval, x = 입력값)
  math: "x * 0.125 + 0"

  # 옵션 3: 열거형/문자열 매핑
  mapping:
    - from: 0xFE
      to: null    # error
    - from: 255
      to: null
```

- **formula**: J1939 SLOT `physical = raw * Factor + Offset`에 직접 대응
- **math**: 복잡한 변환(에러값 처리, 보간 등)에 사용
- **mapping**: DBC ValTable, J1939 열거형 등

### 6.3 J1939-71 SLOT → transform 매핑

J1939 SLOT_Master의 Factor, Offset을 DDS mapping transform으로 변환한다.

| SLOT_Master | mapping transform |
|-------------|-------------------|
| Factor: 0.125, Offset: 0 | `formula: { nominator: 0.125, denominator: 1, offset: 0 }` 또는 `math: "x * 0.125"` |
| Factor: 1, Offset: -273 | `formula: { nominator: 1, denominator: 1, offset: -273 }` |

**에러값 처리** (J1939 0xFE, 0xFF): mapping으로 명시

```yaml
Vehicle.Powertrain.CombustionEngine.Speed:
  source:
    Vehicle_Powertrain_CombustionEngine_Speed:
      typename: Vehicle_Powertrain_CombustionEngine
      element: speed
      transform:
        # 기본: SLOT 적용
        formula:
          nominator: 0.125
          denominator: 1
          offset: 0
        # 에러값은 null로 (또는 별도 처리)
        mapping:
          - from: 254   # 0xFE
            to: null
          - from: 255   # 0xFF
            to: null
```

**참고:** formula와 mapping을 동시에 쓸 때는 **먼저 mapping 검사 → 매칭 없으면 formula 적용** 순서로 처리한다. 에러값(0xFE, 0xFF)을 mapping에서 걸러내고, 정상값은 formula로 변환하는 패턴에 유용하다.

### 6.4 양방향 변환 (dds2vss / vss2dds)

DBC는 `dbc2vss`(CAN→VSS)와 `vss2dbc`(VSS→CAN)에 각각 transform을 둔다. DDS도 동일하게:

| 방향 | 용도 | transform |
|------|------|-----------|
| **dds2vss** | DDS 수신 → Databroker(VSS) | raw/직렬화값 → VSS 물리값 |
| **vss2dds** | Databroker(VSS) → DDS 발행 | VSS 물리값 → DDS 직렬화값 |

현재 kuksa-dds-provider는 dds2vss만 지원. vss2dds 발행 시 **역변환**이 필요하다.

- formula 역변환: `x_out = (x_in - offset) * denominator / nominator`
- math 역변환: 수식이 가역이면 별도 `math_inverse` 정의, 불가역이면 매핑 테이블

### 6.5 적용 체크리스트

| 항목 | 작업 |
|------|------|
| vss2ddsmapper 확장 | `math`, `mapping` 분기 추가 |
| mapping 우선순위 | mapping → math → formula (매칭 순서) |
| J1939 SLOT 연동 | Message_Spec + SLOT_Master → mapping.yaml transform 자동 생성 |
| vss2dds (발행) | 역변환 수식/매핑 정의 (필요 시) |

---

## 7. 참고

- **vspec2ddsidl:** `ref./VSS/vss-tools/src/vss_tools/exporters/ddsidl.py`
- **J1939 SLOT:** `doc/J1939 Specification and DBC Conversion Technical Standard.md` 2.1절
- **kuksa mapping 예시:** `ref./eclipse-kuksa/providers/kuksa-dds-provider/mapping/vss_4.0/mapping.yml`
- **DBC transform (dbc2val):** `ref./eclipse-kuksa/providers/kuksa-can-provider/dbcfeederlib/dbc2vssmapper.py`, `mapping/README.md`
