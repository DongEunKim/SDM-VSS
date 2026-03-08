# KUKSA DDS Provider 통합 가이드

kuksa-dds-provider 현황, IDL-Sample.idl과의 호환성, 실제 사용을 위한 IDL 작성 절차, 추가 개발 필요 사항을 정리한 문서입니다.

---

## 1. kuksa-dds-provider 현황

### 1.1 개요

**실제로는 스켈레톤 수준**입니다.

| 구분 | 내용 |
|------|------|
| 포함 IDL | `NavSatFix.idl`, `NavSatStatus.idl`, `Header.idl`, `Time.idl` (ROS2 sensor_msgs 스타일) |
| 목적 | GPS 위치 데모(KML 재생) – `Vehicle.CurrentLocation.Latitude/Longitude/Altitude` 등 소수 신호 |
| mapping.yml | VSS 경로 ↔ DDS 토픽 ↔ typename ↔ element 매핑 (수동 정의) |

### 1.2 포함된 IDL 파일

```
ref./eclipse-kuksa/providers/kuksa-dds-provider/ddsproviderlib/idls/
├── NavStatFix.idl
├── NavSatStatus.idl
├── std_msgs/msg/Header.idl
└── std_msgs/msg/Time.idl
```

### 1.3 빌드 프로세스

`generate_py_dataclass.sh`가 수행하는 작업:

1. VSS 표준 스펙을 vss-tools로 IDL 변환
2. Cyclone DDS idlc로 Python dataclass 생성
3. pip install로 패키지화

**결론:** 실제 차량 신호를 사용하려면 **우리가 IDL과 매핑을 직접 설계·구현해야 합니다.**

---

## 2. IDL-Sample.idl과의 호환성 검토

### 2.1 구조 비교

| 항목 | kuksa-dds-provider (데모) | IDL-Sample.idl (VSS 표준) |
|------|---------------------------|---------------------------|
| 스타일 | ROS2 (sensor_msgs, 1 struct = 여러 신호) | VSS (리프당 1 struct, `value` 필드) |
| 예시 | `NavSatFix` → latitude, longitude, altitude | `Speed` → value |
| 토픽 수 | 1개 (Nav_Sat_Fix) | ~1,900개 (리프 수) |
| typename | `sensor_msgs.msg.NavSatFix` | `Vehicle.Powertrain.CombustionEngine.Speed` |

### 2.2 기술적 호환성

| 항목 | 호환 여부 | 비고 |
|------|-----------|------|
| IDL 문법 | ✅ | 둘 다 OMG IDL 계열, Cyclone DDS `idlc -l py`로 컴파일 가능 |
| typename 포맷 | ✅ | kuksa-dds-provider는 `eval(dataclass_name)` 사용 → Python import 경로 형식 필요 |
| mapping.yml | ⚠️ 수동/자동 생성 필요 | IDL-Sample 구조에 맞는 매핑 정의 필요 |

### 2.3 호환되기 위한 조건

1. **mapping.yml**: IDL-Sample의 struct마다 VSS 경로 ↔ DDS 토픽 ↔ typename ↔ element 매핑 정의
   - `typename`: `Vehicle.Powertrain.CombustionEngine.Speed` (Python 경로 형식)
   - `element`: 대부분 `value` (리프 struct의 단일 필드)
2. **토픽명**: 구현 시 정의 (예: `Vehicle_Powertrain_CombustionEngine_Speed`)
3. **IDL → Python 빌드**: `generate_py_dataclass.sh`와 유사한 절차로 idlc 실행 후 pip install

---

## 3. 실제 사용을 위한 IDL 작성 절차

### 3.1 전체 플로우

```
┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│ VSS vspec        │───▶│ vss-tools ddsidl    │───▶│ IDL 생성         │
│ (construction_   │    │ 또는 후처리 스크립트 │    │ (필요 시 수정)   │
│  machinery.vspec)│    │                     │    │                  │
└──────────────────┘    └─────────────────────┘    └────────┬─────────┘
                                                           │
                                                           ▼
┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│ mapping.yml      │◀───│ vss2mapping 스크립트 │◀───│ IDL + VSS 트리   │
│ (수동 또는 자동) │    │ (신규 개발 권장)     │    │                  │
└──────────────────┘    └─────────────────────┘    └──────────────────┘
         │
         ▼
┌──────────────────┐    ┌─────────────────────┐
│ Cyclone idlc     │───▶│ Python dataclass    │───▶ kuksa-dds-provider
│ -l py -x final   │    │ (pip install)       │     구독/발행
└──────────────────┘    └─────────────────────┘
```

### 3.2 단계별 절차

| 단계 | 작업 | 산출물 |
|------|------|--------|
| 1 | vspec에서 IDL 생성 | `vspec export ddsidl --vspec specs/xxx.vspec -o our.idl` |
| 2 | (선택) 브랜치 단위 struct 병합 | `IDL_IMPROVEMENT_SOLUTIONS.md` 참고, 후처리 스크립트 |
| 3 | mapping.yml 생성 | vss2mapping 스크립트 또는 수동 작성 |
| 4 | idlc로 Python 생성 | `idlc -l py -x final our.idl` |
| 5 | 패키지 설치 | `pip install .` (setup.py/pyproject.toml 필요) |
| 6 | generate_py_dataclass.sh 수정 | 우리 IDL 경로 반영 |
| 7 | DDS Publisher 구현 | 건설기계 데이터를 DDS로 발행하는 코드 |

### 3.3 mapping.yml 예시 (IDL-Sample 구조)

```yaml
Vehicle.Powertrain.CombustionEngine.Speed:
  description: "Engine speed measured as rotations per minute."
  databroker:
    datatype: UINT16
  source:
    Vehicle_Powertrain_CombustionEngine_Speed:
      transform:
        math: {}
        formula:
          nominator: 1
          denominator: 1
          offset: 0
      typename: Vehicle.Powertrain.CombustionEngine.Speed
      element: value

Vehicle.Powertrain.CombustionEngine.ECT:
  description: "Engine coolant temperature."
  databroker:
    datatype: FLOAT
  source:
    Vehicle_Powertrain_CombustionEngine_ECT:
      transform:
        math: {}
        formula:
          nominator: 1
          denominator: 1
          offset: 0
      typename: Vehicle.Powertrain.CombustionEngine.ECT
      element: value
```

---

## 4. IDL 외 추가 개발 필요 사항

### 4.1 필수 항목

| 항목 | 설명 |
|------|------|
| **mapping.yml** | VSS 경로 ↔ DDS 토픽 ↔ typename ↔ element 매핑 정의 (vss2mapping 자동 생성 권장) |
| **vss2mapping 스크립트** | IDL 파싱 또는 vspec 기반으로 mapping.yml 자동 생성 |
| **generate_py_dataclass.sh 수정** | 프로젝트 vspec/IDL 경로 및 의존성 반영 |
| **DDS Publisher** | 실제 데이터 소스(CAN/J1939 등)에서 DDS로 발행 (kuksa의 KML 재생 역할) |

### 4.2 선택(권장) 항목

| 항목 | 설명 |
|------|------|
| **IDL 후처리** | 리프당 struct → 브랜치당 struct 병합 (토픽 수 축소) |
| **transforms.yaml** | J1939 SLOT(Factor/Offset) 등 물리값 변환 규칙 |
| **토픽명 규칙** | `Vehicle_Powertrain_CombustionEngine_Speed` 등 네이밍 컨벤션 정의 |

### 4.3 J1939/건설기계 연동 시

| 항목 | 설명 |
|------|------|
| **DBC→DDS 게이트웨이** | CAN/DBC 수신 → DDS 발행 (또는 kuksa-can-provider와 연동) |
| **transforms.yaml** | J1939 raw ↔ VSS physical 변환 규칙 |
| **SLOT 메타데이터** | Factor, Offset 등 변환 파라미터 정의 |

---

## 5. 우선순위 및 로드맵

| 순위 | 항목 | 작업 | 난이도 |
|------|------|------|--------|
| 1 | IDL 생성 | construction_machinery.vspec → ddsidl export | 하 |
| 2 | mapping.yml 자동 생성 | vss2mapping 스크립트 | 중 |
| 3 | generate_py_dataclass.sh 수정 | 프로젝트 IDL 경로 반영 | 하 |
| 4 | kuksa-dds-provider 빌드/실행 | 테스트 및 검증 | 중 |
| 5 | DDS Publisher 구현 | 실제 데이터 소스 연동 | 중~상 |
| 6 | (선택) IDL 구조 단순화 | 브랜치 단위 struct 병합 | 중 |
| 7 | (선택) transforms.yaml | J1939 SLOT 연동 | 중 |

---

## 6. 아키텍처 이해: vss-tools, vss2ddsmapper, IDL 매핑

### 6.1 vss-tools와 vss2ddsmapper의 역할

| 구성요소 | 시점 | 입력 | 출력 |
|----------|------|------|------|
| **vss-tools (vspec2ddsidl)** | 빌드 시 | vspec | IDL |
| **vss2ddsmapper.py** | 런타임 | mapping.yml | DDS 구독/데이터 추출용 매핑 딕셔너리 |

둘 다 사용되며, **서로 다른 목적**을 가집니다. vss2ddsmapper가 vss-tools를 대체하는 것이 아닙니다.

### 6.2 vss-tools IDL = 중간 산출물

vss-tools가 생성하는 IDL은 **VSS를 IDL 문법으로 변환한 중간 산출물**입니다.

- 실제 DDS 네트워크에서 **쓸 수도 있고 안 쓸 수도 있음**
- "VSS 신호를 DDS로 표현할 때 쓰는 가능한 스키마 중 하나"일 뿐

### 6.3 매핑의 본질: IDL(VSS) ↔ IDL(실제 DDS)

매핑은 **VSS 경로를 vspec에 직접 연결하는 게 아니라**, 두 IDL 세계를 연결합니다.

| 구분 | 의미 |
|------|------|
| **IDL(VSS)** | vss-tools가 vspec에서 생성한 IDL (VSS 구조 그대로) |
| **IDL(실제 DDS)** | 실제 DDS에서 publish/subscribe에 쓰는 타입 (ROS2, 자체 정의 등) |

mapping.yml은 다음을 매핑합니다:

- **VSS 경로** (Databroker가 아는 키)
- **DDS (topic + typename + element)** (실제 네트워크에서 사용하는 IDL)

**패턴 A:** vss-tools IDL을 DDS에 그대로 사용 → 1:1, element=`value`  
**패턴 B:** 외부 IDL 사용 (예: ROS2 `sensor_msgs.msg.NavSatFix`) → 1 struct가 여러 VSS 신호에 매핑

### 6.4 개발자 관점: 몰라도 되는 것

일반 개발자는 다음을 알 필요 없습니다.

| 몰라도 됨 | 설명 |
|-----------|------|
| IDL(VSS) vs IDL(실제 DDS) 구분 | 내부 설계 개념 |
| vss-tools IDL이 "중간 산출물"인지 | 빌드 파이프라인 세부 |
| vss2ddsmapper 내부 동작 | 라이브러리 구현 상세 |

**필요한 것만:**

| 역할 | 필요한 지식 |
|------|-------------|
| DDS Publisher 작성 | 토픽명, typename, 발행할 필드 |
| Databroker 사용 | VSS 경로로 구독/발행 |
| mapping.yml 편집 | 신호 추가 시 VSS 경로 ↔ topic/typename/element 정의 |

---

## 7. 관련 문서

- [IDL_IMPROVEMENT_SOLUTIONS.md](./IDL_IMPROVEMENT_SOLUTIONS.md) – IDL 구조 개선, mapping.yaml 자동 생성, J1939 변환 등 상세 설계
- [ARCHITECTURE.md](./ARCHITECTURE.md) – DDS 아키텍처 개요
- [IMPROVEMENT_PROPOSAL.md](./IMPROVEMENT_PROPOSAL.md) – 개선 제안
