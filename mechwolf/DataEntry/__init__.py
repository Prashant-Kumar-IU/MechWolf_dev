"""
MechWolf DataEntry Package v3.0

Modernized data entry system for MechWolf flow chemistry automation.

🚀 NEW ARCHITECTURE (v3.0):
    experimental_metadata: Unified experimental data management (eliminates redundancy)
    Phase1_ReagentEntry: Modern reagent entry with PubChem integration
    Phase2_ApparatusBuilder: Integrated apparatus & pump configuration (replaces separate notebooks)
    Phase3_ProtocolDev: Protocol development with MechWolf core validation
    shared_components: Common utilities and enhanced apparatus factory
    utilities: Essential tools (SerialPortViewer, TLCInputForm, GetNotebookName, etc.)

✨ KEY IMPROVEMENTS:
    ✅ Zero redundancy - single experimental metadata system
    ✅ Integrated pump configuration - no separate pump notebooks needed
    ✅ Modern phase-based workflow with guided interfaces
    ✅ Real-time validation and error checking
    ✅ Enhanced Jupyter notebook integration
    ✅ Complete experiment tracking and reproducibility

📖 USAGE:
    See ENHANCED_NOTEBOOK_TEMPLATE.py for complete workflow example
"""

# Import new phase modules
try:
    from . import experimental_metadata
    from . import Phase1_ReagentEntry
    from . import Phase2_ApparatusBuilder  
    from . import Phase3_ProtocolDev
    from . import shared_components
except ImportError as e:
    print(f"Warning: Some DataEntry modules not available: {e}")

# Import utilities for backward compatibility
try:
    from .utilities.GetNotebookName import get_notebook_json_name
    from .utilities.SerialPortViewer import SerialPortViewer
    from .utilities.TLCInputForm import TLCInputForm
except ImportError:
    # Utilities may not be available in all environments
    pass

# Convenience imports for easy access
try:
    from .experimental_metadata import ExperimentalMetadataManager
    from .shared_components import ApparatusFactory
except ImportError:
    pass

__version__ = "3.0.0"
__author__ = "Prashant Kumar"

# Modern workflow convenience functions
def create_experiment(data_file: str, experiment_name: str):
    """
    Create a new experiment using the modern unified system
    
    Args:
        data_file: JSON file path for experiment data
        experiment_name: Name for the experiment
        
    Returns:
        ExperimentalMetadataManager instance
    """
    from .experimental_metadata import ExperimentalMetadataManager
    return ExperimentalMetadataManager(data_file, experiment_name)

def launch_reagent_entry(experiment):
    """Launch Phase 1: Reagent Entry GUI"""
    from . import Phase1_ReagentEntry
    return Phase1_ReagentEntry.launch_gui(experiment)

def launch_apparatus_builder(experiment):
    """Launch Phase 2: Apparatus & Pump Builder GUI"""
    from . import Phase2_ApparatusBuilder
    return Phase2_ApparatusBuilder.launch_gui(experiment)

def launch_protocol_dev(experiment, protocol=None, pumps=None):
    """Launch Phase 3: Protocol Development GUI"""
    from . import Phase3_ProtocolDev
    return Phase3_ProtocolDev.launch_gui(experiment, protocol, pumps)

# Export main interfaces
__all__ = [
    'experimental_metadata',
    'Phase1_ReagentEntry', 
    'Phase2_ApparatusBuilder',
    'Phase3_ProtocolDev',
    'shared_components',
    'ExperimentalMetadataManager',
    'ApparatusFactory',
    'create_experiment',
    'launch_reagent_entry',
    'launch_apparatus_builder', 
    'launch_protocol_dev'
]