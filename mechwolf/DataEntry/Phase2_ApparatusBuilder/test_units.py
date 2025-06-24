#!/usr/bin/env python3
"""
Test script for the new universal unit system.

Tests unit parsing, validation, and conversion functionality.
"""

import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_unit_parsing():
    """Test unit parsing functionality."""
    print("🧪 Testing Unit Parsing...")
    
    from config.units import UnitSystem
    
    test_cases = [
        ("1.5 ft", 1.5, "ft"),
        ("1/16 in", 0.0625, "in"),
        ("3 mL", 3.0, "mL"),
        ("10 mm", 10.0, "mm"),
        ("0.5", 0.5, None),
        ("invalid", None, None),
    ]
    
    for test_input, expected_value, expected_unit in test_cases:
        value, unit = UnitSystem.parse_value_with_unit(test_input)
        
        if value == expected_value and unit == expected_unit:
            print(f"  ✅ '{test_input}' -> {value}, {unit}")
        else:
            print(f"  ❌ '{test_input}' -> {value}, {unit} (expected {expected_value}, {expected_unit})")


def test_unit_conversion():
    """Test unit conversion functionality."""
    print("\n🔄 Testing Unit Conversion...")
    
    from config.units import UnitSystem
    
    test_cases = [
        (1.0, "ft", "in", 12.0),
        (1.0, "in", "mm", 25.4),
        (1000.0, "mL", "L", 1.0),
        (0.0625, "in", "mm", 1.5875),
    ]
    
    for value, from_unit, to_unit, expected in test_cases:
        result = UnitSystem.convert_value(value, from_unit, to_unit)
        
        if result is not None and abs(result - expected) < 0.001:
            print(f"  ✅ {value} {from_unit} -> {result:.4f} {to_unit}")
        else:
            print(f"  ❌ {value} {from_unit} -> {result} {to_unit} (expected {expected})")


def test_tube_validation():
    """Test tube dimension validation."""
    print("\n📏 Testing Tube Validation...")
    
    try:
        # Import with fallback for different execution contexts
        try:
            from models.validators import validate_tube_dimensions
            from models.exceptions import TubeDimensionError
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from Phase2_ApparatusBuilder.models.validators import validate_tube_dimensions
            from Phase2_ApparatusBuilder.models.exceptions import TubeDimensionError
    except ImportError as e:
        print(f"  ⚠️ Could not import validation modules: {e}")
        return
    
    test_cases = [
        ("1/16 in", "1/8 in", True),  # Valid: OD > ID
        ("1/8 in", "1/16 in", False), # Invalid: OD < ID
        ("1.5 mm", "3 mm", True),     # Valid: different units
        ("invalid", "1/8 in", False), # Invalid format
    ]
    
    for id_val, od_val, should_pass in test_cases:
        try:
            validate_tube_dimensions(id_val, od_val)
            result = True
        except TubeDimensionError:
            result = False
        except Exception as e:
            print(f"  ⚠️ Unexpected error: {e}")
            result = False
        
        if result == should_pass:
            status = "✅" if should_pass else "✅ (correctly failed)"
            print(f"  {status} ID: {id_val}, OD: {od_val}")
        else:
            status = "❌"
            print(f"  {status} ID: {id_val}, OD: {od_val} (expected {'pass' if should_pass else 'fail'})")


def test_component_creation():
    """Test component creation with validation."""
    print("\n🔧 Testing Component Creation...")
    
    try:
        try:
            from models.component import ApparatusComponent
            from models.exceptions import ComponentValidationError
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from Phase2_ApparatusBuilder.models.component import ApparatusComponent
            from Phase2_ApparatusBuilder.models.exceptions import ComponentValidationError
    except ImportError as e:
        print(f"  ⚠️ Could not import component modules: {e}")
        return
    
    # Test tube component
    try:
        tube = ApparatusComponent('Tube', 'test_tube', 1)
        tube.properties = {
            'ID': '1/16 in',
            'OD': '1/8 in', 
            'length': '2 ft',
            'material': 'PFA'
        }
        
        tube.validate_properties()
        print("  ✅ Tube component created and validated")
        
        # Test to_dict with structured units
        tube_dict = tube.to_dict()
        if 'unit_system_version' in tube_dict:
            print("  ✅ Structured unit data saved")
        else:
            print("  ❌ Structured unit data not saved")
            
    except ComponentValidationError as e:
        print(f"  ❌ Tube validation failed: {e}")
    except Exception as e:
        print(f"  ⚠️ Unexpected error: {e}")


def test_connection_creation():
    """Test connection creation with validation."""
    print("\n🔗 Testing Connection Creation...")
    
    try:
        try:
            from models.connection import ApparatusConnection
            from models.exceptions import ConnectionValidationError
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from Phase2_ApparatusBuilder.models.connection import ApparatusConnection
            from Phase2_ApparatusBuilder.models.exceptions import ConnectionValidationError
    except ImportError as e:
        print(f"  ⚠️ Could not import connection modules: {e}")
        return
    
    try:
        conn = ApparatusConnection('pump_1', 'vessel_1', 'tube_1', '1.5 ft')
        conn.validate_connection()
        print("  ✅ Connection created and validated")
        
        # Test to_dict with structured units
        conn_dict = conn.to_dict()
        if 'unit_system_version' in conn_dict:
            print("  ✅ Structured unit data saved for connection")
        else:
            print("  ❌ Structured unit data not saved for connection")
            
    except ConnectionValidationError as e:
        print(f"  ❌ Connection validation failed: {e}")
    except Exception as e:
        print(f"  ⚠️ Unexpected error: {e}")


if __name__ == "__main__":
    print("🚀 Universal Unit System Test Suite")
    print("=" * 50)
    
    try:
        test_unit_parsing()
        test_unit_conversion()
        test_tube_validation()
        test_component_creation()
        test_connection_creation()
        
        print("\n🎉 Test suite completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the Phase2_ApparatusBuilder directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()