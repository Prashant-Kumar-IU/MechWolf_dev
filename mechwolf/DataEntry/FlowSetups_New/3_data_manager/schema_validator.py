"""
Schema Validator - JSON schema definitions and validation for apparatus configurations

This module provides comprehensive schema validation for MechWolf apparatus
configurations with support for different schema versions.
"""
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re


class SchemaValidator:
    """Validates apparatus configurations against JSON schemas"""
    
    def __init__(self):
        self.current_version = "2.0.0"
        self.supported_versions = ["1.0.0", "2.0.0"]
        
        # Define schemas for different versions
        self.schemas = {
            "2.0.0": self._get_v2_schema(),
            "1.0.0": self._get_v1_schema()
        }
        
        # Common validation patterns
        self.patterns = {
            'python_identifier': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
            'serial_port': r'^(/dev/|COM)',
            'unit_volume': r'^\d+(\.\d+)?\s*(mL|ml|ML|Ml|L|l)$',
            'unit_length': r'^\d+(\.\d+)?\s*(ft|in|cm|mm|m)$',
            'unit_flow_rate': r'^\d+(\.\d+)?\s*(mL/min|ml/min|ML/min|L/min|l/min)$',
            'unit_diameter': r'^\d+(\.\d+)?\s*(mm|cm|in|")$|^\d+/\d+\s*(in|")$',
            'iso_datetime': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        }
    
    def validate_apparatus_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate complete apparatus configuration
        
        Args:
            config: Configuration dictionary to validate
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check basic structure
        if not isinstance(config, dict):
            return ["Configuration must be a dictionary"]
        
        # Detect version
        version = config.get("version", "1.0.0")
        if version not in self.supported_versions:
            errors.append(f"Unsupported schema version: {version}")
            version = self.current_version  # Fall back to current version
        
        # Get appropriate schema
        schema = self.schemas.get(version, self.schemas[self.current_version])
        
        # Validate against schema
        errors.extend(self._validate_against_schema(config, schema))
        
        # Additional semantic validation
        errors.extend(self._validate_semantic_rules(config))
        
        return errors
    
    def validate_components(self, components: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Validate component configurations"""
        errors = []
        
        if not isinstance(components, dict):
            return ["Components must be a dictionary"]
        
        # Validate each category
        for category in ["active", "passive"]:
            if category in components:
                category_errors = self._validate_component_category(
                    components[category], category
                )
                errors.extend(category_errors)
        
        # Check for name conflicts across categories
        errors.extend(self._check_component_name_conflicts(components))
        
        return errors
    
    def validate_connections(self, connections: List[Dict[str, Any]], 
                           components: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Validate connection configurations"""
        errors = []
        
        if not isinstance(connections, list):
            return ["Connections must be a list"]
        
        # Get all component names for reference checking
        component_names = set()
        for category in ["active", "passive"]:
            if category in components:
                for comp in components[category]:
                    if "name" in comp:
                        component_names.add(comp["name"])
        
        # Validate each connection
        for i, connection in enumerate(connections):
            conn_errors = self._validate_single_connection(
                connection, component_names, i
            )
            errors.extend(conn_errors)
        
        # Check for duplicate connections
        errors.extend(self._check_duplicate_connections(connections))
        
        return errors
    
    def migrate_schema(self, config: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """
        Migrate configuration to target schema version
        
        Args:
            config: Configuration to migrate
            target_version: Target schema version
        
        Returns:
            Migrated configuration
        """
        current_version = config.get("version", "1.0.0")
        
        if current_version == target_version:
            return config
        
        if current_version == "1.0.0" and target_version == "2.0.0":
            return self._migrate_v1_to_v2(config)
        
        # Add more migration paths as needed
        raise ValueError(f"Migration from {current_version} to {target_version} not supported")
    
    def _get_v2_schema(self) -> Dict[str, Any]:
        """Get version 2.0.0 schema"""
        return {
            "type": "object",
            "required": ["version", "apparatus_config"],
            "properties": {
                "version": {
                    "type": "string",
                    "enum": ["2.0.0"]
                },
                "created": {
                    "type": "string",
                    "pattern": self.patterns['iso_datetime']
                },
                "last_updated": {
                    "type": "string", 
                    "pattern": self.patterns['iso_datetime']
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "component_count": {"type": "integer", "minimum": 0},
                        "connection_count": {"type": "integer", "minimum": 0},
                        "file_size": {"type": "integer", "minimum": 0},
                        "schema_version": {"type": "string"}
                    }
                },
                "apparatus_config": {
                    "type": "object",
                    "required": ["components"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "components": {
                            "type": "object",
                            "required": ["active", "passive"],
                            "properties": {
                                "active": {
                                    "type": "array",
                                    "items": {"$ref": "#/definitions/active_component"}
                                },
                                "passive": {
                                    "type": "array", 
                                    "items": {"$ref": "#/definitions/passive_component"}
                                }
                            }
                        },
                        "connections": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/connection"}
                        }
                    }
                }
            },
            "definitions": {
                "active_component": {
                    "type": "object",
                    "required": ["type", "name", "category"],
                    "properties": {
                        "type": {"type": "string"},
                        "name": {
                            "type": "string",
                            "pattern": self.patterns['python_identifier']
                        },
                        "category": {
                            "type": "string",
                            "enum": ["active_contrib", "active_stdlib"]
                        },
                        "serial_port": {
                            "type": "string",
                            "pattern": self.patterns['serial_port']
                        }
                    }
                },
                "passive_component": {
                    "type": "object",
                    "required": ["type", "name", "category"],
                    "properties": {
                        "type": {"type": "string"},
                        "name": {
                            "type": "string",
                            "pattern": self.patterns['python_identifier']
                        },
                        "category": {
                            "type": "string",
                            "enum": ["passive"]
                        },
                        "description": {"type": "string"}
                    }
                },
                "connection": {
                    "type": "object",
                    "required": ["from", "to", "tube"],
                    "properties": {
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "tube": {"type": "string"},
                        "from_type": {"type": "string"},
                        "to_type": {"type": "string"},
                        "tube_type": {"type": "string"}
                    }
                }
            }
        }
    
    def _get_v1_schema(self) -> Dict[str, Any]:
        """Get version 1.0.0 schema (legacy)"""
        return {
            "type": "object",
            "properties": {
                "apparatus_config": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "components": {"type": "array"},
                        "connections": {"type": "array"}
                    }
                }
            }
        }
    
    def _validate_against_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate configuration against JSON schema"""
        errors = []
        
        # Basic structure validation
        try:
            # Check required fields
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
            
            # Validate apparatus_config structure
            if "apparatus_config" in config:
                apparatus_config = config["apparatus_config"]
                errors.extend(self._validate_apparatus_structure(apparatus_config))
            
        except Exception as e:
            errors.append(f"Schema validation error: {e}")
        
        return errors
    
    def _validate_apparatus_structure(self, apparatus_config: Dict[str, Any]) -> List[str]:
        """Validate apparatus configuration structure"""
        errors = []
        
        # Check components structure
        if "components" in apparatus_config:
            components = apparatus_config["components"]
            errors.extend(self.validate_components(components))
        
        # Check connections structure
        if "connections" in apparatus_config:
            connections = apparatus_config["connections"]
            components = apparatus_config.get("components", {})
            errors.extend(self.validate_connections(connections, components))
        
        return errors
    
    def _validate_component_category(self, components: List[Dict[str, Any]], 
                                   category: str) -> List[str]:
        """Validate components in a specific category"""
        errors = []
        
        if not isinstance(components, list):
            return [f"{category} components must be a list"]
        
        for i, component in enumerate(components):
            comp_errors = self._validate_single_component(component, category, i)
            errors.extend(comp_errors)
        
        return errors
    
    def _validate_single_component(self, component: Dict[str, Any], 
                                 category: str, index: int) -> List[str]:
        """Validate a single component"""
        errors = []
        prefix = f"Component {index + 1} ({category})"
        
        # Check required fields
        required_fields = ["type", "name"]
        for field in required_fields:
            if field not in component:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Validate name
        if "name" in component:
            name = component["name"]
            if not re.match(self.patterns['python_identifier'], name):
                errors.append(f"{prefix}: Invalid name '{name}' (must be valid Python identifier)")
        
        # Category-specific validation
        if category in ["active_contrib", "active_stdlib"]:
            errors.extend(self._validate_active_component_fields(component, prefix))
        elif category == "passive":
            errors.extend(self._validate_passive_component_fields(component, prefix))
        
        return errors
    
    def _validate_active_component_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate active component specific fields"""
        errors = []
        
        comp_type = component.get("type", "")
        
        # Serial port validation
        if "serial_port" in component:
            serial_port = component["serial_port"]
            if serial_port and not re.match(self.patterns['serial_port'], serial_port):
                errors.append(f"{prefix}: Invalid serial port format '{serial_port}'")
        
        # Type-specific validation
        if "Pump" in comp_type:
            errors.extend(self._validate_pump_fields(component, prefix))
        elif "Valve" in comp_type:
            errors.extend(self._validate_valve_fields(component, prefix))
        elif "Sensor" in comp_type:
            errors.extend(self._validate_sensor_fields(component, prefix))
        
        return errors
    
    def _validate_passive_component_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate passive component specific fields"""
        errors = []
        
        comp_type = component.get("type", "")
        
        if comp_type == "Tube":
            errors.extend(self._validate_tube_fields(component, prefix))
        elif comp_type == "Vessel":
            errors.extend(self._validate_vessel_fields(component, prefix))
        
        return errors
    
    def _validate_pump_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate pump-specific fields"""
        errors = []
        
        # Volume validation
        if "syringe_volume" in component:
            volume = component["syringe_volume"]
            if volume and not re.match(self.patterns['unit_volume'], volume):
                errors.append(f"{prefix}: Invalid syringe volume format '{volume}'")
        
        # Diameter validation
        if "syringe_diameter" in component:
            diameter = component["syringe_diameter"]
            if diameter and not re.match(self.patterns['unit_diameter'], diameter):
                errors.append(f"{prefix}: Invalid syringe diameter format '{diameter}'")
        
        # Flow rate validation
        if "max_rate" in component:
            rate = component["max_rate"]
            if rate and not re.match(self.patterns['unit_flow_rate'], rate):
                errors.append(f"{prefix}: Invalid max rate format '{rate}'")
        
        return errors
    
    def _validate_valve_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate valve-specific fields"""
        errors = []
        
        # Mapping validation
        if "mapping" in component:
            mapping = component["mapping"]
            if not isinstance(mapping, dict):
                errors.append(f"{prefix}: Mapping must be a dictionary")
            else:
                # Check port numbers
                ports = list(mapping.values())
                if len(ports) != len(set(ports)):
                    errors.append(f"{prefix}: Duplicate port numbers in mapping")
                
                for vessel, port in mapping.items():
                    if not isinstance(port, int) or port < 1:
                        errors.append(f"{prefix}: Invalid port number {port} for {vessel}")
        
        return errors
    
    def _validate_sensor_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate sensor-specific fields"""
        errors = []
        
        # Unit validation (optional)
        if "unit" in component and component["unit"]:
            unit = component["unit"]
            # Basic check - could be enhanced with specific unit validation
            if len(unit) > 20:
                errors.append(f"{prefix}: Unit string too long: '{unit}'")
        
        return errors
    
    def _validate_tube_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate tube-specific fields"""
        errors = []
        
        # Length validation
        if "length" in component:
            length = component["length"]
            if length and not re.match(self.patterns['unit_length'], length):
                errors.append(f"{prefix}: Invalid length format '{length}'")
        
        # Diameter validation for custom tubes
        preset = component.get("preset", "custom")
        if preset == "custom":
            for field in ["ID", "OD"]:
                if field in component and component[field]:
                    diameter = component[field]
                    if not re.match(self.patterns['unit_diameter'], diameter):
                        errors.append(f"{prefix}: Invalid {field} format '{diameter}'")
        
        return errors
    
    def _validate_vessel_fields(self, component: Dict[str, Any], prefix: str) -> List[str]:
        """Validate vessel-specific fields"""
        errors = []
        
        # Description length check
        if "description" in component:
            description = component["description"]
            if description and len(description) > 500:
                errors.append(f"{prefix}: Description too long (max 500 characters)")
        
        return errors
    
    def _validate_single_connection(self, connection: Dict[str, Any], 
                                  component_names: set, index: int) -> List[str]:
        """Validate a single connection"""
        errors = []
        prefix = f"Connection {index + 1}"
        
        # Check required fields
        required_fields = ["from", "to", "tube"]
        for field in required_fields:
            if field not in connection:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Check component references
        for field in ["from", "to", "tube"]:
            if field in connection:
                component_name = connection[field]
                if component_name not in component_names:
                    errors.append(f"{prefix}: Unknown component '{component_name}' in field '{field}'")
        
        # Check for self-connection
        if "from" in connection and "to" in connection:
            if connection["from"] == connection["to"]:
                errors.append(f"{prefix}: Component cannot connect to itself")
        
        return errors
    
    def _check_component_name_conflicts(self, components: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Check for name conflicts across component categories"""
        errors = []
        
        all_names = set()
        
        for category, comp_list in components.items():
            for component in comp_list:
                name = component.get("name")
                if name:
                    if name in all_names:
                        errors.append(f"Duplicate component name: '{name}'")
                    else:
                        all_names.add(name)
        
        return errors
    
    def _check_duplicate_connections(self, connections: List[Dict[str, Any]]) -> List[str]:
        """Check for duplicate connections"""
        errors = []
        
        seen_connections = set()
        
        for i, connection in enumerate(connections):
            conn_key = (
                connection.get("from"), 
                connection.get("to"), 
                connection.get("tube")
            )
            
            if conn_key in seen_connections:
                errors.append(f"Duplicate connection: {conn_key[0]} → {conn_key[1]} via {conn_key[2]}")
            else:
                seen_connections.add(conn_key)
        
        return errors
    
    def _validate_semantic_rules(self, config: Dict[str, Any]) -> List[str]:
        """Validate semantic rules beyond schema"""
        errors = []
        
        apparatus_config = config.get("apparatus_config", {})
        components = apparatus_config.get("components", {})
        connections = apparatus_config.get("connections", [])
        
        # Check for minimum required components
        active_components = components.get("active", [])
        passive_components = components.get("passive", [])
        
        if not active_components and not passive_components:
            errors.append("Apparatus must have at least one component")
        
        # Check for at least one pump if there are connections
        if connections:
            has_pump = any("Pump" in comp.get("type", "") for comp in active_components)
            if not has_pump:
                errors.append("Apparatus with connections should have at least one pump")
        
        # Check for vessels
        has_vessel = any(comp.get("type") == "Vessel" for comp in passive_components)
        if connections and not has_vessel:
            errors.append("Apparatus should have at least one vessel")
        
        return errors
    
    def _migrate_v1_to_v2(self, v1_config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate version 1.0.0 configuration to 2.0.0"""
        
        v2_config = {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "apparatus_config": {
                "name": v1_config.get("apparatus_config", {}).get("name", ""),
                "description": "",
                "components": {
                    "active": [],
                    "passive": []
                },
                "connections": v1_config.get("apparatus_config", {}).get("connections", [])
            }
        }
        
        # Migrate components (this would need specific logic based on v1 structure)
        old_components = v1_config.get("apparatus_config", {}).get("components", [])
        
        for comp in old_components:
            # Categorize component as active or passive
            comp_type = comp.get("type", "")
            if any(keyword in comp_type for keyword in ["Pump", "Valve", "Sensor"]):
                comp["category"] = "active_contrib"
                v2_config["apparatus_config"]["components"]["active"].append(comp)
            else:
                comp["category"] = "passive"
                v2_config["apparatus_config"]["components"]["passive"].append(comp)
        
        return v2_config