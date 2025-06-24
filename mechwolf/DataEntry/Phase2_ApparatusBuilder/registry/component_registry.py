"""
Component registry for managing available component types.

Provides a centralized registry for component discovery and access.
"""

from typing import Dict, Any
from .component_discovery import discover_components
try:
    from ..config.component_definitions import TUBE_TYPES
except ImportError:
    from config.component_definitions import TUBE_TYPES


class ComponentRegistry:
    """Registry for available components with dynamic discovery from contrib files."""
    
    # Initialize components using discovery system
    _discovered = discover_components()
    ACTIVE_COMPONENTS = _discovered['active']
    PASSIVE_COMPONENTS = _discovered['passive']
    
    # Tube Specifications (used in connections)
    TUBE_TYPES = TUBE_TYPES
    
    @classmethod
    def get_all_components(cls):
        """Get all available components for dropdown menus."""
        all_comps = {}
        all_comps.update(cls.ACTIVE_COMPONENTS)
        all_comps.update(cls.PASSIVE_COMPONENTS)
        return all_comps
    
    @classmethod
    def add_component_type(cls, category: str, comp_type: str, config: Dict[str, Any]):
        """Add a new component type for future extensibility."""
        if category == 'active':
            cls.ACTIVE_COMPONENTS[comp_type] = config
        elif category == 'passive':
            cls.PASSIVE_COMPONENTS[comp_type] = config
    
    @classmethod
    def get_component_info(cls, component_type: str) -> Dict[str, Any]:
        """Get component info with backward compatibility."""
        # Handle backward compatibility for old naming
        if component_type == 'HarvardSyringePump':
            component_type = 'HarvardSyringePump'
        
        # Check active components first
        if component_type in cls.ACTIVE_COMPONENTS:
            return cls.ACTIVE_COMPONENTS[component_type]
        
        # Check passive components
        if component_type in cls.PASSIVE_COMPONENTS:
            return cls.PASSIVE_COMPONENTS[component_type]
        
        # Fallback for unknown components
        return {
            'class_name': component_type,
            'import_path': 'mechwolf',
            'display_name': component_type,
            'icon': '🔧',
            'default_properties': {},
            'required_properties': [],
            'property_types': {}
        }
    
    @classmethod
    def normalize_component_type(cls, component_type: str) -> str:
        """Normalize component type with backward compatibility."""
        if component_type == 'HarvardSyringePump':
            return 'HarvardSyringePump'
        return component_type