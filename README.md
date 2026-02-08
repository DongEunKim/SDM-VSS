# SDM-VSS (Signal Definition & Management - Vehicle Signal Specification)

차량 내 J1939 통신 네트워크의 데이터 사양을 엑셀 기반으로 정의하고, DBC 파일로 변환하는 프로젝트입니다.

## 프로젝트 구조

```
SDM-VSS/
├── doc/                          # 문서
│   ├── J1939 Specification and DBC Conversion Technical Standard.md
│   ├── File Tree.md
│   └── work_flow.md
│
├── specs/                        # [Input] 계층적 설정 정의 (상속의 핵심)
│   ├── j1939_standard.xlsx      # Level 0: J1939 표준 정의
│   ├── 00_common/               # Level 1: 전사 공통
│   │   └── common_spec.xlsx
│   ├── 10_excavator/            # Level 2: 굴착기 제품군
│   │   ├── excavator_spec.xlsx
│   │   └── 12_electric/        # Level 3: 전기 굴착기
│   │       ├── electric_spec.xlsx
│   │       └── 01_CEABC/        # Level 4: CEABC 모델
│   │           ├── manifest.yaml
│   │           └── CEABC_spec.xlsx
│   └── 20_wheel_loader/         # Level 2: 휠로더 제품군
│
├── data_sources/                 # [Source] 변경되지 않는 원천 데이터 (Read-Only)
│   ├── vss_core/                # COVESA VSS 표준 (Git Submodule)
│   ├── j1939_master/            # J1939 마스터 DBC 파일
│   └── oem_legacy/              # 레거시 데이터 (참조용)
│
├── tools/                        # [Tools] 빌드 및 변환 도구
│   ├── excel_to_dbc.py          # 엑셀 -> DBC 변환 스크립트
│   └── validator.py             # 매니페스트 문법 검사기
│
├── build/                        # [Temp] 빌드 중간 산출물 (Git Ignore)
│
└── dist/                         # [Output] 최종 배포 산출물
    └── [project_name]/
        └── [version]/
            ├── PCAN.dbc
            ├── BCAN.dbc
            ├── can.conf
            └── [Project]_Spec.xlsx
```

## 주요 기능

- **엑셀 기반 사양 정의**: J1939 메시지 및 신호를 엑셀 파일로 정의
- **계층적 상속 구조**: Level 0~4의 상속 구조로 다기종 모델 관리
- **자동 DBC 생성**: 엑셀 사양서를 자동으로 DBC 파일로 변환
- **검증 시스템**: 비트 중복, 프로토콜 준수 등 자동 검증

## 사용 방법

자세한 내용은 [J1939 Specification and DBC Conversion Technical Standard.md](doc/J1939%20Specification%20and%20DBC%20Conversion%20Technical%20Standard.md) 문서를 참조하세요.

## 참고 자료

- [COVESA VSS Specification](https://covesa.github.io/vehicle_signal_specification/)
- [SAE J1939 Standard](https://www.sae.org/standards/content/j1939_202302/)

