"""
Phase1_ReagentEntry - Reagent Entry Interface

This module provides the original ReagentUI interface restored with 
modern experimental metadata backend integration.

Main Components:
    ReagentUI: Main tabbed interface for reagent entry and management
    PubChemService: PubChem API integration for compound lookup
    StructureVisualization: Molecular structure visualization
"""

try:
    # Import core components
    from .reagent_ui_restored import ReagentUI
    from .pubchem_service import PubChemService
    from .structure_visualization import StructureVisualization
    from .ui_components import UIComponents
    from .reagent_utils import validate_reagent_data, validate_smiles, is_rdkit_available
    
    # Create alias for backward compatibility
    ReagentEntryGUI = ReagentUI
    _import_error = None
    
except ImportError as e:
    # Graceful fallback for missing dependencies
    _import_error = e
    
    class ReagentUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"⚠️ ReagentUI dependencies not available: {_import_error}")
        
        def display(self):
            print("❌ ReagentUI not available - install required dependencies")
    
    ReagentEntryGUI = ReagentUI
    PubChemService = None
    StructureVisualization = None 
    UIComponents = None
    validate_reagent_data = None
    validate_smiles = None
    is_rdkit_available = None

def launch_gui(experiment_manager):
    """
    Launch the ReagentUI interface for an experiment
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        ReagentUI instance
    """
    gui = ReagentUI(experiment_manager)
    gui.display()
    return gui

__all__ = [
    'ReagentUI', 
    'ReagentEntryGUI', 
    'launch_gui', 
    'PubChemService', 
    'StructureVisualization', 
    'UIComponents',
    'validate_reagent_data',
    'validate_smiles', 
    'is_rdkit_available'
]