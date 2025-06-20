#!/usr/bin/env python3
"""
Usage Example - Unified Experimental Metadata System

This example shows how to use the new unified system with reagent data
from the preceding Jupyter notebook, then add apparatus configuration
and protocol development.
"""

from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory

def example_workflow():
    """Example workflow showing complete experiment setup"""
    
    print("🧪 Creating new experiment with reagent data...")
    
    # 1. Create experiment (this replaces the old separate JSON files)
    experiment = ExperimentalMetadataManager("birch_reduction_experiment.json", "Birch Reduction")
    
    # 2. Add reagent data (this would come from your preceding notebook)
    reagent_data = {
        "mass_scale": 0.14,
        "concentration": 0.2,
        "solvent": "THF",
        "limiting_reagent": "Benzyalted diacetone-D-glucose",
        "solid_reagents": [
            {
                "name": "Benzyalted diacetone-D-glucose",
                "inChi": "InChI=1S/C19H26O6/c1-18(2)21-11-13(23-18)14-15(20-10-12-8-6-5-7-9-12)16-17(22-14)25-19(3,4)24-16/h5-9,13-17H,10-11H2,1-4H3/t13-,14-,15+,16-,17-/m1/s1",
                "inChi_Key": "ZHFVGOMEUGAIJX-NQNKBUKLSA-N",
                "molecular_weight": 350.41,
                "eq": 1,
                "mass": 0.14,
                "position": 5
            },
            {
                "name": "Lithium",
                "inChi": "InChI=1S/Li",
                "inChi_Key": "WHXSMMKQMYFTQS-UHFFFAOYSA-N",
                "molecular_weight": 6.94,
                "eq": None,
                "mass": 0.035,
                "position": None
            }
        ],
        "liquid_reagents": [
            {
                "name": "tert-butanol",
                "inChi": "InChI=1S/C4H10O/c1-4(2,3)5/h5H,1-3H3",
                "inChi_Key": "DKGAVHZHDRPRBM-UHFFFAOYSA-N",
                "molecular_weight": 74.12,
                "eq": 1,
                "volume": None,
                "density": 0.775,
                "position": 5
            },
            {
                "name": "ethane-1,2-diamine",
                "inChi": "InChI=1S/C2H8N2/c3-1-2-4/h1-4H2",
                "inChi_Key": "PIICEJLVQHRZGT-UHFFFAOYSA-N",
                "molecular_weight": 60.10,
                "eq": None,
                "volume": 5,
                "density": 0.899,
                "position": 4
            }
        ],
        "solvent_volume": [5, 2]
    }
    
    # Add chemistry data to experiment
    experiment.chemistry.update_reagents(reagent_data)
    experiment.chemistry.set_reaction_scale(
        mass_scale=reagent_data["mass_scale"],
        concentration=reagent_data["concentration"],
        solvent=reagent_data["solvent"]
    )
    experiment.chemistry.set_limiting_reagent(reagent_data["limiting_reagent"])
    
    print("✅ Chemistry data added")
    
    # 3. Configure apparatus (this would be done through GUI or programmatically)
    print("\n⚙️  Configuring apparatus...")
    
    # Add components
    experiment.apparatus.add_active_component({
        "type": "VarianPump",
        "name": "Li_activator_pump",
        "serial_port": "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A106H6YE-if00-port0",
        "parameters": {"max_rate": "25mL/min"}
    })
    
    experiment.apparatus.add_active_component({
        "type": "ViciValve", 
        "name": "reagent_valve",
        "serial_port": "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0",
        "parameters": {
            "mapping": {
                "THF": 1,
                "SM": 2,
                "Li": 3
            }
        }
    })
    
    # Add passive components
    for vessel_name, description in [
        ("THF", "Tetrahydrofuran"),
        ("SM", "Starting_material_and_tbutanol_THF"),
        ("Li", "Li_ammonia_THF"),
        ("product_vessel", "Product collection vessel")
    ]:
        experiment.apparatus.add_passive_component({
            "type": "Vessel",
            "name": vessel_name,
            "parameters": {"description": description}
        })
    
    # Add tubes
    for tube_name, length, id_val, od_val in [
        ("fat_tube_1ft", "1 ft", "1/16 in", "1/8 in"),
        ("valve_tube", "6 in", "0.030 in", "1/16 in"),
        ("product_tube", "2 ft", "1/16 in", "1/8 in")
    ]:
        experiment.apparatus.add_passive_component({
            "type": "Tube",
            "name": tube_name,
            "parameters": {
                "length": length,
                "ID": id_val,
                "OD": od_val,
                "material": "PFA"
            }
        })
    
    # Add connections
    connections = [
        {"from": "THF", "to": "reagent_valve", "tube": "fat_tube_1ft"},
        {"from": "reagent_valve", "to": "Li_activator_pump", "tube": "valve_tube"},
        {"from": "Li_activator_pump", "to": "product_vessel", "tube": "product_tube"}
    ]
    
    for conn in connections:
        experiment.apparatus.add_connection(conn)
    
    experiment.apparatus.set_apparatus_info("Birch_Reduction_Apparatus", "Birch reduction flow chemistry setup")
    
    print("✅ Apparatus configured")
    
    # 4. Add protocol (this would be done through ProtocolDev GUI)
    print("\n📋 Adding protocol...")
    
    experiment.protocol.set_protocol_info("Birch_Reduction_Protocol", "Standard Birch reduction procedure")
    
    procedures = [
        {
            "component": "reagent_valve",
            "action": "switch",
            "start_time": "0s",
            "parameters": {"position": "THF"}
        },
        {
            "component": "Li_activator_pump",
            "action": "run",
            "start_time": "5s",
            "duration": "10min",
            "parameters": {"rate": "5 mL/min"}
        },
        {
            "component": "reagent_valve",
            "action": "switch", 
            "start_time": "10min 5s",
            "parameters": {"position": "Li"}
        },
        {
            "component": "Li_activator_pump",
            "action": "run",
            "start_time": "10min 10s",
            "duration": "5min",
            "parameters": {"rate": "2 mL/min"}
        }
    ]
    
    experiment.protocol.load_procedures_from_list(procedures)
    
    print("✅ Protocol added")
    
    # 5. Save complete experiment
    experiment.save()
    print(f"\n💾 Complete experiment saved to: {experiment.json_file}")
    
    # 6. Create apparatus for execution
    print("\n🔧 Creating MechWolf apparatus...")
    
    try:
        A = ApparatusFactory.create_apparatus_from_experiment(experiment, "Birch_Reduction")
        print(f"✅ Apparatus created: {A.name}")
        print(f"   Components: {len(A.components)}")
        
        # Now you can create protocols and execute
        import mechwolf as mw
        P = mw.Protocol(A)
        P.add(Li_activator_pump, start='0s', duration='10min', rate='5 mL/min')
        
        print("✅ Protocol ready for execution!")
        
    except Exception as e:
        print(f"⚠️  Apparatus creation failed: {e}")
        print("   (This is expected if MechWolf dependencies are not available)")
    
    # 7. Show experiment summary
    print("\n📊 Experiment Summary:")
    print(experiment.get_summary())
    
    return experiment

def example_loading_existing():
    """Example of loading and modifying existing experiment"""
    
    print("\n🔄 Loading existing experiment...")
    
    try:
        # Load existing experiment
        experiment = ExperimentalMetadataManager("birch_reduction_experiment.json")
        
        print(f"✅ Loaded experiment: {experiment.get_experiment_name()}")
        
        # Add analysis data (e.g., from TLC or NMR)
        experiment.analysis.add_tlc_plate({
            "solvent_system": "hexanes:ethyl acetate 3:1",
            "observations": "Product spot visible under UV at Rf 0.3"
        })
        
        experiment.analysis.update_rf_values({
            "starting_material": 0.6,
            "product": 0.3
        })
        
        experiment.analysis.set_yield_data({
            "theoretical_yield": 120.0,  # mg
            "actual_yield": 95.5,        # mg
            "purity": 92.3               # %
        })
        
        print("✅ Analysis data added")
        
        # Save updates
        experiment.save()
        
        # Show updated summary
        print("\n📊 Updated Experiment Summary:")
        print(experiment.get_summary())
        
        return experiment
        
    except FileNotFoundError:
        print("❌ Experiment file not found. Run example_workflow() first.")
        return None

def example_migration():
    """Example of migrating legacy files"""
    
    print("\n🔄 Migration Example...")
    
    # This would migrate your existing reagent JSON files
    # to the new unified format
    
    from mechwolf.DataEntry.experimental_metadata import convert_reagent_json
    
    # Example legacy reagent data
    legacy_data = {
        "mass scale": 0.14,
        "concentration": 0.2,
        "solvent": "THF",
        "solid reagents": [
            {
                "name": "Test Reagent",
                "molecular weight": 100.0,
                "eq": 1.0
            }
        ],
        "liquid reagents": []
    }
    
    # Convert to unified format
    unified_data = convert_reagent_json(legacy_data, "Migrated Experiment")
    
    print("✅ Legacy data converted to unified format")
    print(f"   New experiment ID: {unified_data['mechwolf_experiment']['experiment_id']}")
    
    return unified_data

if __name__ == "__main__":
    print("🧪 MechWolf Unified Experimental Metadata - Usage Examples")
    print("=" * 60)
    
    # Run examples
    experiment = example_workflow()
    
    if experiment:
        example_loading_existing()
    
    example_migration()
    
    print("\n🎉 Examples completed!")
    print("\nNext steps:")
    print("1. Use the experiment file in your Jupyter notebooks")
    print("2. Add apparatus configuration through FlowSetups_New GUI")
    print("3. Develop protocols through ProtocolDev")
    print("4. Add analysis data as you collect results")
    print("5. Export summaries for reports and documentation")