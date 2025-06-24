# Phase2_ApparatusBuilder Development Guide

## 🏗️ Architecture Overview

The Phase2_ApparatusBuilder has been refactored from a monolithic 1,346-line file into a clean, modular architecture with **zero breaking changes** to the public API.

### **Directory Structure**
```
Phase2_ApparatusBuilder/
├── __init__.py                     # Public API & backward compatibility
├── tabbed_apparatus_designer.py   # Original monolithic file (preserved)
├── tabbed_designer.py              # New modular entry point (primary)
├── models/                         # Data models
│   ├── __init__.py
│   ├── component.py               # ApparatusComponent class
│   └── connection.py              # ApparatusConnection class
├── registry/                       # Component management
│   ├── __init__.py
│   ├── component_registry.py      # ComponentRegistry class
│   └── component_discovery.py     # Discovery logic
├── ui/                            # User interface
│   ├── __init__.py
│   ├── tab_builders.py           # Tab creation methods
│   └── event_handlers.py         # Event binding logic
├── core/                          # Business logic
│   ├── __init__.py
│   ├── designer.py               # Main TabbedApparatusDesigner
│   ├── editors.py                # Component & connection editors
│   └── code_generator.py         # Code generation
├── config/                        # Configuration
│   ├── __init__.py
│   ├── component_definitions.py  # Component specs
│   └── settings.py               # App settings
└── DEVELOPMENT_GUIDE.md          # This file
```

## 🔌 Public API (Unchanged)

All existing imports and function calls work identically:

```python
# These all work exactly as before
from mechwolf.DataEntry.Phase2_ApparatusBuilder import (
    TabbedApparatusDesigner,
    ComponentRegistry,
    ApparatusComponent,
    ApparatusConnection,
    create_tabbed_apparatus_designer,
    launch_tabbed_designer
)

# Enhanced v2 function (new)
from mechwolf.DataEntry.Phase2_ApparatusBuilder import create_tabbed_designer
```

## 📊 Module Responsibilities

### **models/** - Data Structures
- **`component.py`**: `ApparatusComponent` class with properties and serialization
- **`connection.py`**: `ApparatusConnection` class for tube connections

### **registry/** - Component Management  
- **`component_registry.py`**: Central registry for all component types
- **`component_discovery.py`**: Dynamic discovery from contrib directory

### **ui/** - User Interface
- **`tab_builders.py`**: Static methods for creating UI tabs
- **`event_handlers.py`**: Event binding and handling logic

### **core/** - Business Logic
- **`designer.py`**: Main `TabbedApparatusDesigner` orchestration class
- **`editors.py`**: Component and connection property editors
- **`code_generator.py`**: MechWolf code generation engine

### **config/** - Configuration
- **`component_definitions.py`**: Static component specifications
- **`settings.py`**: Application settings and paths

## 🆕 Adding New Component Types

### **Step 1: Add Component Definition**
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

### **Step 2: Update Code Generator** 
Edit `core/code_generator.py` to handle your component's parameter pattern:

```python
elif comp.component_type == 'YourNewPump':
    # Define parameter pattern for your component
    params = [f'name="{name}"']
    for prop_name, prop_value in comp.properties.items():
        if prop_value:
            params.append(f'{prop_name}="{prop_value}"')
    code_lines.append(f'{name} = YourNewPump({", ".join(params)})')
```

### **Step 3: Add UI Button (Optional)**
Edit `ui/tab_builders.py` to add a dedicated button for your component.

## 🧪 Testing Framework

### **Unit Tests Structure**
```python
# tests/test_component_registry.py
def test_component_discovery():
    from registry import ComponentRegistry
    assert 'HarvardSyringePump' in ComponentRegistry.ACTIVE_COMPONENTS

# tests/test_code_generation.py  
def test_harvard_pump_code_generation():
    from core import CodeGenerator
    # Test code generation for various components
```

### **Integration Tests**
```python
# tests/test_full_workflow.py
def test_create_apparatus_workflow():
    designer = create_tabbed_designer()
    # Test full component creation -> connection -> code generation
```

## 🔄 Migration from v1 to v2

The system automatically tries v2 (modular) first, then falls back to v1 (monolithic):

```python
# This automatically uses the best available version
designer = create_tabbed_apparatus_designer(experiment_manager)

# Force v2 usage
designer = create_tabbed_designer(experiment_manager)
```

## 🐛 Debugging Guide

### **Import Issues**
```python
from mechwolf.DataEntry.Phase2_ApparatusBuilder import get_designer_info
info = get_designer_info()
print(info)  # Shows which designers are available and any import errors
```

### **Component Discovery Issues**
```python
from mechwolf.DataEntry.Phase2_ApparatusBuilder.registry import ComponentRegistry
print(ComponentRegistry.ACTIVE_COMPONENTS)  # List discovered components
```

### **UI Issues**
Check that all required widgets are properly stored as attributes in tab builders.

## 🚀 Performance Optimizations

### **Lazy Loading**
- Component discovery happens once at module load
- UI elements are created only when tabs are accessed
- Code generation is on-demand only

### **Memory Management**
- Circular import prevention with local imports
- Clean separation of concerns reduces memory footprint

## 🔮 Future Enhancements

### **Graph-Based Network Architecture**
The current list-based connection model can be easily migrated to NetworkX:

```python
# Current: List[ApparatusConnection]
# Future: networkx.DiGraph with apparatus_graph.add_edge(from, to, tube=tube_obj)
```

### **Plugin Architecture**
```python
# Future: Dynamic component loading
from registry import ComponentRegistry
ComponentRegistry.register_plugin('MyCustomComponent', plugin_config)
```

### **Advanced Validation**
```python
# Future: Graph-based validation
def validate_apparatus_topology(components, connections):
    # Check for cycles, unreachable components, flow analysis
    pass
```

## 📝 LLM Assistance Guidelines

When working with this codebase:

1. **Always preserve backward compatibility** - existing imports must continue working
2. **Follow the module separation** - don't mix UI logic with data models
3. **Update both v1 and v2** when making core changes
4. **Test thoroughly** - the system has fallback mechanisms that should be validated
5. **Document new components** in `component_definitions.py` first

## 🏆 Benefits Achieved

- ✅ **Maintainability**: 8 focused files vs 1 monolithic file
- ✅ **Testability**: Clear separation enables targeted unit testing
- ✅ **Extensibility**: Easy to add new components and features
- ✅ **Zero Breaking Changes**: All existing code continues to work
- ✅ **Performance**: Lazy loading and optimized imports
- ✅ **Readability**: Each module has single responsibility
- ✅ **Future-Ready**: Prepared for graph-based architecture migration

---

**Last Updated**: June 2025  
**Version**: 2.0 (Modular Architecture)