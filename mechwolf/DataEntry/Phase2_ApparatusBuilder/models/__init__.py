"""
Data models for Phase2_ApparatusBuilder.

Contains the core data structures used throughout the apparatus builder.
"""

from .component import ApparatusComponent
from .connection import ApparatusConnection
from .exceptions import (
    ApparatusBuilderError,
    ComponentValidationError,
    ConnectionValidationError,
    PropertyValidationError,
    MetadataError,
    UnitParsingError,
    TubeDimensionError
)
from .validators import (
    validate_component_name,
    validate_tube_dimensions,
    validate_syringe_volume,
    validate_syringe_diameter,
    validate_serial_port,
    validate_connection_integrity,
    parse_tube_dimension,
    parse_length_dimension
)

__all__ = [
    'ApparatusComponent', 
    'ApparatusConnection',
    'ApparatusBuilderError',
    'ComponentValidationError',
    'ConnectionValidationError',
    'PropertyValidationError',
    'MetadataError',
    'UnitParsingError',
    'TubeDimensionError',
    'validate_component_name',
    'validate_tube_dimensions',
    'validate_syringe_volume',
    'validate_syringe_diameter',
    'validate_serial_port',
    'validate_connection_integrity',
    'parse_tube_dimension',
    'parse_length_dimension'
]