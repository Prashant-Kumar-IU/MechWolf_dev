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
        """Convert to dictionary for metadata storage."""
        return {
            'from': self.from_component,  # Match ApparatusDataManager expected format
            'to': self.to_component,
            'tube_type': self.tube_type,
            'tube_length': self.tube_length,
            'tube_properties': self.tube_properties
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
        if not self.tube_length:
            raise ConnectionValidationError(
                f"{self.from_component} → {self.to_component}",
                "Tube length cannot be empty"
            )
        
        # Parse and validate tube length format
        parsed_length = parse_length_dimension(self.tube_length)
        if parsed_length is None:
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
        conn.tube_properties = data.get('tube_properties', {})
        
        # Validate connection after loading
        try:
            conn.validate_connection()
        except ConnectionValidationError as e:
            print(f"Warning: Loaded connection has validation issues: {e}")
        
        return conn