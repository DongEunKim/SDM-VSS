# Vehicle
## ADAS
  > All Advanced Driver Assist Systems data.
  - ABS
    > Antilock Braking System signals.
  - CruiseControl
    > Signals from Cruise Control system.
  - DMS
    > Driver Monitoring System signals.
  - EBA
    > Emergency Brake Assist (EBA) System signals.
  - EBD
    > Electronic Brakeforce Distribution (EBD) System signals.
  - ESC
    > Electronic Stability Control System signals.
    - RoadFriction
      > Road friction values reported by the ESC system.
  - LaneDepartureDetection
    > Signals from Lane Departure Detection System.
  - ObstacleDetection
  - TCS
    > Traction Control System signals.
## Body
  > All body components.
  - Hood
    > Hood status. Start position for Hood is Closed.
  - Horn
    > Horn signals.
  - Lights
    > Exterior lights.
    - Backup
      > Backup lights.
    - Beam
      > Beam lights.
      * Instances: ["Low","High"]
    - Brake
      > Brake lights.
    - DirectionIndicator
      > Indicator lights.
      * Instances: ["Left","Right"]
    - Fog
      > Fog lights.
      * Instances: ["Rear","Front"]
    - Hazard
      > Hazard lights.
    - LicensePlate
      > License plate lights.
    - Parking
      > Parking lights.
    - Running
      > Daytime running lights (DRL).
  - Mirrors
    > All mirrors.
    * Instances: ["DriverSide", "PassengerSide"]
  - Raindetection
    > Rain sensor signals.
  - Trunk
    > Trunk status. Start position for Trunk is Closed.
    * Instances: ["Front", "Rear"]
  - Windshield
    > Windshield signals.
    * Instances: ["Front", "Rear"]
    - WasherFluid
      > Windshield washer fluid signals
    - Wiping
      > Windshield wiper signals.
      - System
        > Signals to control behavior of wipers in detail.
## Cabin
  > All in-cabin components, including doors.
  - Convertible
    > Convertible roof.
  - Door
    - Shade
      > Side window shade. Open = Retracted, Closed = Deployed.
    - Window
      > Door window status. Start position for Window is Closed.
  - HVAC
    > Climate control
    - Station
  - Infotainment
    > Infotainment system.
    - HMI
      > HMI related signals
    - Media
      > All Media actions
      - Played
        > Collection of signals updated in concert when a new media is played
    - Navigation
      > All navigation actions
      - DestinationSet
        > A navigation has been selected.
      - Map
        > All map actions
    - SmartphoneProjection
      > All smartphone projection actions.
    - SmartphoneScreenMirroring
      > All smartphone screen mirroring actions.
  - Light
    > Light that is part of the Cabin.
    - AmbientLight
    - InteractiveLightBar
      > Decorative coloured light bar that supports effects, usually mounted on the dashboard (e.g. BMW i7 Interactive bar).
    - Spotlight
  - RearShade
    > Rear window shade. Open = Retracted, Closed = Deployed.
  - RearviewMirror
    > Rear-view mirror.
  - Seat
    - Airbag
      > Airbag signals.
    - Backrest
      > Describes signals related to the backrest of the seat.
      - Lumbar
        > Adjustable lumbar support mechanisms in seats allow the user to change the seat back shape.
      - SideBolster
        > Backrest side bolster (lumbar side support) settings.
    - Headrest
      > Headrest settings.
    - Massage
      > Massage related information for the seat.
    - NeckScarf
      > NeckScarf settings.
    - Occupant
      > Occupant data.
      - Identifier
        > Identifier attributes based on OAuth 2.0.
    - Seating
      > Describes signals related to the seat bottom of the seat.
    - Switch
      > Seat switch signals
      - Backrest
        > Describes switches related to the backrest of the seat.
        - Lumbar
          > Switches for Backrest.Lumbar.
        - SideBolster
          > Switches for Backrest.SideBolster.
      - Headrest
        > Switches for Headrest.
      - Massage
        > Switches for Massage.
      - Seating
        > Describes switches related to the seating of the seat.
  - Sunroof
    > Sun roof status.
    - Shade
      > Sun roof shade status. Open = Retracted, Closed = Deployed.
## Chassis
  > All data concerning steering, suspension, wheels, and brakes.
  - Accelerator
    > Accelerator signals
  - Axle
    - Wheel
      > Wheel signals for axle
      * Instances: ["Left","Right"]
      - Brake
        > Brake signals for wheel
      - Tire
        > Tire signals for wheel.
  - Brake
    > Brake system signals
  - ParkingBrake
    > Parking brake signals
  - SteeringWheel
    > Steering wheel signals
  - instances
    > Axle signals
## Connectivity
  > Connectivity data.
## Driver
  > Driver data.
  - Identifier
    > Identifier attributes based on OAuth 2.0.
## Exterior
  > Information about exterior measured by vehicle.
## OBD
  > OBD data.
  - Catalyst
    > Catalyst signals
    - Bank1
      > Catalyst bank 1 signals
    - Bank2
      > Catalyst bank 2 signals
  - DriveCycleStatus
    > PID 41 - OBD status for the current drive cycle
  - Status
    > PID 01 - OBD status
  - instances
    > Oxygen sensors (PID 14 - PID 1B)
## Occupant
  - HeadPosition
    > The current position of the driver head on vehicle axis according to ISO 23150:2023.
  - Identifier
    > Identifier attributes based on OAuth 2.0.
  - MidEyeGaze
    > Direction from mid eye position to object driver is looking at.
## Powertrain
  > Powertrain data for battery management, etc.
  - CombustionEngine
    > Engine-specific data, stopping at the bell housing.
    - DieselExhaustFluid
      > Signals related to Diesel Exhaust Fluid (DEF).
    - DieselParticulateFilter
      > Diesel Particulate Filter signals.
    - EngineCoolant
      > Signals related to the engine coolant
    - EngineOil
      > Signals related to the engine oil
  - ElectricMotor
    > Electric Motor specific data.
    - EngineCoolant
      > Signals related to the engine coolant (if applicable).
  - FuelSystem
    > Fuel system data.
  - RangeExtender
    > Extended Range Electric Vehicle (EREV) specific data.
    - ChargeDepleting
      > Signals related to Charge Depleting (CD) mode operation.
    - ChargeSustaining
      > Signals related to Charge Sustaining (CS) mode operation.
  - TractionBattery
    > Battery Management data.
    - CellVoltage
      > Voltage information for cells in the battery pack.
    - Charging
      > Properties related to battery charging.
      - ChargeCurrent
        > Current charging current.
      - ChargeVoltage
        > Current charging voltage, as measured at the charging inlet.
      - ChargingPort
      - Location
        > Location of last or current charging event.
      - MaximumChargingCurrent
        > Maximum charging current that can be accepted by the system, as measured at the charging inlet.
      - Timer
        > Properties related to timing of battery charging sessions.
    - DCDC
      > Properties related to DC/DC converter converting high voltage (from high voltage battery)
      - Temperature
        - BatteryConditioning
          > Properties related to preparing the vehicle battery for charging or driving.
    - StateOfCharge
      > Information on the state of charge of the vehicle's high voltage battery.
    - Temperature
      > Temperature Information for the battery pack.
  - Transmission
    > Transmission-specific data, stopping at the drive shafts.
## Service
  > Service data.
## Vehicle
  > High-level vehicle data.
  - Acceleration
    > Spatial acceleration. Axis definitions according to ISO 8855.
  - AngularVelocity
    > Spatial rotation. Axis definitions according to ISO 8855.
  - CurrentLocation
    > The current latitude and longitude of the vehicle.
    - GNSSReceiver
      > Information on the GNSS receiver used for determining current location.
      - MountingPosition
        > Mounting position of GNSS receiver antenna relative to vehicle coordinate system.
  - Diagnostics
    > Diagnostics data.
  - LowVoltageBattery
    > Signals related to low voltage battery.
  - MotionManagement
    > Motion Management Information.
    - Brake
      > MotionManagement related to braking (both frictions brakes and contribution from electric axles).
      - Axle
        - Wheel
          > MotionManagement signals for a specific wheel.
          * Instances: ["Left","Right"]
    - ElectricAxle
    - Steering
      > MotionManagement related to steering.
      - Axle
        > MotionManagement related to a specific axle.
        - Row1
          > MotionManagement related to front axle.
        - Row2
          > MotionManagement related to rear axle.
      - SteeringWheel
        > MotionManagement related to steering wheel.
    - Suspension
      > MotionManagement related to suspension.
      - Axle
        - Wheel
          > MotionManagement signals for a specific wheel.
          * Instances: ["Left","Right"]
  - Trailer
    > Trailer signals.
  - VehicleIdentification
    > Attributes that identify a vehicle.
  - VersionVSS
    > Supported Version of VSS.