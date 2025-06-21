"""
Phase2_ApparatusBuilder - Integrated apparatus and pump configuration

This module provides a unified interface for configuring both pumps and apparatus
components, eliminating the need for separate pump code generation steps.

Key Innovation:
    - Integrated pump configuration with apparatus building
    - Auto-generation of pump initialization code
    - Visual apparatus building with connection management
    - Real-time validation and error checking
    - Seamless integration with experimental metadata

Main Components:
    apparatus_gui: Main integrated interface
    pump_configurator: Pump configuration and code generation
    component_configurator: Component selection and configuration  
    connection_builder: Visual connection management
    apparatus_validator: Real-time validation
    apparatus_visualizer: Network diagram visualization
"""

try:
    from .apparatus_gui import ApparatusBuilderGUI
except ImportError as e:
    # Handle missing dependencies gracefully
    class ApparatusBuilderGUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"Warning: ApparatusBuilderGUI dependencies not available: {e}")
        
        def display(self):
            print("ApparatusBuilderGUI not available - install required dependencies (ipywidgets, etc.)")
            
        def get_configured_pumps(self):
            return {}
            
        def get_apparatus(self):
            return None
            
    print(f"Warning: ApparatusBuilderGUI not fully available: {e}")

# Convenience function for launching GUI
def launch_gui(experiment_manager):
    """
    Launch the integrated apparatus and pump builder GUI
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        ApparatusBuilderGUI instance
    """
    gui = ApparatusBuilderGUI(experiment_manager)
    gui.display()
    return gui

__all__ = ['ApparatusBuilderGUI', 'launch_gui']