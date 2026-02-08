# 건설기계 VSS 트리 구조 도식화

이 문서는 `construction_machinery.vspec` 파일의 브랜치와 주요 신호를 tree 구조로 도식화한 것입니다.

## 전체 트리 구조

```
Vehicle
├── VehicleIdentification (branch)
│   ├── Type (attribute, string) - 건설기계 타입
│   ├── VIN (attribute, string) - 차량 식별 번호
│   ├── Brand (attribute, string) - 제조사 브랜드
│   └── Model (attribute, string) - 모델명
│
├── Powertrain (branch)
│   ├── CombustionEngine (branch)
│   │   ├── Speed (sensor, uint16, rpm) - 엔진 속도
│   │   ├── Torque (sensor, int8, percent) - 엔진 토크
│   │   ├── Temperature (sensor, int16, celsius) - 엔진 온도
│   │   └── OilPressure (sensor, uint16, kPa) - 엔진 오일 압력
│   │
│   ├── PowerMode (branch)
│   │   ├── Mode (actuator, string) - 파워 모드 설정
│   │   └── CurrentMode (sensor, string) - 현재 파워 모드
│   │
│   ├── Transmission (branch)
│   │   ├── CurrentGear (sensor, int8) - 현재 기어 위치
│   │   ├── SelectedGear (sensor, int8) - 선택된 기어
│   │   ├── GearRatio (sensor, uint16) - 기어비
│   │   └── OilTemperature (sensor, int16, celsius) - 변속기 오일 온도
│   │
│   ├── FuelSystem (branch)
│   │   ├── Level (sensor, uint8, percent) - 연료 잔량
│   │   ├── ConsumptionRate (sensor, uint16, Lph) - 연료 소비율
│   │   └── Pressure (sensor, uint16, kPa) - 연료 압력
│   │
│   ├── TractionBattery (branch) - 구동 배터리 (전기/하이브리드)
│   │   ├── StateOfCharge (sensor, uint8, percent) - 배터리 충전 상태
│   │   ├── Temperature (sensor, int16, celsius) - 배터리 온도
│   │   └── Voltage (sensor, uint16, V) - 배터리 전압
│   │
│   └── Reservoir (branch) ⭐ - 오일 탱크 (Hydraulics에서 이동)
│       ├── Level (sensor, uint8, percent) - 오일 레벨
│       ├── Temperature (sensor, int16, celsius) - 오일 온도
│       └── OilQuality (branch)
│           ├── DielectricConstant (sensor, uint16) - 유전 상수
│           ├── Density (sensor, uint16, gpcm3) - 오일 밀도
│           └── Viscosity (sensor, uint16, cP) - 오일 점도
│
├── Chassis (branch)
│   ├── Brake (branch)
│   │   ├── ParkingBrake (sensor, boolean) - 주차 브레이크 상태
│   │   └── OilPressure (sensor, uint16, kPa) - 브레이크 오일 압력
│   │
│   ├── Steering (branch)
│   │   ├── Angle (sensor, int16, degree) - 조향 각도
│   │   ├── WheelAngle (sensor, int16, degree) - 휠 각도
│   │   └── Mode (sensor, string) - 조향 모드 (2WHEEL, 4WHEEL_ROUND, 4WHEEL_CRAB)
│   │
│   ├── Track (branch) - 트랙 시스템 (굴착기, 불도저 등)
│   │   ├── LeftSpeed (sensor, uint16, kmh) - 왼쪽 트랙 속도
│   │   └── RightSpeed (sensor, uint16, kmh) - 오른쪽 트랙 속도
│   │
│   └── Wheel (branch) - 휠 시스템 (휠로더, ADT 등)
│       └── Speed (sensor, uint16, kmh) - 휠 속도
│
├── Hydraulics (branch) ⭐ - 하이드로리식 제어 시스템
│   ├── FEHSystem (branch) ⭐ - Full Electric Hydraulic 시스템 (Powertrain에서 이동)
│   │   ├── ElectricMotor (branch)
│   │   │   ├── Speed (sensor, uint16, rpm) - FEH 모터 속도
│   │   │   └── Torque (sensor, int16, Nm) - FEH 모터 토크
│   │   ├── Pump (branch)
│   │   │   ├── Pressure (sensor, uint16, kPa) - 펌프 압력
│   │   │   └── FlowRate (sensor, uint16, Lpm) - 펌프 유량
│   │   └── PowerManagement (branch)
│   │       └── PowerDistribution (sensor, uint8, percent) - 전력 분배율
│   │
│   ├── System (branch)
│   │   ├── Pressure (sensor, uint16, kPa) - 시스템 압력
│   │   ├── Temperature (sensor, int16, celsius) - 시스템 온도
│   │   └── OilLevel (sensor, uint8, percent) - 오일 레벨
│   │
│   ├── Valve (branch)
│   │   ├── Position (sensor, uint8, percent) - 밸브 위치
│   │   └── State (sensor, string) - 밸브 상태 (BLOCK, EXTEND, RETRACT, FLOAT)
│   │
│   └── Cylinder (branch)
│       ├── Boom (branch) - 붐 실린더
│       │   ├── Position (sensor, int16, mm) - 붐 실린더 위치
│       │   ├── Speed (sensor, uint16, mms) - 붐 실린더 속도
│       │   ├── HeadPressure (sensor, uint16, bar) - 헤드 측 압력
│       │   └── RodPressure (sensor, uint16, bar) - 로드 측 압력
│       ├── Arm (branch) - 암 실린더
│       │   ├── Position (sensor, int16, mm) - 암 실린더 위치
│       │   └── Speed (sensor, uint16, mms) - 암 실린더 속도
│       └── Bucket (branch) - 버킷 실린더
│           ├── Position (sensor, int16, mm) - 버킷 실린더 위치
│           └── Speed (sensor, uint16, mms) - 버킷 실린더 속도
│
├── 작업 장치 (Work Equipment) - Vehicle 아래 직접 배치 ⭐ 이름 변경
│
├── Boom (branch) ⭐ - 붐 (굴착기용)
│   ├── Position (branch)
│   │   ├── Angle (sensor, int16, degree) - 붐 각도
│   │   └── Length (sensor, uint16, mm) - 붐 길이
│   ├── Speed (sensor, uint16, mms) - 붐 속도
│   ├── Load (sensor, uint16, kg) - 붐 하중
│   ├── Float (branch)
│   │   ├── BiDirectional (actuator, boolean) - 양방향 플로트 활성화
│   │   └── SingleDirection (actuator, boolean) - 단방향 플로트 활성화
│   └── Attachment (branch) ⭐ 신규
│
├── Arm (branch) ⭐ - 암 (굴착기용)
│   ├── Position (branch)
│   │   └── Angle (sensor, int16, degree) - 암 각도
│   ├── Speed (sensor, uint16, mms) - 암 속도
│   ├── Load (sensor, uint16, kg) - 암 하중
│   ├── AngleInfo (sensor, uint8, degree) - 암 각도 정보
│   └── Attachment (branch) ⭐ 신규
│
├── Bucket (branch) ⭐ - 버킷 (공통)
│   ├── Position (branch)
│   │   └── Angle (sensor, int16, degree) - 버킷 각도
│   ├── Load (sensor, uint16, kg) - 버킷 하중
│   ├── Weighing (branch) ⭐ - 계량 시스템
│   │   ├── Measurement (sensor, uint16, kg) - 계량 측정값
│   │   └── Status (sensor, string) - 계량 상태
│   └── Attachment (branch) ⭐ - 부착물 시스템
│       └── TiltRotator (branch)
│           ├── TiltAngle (sensor, int16, degree) - 틸트 각도
│           └── RotatorAngle (sensor, int16, degree) - 로테이터 각도
│
├── Swing (branch) ⭐ - 선회 (굴착기용)
│   ├── Angle (sensor, int32, degree) - 선회 각도
│   ├── Speed (sensor, uint16, degs) - 선회 속도
│   └── Attachment (branch) ⭐ 신규
│
├── Travel (branch) ⭐ - 주행 (굴착기용)
│   ├── Speed (sensor, uint16, kmh) - 주행 속도
│   ├── Direction (sensor, string) - 주행 방향 (FORWARD, REVERSE, NEUTRAL)
│   ├── Mode (sensor, string) - 주행 모드 (LOW_SPEED, HIGH_SPEED, AUTO_SPEED)
│   ├── TractionControl (branch) ⭐ - 견인 제어
│   │   └── Mode (actuator, string) - 견인 제어 모드 (MAX, CONTROL, SLIP)
│   └── Attachment (branch) ⭐ 신규
│
├── LiftArm (branch) ⭐ - 리프트 암 (휠로더, SSL, CTL용)
│   ├── Position (branch)
│   │   └── Height (sensor, uint16, mm) - 리프트 암 높이
│   ├── Speed (sensor, uint16, mms) - 리프트 암 속도
│   ├── Load (sensor, uint16, kg) - 리프트 암 하중
│   └── Attachment (branch) ⭐ 신규
│
└── Blade (branch) ⭐ - 블레이드 (불도저용)
    ├── Position (branch)
    │   ├── Height (sensor, int16, mm) - 블레이드 높이
    │   ├── Angle (sensor, int16, degree) - 블레이드 각도
    │   └── Tilt (sensor, int16, degree) - 블레이드 틸트
    ├── AutoMode (sensor, string) - 자동 모드
    └── Attachment (branch) ⭐ 신규
│
├── ADAS (branch) - 고급 운전자 보조 시스템
│   ├── MachineGuidance (branch) ⭐ 신규
│   │   ├── Mode2D (branch) - 2D 기계 가이던스
│   │   │   ├── GNSSPosition (branch)
│   │   │   └── TargetElevation (sensor, int32, mm) - 목표 고도
│   │   ├── Mode3D (branch) - 3D 기계 제어
│   │   │   ├── Model3D (sensor, boolean) - 3D 모델 활성화
│   │   │   └── TargetPosition (branch)
│   │   │       ├── X (sensor, float, m) - 목표 X 좌표
│   │   │       ├── Y (sensor, float, m) - 목표 Y 좌표
│   │   │       └── Z (sensor, float, m) - 목표 Z 좌표
│   │   └── VirtualWall (branch) - 가상 벽
│   │       ├── Active (sensor, boolean) - 가상 벽 활성화
│   │       └── Proximity (sensor, uint16, mm) - 접근 거리
│   │
│   ├── SurroundingAwareness (branch) ⭐ 확장
│   │   ├── HumanDetection (branch) - 사람 감지
│   │   │   └── Active (sensor, boolean) - 사람 감지 활성화
│   │   └── ObjectDetection (branch) - 사물 감지
│   │       └── Active (sensor, boolean) - 사물 감지 활성화
│   │
│   └── EmergencyStop (branch) ⭐ 확장
│       ├── Button (sensor, boolean) - 비상 정지 버튼 상태
│       ├── Remote (sensor, boolean) - 원격 비상 정지 상태
│       └── Auto (sensor, boolean) - 자동 비상 정지 상태
│
├── Connectivity (branch) - 연결성
│   ├── RemoteControl (branch) ⭐ 신규
│   │   ├── Active (sensor, boolean) - 원격 제어 활성화
│   │   ├── RemoteStart (actuator, boolean) - 원격 시동
│   │   └── RemoteStop (actuator, boolean) - 원격 정지
│   │
│   ├── DigitalKey (branch) ⭐ 신규
│   │   └── MobileKey (branch)
│   │       └── Connected (sensor, boolean) - 모바일 키 연결 상태
│   │
│   └── CurrentLocation (branch) ⭐ - 현재 위치 (병합)
│       └── GNSSReceiver (branch)
│           ├── Latitude (sensor, float, degree) - 위도
│           ├── Longitude (sensor, float, degree) - 경도
│           ├── Altitude (sensor, float, m) - 고도
│           └── Status (sensor, string) - GNSS 상태
│
├── Body (branch)
│   ├── Lights (branch)
│   │   ├── WorkLamp (actuator, boolean) - 작업등
│   │   ├── TurnSignalLeft (actuator, boolean) - 좌측 깜빡이
│   │   └── TurnSignalRight (actuator, boolean) - 우측 깜빡이
│   │
│   └── Cabin (branch) ⭐ - 운전실 (병합)
│       ├── HVAC (branch)
│       │   └── Temperature (actuator, int16, celsius) - 운전실 온도 설정
│       └── Display (branch)
│           └── Screen (branch)
│               └── Brightness (actuator, uint8, percent) - 화면 밝기
│
├── Diagnostics (branch)
│   ├── EngineDiagnostics (branch) - 엔진 진단
│   ├── HydraulicDiagnostics (branch) ⭐ - 하이드로리식 시스템 진단
│   └── WorkEquipmentDiagnostics (branch) ⭐ - 작업 장치 진단
│
├── Service (branch)
├── OBD (branch)
├── Driver (branch)
└── Exterior (branch)
```

## 주요 브랜치 통계

### 표준 VSS 브랜치
- VehicleIdentification
- Powertrain (확장됨 - Reservoir 추가)
- Chassis (확장됨)
- Body (확장됨 - Cabin 병합)
- ADAS (확장됨)
- Connectivity (확장됨 - CurrentLocation 병합)
- Diagnostics (확장됨)
- Service
- OBD
- Driver
- Exterior

### 건설기계 특화 브랜치 (신규)
1. **Hydraulics** ⭐ - 하이드로리식 제어 시스템
   - FEHSystem (Full Electric Hydraulic) - Powertrain에서 이동
   - System (압력, 온도, 오일 레벨)
   - Valve (밸브 제어)
   - Cylinder (붐/암/버킷 실린더)

2. **Powertrain.Reservoir** ⭐ - 오일 탱크 (Hydraulics에서 이동)
   - Level, Temperature
   - OilQuality (유전상수, 밀도, 점도)

3. **작업 장치 (Work Equipment)** ⭐ (이름 변경: 작업 장비 → 작업 장치)
   - Boom (붐) - Attachment 추가
   - Arm (암) - Attachment 추가
   - Bucket (버킷 - 계량 시스템, Attachment 포함)
   - Swing (선회) - Attachment 추가
   - Travel (주행 - 견인 제어, Attachment 포함)
   - LiftArm (리프트 암) - Attachment 추가
   - Blade (블레이드) - Attachment 추가

4. **ADAS 확장** ⭐
   - MachineGuidance (기계 가이던스)
   - SurroundingAwareness (주변 환경 인식)
   - EmergencyStop (비상 정지)

5. **Connectivity 확장** ⭐
   - RemoteControl (원격 제어)
   - DigitalKey (디지털 키)
   - CurrentLocation (GNSS 위치) - 병합

6. **Body 확장** ⭐
   - Cabin (운전실) - 병합

## 주요 변경사항 (2025년 업데이트)

### 구조 변경
1. ✅ **FEHSystem 병합**: `Powertrain.HydraulicPump.FEHSystem` → `Hydraulics.FEHSystem`
2. ✅ **Reservoir 이동**: `Hydraulics.Reservoir` → `Powertrain.Reservoir`
3. ✅ **Cabin 병합**: `Vehicle.Cabin` → `Vehicle.Body.Cabin`
4. ✅ **CurrentLocation 병합**: `Vehicle.CurrentLocation` → `Vehicle.Connectivity.CurrentLocation`
5. ✅ **작업 장비 → 작업 장치**: 명칭 변경
6. ✅ **Attachment 브랜치 추가**: 모든 작업 장치 하위에 Attachment 브랜치 추가

### 신호 타입 분류

#### Sensor (센서)
- 차량 상태를 읽는 읽기 전용 신호
- 예: Speed, Temperature, Pressure, Load 등

#### Actuator (액추에이터)
- 차량을 제어하는 쓰기 가능한 신호
- 예: Mode, RemoteStart, RemoteStop, WorkLamp 등

#### Attribute (속성)
- 차량의 고정 속성 정보
- 예: Type, VIN, Brand, Model

## 주요 신호 카테고리

### 1. 동력전달계 (Powertrain)
- 엔진: Speed, Torque, Temperature, OilPressure
- 변속기: CurrentGear, SelectedGear, GearRatio, OilTemperature
- 연료: Level, ConsumptionRate, Pressure
- 배터리: StateOfCharge, Temperature, Voltage
- Reservoir: Level, Temperature, OilQuality

### 2. 하이드로리식 시스템 (Hydraulics)
- FEHSystem: ElectricMotor (Speed, Torque), Pump (Pressure, FlowRate), PowerManagement
- 시스템: Pressure, Temperature, OilLevel
- 실린더: Position, Speed, HeadPressure, RodPressure
- 밸브: Position, State

### 3. 작업 장치 (Work Equipment)
- 위치: Angle, Length, Height
- 속도: Speed
- 하중: Load
- 계량: Weighing (Measurement, Status)
- 제어: Float, TractionControl, AutoMode
- Attachment: 부착물 브랜치 (모든 작업 장치에 추가)

### 4. 안전 및 보조 시스템 (ADAS)
- 기계 가이던스: 2D/3D 모드, 가상 벽
- 주변 인식: HumanDetection, ObjectDetection
- 비상 정지: Button, Remote, Auto

### 5. 연결성 (Connectivity)
- 원격 제어: Active, RemoteStart, RemoteStop
- 디지털 키: MobileKey (Connected)
- 현재 위치: GNSSReceiver (Latitude, Longitude, Altitude, Status)

## 설계 원칙

1. **표준 VSS 호환성**: 기존 VSS 브랜치 최대한 재사용
2. **건설기계 특화**: 작업 장치, 하이드로리식 시스템 등 추가
3. **계층 구조**: 명확한 브랜치 계층 구조 유지
4. **확장성**: 향후 기능 추가를 고려한 구조
5. **J1939 호환**: DBC 파일 기반 신호 정의
6. **논리적 그룹화**: 관련 기능을 논리적으로 그룹화 (예: FEH를 Hydraulics에, Reservoir를 Powertrain에)

## 참고사항

- ⭐ 표시는 건설기계 특화 브랜치/신호를 나타냅니다
- 모든 신호는 DBC 파일 (VSS_J1939.dbc)을 참고하여 정의되었습니다
- 신호 타입 (sensor/actuator/attribute)과 데이터 타입이 명시되어 있습니다
- 단위(unit)가 필요한 신호는 해당 단위가 표시되어 있습니다
- 2025년 업데이트로 구조가 변경되었습니다 (병합 및 재구성)
