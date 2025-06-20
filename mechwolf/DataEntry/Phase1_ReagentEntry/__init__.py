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

from .reagent_gui import ReagentEntryGUI

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