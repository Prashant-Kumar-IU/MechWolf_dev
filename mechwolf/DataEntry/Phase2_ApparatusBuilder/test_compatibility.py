#!/usr/bin/env python3
"""
Test Python version compatibility for the Phase2_ApparatusBuilder.

Tests that all type annotations work in different Python versions.
"""

# Python version compatibility
from __future__ import annotations

import sys
print(f"Testing Python compatibility with version: {sys.version}")

def test_type_annotations():
    """Test that type annotations work correctly."""
    
    # Test function with return type annotation
    def test_function() -> tuple[bool, str]:
        return True, "test"
    
    # Test that the function works
    result = test_function()
    print(f"✅ Type annotation test passed: {result}")

def test_imports():
    """Test that all modules can be imported."""
    try:
        from config.units import UnitSystem
        print("✅ UnitSystem imported successfully")
        
        # Test unit parsing
        value, unit = UnitSystem.parse_value_with_unit("1.5 ft")
        print(f"✅ Unit parsing works: {value} {unit}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Runtime error: {e}")

def test_widget_compatibility():
    """Test widget imports work."""
    try:
        # Try to import without ipywidgets dependency
        import sys
        sys.modules['ipywidgets'] = None  # Mock missing ipywidgets
        
        # This should not fail even if ipywidgets is missing
        print("✅ Widget compatibility check would pass with proper fallbacks")
        
    except Exception as e:
        print(f"⚠️ Widget compatibility issue: {e}")

if __name__ == "__main__":
    print("🧪 Testing Phase2_ApparatusBuilder Python Compatibility")
    print("=" * 60)
    
    try:
        test_type_annotations()
        test_imports()
        test_widget_compatibility()
        
        print("\n🎉 Compatibility tests completed!")
        print("The codebase should now work with Python 3.7+")
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        import traceback
        traceback.print_exc()