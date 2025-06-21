"""
Shared Components

Common components and utilities shared across all phases of the
MechWolf DataEntry system.

Modules:
    modern_ui_components: Tailwind CSS-styled ipywidgets
    validation_utilities: Common validation functions
    notebook_integration: Jupyter notebook helpers
    apparatus_factory: Enhanced apparatus factory (moved from FlowSetups_New)
"""

# Import key components for easy access
try:
    from .apparatus_factory import ApparatusFactory, create_apparatus_from_config
    from .validation_utilities import ValidationUtils
    from .notebook_integration import NotebookIntegration
except ImportError as e:
    # Allow partial imports if some dependencies are missing
    print(f"Warning: Some shared components not available: {e}")

__all__ = [
    'ApparatusFactory',
    'create_apparatus_from_config',
    'ValidationUtils', 
    'NotebookIntegration'
]