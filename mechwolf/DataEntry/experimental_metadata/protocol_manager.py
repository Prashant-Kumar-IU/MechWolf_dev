"""
Protocol Data Manager - Handles protocol configuration and procedures

This module manages the protocol section of experimental metadata, including
procedures, timing, parameters, and execution details.
"""

from typing import Dict, Any, List, Optional, Union
from .schema_definitions import get_current_timestamp


class ProtocolDataManager:
    """
    Manager for protocol-related experimental data
    
    Handles:
    - Protocol procedures and steps
    - Timing and scheduling
    - Component parameters and settings
    - Protocol validation
    """
    
    def __init__(self, metadata_manager):
        """Initialize with reference to main metadata manager"""
        self.metadata_manager = metadata_manager
        self.section_name = "protocol_config"
    
    def get_data(self) -> Dict[str, Any]:
        """Get the protocol section data"""
        return self.metadata_manager.get_section_data(self.section_name)
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save protocol section data"""
        # Update modification timestamp
        data["last_modified"] = get_current_timestamp()
        return self.metadata_manager.update_section_data(self.section_name, data)
    
    # Basic Configuration
    def set_protocol_info(self, name: str, description: str = "") -> bool:
        """Set basic protocol information"""
        data = self.get_data()
        data["name"] = name
        data["description"] = description
        
        # Set created timestamp if not exists
        if "created" not in data:
            data["created"] = get_current_timestamp()
        
        return self.save_data(data)
    
    # Procedure Management
    def add_procedure(self, procedure: Dict[str, Any]) -> bool:
        """
        Add a procedure to the protocol
        
        Args:
            procedure: Dictionary with procedure properties
                Required: component, action
                Optional: start_time, duration, parameters
        
        Returns:
            True if added successfully
        """
        if not procedure.get("component") or not procedure.get("action"):
            print("❌ Procedure must have 'component' and 'action'")
            return False
        
        data = self.get_data()
        if "procedures" not in data:
            data["procedures"] = []
        
        # Add unique ID to procedure
        procedure_id = len(data["procedures"]) + 1
        procedure["id"] = procedure_id
        
        data["procedures"].append(procedure)
        return self.save_data(data)
    
    def insert_procedure(self, index: int, procedure: Dict[str, Any]) -> bool:
        """Insert a procedure at a specific index"""
        if not procedure.get("component") or not procedure.get("action"):
            print("❌ Procedure must have 'component' and 'action'")
            return False
        
        data = self.get_data()
        if "procedures" not in data:
            data["procedures"] = []
        
        # Validate index
        if index < 0 or index > len(data["procedures"]):
            print(f"❌ Invalid index {index}. Must be between 0 and {len(data['procedures'])}")
            return False
        
        # Add unique ID
        procedure["id"] = len(data["procedures"]) + 1
        
        data["procedures"].insert(index, procedure)
        return self.save_data(data)
    
    def update_procedure(self, procedure_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing procedure by ID"""
        data = self.get_data()
        
        for i, proc in enumerate(data.get("procedures", [])):
            if proc.get("id") == procedure_id:
                data["procedures"][i].update(updates)
                return self.save_data(data)
        
        print(f"❌ Procedure with ID {procedure_id} not found")
        return False
    
    def remove_procedure(self, procedure_id: int) -> bool:
        """Remove a procedure by ID"""
        data = self.get_data()
        
        original_count = len(data.get("procedures", []))
        data["procedures"] = [
            proc for proc in data.get("procedures", [])
            if proc.get("id") != procedure_id
        ]
        
        if len(data["procedures"]) < original_count:
            return self.save_data(data)
        else:
            print(f"❌ Procedure with ID {procedure_id} not found")
            return False
    
    def clear_all_procedures(self) -> bool:
        """Clear all procedures"""
        data = self.get_data()
        data["procedures"] = []
        return self.save_data(data)
    
    def reorder_procedures(self, new_order: List[int]) -> bool:
        """
        Reorder procedures by providing new order of IDs
        
        Args:
            new_order: List of procedure IDs in desired order
        
        Returns:
            True if reordered successfully
        """
        data = self.get_data()
        procedures = data.get("procedures", [])
        
        # Create mapping from ID to procedure
        id_to_proc = {proc.get("id"): proc for proc in procedures}
        
        # Validate that all IDs exist
        existing_ids = set(id_to_proc.keys())
        provided_ids = set(new_order)
        
        if existing_ids != provided_ids:
            missing = existing_ids - provided_ids
            extra = provided_ids - existing_ids
            print(f"❌ ID mismatch. Missing: {missing}, Extra: {extra}")
            return False
        
        # Reorder procedures
        data["procedures"] = [id_to_proc[proc_id] for proc_id in new_order]
        return self.save_data(data)
    
    # Timing and Parameters
    def set_timing_parameters(self, timing: Dict[str, Any]) -> bool:
        """Set overall timing parameters for the protocol"""
        data = self.get_data()
        data["timing"] = timing
        return self.save_data(data)
    
    def set_global_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Set global protocol parameters"""
        data = self.get_data()
        data["parameters"] = parameters
        return self.save_data(data)
    
    def add_component_parameter(self, component_name: str, parameter_name: str, value: Any) -> bool:
        """Add a parameter for a specific component"""
        data = self.get_data()
        if "parameters" not in data:
            data["parameters"] = {}
        if "components" not in data["parameters"]:
            data["parameters"]["components"] = {}
        if component_name not in data["parameters"]["components"]:
            data["parameters"]["components"][component_name] = {}
        
        data["parameters"]["components"][component_name][parameter_name] = value
        return self.save_data(data)
    
    # Query Methods
    def get_procedure_by_id(self, procedure_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific procedure by ID"""
        data = self.get_data()
        
        for proc in data.get("procedures", []):
            if proc.get("id") == procedure_id:
                return proc.copy()
        
        return None
    
    def get_procedures_for_component(self, component_name: str) -> List[Dict[str, Any]]:
        """Get all procedures for a specific component"""
        data = self.get_data()
        procedures = []
        
        for proc in data.get("procedures", []):
            if proc.get("component") == component_name:
                procedures.append(proc.copy())
        
        return procedures
    
    def get_procedures_by_action(self, action: str) -> List[Dict[str, Any]]:
        """Get all procedures with a specific action"""
        data = self.get_data()
        procedures = []
        
        for proc in data.get("procedures", []):
            if proc.get("action") == action:
                procedures.append(proc.copy())
        
        return procedures
    
    def get_protocol_duration(self) -> Optional[str]:
        """Calculate total protocol duration from procedures"""
        data = self.get_data()
        procedures = data.get("procedures", [])
        
        if not procedures:
            return None
        
        # This is a simplified calculation - could be enhanced
        # to parse time strings and calculate actual duration
        durations = []
        for proc in procedures:
            if proc.get("duration"):
                durations.append(proc["duration"])
        
        if durations:
            return f"Multiple steps: {', '.join(durations[:3])}{'...' if len(durations) > 3 else ''}"
        
        return "Duration not specified"
    
    def get_component_usage(self) -> Dict[str, int]:
        """Get count of how many times each component is used"""
        data = self.get_data()
        usage = {}
        
        for proc in data.get("procedures", []):
            component = proc.get("component")
            if component:
                usage[component] = usage.get(component, 0) + 1
        
        return usage
    
    def get_action_summary(self) -> Dict[str, int]:
        """Get summary of actions used in the protocol"""
        data = self.get_data()
        actions = {}
        
        for proc in data.get("procedures", []):
            action = proc.get("action")
            if action:
                actions[action] = actions.get(action, 0) + 1
        
        return actions
    
    # Validation
    def validate_protocol(self) -> List[str]:
        """Validate protocol configuration and return any issues"""
        issues = []
        data = self.get_data()
        
        procedures = data.get("procedures", [])
        
        # Check for procedures without required fields
        for i, proc in enumerate(procedures):
            if not proc.get("component"):
                issues.append(f"Procedure {i+1} missing component")
            if not proc.get("action"):
                issues.append(f"Procedure {i+1} missing action")
        
        # Check for duplicate procedure IDs
        ids = [proc.get("id") for proc in procedures if proc.get("id")]
        if len(ids) != len(set(ids)):
            issues.append("Duplicate procedure IDs found")
        
        # Check timing consistency
        for i, proc in enumerate(procedures):
            start_time = proc.get("start_time")
            duration = proc.get("duration")
            
            if start_time and not duration:
                issues.append(f"Procedure {i+1} has start_time but no duration")
        
        # Validate against apparatus components (if available)
        try:
            apparatus_manager = self.metadata_manager.apparatus
            all_component_names = apparatus_manager.get_all_component_names()
            
            for i, proc in enumerate(procedures):
                component = proc.get("component")
                if component and component not in all_component_names:
                    issues.append(f"Procedure {i+1} references non-existent component: '{component}'")
        except:
            # If apparatus data not available, skip this validation
            pass
        
        return issues
    
    # Bulk Operations
    def load_procedures_from_list(self, procedures: List[Dict[str, Any]]) -> bool:
        """Load procedures from a list, replacing existing ones"""
        data = self.get_data()
        
        # Assign IDs to procedures
        for i, proc in enumerate(procedures):
            proc["id"] = i + 1
        
        data["procedures"] = procedures
        return self.save_data(data)
    
    def append_procedures_from_list(self, procedures: List[Dict[str, Any]]) -> bool:
        """Append procedures to existing ones"""
        data = self.get_data()
        if "procedures" not in data:
            data["procedures"] = []
        
        # Assign IDs starting from last existing ID
        next_id = len(data["procedures"]) + 1
        for proc in procedures:
            proc["id"] = next_id
            next_id += 1
        
        data["procedures"].extend(procedures)
        return self.save_data(data)
    
    # Export and Import
    def export_protocol_yaml(self) -> str:
        """Export protocol in YAML-like format (simplified for readability)"""
        data = self.get_data()
        
        yaml_content = f"""# Protocol: {data.get('name', 'Unnamed')}
# Description: {data.get('description', 'No description')}
# Created: {data.get('created', 'Unknown')}
# Last Modified: {data.get('last_modified', 'Unknown')}

protocol:
  name: {data.get('name', 'Unnamed')}
  description: {data.get('description', 'No description')}
  
procedures:
"""
        
        for proc in data.get("procedures", []):
            yaml_content += f"""  - component: {proc.get('component', 'unknown')}
    action: {proc.get('action', 'unknown')}
"""
            if proc.get("start_time"):
                yaml_content += f"    start_time: {proc['start_time']}\n"
            if proc.get("duration"):
                yaml_content += f"    duration: {proc['duration']}\n"
            if proc.get("parameters"):
                yaml_content += f"    parameters: {proc['parameters']}\n"
            yaml_content += "\n"
        
        if data.get("timing"):
            yaml_content += f"timing: {data['timing']}\n\n"
        
        if data.get("parameters"):
            yaml_content += f"parameters: {data['parameters']}\n"
        
        return yaml_content
    
    def export_protocol_summary(self) -> str:
        """Export a human-readable protocol summary"""
        data = self.get_data()
        usage = self.get_component_usage()
        actions = self.get_action_summary()
        
        summary = f"""
📋 Protocol Summary
══════════════════
📝 Information:
   • Name: {data.get('name', 'Unnamed')}
   • Description: {data.get('description', 'No description')}
   • Created: {data.get('created', 'Unknown')}
   • Last Modified: {data.get('last_modified', 'Unknown')}

📊 Overview:
   • Total Procedures: {len(data.get('procedures', []))}
   • Components Used: {len(usage)}
   • Unique Actions: {len(actions)}
   • Duration: {self.get_protocol_duration()}

🔧 Component Usage:
        """
        
        for component, count in sorted(usage.items()):
            summary += f"\n   • {component}: {count} procedure{'s' if count != 1 else ''}"
        
        summary += "\n\n⚡ Action Summary:"
        for action, count in sorted(actions.items()):
            summary += f"\n   • {action}: {count} time{'s' if count != 1 else ''}"
        
        summary += "\n\n📋 Procedure Details:"
        for i, proc in enumerate(data.get("procedures", []), 1):
            summary += f"\n   {i}. {proc.get('component', 'unknown')} - {proc.get('action', 'unknown')}"
            if proc.get("start_time"):
                summary += f" (start: {proc['start_time']})"
            if proc.get("duration"):
                summary += f" (duration: {proc['duration']})"
        
        return summary.strip()