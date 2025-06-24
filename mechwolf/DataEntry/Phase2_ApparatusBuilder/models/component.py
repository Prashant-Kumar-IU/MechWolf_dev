"""
ApparatusComponent data model.

Represents a single component in the apparatus with properties and metadata.
"""

from typing import Dict, Any
from .validators import (
    validate_component_name,
    validate_tube_dimensions,
    validate_syringe_volume,
    validate_syringe_diameter,
    validate_serial_port,
    validate_required_component_properties
)
from .exceptions import ComponentValidationError


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
        
        # Validate component name
        validate_component_name(name)
    
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
    
    def validate_properties(self) -> None:
        """
        Validate component properties based on component type.
        
        Raises:
            ComponentValidationError: If validation fails
        """
        # Validate required properties
        required_props = self.registry_info.get('required_properties', [])
        missing_props = validate_required_component_properties(
            self.component_type, 
            self.properties, 
            required_props
        )
        
        if missing_props:
            raise ComponentValidationError(
                self.name,
                f"Missing required properties: {', '.join(missing_props)}"
            )
        
        # Component-specific validation
        if self.component_type == 'Tube':
            self._validate_tube_properties()
        elif self.component_type == 'HarvardSyringePump':
            self._validate_harvard_pump_properties()
        elif self.component_type in ['VarianPump', 'ViciPump', 'ViciValve']:
            self._validate_pump_properties()
    
    def _validate_tube_properties(self) -> None:
        """Validate tube-specific properties."""
        id_val = self.properties.get('ID')
        od_val = self.properties.get('OD')
        
        if id_val and od_val:
            validate_tube_dimensions(id_val, od_val)
    
    def _validate_harvard_pump_properties(self) -> None:
        """Validate Harvard pump specific properties."""
        if 'syringe_volume' in self.properties:
            validate_syringe_volume(self.properties['syringe_volume'])
        
        if 'syringe_diameter' in self.properties:
            validate_syringe_diameter(self.properties['syringe_diameter'])
        
        if 'serial_port' in self.properties:
            validate_serial_port(self.properties['serial_port'])
    
    def _validate_pump_properties(self) -> None:
        """Validate general pump properties."""
        if 'serial_port' in self.properties:
            validate_serial_port(self.properties['serial_port'])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create component from dictionary."""
        comp_type = data.get('type', data.get('component_type', ''))
        comp = cls(comp_type, data['name'], data.get('instance_id', 0))
        comp.description = data.get('description', '')
        comp.properties = data.get('properties', {})
        
        # Validate properties after loading
        try:
            comp.validate_properties()
        except ComponentValidationError as e:
            print(f"Warning: Loaded component has validation issues: {e}")
        
        return comp