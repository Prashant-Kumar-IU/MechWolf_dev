"""
ApparatusComponent data model.

Represents a single component in the apparatus with properties and metadata.
"""

# Python version compatibility
from __future__ import annotations

from typing import Dict, Any
from .validators import (
    validate_component_name,
    validate_tube_dimensions,
    validate_syringe_volume,
    validate_syringe_diameter,
    validate_serial_port,
    validate_required_component_properties
)
from ..config.units import UnitSystem
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
    
    def to_dict(self, include_registry_info=False):
        """Convert to dictionary for metadata storage with structured units.
        
        Args:
            include_registry_info: If True, includes full registry_info (legacy format)
                                 If False, excludes registry_info (new compact format)
        """
        # Process properties to separate values and units for better storage
        processed_properties = {}
        
        for prop_name, prop_value in self.properties.items():
            if isinstance(prop_value, str) and prop_value:
                # Try to parse as value with unit
                parsed_value, unit = UnitSystem.parse_value_with_unit(prop_value)
                
                if parsed_value is not None and unit is not None:
                    # Store as structured data
                    processed_properties[prop_name] = {
                        'value': parsed_value,
                        'unit': unit,
                        'formatted': prop_value  # Keep original for display
                    }
                else:
                    # Store as simple string
                    processed_properties[prop_name] = prop_value
            else:
                processed_properties[prop_name] = prop_value
        
        result = {
            'type': self.component_type,  # Match ApparatusDataManager expected format
            'name': self.name,
            'description': self.description,
            'instance_id': self.instance_id,
            'properties': processed_properties,
            'unit_system_version': '1.0'  # Track format version
        }
        
        # Include registry_info only if explicitly requested (for backwards compatibility)
        if include_registry_info:
            result['registry_info'] = self.registry_info
            
        return result
    
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
        
        # Validate length if present
        length_val = self.properties.get('length')
        if length_val:
            parsed_value, unit = UnitSystem.parse_value_with_unit(length_val)
            if parsed_value is None:
                raise ComponentValidationError(
                    self.name,
                    f"Invalid length format: '{length_val}'. Use format like '1 ft' or '12 in'"
                )
            if parsed_value <= 0:
                raise ComponentValidationError(
                    self.name,
                    f"Length must be positive: '{length_val}'"
                )
        
        # Validate material is specified
        material = self.properties.get('material')
        if not material or not material.strip():
            raise ComponentValidationError(
                self.name,
                "Tube material must be specified (e.g., 'PFA', 'PTFE', 'Stainless Steel')"
            )
    
    def _validate_harvard_pump_properties(self) -> None:
        """Validate Harvard pump specific properties."""
        if 'syringe_volume' in self.properties:
            validate_syringe_volume(self.properties['syringe_volume'])
        
        if 'syringe_diameter' in self.properties:
            validate_syringe_diameter(self.properties['syringe_diameter'])
        
        if 'serial_port' in self.properties:
            validate_serial_port(self.properties['serial_port'])
        
        # Additional validation for flow rate if present
        flow_rate = self.properties.get('flow_rate')
        if flow_rate:
            parsed_value, unit = UnitSystem.parse_value_with_unit(flow_rate)
            if parsed_value is None:
                raise ComponentValidationError(
                    self.name,
                    f"Invalid flow rate format: '{flow_rate}'. Use format like '1.5 mL/min'"
                )
            if parsed_value <= 0:
                raise ComponentValidationError(
                    self.name,
                    f"Flow rate must be positive: '{flow_rate}'"
                )
            if unit and not UnitSystem.validate_unit_for_property(unit, 'flow_rate'):
                available_units = UnitSystem.get_available_units('flow_rate')
                raise ComponentValidationError(
                    self.name,
                    f"Invalid flow rate unit '{unit}'. Use one of: {', '.join(available_units)}"
                )
    
    def _validate_pump_properties(self) -> None:
        """Validate general pump properties."""
        if 'serial_port' in self.properties:
            validate_serial_port(self.properties['serial_port'])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], component_types_registry: Dict[str, Any] = None):
        """Create component from dictionary.
        
        Args:
            data: Component instance data
            component_types_registry: Registry of component type definitions (for new format)
        """
        comp_type = data.get('type', data.get('component_type', ''))
        comp = cls(comp_type, data['name'], data.get('instance_id', 0))
        comp.description = data.get('description', '')
        
        # Handle registry_info - either from data (old format) or from registry (new format)
        if 'registry_info' in data:
            # Old format - registry_info is embedded
            comp.registry_info = data['registry_info']
        elif component_types_registry and comp_type in component_types_registry:
            # New format - get registry_info from component_types registry
            comp.registry_info = component_types_registry[comp_type]
        # If neither available, registry_info from __init__ is used (ComponentRegistry lookup)
        
        # Load properties, handling both old and new unit formats
        raw_properties = data.get('properties', {})
        processed_properties = {}
        
        for prop_name, prop_value in raw_properties.items():
            if isinstance(prop_value, dict) and 'value' in prop_value and 'unit' in prop_value:
                # New structured format - reconstruct formatted string
                processed_properties[prop_name] = UnitSystem.format_value_with_unit(
                    prop_value['value'], prop_value['unit']
                )
            else:
                # Old format or non-unit property
                processed_properties[prop_name] = prop_value
        
        comp.properties = processed_properties
        
        # Validate properties after loading
        try:
            comp.validate_properties()
        except ComponentValidationError as e:
            print(f"Warning: Loaded component has validation issues: {e}")
        except Exception as e:
            print(f"Warning: Unexpected validation error for component {comp.name}: {e}")
        
        return comp