# Developer Guide: Flow Setups Architecture

This document explains the internal architecture and code flow for developers who need to understand, modify, or extend the Flow Setups system.

## Architecture Overview

The Flow Setups module uses several design patterns to create a modular, extensible system:

- **Factory Pattern**: `FlowSetupFactory` creates setup instances
- **Template Method Pattern**: Base classes define workflow, subclasses implement specifics
- **Strategy Pattern**: Different setup types implement different strategies
- **Observer Pattern**: Widget events trigger data processing

## Code Flow: Step-by-Step

When you call `FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump_1, pump_2])`, here's what happens:

### 1. Factory Resolution (`factory.py`)
```python
# FlowSetupFactory.create_setup() called
setup_type = 'two_syringes_1r_1m'
creator_class = _CREATORS[setup_type]  # → TwoSyringesApparatusCreator
creator = creator_class(pump_1, pump_2, data_file=None)
```

### 2. Creator Instantiation (`base_classes.py`)
```python
# BaseApparatusCreator.__init__()
self.pumps = (pump_1, pump_2)
self.json_file = "apparatus_config.json"  # default
self.pump_type = self._determine_pump_type()  # "dual-channel" or "single-channel"
```

### 3. Template Method Execution
```python
# creator.create_apparatus() follows template pattern:
app = self._create_component_app()           # Step 4
app.create_widgets()                         # Step 5
self._wait_for_setup_completion(app)         # Step 6-7
return self._build_apparatus()               # Step 8
```

### 4. Component App Creation (`two_syringes_setup.py`)
```python
# TwoSyringesApparatusCreator._create_component_app()
app = TwoSyringesComponentApp(self.pumps, self.json_file)

# TwoSyringesComponentApp.__init__()
config = get_config('two_syringes_1r_1m')  # Load configuration
super().__init__(pumps, json_file, config)
self.data_manager = DataManager(json_file)
self.widget_manager = WidgetManager(self)
```

### 5. Widget Creation (`widget_manager.py`)
```python
# app.create_widgets()
widgets = self.widget_manager.create_all_widgets(**config.to_dict())
# Creates: apparatus name, vessel inputs, tube specs, coil lengths, mixer settings
self.widget_container = self.widget_manager.widget_container
# Form is displayed in Jupyter notebook
```

### 6. User Interaction Phase
**⚠️ Code execution PAUSES here** waiting for user input:
- User sees interactive form in Jupyter
- User fills out fields and clicks "Create Setup"
- Button click triggers `app.create_setup()`

### 7. Data Processing Pipeline
When user clicks "Create Setup":

#### 7a. Input Gathering
```python
# TwoSyringesComponentApp._gather_inputs()
widget_values = self.widget_manager.get_widget_values()
self.data = {
    "apparatus_name": widget_values["apparatus_name"],
    "vessel1_name": widget_values["vessel1_name"],
    # ... all widget values collected
}
```

#### 7b. Validation (`error_handler.py`)
```python
# BaseComponentApp._validate_inputs()
ErrorHandler.validate_mixer_inputs(self.data)
# Checks mixer configuration consistency
```

#### 7c. Data Processing (`FlowSetupUtils.py`)
```python
# BaseComponentApp._process_data()
self.data["reaction_tube_ID"] = parse_tube_dimension(self.data["reaction_tube_id_raw"])
self.data["coil_a_length"] = parse_numeric_foot(self.data["coil_a_raw"])
# Converts user input to standardized units
```

#### 7d. Configuration Creation
```python
# TwoSyringesComponentApp._create_apparatus_config()
config = {
    "apparatus_name": self.data["apparatus_name"],
    "setup_type": "two_syringes_1r_1m",
    "vessels": [...],
    "tubes": {...},
    "coils": [...],
    "using_mixer": self.data["using_mixer"]
}
```

#### 7e. Data Persistence (`data_manager.py`)
```python
# DataManager.save_config()
with open(self.json_file, "w") as f:
    json.dump({"apparatus_config": config}, f)
self.setup_complete = True  # Signals completion
```

### 8. Apparatus Building
Once `setup_complete = True`:

#### 8a. Configuration Loading
```python
# BaseApparatusCreator._load_config()
with open(self.json_file, "r") as f:
    data = json.load(f)
config = data["apparatus_config"]
```

#### 8b. MechWolf Component Creation
```python
# TwoSyringesApparatusCreator._build_apparatus()
A = mw.Apparatus(config["apparatus_name"])
vessels = [mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]]
vessel1, vessel2, product_vessel = vessels

# Create tubes and coils
reaction_tube = lambda length: self._make_tube(config["tubes"]["reaction"], length)
coil_a = reaction_tube(coil_lengths["a"])
coil_x = reaction_tube(coil_lengths["x"])
T1 = mw.TMixer(name=coil_x)
```

#### 8c. Apparatus Assembly
```python
# Connect components based on pump type and setup
if self.pump_type == "single-channel":
    A.add(self.pumps[0], vessel1, coil_a)
    A.add(self.pumps[1], vessel2, coil_a)
elif self.pump_type == "dual-channel":
    A.add(self.pumps[0], vessel1, coil_a)
    A.add(self.pumps[0], vessel2, coil_a)

A.add(vessel1, T1, coil_a)
A.add(vessel2, T1, coil_a)
A.add(T1, product_vessel, coil_x)
```

### 9. Return Complete Apparatus
```python
return A  # Fully configured mw.Apparatus object
```

## File Architecture

### Core Framework

#### `__init__.py` - Public API
- Exposes main classes: `FlowSetupFactory`, creator classes
- Controls imports and public interface
- Provides module-level documentation

#### `factory.py` - Factory Implementation
```python
class FlowSetupFactory:
    _CREATORS = {
        'two_syringes_1r_1m': TwoSyringesApparatusCreator,
        'three_syringes_1r_1m': ThreeSyringes1R1MApparatusCreator,
        # ...
    }
    
    @classmethod
    def create_setup(cls, setup_type, pumps, data_file=None):
        creator_class = cls._CREATORS[setup_type]
        creator = creator_class(*pumps, data_file=data_file)
        return creator.create_apparatus()
```

#### `base_classes.py` - Abstract Framework
```python
class BaseComponentApp(ABC):
    """Handles UI and data processing"""
    def create_widgets(self): pass  # Common widget creation
    def create_setup(self): pass    # Common setup flow
    
    @abstractmethod
    def _gather_inputs(self): pass      # Setup-specific input gathering
    @abstractmethod
    def _create_apparatus_config(self): pass  # Setup-specific config

class BaseApparatusCreator(ABC):
    """Handles apparatus creation"""
    def create_apparatus(self): pass    # Template method
    
    @abstractmethod
    def _create_component_app(self): pass   # Create specific app
    @abstractmethod
    def _build_apparatus(self): pass        # Build specific apparatus
```

#### `config_templates.py` - Configuration System
```python
@dataclass
class FlowSetupConfig:
    name: str
    num_vessels: int
    num_coils: int
    num_mixers: int
    coil_letters: List[str]
    description: str = ""

FLOW_CONFIGS = {
    'two_syringes_1r_1m': FlowSetupConfig(
        name="Two Syringes, 1 Reaction Coil, 1 Mixer",
        num_vessels=2,
        num_coils=2,
        num_mixers=1,
        coil_letters=['a', 'x']
    ),
    # ...
}
```

### Setup Implementations

#### `two_syringes_setup.py` - Two Syringe Implementation
```python
class TwoSyringesComponentApp(BaseComponentApp):
    def _gather_inputs(self):
        # Collect values for 2-syringe setup
        self.data = {
            "vessel1_name": widget_values["vessel1_name"],
            "vessel2_name": widget_values["vessel2_name"],
            # ...
        }
    
    def _create_apparatus_config(self):
        # Create JSON config for 2-syringe setup
        return {
            "apparatus_name": self.data["apparatus_name"],
            "setup_type": "two_syringes_1r_1m",
            "vessels": [...],
            # ...
        }

class TwoSyringesApparatusCreator(BaseApparatusCreator):
    def _create_component_app(self):
        return TwoSyringesComponentApp(self.pumps, self.json_file)
    
    def _build_apparatus(self):
        # Build MechWolf apparatus for 2-syringe setup
        # Connect pumps → vessels → mixer → product
        pass
```

### Support Modules

#### `widget_manager.py` - UI Management
```python
class WidgetManager:
    def create_all_widgets(self, **config):
        # Create widgets based on configuration
        self.create_vessel_widgets(config['num_vessels'])
        self.create_tube_widgets(config['num_tubes'])
        self.create_coil_widgets(config['num_coils'])
        self.create_mixer_widgets(config['num_mixers'])
    
    def get_widget_values(self):
        # Extract all widget values as dictionary
        return {name: widget.value for name, widget in self.widgets.items()}
```

#### `data_manager.py` - Configuration Persistence
```python
class DataManager:
    def save_config(self, config):
        data = {"apparatus_config": config, "timestamp": datetime.now()}
        with open(self.json_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_config(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as f:
                return json.load(f).get("apparatus_config")
        return None
```

#### `error_handler.py` - Validation
```python
class ErrorHandler:
    @staticmethod
    def validate_mixer_inputs(data):
        if data.get("using_mixer") and not data.get("mixer_tube_id_raw"):
            raise ValidationError("Mixer tube ID required when using mixer")
    
    @staticmethod
    def validate_tube_dimensions(tube_data):
        for id_val, od_val in tube_data.get("reaction_tubes", []):
            if od_val <= id_val:
                raise ValidationError("Tube OD must be greater than ID")
```

#### `FlowSetupUtils.py` - Utility Functions
```python
def parse_tube_dimension(raw_input: str) -> str:
    """Convert user input like '1/16 in' to standardized format"""
    # Handle fractional inches, decimal inches, millimeters
    pass

def parse_numeric_foot(raw_input: str) -> str:
    """Convert user input like '10 ft' to standardized format"""
    # Handle feet, meters, inches, centimeters
    pass
```

## Design Pattern Details

### Factory Pattern Benefits
- **Encapsulation**: Object creation logic is hidden
- **Extensibility**: Add new setup types without modifying existing code
- **Consistency**: All setups created through same interface

### Template Method Pattern Benefits
- **Code Reuse**: Common workflow shared across all setups
- **Customization**: Each setup can customize specific steps
- **Consistency**: All setups follow same basic flow

### Strategy Pattern Benefits
- **Flexibility**: Different setup strategies can be swapped at runtime
- **Isolation**: Each setup type is independent
- **Testing**: Individual strategies can be tested separately

## Extension Guide

### Adding a New Setup Type

#### 1. Create Configuration
```python
# In config_templates.py
FLOW_CONFIGS['my_new_setup'] = FlowSetupConfig(
    name="My New Setup Type",
    description="Description of my setup",
    num_vessels=4,
    num_coils=3,
    num_mixers=2,
    coil_letters=['a', 'b', 'x']
)
```

#### 2. Implement Component App
```python
# In my_new_setup.py
class MyNewSetupComponentApp(BaseComponentApp):
    def __init__(self, pumps, json_file):
        config = get_config('my_new_setup')
        super().__init__(pumps, json_file, config)
    
    def _gather_inputs(self):
        widget_values = self.widget_manager.get_widget_values()
        self.data = {
            # Collect values specific to your setup
        }
    
    def _create_apparatus_config(self):
        return {
            # Create JSON config specific to your setup
        }
```

#### 3. Implement Apparatus Creator
```python
class MyNewSetupApparatusCreator(BaseApparatusCreator):
    def _create_component_app(self):
        return MyNewSetupComponentApp(self.pumps, self.json_file)
    
    def _build_apparatus(self):
        config = self._load_config()
        # Build MechWolf apparatus based on your setup
        A = mw.Apparatus(config["apparatus_name"])
        # Add vessels, tubes, coils, connections
        return A
```

#### 4. Register in Factory
```python
# In factory.py
_CREATORS = {
    # ... existing creators
    'my_new_setup': MyNewSetupApparatusCreator,
}
```

#### 5. Update Public API
```python
# In __init__.py
from .my_new_setup import MyNewSetupApparatusCreator, MyNewSetupComponentApp

__all__ = [
    # ... existing exports
    'MyNewSetupApparatusCreator',
    'MyNewSetupComponentApp',
]
```

## Error Handling Strategy

### Layered Validation
1. **Widget Level**: Immediate feedback on invalid input
2. **Form Level**: Validation before processing
3. **Data Level**: Business logic validation
4. **System Level**: Exception handling and recovery

### Error Types
```python
class ValidationError(Exception):
    """User input validation errors"""
    pass

class ConfigurationError(Exception):
    """Setup configuration errors"""
    pass

class ApparatusError(Exception):
    """MechWolf apparatus creation errors"""
    pass
```

## Testing Strategy

### Unit Testing
- Test individual classes and methods
- Mock dependencies for isolation
- Test edge cases and error conditions

### Integration Testing
- Test component interactions
- Test complete workflow
- Test with different pump configurations

### Widget Testing
- Test UI behavior
- Test form validation
- Test event handling

## Performance Considerations

### Widget Creation
- Widgets are created on-demand
- Reuse widget instances when possible
- Minimize DOM updates

### Data Processing
- Parse inputs only when needed
- Cache parsed values
- Validate incrementally

### File I/O
- Use JSON for human-readable configs
- Implement atomic writes for safety
- Handle file permission errors gracefully

## Security Considerations

### File Operations
- Validate file paths to prevent directory traversal
- Handle file permissions properly
- Use safe JSON parsing

### Input Validation
- Sanitize all user inputs
- Validate numeric ranges
- Prevent code injection through widget values

This developer guide provides the detailed understanding needed to work with, modify, or extend the Flow Setups system effectively.
