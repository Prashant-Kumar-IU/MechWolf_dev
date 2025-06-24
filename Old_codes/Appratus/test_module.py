"""
Test script for the new modular FlowSetups system.

This script verifies that all the major components work correctly together.
Run this after installation to ensure everything is functioning properly.
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing imports...")
    
    try:
        from mechwolf.DataEntry.FlowSetups import (
            FlowSetupFactory,
            FlowSetupConfig,
            get_config,
            list_available_configs,
            BaseComponentApp,
            BaseApparatusCreator
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_configurations():
    """Test configuration system"""
    print("\nTesting configuration system...")
    
    try:
        from mechwolf.DataEntry.FlowSetups import get_config, list_available_configs
        
        # Test listing configs
        configs = list_available_configs()
        expected_configs = ['two_syringes_1r_1m', 'three_syringes_1r_1m', 
                          'three_syringes_2r_2m', 'flexible_setup']
        
        for expected in expected_configs:
            if expected not in configs:
                print(f"✗ Missing expected config: {expected}")
                return False
        
        # Test getting specific config
        config = get_config('two_syringes_1r_1m')
        if config.name != "Two Syringes, 1 Reaction Coil, 1 Mixer":
            print(f"✗ Unexpected config name: {config.name}")
            return False
        
        print("✓ Configuration system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_factory():
    """Test factory pattern"""
    print("\nTesting factory pattern...")
    
    try:
        from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
        
        # Test available setups
        setups = FlowSetupFactory.available_setups()
        if len(setups) < 4:
            print(f"✗ Expected at least 4 setups, got {len(setups)}")
            return False
        
        # Test setup info
        info = FlowSetupFactory.get_setup_info('two_syringes_1r_1m')
        if 'name' not in info or 'description' not in info:
            print("✗ Setup info missing required fields")
            return False
        
        print("✓ Factory pattern working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Factory test failed: {e}")
        return False


def test_data_manager():
    """Test data management"""
    print("\nTesting data manager...")
    
    try:
        from mechwolf.DataEntry.FlowSetups import DataManager
        import tempfile
        import json
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "apparatus_config": {
                    "apparatus_name": "Test Apparatus",
                    "setup_type": "two_syringes_1r_1m"
                }
            }
            json.dump(test_config, f)
            temp_file = f.name
        
        try:
            # Test loading
            dm = DataManager(temp_file)
            loaded_config = dm.load_config()
            
            if loaded_config is None or loaded_config["apparatus_name"] != "Test Apparatus":
                print("✗ Failed to load configuration correctly")
                return False
            
            # Test saving
            new_config = loaded_config.copy()
            new_config["apparatus_name"] = "Updated Test Apparatus"
            dm.save_config(new_config)
            
            # Verify save
            reloaded_config = dm.load_config()
            if reloaded_config["apparatus_name"] != "Updated Test Apparatus":
                print("✗ Failed to save configuration correctly")
                return False
            
            print("✓ Data manager working correctly")
            return True
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        print(f"✗ Data manager test failed: {e}")
        return False


def run_all_tests() -> bool:
    """Run all tests and return overall success"""
    print("MechWolf FlowSetups Module Test Suite")
    print("=====================================")
    
    tests = [
        test_imports,
        test_configurations,
        test_factory,
        test_data_manager
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\nTest Results: {success_count}/{total_count} passed")
    
    if all(results):
        print("🎉 All tests passed! The FlowSetups module is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
