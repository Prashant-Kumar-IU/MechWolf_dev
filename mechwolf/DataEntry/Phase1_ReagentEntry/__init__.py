"""
Phase1_ReagentEntry - Reagent Entry Interface

This module provides a modern, modular reagent entry interface with 
experimental metadata backend integration. The original monolithic
interface has been refactored into focused, maintainable components.

## Architecture Overview

### Core Layer (Business Logic)
- `core.models`: Data models (ReagentModel, ExperimentModel)
- `core.services`: Business logic services (ReagentService, ExperimentService)
- `core.data_adapter`: Bridge to experimental metadata system

### UI Layer (User Interface)
- `ui.main_interface`: Main interface coordinator
- `ui.tabs.*`: Individual tab implementations (solid, liquid, search, display, final)
- `ui.components.*`: Reusable UI components (forms, base components)

### External Layer (Third-party Services)
- `external.pubchem`: PubChem API integration
- `external.visualization`: Chemical structure rendering

### Utils Layer (Utilities)
- `utils.imports`: Centralized import handling
- `utils.validation`: Data validation functions  
- `utils.chemistry`: Chemistry-specific utilities

## Usage Examples

### Basic Usage (Backward Compatible)
```python
from mechwolf.DataEntry.Phase1_ReagentEntry import launch_gui

# Launch with experiment manager
gui = launch_gui(experiment_manager)
```

### Advanced Usage (New Modular Interface)
```python
from mechwolf.DataEntry.Phase1_ReagentEntry import ReagentEntryInterface
from mechwolf.DataEntry.Phase1_ReagentEntry.core.services import ReagentService

# Create interface
interface = ReagentEntryInterface(experiment_manager)

# Access services directly
reagent_service = interface.reagent_service
experiment_service = interface.experiment_service

# Display interface
interface.display()
```

### Working with Models
```python
from mechwolf.DataEntry.Phase1_ReagentEntry.core.models import ReagentModel

# Create reagent from form data
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
    print("Reagent is valid")
else:
    print("Errors:", reagent.errors)
```

## Migration from Original Code

The original 1,427-line monolithic file has been broken down into:
- 5 focused tab modules (~250-300 lines each)
- Reusable component library
- Clean service layer for business logic
- Centralized utilities with no duplication

This provides:
- ✅ Better maintainability 
- ✅ Easier testing
- ✅ Clear separation of concerns
- ✅ Reusable components
- ✅ Backward compatibility
"""

# Backward compatibility imports - maintain original API
try:
    # Import main interface components
    from .ui.main_interface import ReagentEntryInterface, ReagentUI, launch_gui
    
    # Import core services for advanced usage
    from .core.services import ReagentService, ExperimentService
    from .core.models import ReagentModel, ExperimentModel
    from .core.data_adapter import ReagentDataAdapter
    
    # Import external services
    from .external.pubchem import PubChemService
    from .external.visualization import StructureVisualization
    
    # Import utilities
    from .utils.validation import validate_reagent_data, validate_smiles
    from .utils.chemistry import is_rdkit_available, safe_mol_from_smiles
    
    # Create backward compatibility aliases
    ReagentEntryGUI = ReagentUI  # Original alias
    
    # Export the same functions as the original OldCode/__init__.py
    def create_reagent_ui(experiment_manager):
        """Create ReagentUI instance - backward compatibility function."""
        return ReagentUI(experiment_manager)
    
except ImportError as e:
    # Graceful fallback for missing dependencies (same as original)
    print(f"⚠️ Some ReagentUI components not available: {e}")
    print("This may be due to missing dependencies (ipywidgets, rdkit, etc.)")
    
    class ReagentUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"⚠️ ReagentUI dependencies not available: {e}")
        
        def display(self):
            print("❌ ReagentUI not available - install required dependencies")
            print("Required: ipywidgets, rdkit-pypi, requests")
    
    # Set fallback aliases
    ReagentEntryGUI = ReagentUI
    ReagentEntryInterface = ReagentUI
    launch_gui = lambda em: ReagentUI(em)
    
    # Set fallback services
    PubChemService = None
    StructureVisualization = None
    ReagentService = None
    ExperimentService = None
    ReagentDataAdapter = None


# Public API - maintains backward compatibility while exposing new features
__all__ = [
    # Main interfaces (backward compatible)
    'ReagentUI',
    'ReagentEntryGUI', 
    'ReagentEntryInterface',
    'launch_gui',
    
    # Core services (new modular features)
    'ReagentService',
    'ExperimentService', 
    'ReagentDataAdapter',
    
    # Models (new)
    'ReagentModel',
    'ExperimentModel',
    
    # External services
    'PubChemService',
    'StructureVisualization',
    
    # Utilities (backward compatible)
    'validate_reagent_data',
    'validate_smiles',
    'is_rdkit_available',
    'safe_mol_from_smiles'
]


# Version info
__version__ = "2.0.0"
__author__ = "MechWolf Team"
__description__ = "Modular reagent entry interface with experimental metadata integration"

# Architecture summary for developers
ARCHITECTURE_SUMMARY = {
    "total_files": 17,  # New modular structure
    "original_monolith": "1,427 lines -> 5 focused modules (~250-300 lines each)",
    "layers": {
        "core": "Business logic, models, services",
        "ui": "User interface components and tabs", 
        "external": "Third-party service integrations",
        "utils": "Shared utilities and helpers"
    },
    "improvements": [
        "Eliminated code duplication",
        "Centralized import handling", 
        "Clear separation of concerns",
        "Reusable components",
        "Better error handling",
        "Comprehensive validation"
    ]
}