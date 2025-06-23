# API Reference: Flow Setups Module

Complete API documentation for the MechWolf Flow Setups module.

## FlowSetupFactory

Main factory class for creating flow setups.

### `create_setup(setup_type, pumps, data_file=None)`

Create apparatus setup based on type.

**Parameters:**
- `setup_type` (str): Type of setup to create
  - `'two_syringes_1r_1m'`: Two syringes, 1 reactor, 1 mixer
  - `'three_syringes_1r_1m'`: Three syringes, 1 reactor, 1 mixer  
  - `'three_syringes_2r_2m'`: Three syringes, 2 reactors, 2 mixers
  - `'flexible_setup'`: Variable configuration
- `pumps` (List[HarvardSyringePump]): List of pumps to use
- `data_file` (str, optional): JSON file for configuration (default: "apparatus_config.json")

**Returns:**
- `mw.Apparatus`: Configured MechWolf Apparatus

**Raises:**
- `ValueError`: If setup_type is not supported

**Example:**
```python
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])
```

### `create_creator(setup_type, pumps, data_file=None)`

Create apparatus creator without immediately building apparatus.

**Parameters:**
- Same as `create_setup()`

**Returns:**
- Apparatus creator instance

**Example:**
```python
creator = FlowSetupFactory.create_creator('two_syringes_1r_1m', [pump1, pump2])
apparatus = creator.create_apparatus()
```

### `available_setups()`

Return list of available setup types.

**Returns:**
- `List[str]`: List of setup type names

**Example:**
```python
setups = FlowSetupFactory.available_setups()
print(setups)  # ['two_syringes_1r_1m', 'three_syringes_1r_1m', ...]
```

### `get_setup_info(setup_type=None)`

Get information about available setups.

**Parameters:**
- `setup_type` (str, optional): Specific setup to get info for, or None for all

**Returns:**
- `Dict[str, Any]`: Dictionary with setup information

**Example:**
```python
# Get info for specific setup
info = FlowSetupFactory.get_setup_info('two_syringes_1r_1m')
print(f"Name: {info['name']}")
print(f"Vessels: {info['num_vessels']}")

# Get info for all setups
all_info = FlowSetupFactory.get_setup_info()
```

### `print_available_setups()`

Print formatted list of available setups.

**Example:**
```python
FlowSetupFactory.print_available_setups()
```

## Configuration System

### FlowSetupConfig

Data class for setup configuration.

**Attributes:**
- `name` (str): Human-readable name
- `description` (str): Detailed description
- `num_vessels` (int): Number of input vessels (excluding product)
- `num_coils` (int): Number of coil sections
- `num_mixers` (int): Number of mixers
- `coil_letters` (List[str]): Letters identifying coils (e.g., ['a', 'x'])

**Methods:**

#### `to_dict()`

Convert configuration to dictionary for widget creation.

**Returns:**
- `Dict[str, Any]`: Configuration dictionary

### Configuration Functions

#### `get_config(setup_type)`

Get configuration for a setup type.

**Parameters:**
- `setup_type` (str): Setup type name

**Returns:**
- `FlowSetupConfig`: Configuration object

**Raises:**
- `ValueError`: If setup_type is unknown

**Example:**
```python
config = get_config('two_syringes_1r_1m')
print(f"Vessels: {config.num_vessels}")
```

#### `list_available_configs()`

List all available configurations.

**Returns:**
- `List[str]`: List of setup type names

#### `add_custom_config(setup_type, config)`

Add a custom configuration.

**Parameters:**
- `setup_type` (str): Name for the new setup type
- `config` (FlowSetupConfig): Configuration object

**Example:**
```python
custom_config = FlowSetupConfig(
    name="My Custom Setup",
    description="Custom flow setup",
    num_vessels=4,
    num_coils=3,
    num_mixers=2,
    coil_letters=['a', 'b', 'x']
)
add_custom_config('my_custom_setup', custom_config)
```

## Base Classes

### BaseComponentApp

Abstract base class for component applications.

**Constructor:**
```python
BaseComponentApp(pumps, json_file, config)
```

**Parameters:**
- `pumps` (List[HarvardSyringePump]): List of pumps
- `json_file` (str): Configuration file path
- `config` (FlowSetupConfig): Setup configuration

**Methods:**

#### `create_widgets()`

Create widgets using the configuration.

#### `create_setup(b)`

Standard setup creation flow (called by button click).

**Parameters:**
- `b`: Button widget (unused)

#### `_gather_inputs()` (Abstract)

Gather inputs specific to this setup type.

#### `_create_apparatus_config()` (Abstract)

Create apparatus config specific to this setup type.

**Returns:**
- `Dict[str, Any]`: Apparatus configuration

#### `_validate_inputs()`

Common validation logic.

#### `_process_data()`

Common data processing (tube dimensions, coil lengths).

### BaseApparatusCreator

Abstract base class for apparatus creators.

**Constructor:**
```python
BaseApparatusCreator(*pumps, data_file=None)
```

**Parameters:**
- `*pumps` (HarvardSyringePump): Variable number of pumps
- `data_file` (str, optional): JSON configuration file

**Methods:**

#### `create_apparatus()`

Template method for apparatus creation.

**Returns:**
- `mw.Apparatus`: Configured apparatus

#### `_create_component_app()` (Abstract)

Create the appropriate component app.

#### `_build_apparatus()` (Abstract)

Build the specific apparatus configuration.

**Returns:**
- `mw.Apparatus`: Built apparatus

#### `_load_config()`

Load configuration from JSON file.

**Returns:**
- `Dict[str, Any]`: Configuration dictionary

#### `_make_tube(tube_config, length=None)`

Create a tube with given configuration and length.

**Parameters:**
- `tube_config` (Dict[str, Any]): Tube configuration
- `length` (str, optional): Tube length

**Returns:**
- `mw.Tube`: Configured tube

## Specific Setup Classes

### TwoSyringesApparatusCreator

Creator for two-syringe setups.

**Constructor:**
```python
TwoSyringesApparatusCreator(pump1, pump2, data_file=None)
```

**Example:**
```python
creator = TwoSyringesApparatusCreator(pump1, pump2, data_file="config.json")
apparatus = creator.create_apparatus()
```

### ThreeSyringes1R1MApparatusCreator

Creator for three-syringe, 1-reactor, 1-mixer setups.

**Constructor:**
```python
ThreeSyringes1R1MApparatusCreator(pump1, pump2, pump3, data_file=None)
```

### ThreeSyringes2R2MApparatusCreator

Creator for three-syringe, 2-reactor, 2-mixer setups.

**Constructor:**
```python
ThreeSyringes2R2MApparatusCreator(pump1, pump2, pump3, data_file=None)
```

### FlexibleSetupApparatusCreator

Creator for flexible setups with variable vessel count.

**Constructor:**
```python
FlexibleSetupApparatusCreator(*pumps, data_file=None)
```

## Widget Management

### WidgetManager

Manages creation and handling of IPython widgets.

**Constructor:**
```python
WidgetManager(component_app)
```

**Methods:**

#### `create_all_widgets(**config)`

Create all widgets with configurable numbers of components.

**Parameters:**
- `**config`: Configuration parameters (num_vessels, num_tubes, etc.)

#### `get_widget_values()`

Get all widget values as dictionary.

**Returns:**
- `Dict[str, Any]`: Widget values

#### `prefill_values(config)`

Prefill widgets with existing configuration.

**Parameters:**
- `config` (Dict[str, Any]): Configuration to prefill

## Data Management

### DataManager

Handles JSON configuration file operations.

**Constructor:**
```python
DataManager(json_file)
```

**Parameters:**
- `json_file` (str): Path to JSON configuration file

**Methods:**

#### `save_config(config)`

Save apparatus configuration to JSON file.

**Parameters:**
- `config` (Dict[str, Any]): Configuration to save

#### `load_config()`

Load configuration from JSON file.

**Returns:**
- `Dict[str, Any]` or `None`: Loaded configuration, or None if file doesn't exist

## Error Handling

### ValidationError

Exception raised for user input validation errors.

**Constructor:**
```python
ValidationError(message)
```

### ErrorHandler

Static class for validation functions.

#### `validate_mixer_inputs(data)`

Validate mixer configuration.

**Parameters:**
- `data` (Dict[str, Any]): Input data to validate

**Raises:**
- `ValidationError`: If mixer configuration is invalid

#### `validate_tube_dimensions(tube_data)`

Validate tube dimensions (OD > ID).

**Parameters:**
- `tube_data` (Dict[str, Any]): Tube data to validate

**Raises:**
- `ValidationError`: If tube dimensions are invalid

#### `validate_coil_lengths(coil_lengths)`

Validate coil lengths are positive.

**Parameters:**
- `coil_lengths` (List[float]): Coil lengths to validate

**Raises:**
- `ValidationError`: If any coil length is invalid

## Utility Functions

### `parse_tube_dimension(raw_input)`

Convert user input to standardized tube dimension.

**Parameters:**
- `raw_input` (str): User input (e.g., "1/16 in", "0.5 mm")

**Returns:**
- `str`: Standardized dimension string

**Example:**
```python
dimension = parse_tube_dimension("1/16 in")
print(dimension)  # "0.0625 in"
```

### `parse_numeric_foot(raw_input)`

Convert user input to standardized length.

**Parameters:**
- `raw_input` (str): User input (e.g., "10 ft", "3 m")

**Returns:**
- `str`: Standardized length string

**Example:**
```python
length = parse_numeric_foot("10 ft")
print(length)  # "10 ft"
```

## Constants

### FLOW_CONFIGS

Dictionary of predefined flow configurations.

**Type:** `Dict[str, FlowSetupConfig]`

**Keys:**
- `'two_syringes_1r_1m'`
- `'three_syringes_1r_1m'`
- `'three_syringes_2r_2m'`
- `'flexible_setup'`

## Exception Hierarchy

```
Exception
├── ValidationError          # User input validation errors
├── ConfigurationError       # Setup configuration errors  
└── ApparatusError          # MechWolf apparatus creation errors
```

## Type Hints

The module uses comprehensive type hints throughout:

```python
from typing import List, Dict, Any, Optional, Union
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import mechwolf as mw

def create_setup(
    setup_type: str, 
    pumps: List[HarvardSyringePump], 
    data_file: Optional[str] = None
) -> mw.Apparatus:
    pass
```

## Usage Patterns

### Basic Usage
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory

apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])
```

### Advanced Usage
```python
from mechwolf.DataEntry.FlowSetups import (
    FlowSetupFactory, 
    TwoSyringesApparatusCreator,
    get_config
)

# Using factory
apparatus1 = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])

# Using creator directly
creator = TwoSyringesApparatusCreator(pump1, pump2, data_file="my_config.json")
apparatus2 = creator.create_apparatus()

# Getting configuration info
config = get_config('two_syringes_1r_1m')
print(f"This setup uses {config.num_vessels} vessels")
```

### Custom Configuration
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupConfig, add_custom_config

# Create custom configuration
custom_config = FlowSetupConfig(
    name="Quadruple Syringe Setup",
    description="Four-syringe advanced setup",
    num_vessels=4,
    num_coils=4,
    num_mixers=3,
    coil_letters=['a', 'b', 'c', 'x']
)

# Add to system
add_custom_config('quad_syringe_setup', custom_config)

# Use custom setup (after implementing creator class)
apparatus = FlowSetupFactory.create_setup('quad_syringe_setup', pumps)
```
