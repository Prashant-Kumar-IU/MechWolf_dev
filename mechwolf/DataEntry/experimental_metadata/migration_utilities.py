"""
Migration Utilities - Convert legacy JSON formats to unified experimental metadata

This module provides utilities to migrate existing JSON files from various
MechWolf modules to the new unified experimental metadata format.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .schema_definitions import (
    DEFAULT_EXPERIMENT_METADATA, 
    generate_experiment_id, 
    get_current_timestamp
)


def migrate_legacy_files(source_directory: str, output_directory: str = None) -> List[str]:
    """
    Migrate all legacy JSON files in a directory to unified format
    
    Args:
        source_directory: Directory containing legacy JSON files
        output_directory: Directory for migrated files (default: source_directory/migrated)
    
    Returns:
        List of successfully migrated file paths
    """
    source_path = Path(source_directory)
    if output_directory is None:
        output_path = source_path / "migrated"
    else:
        output_path = Path(output_directory)
    
    output_path.mkdir(exist_ok=True)
    
    migrated_files = []
    json_files = list(source_path.glob("*.json"))
    
    print(f"🔄 Found {len(json_files)} JSON files to check for migration...")
    
    for json_file in json_files:
        try:
            print(f"Checking {json_file.name}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine file type and migrate accordingly
            migrated_data = None
            
            if _is_reagent_file(data):
                print(f"  → Reagent file detected")
                migrated_data = convert_reagent_json(data, json_file.stem)
            
            elif _is_apparatus_file(data):
                print(f"  → Apparatus file detected") 
                migrated_data = convert_apparatus_json(data, json_file.stem)
            
            elif _is_protocol_file(data):
                print(f"  → Protocol file detected")
                migrated_data = convert_protocol_json(data, json_file.stem)
            
            elif _is_unified_file(data):
                print(f"  → Already in unified format, copying...")
                migrated_data = data
            
            else:
                print(f"  → Unknown format, attempting generic migration...")
                migrated_data = _generic_migration(data, json_file.stem)
            
            if migrated_data:
                # Save migrated file
                output_file = output_path / f"{json_file.stem}_migrated.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(migrated_data, f, indent=4, ensure_ascii=False, sort_keys=True)
                
                migrated_files.append(str(output_file))
                print(f"  ✅ Migrated to {output_file}")
            else:
                print(f"  ❌ Could not migrate {json_file.name}")
        
        except Exception as e:
            print(f"  ❌ Error migrating {json_file.name}: {e}")
    
    print(f"\n🎉 Migration complete! {len(migrated_files)} files migrated.")
    return migrated_files


def convert_reagent_json(reagent_data: Dict[str, Any], experiment_name: str = "Reagent Experiment") -> Dict[str, Any]:
    """
    Convert legacy reagent JSON to unified format
    
    Args:
        reagent_data: Legacy reagent data
        experiment_name: Name for the experiment
    
    Returns:
        Unified experimental metadata dictionary
    """
    # Start with default structure
    unified_data = DEFAULT_EXPERIMENT_METADATA.copy()
    
    # Set experiment metadata
    now = get_current_timestamp()
    experiment_id = generate_experiment_id()
    
    unified_data["mechwolf_experiment"].update({
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "created": now,
        "last_updated": now,
        "description": "Migrated from legacy reagent format"
    })
    
    # Migrate chemistry data
    chemistry_section = unified_data["chemistry"]
    
    # Map known fields
    field_mappings = {
        "mass_scale": "mass_scale",
        "concentration": "concentration", 
        "solvent": "solvent",
        "limiting_reagent": "limiting_reagent",
        "solid_reagents": "solid_reagents",
        "liquid_reagents": "liquid_reagents",
        "solvent_volume": "solvent_volume"
    }
    
    for old_field, new_field in field_mappings.items():
        if old_field in reagent_data:
            chemistry_section[new_field] = reagent_data[old_field]
    
    return unified_data


def convert_apparatus_json(apparatus_data: Dict[str, Any], experiment_name: str = "Apparatus Experiment") -> Dict[str, Any]:
    """
    Convert legacy apparatus JSON to unified format
    
    Args:
        apparatus_data: Legacy apparatus data
        experiment_name: Name for the experiment
    
    Returns:
        Unified experimental metadata dictionary
    """
    # Start with default structure
    unified_data = DEFAULT_EXPERIMENT_METADATA.copy()
    
    # Set experiment metadata
    now = get_current_timestamp()
    experiment_id = generate_experiment_id()
    
    unified_data["mechwolf_experiment"].update({
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "created": now,
        "last_updated": now,
        "description": "Migrated from legacy apparatus format"
    })
    
    # Migrate apparatus data
    if "apparatus_config" in apparatus_data:
        unified_data["apparatus_config"] = apparatus_data["apparatus_config"]
    else:
        # Try to extract apparatus data from root level
        apparatus_section = unified_data["apparatus_config"]
        
        if "components" in apparatus_data:
            apparatus_section["components"] = apparatus_data["components"]
        
        if "connections" in apparatus_data:
            apparatus_section["connections"] = apparatus_data["connections"]
        
        if "name" in apparatus_data:
            apparatus_section["name"] = apparatus_data["name"]
        
        if "description" in apparatus_data:
            apparatus_section["description"] = apparatus_data["description"]
    
    # Ensure schema version is set
    unified_data["apparatus_config"]["schema_version"] = "2.0.0"
    
    return unified_data


def convert_protocol_json(protocol_data: Dict[str, Any], experiment_name: str = "Protocol Experiment") -> Dict[str, Any]:
    """
    Convert legacy protocol JSON to unified format
    
    Args:
        protocol_data: Legacy protocol data
        experiment_name: Name for the experiment
    
    Returns:
        Unified experimental metadata dictionary
    """
    # Start with default structure
    unified_data = DEFAULT_EXPERIMENT_METADATA.copy()
    
    # Set experiment metadata
    now = get_current_timestamp()
    experiment_id = generate_experiment_id()
    
    unified_data["mechwolf_experiment"].update({
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "created": now,
        "last_updated": now,
        "description": "Migrated from legacy protocol format"
    })
    
    # Migrate protocol data
    if "protocol_configs" in protocol_data and protocol_data["protocol_configs"]:
        # Take the latest protocol config
        latest_protocol = protocol_data["protocol_configs"][-1]
        unified_data["protocol_config"] = latest_protocol
    elif "protocol_config" in protocol_data:
        unified_data["protocol_config"] = protocol_data["protocol_config"]
    else:
        # Try to extract protocol data from root level
        protocol_section = unified_data["protocol_config"]
        
        for field in ["name", "description", "procedures", "timing", "parameters"]:
            if field in protocol_data:
                protocol_section[field] = protocol_data[field]
    
    # Ensure schema version and timestamps are set
    unified_data["protocol_config"]["schema_version"] = "1.0.0"
    if "created" not in unified_data["protocol_config"]:
        unified_data["protocol_config"]["created"] = now
    unified_data["protocol_config"]["last_modified"] = now
    
    return unified_data


def convert_combined_json(combined_data: Dict[str, Any], experiment_name: str = "Combined Experiment") -> Dict[str, Any]:
    """
    Convert a JSON file that contains multiple types of data
    
    Args:
        combined_data: Combined legacy data
        experiment_name: Name for the experiment
    
    Returns:
        Unified experimental metadata dictionary
    """
    # Start with default structure
    unified_data = DEFAULT_EXPERIMENT_METADATA.copy()
    
    # Set experiment metadata
    now = get_current_timestamp()
    experiment_id = generate_experiment_id()
    
    unified_data["mechwolf_experiment"].update({
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "created": now,
        "last_updated": now,
        "description": "Migrated from combined legacy format"
    })
    
    # Migrate chemistry data if present
    if any(key in combined_data for key in ["solid_reagents", "liquid_reagents", "mass_scale"]):
        reagent_dict = convert_reagent_json(combined_data, experiment_name)
        unified_data["chemistry"] = reagent_dict["chemistry"]
    
    # Migrate apparatus data if present
    if "apparatus_config" in combined_data or "components" in combined_data:
        apparatus_dict = convert_apparatus_json(combined_data, experiment_name)
        unified_data["apparatus_config"] = apparatus_dict["apparatus_config"]
    
    # Migrate protocol data if present
    if any(key in combined_data for key in ["protocol_configs", "protocol_config", "procedures"]):
        protocol_dict = convert_protocol_json(combined_data, experiment_name)
        unified_data["protocol_config"] = protocol_dict["protocol_config"]
    
    return unified_data


def update_legacy_imports(file_path: str, backup: bool = True) -> bool:
    """
    Update import statements in Python files to use new unified system
    
    Args:
        file_path: Path to Python file to update
        backup: Whether to create a backup before updating
    
    Returns:
        True if updated successfully
    """
    file_path = Path(file_path)
    
    if not file_path.exists() or file_path.suffix != '.py':
        print(f"❌ File {file_path} not found or not a Python file")
        return False
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup if requested
        if backup:
            backup_path = file_path.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Backup created: {backup_path}")
        
        # Define import replacements
        replacements = {
            # Old ReagentUI imports
            "from mechwolf.DataEntry.ReagentUI.DataManager import ReagentDataManager": 
                "from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager",
            
            # Old FlowSetups imports
            "from mechwolf.DataEntry.FlowSetups.data_manager import": 
                "from mechwolf.DataEntry.experimental_metadata import",
            
            # Old ProtocolDev imports
            "from mechwolf.DataEntry.ProtocolDev.protocol_data_manager import ProtocolDataManager":
                "from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager",
        }
        
        # Apply replacements
        updated_content = content
        changes_made = 0
        
        for old_import, new_import in replacements.items():
            if old_import in updated_content:
                updated_content = updated_content.replace(old_import, new_import)
                changes_made += 1
                print(f"  ✅ Updated import: {old_import[:50]}...")
        
        if changes_made > 0:
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"🔄 Updated {changes_made} import statements in {file_path}")
            return True
        else:
            print(f"ℹ️  No import updates needed in {file_path}")
            return True
    
    except Exception as e:
        print(f"❌ Error updating imports in {file_path}: {e}")
        return False


# Helper functions for file type detection
def _is_reagent_file(data: Dict[str, Any]) -> bool:
    """Check if data represents a reagent file"""
    reagent_indicators = ["solid_reagents", "liquid_reagents", "mass_scale", "concentration"]
    return any(key in data for key in reagent_indicators)


def _is_apparatus_file(data: Dict[str, Any]) -> bool:
    """Check if data represents an apparatus file"""
    apparatus_indicators = ["apparatus_config", "components", "connections"]
    return any(key in data for key in apparatus_indicators)


def _is_protocol_file(data: Dict[str, Any]) -> bool:
    """Check if data represents a protocol file"""
    protocol_indicators = ["protocol_configs", "protocol_config", "procedures"]
    return any(key in data for key in protocol_indicators)


def _is_unified_file(data: Dict[str, Any]) -> bool:
    """Check if data is already in unified format"""
    return "mechwolf_experiment" in data


def _generic_migration(data: Dict[str, Any], experiment_name: str) -> Dict[str, Any]:
    """
    Attempt generic migration for unknown file formats
    
    Args:
        data: Unknown format data
        experiment_name: Name for the experiment
    
    Returns:
        Unified experimental metadata dictionary
    """
    print(f"  ⚠️  Attempting generic migration for unknown format...")
    
    # Start with default structure
    unified_data = DEFAULT_EXPERIMENT_METADATA.copy()
    
    # Set experiment metadata
    now = get_current_timestamp()
    experiment_id = generate_experiment_id()
    
    unified_data["mechwolf_experiment"].update({
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "created": now,
        "last_updated": now,
        "description": "Migrated from unknown legacy format"
    })
    
    # Try to detect and migrate different sections
    if _is_reagent_file(data):
        reagent_dict = convert_reagent_json(data, experiment_name)
        unified_data["chemistry"] = reagent_dict["chemistry"]
    
    if _is_apparatus_file(data):
        apparatus_dict = convert_apparatus_json(data, experiment_name)
        unified_data["apparatus_config"] = apparatus_dict["apparatus_config"]
    
    if _is_protocol_file(data):
        protocol_dict = convert_protocol_json(data, experiment_name)
        unified_data["protocol_config"] = protocol_dict["protocol_config"]
    
    # Store any unrecognized data in custom analysis section
    unrecognized_keys = set(data.keys()) - {
        "mass_scale", "concentration", "solvent", "limiting_reagent",
        "solid_reagents", "liquid_reagents", "solvent_volume",
        "apparatus_config", "components", "connections", "name", "description",
        "protocol_configs", "protocol_config", "procedures", "timing", "parameters"
    }
    
    if unrecognized_keys:
        custom_data = {key: data[key] for key in unrecognized_keys}
        unified_data["analysis"]["custom_analysis"]["legacy_data"] = custom_data
        print(f"    → Stored {len(unrecognized_keys)} unrecognized fields in custom analysis")
    
    return unified_data


def validate_migration(original_file: str, migrated_file: str) -> Dict[str, Any]:
    """
    Validate that migration preserved important data
    
    Args:
        original_file: Path to original file
        migrated_file: Path to migrated file
    
    Returns:
        Dictionary with validation results
    """
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        with open(migrated_file, 'r', encoding='utf-8') as f:
            migrated_data = json.load(f)
        
        validation_results = {
            "status": "success",
            "issues": [],
            "preserved_data": [],
            "new_structure": True
        }
        
        # Check that important data was preserved
        if "solid_reagents" in original_data:
            migrated_reagents = migrated_data.get("chemistry", {}).get("solid_reagents", [])
            if len(migrated_reagents) == len(original_data["solid_reagents"]):
                validation_results["preserved_data"].append("solid_reagents")
            else:
                validation_results["issues"].append("Solid reagents count mismatch")
        
        if "apparatus_config" in original_data:
            if "apparatus_config" in migrated_data:
                validation_results["preserved_data"].append("apparatus_config")
            else:
                validation_results["issues"].append("Apparatus config not preserved")
        
        # Check new structure exists
        if "mechwolf_experiment" not in migrated_data:
            validation_results["issues"].append("New unified structure not created")
            validation_results["new_structure"] = False
        
        if validation_results["issues"]:
            validation_results["status"] = "warning"
        
        return validation_results
    
    except Exception as e:
        return {
            "status": "error",
            "issues": [f"Validation failed: {e}"],
            "preserved_data": [],
            "new_structure": False
        }