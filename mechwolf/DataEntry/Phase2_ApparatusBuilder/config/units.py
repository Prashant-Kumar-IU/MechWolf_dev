"""
Universal unit configuration system for Phase2_ApparatusBuilder.

Provides comprehensive unit definitions, validation, and conversion utilities
for all measurement types used in apparatus design.
"""

# Python version compatibility
from __future__ import annotations

from typing import List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class UnitDefinition:
    """Definition of a measurement unit with conversion factor."""
    symbol: str  # e.g., "ft", "in", "mm"
    name: str    # e.g., "feet", "inches", "millimeters"
    factor: float  # Conversion factor to base unit
    category: str  # e.g., "length", "volume", "diameter"


class UnitSystem:
    """Universal unit system for apparatus measurements."""
    
    # Define all available units with conversion factors to base units
    UNIT_DEFINITIONS = {
        # Length units (base: inches)
        'in': UnitDefinition('in', 'inches', 1.0, 'length'),
        'ft': UnitDefinition('ft', 'feet', 12.0, 'length'),
        'mm': UnitDefinition('mm', 'millimeters', 0.0393701, 'length'),
        'cm': UnitDefinition('cm', 'centimeters', 0.393701, 'length'),
        'm': UnitDefinition('m', 'meters', 39.3701, 'length'),
        
        # Diameter/tube dimensions (base: inches)
        'in_d': UnitDefinition('in', 'inches', 1.0, 'diameter'),
        'mm_d': UnitDefinition('mm', 'millimeters', 0.0393701, 'diameter'),
        'cm_d': UnitDefinition('cm', 'centimeters', 0.393701, 'diameter'),
        
        # Volume units (base: mL)
        'mL': UnitDefinition('mL', 'milliliters', 1.0, 'volume'),
        'L': UnitDefinition('L', 'liters', 1000.0, 'volume'),
        'uL': UnitDefinition('μL', 'microliters', 0.001, 'volume'),
        'ul': UnitDefinition('μL', 'microliters', 0.001, 'volume'),  # Alternative spelling
        'fl_oz': UnitDefinition('fl oz', 'fluid ounces', 29.5735, 'volume'),
        
        # Flow rate units (base: mL/min)
        'mL/min': UnitDefinition('mL/min', 'milliliters per minute', 1.0, 'flow_rate'),
        'uL/min': UnitDefinition('μL/min', 'microliters per minute', 0.001, 'flow_rate'),
        'L/min': UnitDefinition('L/min', 'liters per minute', 1000.0, 'flow_rate'),
        'mL/hr': UnitDefinition('mL/hr', 'milliliters per hour', 1/60.0, 'flow_rate'),
        
        # Temperature units (base: Celsius)
        'C': UnitDefinition('°C', 'degrees Celsius', 1.0, 'temperature'),
        'celsius': UnitDefinition('°C', 'degrees Celsius', 1.0, 'temperature'),
        'F': UnitDefinition('°F', 'degrees Fahrenheit', 1.0, 'temperature'),  # Special conversion
        'fahrenheit': UnitDefinition('°F', 'degrees Fahrenheit', 1.0, 'temperature'),
        'K': UnitDefinition('K', 'Kelvin', 1.0, 'temperature'),  # Special conversion
        'kelvin': UnitDefinition('K', 'Kelvin', 1.0, 'temperature'),
        
        # Pressure units (base: psi)
        'psi': UnitDefinition('psi', 'pounds per square inch', 1.0, 'pressure'),
        'bar': UnitDefinition('bar', 'bar', 14.5038, 'pressure'),
        'atm': UnitDefinition('atm', 'atmospheres', 14.6959, 'pressure'),
        'Pa': UnitDefinition('Pa', 'pascals', 0.000145038, 'pressure'),
        'kPa': UnitDefinition('kPa', 'kilopascals', 0.145038, 'pressure'),
        'MPa': UnitDefinition('MPa', 'megapascals', 145.038, 'pressure'),
    }
    
    # Define which units are available for each property type
    PROPERTY_UNITS = {
        'length': ['ft', 'in', 'mm', 'cm', 'm'],
        'diameter': ['in', 'mm', 'cm'],  # For tube ID/OD
        'volume': ['mL', 'L', 'uL', 'ul', 'fl_oz'],
        'flow_rate': ['mL/min', 'uL/min', 'L/min', 'mL/hr'],
        'temperature': ['C', 'celsius', 'F', 'fahrenheit', 'K', 'kelvin'],
        'pressure': ['psi', 'bar', 'atm', 'Pa', 'kPa', 'MPa'],
    }
    
    # Define default units for different component properties
    DEFAULT_UNITS = {
        'length': 'ft',
        'ID': 'in',
        'OD': 'in', 
        'diameter': 'mm',
        'syringe_diameter': 'mm',
        'syringe_volume': 'mL',
        'flow_rate': 'mL/min',
        'temperature': 'C',
        'pressure': 'psi',
        'volume': 'mL',
    }
    
    @classmethod
    def get_available_units(cls, property_name: str) -> List[str]:
        """Get available units for a specific property."""
        # Determine unit category based on property name
        if property_name in ['length', 'tube_length']:
            category = 'length'
        elif property_name in ['ID', 'OD', 'inner_diameter', 'outer_diameter']:
            category = 'diameter'
        elif property_name in ['syringe_diameter', 'diameter']:
            category = 'diameter'
        elif property_name in ['syringe_volume', 'volume']:
            category = 'volume'
        elif property_name in ['flow_rate', 'rate']:
            category = 'flow_rate'
        elif property_name in ['temperature', 'temp']:
            category = 'temperature'
        elif property_name in ['pressure']:
            category = 'pressure'
        else:
            # Default to length for unknown properties
            category = 'length'
        
        return cls.PROPERTY_UNITS.get(category, ['ft'])
    
    @classmethod
    def get_default_unit(cls, property_name: str) -> str:
        """Get default unit for a property."""
        return cls.DEFAULT_UNITS.get(property_name, 'ft')
    
    @classmethod
    def parse_value_with_unit(cls, value_str: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Parse a string like "1.5 ft" into value and unit.
        
        Returns:
            Tuple of (numeric_value, unit_string) or (None, None) if parsing fails
        """
        if not value_str or not isinstance(value_str, str):
            return None, None
        
        value_str = value_str.strip()
        
        # Try to match number followed by unit
        match = re.match(r'^([+-]?\d*\.?\d+)\s*([a-zA-Z/°μ]+)$', value_str)
        if match:
            try:
                numeric_value = float(match.group(1))
                unit = match.group(2)
                return numeric_value, unit
            except ValueError:
                return None, None
        
        # Try fraction format like "1/16 in"
        fraction_match = re.match(r'^(\d+)/(\d+)\s*([a-zA-Z/°μ]+)$', value_str)
        if fraction_match:
            try:
                num = int(fraction_match.group(1))
                denom = int(fraction_match.group(2))
                unit = fraction_match.group(3)
                return num / denom, unit
            except (ValueError, ZeroDivisionError):
                return None, None
        
        # Try fraction format without unit like "1/16"
        fraction_no_unit_match = re.match(r'^(\d+)/(\d+)$', value_str)
        if fraction_no_unit_match:
            try:
                num = int(fraction_no_unit_match.group(1))
                denom = int(fraction_no_unit_match.group(2))
                return num / denom, None
            except (ValueError, ZeroDivisionError):
                return None, None
        
        # Just a number without unit
        try:
            numeric_value = float(value_str)
            return numeric_value, None
        except ValueError:
            return None, None
    
    @classmethod
    def format_value_with_unit(cls, value: float, unit: str) -> str:
        """Format a numeric value with its unit."""
        if value is None or unit is None:
            return ""
        
        # Handle fractions for common tube dimensions
        if unit in ['in'] and 0 < value < 1:
            # Try to represent as a simple fraction
            for denom in [2, 4, 8, 16, 32, 64]:
                num = value * denom
                if abs(num - round(num)) < 0.001:  # Close to integer
                    return f"{int(round(num))}/{denom} {unit}"
        
        # Format as decimal
        if value == int(value):
            return f"{int(value)} {unit}"
        else:
            return f"{value:.3g} {unit}"
    
    @classmethod
    def convert_value(cls, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """
        Convert a value from one unit to another within the same category.
        
        Returns None if conversion is not possible.
        """
        from_def = cls.UNIT_DEFINITIONS.get(from_unit)
        to_def = cls.UNIT_DEFINITIONS.get(to_unit)
        
        if not from_def or not to_def:
            return None
        
        if from_def.category != to_def.category:
            return None
        
        # Special handling for temperature
        if from_def.category == 'temperature':
            return cls._convert_temperature(value, from_unit, to_unit)
        
        # Standard conversion via base unit
        base_value = value * from_def.factor
        converted_value = base_value / to_def.factor
        
        return converted_value
    
    @classmethod
    def _convert_temperature(cls, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert temperature values with proper formulas."""
        # Normalize unit names
        from_unit = from_unit.lower().replace('°', '').replace('degrees', '').strip()
        to_unit = to_unit.lower().replace('°', '').replace('degrees', '').strip()
        
        # Convert to Celsius first
        if from_unit in ['c', 'celsius']:
            celsius = value
        elif from_unit in ['f', 'fahrenheit']:
            celsius = (value - 32) * 5/9
        elif from_unit in ['k', 'kelvin']:
            celsius = value - 273.15
        else:
            return None
        
        # Convert from Celsius to target
        if to_unit in ['c', 'celsius']:
            return celsius
        elif to_unit in ['f', 'fahrenheit']:
            return celsius * 9/5 + 32
        elif to_unit in ['k', 'kelvin']:
            return celsius + 273.15
        else:
            return None
    
    @classmethod
    def validate_unit_for_property(cls, unit: str, property_name: str) -> bool:
        """Check if a unit is valid for a given property."""
        available_units = cls.get_available_units(property_name)
        return unit in available_units
    
    @classmethod
    def get_unit_info(cls, unit: str) -> Optional[UnitDefinition]:
        """Get detailed information about a unit."""
        return cls.UNIT_DEFINITIONS.get(unit)


# Convenience functions for backward compatibility
def parse_dimension_with_unit(value_str: str) -> Tuple[Optional[float], Optional[str]]:
    """Parse dimension string into value and unit."""
    return UnitSystem.parse_value_with_unit(value_str)


def format_dimension_with_unit(value: float, unit: str) -> str:
    """Format dimension with proper unit display."""
    return UnitSystem.format_value_with_unit(value, unit)


def convert_dimension(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    """Convert dimension between units."""
    return UnitSystem.convert_value(value, from_unit, to_unit)