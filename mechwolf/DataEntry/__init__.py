"""
MechWolf DataEntry Package

This package contains various data entry tools and flow setup utilities
for the MechWolf flow chemistry automation framework.

Available modules:
    FlowSetups: Legacy flow setup system
    FlowSetups_New: Modern modular flow setup system with GUI
    ProtocolDev: Protocol development tools
    ReagentUI: Reagent management interface
"""

# Import key modules for easier access
try:
    from . import FlowSetups_New
except ImportError:
    # FlowSetups_New may not be available if dependencies are missing
    pass

try:
    from . import FlowSetups
except ImportError:
    # FlowSetups may not be available
    pass

try:
    from . import ProtocolDev
except ImportError:
    # ProtocolDev may not be available
    pass

__version__ = "2.0.0"
__author__ = "Prashant Kumar"