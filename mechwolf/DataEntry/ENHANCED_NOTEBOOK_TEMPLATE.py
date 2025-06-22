#!/usr/bin/env python3
"""
MechWolf Enhanced Notebook Template

This template demonstrates the new integrated workflow using the modernized
MechWolf DataEntry system. Copy this code into Jupyter notebook cells.

Key Features:
- Unified experimental metadata management
- Integrated pump configuration (no separate notebook needed)
- Modern phase-based workflow (ReagentEntry → ApparatusBuilder → ProtocolDev)
- Real-time validation and visualization
- Complete experiment tracking

Usage:
1. Copy each cell's code into separate Jupyter notebook cells
2. Run cells in sequence
3. Use the interactive GUIs to configure your experiment
4. Export final protocol code for execution
"""

# =============================================================================
# CELL 1: Experiment Setup and Initialization
# =============================================================================

# Import the unified experimental metadata system
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
from mechwolf.DataEntry.utilities import get_notebook_json_name
from mechwolf.DataEntry.shared_components import NotebookIntegration

# Create enhanced header
header = NotebookIntegration.create_section_header(
    "🧪 MechWolf Flow Chemistry Experiment",
    "Modernized workflow with integrated data management"
)
display(header)

# Initialize experiment
data_file = get_notebook_json_name()
experiment = ExperimentalMetadataManager(data_file, "Birch Reduction Experiment")

print(f"📊 Experiment: {experiment.get_experiment_name()}")
print(f"📁 Data file: {data_file}")
print(f"🆔 Experiment ID: {experiment.get_experiment_info()['experiment_id']}")

# Show workflow navigator
workflow_phases = [
    {"name": "Setup", "description": "Initialize experiment"},
    {"name": "Reagents", "description": "Configure chemistry"},
    {"name": "Apparatus", "description": "Build apparatus & configure pumps"},
    {"name": "Protocol", "description": "Develop protocol"},
    {"name": "Execute", "description": "Run experiment"}
]

navigator = NotebookIntegration.create_workflow_navigator(workflow_phases, current_phase=0)
display(navigator)

# =============================================================================
# CELL 2: Hardware Discovery (Optional)
# =============================================================================

# Optional: Discover available hardware
info_box = NotebookIntegration.create_info_box(
    "💡 <strong>Hardware Discovery</strong><br>"
    "This step helps identify available serial ports and hardware before configuration.",
    "info"
)
display(info_box)

from mechwolf.DataEntry.utilities import SerialPortViewer

# Launch serial port viewer
port_viewer = SerialPortViewer()
port_viewer.run()

# =============================================================================
# CELL 3: Phase 1 - Reagent Entry
# =============================================================================

import Phase1_ReagentEntry

# Create phase header
phase1_header = NotebookIntegration.create_section_header(
    "🧱 Phase 1: Reagent Entry",
    "Configure reagents, stoichiometry, and reaction conditions",
    "135deg, #4facfe 0%, #00f2fe 100%"
)
display(phase1_header)

# Launch reagent entry interface
reagent_gui = Phase1_ReagentEntry.launch_gui(experiment)

# The GUI will be displayed below this cell
# Use it to:
# 1. Add solid and liquid reagents
# 2. Set molecular weights and equivalents
# 3. Configure reaction scale
# 4. Set limiting reagent

print("✅ Use the interface above to configure your reagents")
print("💡 Pro tip: Use the PubChem lookup for automatic molecular data")

# =============================================================================
# CELL 4: Phase 2 - Integrated Apparatus & Pump Builder
# =============================================================================

import Phase2_ApparatusBuilder

# Create phase header
phase2_header = NotebookIntegration.create_section_header(
    "⚙️ Phase 2: Apparatus & Pump Configuration", 
    "Build apparatus and configure pumps in one integrated workflow",
    "135deg, #667eea 0%, #764ba2 100%"
)
display(phase2_header)

# Key innovation info
innovation_box = NotebookIntegration.create_info_box(
    "🎯 <strong>Key Innovation</strong><br>"
    "This interface combines pump configuration with apparatus building, "
    "eliminating the need for separate pump code generation notebooks!",
    "success"
)
display(innovation_box)

# Launch integrated apparatus builder
apparatus_gui = Phase2_ApparatusBuilder.launch_gui(experiment)

# The GUI provides:
# 1. Visual pump configuration with serial port selection
# 2. Component configuration (vessels, tubes, mixers)
# 3. Connection building with validation
# 4. Real-time apparatus visualization
# 5. Automatic code generation

print("✅ Use the tabbed interface above to:")
print("   🔧 Configure pumps (replaces separate pump notebook)")
print("   📦 Add apparatus components") 
print("   🔗 Build connections")
print("   ✅ Validate configuration")
print("   💾 Export code")

# =============================================================================
# CELL 5: Get Configured Objects
# =============================================================================

# After using the apparatus builder GUI above, run this cell to get the objects

# Get configured pumps and apparatus
pumps = apparatus_gui.get_configured_pumps()
A = apparatus_gui.get_apparatus()

if A:
    print("✅ Apparatus created successfully!")
    print(f"📊 Apparatus: {A.name}")
    print(f"🔗 Components: {len(A.components)}")
    
    # Display apparatus summary
    A.describe()
    
    # Show available pumps
    if pumps:
        print(f"\n🔧 Configured pumps: {list(pumps.keys())}")
    else:
        print("\n⚠️ No pumps configured - check Phase 2 configuration")
else:
    print("❌ No apparatus created - please complete Phase 2 configuration")

# =============================================================================
# CELL 6: Phase 3 - Protocol Development
# =============================================================================

import Phase3_ProtocolDev
import mechwolf as mw

# Create phase header
phase3_header = NotebookIntegration.create_section_header(
    "📋 Phase 3: Protocol Development",
    "Build, validate, and simulate your experimental protocol",
    "135deg, #8e24aa 0%, #3f51b5 100%"
)
display(phase3_header)

# Create protocol from apparatus
if A:
    P = mw.Protocol(A)
    print("✅ Protocol initialized with apparatus")
else:
    print("❌ Cannot create protocol - apparatus not available")
    print("💡 Complete Phase 2 first")

# Launch protocol development interface
if A:
    protocol_gui = Phase3_ProtocolDev.launch_gui(experiment, protocol=P, pumps=pumps)
    
    print("✅ Use the interface above to:")
    print("   🔧 Build procedures with drag-and-drop interface")
    print("   📅 View timeline and concurrent operations")
    print("   ✅ Validate using MechWolf core")
    print("   🧪 Run simulations and dry runs")

# =============================================================================
# CELL 7: Protocol Validation & Code Generation
# =============================================================================

# After building protocol in Phase 3, get the validated protocol
try:
    P_validated = Phase3_ProtocolDev.get_validated_protocol(experiment, A)
    
    if P_validated:
        print("✅ Protocol validated successfully!")
        
        # Display protocol summary
        print("\n📋 PROTOCOL SUMMARY")
        print("=" * 50)
        print(f"Protocol: {P_validated.name}")
        print(f"Apparatus: {P_validated.apparatus.name}")
        print(f"Procedures: {len(P_validated.procedure_list)}")
        
        # Visualize protocol
        print("\n📊 Protocol Visualization:")
        P_validated.visualize(renderer='default')
        
    else:
        print("⚠️ No validated protocol available")
        print("💡 Complete protocol configuration in Phase 3")
        
except Exception as e:
    print(f"Note: Protocol validation requires completing Phase 3: {e}")

# =============================================================================
# CELL 8: Protocol Execution
# =============================================================================

execution_header = NotebookIntegration.create_section_header(
    "▶️ Protocol Execution",
    "Execute your validated protocol",
    "135deg, #4caf50 0%, #45a049 100%"
)
display(execution_header)

# Safety warning
safety_box = NotebookIntegration.create_info_box(
    "🛡️ <strong>Safety First</strong><br>"
    "Always run a dry run before actual execution. Ensure all safety measures are in place.",
    "warning"  
)
display(safety_box)

# Execute protocol (after completing all phases)
if 'P_validated' in locals() and P_validated:
    print("🧪 Running dry run first...")
    try:
        dry_run_result = P_validated.execute(dry_run=1000)
        print("✅ Dry run completed successfully!")
        
        # Execute actual protocol (uncomment when ready)
        print("\n⚠️ Ready for actual execution!")
        print("💡 Uncomment the line below when ready:")
        print("# executed_experiment = P_validated.execute()")
        
        # executed_experiment = P_validated.execute()
        # print("✅ Protocol execution completed!")
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        print("💡 Check protocol configuration and hardware connections")
        
else:
    print("❌ No validated protocol available for execution")
    print("💡 Complete all previous phases first")

# =============================================================================
# CELL 9: Analysis & Results
# =============================================================================

analysis_header = NotebookIntegration.create_section_header(
    "📊 Analysis & Results",
    "Record analysis data and results",
    "135deg, #ff6b6b 0%, #ee5a6f 100%"
)
display(analysis_header)

# Add TLC analysis
from mechwolf.DataEntry.utilities import TLCInputForm

tlc_form = TLCInputForm(experiment)
tlc_form.run()

# Add other analysis data through experimental metadata
print("💡 You can also add analysis data programmatically:")
print()
print("# Add NMR data")
print("experiment.analysis.add_nmr_data({")
print("    'nucleus': '1H',")
print("    'frequency': '400 MHz',") 
print("    'solvent': 'CDCl3',")
print("    'file_path': 'nmr_spectrum.fid'")
print("})")
print()
print("# Add yield data")
print("experiment.analysis.set_yield_data({")
print("    'theoretical_yield': 120.0,  # mg")
print("    'actual_yield': 95.5,        # mg") 
print("    'purity': 92.3               # %")
print("})")

# =============================================================================
# CELL 10: Experiment Summary & Export
# =============================================================================

summary_header = NotebookIntegration.create_section_header(
    "📋 Experiment Summary",
    "View complete experiment data and export results",
    "135deg, #6c5ce7 0%, #a29bfe 100%"
)
display(summary_header)

# Create data summary widget
summary_widget = NotebookIntegration.create_data_summary_widget(experiment)
display(summary_widget)

# Create export widget
export_widget = NotebookIntegration.create_export_widget(experiment)
display(export_widget)

# Print final summary
print("\n🎉 EXPERIMENT COMPLETE!")
print("=" * 50)
print(experiment.get_summary())

print("\n💾 All data has been automatically saved to:")
print(f"   📁 {experiment.json_file}")

print("\n✨ Benefits of the new system:")
print("   ✅ Unified data management - no more scattered JSON files")
print("   ✅ Integrated pump configuration - no separate notebooks")  
print("   ✅ Real-time validation and error checking")
print("   ✅ Modern, interactive interfaces")
print("   ✅ Complete experiment tracking and reproducibility")
print("   ✅ Seamless MechWolf core integration")

# =============================================================================
# END OF ENHANCED NOTEBOOK TEMPLATE
# =============================================================================