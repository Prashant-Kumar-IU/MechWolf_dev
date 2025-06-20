"""
Connection Validator - Validates apparatus connections for flow chemistry logic

This module provides validation for component connections to ensure they
follow proper flow chemistry principles and avoid common errors.
"""
from typing import Dict, List, Any, Set, Tuple, Optional
import networkx as nx


class ConnectionValidator:
    """Validates component connections for flow chemistry apparatus"""
    
    def __init__(self):
        # Define connection rules for different component types
        self.connection_rules = self._initialize_connection_rules()
        
        # Common validation errors and suggestions
        self.error_messages = {
            'vessel_to_vessel': "Vessels should not connect directly to other vessels without active components",
            'pump_to_pump': "Pumps should not connect directly to other pumps",
            'valve_output_multiple': "Valves should typically have only one output connection",
            'vessel_multiple_inputs': "Vessels should typically have only one input connection",
            'sensor_connection': "Sensors should be placed in series with the flow stream",
            'circular_dependency': "Connection creates a circular dependency in the flow path",
            'isolated_component': "Component would become isolated from the flow path",
            'invalid_tube_usage': "Tube configuration may not be suitable for this connection",
            'flow_direction': "Check flow direction - this connection may cause flow issues"
        }
    
    def _initialize_connection_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize connection rules for different component types"""
        return {
            'Vessel': {
                'can_connect_to': ['Pump', 'Valve', 'Sensor'],
                'can_receive_from': ['Pump', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer', 'Sensor'],
                'max_inputs': 1,
                'max_outputs': 1,
                'flow_role': 'source_or_sink'
            },
            'Pump': {
                'can_connect_to': ['Vessel', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer', 'Sensor', 'TempControl'],
                'can_receive_from': ['Vessel', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer'],
                'max_inputs': 1,
                'max_outputs': 1,
                'flow_role': 'active_transport'
            },
            'Valve': {
                'can_connect_to': ['Pump', 'Vessel', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer', 'Sensor'],
                'can_receive_from': ['Vessel', 'Pump', 'Sensor'],
                'max_inputs': None,  # Multiple inputs allowed
                'max_outputs': 1,
                'flow_role': 'flow_control'
            },
            'Mixer': {
                'can_connect_to': ['Vessel', 'Pump', 'Valve', 'Sensor', 'TempControl'],
                'can_receive_from': ['Pump', 'Valve', 'Sensor'],
                'max_inputs': None,
                'max_outputs': 1,
                'flow_role': 'mixing'
            },
            'TMixer': {
                'can_connect_to': ['Vessel', 'Pump', 'Valve', 'Sensor', 'TempControl'],
                'can_receive_from': ['Pump', 'Valve', 'Sensor'],
                'max_inputs': 2,  # T-mixer typically has 2 inputs
                'max_outputs': 1,
                'flow_role': 'mixing'
            },
            'CrossMixer': {
                'can_connect_to': ['Vessel', 'Pump', 'Valve', 'Sensor', 'TempControl'],
                'can_receive_from': ['Pump', 'Valve', 'Sensor'],
                'max_inputs': 4,  # Cross mixer can have up to 4 inputs
                'max_outputs': 1,
                'flow_role': 'mixing'
            },
            'YMixer': {
                'can_connect_to': ['Vessel', 'Pump', 'Valve', 'Sensor', 'TempControl'],
                'can_receive_from': ['Pump', 'Valve', 'Sensor'],
                'max_inputs': 2,  # Y-mixer typically has 2 inputs
                'max_outputs': 1,
                'flow_role': 'mixing'
            },
            'Sensor': {
                'can_connect_to': ['Vessel', 'Pump', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer', 'TempControl'],
                'can_receive_from': ['Pump', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer'],
                'max_inputs': 1,
                'max_outputs': 1,
                'flow_role': 'monitoring'
            },
            'TempControl': {
                'can_connect_to': ['Vessel', 'Pump', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer', 'Sensor'],
                'can_receive_from': ['Pump', 'Valve', 'Mixer', 'TMixer', 'CrossMixer', 'YMixer', 'Sensor'],
                'max_inputs': 1,
                'max_outputs': 1,
                'flow_role': 'temperature_control'
            }
        }
    
    def validate_connection(self, from_comp: Dict[str, Any], to_comp: Dict[str, Any], 
                          tube: Dict[str, Any], existing_connections: List[Dict[str, Any]]) -> List[str]:
        """
        Validate a single connection between two components
        
        Args:
            from_comp: Source component data
            to_comp: Destination component data  
            tube: Tube component data
            existing_connections: List of existing connections
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        from_type = from_comp.get('type', '')
        to_type = to_comp.get('type', '')
        from_name = from_comp.get('name', '')
        to_name = to_comp.get('name', '')
        
        # Basic connection compatibility
        errors.extend(self._validate_basic_compatibility(from_type, to_type))
        
        # Check connection limits
        errors.extend(self._validate_connection_limits(
            from_comp, to_comp, existing_connections
        ))
        
        # Tube suitability
        errors.extend(self._validate_tube_suitability(
            from_comp, to_comp, tube
        ))
        
        # Flow chemistry logic
        errors.extend(self._validate_flow_logic(
            from_comp, to_comp, existing_connections
        ))
        
        return errors
    
    def validate_complete_apparatus(self, components: Dict[str, Dict[str, Any]], 
                                  connections: List[Dict[str, Any]]) -> List[str]:
        """
        Validate the complete apparatus for flow chemistry principles
        
        Args:
            components: Dictionary of all components
            connections: List of all connections
        
        Returns:
            List of validation errors and warnings
        """
        errors = []
        
        if not connections:
            return ["Apparatus has no connections"]
        
        # Build network graph
        graph = self._build_network_graph(components, connections)
        
        # Check connectivity
        errors.extend(self._validate_network_connectivity(graph, components))
        
        # Check for cycles
        errors.extend(self._validate_flow_cycles(graph))
        
        # Check component roles
        errors.extend(self._validate_component_roles(components, connections))
        
        # Check for isolated components
        errors.extend(self._validate_component_isolation(components, connections))
        
        return errors
    
    def _validate_basic_compatibility(self, from_type: str, to_type: str) -> List[str]:
        """Validate basic compatibility between component types"""
        errors = []
        
        # Get connection rules
        from_rules = self.connection_rules.get(from_type, {})
        to_rules = self.connection_rules.get(to_type, {})
        
        # Check if from_component can connect to to_component
        allowed_targets = from_rules.get('can_connect_to', [])
        if allowed_targets and to_type not in allowed_targets:
            errors.append(f"{from_type} cannot connect directly to {to_type}")
        
        # Check if to_component can receive from from_component
        allowed_sources = to_rules.get('can_receive_from', [])
        if allowed_sources and from_type not in allowed_sources:
            errors.append(f"{to_type} cannot receive connection from {from_type}")
        
        # Special case checks
        if from_type == 'Vessel' and to_type == 'Vessel':
            errors.append(self.error_messages['vessel_to_vessel'])
        
        if 'Pump' in from_type and 'Pump' in to_type:
            errors.append(self.error_messages['pump_to_pump'])
        
        return errors
    
    def _validate_connection_limits(self, from_comp: Dict[str, Any], to_comp: Dict[str, Any],
                                  existing_connections: List[Dict[str, Any]]) -> List[str]:
        """Validate connection limits for components"""
        errors = []
        
        from_type = from_comp.get('type', '')
        to_type = to_comp.get('type', '')
        from_name = from_comp.get('name', '')
        to_name = to_comp.get('name', '')
        
        # Count existing connections
        from_outputs = sum(1 for conn in existing_connections if conn['from'] == from_name)
        to_inputs = sum(1 for conn in existing_connections if conn['to'] == to_name)
        
        # Check output limits
        from_rules = self.connection_rules.get(from_type, {})
        max_outputs = from_rules.get('max_outputs')
        if max_outputs is not None and from_outputs >= max_outputs:
            errors.append(f"{from_name} already has {from_outputs} output connection(s), maximum is {max_outputs}")
        
        # Check input limits
        to_rules = self.connection_rules.get(to_type, {})
        max_inputs = to_rules.get('max_inputs')
        if max_inputs is not None and to_inputs >= max_inputs:
            errors.append(f"{to_name} already has {to_inputs} input connection(s), maximum is {max_inputs}")
        
        return errors
    
    def _validate_tube_suitability(self, from_comp: Dict[str, Any], to_comp: Dict[str, Any],
                                 tube: Dict[str, Any]) -> List[str]:
        """Validate tube suitability for the connection"""
        errors = []
        warnings = []
        
        tube_preset = tube.get('preset', 'custom')
        tube_length = tube.get('length', '')
        
        # Extract length value for analysis
        length_val = self._extract_length_value(tube_length)
        
        # Check for very long connections that might cause issues
        if length_val and length_val > 20:  # > 20 feet
            warnings.append(f"Long tube connection ({tube_length}) may cause significant pressure drop")
        
        # Check tube type suitability based on components
        from_type = from_comp.get('type', '')
        to_type = to_comp.get('type', '')
        
        # Pumps typically need smaller diameter tubing for better control
        if 'Pump' in from_type and tube_preset == 'fat_tube':
            warnings.append("Fat tube after pump may reduce flow control precision")
        
        # Mixers might benefit from specific tube configurations
        if 'Mixer' in to_type and tube_preset == 'thinner_tube' and length_val and length_val < 0.5:
            warnings.append("Very short connection to mixer may not allow proper mixing")
        
        # Convert warnings to errors for critical issues only
        # For now, we'll just note them without blocking the connection
        
        return errors
    
    def _validate_flow_logic(self, from_comp: Dict[str, Any], to_comp: Dict[str, Any],
                           existing_connections: List[Dict[str, Any]]) -> List[str]:
        """Validate flow chemistry logic"""
        errors = []
        
        from_type = from_comp.get('type', '')
        to_type = to_comp.get('type', '')
        from_name = from_comp.get('name', '')
        to_name = to_comp.get('name', '')
        
        # Check for potential flow direction issues
        if from_type == 'Vessel' and to_type == 'Vessel':
            # Check if there's an active component in between via existing connections
            has_active_path = self._check_active_path_exists(from_name, to_name, existing_connections)
            if not has_active_path:
                errors.append("Direct vessel-to-vessel connection requires active pumping")
        
        # Check mixer input logic
        if 'Mixer' in to_type:
            mixer_inputs = [conn for conn in existing_connections if conn['to'] == to_name]
            
            if to_type == 'TMixer' and len(mixer_inputs) >= 2:
                errors.append("T-Mixer already has 2 inputs (typical maximum)")
            elif to_type == 'YMixer' and len(mixer_inputs) >= 2:
                errors.append("Y-Mixer already has 2 inputs (typical maximum)")
        
        return errors
    
    def _build_network_graph(self, components: Dict[str, Dict[str, Any]], 
                           connections: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build a NetworkX directed graph from connections"""
        G = nx.DiGraph()
        
        # Add nodes (components)
        for comp_name, comp_data in components.items():
            G.add_node(comp_data['name'], **comp_data)
        
        # Add edges (connections)
        for conn in connections:
            G.add_edge(conn['from'], conn['to'], tube=conn['tube'])
        
        return G
    
    def _validate_network_connectivity(self, graph: nx.DiGraph, 
                                     components: Dict[str, Dict[str, Any]]) -> List[str]:
        """Validate network connectivity"""
        errors = []
        
        # Convert to undirected for connectivity check
        undirected = graph.to_undirected()
        
        # Check if all components are connected
        if not nx.is_connected(undirected):
            connected_components = list(nx.connected_components(undirected))
            if len(connected_components) > 1:
                errors.append(f"Apparatus has {len(connected_components)} disconnected sections")
        
        return errors
    
    def _validate_flow_cycles(self, graph: nx.DiGraph) -> List[str]:
        """Check for problematic flow cycles"""
        errors = []
        
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                for cycle in cycles:
                    cycle_str = " → ".join(cycle + [cycle[0]])
                    errors.append(f"Flow cycle detected: {cycle_str}")
        except:
            # NetworkX might fail on very large graphs
            pass
        
        return errors
    
    def _validate_component_roles(self, components: Dict[str, Dict[str, Any]], 
                                connections: List[Dict[str, Any]]) -> List[str]:
        """Validate that components are used in appropriate roles"""
        errors = []
        
        # Check for missing essential components
        has_source = False
        has_sink = False
        has_pump = False
        
        for comp_data in components.values():
            comp_type = comp_data.get('type', '')
            
            if comp_type == 'Vessel':
                comp_name = comp_data.get('name', '')
                # Check if vessel is source (no inputs) or sink (no outputs)
                has_input = any(conn['to'] == comp_name for conn in connections)
                has_output = any(conn['from'] == comp_name for conn in connections)
                
                if not has_input:
                    has_source = True
                if not has_output:
                    has_sink = True
            
            elif 'Pump' in comp_type:
                has_pump = True
        
        if not has_source:
            errors.append("Apparatus should have at least one source vessel (vessel with no inputs)")
        
        if not has_sink:
            errors.append("Apparatus should have at least one product/waste vessel (vessel with no outputs)")
        
        if not has_pump:
            errors.append("Apparatus should have at least one pump for fluid transport")
        
        return errors
    
    def _validate_component_isolation(self, components: Dict[str, Dict[str, Any]], 
                                    connections: List[Dict[str, Any]]) -> List[str]:
        """Check for isolated components"""
        errors = []
        
        connected_components = set()
        
        for conn in connections:
            connected_components.add(conn['from'])
            connected_components.add(conn['to'])
        
        for comp_data in components.values():
            comp_name = comp_data.get('name', '')
            if comp_name not in connected_components:
                comp_type = comp_data.get('type', '')
                errors.append(f"Component {comp_name} ({comp_type}) is not connected to the apparatus")
        
        return errors
    
    def _check_active_path_exists(self, from_name: str, to_name: str, 
                                connections: List[Dict[str, Any]]) -> bool:
        """Check if there's an active component between two components"""
        # This is a simplified check - could be enhanced with proper path finding
        for conn in connections:
            if (conn['from'] == from_name or conn['to'] == to_name):
                # Check if the other component is active
                other_comp = conn['to'] if conn['from'] == from_name else conn['from']
                # This would need component type information to determine if active
                # For now, assume any non-vessel component is potentially active
                return True
        return False
    
    def _extract_length_value(self, length_str: str) -> Optional[float]:
        """Extract numeric value from length string"""
        if not length_str:
            return None
        
        try:
            # Simple extraction - could be enhanced
            import re
            match = re.match(r'(\d+(?:\.\d+)?)', length_str)
            if match:
                value = float(match.group(1))
                
                # Convert to feet for comparison
                if 'cm' in length_str:
                    value = value / 30.48  # cm to feet
                elif 'mm' in length_str:
                    value = value / 304.8  # mm to feet
                elif 'm' in length_str and 'mm' not in length_str:
                    value = value * 3.28084  # m to feet
                elif 'in' in length_str:
                    value = value / 12  # inches to feet
                
                return value
        except:
            pass
        
        return None
    
    def get_connection_suggestions(self, from_comp: Dict[str, Any], 
                                 components: Dict[str, Dict[str, Any]]) -> List[str]:
        """Get suggestions for valid connections from a component"""
        suggestions = []
        
        from_type = from_comp.get('type', '')
        from_rules = self.connection_rules.get(from_type, {})
        allowed_targets = from_rules.get('can_connect_to', [])
        
        for comp_data in components.values():
            comp_type = comp_data.get('type', '')
            comp_name = comp_data.get('name', '')
            
            if comp_type in allowed_targets and comp_name != from_comp.get('name'):
                suggestions.append(comp_name)
        
        return suggestions