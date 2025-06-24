#!/usr/bin/env python3
"""
Test script to verify the modular designer works after refactoring.
"""

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test v2 imports
        from .tabbed_apparatus_designer_v2 import (
            TabbedApparatusDesigner,
            ComponentRegistry,
            ApparatusComponent,
            ApparatusConnection,
            create_tabbed_apparatus_designer
        )
        print("   ✅ V2 imports successful")
        
        # Test backward compatibility imports
        from . import create_tabbed_apparatus_designer as create_func
        from . import get_designer_info
        print("   ✅ Backward compatibility imports successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_component_creation():
    """Test component creation."""
    print("\n🔧 Testing component creation...")
    
    try:
        from .models import ApparatusComponent
        from .registry import ComponentRegistry
        
        # Test creating a Harvard pump
        pump = ApparatusComponent('HarvardSyringePump', 'test_pump', 1)
        print(f"   ✅ Created pump: {pump.name} of type {pump.component_type}")
        
        # Test component registry
        info = ComponentRegistry.get_component_info('HarvardSyringePump')
        print(f"   ✅ Registry info: {info['display_name']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Component creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_creation():
    """Test connection creation."""
    print("\n🔗 Testing connection creation...")
    
    try:
        from .models import ApparatusConnection
        
        conn = ApparatusConnection('pump_1', 'vessel_1', 'fat_tube')
        print(f"   ✅ Created connection: {conn.from_component} → {conn.to_component}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_designer_creation():
    """Test designer creation without UI display."""
    print("\n🎨 Testing designer creation...")
    
    try:
        from .core import TabbedApparatusDesigner
        
        # Create designer without experiment manager
        designer = TabbedApparatusDesigner(None)
        print("   ✅ Designer created successfully")
        
        # Test adding a component programmatically
        designer._add_harvard_pump(None)
        print(f"   ✅ Added component, total components: {len(designer.components)}")
        
        # Test code generation
        code = designer.code_output.value
        print("   ✅ Code generation accessible")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Designer creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_designer_info():
    """Test designer info function."""
    print("\n📋 Testing designer info...")
    
    try:
        from . import get_designer_info
        
        info = get_designer_info()
        print(f"   ✅ Available designers: {len(info['available_designers'])}")
        for designer in info['available_designers']:
            print(f"      - {designer}")
        
        enhanced_available = info.get('enhanced_designer_available', False)
        print(f"   ✅ Enhanced designer available: {enhanced_available}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Designer info failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("🧪 Testing Modular Phase2_ApparatusBuilder")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_component_creation,
        test_connection_creation,
        test_designer_creation,
        test_designer_info
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! Modular refactoring successful.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print("=" * 50)
    
    return all(results)

if __name__ == "__main__":
    run_all_tests()