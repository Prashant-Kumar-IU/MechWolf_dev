"""
Apparatus Validator

Comprehensive validation system for apparatus configurations.
Checks for flow chemistry rules, component compatibility, and safety considerations.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
import re


class ApparatusValidator:
    """Comprehensive apparatus validation system"""
    
    def __init__(self):
        """Initialize validator with validation rules"""
        
        # Define component categories
        self.source_components = {'Vessel'}
        self.pump_components = {'HarvardSyringePump', 'VarianPump', 'FreeStepPump'}
        self.mixing_components = {'TMixer', 'CrossMixer', 'YMixer'}
        self.destination_components = {'Vessel', 'Reactor'}
        self.connecting_components = {'Tube'}
        self.sensor_components = {'Sensor'}
        
        # Define flow chemistry rules
        self.flow_rules = {
            'max_pressure_drop': 100,  # psi
            'max_flow_rate': 100,     # mL/min
            'min_tubing_id': 0.010,   # inches
            'max_dead_volume': 5.0    # mL
        }
        
        # Compatible material combinations
        self.material_compatibility = {
            'PFA': ['Glass', 'PTFE', 'FEP', 'Stainless Steel', 'PEEK'],
            'PTFE': ['Glass', 'PFA', 'FEP', 'Stainless Steel', 'PEEK'],
            'Glass': ['PFA', 'PTFE', 'FEP', 'PEEK'],
            'Stainless Steel': ['PFA', 'PTFE', 'FEP', 'PEEK'],
            'PEEK': ['PFA', 'PTFE', 'Glass', 'Stainless Steel']
        }
        
    def validate_apparatus(self, apparatus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive apparatus validation
        
        Args:
            apparatus_data: Apparatus configuration data
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'component_analysis': {},
            'flow_analysis': {},
            'safety_analysis': {}
        }
        
        try:
            components = apparatus_data.get('components', {})
            connections = apparatus_data.get('connections', [])
            
            # Component validation
            results['component_analysis'] = self._validate_components(components)
            if results['component_analysis']['errors']:
                results['valid'] = False
                results['errors'].extend(results['component_analysis']['errors'])
            results['warnings'].extend(results['component_analysis']['warnings'])
            results['suggestions'].extend(results['component_analysis']['suggestions'])
            
            # Connection validation
            connection_results = self._validate_connections(connections, components)
            if connection_results['errors']:
                results['valid'] = False
                results['errors'].extend(connection_results['errors'])
            results['warnings'].extend(connection_results['warnings'])
            results['suggestions'].extend(connection_results['suggestions'])
            
            # Flow path validation
            results['flow_analysis'] = self._validate_flow_paths(connections, components)
            if results['flow_analysis']['errors']:
                results['valid'] = False
                results['errors'].extend(results['flow_analysis']['errors'])
            results['warnings'].extend(results['flow_analysis']['warnings'])
            
            # Safety validation
            results['safety_analysis'] = self._validate_safety(components, connections)
            results['warnings'].extend(results['safety_analysis']['warnings'])
            results['suggestions'].extend(results['safety_analysis']['suggestions'])
            
            # Material compatibility
            material_results = self._validate_material_compatibility(components, connections)
            if material_results['errors']:
                results['valid'] = False
                results['errors'].extend(material_results['errors'])
            results['warnings'].extend(material_results['warnings'])
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Validation error: {e}")
        
        return results
    
    def _validate_components(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual components"""
        results = {
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'component_count': {
                'active': 0,
                'passive': 0,
                'pumps': 0,
                'mixers': 0,
                'vessels': 0
            }
        }
        
        active_components = components.get('active', [])
        passive_components = components.get('passive', [])
        
        results['component_count']['active'] = len(active_components)
        results['component_count']['passive'] = len(passive_components)
        
        # Validate active components
        for component in active_components:
            component_errors = self._validate_individual_component(component, 'active')
            results['errors'].extend(component_errors)
            
            # Count pump types
            if component.get('type') in self.pump_components:
                results['component_count']['pumps'] += 1
        
        # Validate passive components
        for component in passive_components:
            component_errors = self._validate_individual_component(component, 'passive')
            results['errors'].extend(component_errors)
            
            # Count component types
            comp_type = component.get('type')
            if comp_type in self.mixing_components:
                results['component_count']['mixers'] += 1
            elif comp_type == 'Vessel':
                results['component_count']['vessels'] += 1
        
        # Check for minimum required components
        if results['component_count']['pumps'] == 0:
            results['warnings'].append("No pumps configured - apparatus may not be functional")
        
        if results['component_count']['vessels'] < 2:
            results['warnings'].append("At least 2 vessels recommended (source and destination)")
        
        # Check for component naming conflicts
        all_names = []
        for component in active_components + passive_components:
            name = component.get('name')
            if name:
                if name in all_names:
                    results['errors'].append(f"Duplicate component name: {name}")
                all_names.append(name)
        
        return results
    
    def _validate_individual_component(self, component: Dict[str, Any], category: str) -> List[str]:
        """Validate a single component"""
        errors = []
        
        # Basic validation
        if not component.get('name'):
            errors.append(f"Component missing name in {category} components")
        
        if not component.get('type'):
            errors.append(f"Component missing type in {category} components")
        
        comp_type = component.get('type')
        parameters = component.get('parameters', {})
        
        # Type-specific validation
        if comp_type == 'HarvardSyringePump':
            if not parameters.get('serial_port'):
                errors.append(f"Harvard pump {component.get('name')} missing serial port")
            if not parameters.get('syringe_volume'):
                errors.append(f"Harvard pump {component.get('name')} missing syringe volume")
        
        elif comp_type == 'VarianPump':
            if not parameters.get('serial_port'):
                errors.append(f"Varian pump {component.get('name')} missing serial port")
            if not parameters.get('max_rate'):
                errors.append(f"Varian pump {component.get('name')} missing max rate")
        
        elif comp_type == 'Tube':
            if not parameters.get('length'):
                errors.append(f"Tube {component.get('name')} missing length")
            if not parameters.get('ID'):
                errors.append(f"Tube {component.get('name')} missing inner diameter")
            
            # Validate tube dimensions
            try:
                id_str = parameters.get('ID', '')
                if 'in' in id_str:
                    # Convert to numeric for validation
                    id_value = self._parse_dimension(id_str)
                    if id_value < 0.010:  # 0.010 inches
                        errors.append(f"Tube {component.get('name')} ID too small (< 0.010 in)")
                    elif id_value > 0.5:  # 0.5 inches
                        errors.append(f"Tube {component.get('name')} ID unusually large (> 0.5 in)")
            except:
                errors.append(f"Tube {component.get('name')} has invalid ID format")
        
        elif comp_type == 'Vessel':
            if not parameters.get('description'):
                errors.append(f"Vessel {component.get('name')} missing description")
        
        return errors
    
    def _parse_dimension(self, dimension_str: str) -> float:
        """Parse dimension string to numeric value in inches"""
        if not dimension_str:
            return 0.0
        
        # Handle fractions like "1/16 in"
        if '/' in dimension_str:
            parts = dimension_str.split()
            fraction_part = parts[0]
            numerator, denominator = fraction_part.split('/')
            return float(numerator) / float(denominator)
        
        # Handle decimals like "0.030 in"
        return float(dimension_str.split()[0])
    
    def _validate_connections(self, connections: List[Dict[str, Any]], 
                            components: Dict[str, Any]) -> Dict[str, Any]:
        """Validate apparatus connections"""
        results = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if not connections:
            results['warnings'].append("No connections configured - apparatus will not function")
            return results
        
        # Get all component names for validation
        all_components = components.get('active', []) + components.get('passive', [])
        component_names = {comp.get('name'): comp for comp in all_components}
        
        for i, connection in enumerate(connections):
            from_name = connection.get('from')
            to_name = connection.get('to')
            tube_name = connection.get('tube')
            
            # Check component existence
            if from_name not in component_names:
                results['errors'].append(f"Connection {i+1}: 'from' component '{from_name}' not found")
                continue
            
            if to_name not in component_names:
                results['errors'].append(f"Connection {i+1}: 'to' component '{to_name}' not found")
                continue
            
            if tube_name and tube_name not in component_names:
                results['errors'].append(f"Connection {i+1}: tube '{tube_name}' not found")
                continue
            
            # Validate connection logic
            from_comp = component_names[from_name]
            to_comp = component_names[to_name]
            from_type = from_comp.get('type')
            to_type = to_comp.get('type')
            
            # Check for logical flow direction
            if from_type in self.pump_components and to_type in self.source_components:
                results['warnings'].append(
                    f"Connection {i+1}: Pump to vessel connection may be backwards"
                )
            
            # Check for missing tubes in high-pressure connections
            if (from_type in self.pump_components and 
                to_type in self.mixing_components and 
                not tube_name):
                results['suggestions'].append(
                    f"Connection {i+1}: Consider adding tube between pump and mixer"
                )
        
        # Check for disconnected components
        connected_components = set()
        for connection in connections:
            connected_components.add(connection.get('from'))
            connected_components.add(connection.get('to'))
            if connection.get('tube'):
                connected_components.add(connection.get('tube'))
        
        all_component_names = set(component_names.keys())
        disconnected = all_component_names - connected_components
        
        if disconnected:
            results['warnings'].append(
                f"Disconnected components: {', '.join(disconnected)}"
            )
        
        return results
    
    def _validate_flow_paths(self, connections: List[Dict[str, Any]], 
                           components: Dict[str, Any]) -> Dict[str, Any]:
        """Validate flow paths through the apparatus"""
        results = {
            'errors': [],
            'warnings': [],
            'flow_paths': [],
            'dead_ends': [],
            'cycles': []
        }
        
        # Build connection graph
        graph = {}
        reverse_graph = {}
        
        for connection in connections:
            from_comp = connection.get('from')
            to_comp = connection.get('to')
            
            if from_comp not in graph:
                graph[from_comp] = []
            graph[from_comp].append(to_comp)
            
            if to_comp not in reverse_graph:
                reverse_graph[to_comp] = []
            reverse_graph[to_comp].append(from_comp)
        
        # Find sources (components with no inputs)
        all_components = components.get('active', []) + components.get('passive', [])
        all_names = [comp.get('name') for comp in all_components]
        
        sources = [name for name in all_names if name not in reverse_graph]
        sinks = [name for name in all_names if name not in graph]
        
        if not sources:
            results['warnings'].append("No source components found - apparatus may have cycles")
        
        if not sinks:
            results['warnings'].append("No sink components found - products may not be collected")
        
        # Find dead ends (components that don't lead anywhere)
        for component_name in all_names:
            if component_name in sinks:
                # Check if it's a reasonable sink (vessel, reactor)
                comp_type = None
                for comp in all_components:
                    if comp.get('name') == component_name:
                        comp_type = comp.get('type')
                        break
                
                if comp_type not in self.destination_components:
                    results['dead_ends'].append(component_name)
        
        if results['dead_ends']:
            results['warnings'].append(
                f"Components with no outputs: {', '.join(results['dead_ends'])}"
            )
        
        # Detect simple cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for component in all_names:
            if component not in visited:
                if has_cycle(component):
                    results['cycles'].append(component)
        
        if results['cycles']:
            results['warnings'].append("Potential cycles detected in flow path")
        
        return results
    
    def _validate_safety(self, components: Dict[str, Any], 
                        connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate safety considerations"""
        results = {
            'warnings': [],
            'suggestions': []
        }
        
        active_components = components.get('active', [])
        passive_components = components.get('passive', [])
        
        # Check for pressure relief
        has_pressure_relief = False
        for component in passive_components:
            if 'relief' in component.get('name', '').lower():
                has_pressure_relief = True
                break
        
        if not has_pressure_relief:
            results['suggestions'].append(
                "Consider adding pressure relief valve for safety"
            )
        
        # Check for multiple pumps without flow control
        pumps = [c for c in active_components if c.get('type') in self.pump_components]
        if len(pumps) > 1:
            results['suggestions'].append(
                "Multiple pumps detected - ensure proper flow rate coordination"
            )
        
        # Check for glass components in high-pressure systems
        glass_components = []
        for component in passive_components:
            if component.get('parameters', {}).get('material') == 'Glass':
                glass_components.append(component.get('name'))
        
        if glass_components and len(pumps) > 0:
            results['warnings'].append(
                f"Glass components in pressurized system: {', '.join(glass_components)}"
            )
        
        return results
    
    def _validate_material_compatibility(self, components: Dict[str, Any], 
                                       connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate material compatibility between connected components"""
        results = {
            'errors': [],
            'warnings': []
        }
        
        # Get component materials
        component_materials = {}
        all_components = components.get('active', []) + components.get('passive', [])
        
        for component in all_components:
            name = component.get('name')
            material = component.get('parameters', {}).get('material')
            if name and material:
                component_materials[name] = material
        
        # Check material compatibility in connections
        for connection in connections:
            from_name = connection.get('from')
            to_name = connection.get('to')
            tube_name = connection.get('tube')
            
            materials_in_path = []
            
            if from_name in component_materials:
                materials_in_path.append(component_materials[from_name])
            
            if tube_name in component_materials:
                materials_in_path.append(component_materials[tube_name])
            
            if to_name in component_materials:
                materials_in_path.append(component_materials[to_name])
            
            # Check compatibility between adjacent materials
            for i in range(len(materials_in_path) - 1):
                mat1, mat2 = materials_in_path[i], materials_in_path[i + 1]
                
                if (mat1 in self.material_compatibility and 
                    mat2 not in self.material_compatibility[mat1]):
                    results['warnings'].append(
                        f"Potential material incompatibility: {mat1} - {mat2} "
                        f"in connection {from_name} → {to_name}"
                    )
        
        return results
    
    def suggest_improvements(self, apparatus_data: Dict[str, Any]) -> List[str]:
        """Suggest improvements for apparatus design"""
        suggestions = []
        
        components = apparatus_data.get('components', {})
        connections = apparatus_data.get('connections', [])
        
        active_components = components.get('active', [])
        passive_components = components.get('passive', [])
        
        # Analyze component distribution
        pumps = len([c for c in active_components if c.get('type') in self.pump_components])
        mixers = len([c for c in passive_components if c.get('type') in self.mixing_components])
        vessels = len([c for c in passive_components if c.get('type') == 'Vessel'])
        
        # Suggest mixing if multiple streams
        if pumps > 1 and mixers == 0:
            suggestions.append("Consider adding mixer for multiple pump streams")
        
        # Suggest sensors for monitoring
        sensors = len([c for c in passive_components if c.get('type') == 'Sensor'])
        if sensors == 0:
            suggestions.append("Consider adding sensors for process monitoring")
        
        # Suggest waste collection
        waste_vessels = [c for c in passive_components 
                        if 'waste' in c.get('name', '').lower()]
        if not waste_vessels:
            suggestions.append("Consider adding waste collection vessel")
        
        return suggestions