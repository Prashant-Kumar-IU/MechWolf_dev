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
    from .reagent_gui import ReagentEntryGUI
except ImportError as e:
    # Handle missing dependencies gracefully
    class ReagentEntryGUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"Warning: ReagentEntryGUI dependencies not available: {e}")
        
        def display(self):
            print("ReagentEntryGUI not available - install required dependencies (ipywidgets, etc.)")
            
    print(f"Warning: ReagentEntryGUI not fully available: {e}")

# Convenience function for launching GUI
def launch_gui(experiment_manager):
    """
    Launch the reagent entry GUI for an experiment
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        ReagentEntryGUI instance
    """
    gui = ReagentEntryGUI(experiment_manager)
    gui.display()
    return gui

__all__ = ['ReagentEntryGUI', 'launch_gui']