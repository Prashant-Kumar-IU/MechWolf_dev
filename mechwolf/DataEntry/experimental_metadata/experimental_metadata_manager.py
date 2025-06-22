"""
Experimental Metadata Manager - Central coordinator for all experiment data

This module provides the main interface for managing comprehensive experimental
metadata in a unified JSON structure. It coordinates between different section
managers and ensures data consistency.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .schema_definitions import (
    UNIFIED_SCHEMA, 
    DEFAULT_EXPERIMENT_METADATA, 
    generate_experiment_id, 
    get_current_timestamp,
    validate_section
)
from .chemistry_manager import ChemistryDataManager
from .apparatus_manager import ApparatusDataManager
from .protocol_manager import ProtocolDataManager
from .analysis_manager import AnalysisDataManager


class ExperimentalMetadataManager:
    """
    Central manager for unified experimental metadata
    
    This class provides the main interface for working with experimental metadata
    that includes chemistry, apparatus, protocol, and analysis data in a single
    structured JSON file.
    
    Usage:
        # Create new experiment
        experiment = ExperimentalMetadataManager("my_experiment.json", "Birch Reduction")
        
        # Load existing experiment  
        experiment = ExperimentalMetadataManager("existing_experiment.json")
        
        # Work with sections
        experiment.chemistry.update_reagents(reagent_data)
        experiment.apparatus.configure_components(components)
        experiment.protocol.add_procedures(procedures)
        
        # Save changes
        experiment.save()
    """
    
    def __init__(self, json_file: str, experiment_name: Optional[str] = None):
        """
        Initialize experimental metadata manager
        
        Args:
            json_file: Path to the JSON metadata file
            experiment_name: Name for new experiment (ignored if file exists)
        """
        self.json_file = Path(json_file)
        self.backup_dir = self.json_file.parent / ".mechwolf_backups" 
        self._data = {}
        self._is_loaded = False
        
        # Initialize section managers (they'll be passed this manager)
        self.chemistry = ChemistryDataManager(self)
        self.apparatus = ApparatusDataManager(self)
        self.protocol = ProtocolDataManager(self)
        self.analysis = AnalysisDataManager(self)
        
        # Load or create the metadata file
        if self.json_file.exists():
            self.load()
        else:
            self.create_new_experiment(experiment_name or "New Experiment")
    
    def create_new_experiment(self, experiment_name: str) -> None:
        """Create a new experiment with default structure"""
        self._data = DEFAULT_EXPERIMENT_METADATA.copy()
        
        # Set experiment metadata
        now = get_current_timestamp()
        experiment_id = generate_experiment_id()
        
        self._data["mechwolf_experiment"].update({
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "created": now,
            "last_updated": now,
            "notebook_file": str(self.json_file.name)
        })
        
        self._is_loaded = True
        self.save()
    
    def load(self) -> Dict[str, Any]:
        """Load experimental metadata from JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different formats
            if "mechwolf_experiment" in data:
                # Already in unified format
                self._data = data
            else:
                # Legacy format - attempt to migrate
                self._data = self._migrate_legacy_data(data)
            
            self._is_loaded = True
            return self._data
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  Error loading {self.json_file}: {e}")
            print("Creating new experiment metadata...")
            self.create_new_experiment("Migrated Experiment")
            return self._data
        
        except Exception as e:
            print(f"❌ Unexpected error loading metadata: {e}")
            raise
    
    def save(self, create_backup: bool = True) -> bool:
        """
        Save experimental metadata to JSON file
        
        Args:
            create_backup: Whether to create a backup before saving
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Update last modified timestamp
            self._data["mechwolf_experiment"]["last_updated"] = get_current_timestamp()
            
            # Create backup if requested and file exists
            if create_backup and self.json_file.exists():
                self._create_backup()
            
            # Ensure parent directory exists
            self.json_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first, then move (atomic operation)
            temp_file = self.json_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            
            # Move temp file to actual file
            temp_file.replace(self.json_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
            return False
    
    def get_section_data(self, section_name: str) -> Dict[str, Any]:
        """Get data for a specific section"""
        if not self._is_loaded:
            self.load()
        
        if section_name not in self._data:
            # Initialize missing section with defaults
            from .schema_definitions import get_default_data
            self._data[section_name] = get_default_data(section_name)
        
        return self._data[section_name]
    
    def update_section_data(self, section_name: str, data: Dict[str, Any]) -> bool:
        """
        Update data for a specific section
        
        Args:
            section_name: Name of the section to update
            data: New data for the section
            
        Returns:
            True if updated successfully, False otherwise
        """
        # Validate the data
        errors = validate_section(section_name, data)
        if errors:
            print(f"❌ Validation errors for section {section_name}:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        # Update the data
        self._data[section_name] = data
        return True
    
    def get_experiment_info(self) -> Dict[str, Any]:
        """Get basic experiment information"""
        return self.get_section_data("mechwolf_experiment")
    
    def get_experiment_id(self) -> str:
        """Get the unique experiment ID"""
        return self.get_experiment_info().get("experiment_id", "unknown")
    
    def get_experiment_name(self) -> str:
        """Get the experiment name"""
        return self.get_experiment_info().get("experiment_name", "Unknown Experiment")
    
    def set_experiment_name(self, name: str) -> None:
        """Set the experiment name"""
        experiment_info = self.get_section_data("mechwolf_experiment")
        experiment_info["experiment_name"] = name
        self.update_section_data("mechwolf_experiment", experiment_info)
    
    def add_description(self, description: str) -> None:
        """Add or update experiment description"""
        experiment_info = self.get_section_data("mechwolf_experiment")
        experiment_info["description"] = description
        self.update_section_data("mechwolf_experiment", experiment_info)
    
    def validate_all_sections(self) -> Dict[str, List[str]]:
        """
        Validate all sections of the metadata
        
        Returns:
            Dictionary mapping section names to lists of error messages
        """
        validation_results = {}
        
        for section_name in ["mechwolf_experiment", "chemistry", "apparatus_config", 
                           "protocol_config", "experiment_execution", "analysis"]:
            if section_name in self._data:
                errors = validate_section(section_name, self._data[section_name])
                if errors:
                    validation_results[section_name] = errors
        
        return validation_results
    
    def export_section(self, section_name: str, output_file: Optional[str] = None) -> bool:
        """
        Export a specific section to a separate JSON file
        
        Args:
            section_name: Name of section to export
            output_file: Output file path (auto-generated if None)
            
        Returns:
            True if exported successfully
        """
        if section_name not in self._data:
            print(f"❌ Section {section_name} not found")
            return False
        
        if output_file is None:
            output_file = f"{self.json_file.stem}_{section_name}.json"
        
        try:
            export_data = {
                "exported_from": str(self.json_file),
                "exported_at": get_current_timestamp(),
                "section": section_name,
                "data": self._data[section_name]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Section {section_name} exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting section {section_name}: {e}")
            return False
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the experiment"""
        info = self.get_experiment_info()
        
        # Count items in each section
        chemistry_data = self.get_section_data("chemistry")
        apparatus_data = self.get_section_data("apparatus_config")
        protocol_data = self.get_section_data("protocol_config")
        
        solid_reagents = len(chemistry_data.get("solid_reagents", []))
        liquid_reagents = len(chemistry_data.get("liquid_reagents", []))
        active_components = len(apparatus_data.get("components", {}).get("active", []))
        passive_components = len(apparatus_data.get("components", {}).get("passive", []))
        connections = len(apparatus_data.get("connections", []))
        procedures = len(protocol_data.get("procedures", []))
        
        summary = f"""
📊 Experiment Summary: {info.get('experiment_name', 'Unknown')}
═══════════════════════════════════════════════════════════
🆔 ID: {info.get('experiment_id', 'Unknown')}
📅 Created: {info.get('created', 'Unknown')}
📝 Last Updated: {info.get('last_updated', 'Unknown')}

🧪 Chemistry:
   • Solid Reagents: {solid_reagents}
   • Liquid Reagents: {liquid_reagents}
   • Solvent: {chemistry_data.get('solvent', 'Not specified')}

⚙️  Apparatus:
   • Active Components: {active_components}
   • Passive Components: {passive_components} 
   • Connections: {connections}

📋 Protocol:
   • Procedures: {procedures}
   • Name: {protocol_data.get('name', 'Not specified')}

💾 File: {self.json_file}
        """
        
        return summary.strip()
    
    def _create_backup(self) -> None:
        """Create a backup of the current file"""
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.json_file.stem}_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_name
            
            # Copy current file to backup
            import shutil
            shutil.copy2(self.json_file, backup_path)
            
            # Clean up old backups (keep last 10)
            backups = sorted(self.backup_dir.glob(f"{self.json_file.stem}_backup_*.json"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
    
    def _migrate_legacy_data(self, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy data format to unified format"""
        print("🔄 Migrating legacy data to unified format...")
        
        # Start with default structure
        unified_data = DEFAULT_EXPERIMENT_METADATA.copy()
        
        # Set experiment metadata
        now = get_current_timestamp()
        experiment_id = generate_experiment_id()
        
        unified_data["mechwolf_experiment"].update({
            "experiment_id": experiment_id,
            "experiment_name": "Migrated Experiment",
            "created": now,
            "last_updated": now,
            "notebook_file": str(self.json_file.name),
            "description": "Migrated from legacy format"
        })
        
        # Migrate chemistry data
        if any(key in legacy_data for key in ["solid_reagents", "liquid_reagents", "mass_scale"]):
            chemistry_section = unified_data["chemistry"]
            
            # Copy chemistry fields
            for field in ["mass_scale", "concentration", "solvent", "limiting_reagent",
                         "solid_reagents", "liquid_reagents", "solvent_volume"]:
                if field in legacy_data:
                    chemistry_section[field] = legacy_data[field]
        
        # Migrate apparatus data
        if "apparatus_config" in legacy_data:
            unified_data["apparatus_config"] = legacy_data["apparatus_config"]
            # Ensure schema version is set
            unified_data["apparatus_config"]["schema_version"] = "2.0.0"
        
        # Migrate protocol data
        if any(key in legacy_data for key in ["protocol_configs", "protocol_config"]):
            if "protocol_configs" in legacy_data and legacy_data["protocol_configs"]:
                # Take the latest protocol config
                latest_protocol = legacy_data["protocol_configs"][-1]
                unified_data["protocol_config"] = latest_protocol
            elif "protocol_config" in legacy_data:
                unified_data["protocol_config"] = legacy_data["protocol_config"]
            
            # Ensure schema version is set
            unified_data["protocol_config"]["schema_version"] = "1.0.0"
        
        print("✅ Migration completed")
        return unified_data