"""
Phase1_ReagentEntry - Modern reagent entry interface

This module provides a modern reagent entry interface that integrates with 
the unified experimental metadata system, replacing the legacy ReagentUI.

Main Components:
    reagent_gui: Main interface for reagent entry and management
    reagent_validator: Chemistry validation logic
    pubchem_integration: PubChem API integration for compound lookup
    structure_visualization: Molecular structure visualization
"""

try:
    # Import the restored original ReagentUI
    from .reagent_ui_restored import ReagentUI
    from .data_adapter import ReagentDataAdapter
    from .pubchem_service import PubChemService
    from .structure_visualization import StructureVisualization
    from .ui_components import UIComponents
    from .reagent_utils import validate_reagent_data, validate_smiles, is_rdkit_available
    
    # Create an alias for backward compatibility
    ReagentEntryGUI = ReagentUI
    
except ImportError as e:
    # Handle missing dependencies gracefully
    class ReagentUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"Warning: ReagentUI dependencies not available: {e}")
        
        def display(self):
            print("ReagentUI not available - install required dependencies (ipywidgets, etc.)")
    
    # Create alias
    ReagentEntryGUI = ReagentUI
            
    print(f"Warning: ReagentUI not fully available: {e}")
    
    # Create dummy classes for missing imports
    PubChemService = None
    StructureVisualization = None 
    UIComponents = None
    ReagentDataAdapter = None

# Convenience function for launching GUI
def launch_gui(experiment_manager):
    """
    Launch the restored original ReagentUI for an experiment
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        ReagentUI instance
    """
    gui = ReagentUI(experiment_manager)
    gui.display()
    return gui

__all__ = ['ReagentUI', 'ReagentEntryGUI', 'launch_gui', 'ReagentDataAdapter', 'PubChemService', 'StructureVisualization', 'UIComponents']