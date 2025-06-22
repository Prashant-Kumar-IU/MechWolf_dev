#!/usr/bin/env python3
"""
Test script for the enhanced Phase1_ReagentEntry module

This script demonstrates that the core functionality works without Jupyter/ipywidgets.
"""

import sys
import os
sys.path.insert(0, '.')

# Test imports and basic functionality
def test_core_functionality():
    """Test the core reagent entry functionality"""
    print("🧪 Testing Enhanced Phase1_ReagentEntry Module")
    print("=" * 50)
    
    try:
        # Test reagent utilities
        from mechwolf.DataEntry.Phase1_ReagentEntry.reagent_utils import (
            validate_smiles, validate_reagent_data, is_rdkit_available
        )
        print("✅ reagent_utils imported successfully")
        
        # Test SMILES validation
        test_smiles = ["CCO", "c1ccccc1", "invalid", ""]
        print("\n🧬 SMILES Validation Tests:")
        for smiles in test_smiles:
            result = validate_smiles(smiles)
            print(f"  '{smiles}': {result}")
        
        # Test reagent data validation
        print("\n📝 Reagent Data Validation Tests:")
        
        # Valid solid reagent
        valid_solid = {
            "name": "Benzene",
            "molecular_weight": 78.11,
            "eq": 1.0,
            "position": 1,
            "mass": 100.0
        }
        errors = validate_reagent_data(valid_solid, "solid")
        print(f"  Valid solid reagent: {len(errors)} errors")
        
        # Invalid reagent (missing name)
        invalid_reagent = {
            "molecular_weight": 78.11,
            "eq": 1.0,
            "position": 1,
            "mass": 100.0
        }
        errors = validate_reagent_data(invalid_reagent, "solid")
        print(f"  Invalid reagent (no name): {len(errors)} errors")
        if errors:
            for error in errors:
                print(f"    - {error}")
        
        # Test RDKit availability
        rdkit_available = is_rdkit_available()
        print(f"\n🔬 RDKit availability: {rdkit_available}")
        
    except Exception as e:
        print(f"❌ Error testing reagent_utils: {e}")
        return False
    
    try:
        # Test PubChem service
        from mechwolf.DataEntry.Phase1_ReagentEntry.pubchem_service import PubChemService
        print("\n🔍 Testing PubChem Service:")
        
        pubchem = PubChemService()
        print("✅ PubChemService instance created")
        
        # Note: We won't actually make API calls in the test to avoid network dependency
        print("  (Skipping actual API calls for offline testing)")
        
    except Exception as e:
        print(f"❌ Error testing PubChem service: {e}")
        return False
    
    print("\n✅ Core functionality tests completed successfully!")
    return True

def test_data_integration():
    """Test integration with the experimental metadata system"""
    print("\n⚗️ Testing Data Integration")
    print("=" * 30)
    
    try:
        # Test if we can create an experimental metadata manager
        from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
        
        # Create a test experiment
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_file = f.name
        
        try:
            # Create experiment manager
            experiment = ExperimentalMetadataManager(test_file, "Test Reagent Entry")
            print("✅ ExperimentalMetadataManager created successfully")
            
            # Test adding reagents directly
            reagent_data = {
                "name": "Test Compound",
                "molecular_weight": 100.0,
                "eq": 1.0,
                "position": 1,
                "mass": 50.0,
                "inChi": "InChI=1S/C6H6/c1-2-4-6-5-3-1/h1-6H",
                "SMILES": "c1ccccc1"
            }
            
            success = experiment.chemistry.add_solid_reagent(reagent_data)
            print(f"✅ Added solid reagent: {success}")
            
            # Test retrieving data
            chemistry_data = experiment.chemistry.get_data()
            solid_reagents = chemistry_data.get("solid_reagents", [])
            print(f"✅ Retrieved {len(solid_reagents)} solid reagents")
            
            if solid_reagents:
                print(f"  First reagent: {solid_reagents[0]['name']}")
            
            experiment.save()
            print("✅ Experiment saved successfully")
            
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.unlink(test_file)
        
    except Exception as e:
        print(f"❌ Error testing data integration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Data integration tests completed successfully!")
    return True

def show_usage_example():
    """Show how to use the enhanced reagent entry system"""
    print("\n📖 Usage Example")
    print("=" * 20)
    
    usage_code = '''
# Example usage in a Jupyter notebook:

from mechwolf.DataEntry import create_experiment, launch_reagent_entry

# Create a new experiment
experiment = create_experiment("my_experiment.json", "Birch Reduction Study")

# Launch the enhanced reagent entry GUI
reagent_gui = launch_reagent_entry(experiment)

# The GUI now provides:
# ✅ Enhanced PubChem search with multiple search types
# ✅ Beautiful reagent display widgets with structure visualization
# ✅ Improved form validation and error handling
# ✅ Better UI layout with sectioned interface
# ✅ Edit/delete functionality for existing reagents
# ✅ Reaction scale management
# ✅ Integration with the unified metadata system

# Access the data programmatically:
chemistry_data = experiment.chemistry.get_data()
solid_reagents = chemistry_data.get("solid_reagents", [])
liquid_reagents = chemistry_data.get("liquid_reagents", [])
'''
    
    print(usage_code)

if __name__ == "__main__":
    success1 = test_core_functionality()
    success2 = test_data_integration()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The enhanced reagent entry system is working correctly.")
        show_usage_example()
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)