# 🛠️ Experimental Metadata Developer Guide

**Complete guide for developing with the unified experimental metadata system**

## 📖 Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Working with Each Section](#working-with-each-section)
4. [Adding New Features](#adding-new-features)
5. [Migration from Legacy Systems](#migration-from-legacy-systems)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Basic Usage
```python
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager

# Create new experiment
experiment = ExperimentalMetadataManager("my_experiment.json", "Birch Reduction")

# Or load existing experiment
experiment = ExperimentalMetadataManager("existing_experiment.json")

# Work with different sections
experiment.chemistry.add_solid_reagent({
    "name": "Starting Material",
    "molecular_weight": 150.2,
    "mass": 100.0,
    "eq": 1.0
})

experiment.apparatus.add_active_component({
    "type": "VarianPump",
    "name": "pump1",
    "serial_port": "/dev/ttyUSB0",
    "parameters": {"max_rate": "10 mL/min"}
})

# Save changes
experiment.save()
```

### Creating Apparatus from Experiment
```python
from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory

# Create apparatus directly from experiment metadata
A = ApparatusFactory.create_apparatus_from_experiment(experiment)

# Or from file (automatically detects unified format)
A = ApparatusFactory.create_apparatus_from_config("my_experiment.json")
```

---

## 🏗️ Architecture Overview

### Core Components

```
experimental_metadata/
├── experimental_metadata_manager.py  # Main coordinator
├── chemistry_manager.py             # Reagent management
├── apparatus_manager.py              # Component management  
├── protocol_manager.py               # Protocol management
├── analysis_manager.py               # Analysis data management
├── schema_definitions.py             # JSON schemas
└── migration_utilities.py            # Legacy migration
```

### Data Structure
```json
{
  "mechwolf_experiment": {
    "version": "3.0.0",
    "experiment_id": "2024_06_19_14_30_45_ABC123",
    "experiment_name": "Birch Reduction",
    "created": "2024-06-19T14:30:45Z"
  },
  "chemistry": { /* reagents, stoichiometry */ },
  "apparatus_config": { /* components, connections */ },
  "protocol_config": { /* procedures, timing */ },
  "experiment_execution": { /* runtime data */ },
  "analysis": { /* TLC, NMR, yields */ }
}
```

---

## 🧪 Working with Each Section

### 1. Chemistry Management

#### Adding Reagents
```python
# Solid reagent
experiment.chemistry.add_solid_reagent({
    "name": "Lithium",
    "inChi": "InChI=1S/Li",
    "molecular_weight": 6.94,
    "eq": 3.0,
    "mass": 20.8,
    "position": 1
})

# Liquid reagent
experiment.chemistry.add_liquid_reagent({
    "name": "THF",
    "molecular_weight": 72.11,
    "density": 0.889,
    "volume": 50.0,
    "position": 2
})
```

#### Reaction Conditions
```python
# Set overall reaction scale
experiment.chemistry.set_reaction_scale(
    mass_scale=100.0,  # mg
    concentration=0.2,  # M
    solvent="THF"
)

# Set limiting reagent
experiment.chemistry.set_limiting_reagent("Starting_Material")
```

#### Bulk Operations
```python
# Update multiple reagents at once
reagents = {
    "solid_reagents": [...],
    "liquid_reagents": [...]
}
experiment.chemistry.update_reagents(reagents)

# Calculate masses from stoichiometry
masses = experiment.chemistry.calculate_masses_from_scale()
```

### 2. Apparatus Management

#### Adding Components
```python
# Active component (pump)
experiment.apparatus.add_active_component({
    "type": "VarianPump",
    "name": "Li_pump",
    "serial_port": "/dev/ttyUSB0",
    "parameters": {
        "max_rate": "25 mL/min"
    }
})

# Passive component (vessel)
experiment.apparatus.add_passive_component({
    "type": "Vessel",
    "name": "THF_vessel",
    "parameters": {
        "description": "THF solvent reservoir"
    }
})
```

#### Managing Connections
```python
# Add connection
experiment.apparatus.add_connection({
    "from": "THF_vessel",
    "to": "Li_pump",
    "tube": "connecting_tube",
    "from_type": "Vessel",
    "to_type": "VarianPump"
})

# Remove connection
experiment.apparatus.remove_connection("THF_vessel", "Li_pump")
```

#### Bulk Configuration
```python
# Configure all components at once
components = {
    "active": [pump1_config, valve1_config],
    "passive": [vessel1_config, tube1_config]
}
experiment.apparatus.configure_components(components)
```

### 3. Protocol Management

#### Adding Procedures
```python
# Add individual procedure
experiment.protocol.add_procedure({
    "component": "Li_pump",
    "action": "run",
    "start_time": "0s",
    "duration": "10min",
    "parameters": {
        "rate": "5 mL/min"
    }
})

# Insert at specific position
experiment.protocol.insert_procedure(1, {
    "component": "valve1",
    "action": "switch",
    "parameters": {"position": "Li_source"}
})
```

#### Protocol Information
```python
# Set protocol metadata
experiment.protocol.set_protocol_info(
    name="Birch Reduction Protocol",
    description="Standard Birch reduction procedure"
)

# Add global parameters
experiment.protocol.set_global_parameters({
    "temperature": "25°C",
    "pressure": "1 atm"
})
```

#### Bulk Operations
```python
# Load procedures from list
procedures = [
    {"component": "pump1", "action": "start", "duration": "5min"},
    {"component": "valve1", "action": "switch", "parameters": {...}}
]
experiment.protocol.load_procedures_from_list(procedures)
```

### 4. Analysis Management

#### TLC Data
```python
# Add TLC plate
experiment.analysis.add_tlc_plate({
    "solvent_system": "hexanes:ethyl acetate 3:1",
    "observations": "Product spot visible under UV"
})

# Update Rf values
experiment.analysis.update_rf_values({
    "starting_material": 0.6,
    "product": 0.3
})
```

#### Spectroscopy Data
```python
# Add NMR data
experiment.analysis.add_nmr_data({
    "nucleus": "1H",
    "frequency": "400 MHz",
    "solvent": "CDCl3",
    "file_path": "nmr_spectrum.fid"
})

# Add MS data
experiment.analysis.add_ms_data({
    "method": "ESI-MS",
    "molecular_ion": 182.5,
    "file_path": "ms_spectrum.raw"
})
```

#### Yield Data
```python
# Set yield information
experiment.analysis.set_yield_data({
    "theoretical_yield": 150.0,  # mg
    "actual_yield": 127.5,       # mg
    "purity": 95.2,              # %
    "method": "isolated yield"
})
```

---

## ➕ Adding New Features

### 1. Adding New Analysis Types

```python
# In analysis_manager.py, add new method:
def add_gc_analysis(self, gc_data: Dict[str, Any]) -> bool:
    """Add GC analysis data"""
    data = self.get_data()
    if "chromatography" not in data:
        data["chromatography"] = {}
    if "gc" not in data["chromatography"]:
        data["chromatography"]["gc"] = []
    
    gc_data["timestamp"] = get_current_timestamp()
    data["chromatography"]["gc"].append(gc_data)
    return self.save_data(data)
```

### 2. Adding New Component Types

```python
# In apparatus_manager.py, add validation:
def add_custom_component(self, component: Dict[str, Any]) -> bool:
    """Add custom component type with specific validation"""
    
    # Custom validation for your component type
    if component.get("type") == "CustomPump":
        required_params = ["flow_range", "pressure_rating"]
        for param in required_params:
            if param not in component.get("parameters", {}):
                print(f"❌ CustomPump missing required parameter: {param}")
                return False
    
    # Use existing add methods
    if component.get("category") == "active":
        return self.add_active_component(component)
    else:
        return self.add_passive_component(component)
```

### 3. Extending Schema Validation

```python
# In schema_definitions.py, update UNIFIED_SCHEMA:
"my_new_section": {
    "type": "object",
    "properties": {
        "schema_version": {"type": "string", "default": "1.0.0"},
        "custom_field": {"type": "string"},
        "custom_array": {
            "type": "array",
            "items": {"type": "object"}
        }
    }
}

# Add to DEFAULT_EXPERIMENT_METADATA:
"my_new_section": {
    "schema_version": "1.0.0",
    "custom_field": "",
    "custom_array": []
}
```

### 4. Creating New Manager Classes

```python
# Create new_feature_manager.py:
from typing import Dict, Any
from .schema_definitions import get_current_timestamp

class NewFeatureManager:
    def __init__(self, metadata_manager):
        self.metadata_manager = metadata_manager
        self.section_name = "my_new_section"
    
    def get_data(self) -> Dict[str, Any]:
        return self.metadata_manager.get_section_data(self.section_name)
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        return self.metadata_manager.update_section_data(self.section_name, data)
    
    def add_feature_data(self, feature_data: Dict[str, Any]) -> bool:
        data = self.get_data()
        # Your custom logic here
        return self.save_data(data)

# Add to ExperimentalMetadataManager.__init__():
self.new_feature = NewFeatureManager(self)
```

---

## 🔄 Migration from Legacy Systems

### Automatic Migration
```python
from mechwolf.DataEntry.experimental_metadata import migrate_legacy_files

# Migrate all legacy files in a directory
migrated_files = migrate_legacy_files(
    source_directory="./legacy_data",
    output_directory="./migrated_data"
)

print(f"Migrated {len(migrated_files)} files")
```

### Manual Migration
```python
from mechwolf.DataEntry.experimental_metadata import (
    convert_reagent_json,
    convert_apparatus_json,
    convert_protocol_json
)

# Convert specific file types
with open("old_reagents.json", 'r') as f:
    old_data = json.load(f)

unified_data = convert_reagent_json(old_data, "My Experiment")

with open("new_experiment.json", 'w') as f:
    json.dump(unified_data, f, indent=4)
```

### Updating Import Statements
```python
from mechwolf.DataEntry.experimental_metadata import update_legacy_imports

# Update Python files to use new imports
success = update_legacy_imports("my_script.py", backup=True)
```

---

## ✅ Best Practices

### 1. Data Management
- **Always save after modifications**: Use `experiment.save()` frequently
- **Use section managers**: Don't manipulate JSON directly
- **Validate data**: Use built-in validation methods
- **Create backups**: Backups are created automatically on save

### 2. Error Handling
```python
try:
    experiment = ExperimentalMetadataManager("experiment.json")
    success = experiment.chemistry.add_solid_reagent(reagent_data)
    if not success:
        print("Failed to add reagent - check validation errors")
    experiment.save()
except Exception as e:
    print(f"Error: {e}")
```

### 3. Performance
- **Batch operations**: Use bulk methods for multiple changes
- **Load once**: Keep experiment object in memory during session
- **Validate periodically**: Run validation after major changes

### 4. Schema Evolution
```python
# Always specify schema versions for new sections
data["my_section"]["schema_version"] = "1.0.0"

# Handle version migrations gracefully
if data.get("schema_version", "1.0.0") < "2.0.0":
    data = migrate_to_v2(data)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Schema Validation Errors
```python
# Check validation errors
errors = experiment.validate_all_sections()
if errors:
    for section, section_errors in errors.items():
        print(f"Errors in {section}:")
        for error in section_errors:
            print(f"  - {error}")
```

#### 2. Missing Components
```python
# Verify all components exist before adding connections
all_components = experiment.apparatus.get_all_component_names()
print(f"Available components: {all_components}")

# Check for invalid connections
issues = experiment.apparatus.validate_apparatus()
if issues:
    print("Apparatus issues:", issues)
```

#### 3. Migration Problems
```python
# Validate migration results
from mechwolf.DataEntry.experimental_metadata import validate_migration

validation = validate_migration("old_file.json", "new_file.json")
print(f"Migration status: {validation['status']}")
if validation['issues']:
    print("Issues:", validation['issues'])
```

### Debug Utilities

```python
# Get comprehensive experiment summary
print(experiment.get_summary())

# Export individual sections for inspection
experiment.export_section("chemistry", "chemistry_debug.json")

# Check file structure
info = experiment.get_experiment_info()
print(f"Experiment ID: {info['experiment_id']}")
print(f"Created: {info['created']}")
```

### Performance Monitoring

```python
import time

start_time = time.time()

# Your operations here
experiment.chemistry.add_solid_reagent(reagent)
experiment.apparatus.add_active_component(component)
experiment.save()

elapsed = time.time() - start_time
print(f"Operations took {elapsed:.2f} seconds")
```

---

## 📚 Advanced Examples

### Complex Experiment Setup
```python
# Create comprehensive experiment
experiment = ExperimentalMetadataManager("birch_reduction.json", "Birch Reduction")

# Add multiple reagents
reagents = [
    {"name": "Starting Material", "molecular_weight": 150.2, "eq": 1.0},
    {"name": "Lithium", "molecular_weight": 6.94, "eq": 3.0},
    {"name": "Ammonia", "molecular_weight": 17.03, "eq": 10.0}
]

for reagent in reagents:
    experiment.chemistry.add_solid_reagent(reagent)

# Configure apparatus
components = {
    "active": [
        {"type": "VarianPump", "name": "Li_pump", "serial_port": "/dev/ttyUSB0"},
        {"type": "ViciValve", "name": "reagent_valve", "serial_port": "/dev/ttyUSB1"}
    ],
    "passive": [
        {"type": "Vessel", "name": "THF", "parameters": {"description": "THF reservoir"}},
        {"type": "Vessel", "name": "product", "parameters": {"description": "Product vessel"}}
    ]
}

experiment.apparatus.configure_components(components)

# Add connections
connections = [
    {"from": "THF", "to": "reagent_valve", "tube": "inlet_tube"},
    {"from": "reagent_valve", "to": "Li_pump", "tube": "pump_tube"},
    {"from": "Li_pump", "to": "product", "tube": "outlet_tube"}
]

for conn in connections:
    experiment.apparatus.add_connection(conn)

# Define protocol
procedures = [
    {"component": "reagent_valve", "action": "switch", "parameters": {"position": "THF"}},
    {"component": "Li_pump", "action": "run", "duration": "10min", "parameters": {"rate": "5 mL/min"}},
    {"component": "reagent_valve", "action": "switch", "parameters": {"position": "closed"}}
]

experiment.protocol.load_procedures_from_list(procedures)

# Save everything
experiment.save()
print("✅ Complete experiment setup saved!")
```

### Integration with Existing Code
```python
# Use with existing FlowSetups_New factory
from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory

# Create apparatus from unified metadata
A = ApparatusFactory.create_apparatus_from_experiment(experiment)

# Create protocol
P = mw.Protocol(A)
P.add(Li_pump, start='0s', duration='10min', rate='5 mL/min')

# Execute experiment
executed_experiment = P.execute()

# Store execution results back in metadata
execution_data = {
    "start_time": executed_experiment.start_time,
    "end_time": executed_experiment.end_time,
    "status": "completed",
    "experiment_id": executed_experiment.experiment_id
}

experiment.update_section_data("experiment_execution", execution_data)
experiment.save()
```

---

This guide provides everything you need to work with the unified experimental metadata system. For additional help, see the inline documentation in each module or create an issue in the repository.

**Happy experimenting! 🧪✨**