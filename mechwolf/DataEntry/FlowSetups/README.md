# MechWolf Flow Setups Module

A user-friendly interface for creating standardized flow chemistry apparatus configurations in MechWolf.

## Quick Start

```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Create pumps
pump1 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
pump2 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")

# Create apparatus - this opens an interactive GUI
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])

# Use the apparatus in your protocol
protocol = mw.Protocol(apparatus)
```

## Available Setup Types

| Setup Type | Description | Vessels | Coils | Mixers |
|------------|-------------|---------|-------|--------|
| `two_syringes_1r_1m` | Basic two-syringe setup | 2 + product | 2 (a,x) | 1 |
| `three_syringes_1r_1m` | Three syringes, single reactor | 3 + product | 2 (a,x) | 1 |
| `three_syringes_2r_2m` | Three syringes, dual reactors | 3 + product | 4 (a,x,b,y) | 2 |
| `flexible_setup` | Variable configuration | User-defined | 2 (a,x) | 1 |

## Key Features

- **Modern UI Interface**: Clean, professional styling with Material Design inspiration
- **Interactive GUI**: Fill out apparatus parameters through enhanced Jupyter widgets
- **Progress Tracking**: Visual progress indicator showing setup completion
- **Smart Organization**: Grouped sections with clear headers and help text
- **Configuration Persistence**: Setups are saved to JSON for reuse
- **Extensible**: Easy to add new setup types
- **Validation**: Built-in error checking and validation
- **Type Safety**: Full type hints throughout
- **Backward Compatible**: Legacy UI still available if needed

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete usage instructions and examples
- **[Modern UI Guide](docs/MODERN_UI_GUIDE.md)** - New modern interface features and styling
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Architecture and code flow for developers  
- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to add new setup types

## File Structure

```
FlowSetups/
├── README.md              # This file - quick start guide
├── docs/                  # Detailed documentation
│   ├── USER_GUIDE.md      # Complete user documentation
│   ├── DEVELOPER_GUIDE.md # Architecture and code flow
│   ├── API_REFERENCE.md   # API documentation
│   └── CONTRIBUTING.md    # How to extend the system
├── __init__.py           # Module initialization and public API
├── factory.py            # Main FlowSetupFactory class
├── base_classes.py       # Abstract base classes
├── config_templates.py   # Setup configurations
├── *_setup.py           # Individual setup implementations
├── widget_manager.py     # UI component management
├── data_manager.py       # Configuration persistence
├── error_handler.py      # Validation and error handling
└── FlowSetupUtils.py     # Utility functions
```

## Getting Help

1. **Start with the [User Guide](docs/USER_GUIDE.md)** for complete usage instructions
2. **Check [API Reference](docs/API_REFERENCE.md)** for specific function documentation
3. **See [Developer Guide](docs/DEVELOPER_GUIDE.md)** if you need to understand the internals
4. **Read [Contributing Guide](docs/CONTRIBUTING.md)** to add new setup types

## Quick Examples

### List Available Setups
```python
FlowSetupFactory.print_available_setups()
```

### Create Setup with Custom Config File
```python
apparatus = FlowSetupFactory.create_setup(
    'two_syringes_1r_1m', 
    [pump1, pump2], 
    data_file='my_custom_config.json'
)
```

### Use Direct Creator Class
```python
from mechwolf.DataEntry.FlowSetups import TwoSyringesApparatusCreator
creator = TwoSyringesApparatusCreator(pump1, pump2)
apparatus = creator.create_apparatus()
```
