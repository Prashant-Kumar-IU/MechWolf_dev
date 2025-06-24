"""
ApparatusConnection data model.

Represents a connection between two components with tube specifications.
"""

from typing import Dict, Any


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
    
    def to_dict(self):
        """Convert to dictionary for metadata storage."""
        return {
            'from': self.from_component,  # Match ApparatusDataManager expected format
            'to': self.to_component,
            'tube_type': self.tube_type,
            'tube_length': self.tube_length,
            'tube_properties': self.tube_properties
        }
    
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
        return conn