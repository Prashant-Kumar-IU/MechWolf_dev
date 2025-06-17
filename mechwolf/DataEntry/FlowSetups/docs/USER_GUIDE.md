# User Guide: MechWolf Flow Setups

Complete guide for using the Flow Setups module to create standardized apparatus configurations.

## Overview

The Flow Setups module provides an interactive interface for creating MechWolf apparatus configurations. Instead of manually writing apparatus setup code, you fill out a form and the system generates the apparatus for you.

## Getting Started

### Prerequisites

- MechWolf installed and working
- Jupyter notebook environment
- Pump objects already created

### Basic Workflow

1. **Create your pumps** - Define your HarvardSyringePump objects
2. **Call the factory** - Use `FlowSetupFactory.create_setup()`
3. **Fill the form** - Complete the interactive GUI that appears
4. **Get your apparatus** - The configured apparatus is returned
5. **Use in protocols** - Use the apparatus in your MechWolf protocols

## Step-by-Step Example

### 1. Import and Setup

```python
import mechwolf as mw
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Create your pumps
pump1 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
pump2 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")
```

### 2. Create the Apparatus

```python
# This will open an interactive form
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])
```

### 3. Fill Out the Form

When you run the above code, an interactive form appears with fields for:

- **Apparatus Name**: Give your apparatus a name
- **Vessel Information**: Names and descriptions for each vessel
- **Tube Specifications**: Inner diameter, outer diameter, and material
- **Coil Lengths**: Length of each coil section
- **Mixer Settings**: Whether to use a mixer and its specifications

### 4. Use the Apparatus

```python
# Create a protocol using your apparatus
protocol = mw.Protocol(apparatus)

# Add steps to your protocol
protocol.add_step(step_name="mix_reagents", duration="5 min")
```

## Available Setup Types

### Two Syringes, 1 Reactor, 1 Mixer (`two_syringes_1r_1m`)

**Best for**: Basic two-reagent mixing reactions

**Configuration**:
- 2 input vessels + 1 product vessel
- 2 coils (coil_a for mixing, coil_x for reaction)
- 1 T-mixer
- Compatible with single or dual-channel pumps

**Example**:
```python
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])
```

### Three Syringes, 1 Reactor, 1 Mixer (`three_syringes_1r_1m`)

**Best for**: Three-reagent reactions with single mixing point

**Configuration**:
- 3 input vessels + 1 product vessel
- 2 coils (coil_a, coil_x)
- 1 mixer
- Requires 3 pumps

**Example**:
```python
apparatus = FlowSetupFactory.create_setup('three_syringes_1r_1m', [pump1, pump2, pump3])
```

### Three Syringes, 2 Reactors, 2 Mixers (`three_syringes_2r_2m`)

**Best for**: Complex multi-step reactions

**Configuration**:
- 3 input vessels + 1 product vessel
- 4 coils (coil_a, coil_b, coil_x, coil_y)
- 2 mixers
- Sequential reaction stages

**Example**:
```python
apparatus = FlowSetupFactory.create_setup('three_syringes_2r_2m', [pump1, pump2, pump3])
```

### Flexible Setup (`flexible_setup`)

**Best for**: Custom configurations

**Configuration**:
- Variable number of vessels
- Customizable coil arrangement
- Flexible mixer placement

**Example**:
```python
apparatus = FlowSetupFactory.create_setup('flexible_setup', [pump1, pump2, pump3, pump4])
```

## Form Field Guide

### Apparatus Settings

- **Apparatus Name**: Descriptive name for your setup (e.g., "Peptide_Synthesis_Setup")

### Vessel Information

- **Vessel Name**: Short identifier (e.g., "Reagent_A", "Solvent")
- **Vessel Description**: Detailed description (e.g., "1M HCl in water")

### Tube Specifications

- **Inner Diameter (ID)**: Internal diameter of tubing (e.g., "1/16 in", "0.5 mm")
- **Outer Diameter (OD)**: External diameter of tubing (e.g., "1/8 in", "1.5 mm")
- **Material**: Tubing material (e.g., "PTFE", "stainless steel")

### Coil Settings

- **Coil Length**: Length of each coil section (e.g., "10 ft", "3 m")
- Different setups have different coil configurations (a, x, b, y)

### Mixer Settings

- **Use Mixer**: Check if you want to include a mixer
- **Mixer Tube Specs**: Same format as reaction tubes if mixer is used

## Configuration Persistence

### Automatic Saving

Configurations are automatically saved to JSON files:

```python
# Default filename: apparatus_config.json
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])

# Custom filename
apparatus = FlowSetupFactory.create_setup(
    'two_syringes_1r_1m', 
    [pump1, pump2], 
    data_file='my_experiment.json'
)
```

### Reusing Configurations

When you run the same setup again, the form will be pre-filled with your previous values:

```python
# This will show your previous settings
apparatus = FlowSetupFactory.create_setup(
    'two_syringes_1r_1m', 
    [pump1, pump2], 
    data_file='my_experiment.json'  # Same filename as before
)
```

## Utility Functions

### List Available Setups

```python
FlowSetupFactory.print_available_setups()
```

### Get Setup Information

```python
info = FlowSetupFactory.get_setup_info('two_syringes_1r_1m')
print(f"Name: {info['name']}")
print(f"Vessels: {info['num_vessels']}")
print(f"Coils: {info['coil_letters']}")
```

### Check Available Setups

```python
available = FlowSetupFactory.available_setups()
print("Available setup types:", available)
```

## Advanced Usage

### Using Creator Classes Directly

For more control, you can use creator classes directly:

```python
from mechwolf.DataEntry.FlowSetups import TwoSyringesApparatusCreator

# Create creator instance
creator = TwoSyringesApparatusCreator(pump1, pump2, data_file="config.json")

# Create apparatus
apparatus = creator.create_apparatus()
```

### Custom Configuration Files

You can organize your configurations by experiment:

```python
# Experiment 1
exp1_apparatus = FlowSetupFactory.create_setup(
    'two_syringes_1r_1m', 
    [pump1, pump2], 
    data_file='experiment_1_config.json'
)

# Experiment 2  
exp2_apparatus = FlowSetupFactory.create_setup(
    'three_syringes_1r_1m', 
    [pump1, pump2, pump3], 
    data_file='experiment_2_config.json'
)
```

## Common Input Formats

### Tube Dimensions

The system accepts various formats for tube dimensions:

```
- "1/16 in"      # Fractional inches
- "0.5 mm"       # Millimeters
- "1.5"          # Assumes millimeters if no unit
- "0.062 in"     # Decimal inches
```

### Coil Lengths

Various formats for coil lengths:

```
- "10 ft"        # Feet
- "3 m"          # Meters
- "120 in"       # Inches
- "300 cm"       # Centimeters
```

## Troubleshooting

### Common Issues

**Form doesn't appear**:
- Check that you're running in a Jupyter notebook
- Ensure ipywidgets is installed: `pip install ipywidgets`

**Invalid pump type error**:
- Make sure you're passing HarvardSyringePump objects
- Check that pumps are properly initialized

**Configuration not saving**:
- Check file permissions in your working directory
- Ensure the filename is valid (no special characters)

**Validation errors**:
- Check that tube OD > ID
- Ensure all required fields are filled
- Verify coil lengths are positive numbers

### Getting Help

If you encounter issues:

1. Check the error message carefully
2. Verify your input formats match the examples
3. Try with a simpler setup first
4. Check that all required fields are filled

## Examples by Use Case

### Simple Acid-Base Neutralization

```python
# Setup
acid_pump = HarvardSyringePump("5 mL", "10 mm", serial_port="COM1")
base_pump = HarvardSyringePump("5 mL", "10 mm", serial_port="COM2")

# Create apparatus
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [acid_pump, base_pump])

# In the form, you might enter:
# - Apparatus Name: "Acid_Base_Neutralization"
# - Vessel 1: "HCl_Solution" / "1M HCl in water"
# - Vessel 2: "NaOH_Solution" / "1M NaOH in water"
# - Product: "Neutralized_Solution" / "Salt water product"
```

### Organic Synthesis

```python
# Setup for multi-step synthesis
reagent1_pump = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
reagent2_pump = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")
catalyst_pump = HarvardSyringePump("1 mL", "10 mm", serial_port="COM3")

# Create complex apparatus
apparatus = FlowSetupFactory.create_setup(
    'three_syringes_2r_2m', 
    [reagent1_pump, reagent2_pump, catalyst_pump]
)
```

This completes the user guide. Users now have comprehensive instructions for using the Flow Setups module without being overwhelmed by implementation details.
