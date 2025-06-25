# Phase2_ApparatusBuilder - LLM-Friendly Documentation

## 🏗️ Architecture Overview

The Phase2_ApparatusBuilder is a modular, tabbed interface system for designing flow chemistry apparatus in MechWolf. It has been refactored from a monolithic 1,346-line file into a clean, modular architecture with **zero breaking changes** to the public API.

### **Directory Structure**
```
Phase2_ApparatusBuilder/
├── __init__.py                     # Public API & backward compatibility
├── tabbed_apparatus_designer.py   # Original monolithic file (preserved)
├── tabbed_designer.py              # New modular entry point (primary)
├── DEVELOPMENT_GUIDE.md           # Development documentation
├── models/                         # Data models & validation
│   ├── __init__.py
│   ├── component.py               # ApparatusComponent class
│   ├── connection.py              # ApparatusConnection class  
│   ├── exceptions.py              # Custom exceptions
│   └── validators.py              # Validation functions
├── registry/                       # Component management
│   ├── __init__.py
│   ├── component_registry.py      # ComponentRegistry class
│   └── component_discovery.py     # Dynamic component discovery
├── ui/                            # User interface components
│   ├── __init__.py
│   ├── tab_builders.py           # Tab creation methods
│   ├── widgets.py                # Custom widget definitions
│   └── event_handlers.py         # Event binding logic
├── core/                          # Business logic
│   ├── __init__.py
│   ├── designer.py               # Main TabbedApparatusDesigner
│   ├── editors.py                # Component & connection editors
│   └── code_generator.py         # MechWolf code generation
├── config/                        # Configuration & definitions
│   ├── __init__.py
│   ├── component_definitions.py  # Static component specifications
│   ├── settings.py               # Application settings
│   ├── path_utils.py             # Path utilities
│   └── units.py                  # Unit system handling
├── examples/                      # Example configurations
│   ├── TabbedDesigner_Demo.ipynb
│   ├── TabbedDesigner_Demo-copy.ipynb
│   ├── tabbed_designer_demo_experiment.json
│   └── test1.json                # Complex apparatus configuration
├── legacy/                        # Legacy components (archived)
│   └── [various legacy files]
└── tests/                         # Test suite
    └── test_modular_designer.py
```

## 🔌 Public API & Entry Points

### **Primary Entry Points**
```python
# Main entry point (recommended)
from mechwolf.DataEntry.Phase2_ApparatusBuilder import create_tabbed_apparatus_designer
designer = create_tabbed_apparatus_designer(experiment_manager)

# Enhanced v2 (modular) 
from mechwolf.DataEntry.Phase2_ApparatusBuilder import create_tabbed_designer
designer = create_tabbed_designer(experiment_manager)

# Direct class instantiation
from mechwolf.DataEntry.Phase2_ApparatusBuilder import TabbedApparatusDesigner
designer = TabbedApparatusDesigner(experiment_manager)

# Utility functions
from mechwolf.DataEntry.Phase2_ApparatusBuilder import (
    launch_tabbed_designer,
    get_designer_info,
    print_designer_info
)
```

### **Available Components**
```python
from mechwolf.DataEntry.Phase2_ApparatusBuilder import (
    ApparatusComponent,     # Component data model
    ApparatusConnection,    # Connection data model  
    ComponentRegistry       # Component registry
)
```

## 📊 Core Models & Data Structures

### **ApparatusComponent** (`models/component.py`)
Represents a single component in the apparatus with properties and metadata.

**Key Features:**
- Type validation and normalization
- Unit system integration with structured storage
- Property validation based on component type
- Serialization/deserialization with backward compatibility

**Example Usage:**
```python
# Create a component
comp = ApparatusComponent('HarvardSyringePump', 'pump_1', 1)
comp.properties = {
    'syringe_volume': '3 mL',
    'syringe_diameter': '10 mm', 
    'serial_port': '/dev/ttyUSB0'
}

# Validate properties
comp.validate_properties()

# Serialize to dict (compact format)
data = comp.to_dict(include_registry_info=False)
```

**Supported Component Types:**
- **Active Components:** HarvardSyringePump, VarianPump, ViciPump, ViciValve
- **Passive Components:** Vessel, TMixer, Tube

### **ApparatusConnection** (`models/connection.py`)
Represents a connection between two components with tube specifications.

**Key Features:**
- Connection integrity validation
- Tube property management
- Unit system integration for tube dimensions
- Self-connection prevention

**Example Usage:**
```python
# Create a connection
conn = ApparatusConnection('pump_1', 'vessel_1', 'tube_1', '1 ft')
conn.validate_connection(components_dict)

# Serialize to dict
data = conn.to_dict()
```

### **ComponentRegistry** (`registry/component_registry.py`)
Centralized registry for component discovery and management.

**Key Features:**
- Dynamic component discovery from contrib directory
- Backward compatibility handling
- Component type normalization
- Extensible architecture for new components

**Registry Structure:**
```python
ComponentRegistry.ACTIVE_COMPONENTS = {
    'HarvardSyringePump': {
        'module': 'harvardpump',
        'category': 'active',
        'display_name': 'Harvard Syringe Pump',
        'icon': '💉',
        'default_properties': {...},
        'required_properties': [...]
    }
}

ComponentRegistry.PASSIVE_COMPONENTS = {
    'Vessel': {...},
    'TMixer': {...},
    'Tube': {...}
}
```

## 🎨 User Interface Architecture

### **TabbedApparatusDesigner** (`core/designer.py`)
Main orchestration class for the apparatus designer interface.

**Tab Structure:**
1. **Active Components Tab:** Harvard pumps, Varian pumps, etc.
2. **Passive Components Tab:** Vessels, T-mixers, tubing
3. **Network Connections Tab:** Connection management and visualization

**Key Methods:**
- `_add_harvard_pump()`: Add Harvard syringe pump
- `_add_passive_component()`: Add vessels, mixers, tubes
- `_add_connection()`: Create component connections
- `_generate_code()`: Generate MechWolf apparatus code
- `_update_*_display()`: Update UI displays
- `_safe_save_to_metadata()`: Save to experimental metadata

### **TabBuilders** (`ui/tab_builders.py`)
Static methods for creating UI tabs with consistent styling.

### **EventHandlers** (`ui/event_handlers.py`) 
Event binding and handling logic for user interactions.

## 🔧 Code Generation System

### **CodeGenerator** (`core/code_generator.py`)
Generates Python code for MechWolf apparatus setup.

**Generated Code Structure:**
```python
# Generated MechWolf Apparatus Code
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Component Definitions
pump_1 = HarvardSyringePump(name="pump_1", syringe_volume="3 mL", ...)
vessel_1 = mw.Vessel(description="", name="vessel_1")
tube_1 = mw.Tube(length="1 ft", ID="1/16 in", OD="1/8 in", material="PFA")

# Apparatus Assembly  
A = mw.Apparatus("Generated Apparatus")
A.add(pump_1, vessel_1, tube_1)
```

**Component-Specific Code Patterns:**
- **HarvardSyringePump:** `name` first, then properties
- **Tube:** No `name` parameter, only dimensional properties
- **Vessel:** `description` first, then `name`
- **TMixer:** Only `name` parameter

## 🔍 Validation System

### **Component Validation**
- Required property validation
- Type-specific validation (tubes, pumps, etc.)
- Unit format validation
- Serial port validation

### **Connection Validation**
- Component existence checking
- Self-connection prevention
- Tube length format validation
- Connection integrity validation

### **Error Handling**
```python
# Custom exceptions
ComponentValidationError(component_name, message)
ConnectionValidationError(connection_desc, message)  
MetadataError(message)
```

## 💾 Data Storage & Serialization

### **Structured Unit Storage**
The system uses structured unit storage for better data management:

```json
{
  "syringe_volume": {
    "value": 3.0,
    "unit": "mL", 
    "formatted": "3 mL"
  }
}
```

### **Metadata Integration**
- Automatic saving to ExperimentalMetadataManager
- Compact JSON format (without registry_info)
- Backward compatibility with legacy formats
- Validation error reporting during save/load

### **Example JSON Structure** (from `examples/test1.json`)
```json
{
  "apparatus_config": {
    "components": {
      "active": [...],
      "passive": [...]
    },
    "connections": [...],
    "component_types": {...}
  }
}
```

## 🚀 Adding New Component Types

### **Step 1: Component Definition**
Edit `config/component_definitions.py`:

```python
COMPONENT_DEFINITIONS = {
    'active': {
        'YourNewPump': {
            'module': 'yournewpump',
            'category': 'active',
            'display_name': 'Your New Pump',
            'icon': '⚡',
            'default_properties': {
                'serial_port': '/dev/ttyUSB0',
                'max_pressure': '100 psi'
            },
            'required_properties': ['serial_port', 'max_pressure']
        }
    }
}
```

### **Step 2: Code Generation**
Update `core/code_generator.py`:

```python
elif comp.component_type == 'YourNewPump':
    params = [f'name="{name}"'] 
    for prop_name, prop_value in comp.properties.items():
        if prop_value:
            params.append(f'{prop_name}="{prop_value}"')
    code_lines.append(f'{name} = YourNewPump({", ".join(params)})')
```

### **Step 3: Validation (Optional)**
Add custom validation in `models/component.py`:

```python
def _validate_your_pump_properties(self):
    """Validate your pump specific properties."""
    # Custom validation logic
    pass
```

## 🧪 Testing & Development

### **Test Structure**
- Unit tests in `tests/test_modular_designer.py`
- Integration tests for full workflow
- Component discovery tests
- Code generation tests

### **Development Workflow**
1. Make changes to specific modules
2. Run validation tests
3. Test in Jupyter notebook environment
4. Verify code generation output
5. Check metadata persistence

### **Debug Information**
```python
# Get designer information
from mechwolf.DataEntry.Phase2_ApparatusBuilder import get_designer_info
info = get_designer_info()
print(info)

# Print available components
from mechwolf.DataEntry.Phase2_ApparatusBuilder.registry import ComponentRegistry
print(ComponentRegistry.ACTIVE_COMPONENTS)
```

## 🔮 Future Enhancements

### **Graph-Based Architecture**
Current list-based connections can be migrated to NetworkX:
```python
# Future: networkx.DiGraph with 
# apparatus_graph.add_edge(from, to, tube=tube_obj)
```

### **Plugin Architecture**
```python
# Future: Dynamic component loading
ComponentRegistry.register_plugin('MyCustomComponent', plugin_config)
```

### **Advanced Validation**
- Graph-based topology validation
- Flow analysis and cycle detection
- Component compatibility checking

## 📝 LLM Development Guidelines

### **Best Practices**
1. **Preserve Backward Compatibility:** All existing imports must continue working
2. **Module Separation:** Don't mix UI logic with data models
3. **Validation First:** Always validate before saving/processing
4. **Error Handling:** Use custom exceptions with descriptive messages
5. **Unit Integration:** Leverage the structured unit system

### **Common Patterns**
```python
# Component creation pattern
comp = ApparatusComponent(comp_type, name, instance_id)
comp.properties = {...}
comp.validate_properties()

# Connection creation pattern  
conn = ApparatusConnection(from_comp, to_comp, tube_type, tube_length)
conn.validate_connection(components_dict)

# Registry lookup pattern
info = ComponentRegistry.get_component_info(comp_type)
normalized_type = ComponentRegistry.normalize_component_type(comp_type)
```

### **Key Files for Modifications**
- **New Components:** `config/component_definitions.py`
- **Code Generation:** `core/code_generator.py`
- **Validation:** `models/validators.py`
- **UI Changes:** `ui/tab_builders.py`, `ui/event_handlers.py`
- **Data Models:** `models/component.py`, `models/connection.py`

## 🏆 Architecture Benefits

- ✅ **Maintainability:** 8 focused modules vs 1 monolithic file
- ✅ **Testability:** Clear separation enables targeted testing
- ✅ **Extensibility:** Easy component addition and feature expansion
- ✅ **Zero Breaking Changes:** All existing code continues working
- ✅ **Performance:** Lazy loading and optimized imports
- ✅ **Validation:** Comprehensive error checking and user feedback
- ✅ **Future-Ready:** Prepared for graph-based architecture migration

---

**Last Updated:** June 2025  
**Version:** 2.0 (Modular Architecture)  
**Compatibility:** Python 3.7+, ipywidgets, MechWolf ecosystem