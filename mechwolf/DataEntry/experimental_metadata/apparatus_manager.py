"""
Apparatus Data Manager - Handles apparatus configuration and components

This module manages the apparatus section of experimental metadata, including
active components (pumps, valves), passive components (vessels, tubes),
and their connections.
"""

from typing import Dict, Any, List, Optional, Union


class ApparatusDataManager:
    """
    Manager for apparatus-related experimental data
    
    Handles:
    - Active components (pumps, valves, sensors)
    - Passive components (vessels, tubes, mixers)
    - Component connections and topology
    - Calibration data
    """
    
    def __init__(self, metadata_manager):
        """Initialize with reference to main metadata manager"""
        self.metadata_manager = metadata_manager
        self.section_name = "apparatus_config"
    
    def get_data(self) -> Dict[str, Any]:
        """Get the apparatus section data"""
        return self.metadata_manager.get_section_data(self.section_name)
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save apparatus section data"""
        return self.metadata_manager.update_section_data(self.section_name, data)
    
    # Basic Configuration
    def set_apparatus_info(self, name: str, description: str = "") -> bool:
        """Set basic apparatus information"""
        data = self.get_data()
        data["name"] = name
        data["description"] = description
        return self.save_data(data)
    
    # Component Management
    def add_active_component(self, component: Dict[str, Any]) -> bool:
        """
        Add an active component (pump, valve, sensor)
        
        Args:
            component: Dictionary with component properties
                Required: type, name
                Optional: category, serial_port, parameters
        
        Returns:
            True if added successfully
        """
        if not component.get("type") or not component.get("name"):
            print("❌ Component must have 'type' and 'name'")
            return False
        
        data = self.get_data()
        if "components" not in data:
            data["components"] = {"active": [], "passive": []}
        if "active" not in data["components"]:
            data["components"]["active"] = []
        
        # Check for duplicate names
        existing_names = [c.get("name") for c in data["components"]["active"]]
        if component["name"] in existing_names:
            print(f"⚠️  Active component '{component['name']}' already exists")
            return False
        
        data["components"]["active"].append(component)
        return self.save_data(data)
    
    def add_passive_component(self, component: Dict[str, Any]) -> bool:
        """
        Add a passive component (vessel, tube, mixer)
        
        Args:
            component: Dictionary with component properties
                Required: type, name
                Optional: category, parameters
        
        Returns:
            True if added successfully
        """
        if not component.get("type") or not component.get("name"):
            print("❌ Component must have 'type' and 'name'")
            return False
        
        data = self.get_data()
        if "components" not in data:
            data["components"] = {"active": [], "passive": []}
        if "passive" not in data["components"]:
            data["components"]["passive"] = []
        
        # Check for duplicate names
        existing_names = [c.get("name") for c in data["components"]["passive"]]
        if component["name"] in existing_names:
            print(f"⚠️  Passive component '{component['name']}' already exists")
            return False
        
        data["components"]["passive"].append(component)
        return self.save_data(data)
    
    def update_component(self, component_name: str, updates: Dict[str, Any], 
                        component_type: str = "auto") -> bool:
        """
        Update an existing component
        
        Args:
            component_name: Name of component to update
            updates: Dictionary of updates to apply
            component_type: "active", "passive", or "auto" to search both
        
        Returns:
            True if updated successfully
        """
        data = self.get_data()
        
        if component_type in ["active", "auto"]:
            for i, comp in enumerate(data.get("components", {}).get("active", [])):
                if comp.get("name") == component_name:
                    data["components"]["active"][i].update(updates)
                    return self.save_data(data)
        
        if component_type in ["passive", "auto"]:
            for i, comp in enumerate(data.get("components", {}).get("passive", [])):
                if comp.get("name") == component_name:
                    data["components"]["passive"][i].update(updates)
                    return self.save_data(data)
        
        print(f"❌ Component '{component_name}' not found")
        return False
    
    def remove_component(self, component_name: str, component_type: str = "auto") -> bool:
        """
        Remove a component
        
        Args:
            component_name: Name of component to remove
            component_type: "active", "passive", or "auto" to search both
        
        Returns:
            True if removed successfully
        """
        data = self.get_data()
        removed = False
        
        if component_type in ["active", "auto"]:
            active_components = data.get("components", {}).get("active", [])
            new_active = [c for c in active_components if c.get("name") != component_name]
            if len(new_active) < len(active_components):
                data["components"]["active"] = new_active
                removed = True
        
        if component_type in ["passive", "auto"]:
            passive_components = data.get("components", {}).get("passive", [])
            new_passive = [c for c in passive_components if c.get("name") != component_name]
            if len(new_passive) < len(passive_components):
                data["components"]["passive"] = new_passive
                removed = True
        
        if removed:
            # Also remove any connections involving this component
            self._remove_connections_with_component(component_name, data)
            return self.save_data(data)
        else:
            print(f"❌ Component '{component_name}' not found")
            return False
    
    # Connection Management
    def add_connection(self, connection: Dict[str, Any]) -> bool:
        """
        Add a connection between components
        
        Args:
            connection: Dictionary with connection properties
                Required: from, to
                Optional: tube, from_type, to_type, tube_type
        
        Returns:
            True if added successfully
        """
        if not connection.get("from") or not connection.get("to"):
            print("❌ Connection must have 'from' and 'to' components")
            return False
        
        data = self.get_data()
        if "connections" not in data:
            data["connections"] = []
        
        # Validate that components exist
        all_component_names = self.get_all_component_names()
        if connection["from"] not in all_component_names:
            print(f"❌ Component '{connection['from']}' not found")
            return False
        if connection["to"] not in all_component_names:
            print(f"❌ Component '{connection['to']}' not found")
            return False
        
        # Check for duplicate connections
        existing_connections = [
            (c.get("from"), c.get("to")) for c in data["connections"]
        ]
        new_connection = (connection["from"], connection["to"])
        if new_connection in existing_connections:
            print(f"⚠️  Connection from '{connection['from']}' to '{connection['to']}' already exists")
            return False
        
        data["connections"].append(connection)
        return self.save_data(data)
    
    def remove_connection(self, from_component: str, to_component: str) -> bool:
        """Remove a specific connection"""
        data = self.get_data()
        
        original_count = len(data.get("connections", []))
        data["connections"] = [
            c for c in data.get("connections", [])
            if not (c.get("from") == from_component and c.get("to") == to_component)
        ]
        
        if len(data["connections"]) < original_count:
            return self.save_data(data)
        else:
            print(f"❌ Connection from '{from_component}' to '{to_component}' not found")
            return False
    
    def clear_all_connections(self) -> bool:
        """Clear all connections"""
        data = self.get_data()
        data["connections"] = []
        return self.save_data(data)
    
    # Bulk Operations
    def configure_components(self, components: Dict[str, List[Dict[str, Any]]], 
                           component_types: Dict[str, Dict[str, Any]] = None) -> bool:
        """
        Configure multiple components at once
        
        Args:
            components: Dictionary with 'active' and/or 'passive' component lists
            component_types: Optional registry of component type definitions (new format)
        
        Returns:
            True if configured successfully
        """
        data = self.get_data()
        
        if "components" not in data:
            data["components"] = {"active": [], "passive": []}
        
        if "active" in components:
            data["components"]["active"] = components["active"]
        
        if "passive" in components:
            data["components"]["passive"] = components["passive"]
        
        # Store component types registry if provided (new format)
        if component_types is not None:
            data["component_types"] = component_types
        
        return self.save_data(data)
    
    def configure_connections(self, connections: List[Dict[str, Any]]) -> bool:
        """Configure multiple connections at once"""
        data = self.get_data()
        data["connections"] = connections
        return self.save_data(data)
    
    # Query Methods
    def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific component by name"""
        data = self.get_data()
        
        # Search active components
        for comp in data.get("components", {}).get("active", []):
            if comp.get("name") == name:
                return comp.copy()
        
        # Search passive components
        for comp in data.get("components", {}).get("passive", []):
            if comp.get("name") == name:
                return comp.copy()
        
        return None
    
    def get_all_component_names(self) -> List[str]:
        """Get names of all components"""
        data = self.get_data()
        names = []
        
        # Add active component names
        names.extend([
            comp.get("name") for comp in data.get("components", {}).get("active", [])
            if comp.get("name")
        ])
        
        # Add passive component names
        names.extend([
            comp.get("name") for comp in data.get("components", {}).get("passive", [])
            if comp.get("name")
        ])
        
        return names
    
    def get_components_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        """Get all components of a specific type (e.g., 'VarianPump', 'Vessel')"""
        data = self.get_data()
        components = []
        
        # Search active components
        components.extend([
            comp.copy() for comp in data.get("components", {}).get("active", [])
            if comp.get("type") == component_type
        ])
        
        # Search passive components
        components.extend([
            comp.copy() for comp in data.get("components", {}).get("passive", [])
            if comp.get("type") == component_type
        ])
        
        return components
    
    def get_component_count(self) -> Dict[str, int]:
        """Get count of components by category"""
        data = self.get_data()
        return {
            "active": len(data.get("components", {}).get("active", [])),
            "passive": len(data.get("components", {}).get("passive", [])),
            "total": (len(data.get("components", {}).get("active", [])) + 
                     len(data.get("components", {}).get("passive", [])))
        }
    
    def get_connections_for_component(self, component_name: str) -> List[Dict[str, Any]]:
        """Get all connections involving a specific component"""
        data = self.get_data()
        connections = []
        
        for conn in data.get("connections", []):
            if conn.get("from") == component_name or conn.get("to") == component_name:
                connections.append(conn.copy())
        
        return connections
    
    def get_apparatus_topology(self) -> Dict[str, List[str]]:
        """Get apparatus topology as adjacency list"""
        data = self.get_data()
        topology = {}
        
        # Initialize all components
        for comp_name in self.get_all_component_names():
            topology[comp_name] = []
        
        # Add connections
        for conn in data.get("connections", []):
            from_comp = conn.get("from")
            to_comp = conn.get("to")
            if from_comp and to_comp:
                if from_comp not in topology:
                    topology[from_comp] = []
                topology[from_comp].append(to_comp)
        
        return topology
    
    # Validation
    def validate_apparatus(self) -> List[str]:
        """Validate apparatus configuration and return any issues"""
        issues = []
        data = self.get_data()
        
        # Check for components without names
        for comp in data.get("components", {}).get("active", []):
            if not comp.get("name"):
                issues.append(f"Active component missing name: {comp}")
        
        for comp in data.get("components", {}).get("passive", []):
            if not comp.get("name"):
                issues.append(f"Passive component missing name: {comp}")
        
        # Check for connections to non-existent components
        all_names = set(self.get_all_component_names())
        for conn in data.get("connections", []):
            if conn.get("from") and conn.get("from") not in all_names:
                issues.append(f"Connection references non-existent component: '{conn.get('from')}'")
            if conn.get("to") and conn.get("to") not in all_names:
                issues.append(f"Connection references non-existent component: '{conn.get('to')}'")
        
        # Check for duplicate component names
        all_names_list = self.get_all_component_names()
        seen_names = set()
        for name in all_names_list:
            if name in seen_names:
                issues.append(f"Duplicate component name: '{name}'")
            seen_names.add(name)
        
        return issues
    
    # Calibration Data
    def set_calibration_data(self, component_name: str, calibration: Dict[str, Any]) -> bool:
        """Set calibration data for a component"""
        data = self.get_data()
        if "calibration_data" not in data:
            data["calibration_data"] = {}
        
        data["calibration_data"][component_name] = calibration
        return self.save_data(data)
    
    def get_calibration_data(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get calibration data for a component"""
        data = self.get_data()
        return data.get("calibration_data", {}).get(component_name)
    
    # Component Types Registry Methods
    def get_component_types_registry(self) -> Dict[str, Dict[str, Any]]:
        """Get the component types registry"""
        data = self.get_data()
        return data.get("component_types", {})
    
    def set_component_types_registry(self, component_types: Dict[str, Dict[str, Any]]) -> bool:
        """Set the component types registry"""
        data = self.get_data()
        data["component_types"] = component_types
        return self.save_data(data)
    
    def ensure_component_types_registry(self) -> bool:
        """Ensure component types registry exists and is populated"""
        data = self.get_data()
        
        if "component_types" not in data:
            data["component_types"] = {}
        
        # Collect all unique component types from existing components
        all_types = set()
        for comp in data.get("components", {}).get("active", []):
            all_types.add(comp.get("type"))
        for comp in data.get("components", {}).get("passive", []):
            all_types.add(comp.get("type"))
        
        # Add missing component types to registry
        from ..Phase2_ApparatusBuilder.registry import ComponentRegistry
        registry_updated = False
        
        for comp_type in all_types:
            if comp_type and comp_type not in data["component_types"]:
                # Get registry info from ComponentRegistry
                registry_info = ComponentRegistry.get_component_info(comp_type)
                data["component_types"][comp_type] = registry_info
                registry_updated = True
        
        if registry_updated:
            return self.save_data(data)
        return True
    
    def convert_to_compact_format(self) -> bool:
        """Convert apparatus config from verbose to compact format"""
        data = self.get_data()
        
        # Ensure component types registry exists
        self.ensure_component_types_registry()
        data = self.get_data()  # Refresh data
        
        # Process components to remove embedded registry_info
        components_updated = False
        
        for comp_list in [data.get("components", {}).get("active", []), 
                         data.get("components", {}).get("passive", [])]:
            for comp in comp_list:
                if "registry_info" in comp:
                    # Remove embedded registry_info (it's now in component_types)
                    del comp["registry_info"]
                    components_updated = True
        
        if components_updated:
            return self.save_data(data)
        return True

    # Helper Methods
    def _remove_connections_with_component(self, component_name: str, data: Dict[str, Any]) -> None:
        """Remove all connections involving a specific component"""
        if "connections" not in data:
            return
        
        data["connections"] = [
            conn for conn in data["connections"]
            if conn.get("from") != component_name and conn.get("to") != component_name
        ]
    
    def export_apparatus_summary(self) -> str:
        """Export a human-readable apparatus summary"""
        data = self.get_data()
        counts = self.get_component_count()
        
        summary = f"""
⚙️  Apparatus Summary
═══════════════════
📋 Configuration:
   • Name: {data.get('name', 'Unnamed')}
   • Description: {data.get('description', 'No description')}

📊 Component Count:
   • Active Components: {counts['active']}
   • Passive Components: {counts['passive']}
   • Total: {counts['total']}
   • Connections: {len(data.get('connections', []))}

🔧 Active Components:
        """
        
        for comp in data.get("components", {}).get("active", []):
            summary += f"\n   • {comp.get('name')} ({comp.get('type')})"
            if comp.get("serial_port"):
                summary += f" - {comp.get('serial_port')}"
        
        summary += "\n\n📦 Passive Components:"
        for comp in data.get("components", {}).get("passive", []):
            summary += f"\n   • {comp.get('name')} ({comp.get('type')})"
        
        summary += "\n\n🔗 Connections:"
        for conn in data.get("connections", []):
            tube_info = f" via {conn.get('tube')}" if conn.get('tube') else ""
            summary += f"\n   • {conn.get('from')} → {conn.get('to')}{tube_info}"
        
        return summary.strip()