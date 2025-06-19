# MechWolf Components Documentation

## Overview

The MechWolf components system provides a comprehensive framework for modeling and controlling laboratory instruments and flow chemistry apparatus. This folder contains two main categories of components:

- **stdlib**: Standard library components that are officially supported by MechWolf
- **contrib**: Contributed components with no guarantee of correctness, safety, or reliability

## Architecture

### Component Hierarchy

```
Component (base class)
├── ActiveComponent (controllable components)
│   ├── Pump (fluid movement)
│   ├── Valve (flow control)
│   ├── Sensor (data collection)
│   └── TempControl (temperature management)
└── Passive Components
    ├── Mixer (fluid mixing)
    ├── Vessel (containers)
    └── Tube (connections)
```

### Key Concepts

- **Component**: Base class for all physical parts of a flow chemistry setup
- **ActiveComponent**: Connected, controllable components that can be manipulated in protocols
- **State Management**: Components maintain a `_base_state` for default configuration
- **Validation**: Built-in validation ensures components are properly configured
- **Context Management**: Components support Python context managers for proper setup/teardown
- **Unit Handling**: Uses Pint quantities for dimensional analysis and unit conversion

## Standard Library Components (stdlib/)

### Core Base Classes

#### Component (`component.py`)
- **Purpose**: Base class for all irreducible parts of a flow chemistry setup
- **Features**: 
  - Automatic naming with sequential IDs
  - Context manager support
  - Visualization shape configuration
- **Attributes**: `name`, `_visualization_shape`

#### ActiveComponent (`active_component.py`)
- **Purpose**: Abstract base for controllable components
- **Features**:
  - State management with `_base_state` dictionary
  - Parameter updating with unit conversion
  - Async `_update()` method for hardware communication
  - Comprehensive validation system
- **Key Methods**: `_update_from_params()`, `_update()`, `_validate()`

### Hardware Components

#### Pump (`pump.py`)
- **Purpose**: Generic pumping device for fluid movement
- **Inherits**: ActiveComponent
- **Attributes**: `rate` (flow rate as pint.Quantity with volume/time dimensionality)
- **Visualization**: `box3d`
- **Base State**: `{"rate": "0 mL/min"}`

#### Valve (`valve.py`)
- **Purpose**: Generic valve for flow control
- **Inherits**: ActiveComponent
- **Attributes**: 
  - `mapping`: Component-to-port number mapping
  - `setting`: Current valve position (integer)
- **Visualization**: `parallelogram`
- **Base State**: `{"setting": 1}`

#### Sensor (`sensor.py`)
- **Purpose**: Generic sensor for data collection
- **Inherits**: ActiveComponent
- **Attributes**: 
  - `rate`: Data collection rate in Hz
  - `_unit`: Unit string for measurements
- **Visualization**: `ellipse`
- **Base State**: `{"rate": "0 Hz"}`
- **Key Methods**: `_read()`, `_monitor()`

#### TempControl (`tempcontrol.py`)
- **Purpose**: Temperature control device
- **Inherits**: ActiveComponent
- **Features**: Temperature setpoint management

### Mixing Components

#### Mixer (`mixer.py`)
- **Purpose**: Generic mixer (alias of Component)
- **Inherits**: Component
- **Visualization**: `cds`

#### TMixer (`t_mixer.py`)
- **Purpose**: T-shaped mixer junction
- **Inherits**: Component
- **Visualization**: `cds`

#### CrossMixer (`cross_mixer.py`)
- **Purpose**: Cross-shaped mixer junction
- **Inherits**: Component
- **Visualization**: `cds`

#### YMixer (`y_mixer.py`)
- **Purpose**: Y-shaped mixer junction
- **Inherits**: Component
- **Visualization**: `cds`

### Utility Components

#### Tube (`tube.py`)
- **Purpose**: Connection between components
- **Inherits**: Component
- **Attributes**: Length, internal diameter specifications
- **Visualization**: Connector representation

#### Vessel (`vessel.py`)
- **Purpose**: Generic container
- **Inherits**: Component
- **Attributes**: 
  - `description`: Contents description
  - `name`: Vessel identifier
- **Visualization**: `cylinder`

### Testing Components

#### Dummy Components
- **DummyPump** (`dummy_pump.py`): Simulated pump for testing
- **DummySensor** (`dummy_sensor.py`): Simulated sensor for testing
- **DummyValve** (`dummy_valve.py`): Simulated valve for testing
- **Dummy** (`dummy.py`): Generic dummy component

#### Broken Components (for testing error handling)
- **BrokenDummyComponent** (`broken_dummy_component.py`)
- **BrokenDummySensor** (`broken_dummy_sensor.py`)

## Contributed Components (contrib/)

### Real Hardware Implementations

#### HarvardSyringePump (`harvardpump.py`)
- **Purpose**: Dual-channel infusion Harvard syringe pump
- **Attributes**: `syringe_volume`, `syringe_diameter`, `serial_port`
- **Communication**: Asynchronous serial communication with `aioserial`
- **Authors**: Prashant Kumar, Nicola Pohl, Murat Ozturkme, Alex Mijalis
- **Stability**: Production-ready

#### FreeStepPump (`freestep_pump.py`)
- **Purpose**: FreeStep 3D syringe pump controller
- **Features**: 
  - Shared controller instances across multiple pumps
  - MCU and motor profile management
  - Syringe volume/diameter calibration
- **Attributes**: `serial_port`, `mcu_id`, `motor_id`, `syringe_volume`, `syringe_diameter`
- **Author**: Prashant Kumar
- **Stability**: Beta

### Laboratory Instruments

#### VICI Components
- **VICIValve** (`vici.py`): VICI multiposition valve
- **VICIPump** (`vicipump.py`): VICI syringe pump

#### Other Instruments
- **VarianHPLC** (`varian.py`): Varian HPLC system integration
- **LabJackSensor** (`labjack.py`): LabJack data acquisition
- **ArduinoComponent** (`arduino.py`): Arduino-based custom devices
- **FC203** (`fc203.py`): FC203 flow controller
- **GSIOC** (`gsioc.py`): GSIOC interface component

### Calibration Tools

#### Calibration System (`calibration_3DSyringePumps_mLmin.py`)
- **Purpose**: Calibration utilities for 3D syringe pumps
- **Features**: Flow rate calibration in mL/min units

#### Visualization Tools (`calibration_visualizations.py`)
- **Purpose**: Plotting and visualization for calibration data
- **Features**: Interactive calibration curve generation

#### Controller Integration (`freestep_3DSyringePump_controller.py`)
- **Purpose**: Low-level controller for FreeStep pumps
- **Features**: Direct hardware communication and profile management

## Component Lifecycle

### Instantiation
```python
# Basic component creation
pump = mw.Pump(name="main_pump")
valve = mw.Valve(mapping={component: port}, name="selector")
```

### Context Management
```python
# Components support context managers
with pump:
    pump.rate = "5 mL/min"
    await pump._update()
```

### State Management
```python
# Components maintain base states
pump._base_state = {"rate": "0 mL/min"}
pump._update_from_params({"rate": "2 mL/min"})
```

### Validation
```python
# Validation ensures proper configuration
pump._validate(dry_run=False)  # Validates and applies state
pump._validate(dry_run=True)   # Validation only
```

## Integration Points

### With MechWolf Core
- Components are used in `Apparatus` objects to define experimental setups
- ActiveComponents are controlled through `Protocol` objects
- Components support visualization in experimental diagrams

### Unit System
- All dimensional quantities use Pint units
- Automatic unit conversion and dimensional analysis
- Base states specify units as strings (e.g., "0 mL/min", "1 bar")

### Async Operations
- ActiveComponents support asynchronous operations
- `_update()` method handles hardware communication
- Sensors provide async data streaming with `_monitor()`

## Development Guidelines

### Creating New Components
1. Inherit from appropriate base class (Component or ActiveComponent)
2. Define `_base_state` dictionary for ActiveComponents
3. Implement `_update()` method for hardware communication
4. Set appropriate `_visualization_shape`
5. Include comprehensive docstrings and metadata

### Metadata Format (contrib components)
```python
metadata = {
    "author": [{
        "first_name": "First",
        "last_name": "Last", 
        "email": "email@domain.com",
        "institution": "Institution Name",
        "github_username": "username"
    }],
    "stability": "beta|stable|experimental",
    "supported": True|False
}
```

### Testing
- Use dummy components for unit testing
- Use broken components for error handling tests
- Validate dimensional analysis with Pint quantities
- Test context manager behavior

## File Structure Summary

```
components/
├── __init__.py                    # Main imports
├── stdlib/                        # Standard library
│   ├── component.py              # Base Component class
│   ├── active_component.py       # ActiveComponent base
│   ├── pump.py                   # Generic pump
│   ├── valve.py                  # Generic valve  
│   ├── sensor.py                 # Generic sensor
│   ├── mixer.py                  # Generic mixer
│   ├── t_mixer.py               # T-junction mixer
│   ├── cross_mixer.py           # Cross mixer
│   ├── y_mixer.py               # Y-junction mixer
│   ├── tube.py                  # Connecting tubes
│   ├── vessel.py                # Containers
│   ├── tempcontrol.py           # Temperature control
│   ├── dummy_*.py               # Testing components
│   └── broken_dummy_*.py        # Error testing
└── contrib/                      # Contributed components
    ├── harvardpump.py           # Harvard syringe pumps
    ├── freestep_pump.py         # FreeStep 3D pumps  
    ├── vici.py                  # VICI valves
    ├── vicipump.py              # VICI pumps
    ├── varian.py                # Varian HPLC
    ├── labjack.py               # LabJack DAQ
    ├── arduino.py               # Arduino devices
    ├── calibration_*.py         # Calibration tools
    └── calibration_handlers/    # UI handlers
```

This documentation provides a comprehensive reference for understanding, using, and extending the MechWolf components system.