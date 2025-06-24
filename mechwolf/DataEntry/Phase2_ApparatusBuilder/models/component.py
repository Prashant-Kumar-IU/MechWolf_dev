"""
ApparatusComponent data model.

Represents a single component in the apparatus with properties and metadata.
"""

from typing import Dict, Any


class ApparatusComponent:
    """Represents a single component in the apparatus."""
    
    def __init__(self, component_type: str, name: str, instance_id: int):
        self.component_type = component_type
        self.name = name
        self.instance_id = instance_id
        self.description = ""  # User-defined description
        self.properties = {}
        
        # Import here to avoid circular imports
        try:
            from ..registry import ComponentRegistry
        except ImportError:
            from registry import ComponentRegistry
        self.registry_info = ComponentRegistry.get_all_components().get(component_type, {})
        
        # Set default properties
        if 'default_properties' in self.registry_info:
            self.properties = self.registry_info['default_properties'].copy()
    
    def to_dict(self):
        """Convert to dictionary for metadata storage."""
        return {
            'type': self.component_type,  # Match ApparatusDataManager expected format
            'name': self.name,
            'description': self.description,
            'instance_id': self.instance_id,
            'properties': self.properties,
            'registry_info': self.registry_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create component from dictionary."""
        comp_type = data.get('type', data.get('component_type', ''))
        comp = cls(comp_type, data['name'], data.get('instance_id', 0))
        comp.description = data.get('description', '')
        comp.properties = data.get('properties', {})
        return comp