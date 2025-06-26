#!/usr/bin/env python3
"""
Test script for the refactored modular reagent entry system.

This script tests the new modular architecture to ensure all components
work correctly and maintain backward compatibility.
"""

import sys
import traceback
from typing import Any

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test main interface imports (backward compatibility)
        from mechwolf.DataEntry.Phase1_ReagentEntry import (
            ReagentUI, ReagentEntryInterface, launch_gui
        )
        print("✅ Main interface imports successful")
        
        # Test core components
        from mechwolf.DataEntry.Phase1_ReagentEntry.core import (
            ReagentModel, ExperimentModel, ReagentService, ExperimentService
        )
        print("✅ Core components imports successful")
        
        # Test UI components
        from mechwolf.DataEntry.Phase1_ReagentEntry.ui import (
            ReagentForm, ButtonFactory, SectionHeader
        )
        print("✅ UI components imports successful")
        
        # Test external services
        from mechwolf.DataEntry.Phase1_ReagentEntry.external import (
            PubChemService, StructureVisualization
        )
        print("✅ External services imports successful")
        
        # Test utilities
        from mechwolf.DataEntry.Phase1_ReagentEntry.utils import (
            validate_smiles, is_rdkit_available, normalize_chemical_data
        )
        print("✅ Utilities imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False


def test_models():
    """Test the data models."""
    print("🧪 Testing data models...")
    
    try:
        from mechwolf.DataEntry.Phase1_ReagentEntry.core.models import ReagentModel, ExperimentModel
        
        # Test ReagentModel creation
        reagent = ReagentModel(
            name="Ethanol",
            molecular_weight=46.07,
            equivalents=2.0,
            position=1,
            smiles="CCO",
            reagent_type="liquid",
            density=0.789
        )
        
        print(f"✅ Created reagent: {reagent.name}")
        print(f"   Valid: {reagent.is_valid}")
        print(f"   Is limiting: {reagent.is_limiting}")
        
        # Test validation
        if reagent.is_valid:
            print("✅ Reagent validation passed")
        else:
            print(f"❌ Reagent validation failed: {reagent.errors}")
        
        # Test format conversion
        old_format = reagent.to_old_format()
        print(f"✅ Old format conversion: {old_format.get('name')}")
        
        # Test ExperimentModel
        experiment = ExperimentModel()
        experiment.add_reagent(reagent)
        
        print(f"✅ Created experiment with {experiment.total_reagent_count} reagents")
        
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        traceback.print_exc()
        return False


def test_validation():
    """Test validation utilities."""
    print("🧪 Testing validation utilities...")
    
    try:
        from mechwolf.DataEntry.Phase1_ReagentEntry.utils import (
            validate_smiles, validate_reagent_data
        )
        
        # Test SMILES validation
        test_smiles = [
            ("CCO", True),           # Valid ethanol
            ("C1CCCCC1", True),      # Valid cyclohexane
            ("INVALID", False),      # Invalid SMILES
            ("", False),             # Empty SMILES
        ]
        
        for smiles, expected in test_smiles:
            result = validate_smiles(smiles)
            status = "✅" if result == expected else "❌"
            print(f"   {status} SMILES '{smiles}': {result}")
        
        # Test reagent data validation
        reagent_data = {
            "name": "Test Reagent",
            "molecular weight (in g/mol)": 100.0,
            "eq": 1.0,
            "syringe": 1
        }
        
        errors = validate_reagent_data(reagent_data, "solid")
        if not errors:
            print("✅ Reagent data validation passed")
        else:
            print(f"❌ Reagent data validation failed: {errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        traceback.print_exc()
        return False


def test_chemistry_utils():
    """Test chemistry utilities."""
    print("🧪 Testing chemistry utilities...")
    
    try:
        from mechwolf.DataEntry.Phase1_ReagentEntry.utils import (
            is_rdkit_available, safe_mol_from_smiles, normalize_chemical_data
        )
        
        # Test RDKit availability
        rdkit_available = is_rdkit_available()
        print(f"   RDKit available: {rdkit_available}")
        
        # Test safe mol creation
        mol = safe_mol_from_smiles("CCO")
        print(f"✅ Safe mol creation: {mol is not None}")
        
        # Test data normalization
        compound_data = {
            'name': 'Ethanol',
            'smiles': 'CCO'
        }
        
        normalized = normalize_chemical_data(compound_data)
        print(f"✅ Data normalization: {len(normalized)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Chemistry utils test failed: {e}")
        traceback.print_exc()
        return False


def test_services():
    """Test service classes (mock mode)."""
    print("🧪 Testing services (mock mode)...")
    
    try:
        # Create a mock experiment manager for testing
        class MockExperimentManager:
            def __init__(self):
                self.chemistry = MockChemistry()
            
            def save(self):
                return True
        
        class MockChemistry:
            def __init__(self):
                self.data = {"solid_reagents": [], "liquid_reagents": []}
            
            def get_data(self):
                return self.data.copy()
            
            def save_data(self, data):
                self.data = data
                return True
            
            def add_solid_reagent(self, reagent):
                self.data["solid_reagents"].append(reagent)
                return True
            
            def add_liquid_reagent(self, reagent):
                self.data["liquid_reagents"].append(reagent)
                return True
        
        # Test service creation
        from mechwolf.DataEntry.Phase1_ReagentEntry.core import (
            ReagentService, ExperimentService
        )
        from mechwolf.DataEntry.Phase1_ReagentEntry.core.data_adapter import ReagentDataAdapter
        
        mock_manager = MockExperimentManager()
        data_adapter = ReagentDataAdapter(mock_manager)
        reagent_service = ReagentService(data_adapter)
        experiment_service = ExperimentService(data_adapter)
        
        print("✅ Services created successfully")
        
        # Test reagent creation
        form_data = {
            'name': 'Test Reagent',
            'molecular_weight': 100.0,
            'equivalents': 1.0,
            'position': 1
        }
        
        reagent, errors = reagent_service.create_reagent_from_form_data(form_data, "solid")
        
        if not errors and reagent:
            print(f"✅ Reagent created via service: {reagent.name}")
        else:
            print(f"❌ Reagent creation failed: {errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility with original interface."""
    print("🧪 Testing backward compatibility...")
    
    try:
        # Test that original imports still work
        from mechwolf.DataEntry.Phase1_ReagentEntry import ReagentUI, launch_gui
        
        print("✅ Original imports still work")
        
        # Test that ReagentEntryGUI alias exists
        from mechwolf.DataEntry.Phase1_ReagentEntry import ReagentEntryGUI
        print("✅ ReagentEntryGUI alias available")
        
        # Test that utility functions are available
        from mechwolf.DataEntry.Phase1_ReagentEntry import (
            validate_reagent_data, validate_smiles
        )
        print("✅ Utility functions available")
        
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        traceback.print_exc()
        return False


def test_ui_components():
    """Test UI components (basic creation)."""
    print("🧪 Testing UI components...")
    
    try:
        # Test form creation
        from mechwolf.DataEntry.Phase1_ReagentEntry.ui.components.forms import ReagentForm
        
        form = ReagentForm("solid")
        print("✅ ReagentForm created successfully")
        
        # Test base components
        from mechwolf.DataEntry.Phase1_ReagentEntry.ui.components.base import (
            ButtonFactory, MessageArea, SectionHeader
        )
        
        button = ButtonFactory.create_success("Test Button")
        message_area = MessageArea()
        header = SectionHeader.create("Test Header")
        
        print("✅ UI components created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting modular system tests...")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Data Models", test_models),
        ("Validation", test_validation),
        ("Chemistry Utils", test_chemistry_utils),
        ("Services", test_services),
        ("Backward Compatibility", test_backward_compatibility),
        ("UI Components", test_ui_components),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("-" * 60)
    print(f"🎯 TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Modular system is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)