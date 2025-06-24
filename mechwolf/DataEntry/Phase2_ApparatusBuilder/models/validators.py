"""
Validation functions for Phase2_ApparatusBuilder.

Provides unit parsing and validation functions based on the proven patterns
from Old_codes/Appratus/FlowSetupUtils.py and error_handler.py
"""

import re
import keyword
from typing import Optional, List, Dict, Any
from .exceptions import (
    PropertyValidationError,
    TubeDimensionError,
    UnitParsingError,
    ComponentValidationError,
    ConnectionValidationError
)


def convert_dimension_to_float(dimension: str) -> Optional[float]:
    """
    Convert a dimension string to float value in inches.
    
    Supports formats like:
    - "1/16 in" -> 0.0625
    - "0.0625 in" -> 0.0625
    - "1/8" -> 0.125
    
    Based on Old_codes/Appratus/FlowSetupUtils.py:44-57
    """
    try:
        # Handle fraction format
        fraction_match = re.match(r"(\d+)/(\d+)\s*(?:in)?", str(dimension))
        if fraction_match:
            num, denom = map(int, fraction_match.groups())
            return num / denom

        # Handle decimal format
        number = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(dimension))[0])
        return number
    except (IndexError, ValueError, TypeError, ZeroDivisionError):
        return None


def parse_tube_dimension(value: str) -> Optional[str]:
    """
    Parse tube dimension that could be fraction or decimal.
    
    Returns standardized format with 'in' unit.
    Based on Old_codes/Appratus/FlowSetupUtils.py:60-71
    """
    try:
        fraction_match = re.match(r"(\d+)/(\d+)\s*(?:in)?", value)
        if fraction_match:
            num, denom = map(int, fraction_match.groups())
            return f"{num}/{denom} in"

        number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
        return f"{number} in"
    except (IndexError, ValueError):
        return None


def parse_length_dimension(value: str) -> Optional[str]:
    """
    Parse length values to foot units.
    
    Based on Old_codes/Appratus/FlowSetupUtils.py:74-80
    """
    try:
        number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
        return f"{number} foot"
    except (IndexError, ValueError):
        return None


def validate_tube_dimensions(id_val: str, od_val: str) -> None:
    """
    Validate tube dimensions ensuring OD > ID for all tubes.
    
    Based on Old_codes/Appratus/error_handler.py:47-76
    """
    if not id_val or not od_val:
        raise TubeDimensionError(
            id_val or "None", 
            od_val or "None",
            "Please enter valid values for tube dimensions (e.g., '1/16 in' or '0.0625 in')"
        )

    r_id = convert_dimension_to_float(id_val)
    r_od = convert_dimension_to_float(od_val)
    
    if r_id is None or r_od is None:
        raise TubeDimensionError(
            id_val, 
            od_val,
            "Invalid dimension format. Use formats like '1/16 in' or '0.0625 in'"
        )

    if r_od <= r_id:
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
    """Validate syringe volume format (e.g., '3 mL')."""
    if not volume:
        raise PropertyValidationError("syringe_volume", volume, "Syringe volume cannot be empty")
    
    # Check for mL unit
    if "mL" not in volume and "ml" not in volume:
        raise PropertyValidationError(
            "syringe_volume", 
            volume, 
            "Syringe volume must include 'mL' unit (e.g., '3 mL')"
        )
    
    # Extract and validate numeric value
    try:
        number_match = re.findall(r"[-+]?\d*\.\d+|\d+", volume)
        if not number_match:
            raise ValueError("No numeric value found")
        
        value = float(number_match[0])
        if value <= 0:
            raise ValueError("Value must be positive")
            
    except ValueError:
        raise PropertyValidationError(
            "syringe_volume", 
            volume, 
            "Invalid volume format. Use format like '3 mL' or '10.5 mL'"
        )


def validate_syringe_diameter(diameter: str) -> None:
    """Validate syringe diameter format (e.g., '10 mm')."""
    if not diameter:
        raise PropertyValidationError("syringe_diameter", diameter, "Syringe diameter cannot be empty")
    
    # Check for mm unit
    if "mm" not in diameter:
        raise PropertyValidationError(
            "syringe_diameter", 
            diameter, 
            "Syringe diameter must include 'mm' unit (e.g., '10 mm')"
        )
    
    # Extract and validate numeric value
    try:
        number_match = re.findall(r"[-+]?\d*\.\d+|\d+", diameter)
        if not number_match:
            raise ValueError("No numeric value found")
        
        value = float(number_match[0])
        if value <= 0:
            raise ValueError("Value must be positive")
            
    except ValueError:
        raise PropertyValidationError(
            "syringe_diameter", 
            diameter, 
            "Invalid diameter format. Use format like '10 mm' or '12.5 mm'"
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