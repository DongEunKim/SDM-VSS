# J1939 사양 정의 및 DBC 변환 기술표준

## 1. 개요 (Overview)

### 1.1. 목적

본 표준은 차량 내 J1939 통신 네트워크의 데이터 사양을 엑셀(Excel) 기반으로 정의하고, 이를 자동화된 파이프라인을 통해 DBC(CAN Database) 파일로 변환하기 위한 **엄격한 작성 규칙과 데이터 구조**를 규정한다. 이를 통해 수기 작성 시 발생하는 휴먼 에러를 제거하고, 물리 계층(CAN)과 논리 계층(Cloud/App) 간의 데이터 일관성을 보장한다.

### 1.2. 범위

- **포함:** J1939 메시지(PGN) 및 신호(SPN) 정의, 멀티플렉싱 구조, 데이터 타입, SLOT(Scaling) 정의.
- **제외:** 물리적 배선, 종단 저항 등 하드웨어 사양.

### 1.3. 산출물 (Artifacts)

빌드 시스템은 다음의 파일을 최종 산출물(`dist/[project_name]/[version]/`)로 생성한다.

1. **DBC Files:** 물리적 채널별로 분리된 CAN DB (예: `PCAN.dbc`, `BCAN.dbc`)
   - 파일명은 Bus 이름만 사용 (접두어 없음)
   - 모델 구분은 디렉토리 경로로 수행 (`dist/Excavator_CEABC/1.0.0/PCAN.dbc`)
2. **Full Specification:** 상속 구조가 모두 반영되어 평면화된 통합 엑셀 사양서 (예: `Excavator_CEABC_Spec.xlsx`)
3. **Configuration:** 런타임 설정 파일 (`can.conf`)
4. **VSS Mapping:** (옵션) 신호 매핑 정의서

### 1.4. 원칙

1. **Single Source of Truth:** 모든 사양은 마스터 엑셀 파일을 유일한 원본으로 하며, DBC 파일의 직접 수정은 지양한다.
2. **Explicit Definition:** SA(송신원), DA(수신처), 데이터 타입 등은 해석기의 추론에 의존하지 않고 명시적으로 정의한다.
3. **Flat Architecture:** 복잡도를 높이는 이중(Nested) 멀티플렉싱은 불허하며, 단일(Flat) 구조만 사용한다.

## 2. 사양서 파일 구조 및 스키마 (File Schema)

사양서 엑셀 파일(`Master_Spec.xlsx`)은 반드시 다음 **세 개의 시트(Sheet)**로 구성되어야 하며, 각 컬럼의 데이터 포맷을 엄격히 준수해야 한다.

### 2.1. 시트 1: `SLOT_Master` (공통 변환 규칙)

J1939-71에 정의된 SLOT(Scaling, Limit, Offset, Transfer) 또는 사내 표준 변환 공식을 정의한다.

| **컬럼명** | **필수** | **데이터 타입** | **설명 및 작성 규칙** |
| --- | --- | --- | --- |
| **SLOT Name** | O | String | 고유 식별자. `SLOT_[물리량]` 형식 권장. (예: `SLOT_Speed`, `SLOT_Temp`) |
| **Factor** | O | Float | 물리값 변환 계수. (예: `0.125`) |
| **Offset** | O | Float | 물리값 오프셋. (예: `-273`) |
| **Min** | O | Float | 물리적 최소값. |
| **Max** | O | Float | 물리적 최대값 (유효 데이터 범위). J1939 Error 영역(0xFE, 0xFF)은 제외된 값이어야 함. |
| **Unit** | X | String | 단위. (예: `rpm`, `kPa`, `%`) |
| **Description** | X | String | SLOT에 대한 설명. |

### 2.2. 시트 2: `Message_Spec` (메시지 및 신호 정의)

CAN 프레임과 신호를 정의하는 핵심 시트이다.

| **그룹** | **컬럼명** | **필수** | **데이터 타입** | **설명 및 작성 규칙** |
| --- | --- | --- | --- | --- |
| **Network** | **Bus** | O | String | 논리 채널명 (`PCAN`, `BCAN`). 명명규칙 준수. |
| **Message** | **Message Name** | O | String | 메시지 이름 (PascalCase). |
|  | **PGN (Hex)** | O | Hex String | Parameter Group Number (`0xF004`). |
|  | **Prio** | △ | Integer | 우선순위 (0~7). 미입력시 7 |
|  | **SA (Hex)** | O | Hex String | 송신 제어기 주소. |
|  | **DA (Hex)** | △ | Hex String | 수신 제어기 주소 (PDU1 필수, PDU2 `0xFF`). |
| **Timing** | **Tx Type** | O | Enum | `Cyclic`, `Event`, `OnRequest`, `Cyclic+Event`. |
|  | **Cycle Time** | △ | Integer | 주기적 전송 시간(ms). (`Cyclic` 필수) |
| **Signal** | **SPN** | O | Integer | Suspect Parameter Number. |
|  | **Signal Name** | O | String | 신호 이름. |
|  | **Start Bit** | O | Integer | 시작 비트 (0~63). |
|  | **Len (Bit)** | O | Integer | 신호 길이. |
|  | **Mux** | X | String | `M`, `m[값]`. (**Flat Mux 원칙**) |
|  | **SigType** | O | Enum | `Float`, `Int`, `Enum`, `String`. |
|  | **Initial Value** | X | Number | **초기값.** 문자열 패딩값, 미입력 시 0x0.  |
|  | **SLOT Ref** | X | String | `SLOT_Master` 참조. |
|  | **ValTable Ref** | X | String | `0=Off;1=On`. |
|  | **Description** | X | String | `ValTable_Master` 참조. |
|  | **VSS Hint** | X | String | VSS 매핑 경로. |

### 2.3. 시트 3: `ValTable_Master`

`0=Off;1=On`과 같은 열거형(Enum) 정의를 전역적으로 관리한다.

| **컬럼명** | **필수** | **설명** | **작성 예시** |
| --- | --- | --- | --- |
| **Table Name** | **O** | 고유 식별자. (`VT_` 접두어 권장) | `VT_Switch`, `VT_Gear` |
| **Definition** | **O** | 값과 의미의 쌍. 세미콜론(`;`) 구분. | `0=Off; 1=On` |
| **Description** | X | 테이블 설명. | `Standard 2-bit Switch` |

## 3. 주소(SA/DA) 및 PGN 정의 상세 가이드

J1939 프로토콜의 핵심인 29비트 ID 구성을 위해 SA와 DA는 다음 규칙에 따라 엄격하게 정의되어야 한다.

### 3.1. SA (Source Address) 정의 기준

SA는 메시지를 송신하는 물리적 ECU의 고정 주소이다. 동적 주소 할당(Address Claiming)을 사용하더라도, DBC 생성 시에는 **Preferred Address(선호 주소)**를 기준으로 고정값을 입력해야 한다.

- **포맷:** 반드시 `0x` 접두어가 포함된 16진수로 입력.
- **입력 예시:**
    - 엔진 (EMS): `0x00`
    - 변속기 (TCU): `0x03`
    - 주 컨트롤러 (EPOS/MCU/VCU): `0x21` 또는 `0x33`
    - 인포테인먼트 계기판 (GP) : `0x28`
    - 텔래매틱스 (TMS/TGU) : `0x4A`
    - 진단 장비 (Tool): `0xF9`

### 3.2. PGN 유형에 따른 DA (Destination Address) 정의 기준

DA의 입력 값은 **PGN의 범위(PDU1 vs PDU2)**에 따라 CAN ID 생성 로직에 다르게 반영된다.

**A. PDU1 영역 (Specific Message)**

- **조건:** `PGN < 0xF000` (예: `0x0000` TSC1, `0xEF00` Proprietary A)
- **특징:** 1:1 통신이므로 **수신처(DA)가 ID에 포함**되어야 한다.
- **작성 규칙:** 엑셀의 `DA (Hex)` 컬럼에 **실제 수신 제어기의 주소**를 입력해야 한다.
- **ID 생성 로직:** `(Prio << 26) | ((PGN & 0x3FF00) << 8) | (DA << 8) | SA`
    - *주의:* PGN `0xEF00`이고 DA가 `0x20`이면, 실제 CAN ID의 PGN 부분은 `0xEF20`이 된다.
    - 상기 로직은 사양 개발자가 실수로 DA 를 입력해도 이를 강제로 보정한다.

**B. PDU2 영역 (Broadcast Message)**

- **조건:** `PGN >= 0xF000` (예: `0xF004` EEC1, `0xFEF1` CruiseControl)
- **특징:** 1:N 브로드캐스트 통신이므로 특정 수신처가 없다.
- **작성 규칙:** 엑셀의 `DA (Hex)` 컬럼에는 반드시 **`0xFF` (Global)**를 입력한다.
- **ID 생성 로직:** `(Prio << 26) | (PGN << 8) | SA`
    - *주의:* 여기서 `DA` 값은 ID 생성에 관여하지 않으며, 문서적 의미(Global)만 가진다.

### 3.3. 멀티 채널 분리 정책

- 하드웨어 포트 이름(`can0`, `can1`)보다는 **기능적 이름**(`Powertrain`, `Body`) 또는 **회로도 상의 이름**(`C1`, `C2`)을 사용하는 것을 권장한다. (SW 매핑은 설정 파일에서 처리)
- 빌드 스크립트는 `Bus` 컬럼 값을 Key로 하여 DBC 파일을 분리 생성한다.
- 하나의 메시지가 여러 버스에 흐를 경우, 엑셀 행을 복제하여 각각 정의한다.
- 구분자(예: `CAN1;CAN2`)를 사용할 수 있으나 권장하지 않는다.

## 4. 명명 규칙 (Naming Convention)

일관성 있는 DBC 및 코드 생성을 위해 다음 명명 규칙을 준수해야 한다.

### 4.1. 일반 규칙

- **언어:** 영문 대소문자 및 숫자만 사용한다. (한글, 특수문자 금지)
- **구분자:** `_` (Underscore)를 사용하되, 가독성을 위해 최소화한다.
- **형식:** **PascalCase** (단어의 첫 글자는 대문자)를 기본으로 한다.

### 4.2. 메시지 명명 (Message Name)

- **형식:** `[Source]_[Function]_[Destination]_[Type]`
- **구성 요소:**
    - `Source`: 소유자 또는 전송자 노드의 약어 (예: `ECU`, `TCU`, `MCU`, `GP`)
    - `Function`: 표준 메시지는 약어(예: `EEC1`), OEM 메시지는 기능 명 약어 (예: `CETI`).
    - `Destination`: 수신자 노드의 약어 (PDU1일 경우 필수, PDU2일 경우 무시)
    - `Type`: 선택 (예시: `CMD`, `ACK`, `STAT`, `INFO`)
- **예시:**
    - 표준:  `ECU_EEC1`, `TCU_CCVS1`
    - OEM 명령: `MCU_Boom`, `Light_Body_CMD`
    - OEM 상태: `TMS_GNSS_STAT`

### 4.3. 신호 명명 (Signal Name)

- **형식:** `[Function][Unit/Attribute]`
- **구성 요소:**
    - `System`: `Engine`, `Trans`, `Hydraulic` 생략 가능
    - `Function`: `Speed`, `Temp`, `Pressure`, `Switch`.
    - `Attribute`: `Target`, `Actual`, `Status`, `Error`.
- **예시:**
    - `EngineSpeed`, `HydOilTemp`
    - `BoomAngleTarget`, `BoomAngleActual`
    - `MainSwitchStatus`

### 4.4. SPN (Suspect Parameter Number) 할당

- **J1939 표준 신호:** J1939 DA 문서에 정의된 SPN 번호를 그대로 사용한다. (예: Engine Speed = 190)
- **OEM 전용 신호:** J1939 표준과 겹치지 않도록 **524288 (0x80000)** 이상의 번호를 할당한다.

### 4.5. 채널(Bus) 명명 규칙

하드웨어 포트명이 아닌 **기능적 도메인**으로 명명한다.

- **형식:** `[Domain]CAN` (대문자 권장)
- **표준 도메인:**
    - **PCAN**: Powertrain (엔진/미션)
    - **BCAN**: Body (전장/편의)
    - **ICAN**: Info (계기판/IVI)
    - **CCAN**: Chassis (제동/조향)
- **금지:** `can0`, `can1`, `eth0` 등 OS 의존적 이름 사용 금지.

## 5. 데이터 타입 및 멀티플렉싱 정책

### 5.1. SigType (신호 유형) 정의

DBC 변환기가 데이터의 성격을 정확히 파악할 수 있도록 `SigType` 컬럼에 다음 4가지 중 하나를 반드시 명시한다.

| **SigType** | **의미** | **DBC 변환 (is_float)** | **적용 기준** |
| --- | --- | --- | --- |
| **Float** | 실수형 | `True` | Factor가 소수점이거나, 소수점 표현이 필요한 물리량 (속도, 온도, 압력). |
| **Int** | 정수형 | `False` | Factor가 1인 카운터, 시간, 주행거리(Odometer) 등 대규모 정수. |
| **Enum** | 상태값 | `False` | `Value Table`이 필수적으로 동반되는 상태/모드 신호. |
| **String** | 문자열 | `False` | VIN, 모델명 등 ASCII 데이터. (DBC 주석에 `[TYPE: STRING]` 태그 자동 삽입) |

### 5.2. 멀티플렉싱 (Multiplexing) 정책: "Only Flat Mux"

복잡성을 줄이고 해석 도구(Vector, cantools)와의 호환성을 극대화하기 위해 **이중(Nested) 멀티플렉싱은 엄격히 금지**한다.

- **금지:** `M` 신호 하위에 `m1 M` 신호가 있고, 그 아래 `m1 m5`가 있는 계층 구조.
- **허용 (Flat):** 하나의 메시지 내에 단 하나의 `M` (Multiplexor Switch)만 존재한다.
- **대안:** 하위 분기가 필요한 경우, **스위치 값의 대역(Range)**을 나누어 평면화한다.
    - *Bad:* Category(1) -> SubCmd(1=Start)
    - *Good:* CmdID (0x10=MoveStart, 0x11=MoveStop, 0x20=LightOn)

### **5.3. 메시지 전송 속성 정의 (Transmission Attributes)**

DBC 파일의 메타데이터인 `Attribute`를 생성하기 위해, 엑셀의 `Tx Type` 컬럼은 다음 4가지 표준 값 중 하나를 가져야 한다.

| **Tx Type 값** | **의미** | **DBC Attribute 매핑 (GenMsgSendType)** | **Cycle Time 입력** |
| --- | --- | --- | --- |
| **Cyclic** | 주기적 전송 | `Cyclic` | **필수** (예: 10, 100, 1000) |
| **Event** | 상태 변경 시 전송 | `Event` | 0 (또는 Debounce 시간) |
| **Cyclic+Event** | 주기적이면서 변경 시 즉시 전송 | `CyclicIfActive` | **필수** (기본 주기) |
| **OnRequest** | 요청이 있을 때만 전송 | `NoSendType` | 0 |

## 6. 산출물 상세 정의 및 생성 규칙

### 6.1. DBC 파일 (Runtime Binary)

빌드 시스템은 다음 방식으로 DBC 파일을 생성한다:

**방식: Bus별 분리 (권장)**
- `Bus` 컬럼 값을 기준으로 분리 생성
- 예: `PCAN.dbc`, `BCAN.dbc`
- 각 파일에는 해당 Bus의 모든 메시지(J1939 표준 + OEM) 포함
- 파일명은 Bus 이름만 사용 (접두어 없음)
- 모델 구분은 디렉토리 경로로 수행 (`dist/Excavator_CEABC/1.0.0/PCAN.dbc`)

> **참고:** 실제 ECU 및 SW가 참조하는 런타임 파일입니다.

### 6.2. 런타임 설정 파일 (`can.conf`)

- INI 포맷.
- **생성 로직:**
    1. `[default]` 섹션에 공통 설정(interface, bitrate 등) 기술.
    2. 엑셀의 `Bus` 컬럼 값을 **Section Name**(`[PCAN]`)으로 생성.
    3. 생성된 DBC 파일명을 커스텀 키 **dbc_file**로 추가.
- **생성된 파일 예시 (`can.conf`):**
    
    ```toml
    [default]
    interface = socketcan # 제어기별 설정
    bitrate = 250000
    
    [PCAN]
    # 엑셀의 'Bus' 컬럼이 섹션명이 됨
    channel = can0 # 제어기별 설정
    bitrate = 500000
    dbc_file = PCAN.dbc
    usage = powertrain_control
    
    [BCAN]
    channel = vcan1  # 제어기별 설정
    bitrate = 500000
    dbc_file = BCAN.dbc
    usage = body_control
    ```
    

### 6.3. 통합 사양서 (`Generated Excel`)

개발자가 아닌 이해관계자(기획, 검증, 협력사)를 위해, 상속된 모든 사양이 하나로 합쳐진 엑셀 파일을 생성한다.

- **파일명 규칙:** `[Layer1]_[Layer2]_...[Model Name]_[Build Date]_[Version].xlsx`
    - 예: `Excavator_Electric_CEABC_20251020.xlsx`
- **포함 내용:**
    - **Cover Sheet:** 빌드 정보(날짜, 버전), **"자동 생성된 파일이므로 수정 금지"** 경고 문구 포함.
    - **SLOT_Master:** 참조된 모든 SLOT 정의.
    - **Message_Spec:** 공통 사양과 모델 전용 사양이 합쳐지고, 충돌이 해결된 최종 리스트.
- **스타일링 (권장):** 자동 생성됨을 시각적으로 알리기 위해, 헤더 색상을 변경(예: 회색)하거나 시트 보호(Password Protected)를 걸어 생성을 권장한다.

## 7. 작성 예시 (Comprehensive Example)

아래는 본 표준의 모든 규칙(PDU1/2, SPN, SA/DA, SigType, Flat Mux)을 준수한 엑셀 작성 예시이다.

### 시트: `Message_Spec`

| **Bus** | **Message Name** | **PGN** | **Prio** | **SA** | **DA** | **SPN** | **Signal Name** | **Start Bit** | **Len (Bit)** | **Mux** | **SigType** | **SLOT Ref** | **ValTable Ref** | **VSS Hint** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PCAN | **EEC1** | F004 | 3 | 00 | FF | 190 | **EngineSpeed** | 24 | 16 |  | **Float** | SLOT_Speed |  | Vehicle.Powertrain.Engine.Speed |
| PCAN | **EEC1** | F004 | 3 | 00 | FF | 512 | **DriverDemandTorque** | 0 | 8 |  | **Float** | SLOT_Percent |  | Vehicle.Powertrain.Engine.Request |
| PCAN | **TSC1_Eng** | 0000 | 3 | 03 | **00** | 695 | **EngOverrideMode** | 0 | 2 |  | **Enum** |  | VT_Switch |  |
| PCAN | **TSC1_Ret** | 0000 | 3 | 03 | **10** | 695 | **RetOverrideMode** | 0 | 2 |  | **Enum** |  | VT_Switch |  |
| ICAN | **OEM_Cmd** | EF00 | 3 | 21 | 00 | 524288 | **CmdID** | 0 | 8 | **M** | **Enum** |  | VT_CmdID |  |
| ICAN | **OEM_Cmd** | EF00 | 3 | 21 | 00 | 524289 | **TargetRPM** | 8 | 16 | **m10** | **Float** | SLOT_Speed |  |  |
| ICAN | **OEM_Cmd** | EF00 | 3 | 21 | 00 | 524290 | **FanSpeedDuty** | 8 | 8 | **m20** | **Float** | SLOT_Percent |  |  |
| PCAN;ICAN | **VIN_Msg** | FEEC | 6 | 00 | FF | 237 | **VehicleID** | 0 | 64 |  | **String** |  |  | Vehicle.VIN |

## 8. 유효성 검증 규칙 (Validation Rules)

DBC 변환 전, 스크립트는 다음 사항을 자동으로 검증해야 한다.

| **카테고리** | **검증 항목 (Rule Name)** | **심각도** | **상세 검증 로직 및 기준** |
| --- | --- | --- | --- |
| **구조적 무결성**
(Structure) | **비트 중복 할당**
(Bit Overlap) | **Error** | • 동일 메시지 내에서 신호 간 비트 영역 충돌 금지.
• *예외:* 서로 다른 `Mux ID`를 가진 신호 간의 중첩은 허용 (단, 동일 Mux ID 내 중첩은 불가). |
|  | **멀티플렉서 구조 오류**
(Mux Logic | **Error** | • `m`(Sub) 신호 존재 시 반드시 대응하는 `M`(Master) 신호 필요.
• **이중 Mux 금지:** `m1 m5`와 같은 중첩(Nested) 구조 사용 시 에러 처리.
• `SigType=Enum`이 아닌 신호는 `M` 스위치가 될 수 없음. |
| **프로토콜 준수**
(Protocol) | **PDU1 DA 적합성**
(Specific Msg) | Warn | • `PGN < 0xF000` (PDU1)인 경우, `DA` 값은 `0x00`~`0xFE` 사이여야 함.
• `DA`가 비어있으면 경고(Warning) 후 `0xFF`로 강제 변환. |
|  | **PDU2 DA 적합성**
(Broadcast Msg) | Warn | • `PGN ≥ 0xF000` (PDU2)인 경우, `DA` 값은  `0xFF`여야 함.
• 특정 주소 기입 또는 비어있으면 경고(Warning) 후 `0xFF`로 강제 변환. |
|  | **주소 범위 유효성**
(Valid Address) | **Error** | • `SA`, `DA` 값은 유효 범위(`0x00`~`0xFD`, `0xFE`, `0xFF`) 내에 존재해야 함. |
|  | **PGN 일관성**
(PGN Consistency) | **Error** | • `Bus`가 다르더라도 신호 구조(Layout)가 동일해야 함.
• `SA`, `DA` ,`Prio` 가 다르더라도 신호 구조(Layout)가 동일해야 함. |
| **데이터 무결성**
(Data & Type) | **초기값 유효성**
(Init Value) | **Error** | • `Initial Value`는 해당 신호의 Bit Length로 표현 가능한 범위 내여야 함.
• `Enum` 타입인 경우, `Value Table`에 정의된 Key 값 중 하나여야 함. |
|  | **물리 범위 논리**
(Min/Max) | Warn | • 물리적 `Min` 값은 `Max` 값보다 작아야 함 (`Min < Max`).
• `Initial Value`가 물리적 범위(`Min`~`Max`)를 벗어나면 경고. |
|  | **Value Table 참조 오류**
(Missing Reference) | **Error** | • `Message_Spec`에 적힌 `ValTable Ref` 값이 `ValTable_Master` 시트에 존재하는지 확인.
• 존재하지 않는 테이블 참조 시 에러. |
|  | **Enum 정의 누락**(Missing Definition) | Error | • `SigType`이 `Enum`인데 `ValTable Ref`가 비어있으면 에러. |
| **명명 및 중복**
(Naming) | **메시지 이름 중복**
(Msg Name) | **Error** | • 전체 사양을 통틀어 메시지 이름(`Message Name`)은 유일해야 함. |
|  | **신호 이름 중복**
(Sig Name) | **Error** | • **동일 메시지 내**에서 신호 이름(`Signal Name`)은 유일해야 함. |
|  | **SPN 정의 일관성**
(Global SPN) | Warn | • 전사적으로 동일한 `SPN` 번호(예: 190) 사용 시, `Factor`, `Offset`, `Unit` 속성이 모든 엑셀 파일에서 일치하는지 검사. |
| **타이밍/보안**
(Timing/IDS) | **필수 타이밍 누락**
(Missing Attr) | **Error** | • `Tx Type=Cyclic` → `Cycle Time >= 5` 필수. |

## **9. 관리 및 운영 규칙 (Management & Operations)**

데이터의 무결성을 유지하고 다기종 파생 모델을 효율적으로 관리하기 위해, 사양서(Excel)와 산출물(DBC)은 다음의 계층 구조 및 운영 원칙에 따라 관리되어야 한다.

### **9.1. 데이터 계층 및 상속 구조 (Data Hierarchy)**

사양 정의는 **"표준(Level 0) → 공통 (Level 1~) → 기종"** 순서의 상속(Inheritance) 구조를 가지며, 하위 계층은 상위 계층의 정의를 자동으로 포함(Include)하거나 오버라이드(Override)한다.

**디렉토리 명명 규칙:**
- Level 1: `00_common` (전사 공통)
- Level 2: `10_[equipment_type]` (예: `10_excavator`, `20_wheel_loader`)
- Level 3: `11_[sub_type]` (예: `11_diesel`, `12_electric`)
- Level 4: `01_[model_name]` (예: `01_CEABC`)

> **참고:** 숫자 접두어는 정렬 순서를 보장하기 위함입니다.

1. **Level 0: Global Standard (J1939 Standard)**
    - **내용:** SAE J1939 표준에 정의된 모든 PGN/SPN 및 SLOT 정의.
    - **형태:** `specs/j1939_standard.xlsx` (필요한 신호만 정의).
    - **관리:** 외부 표준 변경 시에만 업데이트.
2. **Level 1: Equipment Generation**
    - **내용:** 전사적으로 사용되는 OEM 공통 메시지, 공통 응답(ACK) 정책, 표준 `SLOT_Master` 시트.
    - **형태:** `specs/00_common/common_spec.xlsx`.
    - **규칙:** 모든 차종은 이 파일을 기본으로 상속받아야 한다.
3. **Level 2: Equipment Type**
    - **내용:** 전사적으로 사용되는 장비 종류 별 공통 메시지
    - **형태:** `specs/00_common/10_excavator/excavator_spec.xlsx`.
    - **규칙:** 모든 차종은 이 파일을 기본으로 상속받아야 한다.
4. **Level 3: Equipment Sub Type**
    - **내용:** 서브 장비 종류 별 공통 메시지, 필요 시에만 정의
    - **형태:** `specs/00_common/10_excavator/12_electric/electric_spec.xlsx`.
    - **규칙:** 모든 차종은 이 파일을 기본으로 상속받아야 한다.
5. **Level 4: Model Specific (세부 모델)**
    - **내용:** 특정 모델 전용 신호
    - **형태:** `specs/00_common/10_excavator/12_electric/01_CEABC/CEABC_spec.xlsx`.

### **9.2. 원천 데이터 불변의 원칙 (Source of Truth)**

모든 데이터 흐름은 **"엑셀(Source) → 변환기(Tool) → DBC(Artifact)"**의 단방향 흐름만을 허용한다.

1. **Rule 1: DBC 수정 금지**
    - 최종 산출물인 `.dbc`, `.json` 파일은 **빌드 시스템에 의해 자동 생성되는 파일**이다.
    - 어떠한 경우에도 DBC 파일을 텍스트 에디터나 CANdb++로 **직접 열어서 수정(Manual Edit)하는 것을 엄격히 금지**한다.
    - 수정이 필요할 경우, 반드시 원본 엑셀(`Master_Spec.xlsx`)을 수정한 후 변환 스크립트를 재실행해야 한다.
2. **Rule 2: 변경 추적**
    - 사양 변경 시, 버전을 기입하고 산출물에도 반영한다.
    - 배포 및 형상 관리 참조
3. **Rule 3: Git 기반 추적 (필요시)**
    - 생성된 DBC 파일의 헤더(Header) 또는 속성(Attribute)에는 반드시 해당 빌드에 사용된 **Git Commit Hash**와 **빌드 날짜**가 자동으로 기입되어야 한다.

### **9.3. 배포 및 형상 관리 (Release Process)**

1. **빌드(Build):** CI/CD 파이프라인을 통해 `specs/` 하위의 모든 엑셀 파일을 감지하여 모델별 DBC를 일괄 생성한다.
2. **검증(Validation):** 생성된 DBC에 대해 `Validate Script`를 수행하여 PDU1 DA 누락, SPN 중복 등을 자동 검사한다.
3. **배포(Deploy):** 검증을 통과한 DBC 파일만 `dist/` 폴더 또는 아티팩트 저장소(Nexus 등)에 업로드하며, 이때 시맨틱 버저닝(`v1.0.0`) 태그를 부여한다.

### 9.4. 산출물 생성 규칙 (Output Generation) **[보강]**

빌드 시스템은 각 모델의 `manifest.yaml`을 기준으로 산출물을 생성한다. 산출물은 용도(시스템용 vs 참조용)에 따라 명명 규칙을 달리 적용하며, 모델 간의 구분은 **출력 디렉토리**를 통해 수행한다.

**9.4.1. 파일명 명명 규칙 (Filename Convention)**

| **파일 구분** | **명명 패턴** | **예시** | **비고** |
| --- | --- | --- | --- |
| **DBC 파일** | `[BusName].dbc` | `PCAN.dbc`
`BCAN.dbc` | **[시스템용]**
제어기 SW 참조 편의를 위해 접두어 없이 **고정된 이름** 사용. |
| **설정 파일** | `can.conf` | `can.conf` | **[시스템용]**
런타임 고정 설정 파일. |
| **통합 사양서**
(Merged Excel) | `[Project]_Spec.xlsx` | `Excavator_CEABC_Spec.xlsx` | **[참조용]**
사람 간 공유 및 식별을 위해 **프로젝트명과 버전**을 파일명에 포함. |

**9.4.2. 디렉토리 구조 (Directory Structure)**

`project_name`과 `version`을 사용하여 모델별로 완전히 격리된 배포 폴더를 생성한다.

- **Output Path:** `dist/[project_name]/[version]/`

```yaml
dist/
└── Excavator_CEABC/          # [project_name]
    └── 1.0.0/                # [version]
        ├── PCAN.dbc          # 논리 채널 1 (Bus별 분리)
        ├── BCAN.dbc          # 논리 채널 2 (Bus별 분리)
        ├── can.conf          # 런타임 설정
        └── Excavator_CEABC_Spec.xlsx  # 통합 참조 사양서
```

**산출물 구조 통합 규칙:**
- 모든 산출물은 `dist/[project_name]/[version]/` 디렉토리 하위에 생성
- DBC 파일은 Bus별로 분리하여 생성 (접두어 없이 Bus 이름만 사용)
- 모델 구분은 디렉토리 경로로 수행하므로 파일명에 모델명 포함 불필요
- 통합 사양서는 참조용이므로 프로젝트명과 버전을 파일명에 포함

### 9.5. 상속 및 중복 정의 처리 규칙 (Inheritance & Override Policy)

계층화된 사양서 구조에서 동일한 메시지가 중복 정의되었을 때의 처리 기준을 규정한다.

### 9.5.1. 중복(Collision)의 판단 기준 (Unique Key)

빌드 시스템은 다음 속성들이 모두 일치할 경우, 서로 다른 파일에 정의되어 있더라도 "동일한 메시지"로 간주한다.

1. **Bus:** 물리 채널 (예: `PCAN`)
2. **PGN:** Parameter Group Number (예: `0xF004`)
3. **SA:** Source Address (예: `0x00`)
4. **DA:** Destination Address
   - **PDU1 (`PGN < 0xF000`)**: 실제 수신 제어기 주소 (예: `0x00`, `0x20`)
     - DA 값이 CAN ID 생성에 직접 관여하므로 중복 판단에 필수
   - **PDU2 (`PGN >= 0xF000`)**: 항상 `0xFF`이므로 중복 판단에서 제외 가능
     - 단, 문서적 일관성을 위해 DA 컬럼 값(`0xFF`)도 확인 권장

> **주의:** 메시지 이름(Message Name)이 다르더라도 위 키가 같으면 CAN ID가 동일하므로 중복으로 처리된다.
> 

### 9.6.2. 덮어쓰기 원칙 (Last Write Wins)

하위 계층(모델)의 정의가 상위 계층(공통)의 정의보다 **항상 우선**한다.

- **원칙:** **Message-Level Override (메시지 단위 교체)**
    - 하위 계층에서 동일 키(Bus+PGN+SA+DA)를 가진 메시지를 정의하면, 상위 계층의 해당 메시지 정의(신호 목록 전체)를 **완전히 무시하고 하위 계층의 정의로 통째로 교체**한다.
    - *이유:* 신호 단위로 병합(Merge)할 경우, 비트 할당(Start Bit) 충돌이나 의도치 않은 데이터 오염이 발생할 위험이 크기 때문이다.

### 9.6.3. 예외: 부분 병합 금지

- 상위 계층의 메시지에서 **"특정 신호 하나만 바꾸고 싶다"**고 하더라도, 하위 계층 엑셀에는 **해당 메시지의 모든 신호를 온전하게 다시 작성**해야 한다.
- 이는 DBC의 무결성(Bit Map Integrity)을 보장하기 위함이다.

### 9.7. 빌드 매니페스트 작성 표준 (Build Manifest)

다단계 계층 구조(Level 0 ~ Level 4)로 세분화된 사양서들을 완벽한 DBC로 조립하기 위해, 각 디렉토리에는 반드시 **`manifest.yaml`** 파일이 존재해야 한다.

**9.7.1. 파일 구조 (Schema)**

| **Key** | **필수** | **설명** |
| --- | --- | --- |
| **project_name** | O | 프로젝트 또는 모델명. (산출물 파일명 접두어) |
| **version** | O | 사양서 버전. (예: `1.0.0`) |
| **base_definitions** | O | 전역 정의 파일 리스트. (SLOT, ValueTable) |
| **inheritance** | O | 병합할 엑셀 파일 경로 리스트.
**Level 0 → Level 4 순서로 기입 필수.** (뒤에 오는 파일이 앞의 내용을 덮어씀) |

### 9.8.2. 상속 경로 구성 전략 (Inheritance Strategy)

매니페스트의 `inheritance` 리스트는 사용자 정의 계층 구조(9.1항)에 따라 다음 순서를 엄격히 준수해야 한다.

1. **Level 0 (Standard):** `j1939_standard.xlsx` (J1939 표준 PGN)
2. **Level 1 (Generation):** `common_spec.xlsx` (OEM 공통 정책)
3. **Level 2 (Type):** `excavator_spec.xlsx` (장비군 공통)
4. **Level 3 (Sub-Type):** `electric_spec.xlsx` (서브 타입, 옵션)
5. **Level 4 (Model):** `model_spec.xlsx` (모델 전용)

### 9.8.3. 작성 예시 (`manifest.yaml`)

**시나리오:** "전기 굴착기 CEABC 모델"을 위한 매니페스트 작성 예시.

```yaml
# File: specs/00_common/10_excavator/12_electric/01_CEABC/manifest.yaml

# [프로젝트 설정]
# 이 이름으로 dist 폴더가 생성됨 (예: dist/Excavator_CEABC/)
project_name: "Excavator_CEABC"  
version: "1.0.0"

# [전역 정의]
base_definitions:
  - "specs/slot_master.xlsx"
  - "specs/valtable_master.xlsx"

# [상속 구조]
inheritance:
  - "specs/j1939_standard.xlsx"
  - "specs/00_common/common_spec.xlsx"
  - "specs/00_common/10_excavator/excavator_spec.xlsx"
  - "specs/00_common/10_excavator/12_electric/electric_spec.xlsx"
  - "specs/00_common/10_excavator/12_electric/01_CEABC/CEABC_spec.xlsx"
```

---

## 부칙

1. 본 표준에 따라 생성된 DBC는 `Vector CANdb++`에서 "J1939 호환 모드"로 완벽하게 열려야 한다.
2. 명시되지 않은 사항은 SAE J1939 표준을 따른다.