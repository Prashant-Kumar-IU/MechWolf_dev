"""
Custom exception classes for Phase2_ApparatusBuilder.

Provides specific exception types for different validation and error scenarios.
Based on patterns from Old_codes/Appratus/error_handler.py
"""


class ApparatusBuilderError(Exception):
    """Base exception for all apparatus builder errors."""
    pass


class ComponentValidationError(ApparatusBuilderError):
    """Exception raised when component validation fails."""
    
    def __init__(self, component_name: str, message: str):
        self.component_name = component_name
        self.message = message
        super().__init__(f"Component '{component_name}': {message}")


class ConnectionValidationError(ApparatusBuilderError):
    """Exception raised when connection validation fails."""
    
    def __init__(self, connection_desc: str, message: str):
        self.connection_desc = connection_desc
        self.message = message
        super().__init__(f"Connection {connection_desc}: {message}")


class PropertyValidationError(ApparatusBuilderError):
    """Exception raised when property validation fails."""
    
    def __init__(self, property_name: str, property_value: str, message: str):
        self.property_name = property_name
        self.property_value = property_value
        self.message = message
        super().__init__(f"Property '{property_name}' (value: '{property_value}'): {message}")


class MetadataError(ApparatusBuilderError):
    """Exception raised when experimental metadata operations fail."""
    pass


class UnitParsingError(ApparatusBuilderError):
    """Exception raised when unit parsing fails."""
    
    def __init__(self, value: str, expected_format: str):
        self.value = value
        self.expected_format = expected_format
        super().__init__(f"Could not parse '{value}'. Expected format: {expected_format}")


class TubeDimensionError(PropertyValidationError):
    """Exception raised when tube dimension validation fails."""
    
    def __init__(self, id_value: str, od_value: str, message: str = None):
        self.id_value = id_value
        self.od_value = od_value
        default_message = f"Invalid tube dimensions: ID='{id_value}', OD='{od_value}'"
        super().__init__("tube_dimensions", f"ID={id_value}, OD={od_value}", message or default_message)