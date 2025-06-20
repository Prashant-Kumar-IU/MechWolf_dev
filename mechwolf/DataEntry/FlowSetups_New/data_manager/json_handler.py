"""
JSON Handler - Enhanced JSON file management with schema validation

This module provides robust JSON file handling with schema validation,
versioning, backup, and error recovery capabilities.
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

from .schema_validator import SchemaValidator
from .export_manager import ExportManager


class JSONHandler:
    """Enhanced JSON file handler with validation and backup"""
    
    def __init__(self, json_file: str):
        self.json_file = Path(json_file)
        self.backup_dir = self.json_file.parent / ".mechwolf_backups"
        self.schema_validator = SchemaValidator()
        self.export_manager = ExportManager()
        
        # Ensure directories exist
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create initial file if it doesn't exist
        if not self.json_file.exists():
            self._create_initial_file()
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Load configuration from JSON file with error recovery
        
        Returns:
            Configuration dictionary or None if load fails
        """
        try:
            # Try to load main file
            return self._load_file(self.json_file)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in {self.json_file}: {e}")
            return self._attempt_recovery()
            
        except FileNotFoundError:
            print(f"⚠️ Configuration file not found: {self.json_file}")
            self._create_initial_file()
            return self._load_file(self.json_file)
            
        except Exception as e:
            print(f"❌ Unexpected error loading configuration: {e}")
            return self._attempt_recovery()
    
    def save_config(self, config: Dict[str, Any], create_backup: bool = True) -> bool:
        """
        Save configuration to JSON file with validation and backup
        
        Args:
            config: Configuration dictionary to save
            create_backup: Whether to create backup before saving
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Validate configuration
            validation_errors = self.schema_validator.validate_apparatus_config(config)
            if validation_errors:
                print("❌ Configuration validation failed:")
                for error in validation_errors:
                    print(f"  • {error}")
                return False
            
            # Create backup if requested and file exists
            if create_backup and self.json_file.exists():
                self._create_backup()
            
            # Add metadata
            config_with_metadata = self._add_metadata(config)
            
            # Write to temporary file first
            temp_file = self.json_file.with_suffix('.tmp')
            self._write_file(temp_file, config_with_metadata)
            
            # Validate written file
            if self._validate_written_file(temp_file):
                # Move temporary file to final location
                shutil.move(str(temp_file), str(self.json_file))
                print(f"✅ Configuration saved successfully to {self.json_file}")
                return True
            else:
                print("❌ Validation failed for written file")
                temp_file.unlink(missing_ok=True)
                return False
                
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            traceback.print_exc()
            return False
    
    def get_backup_files(self) -> List[Path]:
        """Get list of available backup files"""
        if not self.backup_dir.exists():
            return []
        
        backup_files = list(self.backup_dir.glob(f"{self.json_file.stem}_backup_*.json"))
        return sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def restore_from_backup(self, backup_file: Optional[Path] = None) -> bool:
        """
        Restore configuration from backup
        
        Args:
            backup_file: Specific backup file to restore from, or None for most recent
        
        Returns:
            True if restore successful, False otherwise
        """
        try:
            if backup_file is None:
                # Use most recent backup
                backups = self.get_backup_files()
                if not backups:
                    print("❌ No backup files available")
                    return False
                backup_file = backups[0]
            
            if not backup_file.exists():
                print(f"❌ Backup file not found: {backup_file}")
                return False
            
            # Load and validate backup
            backup_config = self._load_file(backup_file)
            if backup_config is None:
                print(f"❌ Failed to load backup file: {backup_file}")
                return False
            
            # Validate backup configuration
            validation_errors = self.schema_validator.validate_apparatus_config(backup_config)
            if validation_errors:
                print(f"⚠️ Backup file has validation errors: {len(validation_errors)} issues")
                # Continue anyway - backup might be from older schema
            
            # Save current file as backup before restore
            if self.json_file.exists():
                self._create_backup(suffix="_pre_restore")
            
            # Copy backup to main file
            shutil.copy(str(backup_file), str(self.json_file))
            
            print(f"✅ Configuration restored from {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error restoring from backup: {e}")
            return False
    
    def export_config(self, export_format: str, output_file: Optional[str] = None) -> bool:
        """
        Export configuration to different formats
        
        Args:
            export_format: Format to export to ('json', 'yaml', 'csv', 'python')
            output_file: Output file path, or None for default naming
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            config = self.load_config()
            if config is None:
                print("❌ No configuration to export")
                return False
            
            return self.export_manager.export_config(config, export_format, output_file)
            
        except Exception as e:
            print(f"❌ Error exporting configuration: {e}")
            return False
    
    def validate_file(self) -> List[str]:
        """
        Validate current configuration file
        
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            config = self.load_config()
            if config is None:
                return ["Failed to load configuration file"]
            
            return self.schema_validator.validate_apparatus_config(config)
            
        except Exception as e:
            return [f"Error validating file: {e}"]
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the configuration file"""
        info = {
            'file_path': str(self.json_file),
            'exists': self.json_file.exists(),
            'size': 0,
            'modified': None,
            'backup_count': len(self.get_backup_files()),
            'is_valid': False
        }
        
        if self.json_file.exists():
            stat = self.json_file.stat()
            info['size'] = stat.st_size
            info['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Check validity
            validation_errors = self.validate_file()
            info['is_valid'] = len(validation_errors) == 0
            info['validation_errors'] = validation_errors
        
        return info
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup files, keeping only the most recent ones
        
        Args:
            keep_count: Number of backups to keep
        
        Returns:
            Number of backups deleted
        """
        try:
            backups = self.get_backup_files()
            
            if len(backups) <= keep_count:
                return 0
            
            # Delete older backups
            to_delete = backups[keep_count:]
            deleted_count = 0
            
            for backup_file in to_delete:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ Failed to delete backup {backup_file}: {e}")
            
            print(f"🧹 Cleaned up {deleted_count} old backup files")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error cleaning up backups: {e}")
            return 0
    
    def _create_initial_file(self) -> None:
        """Create initial configuration file"""
        initial_config = {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "apparatus_config": {
                "name": "",
                "description": "",
                "components": {
                    "active": [],
                    "passive": []
                },
                "connections": []
            }
        }
        
        self._write_file(self.json_file, initial_config)
    
    def _load_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON file with proper error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return None
    
    def _write_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Write JSON file with proper formatting"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
    
    def _create_backup(self, suffix: str = "") -> Optional[Path]:
        """Create backup of current file"""
        try:
            if not self.json_file.exists():
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.json_file.stem}_backup_{timestamp}{suffix}.json"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy(str(self.json_file), str(backup_path))
            return backup_path
            
        except Exception as e:
            print(f"⚠️ Failed to create backup: {e}")
            return None
    
    def _attempt_recovery(self) -> Optional[Dict[str, Any]]:
        """Attempt to recover from backup files"""
        print("🔄 Attempting recovery from backup files...")
        
        backups = self.get_backup_files()
        
        for backup_file in backups:
            try:
                print(f"📁 Trying backup: {backup_file}")
                config = self._load_file(backup_file)
                
                if config is not None:
                    print(f"✅ Successfully loaded backup: {backup_file}")
                    return config
                    
            except Exception as e:
                print(f"❌ Failed to load backup {backup_file}: {e}")
        
        print("❌ All recovery attempts failed, creating new configuration")
        self._create_initial_file()
        return self._load_file(self.json_file)
    
    def _validate_written_file(self, file_path: Path) -> bool:
        """Validate that a written file can be loaded properly"""
        try:
            data = self._load_file(file_path)
            return data is not None
        except Exception:
            return False
    
    def _add_metadata(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to configuration"""
        config_with_metadata = config.copy()
        
        # Update version and timestamps
        config_with_metadata["version"] = "2.0.0"
        config_with_metadata["last_updated"] = datetime.now().isoformat()
        
        # Add creation timestamp if not present
        if "created" not in config_with_metadata:
            config_with_metadata["created"] = datetime.now().isoformat()
        
        # Add file statistics
        config_with_metadata["metadata"] = {
            "component_count": self._count_components(config),
            "connection_count": len(config.get("apparatus_config", {}).get("connections", [])),
            "file_size": len(json.dumps(config_with_metadata)),
            "schema_version": "2.0.0"
        }
        
        return config_with_metadata
    
    def _count_components(self, config: Dict[str, Any]) -> int:
        """Count total components in configuration"""
        apparatus_config = config.get("apparatus_config", {})
        components = apparatus_config.get("components", {})
        
        total_count = 0
        for category in ["active", "passive"]:
            total_count += len(components.get(category, []))
        
        return total_count
    
    def merge_configurations(self, other_file: str) -> bool:
        """
        Merge another configuration file into this one
        
        Args:
            other_file: Path to other configuration file
        
        Returns:
            True if merge successful, False otherwise
        """
        try:
            # Load other configuration
            other_handler = JSONHandler(other_file)
            other_config = other_handler.load_config()
            
            if other_config is None:
                print(f"❌ Failed to load other configuration: {other_file}")
                return False
            
            # Load current configuration
            current_config = self.load_config()
            if current_config is None:
                print("❌ Failed to load current configuration")
                return False
            
            # Merge configurations
            merged_config = self._merge_config_data(current_config, other_config)
            
            # Save merged configuration
            return self.save_config(merged_config)
            
        except Exception as e:
            print(f"❌ Error merging configurations: {e}")
            return False
    
    def _merge_config_data(self, base_config: Dict[str, Any], 
                          other_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries"""
        merged = base_config.copy()
        
        # Merge apparatus config
        base_apparatus = merged.get("apparatus_config", {})
        other_apparatus = other_config.get("apparatus_config", {})
        
        # Merge components
        base_components = base_apparatus.get("components", {})
        other_components = other_apparatus.get("components", {})
        
        for category in ["active", "passive"]:
            base_list = base_components.get(category, [])
            other_list = other_components.get(category, [])
            
            # Add components that don't already exist (by name)
            existing_names = {comp.get("name") for comp in base_list}
            for comp in other_list:
                if comp.get("name") not in existing_names:
                    base_list.append(comp)
        
        # Merge connections (avoid duplicates)
        base_connections = base_apparatus.get("connections", [])
        other_connections = other_apparatus.get("connections", [])
        
        existing_connections = {
            (conn.get("from"), conn.get("to"), conn.get("tube")) 
            for conn in base_connections
        }
        
        for conn in other_connections:
            conn_key = (conn.get("from"), conn.get("to"), conn.get("tube"))
            if conn_key not in existing_connections:
                base_connections.append(conn)
        
        return merged