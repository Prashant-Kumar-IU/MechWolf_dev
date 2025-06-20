# Factory Usage Examples - FlowSetups_New

This document shows how to use the new ApparatusFactory to create MechWolf apparatus with a simple factory pattern, similar to the old FlowSetups system.

## 🚀 Quick Start - Old vs New

### Old FlowSetups Usage:
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
A = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump_1, pump_2])
```

### New FlowSetups_New Usage:
```python
from mechwolf.DataEntry.FlowSetups_New import create_setup
A = create_setup('birch_reduction', 'birch_reduction_config.json')
```

## 📋 Complete Usage Examples

### 1. Basic Factory Usage
```python
import mechwolf as mw
from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory

# Create apparatus from JSON configuration
A = ApparatusFactory.create_apparatus_from_config('example_birch_reduction.json')

# The apparatus is ready to use!
print(f"Created apparatus: {A.name}")
print(f"Components: {len(A.components)}")

# Create a protocol
P = mw.Protocol(A)
P.add(Li_activator_pump, start='0s', duration='10min', rate='5 mL/min')

# Execute the experiment
experiment = P.execute()
```

### 2. Backward Compatibility Interface
```python
from mechwolf.DataEntry.FlowSetups_New import create_setup

# This mimics the old factory pattern:
A = create_setup('my_apparatus', 'my_config.json')

# Optional: the pumps parameter is ignored but accepted for compatibility
A = create_setup('my_apparatus', 'my_config.json', pumps=[])  # pumps ignored
```

### 3. Direct Factory Methods
```python
from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory

# Method 1: From config file
A = ApparatusFactory.create_apparatus_from_config('config.json', 'My_Apparatus')

# Method 2: From components and connections dictionaries
components = {
    "active": [
        {
            "type": "VarianPump",
            "name": "pump1", 
            "serial_port": "/dev/ttyUSB0",
            "max_rate": "10 mL/min"
        }
    ],
    "passive": [
        {
            "type": "Vessel",
            "name": "vessel1",
            "description": "Starting material"
        }
    ]
}

connections = [
    {
        "from": "vessel1",
        "to": "pump1", 
        "tube": "tube1"
    }
]

A = ApparatusFactory.create_apparatus_from_components(components, connections, "My_Apparatus")

# Method 3: From FlowSetupMain instance
from mechwolf.DataEntry.FlowSetups_New import FlowSetupMain

flow_app = FlowSetupMain("config.json")
# ... configure components and connections using the GUI ...

A = ApparatusFactory.create_apparatus_from_flow_setup(flow_app, "My_Apparatus")
```

### 4. Configuration Management
```python
from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory

# List available configurations
available_configs = ApparatusFactory.list_available_configs("./configs/")
print("Available configurations:", available_configs)

# Validate a configuration
is_valid = ApparatusFactory.validate_config("my_config.json")
print(f"Configuration valid: {is_valid}")

# Print configuration summary
ApparatusFactory.print_config_summary("example_birch_reduction.json")
```

### 5. Convenience Functions
```python
from mechwolf.DataEntry.FlowSetups_New import create_apparatus_from_config

# Simple one-liner to create apparatus
A = create_apparatus_from_config('birch_reduction.json')

# Ready to use with protocols
P = mw.Protocol(A)
```

## 🔧 Creating Configuration Files

You can create configuration files in three ways:

### Method 1: Use the FlowSetups GUI
```python
from mechwolf.DataEntry.FlowSetups_New import quick_start

# Launch the GUI to build your configuration
app = quick_start("my_new_config.json")
# Use the GUI to configure components and connections
# Save the configuration when done
```

### Method 2: Export from FlowSetupMain
```python
from mechwolf.DataEntry.FlowSetups_New import FlowSetupMain

app = FlowSetupMain("config.json")
# ... configure using the interface ...

# Get the current configuration
config = app.get_current_config()

# Create apparatus from this configuration
A = ApparatusFactory.create_apparatus_from_components(
    config["apparatus_config"]["components"],
    config["apparatus_config"]["connections"],
    "My_Apparatus"
)
```

### Method 3: Write JSON manually (advanced)
```json
{
    "version": "2.0.0",
    "apparatus_config": {
        "name": "My_Apparatus",
        "description": "Custom apparatus",
        "components": {
            "active": [...],
            "passive": [...]
        },
        "connections": [...]
    }
}
```

## 🎯 Key Benefits

1. **Simple Interface**: One-line apparatus creation
2. **Backward Compatibility**: Works with old-style code patterns
3. **Flexible Input**: Support for config files, dictionaries, or GUI instances
4. **Validation**: Built-in configuration validation
5. **Error Handling**: Graceful handling of missing components
6. **Ready to Use**: Apparatus returned ready for protocol creation

## 🔄 Migration from Old FlowSetups

### Before (Old FlowSetups):
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory

# Define pumps
pump_1 = mw.HarvardSyringePump(...)
pump_2 = mw.HarvardSyringePump(...)

# Create apparatus
A = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump_1, pump_2])
```

### After (New FlowSetups_New):
```python
from mechwolf.DataEntry.FlowSetups_New import create_setup

# All components are defined in the JSON config file
A = create_setup('my_apparatus', 'two_syringes_config.json')
```

### Key Differences:
1. **Component Definition**: Components are now defined in JSON instead of Python code
2. **Configuration Storage**: All apparatus details are stored in JSON files
3. **GUI Support**: Configuration files can be created/edited using the modern GUI
4. **Better Validation**: Schema-based validation ensures configuration integrity
5. **Modular Design**: Cleaner separation between configuration and execution

## 📊 Example Output

When you run:
```python
A = ApparatusFactory.create_apparatus_from_config('example_birch_reduction.json')
```

You get a fully configured MechWolf apparatus with:
- All components instantiated (pumps, valves, vessels, tubes)
- All connections established
- Ready for protocol definition and execution
- Proper error handling for missing/invalid components

The apparatus behaves exactly like apparatus created with the old system, but with better configuration management and validation.