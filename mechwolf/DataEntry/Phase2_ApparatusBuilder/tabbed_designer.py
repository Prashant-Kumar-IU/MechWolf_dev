"""
Modular Tabbed Apparatus Designer for MechWolf Development

This is the new modular version that imports from the restructured modules.
Maintains backward compatibility with the original API.
"""

# Re-export all the main classes for backward compatibility
from .models import ApparatusComponent, ApparatusConnection
from .registry import ComponentRegistry
from .core import TabbedApparatusDesigner

# Re-export the factory function
def create_tabbed_apparatus_designer(experiment_manager=None):
    """Create and return a TabbedApparatusDesigner instance."""
    return TabbedApparatusDesigner(experiment_manager)

# Backward compatibility exports
__all__ = [
    'TabbedApparatusDesigner',
    'ComponentRegistry', 
    'ApparatusComponent',
    'ApparatusConnection',
    'create_tabbed_apparatus_designer'
]