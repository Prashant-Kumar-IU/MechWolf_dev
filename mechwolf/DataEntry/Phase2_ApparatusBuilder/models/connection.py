"""
ApparatusConnection data model.

Represents a connection between two components with tube specifications.
"""

from typing import Dict, Any
from .validators import (
    validate_connection_integrity,
    parse_length_dimension
)
from .exceptions import ConnectionValidationError


class ApparatusConnection:
    """Represents a connection between two components."""
    
    def __init__(self, from_component: str, to_component: str, tube_type: str = 'fat_tube', tube_length: str = '1 ft'):
        self.from_component = from_component
        self.to_component = to_component
        self.tube_type = tube_type
        self.tube_length = tube_length
        
        # Import here to avoid circular imports
        try:
            from ..registry import ComponentRegistry
        except ImportError:
            from registry import ComponentRegistry
        self.tube_properties = ComponentRegistry.TUBE_TYPES.get(tube_type, {}).copy()
        
        # Validate connection during initialization
        # Note: Components dict validation will be done externally when available
    
    def to_dict(self):
        """Convert to dictionary for metadata storage with structured units."""
        # Process tube_length for structured storage
        tube_length_data = self.tube_length
        if isinstance(self.tube_length, str) and self.tube_length:
            from ..config.units import UnitSystem
            parsed_value, unit = UnitSystem.parse_value_with_unit(self.tube_length)
            
            if parsed_value is not None and unit is not None:
                tube_length_data = {
                    'value': parsed_value,
                    'unit': unit,
                    'formatted': self.tube_length
                }
        
        return {
            'from': self.from_component,  # Match ApparatusDataManager expected format
            'to': self.to_component,
            'tube_type': self.tube_type,
            'tube_length': tube_length_data,
            'tube_properties': self.tube_properties,
            'unit_system_version': '1.0'
        }
    
    def validate_connection(self, components_dict: Dict[str, Any] = None) -> None:
        """
        Validate connection integrity.
        
        Args:
            components_dict: Dictionary of components to validate against (optional)
            
        Raises:
            ConnectionValidationError: If validation fails
        """
        # Basic connection validation
        self._validate_basic_connection()
        
        # Tube length validation
        self._validate_tube_length()
        
        # Component existence validation (if components dict provided)
        if components_dict:
            validate_connection_integrity(
                self.from_component,
                self.to_component,
                self.tube_type,
                components_dict
            )
    
    def _validate_basic_connection(self) -> None:
        """Validate basic connection properties."""
        if not self.from_component:
            raise ConnectionValidationError(
                f"{self.from_component} → {self.to_component}",
                "From component cannot be empty"
            )
        
        if not self.to_component:
            raise ConnectionValidationError(
                f"{self.from_component} → {self.to_component}",
                "To component cannot be empty"
            )
        
        if not self.tube_type:
            raise ConnectionValidationError(
                f"{self.from_component} → {self.to_component}",
                "Tube type cannot be empty"
            )
        
        # Prevent self-connection
        if self.from_component == self.to_component:
            raise ConnectionValidationError(
                f"{self.from_component} → {self.to_component}",
                "Component cannot connect to itself"
            )
    
    def _validate_tube_length(self) -> None:
        """Validate tube length format."""
        # If tube_length is empty or None, set a default
        if not self.tube_length or self.tube_length.strip() == "":
            self.tube_length = "1 ft"  # Set reasonable default
            return
        
        # Parse and validate tube length format
        parsed_length = parse_length_dimension(self.tube_length)
        if parsed_length is None:
            # Try to fix common issues - if it's just a number, assume feet
            try:
                float(self.tube_length.strip())
                self.tube_length = f"{self.tube_length.strip()} ft"
                return  # Successfully fixed
            except ValueError:
                pass
            
            raise ConnectionValidationError(
                f"{self.from_component} → {self.to_component}",
                f"Invalid tube length format: '{self.tube_length}'. Use format like '1 ft' or '12 in'"
            )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create connection from dictionary."""
        from_comp = data.get('from', data.get('from_component', ''))
        to_comp = data.get('to', data.get('to_component', ''))
        conn = cls(
            from_comp,
            to_comp, 
            data.get('tube_type', 'fat_tube'),
            data.get('tube_length', '1 ft')
        )
        # Handle tube_length in both old and new formats
        tube_length_data = data.get('tube_length', '1 ft')
        if isinstance(tube_length_data, dict) and 'value' in tube_length_data and 'unit' in tube_length_data:
            # New structured format
            from ..config.units import UnitSystem
            conn.tube_length = UnitSystem.format_value_with_unit(
                tube_length_data['value'], tube_length_data['unit']
            )
        else:
            # Old format or simple string
            conn.tube_length = str(tube_length_data)
        
        conn.tube_properties = data.get('tube_properties', {})
        
        # Validate connection after loading
        try:
            conn.validate_connection()
        except ConnectionValidationError as e:
            print(f"Warning: Loaded connection has validation issues: {e}")
        
        return conn