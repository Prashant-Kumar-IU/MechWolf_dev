"""
Schema Definitions for Unified Experimental Metadata

This module defines the JSON schema structure for the unified experimental
metadata format. Each section has its own schema version and validation rules.
"""

from typing import Dict, Any, List
from datetime import datetime

# Current schema version
CURRENT_VERSION = "3.0.0"

# Unified schema definition
UNIFIED_SCHEMA = {
    "type": "object",
    "properties": {
        "mechwolf_experiment": {
            "type": "object",
            "properties": {
                "version": {"type": "string", "default": CURRENT_VERSION},
                "experiment_id": {"type": "string"},
                "experiment_name": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "last_updated": {"type": "string", "format": "date-time"},
                "notebook_file": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["version", "experiment_id", "created"]
        },
        
        "chemistry": {
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "default": "1.0.0"},
                "mass_scale": {"type": "number"},
                "concentration": {"type": "number"},
                "solvent": {"type": "string"},
                "limiting_reagent": {"type": "string"},
                "solid_reagents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "inChi": {"type": "string"},
                            "inChi_Key": {"type": "string"},
                            "SMILES": {"type": "string"},
                            "molecular_weight": {"type": "number"},
                            "eq": {"type": ["number", "null"]},
                            "mass": {"type": "number"},
                            "position": {"type": ["number", "null"]},
                        },
                        "required": ["name", "molecular_weight"]
                    }
                },
                "liquid_reagents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "inChi": {"type": "string"},
                            "inChi_Key": {"type": "string"},
                            "SMILES": {"type": "string"},
                            "molecular_weight": {"type": "number"},
                            "eq": {"type": ["number", "null"]},
                            "volume": {"type": ["number", "null"]},
                            "density": {"type": "number"},
                            "position": {"type": ["number", "null"]},
                        },
                        "required": ["name", "molecular_weight"]
                    }
                },
                "solvent_volume": {
                    "type": "array",
                    "items": {"type": "number"}
                }
            }
        },
        
        "apparatus_config": {
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "default": "2.0.0"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "components": {
                    "type": "object",
                    "properties": {
                        "active": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "name": {"type": "string"},
                                    "category": {"type": "string"},
                                    "serial_port": {"type": "string"},
                                    "parameters": {"type": "object"}
                                },
                                "required": ["type", "name"]
                            }
                        },
                        "passive": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "name": {"type": "string"},
                                    "category": {"type": "string"},
                                    "parameters": {"type": "object"}
                                },
                                "required": ["type", "name"]
                            }
                        }
                    }
                },
                "connections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "tube": {"type": "string"},
                            "from_type": {"type": "string"},
                            "to_type": {"type": "string"},
                            "tube_type": {"type": "string"}
                        },
                        "required": ["from", "to"]
                    }
                },
                "calibration_data": {"type": "object"}
            }
        },
        
        "protocol_config": {
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "default": "1.0.0"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "procedures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component": {"type": "string"},
                            "action": {"type": "string"},
                            "start_time": {"type": "string"},
                            "duration": {"type": "string"},
                            "parameters": {"type": "object"}
                        },
                        "required": ["component", "action"]
                    }
                },
                "timing": {"type": "object"},
                "parameters": {"type": "object"},
                "created": {"type": "string", "format": "date-time"},
                "last_modified": {"type": "string", "format": "date-time"}
            }
        },
        
        "experiment_execution": {
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "default": "1.0.0"},
                "experiment_id": {"type": "string"},
                "start_time": {"type": "string", "format": "date-time"},
                "end_time": {"type": "string", "format": "date-time"},
                "status": {
                    "type": "string",
                    "enum": ["not_started", "running", "paused", "completed", "failed", "cancelled"]
                },
                "sensor_data": {"type": "object"},
                "executed_procedures": {"type": "array"},
                "errors": {"type": "array"},
                "logs": {"type": "array"}
            }
        },
        
        "analysis": {
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "default": "1.0.0"},
                "tlc_data": {
                    "type": "object",
                    "properties": {
                        "plates": {"type": "array"},
                        "rf_values": {"type": "object"},
                        "observations": {"type": "string"}
                    }
                },
                "spectroscopy": {
                    "type": "object",
                    "properties": {
                        "nmr": {"type": "object"},
                        "ir": {"type": "object"},
                        "ms": {"type": "object"},
                        "uv_vis": {"type": "object"}
                    }
                },
                "chromatography": {
                    "type": "object",
                    "properties": {
                        "gc_ms": {"type": "object"},
                        "hplc": {"type": "object"},
                        "lc_ms": {"type": "object"}
                    }
                },
                "yield_data": {
                    "type": "object",
                    "properties": {
                        "theoretical_yield": {"type": "number"},
                        "actual_yield": {"type": "number"},
                        "percent_yield": {"type": "number"},
                        "purity": {"type": "number"},
                        "method": {"type": "string"}
                    }
                },
                "custom_analysis": {"type": "object"}
            }
        }
    },
    "required": ["mechwolf_experiment"]
}

# Default values for new experiments
DEFAULT_EXPERIMENT_METADATA = {
    "mechwolf_experiment": {
        "version": CURRENT_VERSION,
        "experiment_id": None,  # Will be generated
        "experiment_name": "New Experiment",
        "created": None,  # Will be set to current time
        "last_updated": None,  # Will be set to current time
        "description": "MechWolf flow chemistry experiment"
    },
    "chemistry": {
        "schema_version": "1.0.0",
        "solid_reagents": [],
        "liquid_reagents": [],
        "solvent_volume": []
    },
    "apparatus_config": {
        "schema_version": "2.0.0",
        "name": "New Apparatus",
        "description": "Flow chemistry apparatus configuration",
        "components": {
            "active": [],
            "passive": []
        },
        "connections": [],
        "calibration_data": {}
    },
    "protocol_config": {
        "schema_version": "1.0.0",
        "name": "New Protocol",
        "description": "Flow chemistry protocol",
        "procedures": [],
        "timing": {},
        "parameters": {}
    },
    "experiment_execution": {
        "schema_version": "1.0.0",
        "status": "not_started",
        "sensor_data": {},
        "executed_procedures": [],
        "errors": [],
        "logs": []
    },
    "analysis": {
        "schema_version": "1.0.0",
        "tlc_data": {},
        "spectroscopy": {},
        "chromatography": {},
        "yield_data": {},
        "custom_analysis": {}
    }
}

def validate_section(section_name: str, data: Dict[str, Any]) -> List[str]:
    """
    Validate a specific section of the experimental metadata
    
    Args:
        section_name: Name of the section to validate
        data: Data to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if section_name not in UNIFIED_SCHEMA["properties"]:
        errors.append(f"Unknown section: {section_name}")
        return errors
    
    section_schema = UNIFIED_SCHEMA["properties"][section_name]
    
    # Basic type checking
    if section_schema.get("type") == "object" and not isinstance(data, dict):
        errors.append(f"Section {section_name} must be an object/dictionary")
        return errors
    
    # Check required fields
    required_fields = section_schema.get("required", [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field '{field}' in section {section_name}")
    
    return errors

def get_default_data(section_name: str) -> Dict[str, Any]:
    """Get default data for a section"""
    return DEFAULT_EXPERIMENT_METADATA.get(section_name, {}).copy()

def generate_experiment_id() -> str:
    """Generate a unique experiment ID"""
    now = datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
    # Add a simple hash component (could be enhanced)
    import hashlib
    hash_input = f"{timestamp}_{now.microsecond}".encode()
    hash_suffix = hashlib.md5(hash_input).hexdigest()[:8]
    return f"{timestamp}_{hash_suffix}"

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

