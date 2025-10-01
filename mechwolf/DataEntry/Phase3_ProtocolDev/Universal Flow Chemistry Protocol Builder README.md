# Universal Flow Chemistry Protocol Builder

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![MechWolf Compatible](https://img.shields.io/badge/MechWolf-compatible-green.svg)](https://github.com/MechWolf/MechWolf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Transform flow chemistry protocol development from manual coding to intelligent, template-based design.

## 🌟 Overview

The Universal Flow Chemistry Protocol Builder revolutionizes how researchers create flow chemistry protocols. Instead of manually coding each protocol from scratch, researchers can now:

- **Select from proven templates** for common flow chemistry applications
- **Configure phases visually** through an intuitive GUI interface
- **Optimize parameters automatically** for yield, selectivity, and efficiency
- **Generate clean MechWolf code** that's readable and maintainable
- **Validate safety and feasibility** before execution

## 🚀 Quick Start

### Installation

```python
# Install as part of MechWolf DataEntry system
from mechwolf.DataEntry.Phase3_UniversalProtocolBuilder import launch_protocol_builder

# Load your experiment (requires Phase 1 reagents and Phase 2 apparatus)
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
experiment = ExperimentalMetadataManager("my_experiment.json")

# Launch the Protocol Builder
protocol_builder = launch_protocol_builder(experiment)
```

### 30-Second Example

```python
# 1. Select template
template = "Peptide Synthesis"

# 2. Configure sequence
peptide_sequence = "ARQIK"

# 3. Generate protocol
# → Clean MechWolf code automatically generated
# → Ready to execute or further customize
```

## 🎯 Key Features

### 📋 Template-Based Design
- **Built-in Templates**: Peptide synthesis, multi-step organic synthesis, catalyst screening
- **Custom Templates**: Create and share your own protocol patterns
- **Smart Validation**: Automatic compatibility checking with your apparatus

### ⚙️ Intelligent Phase Configuration
- **Visual Designer**: Drag-and-drop phase arrangement
- **Parameter Optimization**: Automatic calculation of flow rates, volumes, timing
- **Resource Integration**: Links to Phase 1 reagents and Phase 2 apparatus

### 🎯 Multi-Objective Optimization
- **Maximize**: Yield, selectivity, throughput, purity
- **Minimize**: Time, cost, waste, energy consumption
- **Constrain**: Safety limits, equipment capabilities, resource availability

### ✅ Comprehensive Validation
- **Safety Analysis**: Hazard identification and mitigation
- **Feasibility Check**: Apparatus compatibility and resource availability
- **Cost Estimation**: Reagent costs, time costs, equipment usage

### 💻 Clean Code Generation
- **Readable Output**: Well-commented, properly formatted MechWolf code
- **Multiple Formats**: Python scripts, Jupyter notebooks, JSON configs
- **Best Practices**: Follows MechWolf coding conventions

## 🏗️ Architecture

```
Phase3_UniversalProtocolBuilder/
├── 📁 core/                    # Core protocol building logic
├── 📁 templates/               # Template system and library
├── 📁 phases/                  # Phase definitions and implementations
├── 📁 optimization/            # Parameter optimization engine
├── 📁 validation/              # Safety and feasibility validation
├── 📁 code_generation/         # MechWolf code compilation
├── 📁 gui/                     # User interface components
└── 📁 integration/             # Phase 1/2 integration
```

## 🎨 User Interface

### 5-Tab Design for Complete Protocol Development

#### 📋 Tab 1: Templates
- Browse template library by category
- Preview template structure and requirements
- Select optimal template for your chemistry

#### ⚙️ Tab 2: Configure Phases
- Visual phase flow designer
- Parameter customization for each phase
- Real-time validation feedback

#### 🎯 Tab 3: Optimization
- Define optimization objectives
- Set practical constraints
- Run multi-parameter optimization

#### ✅ Tab 4: Validation
- Safety hazard analysis
- Resource availability check
- Timeline and cost visualization

#### 💻 Tab 5: Generated Code
- Clean, executable MechWolf protocol
- Multiple export formats
- Execution templates included

## 📚 Protocol Templates

### Synthesis Templates

#### Peptide Synthesis
```python
# Handles any peptide sequence
peptide_sequence = "ARQIKLVFF"  # User input
# Generates optimized coupling/deprotection cycles
# Automatic amino acid library management
# UV monitoring integration
```

#### Multi-Step Organic Synthesis
```python
# Sequential reactions: A + B → I → I + C → Product  
reactions = [
    {"reagents": ["substrate", "reagent_A"], "conditions": {...}},
    {"reagents": ["intermediate", "reagent_B"], "conditions": {...}}
]
# Optimizes reaction times, temperatures, stoichiometry
```

### Screening Templates

#### Catalyst Screening
```python
# Parallel catalyst evaluation
catalysts = ["Pd_catalyst", "Ru_catalyst", "Au_catalyst"]
# Automated screening with statistical analysis
# Real-time conversion monitoring
```

#### Reaction Optimization
```python
# DoE-based parameter optimization
variables = ["temperature", "flow_rate", "stoichiometry"]
# Automated multi-parameter screening
```

### Purification Templates

#### Liquid-Liquid Extraction
```python
# Multi-stage extraction optimization
phases = ["extraction", "separation", "purification"]
# Automatic phase ratio optimization
```

## 🔧 Integration with MechWolf Ecosystem

### Seamless Phase Integration

```python
# Phase 1: Reagent Entry → Automatic reagent availability
# Phase 2: Apparatus Design → Automatic component mapping  
# Phase 3: Protocol Builder → Intelligent protocol generation
# → Clean MechWolf execution
```

### Data Flow Architecture

```
Reagent Data (Phase 1) ──┐
                         ├─→ Protocol Builder ─→ Clean MechWolf Code
Apparatus Config (Phase 2) ─┘
```

## 📖 Usage Examples

### Example 1: Automated Peptide Synthesis

```python
from mechwolf.DataEntry.Phase3_UniversalProtocolBuilder import launch_protocol_builder

# Load experiment with reagents and apparatus
experiment = ExperimentalMetadataManager("peptide_experiment.json")

# Launch builder
builder = launch_protocol_builder(experiment)

# User workflow:
# 1. Select "Peptide Synthesis" template
# 2. Enter sequence: "ARQIKLVFF"  
# 3. Configure coupling conditions
# 4. Generate optimized protocol

# Result: Clean MechWolf code for 9-residue peptide
```

### Example 2: Multi-Step Synthesis Optimization

```python
# Template: Multi-Step Organic Synthesis
# Chemistry: Suzuki coupling followed by hydrogenation

# User configures:
phases = [
    {
        "name": "Suzuki Coupling",
        "reagents": ["aryl_halide", "boronic_acid", "Pd_catalyst"],
        "optimize_for": "conversion"
    },
    {
        "name": "Hydrogenation", 
        "reagents": ["alkene_intermediate", "H2", "Pd_C"],
        "optimize_for": "selectivity"
    }
]

# System generates optimized protocol with:
# - Calculated flow rates for desired residence times
# - Temperature profiles for each reaction
# - Automated workup and purification steps
```

### Example 3: Catalyst Screening Study

```python
# Template: Catalyst Screening
# Objective: Find best catalyst for C-H activation

screening_config = {
    "catalysts": ["Pd_OAc2", "Rh_Cp*", "Ir_complex"],
    "substrates": ["substrate_A", "substrate_B"], 
    "conditions": {
        "temperature_range": [80, 120],  # °C
        "flow_rate_range": [0.5, 2.0]   # mL/min
    },
    "analysis": ["GC_conversion", "HPLC_selectivity"]
}

# Generates DoE protocol with statistical analysis
```

## 🔬 Advanced Features

### Multi-Objective Optimization

```python
optimization_targets = {
    "maximize": ["yield", "selectivity", "throughput"],
    "minimize": ["reagent_cost", "synthesis_time", "waste"],
    "constraints": {
        "temperature": {"max": 150, "unit": "°C"},
        "pressure": {"max": 10, "unit": "bar"},
        "flow_rate": {"min": 0.1, "max": 5.0, "unit": "mL/min"}
    }
}
```

### Real-Time Protocol Validation

```python
validation_results = {
    "safety_analysis": ["No incompatible mixing", "Pressure within limits"],
    "resource_check": ["All reagents available", "Apparatus compatible"],
    "feasibility": ["Estimated time: 2.5 hours", "Cost: $45.20"],
    "optimization": ["Predicted yield: 87%", "Confidence: 92%"]
}
```

### Intelligent Code Generation

```python
# Input: Template + User Configuration
# Output: Clean, optimized MechWolf protocol

"""
Generated Protocol Features:
✅ Proper variable naming and time management
✅ Comprehensive error handling
✅ Inline documentation and comments  
✅ Modular structure for easy modification
✅ Integration with MechWolf best practices
✅ Execution templates (dry run, real execution)
"""
```

## 🛠️ Development & Extension

### Adding Custom Templates

```python
from mechwolf.DataEntry.Phase3_UniversalProtocolBuilder.templates import ProtocolTemplate
from mechwolf.DataEntry.Phase3_UniversalProtocolBuilder.phases import ReactionPhase, RinsePhase

class MyCustomTemplate(ProtocolTemplate):
    def __init__(self):
        super().__init__(
            name="My Custom Synthesis",
            description="Custom protocol for my specific reaction",
            category="Synthesis"
        )
        
        # Define phases
        self.add_phase(ReactionPhase("Addition", reagents=["A", "B"]))
        self.add_phase(RinsePhase("Cleanup", solvent="THF"))
        
# Register template
template_manager.register_custom_template(MyCustomTemplate())
```

### Creating New Phase Types

```python
from mechwolf.DataEntry.Phase3_UniversalProtocolBuilder.phases import PhaseBase

class CrystallizationPhase(PhaseBase):
    def __init__(self, solvent, temperature, time):
        super().__init__("Crystallization")
        self.solvent = solvent
        self.temperature = temperature
        self.time = time
        
    def validate(self, apparatus, reagents):
        # Validation logic
        return True, []
        
    def generate_code(self, context):
        # Code generation logic
        return [
            f"P.add(temp_controller, start=current, temp='{self.temperature}')",
            f"P.add(pump, start=current, duration={self.time})"
        ]
```

## 🧪 Testing & Validation

### Built-in Test Suite

```bash
# Run comprehensive tests
python -m pytest tests/

# Test specific template
python -m pytest tests/test_peptide_synthesis.py

# Integration tests with real apparatus
python -m pytest tests/test_integration.py
```

### Protocol Simulation

```python
# Virtual execution for testing
protocol_code = builder.generate_protocol()
simulation_results = simulate_protocol(protocol_code, apparatus_config)

print(f"Estimated execution time: {simulation_results.total_time}")
print(f"Reagent consumption: {simulation_results.reagent_usage}")
print(f"Predicted yield: {simulation_results.yield_estimate}")
```

## 📊 Performance Metrics

- **Protocol Generation**: < 5 seconds for complex multi-step syntheses
- **Optimization**: < 30 seconds for multi-objective parameter optimization  
- **Validation**: Real-time safety and feasibility checking
- **Code Quality**: Generated protocols pass all MechWolf validation tests

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone repository
git clone https://github.com/MechWolf/MechWolf.git
cd MechWolf/mechwolf/DataEntry/Phase3_ProtocolDev

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

### Contribution Areas

- **New Templates**: Add templates for specific chemistry applications
- **Phase Types**: Create new phase types for specialized operations
- **Optimization**: Improve parameter optimization algorithms
- **GUI**: Enhance user interface and experience
- **Integration**: Better integration with external analysis tools

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MechWolf Team**: For the foundational flow chemistry platform
- **Research Community**: For feedback and real-world testing
- **Contributors**: Everyone who helped make this project possible

## 📞 Support & Documentation

- **Documentation**: [Full documentation and tutorials](docs/)
- **Examples**: [Example protocols and use cases](examples/)
- **Issues**: [Report bugs and request features](issues/)
- **Discussions**: [Community discussions and Q&A](discussions/)

---

## 🎯 Quick Links

| Resource | Description | Link |
|----------|-------------|------|
| 🚀 **Quick Start** | Get up and running in 5 minutes | [Quick Start Guide](docs/quickstart.md) |
| 📚 **Templates** | Browse available protocol templates | [Template Library](docs/templates.md) |
| 🎨 **GUI Guide** | Complete interface documentation | [GUI Documentation](docs/gui.md) |
| 🔧 **API Reference** | Developer API documentation | [API Docs](docs/api.md) |
| 💡 **Examples** | Real-world protocol examples | [Examples](examples/) |
| 🐛 **Troubleshooting** | Common issues and solutions | [Troubleshooting](docs/troubleshooting.md) |

---

**Ready to revolutionize your flow chemistry protocols?** 

Start with our [Quick Start Guide](docs/quickstart.md) and build your first intelligent protocol in minutes! 🧪✨