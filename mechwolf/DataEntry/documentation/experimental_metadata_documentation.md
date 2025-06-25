# MechWolf Experimental Metadata System - LLM Reference Guide

## Overview

The MechWolf Experimental Metadata system is a unified JSON-based data management framework for flow chemistry experiments. It consolidates reagent data, apparatus configurations, protocol procedures, and analytical results into a single, version-controlled metadata structure.

**Version:** 3.0.0  
**Location:** `/mechwolf/DataEntry/experimental_metadata/`  
**Main Entry Point:** `ExperimentalMetadataManager` class

## Core Architecture

### 1. Unified Data Structure

The experimental metadata follows a hierarchical JSON schema with six main sections:

```json
{
  "mechwolf_experiment": {
    "experiment_id": "unique-identifier",
    "experiment_name": "Human readable name",
    "created": "ISO timestamp",
    "last_updated": "ISO timestamp",
    "version": "3.0.0",
    "description": "Experiment description",
    "notebook_file": "path/to/notebook.ipynb"
  },
  "chemistry": { /* Chemical data */ },
  "apparatus_config": { /* Hardware configuration */ },
  "protocol_config": { /* Protocol procedures */ },
  "experiment_execution": { /* Runtime data */ },
  "analysis": { /* Analytical results */ }
}
```

### 2. Manager Classes

Each section is managed by a dedicated class:

- **`ExperimentalMetadataManager`** - Main coordinator class
- **`ChemistryDataManager`** - Handles reagents and reaction conditions
- **`ApparatusDataManager`** - Manages hardware components and connections
- **`ProtocolDataManager`** - Controls protocol procedures and timing
- **`AnalysisDataManager`** - Processes analytical data and results

## Key File Locations

### Core System Files
- `__init__.py` - Package initialization and main imports
- `experimental_metadata_manager.py` - Main coordinator class
- `schema_definitions.py` - JSON schema definitions and validation rules

### Manager Classes
- `chemistry_manager.py` - Chemical data management
- `apparatus_manager.py` - Hardware configuration management
- `protocol_manager.py` - Protocol development and validation
- `analysis_manager.py` - Analytical data processing

### Integration Points
- `data_adapter.py` - Legacy format compatibility adapter
- `migration_utilities.py` - Legacy data migration tools
- `apparatus_factory.py` - MechWolf Apparatus object creation

### Templates and Examples
- `USAGE_EXAMPLE.py` - Complete workflow demonstration
- `ENHANCED_NOTEBOOK_TEMPLATE.py` - Jupyter notebook template

## Data Sections Reference

### 1. Chemistry Section (`chemistry`)

**Purpose:** Store reagent information, stoichiometry, and reaction conditions

**Key Fields:**
```json
{
  "solid_reagents": [
    {
      "reagent_id": "unique-id",
      "name": "Reagent Name",
      "molecular_weight": 123.45,
      "mass": 0.100,
      "moles": 0.00081,
      "equivalents": 1.0,
      "cas_number": "123-45-6",
      "role": "substrate|reagent|catalyst|base|acid"
    }
  ],
  "liquid_reagents": [
    {
      "reagent_id": "unique-id",
      "name": "Liquid Reagent",
      "molecular_weight": 78.11,
      "density": 0.789,
      "volume": 1.0,
      "concentration": 0.5,
      "cas_number": "64-17-5"
    }
  ],
  "mass_scale": 0.100,
  "concentration": 0.1,
  "solvent": "THF",
  "limiting_reagent": "reagent-id",
  "solvent_volume": [
    {"solvent": "THF", "volume": 10.0, "unit": "mL"}
  ]
}
```

**Key Methods:**
- `add_solid_reagent(reagent_data)` - Add solid reagent
- `add_liquid_reagent(reagent_data)` - Add liquid reagent
- `set_reaction_scale(mass_scale, concentration, solvent)` - Set reaction scale
- `calculate_stoichiometry()` - Calculate molar ratios

### 2. Apparatus Configuration Section (`apparatus_config`)

**Purpose:** Define hardware components, connections, and calibration data

**Key Fields:**
```json
{
  "components": {
    "active": {
      "pump_1": {
        "component_id": "pump_1",
        "type": "SyringePump",
        "manufacturer": "Harvard Apparatus",
        "model": "PHD Ultra",
        "parameters": {
          "syringe_volume": 10.0,
          "max_flow_rate": 5.0,
          "min_flow_rate": 0.01
        }
      }
    },
    "passive": {
      "tube_1": {
        "component_id": "tube_1",
        "type": "Tube",
        "length": 100.0,
        "inner_diameter": 0.8,
        "material": "PTFE"
      }
    }
  },
  "connections": [
    {
      "from_component": "pump_1",
      "from_port": "outlet",
      "to_component": "tube_1",
      "to_port": "inlet"
    }
  ],
  "calibration_data": {
    "pump_1": {
      "flow_rate_calibration": [
        {"set_point": 1.0, "actual": 0.98},
        {"set_point": 2.0, "actual": 1.97}
      ]
    }
  }
}
```

**Key Methods:**
- `add_active_component(component_data)` - Add active hardware component
- `add_passive_component(component_data)` - Add passive component
- `add_connection(connection_data)` - Connect components
- `validate_connections()` - Validate network topology

### 3. Protocol Configuration Section (`protocol_config`)

**Purpose:** Define protocol procedures, timing, and parameters

**Key Fields:**
```json
{
  "name": "My Flow Protocol",
  "description": "Flow synthesis protocol",
  "procedures": [
    {
      "procedure_id": "step_1",
      "name": "Prime System",
      "type": "prime",
      "parameters": {
        "component": "pump_1",
        "flow_rate": 1.0,
        "duration": 300,
        "volume": 5.0
      },
      "order": 1
    }
  ],
  "timing": {
    "total_runtime": 3600,
    "step_intervals": [300, 1800, 1500]
  }
}
```

**Key Methods:**
- `add_procedure(procedure_data)` - Add protocol step
- `set_protocol_info(name, description)` - Set protocol metadata
- `validate_protocol()` - Validate procedure order and parameters

### 4. Experiment Execution Section (`experiment_execution`)

**Purpose:** Store runtime data, sensor readings, and execution logs

**Key Fields:**
```json
{
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T11:30:00Z",
  "status": "completed|running|failed|paused",
  "sensor_data": [
    {
      "timestamp": "2024-01-15T10:31:00Z",
      "sensor": "pressure_sensor_1",
      "value": 2.5,
      "unit": "bar"
    }
  ],
  "executed_procedures": [
    {
      "procedure_id": "step_1",
      "start_time": "2024-01-15T10:30:00Z",
      "end_time": "2024-01-15T10:35:00Z",
      "status": "completed"
    }
  ],
  "errors": [],
  "logs": []
}
```

**Key Methods:**
- `start_experiment()` - Begin experiment execution
- `log_sensor_data(sensor_data)` - Record sensor readings
- `complete_procedure(procedure_id)` - Mark procedure complete

### 5. Analysis Section (`analysis`)

**Purpose:** Store analytical data, results, and characterization

**Key Fields:**
```json
{
  "tlc_data": [
    {
      "plate_id": "tlc_1",
      "solvent_system": "Hexane:EtOAc 7:3",
      "spots": [
        {
          "compound": "product",
          "rf_value": 0.45,
          "color": "yellow"
        }
      ]
    }
  ],
  "spectroscopy": {
    "nmr": [
      {
        "nucleus": "1H",
        "solvent": "CDCl3",
        "frequency": 400,
        "file_path": "spectra/1H_NMR.fid"
      }
    ]
  },
  "yield_data": {
    "theoretical_yield": 0.150,
    "actual_yield": 0.135,
    "percent_yield": 90.0,
    "purity": 95.0
  }
}
```

**Key Methods:**
- `add_tlc_plate(tlc_data)` - Add TLC analysis
- `add_nmr_data(nmr_data)` - Add NMR spectrum
- `set_yield_data(yield_data)` - Record yield and purity

## Common Usage Patterns

### Creating a New Experiment

```python
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager

# Create new experiment
experiment = ExperimentalMetadataManager(
    filename="my_experiment.json",
    experiment_name="Flow Synthesis Example"
)

# Add chemistry data
experiment.chemistry.add_solid_reagent({
    "name": "Benzoic Acid",
    "molecular_weight": 122.12,
    "mass": 0.100,
    "cas_number": "65-85-0",
    "role": "substrate"
})

# Configure apparatus
experiment.apparatus.add_active_component({
    "component_id": "pump_1",
    "type": "SyringePump",
    "parameters": {"syringe_volume": 10.0}
})

# Save experiment
experiment.save()
```

### Loading Existing Experiment

```python
# Load existing experiment
experiment = ExperimentalMetadataManager("existing_experiment.json")

# Access data
reagents = experiment.get_chemistry_data()["solid_reagents"]
components = experiment.get_apparatus_data()["components"]
```

### Legacy Data Migration

```python
from mechwolf.DataEntry.experimental_metadata.migration_utilities import migrate_legacy_files

# Migrate old format files
migrate_legacy_files(
    input_directory="legacy_data/",
    output_directory="unified_metadata/"
)
```

### Integration with MechWolf Apparatus

```python
from mechwolf.DataEntry.shared_components.apparatus_factory import ApparatusFactory

# Create MechWolf Apparatus from metadata
apparatus = ApparatusFactory.create_apparatus_from_experiment(
    experiment_file="my_experiment.json"
)
```

## Integration Points

### Phase 1 - Reagent Entry Integration
- **File:** `Phase1_ReagentEntry/data_adapter.py`
- **Purpose:** Maintains compatibility with existing ReagentUI interface
- **Usage:** Translates between old and new data formats automatically

### Phase 2 - Apparatus Builder Integration
- **File:** `Phase2_ApparatusBuilder/core/designer.py`
- **Purpose:** GUI apparatus designer saves directly to experimental_metadata
- **Usage:** Network topology and component configuration storage

### Shared Components Integration
- **File:** `shared_components/apparatus_factory.py`
- **Purpose:** Creates MechWolf Apparatus objects from experimental_metadata
- **Usage:** Bridge between metadata and executable apparatus

## Validation and Quality Assurance

### Schema Validation
- Real-time validation during data entry
- JSON schema compliance checking
- Cross-section data consistency validation

### Error Handling
- Graceful handling of missing or invalid data
- Detailed error messages with suggested corrections
- Automatic data type conversion where appropriate

## Migration and Legacy Support

### Automatic Migration
- Detects legacy reagent, apparatus, and protocol JSON files
- Converts to unified format while preserving all original data
- Maintains backward compatibility with existing workflows

### Version Management
- Schema versioning for future upgrades
- Migration utilities for version updates
- Preservation of data integrity across versions

## Best Practices for LLM Usage

### When Working with Experimental Metadata:

1. **Always load the full experiment context** before making modifications
2. **Use the appropriate manager class** for each data section
3. **Validate data** after modifications using built-in validation methods
4. **Save frequently** to prevent data loss
5. **Check for legacy formats** and migrate when necessary

### Common LLM Tasks:

1. **Data Analysis:** Use the analysis section to access experimental results
2. **Protocol Generation:** Build protocols using the protocol manager
3. **Component Configuration:** Define apparatus using the apparatus manager
4. **Stoichiometry Calculations:** Use chemistry manager for reagent calculations
5. **Data Migration:** Use migration utilities for legacy data conversion

### File Path References:

When referencing code, always use the pattern `file_path:line_number` for easy navigation:
- Core manager: `experimental_metadata_manager.py:123`
- Schema definitions: `schema_definitions.py:45`
- Chemistry manager: `chemistry_manager.py:67`

## Recent Updates and Version History

### Version 3.0.0 (Current)
- Unified metadata format implementation
- Complete manager class architecture
- Legacy migration utilities
- Enhanced validation system
- Jupyter notebook integration templates

### Migration from Previous Versions
- Automatic detection and conversion of legacy formats
- Preservation of all historical data
- Seamless integration with existing workflows

---

*This reference guide provides comprehensive coverage of the MechWolf Experimental Metadata system for LLM-assisted development and analysis tasks. For additional details, refer to the source code documentation and usage examples.*