# Contributing Guide: Flow Setups Module

Guide for developers who want to extend the Flow Setups system by adding new setup types or modifying existing functionality.

## Overview

The Flow Setups module is designed to be easily extensible. Adding a new setup type involves:

1. Creating a configuration template
2. Implementing the component app class
3. Implementing the apparatus creator class
4. Registering the new setup type
5. Testing and documentation

## Step-by-Step: Adding a New Setup Type

### Step 1: Define Configuration

Add your setup configuration to `config_templates.py`:

```python
# In config_templates.py
FLOW_CONFIGS['my_new_setup'] = FlowSetupConfig(
    name="My New Setup Type",
    description="Detailed description of what this setup does",
    num_vessels=4,           # Number of input vessels (excluding product)
    num_coils=3,            # Number of coil sections
    num_mixers=2,           # Number of mixers
    coil_letters=['a', 'b', 'x']  # Letters identifying each coil
)
```

### Step 2: Create Component App

Create a new file `my_new_setup.py`:

```python
"""
My New Setup Implementation

Description of what this setup does and when to use it.
"""
from typing import Dict, Any, List
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

from .base_classes import BaseComponentApp, BaseApparatusCreator
from .config_templates import get_config


class MyNewSetupComponentApp(BaseComponentApp):
    """Component app for my new setup"""
    
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str):
        config = get_config('my_new_setup')
        super().__init__(pumps, json_file, config)
    
    def _gather_inputs(self) -> None:
        """Gather inputs specific to my new setup"""
        widget_values = self.widget_manager.get_widget_values()
        
        # Collect all widget values needed for your setup
        self.data = {
            "apparatus_name": widget_values["apparatus_name"],
            
            # Vessel information
            "vessel1_name": widget_values["vessel1_name"],
            "vessel1_desc": widget_values["vessel1_desc"],
            "vessel2_name": widget_values["vessel2_name"],
            "vessel2_desc": widget_values["vessel2_desc"],
            # ... add more vessels as needed
            
            "product_vessel_name": widget_values["product_vessel_name"],
            "product_vessel_desc": widget_values["product_vessel_desc"],
            
            # Tube specifications
            "reaction_tube_id_raw": widget_values["reaction_tube1_id"],
            "reaction_tube_od_raw": widget_values["reaction_tube1_od"],
            "reaction_tube_material": widget_values["reaction_tube1_material"],
            
            # Mixer settings
            "using_mixer": widget_values["using_mixer"],
            "mixer_tube_id_raw": widget_values["mixer1_tube_id"],
            "mixer_tube_od_raw": widget_values["mixer1_tube_od"],
            "mixer_tube_material": widget_values["mixer1_tube_material"],
            
            # Coil lengths (based on your coil_letters)
            "coil_a_raw": widget_values["coil_a"],
            "coil_b_raw": widget_values["coil_b"],
            "coil_x_raw": widget_values["coil_x"],
        }
    
    def _create_apparatus_config(self) -> Dict[str, Any]:
        """Create apparatus config for my new setup"""
        config = {
            "apparatus_name": self.data["apparatus_name"],
            "setup_type": "my_new_setup",
            
            # Vessel configurations
            "vessels": [
                {
                    "name": self.data["vessel1_name"],
                    "description": self.data["vessel1_desc"],
                },
                {
                    "name": self.data["vessel2_name"],
                    "description": self.data["vessel2_desc"],
                },
                # ... add more vessels
                {
                    "name": self.data["product_vessel_name"],
                    "description": self.data["product_vessel_desc"],
                },
            ],
            
            # Tube configurations
            "tubes": {
                "reaction": {
                    "ID": self.data["reaction_tube_ID"],
                    "OD": self.data["reaction_tube_OD"],
                    "material": self.data["reaction_tube_material"],
                }
            },
            
            # Coil configurations
            "coils": [
                {"letter": "a", "length": self.data["coil_a_length"]},
                {"letter": "b", "length": self.data["coil_b_length"]},
                {"letter": "x", "length": self.data["coil_x_length"]},
            ],
            
            # Mixer configuration
            "using_mixer": self.data["using_mixer"],
        }
        
        # Add mixer tube details if using mixer
        if self.data["using_mixer"]:
            config["tubes"]["mixer"] = {
                "ID": self.data["mixer_tube_ID"],
                "OD": self.data["mixer_tube_OD"],
                "material": self.data["mixer_tube_material"],
            }
        
        return config


class MyNewSetupApparatusCreator(BaseApparatusCreator):
    """Apparatus creator for my new setup"""
    
    def _create_component_app(self):
        """Create the my new setup component app"""
        return MyNewSetupComponentApp(self.pumps, self.json_file)
    
    def _build_apparatus(self) -> mw.Apparatus:
        """Build apparatus for my new setup"""
        config = self._load_config()
        print(f"Creating apparatus: {config['apparatus_name']}")
        
        # Create apparatus
        A = mw.Apparatus(config["apparatus_name"])
        
        # Create vessels
        vessels = [
            mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]
        ]
        # Unpack vessels based on your setup
        vessel1, vessel2, product_vessel = vessels[:3]  # Adjust as needed
        
        # Create tubes and coils
        reaction_tube = lambda length: self._make_tube(config["tubes"]["reaction"], length)
        if config["using_mixer"]:
            mixer_tube = lambda length: self._make_tube(config["tubes"]["mixer"], length)
        
        # Get coil lengths by letter
        coil_lengths = {coil["letter"]: coil["length"] for coil in config["coils"]}
        coil_a = reaction_tube(coil_lengths["a"])
        coil_b = reaction_tube(coil_lengths["b"])
        coil_x = reaction_tube(coil_lengths["x"])
        
        # Create mixers
        def Tmixer(name: str) -> mw.TMixer:
            return mw.TMixer(name=name)
        
        T1 = Tmixer("mixer1")
        T2 = Tmixer("mixer2")  # If you need multiple mixers
        
        # Build apparatus connections
        # This is where you define how your setup connects components
        # Example for a complex setup:
        
        if self.pump_type == "single-channel":
            # Connect each pump to its vessel
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
            # ... add more pump connections
        elif self.pump_type == "dual-channel":
            # For dual-channel pumps, connect multiple vessels to one pump
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)
            # ... adjust based on your needs
        
        # Connect vessels to mixers and mixers to product
        # Example connection pattern - customize for your setup:
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        A.add(T1, T2, coil_b)
        A.add(T2, product_vessel, coil_x)
        
        return A
```

### Step 3: Register in Factory

Add your new setup to `factory.py`:

```python
# In factory.py, import your creator
from .my_new_setup import MyNewSetupApparatusCreator

# Add to the _CREATORS dictionary
class FlowSetupFactory:
    _CREATORS = {
        'two_syringes_1r_1m': TwoSyringesApparatusCreator,
        'three_syringes_1r_1m': ThreeSyringes1R1MApparatusCreator,
        'three_syringes_2r_2m': ThreeSyringes2R2MApparatusCreator,
        'flexible_setup': FlexibleSetupApparatusCreator,
        
        # Add your new setup
        'my_new_setup': MyNewSetupApparatusCreator,
    }
```

### Step 4: Update Public API

Add your classes to `__init__.py`:

```python
# In __init__.py
from .my_new_setup import MyNewSetupApparatusCreator, MyNewSetupComponentApp

__all__ = [
    # ... existing exports
    'MyNewSetupApparatusCreator',
    'MyNewSetupComponentApp',
]
```

### Step 5: Test Your Implementation

Create a test script to verify your setup works:

```python
# test_my_new_setup.py
import mechwolf as mw
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Create test pumps
pump1 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
pump2 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")
pump3 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM3")
pump4 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM4")

# Test your new setup
try:
    apparatus = FlowSetupFactory.create_setup(
        'my_new_setup', 
        [pump1, pump2, pump3, pump4],  # Adjust pump count as needed
        data_file='test_my_new_setup.json'
    )
    print("Setup created successfully!")
    print(f"Apparatus: {apparatus}")
except Exception as e:
    print(f"Error: {e}")
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints throughout
- Include comprehensive docstrings
- Use descriptive variable names

### Error Handling

Implement proper error handling:

```python
def _build_apparatus(self) -> mw.Apparatus:
    try:
        config = self._load_config()
    except FileNotFoundError:
        raise ConfigurationError("Configuration file not found")
    except json.JSONDecodeError:
        raise ConfigurationError("Invalid JSON in configuration file")
    
    try:
        # Build apparatus
        A = mw.Apparatus(config["apparatus_name"])
        # ... rest of apparatus building
        return A
    except KeyError as e:
        raise ConfigurationError(f"Missing configuration key: {e}")
    except Exception as e:
        raise ApparatusError(f"Failed to build apparatus: {e}")
```

### Validation

Add setup-specific validation:

```python
def _validate_inputs(self) -> None:
    """Add setup-specific validation"""
    # Call parent validation first
    super()._validate_inputs()
    
    # Add your custom validation
    if self.data["num_vessels"] < 2:
        raise ValidationError("Setup requires at least 2 vessels")
    
    if len(self.pumps) != self.data["expected_pump_count"]:
        raise ValidationError(f"Setup requires {self.data['expected_pump_count']} pumps")
```

### Documentation

Document your setup thoroughly:

```python
"""
My New Setup Implementation

This setup is designed for [specific use case]. It provides:
- Multiple vessel inputs for complex reactions
- Sequential mixing stages
- Flexible coil configuration

Best used for:
- Multi-step synthesis reactions
- Reactions requiring precise reagent addition timing
- Complex mixing patterns

Configuration:
- Vessels: 4 input + 1 product
- Coils: 3 (a, b, x)
- Mixers: 2 (T1, T2)

Connection Pattern:
vessel1 → T1
vessel2 → T1  } → T2 → product
vessel3 → T2
vessel4 → T2
"""
```

## Advanced Features

### Custom Widget Creation

If your setup needs special widgets:

```python
class MyNewSetupComponentApp(BaseComponentApp):
    def create_widgets(self) -> None:
        """Override to add custom widgets"""
        # Create standard widgets first
        super().create_widgets()
        
        # Add custom widgets
        self.widgets["custom_parameter"] = widgets.FloatSlider(
            value=1.0,
            min=0.0,
            max=10.0,
            step=0.1,
            description='Custom Param:',
            layout=widgets.Layout(width='50%')
        )
        
        # Add to widget container
        self.widget_container.children = (
            *self.widget_container.children,
            self.widgets["custom_parameter"]
        )
```

### Custom Validation

Add complex validation logic:

```python
class MySetupErrorHandler(ErrorHandler):
    @staticmethod
    def validate_my_setup_constraints(data):
        """Custom validation for my setup"""
        # Check vessel compatibility
        if data["vessel1_type"] == "glass" and data["reaction_temp"] > 200:
            raise ValidationError("Glass vessels cannot exceed 200°C")
        
        # Check flow rate constraints
        total_flow_rate = sum(data[f"pump{i}_flow_rate"] for i in range(1, 5))
        if total_flow_rate > data["max_system_flow_rate"]:
            raise ValidationError("Total flow rate exceeds system maximum")
```

### Custom Data Processing

Add specialized data processing:

```python
def _process_data(self) -> None:
    """Add custom data processing"""
    # Call parent processing first
    super()._process_data()
    
    # Add custom processing
    self._calculate_residence_times()
    self._optimize_coil_lengths()
    self._validate_pressure_drops()

def _calculate_residence_times(self) -> None:
    """Calculate residence times for each coil section"""
    for coil_letter in self.config.coil_letters:
        length = self.data[f"coil_{coil_letter}_length"]
        flow_rate = self.data["total_flow_rate"]
        tube_volume = self._calculate_tube_volume(coil_letter)
        residence_time = tube_volume / flow_rate
        self.data[f"coil_{coil_letter}_residence_time"] = residence_time
```

## Testing Guidelines

### Unit Tests

Create comprehensive unit tests:

```python
import unittest
from unittest.mock import Mock, patch
from mechwolf.DataEntry.FlowSetups.my_new_setup import MyNewSetupApparatusCreator

class TestMyNewSetup(unittest.TestCase):
    def setUp(self):
        self.pump1 = Mock()
        self.pump2 = Mock()
        self.pump3 = Mock()
        self.pump4 = Mock()
        self.creator = MyNewSetupApparatusCreator(
            self.pump1, self.pump2, self.pump3, self.pump4,
            data_file="test_config.json"
        )
    
    def test_creator_initialization(self):
        self.assertEqual(len(self.creator.pumps), 4)
        self.assertEqual(self.creator.json_file, "test_config.json")
    
    @patch('builtins.open', mock_open(read_data='{"apparatus_config": {...}}'))
    def test_apparatus_building(self):
        apparatus = self.creator._build_apparatus()
        self.assertIsInstance(apparatus, mw.Apparatus)
    
    def test_invalid_pump_count(self):
        with self.assertRaises(ValueError):
            MyNewSetupApparatusCreator(self.pump1, self.pump2)  # Too few pumps
```

### Integration Tests

Test the complete workflow:

```python
def test_complete_workflow(self):
    """Test the entire setup creation workflow"""
    # This would require manual interaction or widget mocking
    apparatus = FlowSetupFactory.create_setup('my_new_setup', pumps)
    
    # Verify apparatus structure
    self.assertIsInstance(apparatus, mw.Apparatus)
    self.assertEqual(len(apparatus.vessels), 5)  # 4 input + 1 product
    # ... more assertions
```

## Common Patterns

### Multi-Stage Reactions

For setups with multiple reaction stages:

```python
def _build_apparatus(self) -> mw.Apparatus:
    # Create multiple mixers for stages
    T1 = mw.TMixer(name="stage1_mixer")
    T2 = mw.TMixer(name="stage2_mixer")
    
    # Connect in sequence
    A.add(vessel1, T1, coil_a)
    A.add(vessel2, T1, coil_a)
    A.add(T1, T2, coil_b)
    A.add(vessel3, T2, coil_b)
    A.add(T2, product_vessel, coil_x)
```

### Variable Vessel Count

For setups with flexible vessel count:

```python
def _build_apparatus(self) -> mw.Apparatus:
    num_vessels = len(self.pumps)
    vessels = [mw.Vessel(f"vessel_{i}") for i in range(num_vessels)]
    product_vessel = mw.Vessel("product")
    
    # Connect all input vessels to main mixer
    T_main = mw.TMixer(name="main_mixer")
    for i, vessel in enumerate(vessels):
        A.add(self.pumps[i], vessel, coil_a)
        A.add(vessel, T_main, coil_a)
    
    A.add(T_main, product_vessel, coil_x)
```

## Best Practices

1. **Start Simple**: Begin with the simplest version that works, then add complexity
2. **Test Early**: Test your setup as soon as the basic structure is in place
3. **Document Everything**: Include clear docstrings and comments
4. **Follow Patterns**: Use the same patterns as existing setup types
5. **Validate Inputs**: Add comprehensive input validation
6. **Handle Errors**: Provide clear error messages for common problems
7. **Consider Reuse**: Extract common functionality to base classes when possible

## Troubleshooting

### Common Issues

**Widget creation fails**:
- Check that your configuration has all required fields
- Verify coil_letters match what you're using in widget creation

**Apparatus building fails**:
- Ensure all vessels are created before connections
- Check that coil lengths are properly parsed
- Verify pump connections match your pump type

**Configuration not saving**:
- Check file permissions
- Ensure JSON structure is valid
- Verify all required config fields are present

### Debugging Tips

1. Add print statements to track execution flow
2. Use debugger to step through apparatus building
3. Test with minimal configuration first
4. Check widget values before processing
5. Validate configuration structure before saving

## Submitting Your Contribution

1. **Test thoroughly** - Ensure your setup works in various scenarios
2. **Update documentation** - Add your setup to README and user guide
3. **Follow naming conventions** - Use consistent naming patterns
4. **Add examples** - Include usage examples in your documentation
5. **Consider edge cases** - Handle unusual pump configurations and input values

Your contribution helps make the Flow Setups system more versatile and useful for the entire lab!
