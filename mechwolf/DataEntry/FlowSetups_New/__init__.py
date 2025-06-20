"""
MechWolf FlowSetups - Modern Apparatus Configuration System

This package provides a comprehensive, modular system for configuring
MechWolf flow chemistry apparatus with modern UI components and robust
data management.

Usage:
    from mechwolf.DataEntry.FlowSetups_New import FlowSetupMain
    
    # Start the Flow Setup application
    app = FlowSetupMain("my_apparatus_config.json")
    app.start()

Modules:
    1_component_configurator: Component selection and configuration
    2_apparatus_builder: Connection building and validation  
    3_data_manager: JSON handling, validation, and export
    4_orchestrator: Main application orchestration and UI
"""

from .4_orchestrator.flow_setup_main import FlowSetupMain
from .1_component_configurator.component_selector import ComponentSelector
from .2_apparatus_builder.connection_gui import ConnectionGUI
from .3_data_manager.json_handler import JSONHandler
from .apparatus_factory import ApparatusFactory, create_apparatus_from_config, create_setup

__version__ = "2.0.0"
__author__ = "MechWolf FlowSetups Team"

# Main entry point
def create_flow_setup(json_file: str = "apparatus_config.json") -> FlowSetupMain:
    """
    Create a new Flow Setup application instance
    
    Args:
        json_file: Path to the JSON configuration file
    
    Returns:
        FlowSetupMain application instance
    """
    return FlowSetupMain(json_file)

# Convenience functions
def quick_start(json_file: str = "apparatus_config.json"):
    """
    Quick start function to launch the Flow Setup application
    
    Args:
        json_file: Path to the JSON configuration file
    """
    app = FlowSetupMain(json_file)
    app.start()
    return app

# Export main classes for direct access
__all__ = [
    'FlowSetupMain',
    'ComponentSelector', 
    'ConnectionGUI',
    'JSONHandler',
    'ApparatusFactory',
    'create_flow_setup',
    'create_apparatus_from_config',
    'create_setup',
    'quick_start'
]