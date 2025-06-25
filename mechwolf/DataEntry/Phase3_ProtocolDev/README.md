# Phase 3: Simple Protocol Builder

A streamlined, table-based interface for building MechWolf protocols that generates clean, readable code with proper `timedelta` variable handling.

## 🎯 Overview

The Simple Protocol Builder is designed to generate **exactly** the MechWolf protocol code format you want:

```python
P = mw.Protocol(A)

switch = timedelta(seconds = 45)
current = timedelta(minutes = 0)
PPh3 = timedelta(minutes = 2)
H2O = timedelta(minutes = 1) 

P.add(pump_1, start = current, duration = PPh3 + H2O, rate = "0.5 mL/min")
current += PPh3
P.add(pump_2, start = current, duration = H2O, rate = "1 mL/min")
current += H2O + switch

print(f'TOTAL TIME: {current}')
# P.execute(confirm = True)
```

## 🚀 Quick Start

### 1. Load Your Experiment
```python
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager

# Load experiment with apparatus from Phase 2
experiment = ExperimentalMetadataManager("my_experiment.json")
```

### 2. Launch the Simple Protocol Builder
```python
from mechwolf.DataEntry.Phase3_ProtocolDev import launch_simple_builder

protocol_builder = launch_simple_builder(experiment)
```

### 3. Build Your Protocol Using the GUI

The interface has 4 tabs:

- **⏱️ Time Variables**: Define reusable time variables
- **➕ Add Procedures**: Add protocol steps  
- **📋 View Procedures**: Review current procedures
- **💻 Generated Code**: Copy the MechWolf code

### 4. Copy and Execute the Generated Code

Copy the generated code from the GUI and paste it into your notebook:

```python
# Load apparatus
from mechwolf.DataEntry.shared_components.apparatus_factory import ApparatusFactory
A = ApparatusFactory.create_apparatus_from_experiment(experiment)

# Paste generated protocol code here...
# (Your generated code)

# Execute protocol
experiment = P.execute(dry_run=1000)  # For testing
# experiment = P.execute(confirm=True)  # For real execution
```

## 📋 Detailed Usage Guide

### Time Variables Tab

**Purpose**: Define reusable time variables for clean code generation.

**Key Features**:
- Preset buttons for common variables (PPh3, H2O, flush, reaction)
- Custom variable creation with duration parsing
- Automatic `current` time tracking variable
- Switch time variable for delays between operations

**Example Variables**:
```
PPh3 = 2min      # Addition time for PPh3
H2O = 1min       # Addition time for H2O  
flush = 15min    # System flush duration
switch = 45s     # Switching delay
current = 0min   # Current protocol time (auto-managed)
```

### Add Procedures Tab

**Purpose**: Add protocol procedures step by step.

**Procedure Types**:

1. **Pump Run**:
   - Component: Select pump from apparatus
   - Action: Run
   - Start time: Use variables like `current`, `PPh3 + H2O`
   - Duration: Use variables like `PPh3`, `H2O + switch`
   - Flow rate: e.g., "0.5 mL/min", "2 mL/min"

2. **Valve Switch**:
   - Component: Select valve from apparatus
   - Action: Switch
   - Position: Port number or mapped reagent name

3. **Pump Stop**:
   - Component: Select pump
   - Action: Stop
   - Start time: When to stop the pump

**Time Expression Examples**:
- `current` - Start at current protocol time
- `PPh3` - Use the PPh3 duration variable
- `PPh3 + H2O` - Sum of two variables
- `PPh3 + H2O + switch` - Multiple variable sum

### View Procedures Tab

**Purpose**: Review and manage your protocol procedures.

**Features**:
- Numbered list of all procedures
- Component, action, timing, and parameter details
- Delete specific procedures by number
- Refresh display after changes

### Generated Code Tab

**Purpose**: View and copy the clean MechWolf protocol code.

**Features**:
- Real-time code generation
- Proper `timedelta` variable formatting
- Copy code for manual clipboard use
- Export code to Python file
- Ready-to-execute format

## 🎨 Generated Code Format

The Simple Protocol Builder generates code that matches this exact format:

### Variable Definitions
```python
import mechwolf as mw
from datetime import timedelta

# Time variable definitions
switch = timedelta(seconds = 45)
current = timedelta(minutes = 0)
PPh3 = timedelta(minutes = 2)
H2O = timedelta(minutes = 1)
```

### Protocol Creation
```python
# Create protocol from apparatus
P = mw.Protocol(A)
```

### Procedures with Clean Formatting
```python
# Protocol procedures
P.add(pump_1, start = current,
              duration = PPh3 + H2O, rate = "0.5 mL/min")

current += PPh3 + H2O

P.add(pump_2, start = current, 
              duration = H2O, rate = "1 mL/min")

current += H2O + switch
```

### Execution Template
```python
# Calculate total time
print(f'TOTAL TIME: {current}')

# Execute protocol (uncomment to run)
# P.execute(confirm = True)
```

## 💾 Data Persistence

### Automatic Saving
- Protocol procedures are automatically saved to experimental metadata
- Time variables are preserved between sessions
- Load existing protocols using the "Load Protocol" button

### Manual Save/Load
```python
# Save current protocol
protocol_builder._save_protocol(None)

# Load saved protocol  
protocol_builder._load_protocol(None)
```

## 🧪 Example Workflow

### Step 1: Define Time Variables
1. Go to "Time Variables" tab
2. Click preset buttons or add custom variables:
   - PPh3 = 2min
   - H2O = 1min  
   - flush = 15min
   - switch = 45s

### Step 2: Add Procedures
1. Go to "Add Procedures" tab
2. Add pump run procedure:
   - Component: pump_1
   - Action: run
   - Start time: current
   - Duration: PPh3 + H2O
   - Flow rate: 0.5 mL/min
   - ✓ Increment current time

3. Add second pump procedure:
   - Component: pump_2
   - Action: run
   - Start time: current
   - Duration: H2O
   - Flow rate: 1 mL/min
   - ✓ Increment current time

### Step 3: Add Flush Procedures
4. Add flush for pump_1:
   - Component: pump_1
   - Start time: current
   - Duration: flush
   - Flow rate: 0.5 mL/min

5. Add flush for pump_2:
   - Component: pump_2
   - Start time: current
   - Duration: flush  
   - Flow rate: 1 mL/min

### Step 4: Generate and Copy Code
1. Go to "Generated Code" tab
2. Review the generated protocol
3. Click "Copy Code" or "Export Code"
4. Paste into your Jupyter notebook

## 🔧 Advanced Features

### Component Detection
- Automatically loads components from Phase 2 apparatus configuration
- Supports Harvard pumps, VICI valves, and other active components
- Filters actions based on component capabilities

### Validation
- Time expression validation using defined variables
- Flow rate format checking
- Required parameter validation
- Component-action compatibility checking

### Code Optimization
- Intelligent variable ordering in generated code
- Proper indentation and formatting
- Minimal, clean output with no unnecessary code

## 📝 Integration with Experimental Metadata

The Simple Protocol Builder integrates seamlessly with the experimental metadata system:

### Loading Apparatus
```python
# Apparatus is automatically loaded from experimental metadata
apparatus_data = experiment.get_section_data("apparatus_config")
```

### Saving Protocols
```python
# Procedures are saved to the protocol_config section
protocol_data = {
    'procedures': [...],
    'time_variables': {...},
    'current_time_variable': 'current'
}
```

### Creating MechWolf Apparatus
```python
from mechwolf.DataEntry.shared_components.apparatus_factory import ApparatusFactory
A = ApparatusFactory.create_apparatus_from_experiment(experiment)
```

## 🆚 Comparison with Advanced GUI

| Feature | Simple Builder | Advanced GUI |
|---------|---------------|--------------|
| Interface | Table-based | Timeline/drag-drop |
| Complexity | Low | High |
| Code Format | Clean, readable | Standard MechWolf |
| Setup Time | Minimal | Longer |
| Learning Curve | Easy | Moderate |
| Use Case | Quick protocols | Complex workflows |

## 🐛 Troubleshooting

### Common Issues

**"No components loaded"**
- Ensure your experimental metadata has apparatus_config from Phase 2
- Check that components have valid names and types

**"Invalid time expression"**
- Define all variables before using them in expressions
- Use proper variable names (letters, numbers, underscore only)
- Check that expressions are syntactically correct

**"Component not found"**
- Verify the component exists in your apparatus configuration
- Check component naming consistency between phases

**"Generated code has errors"**
- Ensure all required parameters are provided
- Validate flow rate formats (e.g., "2 mL/min")
- Check that variable expressions are properly defined

### Getting Help

1. Check the integration test: `test_integration.py`
2. Review the usage example: `USAGE_EXAMPLE.py`
3. Examine existing protocol configurations in `examples/`

## 🔮 Future Enhancements

### Planned Features
- Visual timeline preview
- Protocol templates library
- Batch procedure import/export
- Real-time execution monitoring
- Advanced validation rules

### Extensibility
The Simple Protocol Builder is designed to be easily extended:
- Add new component types in `simple_protocol_builder.py`
- Extend code generation in `protocol_code_generator.py`
- Add new time variable formats in `time_variable_manager.py`

---

**Ready to build your first protocol?** Start with the Quick Start guide above! 🚀