"""
MechWolf Flow Setups Module

This module provides a modular and extensible system for creating different
types of flow chemistry apparatus configurations. It supports various
combinations of syringes, reaction coils, and mixers.

Quick Start:
-----------
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

# Create pumps
pump1 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM1")
pump2 = HarvardSyringePump("3 mL", "10 mm", serial_port="COM2")

# Create apparatus using factory
apparatus = FlowSetupFactory.create_setup(
    'two_syringes_1r_1m', 
    [pump1, pump2], 
    data_file='my_setup.json'
)
```

Available Setup Types:
---------------------
- two_syringes_1r_1m: Two syringes with 1 reaction coil and 1 mixer
- three_syringes_1r_1m: Three syringes with 1 reaction coil and 1 mixer  
- three_syringes_2r_2m: Three syringes with 2 reaction coils and 2 mixers
- flexible_setup: Variable number of vessels with flexible configuration

For more information, use FlowSetupFactory.print_available_setups()
"""

# Main API - Factory pattern
from .factory import FlowSetupFactory

# Configuration system
from .config_templates import (
    FlowSetupConfig,
    FLOW_CONFIGS,
    get_config,
    list_available_configs,
    add_custom_config
)

# Base classes for extending the system
from .base_classes import (
    BaseComponentApp,
    BaseApparatusCreator
)

# Utility modules
from .data_manager import DataManager
from .widget_manager import WidgetManager
from .error_handler import ErrorHandler, ValidationError
from .FlowSetupUtils import (
    parse_tube_dimension,
    parse_numeric_foot,
    check_required_fields,
    validate_required_fields_with_rmv
)

# Individual setup modules (for advanced users)
from .two_syringes_setup import (
    TwoSyringesComponentApp,
    TwoSyringesApparatusCreator
)
from .three_syringes_1r1m_setup import (
    ThreeSyringes1R1MComponentApp,
    ThreeSyringes1R1MApparatusCreator
)
from .three_syringes_2r2m_setup import (
    ThreeSyringes2R2MComponentApp,
    ThreeSyringes2R2MApparatusCreator
)
from .flexible_setup import (
    FlexibleSetupComponentApp,
    FlexibleSetupApparatusCreator
)

# Version info
__version__ = "2.0.0"
__all__ = [
    # Main factory interface
    'FlowSetupFactory',
    
    # Configuration
    'FlowSetupConfig',
    'FLOW_CONFIGS',
    'get_config',
    'list_available_configs',
    'add_custom_config',
    
    # Base classes
    'BaseComponentApp',
    'BaseApparatusCreator',
    
    # Utilities
    'DataManager',
    'WidgetManager', 
    'ErrorHandler',
    'ValidationError',
    
    # Individual components (advanced usage)
    'TwoSyringesComponentApp',
    'TwoSyringesApparatusCreator',
    'ThreeSyringes1R1MComponentApp',
    'ThreeSyringes1R1MApparatusCreator',
    'ThreeSyringes2R2MComponentApp',
    'ThreeSyringes2R2MApparatusCreator',
    'FlexibleSetupComponentApp',
    'FlexibleSetupApparatusCreator',
]
