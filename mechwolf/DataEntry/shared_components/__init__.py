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
# Import them individually to provide better error messages

ValidationUtils = None
try:
    from .validation_utilities import ValidationUtils
except ImportError as e:
    print(f"Warning: ValidationUtils not available: {e}")

NotebookIntegration = None
try:
    from .notebook_integration import NotebookIntegration
except ImportError as e:
    print(f"Warning: NotebookIntegration not available: {e}")

ApparatusFactory = None
create_apparatus_from_config = None
try:
    from .apparatus_factory import ApparatusFactory, create_apparatus_from_config
except ImportError as e:
    print(f"Warning: ApparatusFactory not available: {e}")

# Only include successfully imported items in __all__
__all__ = []
if ValidationUtils is not None:
    __all__.append('ValidationUtils')
if NotebookIntegration is not None:
    __all__.append('NotebookIntegration')
if ApparatusFactory is not None:
    __all__.extend(['ApparatusFactory', 'create_apparatus_from_config'])