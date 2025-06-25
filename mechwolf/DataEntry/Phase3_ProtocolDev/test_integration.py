"""
Integration Test for Phase 3 Simple Protocol Builder

Tests the integration between all components of the simple protocol builder.
"""

import tempfile
import os
import json
from datetime import timedelta

# Test imports
try:
    from ..experimental_metadata import ExperimentalMetadataManager
    from .time_variable_manager import TimeVariableManager
    from .protocol_code_generator import ProtocolCodeGenerator
    from .simple_protocol_builder import SimpleProtocolBuilder
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


def create_test_experiment():
    """Create a test experiment with apparatus configuration"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    
    # Test apparatus configuration
    test_config = {
        "mechwolf_experiment": {
            "experiment_id": "test_protocol_builder",
            "experiment_name": "Test Protocol Builder",
            "created": "2024-01-01T00:00:00",
            "version": "3.0.0"
        },
        "apparatus_config": {
            "name": "Test Apparatus",
            "components": {
                "active": [
                    {
                        "name": "pump_1",
                        "type": "HarvardSyringePump",
                        "parameters": {
                            "syringe_volume": "10 mL",
                            "syringe_diameter": "10 mm",
                            "serial_port": "/dev/ttyUSB0"
                        }
                    },
                    {
                        "name": "pump_2", 
                        "type": "HarvardSyringePump",
                        "parameters": {
                            "syringe_volume": "5 mL",
                            "syringe_diameter": "8 mm",
                            "serial_port": "/dev/ttyUSB1"
                        }
                    },
                    {
                        "name": "valve_1",
                        "type": "ViciValve",
                        "parameters": {
                            "serial_port": "/dev/ttyUSB2",
                            "mapping": {
                                "THF": 1,
                                "Li": 2,
                                "waste": 3
                            }
                        }
                    }
                ],
                "passive": [
                    {
                        "name": "vessel_1",
                        "type": "Vessel",
                        "description": "Reaction vessel"
                    },
                    {
                        "name": "tube_1",
                        "type": "Tube",
                        "length": "1 ft",
                        "ID": "1/16 in"
                    }
                ]
            },
            "connections": [
                {
                    "from": "vessel_1",
                    "to": "pump_1", 
                    "tube": "tube_1"
                }
            ]
        }
    }
    
    # Write test config
    json.dump(test_config, temp_file, indent=2)
    temp_file.close()
    
    return temp_file.name


def test_time_variable_manager():
    """Test time variable manager functionality"""
    print("\n🧪 Testing TimeVariableManager...")
    
    manager = TimeVariableManager()
    
    # Test adding variables
    assert manager.add_time_variable("PPh3", "2min"), "Failed to add PPh3 variable"
    assert manager.add_time_variable("H2O", "1min"), "Failed to add H2O variable" 
    assert manager.add_time_variable("flush", "15min"), "Failed to add flush variable"
    
    # Test variable definitions code
    definitions = manager.get_variable_definitions_code()
    assert len(definitions) > 0, "No variable definitions generated"
    assert any("PPh3" in line for line in definitions), "PPh3 not in definitions"
    
    # Test validation
    is_valid, _ = manager.validate_expression("PPh3 + H2O")
    assert is_valid, "Failed to validate valid expression"
    
    is_valid, _ = manager.validate_expression("undefined_var")
    assert not is_valid, "Should have failed validation for undefined variable"
    
    print("✅ TimeVariableManager tests passed")


def test_protocol_code_generator():
    """Test protocol code generator functionality"""
    print("\n🧪 Testing ProtocolCodeGenerator...")
    
    time_manager = TimeVariableManager()
    time_manager.add_time_variable("PPh3", "2min")
    time_manager.add_time_variable("H2O", "1min")
    
    generator = ProtocolCodeGenerator(time_manager)
    
    # Test adding procedures
    test_procedures = [
        {
            "component": "pump_1",
            "action": "run",
            "start_expression": "current",
            "duration_expression": "PPh3 + H2O",
            "parameters": {"rate": "0.5 mL/min"},
            "increment_current_time": True
        },
        {
            "component": "pump_2",
            "action": "run", 
            "start_expression": "current",
            "duration_expression": "H2O",
            "parameters": {"rate": "1 mL/min"},
            "increment_current_time": True
        }
    ]
    
    generator.set_procedures(test_procedures)
    
    # Test code generation
    code = generator.generate_protocol_code()
    assert "import mechwolf as mw" in code, "Missing MechWolf import"
    assert "from datetime import timedelta" in code, "Missing timedelta import"
    assert "PPh3 = timedelta(minutes = 2)" in code, "Missing PPh3 definition"
    assert "P.add(pump_1" in code, "Missing pump_1 procedure"
    assert "rate = \"0.5 mL/min\"" in code, "Missing flow rate"
    
    # Test validation
    is_valid, errors = generator.validate_procedures()
    assert is_valid, f"Validation failed: {errors}"
    
    print("✅ ProtocolCodeGenerator tests passed")


def test_simple_protocol_builder():
    """Test simple protocol builder integration"""
    print("\n🧪 Testing SimpleProtocolBuilder integration...")
    
    # Create test experiment
    config_file = create_test_experiment()
    
    try:
        # Load experiment
        experiment = ExperimentalMetadataManager(config_file)
        
        # Create protocol builder
        builder = SimpleProtocolBuilder(experiment)
        
        # Test apparatus loading
        assert builder.apparatus is not None, "Apparatus not loaded"
        assert len(builder.available_components) > 0, "No components loaded"
        assert "pump_1" in builder.available_components, "pump_1 not found"
        assert "pump_2" in builder.available_components, "pump_2 not found"
        
        # Test adding time variables
        success = builder.time_manager.add_time_variable("test_var", "30s")
        assert success, "Failed to add time variable"
        
        # Test adding procedures programmatically
        test_procedure = {
            "component": "pump_1",
            "action": "run",
            "start_expression": "current",
            "duration_expression": "test_var",
            "parameters": {"rate": "2.0 mL/min"},
            "increment_current_time": True,
            "description": "Test procedure"
        }
        
        builder.procedures.append(test_procedure)
        builder.code_generator.set_procedures(builder.procedures)
        
        # Test code generation
        code = builder.get_generated_code()
        assert "test_var = timedelta(seconds = 30)" in code, "Time variable not in code"
        assert "P.add(pump_1" in code, "Procedure not in code"
        
        # Test summary
        summary = builder.get_procedure_summary()
        assert summary["total_procedures"] == 1, "Wrong procedure count"
        assert "pump_1" in summary["components_used"], "pump_1 not in summary"
        
        print("✅ SimpleProtocolBuilder integration tests passed")
        
    finally:
        # Clean up
        os.unlink(config_file)


def test_example_code_generation():
    """Test generation of code matching the user's example format"""
    print("\n🧪 Testing example code format generation...")
    
    time_manager = TimeVariableManager()
    time_manager.add_time_variable("switch", "45s")
    time_manager.add_time_variable("PPh3", "2min")
    time_manager.add_time_variable("H2O", "1min")
    
    generator = ProtocolCodeGenerator(time_manager)
    
    # Create procedures matching the user's example
    procedures = [
        {
            "component": "pump_1",
            "action": "run",
            "start_expression": "current",
            "duration_expression": "PPh3 + H2O",
            "parameters": {"rate": "0.5 mL/min"},
            "increment_current_time": True
        },
        {
            "component": "pump_2",
            "action": "run",
            "start_expression": "current", 
            "duration_expression": "H2O",
            "parameters": {"rate": "1 mL/min"},
            "increment_current_time": True
        }
    ]
    
    generator.set_procedures(procedures)
    code = generator.generate_protocol_code()
    
    # Verify key elements are present
    required_elements = [
        "switch = timedelta(seconds = 45)",
        "current = timedelta(minutes = 0)",
        "PPh3 = timedelta(minutes = 2)",
        "H2O = timedelta(minutes = 1)",
        "P = mw.Protocol(A)",
        "P.add(pump_1, start = current,",
        "duration = PPh3 + H2O, rate = \"0.5 mL/min\")",
        "current += PPh3 + H2O",
        "P.add(pump_2, start = current,",
        "duration = H2O, rate = \"1 mL/min\")",
        "current += H2O",
        "print(f'TOTAL TIME: {current}')"
    ]
    
    for element in required_elements:
        assert element in code, f"Missing required element: {element}"
    
    print("✅ Example code format generation tests passed")
    print("\n📋 Generated code preview:")
    print("=" * 50)
    print(code[:500] + "..." if len(code) > 500 else code)
    print("=" * 50)


def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Phase 3 Simple Protocol Builder Integration Tests")
    print("=" * 60)
    
    try:
        test_time_variable_manager()
        test_protocol_code_generator()
        test_simple_protocol_builder()
        test_example_code_generation()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 3 Simple Protocol Builder is ready for use")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    run_all_tests()