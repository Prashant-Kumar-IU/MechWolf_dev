<h1 align ="center">
<img src='https://github.com/MechWolf/MechWolf/raw/master/logo/head10x.png' width="150">
<br>
MechWolf v2.0.0
</h1>

<div align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="Python version" /></a>
<a href="https://github.com/Prashant-Kumar-IU/MechWolf_dev/releases"><img src="https://img.shields.io/badge/version-2.0.0-brightgreen.svg" alt="Version" /></a>
<a href="https://github.com/Prashant-Kumar-IU/MechWolf_dev/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="GPLv3 license" /></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</div>
<br>

## 🚀 What's New in v2.0.0

- **Enhanced Flow Setups Module**: Complete redesign with modern UI and extensible architecture
- **Interactive GUI**: Advanced Jupyter widgets for apparatus configuration
- **Configuration Persistence**: Save and reuse experimental setups
- **Extensible Framework**: Easy addition of new flow chemistry setups
- **Improved Documentation**: Comprehensive guides for users and developers
- **Better Error Handling**: Enhanced validation and user feedback

## 📖 Overview

MechWolf is a Python framework for automating continuous flow processes.
It was developed as a collaboration between computer scientists, chemists, and complete novices to be used by anyone wanting to do better, faster, more reproducible flow-based science.
Features include:

- **Enhanced Flow Setups Module**: Interactive GUI for creating standardized apparatus configurations
- **Configuration Persistence**: Save and reuse experimental setups as JSON files
- **Extensible Architecture**: Easily add new flow chemistry setup types
- **Modern UI**: Material Design-inspired interface with progress tracking
- Natural language description, analysis, and visualization of continuous flow networks
- Automated execution of protocols
- Full user extensibility
- Smart default settings, designed by scientists for scientists
- Extensive checking to prevent potentially costly and dangerous errors before runtime
- Natural language parsing of times and quantities
- Thorough documentation and tutorials

## 🛠️ Installation

### From GitHub (Recommended for v2.0.0)

```bash
# Clone the repository
git clone https://github.com/Prashant-Kumar-IU/MechWolf_dev.git
cd MechWolf_dev

# Install with all dependencies
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Quick Install (Production)

```bash
# Install directly from GitHub
pip install git+https://github.com/Prashant-Kumar-IU/MechWolf_dev.git

# Or install with chemistry extras (includes RDKit)
pip install "git+https://github.com/Prashant-Kumar-IU/MechWolf_dev.git[chemistry]"
```

### Legacy Installation (Original MechWolf)

```bash
# For the original version from conda-forge
conda install -c conda-forge mechwolf
```

## 🔬 Enhanced Flow Setups Module

The new Flow Setups module provides an intuitive interface for creating standardized flow chemistry apparatus:

```python
import mechwolf as mw
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Create pumps
pump1 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
pump2 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")

# Create apparatus with interactive GUI
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])

# Available setup types:
FlowSetupFactory.print_available_setups()
```

## 🎯 Key Features

## What can MechWolf do?

A lot.
Let's say you're trying to automate the production of [acetaminophen](https://en.wikipedia.org/wiki/Paracetamol), a popular pain reliever and fever reducer.
The reaction involves combining two chemicals, 4-aminophenol and acetic anhydride.
The basic level of organization in MechWolf are individual components, such as the vessels and pumps.

First, we define our components and create an **`Apparatus`** object to hold them:

```python
import mechwolf as mw

# define the vessels
aminophenol = mw.Vessel("15 mL 4-aminophenol")
acetic_anhydride = mw.Vessel("15 mL acetic anhydride")
acetaminophen = mw.Vessel("acetaminophen")

# define the pumps
pump_1 = mw.Pump()
pump_2 = mw.Pump()

# define the mixer
mixer = mw.TMixer()

# same tube specs for all tubes
tube = mw.Tube(length="1 m", ID="1/16 in", OD="2/16 in", material="PVC")

# create the Apparatus object
A = mw.Apparatus()
```

Next, we define the connectivity of the **`Apparatus`** with **`add()`**. **`add()`** expects three arguments, `from_component`, `to_component`, and `tube` (in that order). First, we connect `aminophenol` to `pump_1` via `tube`:

```python
A.add(from_component=aminophenol, to_component=pump_1, tube=tube)
```

Note that the keyword arguments are optional:

```python
A.add(acetic_anhydride, pump_2, tube)
```

Since `from_component` is a list, both `pump_1` and `pump_2` will be connected to `mixer`.

```python
A.add([pump_1, pump_2], mixer, tube)
```

Finally, connect `mixer` to the output vessel, `acetaminophen`:

```python
A.add(mixer, acetaminophen, tube)
```

Then we define a **`Protocol`** and run it:

```python
# create the Protocol object
P = mw.Protocol(A, name="acetaminophen synthesis")
P.add([pump_1, pump_2], duration="15 mins", rate="1 mL/min")

# execute the Protocol
P.execute()
```

That's it! You can do this and a whole lot more with MechWolf.

## 📚 Documentation

### Flow Setups Module (v2.0.0)
- **[User Guide](mechwolf/DataEntry/FlowSetups/docs/USER_GUIDE.md)** - Complete usage instructions
- **[Developer Guide](mechwolf/DataEntry/FlowSetups/docs/DEVELOPER_GUIDE.md)** - Architecture and code flow
- **[API Reference](mechwolf/DataEntry/FlowSetups/docs/API_REFERENCE.md)** - Detailed API documentation
- **[Contributing Guide](mechwolf/DataEntry/FlowSetups/docs/CONTRIBUTING.md)** - How to extend the system

### General Documentation
- **[Installation Guide](MechWolf_Dev_Experimental_Installation_Guide.html)** - Detailed installation instructions
- **[Examples](examples/)** - Jupyter notebooks with practical examples
- **[Templates](jupyter%20notebook%20templates/)** - Template notebooks for common setups

## 🆕 What's New in v2.0.0

### Enhanced Flow Setups Module
The Flow Setups module has been completely redesigned with:
- **Modern UI** with Material Design inspiration
- **Interactive widgets** for easy apparatus configuration
- **Configuration persistence** to save and reuse setups
- **Extensible architecture** for easy addition of new setup types
- **Comprehensive validation** and error handling

### Improved Developer Experience
- Clean, modular codebase with 70% reduction in duplicate code
- Comprehensive documentation and examples
- Type hints throughout the codebase
- Better error messages and debugging support

## 🚀 Quick Examples

### Traditional MechWolf Usage
```python
import mechwolf as mw

# Create components
pump = mw.Pump()
vessel = mw.Vessel("reagent")
# ... continue with traditional apparatus building
```

### New Flow Setups Module (Recommended)
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Create pumps
pump1 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
pump2 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")

# Create apparatus interactively
apparatus = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump1, pump2])
```

## 🤝 Contributing

We welcome contributions! Please see:
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - General contribution guidelines
- **[Flow Setups Contributing Guide](mechwolf/DataEntry/FlowSetups/docs/CONTRIBUTING.md)** - Specific to Flow Setups module

## 👥 Contributors

### v2.0.0 Enhancements
- **Prashant Kumar** ([@Prashant-Kumar-IU](https://github.com/Prashant-Kumar-IU)) - Flow Setups redesign and development
- **Dr. Nicola Pohl** ([@NLPohl](https://github.com/NLPohl)) - Project supervision and guidance

### Original MechWolf Framework
- **Benjamin Lee** - Original framework development
- **Alex Mijalis** - Original framework development

## 📄 License

[GPLv3](LICENSE) [(summary)](https://choosealicense.com/licenses/gpl-3.0/).

## 📖 Citation

```bibtex
@software{mechwolf2024,
  title={MechWolf: Enhanced Flow Chemistry Automation Platform},
  author={Kumar, Prashant and Pohl, Nicola and Lee, Benjamin and Mijalis, Alex},
  version={2.0.0},
  year={2025},
  url={https://github.com/Prashant-Kumar-IU/MechWolf_dev}
}
```

## 🐛 Issues and Support

- **Bug Reports**: [GitHub Issues](https://github.com/Prashant-Kumar-IU/MechWolf_dev/issues)
- **Questions**: Start with the documentation above
- **Email**: pprashan@iu.edu
