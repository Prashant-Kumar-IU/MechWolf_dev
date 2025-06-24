"""
Validation functions for Phase2_ApparatusBuilder.

Provides unit parsing and validation functions based on the proven patterns
from Old_codes/Appratus/FlowSetupUtils.py and error_handler.py
"""

# Python version compatibility
from __future__ import annotations

import re
import keyword
from typing import Optional, List, Dict, Any, Tuple
from .exceptions import (
    PropertyValidationError,
    TubeDimensionError,
    UnitParsingError,
    ComponentValidationError,
    ConnectionValidationError
)
from ..config.units import UnitSystem


def convert_dimension_to_float(dimension: str, target_unit: str = 'in') -> Optional[float]:
    """
    Convert a dimension string to float value in target unit (default: inches).
    
    Supports formats like:
    - "1/16 in" -> 0.0625
    - "0.0625 in" -> 0.0625
    - "1.5 mm" -> converted to inches
    - "1/8" -> 0.125 (assumes inches)
    
    Based on Old_codes/Appratus/FlowSetupUtils.py but enhanced with unit system.
    """
    try:
        value, unit = UnitSystem.parse_value_with_unit(str(dimension))
        
        if value is None:
            return None
        
        # If no unit specified, assume target unit
        if unit is None:
            return value
        
        # Convert to target unit if different
        if unit != target_unit:
            converted = UnitSystem.convert_value(value, unit, target_unit)
            return converted if converted is not None else value
        
        return value
    except (IndexError, ValueError, TypeError, ZeroDivisionError):
        return None


def parse_tube_dimension(value: str, default_unit: str = 'in') -> Optional[str]:
    """
    Parse tube dimension that could be fraction or decimal.
    
    Returns standardized format with proper unit.
    Enhanced from Old_codes/Appratus/FlowSetupUtils.py with unit system.
    """
    try:
        parsed_value, unit = UnitSystem.parse_value_with_unit(value)
        
        if parsed_value is None:
            return None
        
        # Use provided unit or default
        final_unit = unit if unit else default_unit
        
        # Validate unit is appropriate for diameter
        if not UnitSystem.validate_unit_for_property(final_unit, 'diameter'):
            final_unit = default_unit
        
        return UnitSystem.format_value_with_unit(parsed_value, final_unit)
    except (IndexError, ValueError):
        return None


def parse_length_dimension(value: str, default_unit: str = 'ft') -> Optional[str]:
    """
    Parse length values with proper unit handling.
    
    Enhanced from Old_codes/Appratus/FlowSetupUtils.py with unit system.
    """
    try:
        parsed_value, unit = UnitSystem.parse_value_with_unit(value)
        
        if parsed_value is None:
            return None
        
        # Use provided unit or default
        final_unit = unit if unit else default_unit
        
        # Validate unit is appropriate for length
        if not UnitSystem.validate_unit_for_property(final_unit, 'length'):
            final_unit = default_unit
        
        return UnitSystem.format_value_with_unit(parsed_value, final_unit)
    except (IndexError, ValueError):
        return None


def validate_tube_dimensions(id_val: str, od_val: str) -> None:
    """
    Validate tube dimensions ensuring OD > ID for all tubes.
    
    Enhanced from Old_codes/Appratus/error_handler.py with unit conversion support.
    """
    if not id_val or not od_val:
        raise TubeDimensionError(
            id_val or "None", 
            od_val or "None",
            "Please enter valid values for tube dimensions (e.g., '1/16 in', '1.5 mm', or '0.0625 in')"
        )

    # Parse dimensions with units
    id_value, id_unit = UnitSystem.parse_value_with_unit(id_val)
    od_value, od_unit = UnitSystem.parse_value_with_unit(od_val)
    
    if id_value is None or od_value is None:
        raise TubeDimensionError(
            id_val, 
            od_val,
            "Invalid dimension format. Use formats like '1/16 in', '1.5 mm', or '0.0625 in'"
        )
    
    # Convert to common unit for comparison (inches)
    id_unit = id_unit or 'in'  # Default to inches if no unit
    od_unit = od_unit or 'in'
    
    id_inches = UnitSystem.convert_value(id_value, id_unit, 'in')
    od_inches = UnitSystem.convert_value(od_value, od_unit, 'in')
    
    if id_inches is None or od_inches is None:
        raise TubeDimensionError(
            id_val,
            od_val,
            f"Cannot compare dimensions with units '{id_unit}' and '{od_unit}'"
        )

    if od_inches <= id_inches:
        raise TubeDimensionError(
            id_val,
            od_val, 
            f"Outer diameter ({od_val}) must be greater than inner diameter ({id_val})"
        )


def validate_component_name(name: str) -> None:
    """
    Validate component name is a valid Python identifier.
    
    Ensures generated code will work properly.
    """
    if not name:
        raise ComponentValidationError(name, "Component name cannot be empty")
    
    if not name.isidentifier():
        raise ComponentValidationError(
            name, 
            "Component name must be a valid Python identifier (letters, numbers, underscore; cannot start with number)"
        )
    
    if keyword.iskeyword(name):
        raise ComponentValidationError(
            name, 
            f"Component name '{name}' is a Python keyword and cannot be used"
        )


def validate_required_component_properties(component_type: str, properties: Dict[str, Any], required_properties: List[str]) -> List[str]:
    """
    Validate component has all required properties.
    
    Returns list of missing property names.
    Based on Old_codes/Appratus/FlowSetupUtils.py:83-107
    """
    missing_fields = []
    
    for prop_name in required_properties:
        prop_value = properties.get(prop_name)
        if not prop_value or (isinstance(prop_value, str) and not prop_value.strip()):
            missing_fields.append(prop_name)
    
    return missing_fields


def validate_syringe_volume(volume: str) -> None:
    """Validate syringe volume format with unit support (e.g., '3 mL', '0.5 L')."""
    if not volume:
        raise PropertyValidationError("syringe_volume", volume, "Syringe volume cannot be empty")
    
    # Parse volume with units
    value, unit = UnitSystem.parse_value_with_unit(volume)
    
    if value is None:
        raise PropertyValidationError(
            "syringe_volume", 
            volume, 
            "Invalid volume format. Use format like '3 mL', '0.5 L', or '500 μL'"
        )
    
    if value <= 0:
        raise PropertyValidationError(
            "syringe_volume", 
            volume, 
            "Syringe volume must be positive"
        )
    
    # Validate unit is a volume unit
    if unit and not UnitSystem.validate_unit_for_property(unit, 'volume'):
        available_units = UnitSystem.get_available_units('volume')
        raise PropertyValidationError(
            "syringe_volume", 
            volume, 
            f"Invalid volume unit '{unit}'. Use one of: {', '.join(available_units)}"
        )


def validate_syringe_diameter(diameter: str) -> None:
    """Validate syringe diameter format with unit support (e.g., '10 mm', '0.5 in')."""
    if not diameter:
        raise PropertyValidationError("syringe_diameter", diameter, "Syringe diameter cannot be empty")
    
    # Parse diameter with units
    value, unit = UnitSystem.parse_value_with_unit(diameter)
    
    if value is None:
        raise PropertyValidationError(
            "syringe_diameter", 
            diameter, 
            "Invalid diameter format. Use format like '10 mm', '0.5 in', or '1.2 cm'"
        )
    
    if value <= 0:
        raise PropertyValidationError(
            "syringe_diameter", 
            diameter, 
            "Syringe diameter must be positive"
        )
    
    # Validate unit is a diameter unit
    if unit and not UnitSystem.validate_unit_for_property(unit, 'diameter'):
        available_units = UnitSystem.get_available_units('diameter')
        raise PropertyValidationError(
            "syringe_diameter", 
            diameter, 
            f"Invalid diameter unit '{unit}'. Use one of: {', '.join(available_units)}"
        )


def validate_serial_port(serial_port: str) -> None:
    """Validate serial port format."""
    if not serial_port:
        raise PropertyValidationError("serial_port", serial_port, "Serial port cannot be empty")
    
    # Basic format validation - either COM# (Windows) or /dev/... (Unix)
    if not (serial_port.startswith('COM') or serial_port.startswith('/dev/')):
        raise PropertyValidationError(
            "serial_port", 
            serial_port, 
            "Serial port should be in format 'COM1' (Windows) or '/dev/ttyUSB0' (Linux/Mac)"
        )


def validate_connection_integrity(from_component: str, to_component: str, tube_type: str, components_dict: Dict[str, Any]) -> None:
    """
    Validate connection integrity.
    
    Ensures components exist and connection is valid.
    """
    # Check components exist
    if from_component not in components_dict:
        raise ConnectionValidationError(
            f"{from_component} → {to_component}",
            f"From component '{from_component}' does not exist"
        )
    
    if to_component not in components_dict:
        raise ConnectionValidationError(
            f"{from_component} → {to_component}",
            f"To component '{to_component}' does not exist"
        )
    
    # Prevent self-connection
    if from_component == to_component:
        raise ConnectionValidationError(
            f"{from_component} → {to_component}",
            "Component cannot connect to itself"
        )
    
    # Validate tube exists and is actually a tube
    if tube_type in components_dict:
        tube_comp = components_dict[tube_type]
        if hasattr(tube_comp, 'component_type') and tube_comp.component_type != 'Tube':
            raise ConnectionValidationError(
                f"{from_component} → {to_component}",
                f"'{tube_type}' is not a tube component (type: {tube_comp.component_type})"
            )
    else:
        # Allow predefined tube types (fat_tube, thin_tube, etc.)
        predefined_tubes = ['fat_tube', 'thin_tube', 'thinner_tube', 'valve_tube']
        if tube_type not in predefined_tubes:
            raise ConnectionValidationError(
                f"{from_component} → {to_component}",
                f"Tube '{tube_type}' does not exist. Available: {predefined_tubes}"
            )