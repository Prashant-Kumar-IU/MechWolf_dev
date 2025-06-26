# 📚 Phase1_ReagentEntry Usage Examples

This document provides comprehensive examples of how to use the refactored modular reagent entry system.

## 🚀 Quick Start (Backward Compatible)

### Basic Usage - Same as Original
```python
# This works exactly like the original interface
from mechwolf.DataEntry.Phase1_ReagentEntry import launch_gui

# Launch interface (same as before)
gui = launch_gui(experiment_manager)

# Get current data (same as before)
data = gui.get_data()
```

## 🏗️ Advanced Usage - New Modular Features

### Working with Services Directly
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.core import ReagentService, ExperimentService
from mechwolf.DataEntry.Phase1_ReagentEntry.core.data_adapter import ReagentDataAdapter

# Create services
data_adapter = ReagentDataAdapter(experiment_manager)
reagent_service = ReagentService(data_adapter)
experiment_service = ExperimentService(data_adapter)

# Search PubChem
compounds, errors = reagent_service.search_pubchem("ethanol", "name")
if not errors:
    print(f"Found {len(compounds)} compounds")
```

### Working with Models
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.core.models import ReagentModel, ExperimentModel

# Create a reagent manually
reagent = ReagentModel(
    name="Ethanol",
    molecular_weight=46.07,
    equivalents=2.0,
    position=1,
    smiles="CCO",
    reagent_type="liquid",
    density=0.789
)

# Validate reagent
if reagent.is_valid:
    print("✅ Reagent is valid")
    print(f"Canonical SMILES: {reagent.smiles}")
else:
    print("❌ Validation errors:", reagent.errors)

# Convert to old format for compatibility
old_format = reagent.to_old_format()
print(old_format)
```

### Creating Custom Interfaces
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.ui import (
    create_solid_reagents_tab, 
    ReagentForm,
    ButtonFactory
)
from mechwolf.DataEntry.Phase1_ReagentEntry.core import ReagentService

# Create individual tabs
reagent_service = ReagentService(data_adapter)
solid_tab = create_solid_reagents_tab(reagent_service)

# Create custom forms
custom_form = ReagentForm(
    reagent_type="liquid",
    on_save=my_custom_save_handler
)

# Create custom buttons
my_button = ButtonFactory.create_success("Custom Action")
```

## 🧪 Chemistry Utilities

### SMILES Validation and Processing
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.utils import (
    validate_smiles,
    canonical_smiles,
    mol_weight_from_smiles,
    normalize_chemical_data
)

# Validate SMILES
smiles = "CCO"
if validate_smiles(smiles):
    print("✅ Valid SMILES")
    
    # Get canonical form
    canonical = canonical_smiles(smiles)
    print(f"Canonical: {canonical}")
    
    # Calculate molecular weight
    mw = mol_weight_from_smiles(smiles)
    print(f"Molecular weight: {mw} g/mol")

# Auto-fill chemical data
compound_data = {
    'name': 'Ethanol',
    'smiles': 'CCO'
}

normalized = normalize_chemical_data(compound_data)
print("Auto-filled data:", normalized)
```

### Data Validation
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.utils import (
    validate_reagent_data,
    validate_experiment_data
)

# Validate individual reagent
reagent_data = {
    "name": "Ethanol",
    "molecular weight (in g/mol)": 46.07,
    "eq": 2.0,
    "syringe": 1,
    "density (in g/mL)": 0.789
}

errors = validate_reagent_data(reagent_data, "liquid")
if not errors:
    print("✅ Reagent data is valid")
else:
    print("❌ Validation errors:", errors)
```

## 📊 Experiment Management

### Working with Complete Experiments
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.core import ExperimentService

experiment_service = ExperimentService(data_adapter)

# Get current experiment
experiment = experiment_service.get_current_experiment()

print(f"Total reagents: {experiment.total_reagent_count}")
print(f"Limiting reagent: {experiment.limiting_reagent.name if experiment.limiting_reagent else 'None'}")

# Validate completeness
is_complete, issues = experiment_service.validate_experiment_completeness()
if is_complete:
    print("✅ Experiment is ready for execution")
else:
    print("❌ Issues to resolve:")
    for issue in issues:
        print(f"  - {issue}")

# Calculate stoichiometry
stoich_data, errors = experiment_service.calculate_stoichiometry()
if not errors:
    print("📊 Stoichiometry calculated successfully")
    print(f"Limiting reagent: {stoich_data['limiting_reagent']}")
    print(f"Total volume needed: {sum(stoich_data['volumes'].values()):.2f} mL")
```

### Batch Processing Reagents
```python
# Process multiple reagents
reagents_to_add = [
    {
        'name': 'Benzene',
        'molecular_weight': 78.11,
        'equivalents': 1.0,
        'position': 1,
        'smiles': 'c1ccccc1',
        'reagent_type': 'liquid',
        'density': 0.876
    },
    {
        'name': 'Sodium chloride',
        'molecular_weight': 58.44,
        'equivalents': 1.5,
        'position': 2,
        'reagent_type': 'solid'
    }
]

for reagent_data in reagents_to_add:
    reagent_type = reagent_data.pop('reagent_type')
    reagent, errors = reagent_service.create_reagent_from_form_data(reagent_data, reagent_type)
    
    if not errors:
        success, save_errors = reagent_service.save_reagent(reagent)
        if success:
            print(f"✅ Added {reagent.name}")
        else:
            print(f"❌ Failed to save {reagent.name}: {save_errors}")
    else:
        print(f"❌ Invalid reagent data: {errors}")
```

## 🔧 Customization Examples

### Custom Tab Creation
```python
import ipywidgets as widgets
from mechwolf.DataEntry.Phase1_ReagentEntry.ui.components.base import SectionHeader, MessageArea

class CustomAnalysisTab:
    """Custom tab for analysis features"""
    
    def __init__(self, experiment_service):
        self.experiment_service = experiment_service
        self.message_area = MessageArea()
        self._create_tab()
    
    def _create_tab(self):
        header = SectionHeader.create(
            "📈 Analysis",
            description="Custom analysis features"
        )
        
        analysis_button = widgets.Button(description="Run Analysis")
        analysis_button.on_click(self._run_analysis)
        
        self.widget = widgets.VBox([
            header,
            self.message_area.widget,
            analysis_button
        ])
    
    def _run_analysis(self, button):
        try:
            experiment = self.experiment_service.get_current_experiment()
            # Custom analysis logic here
            self.message_area.show_success("Analysis completed!")
        except Exception as e:
            self.message_area.show_error(f"Analysis failed: {e}")
    
    def get_widget(self):
        return self.widget

# Add to main interface
custom_tab = CustomAnalysisTab(experiment_service)
```

### Custom Form Validation
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.ui.components.forms import ReagentForm

class CustomReagentForm(ReagentForm):
    """Extended reagent form with custom validation"""
    
    def validate_custom_rules(self, form_data):
        """Add custom validation rules"""
        errors = []
        
        # Custom rule: MW must be between 10 and 1000
        mw = form_data.get('molecular_weight', 0)
        if mw < 10 or mw > 1000:
            errors.append("Molecular weight must be between 10 and 1000 g/mol")
        
        # Custom rule: Name must not contain numbers
        name = form_data.get('name', '')
        if any(c.isdigit() for c in name):
            errors.append("Reagent name should not contain numbers")
        
        return errors
```

## 🐛 Error Handling and Debugging

### Graceful Error Handling
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.utils.imports import safe_import

# Safe imports with fallbacks
rdkit_mol = safe_import([
    'rdkit.Chem.MolFromSmiles',
    'fallback.dummy_mol_function'
], fallback_factory=lambda: lambda smiles: None)

# Use the imported function safely
mol = rdkit_mol("CCO")
```

### Debugging Tools
```python
# Enable debug mode for detailed error reporting
import logging
logging.basicConfig(level=logging.DEBUG)

# Check system capabilities
from mechwolf.DataEntry.Phase1_ReagentEntry.utils import is_rdkit_available

print(f"RDKit available: {is_rdkit_available()}")

# Validate system state
def check_system_health():
    """Check if all components are working"""
    checks = {
        'RDKit': is_rdkit_available(),
        'Data Adapter': data_adapter is not None,
        'Services': reagent_service is not None
    }
    
    for component, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}: {'OK' if status else 'NOT AVAILABLE'}")

check_system_health()
```

## 🔄 Migration from Original Code

### Old Code → New Code Mapping
```python
# OLD WAY (still works)
from mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.reagent_ui_restored import ReagentUI
gui = ReagentUI(experiment_manager)

# NEW WAY (recommended)
from mechwolf.DataEntry.Phase1_ReagentEntry import ReagentEntryInterface
interface = ReagentEntryInterface(experiment_manager)

# Both provide the same functionality, but new way offers:
# - Better error handling
# - Modular components
# - Extensibility
# - Better testing support
```

### Accessing New Features
```python
# Access individual services (not available in old version)
reagent_service = interface.reagent_service
experiment_service = interface.experiment_service

# Access individual tabs (for custom interfaces)
solid_tab = interface.solid_tab
liquid_tab = interface.liquid_tab

# Use new model classes
from mechwolf.DataEntry.Phase1_ReagentEntry.core.models import ReagentModel
reagent = ReagentModel.from_pubchem_data(compound_data, "liquid")
```

## 🎯 Best Practices

### 1. **Use Services for Business Logic**
```python
# ✅ Good - use services
reagent, errors = reagent_service.create_reagent_from_form_data(data, "solid")

# ❌ Avoid - direct data manipulation
# Don't manipulate data_adapter directly unless necessary
```

### 2. **Validate Early and Often**
```python
# ✅ Good - validate before processing
if reagent.is_valid:
    success, errors = reagent_service.save_reagent(reagent)
else:
    print("Fix errors first:", reagent.errors)
```

### 3. **Use Models for Type Safety**
```python
# ✅ Good - use models
reagent = ReagentModel(name="Ethanol", molecular_weight=46.07, ...)

# ❌ Avoid - raw dictionaries when models are available
# reagent_dict = {"name": "Ethanol", "molecular_weight": 46.07}
```

### 4. **Handle Errors Gracefully**
```python
# ✅ Good - handle both success and error cases
success, errors = reagent_service.save_reagent(reagent)
if success:
    print("✅ Saved successfully")
else:
    print("❌ Errors:", errors)
```

This modular system provides much more flexibility while maintaining full backward compatibility! 🚀