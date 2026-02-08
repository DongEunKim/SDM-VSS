graph TD
    %% 스타일 정의
    classDef documents fill:#f9f9f9,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;
    classDef artifacts fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef tools fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef runtime fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef hardware fill:#424242,stroke:#000,stroke-width:2px,color:#fff;

    %% 1. Input Sources
    subgraph Inputs [Step 0: 원천 데이터]
        J1939_Spec(J1939 Standard Doc):::documents
        OEM_Spec(OEM Signal Spec):::documents
        VSS_Std(COVESA VSS Standard):::documents
    end

    %% 2. Design & Build Phase
    subgraph DesignTime [Design & Build Phase: 준비 단계]
        direction TB
        
        %% DBC Path
        CreateDBC[DBC Generation Tool<br/>CANdb++, scripts]:::tools
        DBC_Files[j1939.dbc<br/>oem.dbc]:::artifacts
        
        %% VSS Path
        CreateOverlay[Manual/Script<br/>Overlay 작성]:::tools
        Overlay_VSpec[oem_overlay.vspec]:::artifacts
        VSSTools[vss-tools<br/>vspec2json]:::tools
        VSS_JSON[vss_expanded.json]:::artifacts
        
        %% Mapping Path (The Bridge)
        CreateMapping[Mapping Tool<br/>Manual or Python Script]:::tools
        Map_File[mapping.yaml<br/>DBC signal ↔ VSS Path]:::artifacts
    end

    %% 3. Run Time Phase
    subgraph RunTime [Run Time Phase: KUKSA 실행 단계]
        direction TB
        CAN_HW((Real CAN Bus)):::hardware
        
        Provider[KUKSA CAN Provider<br/>dbcfeeder]:::runtime
        Broker[KUKSA Databroker<br/>VSS Server]:::runtime
        App[Vehicle Application]:::runtime
    end

    %% Connections - DBC Flow
    J1939_Spec & OEM_Spec --> CreateDBC
    CreateDBC --> DBC_Files

    %% Connections - VSS Flow
    VSS_Std & OEM_Spec --> CreateOverlay
    CreateOverlay --> Overlay_VSpec
    Overlay_VSpec --> VSSTools
    VSSTools --> VSS_JSON

    %% Connections - Mapping (The Convergence)
    DBC_Files & VSS_JSON --> CreateMapping
    CreateMapping --> Map_File

    %% Connections - Runtime Loading
    DBC_Files -.->|Load Definition| Provider
    Map_File -.->|Load Rules| Provider
    VSS_JSON -.->|Load Taxonomy| Broker

    %% Connections - Data Flow
    CAN_HW ==>|Raw CAN Frame| Provider
    Provider ==>|Decoded & Mapped Value| Broker
    Broker ==>|VSS Data| App

    %% 레이블 추가
    linkStyle 10,11 stroke-width:4px,fill:none,stroke:red;