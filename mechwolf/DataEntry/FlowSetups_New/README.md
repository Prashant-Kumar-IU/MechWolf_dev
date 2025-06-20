# MechWolf FlowSetups - Modern Apparatus Configuration System

A comprehensive, modular system for configuring MechWolf flow chemistry apparatus with modern UI components and robust data management.

## 🚀 Quick Start

```python
from mechwolf.DataEntry.FlowSetups_New import quick_start

# Launch the application
app = quick_start("my_apparatus_config.json")
```

## 📁 Architecture Overview

The system is organized into 4 main modules following a clean separation of concerns:

```
FlowSetups_New/
├── component_configurator/    # Component selection and configuration
├── apparatus_builder/         # Connection building and validation  
├── data_manager/             # JSON handling, validation, and export
└── orchestrator/             # Main application orchestration and UI
```

## 🔧 Phase 1: Component Configurator

**Purpose**: Configure all components (active & passive) with proper validation

### Features:
- **Component Type Selector**: Dropdown for pumps, valves, vessels, tubes, etc.
- **Dynamic Forms**: Different forms based on component type selection
- **Real-time Validation**: Serial port format, dimensional units, required fields
- **Component Preview**: Show configured components in organized lists

### Active Components:
- **HarvardSyringePump**: Syringe volume, diameter, serial port
- **ViciValve**: Serial port, vessel-to-port mappings
- **VarianPump**: Serial port, maximum flow rate
- **FreeStepPump**: MCU ID, motor ID, syringe specifications
- **Sensors**: Name, serial port, measurement units

### Passive Components:
- **Vessels**: Name and content description
- **Tubes**: Length, diameter (ID/OD), material with presets:
  - Fat Tube (1/16" ID, 1/8" OD)
  - Thin Tube (0.030" ID, 1/16" OD) 
  - Thinner Tube (0.020" ID, 1/16" OD)
  - Custom configuration
- **Mixers**: T-Mixer, Cross-Mixer, Y-Mixer with descriptions

### Validation:
- Python identifier name validation
- Serial port format checking
- Unit validation (volumes, lengths, flow rates)
- Duplicate name detection
- Component-specific parameter validation

## 🔗 Phase 2: Apparatus Builder

**Purpose**: Connect components using intuitive A.add() logic

### Features:
- **Visual Connection Builder**: Dropdown-based connection interface
- **Connection Validator**: Check for invalid connections, cycles
- **Real-time Preview**: Live connection preview as selections are made
- **Connection Management**: Edit and delete existing connections

### Connection Interface:
```
From Component: [dropdown of all components]
To Component: [dropdown of all components]  
Tube: [dropdown of configured tubes]
[Add Connection] [Remove Connection]
```

### Validation Rules:
- Flow chemistry logic validation
- Component compatibility checking
- Connection limit enforcement (e.g., valve ports)
- Circular dependency detection
- Network connectivity validation

### Code Generation:
Automatically generates Python code:
```python
# Generated MechWolf Apparatus Code
import mechwolf as mw

# Define Vessels
THF = mw.Vessel("Tetrahydrofuran", name="THF")
SM = mw.Vessel("Starting_material_and_tbutanol_THF", name="SM")

# Define Active Components  
Li_activator_pump = mw.VarianPump(
    serial_port='/dev/serial/by-id/...',
    max_rate='25mL/min',
    name="Li_activator_pump"
)

# Build Apparatus
A = mw.Apparatus("Generated Apparatus")
A.add(THF, reagent_valve, fat_tube_1ft)
A.add(reagent_valve, reagent_pump, valve_tube)
```

## 💾 Phase 3: Data Manager

**Purpose**: Robust JSON handling with schema validation

### Features:
- **Schema-based Validation**: Ensure JSON structure integrity
- **Version Management**: Handle different schema versions
- **Backup System**: Automatic backups with cleanup
- **Error Recovery**: Attempt recovery from backup files

### JSON Structure:
```json
{
    "version": "2.0.0",
    "created": "2024-06-19T10:30:00",
    "last_updated": "2024-06-19T11:45:00",
    "apparatus_config": {
        "name": "Birch Reduction Apparatus",
        "components": {
            "active": [
                {
                    "type": "VarianPump",
                    "name": "Li_activator_pump", 
                    "serial_port": "/dev/serial/...",
                    "max_rate": "25mL/min",
                    "category": "active_contrib"
                }
            ],
            "passive": [
                {
                    "type": "Vessel",
                    "name": "THF",
                    "description": "Tetrahydrofuran",
                    "category": "passive"
                }
            ]
        },
        "connections": [
            {
                "from": "THF",
                "to": "reagent_valve", 
                "tube": "fat_tube_1ft",
                "from_type": "Vessel",
                "to_type": "ViciValve",
                "tube_type": "Tube"
            }
        ]
    }
}
```

### Data Operations:
- **Load Configuration**: With error recovery from backups
- **Save Configuration**: With validation and automatic backup
- **Export Options**: JSON and Python code generation
- **Backup Management**: Automatic cleanup of old backups
- **Schema Migration**: Upgrade old configurations to new formats

## 🎨 Phase 4: Main Orchestrator

**Purpose**: Coordinate the complete workflow with modern UI

### Features:
- **Navigation System**: Tab-based interface between phases
- **Progress Tracking**: Visual indicators of completion status
- **Modern Styling**: Tailwind CSS-inspired components
- **Responsive Design**: Works across different screen sizes

### User Interface:
- **Welcome Screen**: Step-by-step workflow introduction
- **Component View**: Access to component configurator
- **Connection View**: Access to apparatus builder
- **Data View**: Configuration management and validation
- **Summary View**: Complete apparatus overview and export

### Tailwind-Inspired Components:
- Modern cards with gradients and shadows
- Styled buttons with hover effects
- Progress bars and status indicators
- Alert messages and validation feedback
- Responsive grid layouts

## 🔄 Complete Workflow

### Step 1: Configure Components
1. Select component type (pump, valve, vessel, tube, mixer)
2. Fill component-specific form with validation
3. Save component to the configured list
4. Repeat for all needed components

### Step 2: Build Connections
1. Select source component from dropdown
2. Select destination component from dropdown  
3. Select connecting tube from configured tubes
4. Preview connection and validate
5. Add connection to apparatus
6. Repeat for all connections

### Step 3: Validate & Export
1. Review complete apparatus summary
2. Validate configuration for errors
3. Visualize network diagram
4. Export as JSON or Python code
5. Save configuration with automatic backup

## 🛠️ Usage Examples

### Basic Usage:
```python
from mechwolf.DataEntry.FlowSetups_New import FlowSetupMain

# Create application instance
app = FlowSetupMain("birch_reduction_config.json")

# Start the interface
app.start()
```

### Direct Component Access:
```python
from mechwolf.DataEntry.FlowSetups_New import ComponentSelector, JSONHandler

# Create data manager
data_manager = JSONHandler("config.json")

# Create component selector
selector = ComponentSelector(data_manager)
selector.create_main_interface()
```

### Programmatic Configuration:
```python
# Get current configuration
config = app.get_current_config()

# Access components and connections
components = config["apparatus_config"]["components"]
connections = config["apparatus_config"]["connections"]
```

## 🔍 Validation & Error Handling

### Component Validation:
- Name format (Python identifiers)
- Serial port format and availability
- Unit validation with dimensional analysis
- Required field checking
- Component-specific parameter validation

### Connection Validation:
- Flow chemistry logic rules
- Component compatibility matrix
- Connection limits (valve ports, vessel inputs)
- Network connectivity requirements
- Circular dependency detection

### Data Validation:
- JSON schema compliance
- Version compatibility
- Referential integrity (component names in connections)
- Configuration completeness

## 📊 Benefits

### For Users:
- **Intuitive Interface**: Step-by-step workflow
- **Real-time Validation**: Immediate feedback on errors
- **Visual Feedback**: Network diagrams and previews
- **Error Recovery**: Automatic backups and recovery
- **Code Generation**: Ready-to-use Python code

### For Developers:
- **Modular Architecture**: Easy to extend and maintain
- **Clean Separation**: Each phase is independent
- **Comprehensive Testing**: Individual modules can be tested
- **Modern Standards**: Professional UI and code organization
- **Documentation**: Extensive inline and external documentation

## 🚀 Future Enhancements

### Phase 5 (Future):
- **Protocol Integration**: Direct connection to ProtocolDev
- **Advanced Visualization**: 3D apparatus diagrams
- **Collaboration Features**: Multi-user configuration
- **Template System**: Pre-built apparatus templates
- **Integration APIs**: Connect with other MechWolf tools

This system provides a robust, professional foundation for MechWolf apparatus configuration that can be easily extended and maintained by future researchers.