# 건설기계 VSS Tree (최종 제안)

## 개요
표준 VSS 구조와 호환되도록 최적화한 건설기계용 VSS Tree입니다.

### 핵심 원칙
1. **표준 VSS 호환성**: 기존 VSS Branch 최대한 재사용
2. **WorkEquipment 상위 노드 없음**: 작업 장비는 Vehicle 아래 직접 배치 (Trailer, CurrentLocation과 동일)
3. **제품별 분리 없음**: 공통 구조 사용, 제품 타입은 속성으로 표현
4. **기능 그룹 최적화**: Control → Connectivity, Safety → ADAS, Attachment → 작업 장비 하위
5. **유압 시스템 하이브리드**: 펌프는 Powertrain, 제어는 Hydraulics

---

## 최종 VSS Tree 구조

```
Vehicle
├── VehicleIdentification
│   └── Type (속성: Excavator, WheelLoader, SSL, CTL, Dozer, ADT, Forklift)
│
├── Powertrain (표준 VSS 확장)
│   ├── CombustionEngine
│   ├── ElectricMotor
│   ├── Transmission
│   ├── FuelSystem
│   ├── TractionBattery (전기/하이브리드)
│   └── HydraulicPump (신규) ⭐ FEH 시스템
│       └── FEHSystem
│           ├── ElectricMotor
│           ├── Pump
│           └── PowerManagement
│
├── Chassis (표준 VSS 확장)
│   ├── Axle
│   ├── Wheel (휠로더, ADT, 지게차)
│   ├── Track (굴착기, CTL, Dozer)
│   ├── Brake
│   ├── Steering
│   └── Suspension
│
├── Body (표준 VSS 확장)
│   ├── Lights
│   ├── Mirrors
│   └── Windshield
│
├── Cabin (표준 VSS 확장)
│   ├── Seat
│   ├── HVAC
│   ├── Display
│   └── Controls
│
├── Hydraulics (신규) - 하이드로리식 제어 시스템
│   ├── System
│   ├── Valve
│   ├── Cylinder
│   ├── Motor
│   ├── Reservoir
│   └── Cooling
│
├── ADAS (표준 VSS 확장) - 작업 보조 및 안전
│   ├── ABS (표준)
│   ├── ESC (표준)
│   ├── MachineGuidance (신규) ⭐
│   │   ├── 2DMG
│   │   ├── 3DMC
│   │   ├── VirtualWall
│   │   └── ARGuidance (TransparentBucket 포함)
│   ├── SurroundingAwareness (확장) ⭐
│   │   ├── HumanDetection
│   │   ├── ObjectDetection
│   │   └── HazardDetection
│   ├── EmergencyStop (확장) ⭐
│   │   ├── EStopButton
│   │   ├── RemoteEStop
│   │   └── AutoEStop
│   └── AutonomousOperation (신규) ⭐
│       ├── AutonomousExcavation
│       ├── AutonomousLoading
│       ├── AutonomousDriving
│       └── TaskPlanning
│
├── Connectivity (표준 VSS 확장) - 원격 제어 및 접근
│   ├── RemoteControl (신규) ⭐
│   │   ├── RemoteOperation
│   │   ├── RemoteStartStop
│   │   └── RemoteMonitoring
│   └── DigitalKey (신규) ⭐
│       ├── MobileKey
│       ├── AccessControl
│       └── KeySharing
│
├── CurrentLocation (표준 VSS 확장)
│   ├── GNSSReceiver
│   └── MachineGuidance (GNSS 기반 가이던스 데이터)
│
├── Diagnostics (표준 VSS 확장)
│   ├── EngineDiagnostics
│   ├── FEHDiagnostics (신규) ⭐
│   ├── HydraulicDiagnostics
│   └── WorkEquipmentDiagnostics
│
├── Service (표준 VSS)
│
├── OBD (표준 VSS)
│
├── Driver (표준 VSS)
│
├── Exterior (표준 VSS)
│
├── Occupant (표준 VSS)
│
│
│=== 작업 장비 (Work Equipment) - Vehicle 아래 직접 배치 ===
│
├── Boom (굴착기용)
│   ├── Position
│   ├── Speed
│   ├── Load
│   └── Angle
│
├── Arm (굴착기용)
│   ├── Position
│   ├── Speed
│   └── Load
│
├── Bucket (공통 - 굴착기, 휠로더, SSL, CTL)
│   ├── Position
│   ├── Angle
│   ├── Load
│   └── Attachment (신규) ⭐
│       ├── TiltRotator
│       └── AttachmentRecognition
│
├── LiftArm (휠로더, SSL, CTL용)
│   ├── Position
│   ├── Speed
│   └── Load
│
├── TiltCylinder (휠로더, SSL, CTL용)
│   ├── Position
│   └── Speed
│
├── Swing (굴착기용)
│   ├── Angle
│   └── Speed
│
├── Travel (굴착기용)
│   ├── Speed
│   └── Direction
│
├── Blade (불도저용)
│   ├── Position
│   ├── Angle
│   └── Tilt
│
├── Ripper (불도저용)
│   ├── Position
│   └── Angle
│
├── DumpBody (ADT용)
│   ├── Angle
│   └── Load
│
├── Articulation (ADT용)
│   └── Angle
│
├── Mast (지게차용)
│   ├── Height
│   └── Angle
│
├── Fork (지게차용)
│   ├── Height
│   ├── Spacing
│   └── Tilt
│
└── SideShift (지게차용)
    └── Position
```

---

## 상세 구조 설명

### 1. Powertrain (동력전달계)

#### 1.1 표준 VSS 확장
- `CombustionEngine`: 디젤/하이브리드 엔진
- `ElectricMotor`: 전기/하이브리드 모터
- `Transmission`: 변속기
- `FuelSystem`: 연료 시스템
- `TractionBattery`: 구동 배터리 (전기/하이브리드)

#### 1.2 HydraulicPump (신규) ⭐ FEH 시스템
```
Powertrain.HydraulicPump
├── FEHSystem
│   ├── ElectricMotor (FEH 전용 전기 모터)
│   ├── Pump (펌프 상태: 압력, 유량, 온도)
│   └── PowerManagement (전력 분배, 에너지 최적화)
```

**설명**: 하이드로리식 펌프는 동력 생성 역할이므로 Powertrain 하위에 배치

---

### 2. Hydraulics (하이드로리식 제어 시스템) - 신규

```
Hydraulics
├── System (시스템 전체 상태)
├── Valve (제어 밸브, 안전 밸브, 로드 홀딩 밸브)
├── Cylinder (붐/암/버킷/리프트 실린더)
├── Motor (선회 모터, 주행 모터)
├── Reservoir (탱크, 필터, 오일 품질)
└── Cooling (오일 쿨러, 냉각 제어)
```

**설명**: 하이드로리식 제어 시스템은 작업 장비 제어 역할이므로 별도 Branch로 분리

---

### 3. ADAS (고급 운전자 보조 시스템) - 확장

#### 3.1 표준 VSS 유지
- `ABS`, `ESC`, `TCS` 등 기존 ADAS 기능

#### 3.2 MachineGuidance (신규) ⭐
```
ADAS.MachineGuidance
├── 2DMG (2D 기계 가이던스)
│   ├── GNSSPosition
│   ├── TargetElevation
│   └── Deviation
├── 3DMC (3D 기계 제어)
│   ├── Model3D
│   ├── TargetPosition
│   └── Deviation
├── VirtualWall (가상 벽)
│   ├── BoundaryDefinition
│   ├── ProximityDetection
│   └── AutoLimit
└── ARGuidance (AR 가이던스)
    ├── TransparentBucket
    └── OverlayDisplay
```

#### 3.3 SurroundingAwareness (확장) ⭐
```
ADAS.SurroundingAwareness
├── HumanDetection (사람 감지)
│   ├── DetectionStatus
│   ├── Position
│   └── SafetyDistance
├── ObjectDetection (사물 감지)
│   ├── StaticObstacles
│   ├── DynamicObstacles
│   └── Position3D
└── HazardDetection (위험 감지)
    ├── RolloverRisk
    ├── OverloadDetection
    └── UnstableTerrain
```

#### 3.4 EmergencyStop (확장) ⭐
```
ADAS.EmergencyStop
├── EStopButton (운전실 e-Stop 버튼)
├── RemoteEStop (원격 e-Stop)
└── AutoEStop (자동 e-Stop - 위험 감지 시)
```

#### 3.5 AutonomousOperation (신규) ⭐
```
ADAS.AutonomousOperation
├── AutonomousExcavation (자율 굴착)
│   ├── WorkPath
│   ├── AutoDepthControl
│   └── ProgressTracking
├── AutonomousLoading (자율 적재)
│   ├── LoadingPath
│   └── LoadControl
├── AutonomousDriving (자율 주행)
│   ├── PathPlanning
│   ├── ObstacleAvoidance
│   └── FleetCoordination
└── TaskPlanning (작업 계획)
    ├── WorkPlan
    ├── OptimalSequence
    └── TimePrediction
```

---

### 4. Connectivity (연결성) - 확장

#### 4.1 RemoteControl (신규) ⭐
```
Connectivity.RemoteControl
├── RemoteOperation (원격 조작)
│   ├── ControlInterface
│   ├── VideoStream
│   └── Latency
├── RemoteStartStop (원격 시동/정지) ⭐
│   ├── RemoteStart
│   ├── RemoteStop
│   └── Preconditioning
└── RemoteMonitoring (원격 모니터링)
    ├── VehicleStatus
    ├── WorkProgress
    └── Diagnostics
```

#### 4.2 DigitalKey (신규) ⭐
```
Connectivity.DigitalKey
├── MobileKey (모바일 기반 키)
│   ├── AppBased
│   ├── NFC
│   └── BLE
├── AccessControl (접근 제어)
│   ├── UserPermissions
│   ├── TimeBasedAccess
│   └── AccessHistory
└── KeySharing (키 공유)
    ├── TemporaryKey
    ├── OneTimeKey
    └── KeyManagement
```

---

### 5. 작업 장비 (Work Equipment) - Vehicle 아래 직접 배치

#### 5.1 공통 작업 장비

**Bucket (공통)**
```
Bucket
├── Position
├── Angle
├── Load
└── Attachment (신규) ⭐
    ├── TiltRotator
    │   ├── TiltAngle
    │   ├── RotatorAngle
    │   └── CompositeControl
    └── AttachmentRecognition
        ├── Type
        ├── AutoSettings
        └── Calibration
```

**Weighing (웨이잉) ⭐**
- 각 작업 장비(Bucket, DumpBody 등)에 `Load` 속성으로 통합
- 또는 별도 `Weighing` Branch로 분리 가능

#### 5.2 굴착기 전용
- `Boom`: 붐 위치, 속도, 하중
- `Arm`: 암 위치, 속도, 하중
- `Swing`: 선회 각도, 속도
- `Travel`: 주행 속도, 방향

#### 5.3 휠로더/SSL/CTL 전용
- `LiftArm`: 리프트 암 위치, 속도, 하중
- `TiltCylinder`: 틸트 실린더 위치, 속도

#### 5.4 불도저 전용
- `Blade`: 블레이드 위치, 각도, 틸트
- `Ripper`: 리퍼 위치, 각도

#### 5.5 ADT 전용
- `DumpBody`: 덤프 적재함 각도, 하중
- `Articulation`: 굴절 각도

#### 5.6 지게차 전용
- `Mast`: 마스트 높이, 각도
- `Fork`: 포크 높이, 간격, 틸트
- `SideShift`: 사이드 시프트 위치

---

## VSS Tree (XMind 호환 형식)

```
# Vehicle
## VehicleIdentification
  > Vehicle identification attributes
  - Type
    > Vehicle type: Excavator, WheelLoader, SSL, CTL, Dozer, ADT, Forklift

## Powertrain
  > Powertrain data
  - CombustionEngine
  - ElectricMotor
  - Transmission
  - FuelSystem
  - TractionBattery
  - HydraulicPump (신규) ⭐
    > FEH System - Full Electric Hydraulic
    - FEHSystem
      - ElectricMotor
      - Pump
      - PowerManagement

## Chassis
  > Chassis data
  - Axle
  - Wheel
  - Track
  - Brake
  - Steering
  - Suspension

## Body
  > Body components
  - Lights
  - Mirrors
  - Windshield

## Cabin
  > Cabin components
  - Seat
  - HVAC
  - Display
  - Controls

## Hydraulics (신규)
  > Hydraulic control system
  - System
  - Valve
  - Cylinder
  - Motor
  - Reservoir
  - Cooling

## ADAS (확장)
  > Advanced Driver Assist Systems
  - ABS
  - ESC
  - MachineGuidance (신규) ⭐
    > Machine Guidance and Control
    - 2DMG
    - 3DMC
    - VirtualWall
    - ARGuidance
  - SurroundingAwareness (확장) ⭐
    > Surrounding environment awareness
    - HumanDetection
    - ObjectDetection
    - HazardDetection
  - EmergencyStop (확장) ⭐
    > Emergency stop system
    - EStopButton
    - RemoteEStop
    - AutoEStop
  - AutonomousOperation (신규) ⭐
    > Autonomous operation and driving
    - AutonomousExcavation
    - AutonomousLoading
    - AutonomousDriving
    - TaskPlanning

## Connectivity (확장)
  > Connectivity and communication
  - RemoteControl (신규) ⭐
    > Remote control system
    - RemoteOperation
    - RemoteStartStop
    - RemoteMonitoring
  - DigitalKey (신규) ⭐
    > Digital key system
    - MobileKey
    - AccessControl
    - KeySharing

## CurrentLocation (확장)
  > Current location and GNSS
  - GNSSReceiver
  - MachineGuidance (GNSS guidance data)

## Diagnostics (확장)
  > Diagnostics data
  - EngineDiagnostics
  - FEHDiagnostics (신규) ⭐
  - HydraulicDiagnostics
  - WorkEquipmentDiagnostics

## Service
  > Service data

## OBD
  > OBD data

## Driver
  > Driver data

## Exterior
  > Exterior information

## Occupant
  > Occupant data

## Boom (작업 장비 - 굴착기용)
  > Boom position and control
  - Position
  - Speed
  - Load
  - Angle

## Arm (작업 장비 - 굴착기용)
  > Arm position and control
  - Position
  - Speed
  - Load

## Bucket (작업 장비 - 공통)
  > Bucket position and control
  - Position
  - Angle
  - Load
  - Attachment (신규) ⭐
    > Attachment system
    - TiltRotator
    - AttachmentRecognition

## LiftArm (작업 장비 - 휠로더, SSL, CTL용)
  > Lift arm position and control
  - Position
  - Speed
  - Load

## TiltCylinder (작업 장비 - 휠로더, SSL, CTL용)
  > Tilt cylinder position and control
  - Position
  - Speed

## Swing (작업 장비 - 굴착기용)
  > Swing rotation control
  - Angle
  - Speed

## Travel (작업 장비 - 굴착기용)
  > Travel movement control
  - Speed
  - Direction

## Blade (작업 장비 - 불도저용)
  > Blade position and control
  - Position
  - Angle
  - Tilt

## Ripper (작업 장비 - 불도저용)
  > Ripper position and control
  - Position
  - Angle

## DumpBody (작업 장비 - ADT용)
  > Dump body position and control
  - Angle
  - Load

## Articulation (작업 장비 - ADT용)
  > Articulation angle control
  - Angle

## Mast (작업 장비 - 지게차용)
  > Mast position and control
  - Height
  - Angle

## Fork (작업 장비 - 지게차용)
  > Fork position and control
  - Height
  - Spacing
  - Tilt

## SideShift (작업 장비 - 지게차용)
  > Side shift position control
  - Position
```

---

## 주요 설계 결정사항

### 1. WorkEquipment 상위 노드 없음 ✅
- **이유**: 표준 VSS 철학 준수 (Trailer, CurrentLocation과 동일)
- **장점**: 구조 단순화, 경로 단순화 (`Vehicle.Boom` vs `Vehicle.WorkEquipment.Boom`)

### 2. 제품별 분리 없음 ✅
- **이유**: 자동차 VSS와 동일한 철학
- **구현**: `VehicleIdentification.Type` 속성으로 제품 타입 표현
- **장점**: 공통 작업 장비 재사용 (Bucket 등)

### 3. 유압 시스템 하이브리드 접근 ✅
- **Powertrain.HydraulicPump**: 동력 생성 (FEH 시스템)
- **Hydraulics**: 제어 시스템 (밸브, 실린더, 모터 등)
- **이유**: 명확한 책임 분리

### 4. 기능 그룹 최적화 ✅
- **Control → Connectivity**: RemoteControl, DigitalKey
- **Safety → ADAS**: SurroundingAwareness, EmergencyStop
- **Guidance → ADAS**: MachineGuidance
- **Autonomous → ADAS**: AutonomousOperation
- **Attachment → Bucket.Attachment**: TiltRotator 등

### 5. 표준 VSS 최대한 재사용 ✅
- 기존 VSS Branch 유지 (Body, Cabin, Powertrain, Chassis, ADAS, Connectivity 등)
- 확장만 추가 (신규 Branch 최소화)
- 표준 VSS와 일관성 유지

---

## 구현 가이드

### 1. VSS Overlay 구조
```
specs/
├── base/
│   └── vehicle_signal_specification.vspec (표준 VSS)
├── overlays/
│   ├── construction_machinery_base.vspec (건설기계 기본 확장)
│   ├── excavator.vspec (굴착기 특화)
│   ├── wheel_loader.vspec (휠로더 특화)
│   └── feh_system.vspec (FEH 시스템)
```

### 2. 제품 타입 표현
```yaml
Vehicle.VehicleIdentification.Type: Excavator
```

### 3. 작업 장비 활성화
- 애플리케이션 레벨에서 `VehicleIdentification.Type` 확인
- 해당 제품에 없는 작업 장비는 무시
- 예: Type이 Excavator면 Boom, Arm, Bucket, Swing, Travel만 활성

---

## 참고사항

1. **표준 VSS 호환성**: 기존 VSS 구조를 최대한 활용
2. **확장성**: 향후 새로운 기능 추가 시 기존 그룹에 확장
3. **단순성**: 구조를 단순하고 명확하게 유지
4. **J1939 매핑**: J1939 신호와의 매핑 고려
5. **FEH 시스템**: 회사 핵심 기술이므로 명확히 구분

