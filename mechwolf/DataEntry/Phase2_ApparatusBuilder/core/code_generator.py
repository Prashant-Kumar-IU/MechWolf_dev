"""
Code generation for MechWolf apparatus.

Generates Python code for apparatus setup from component and connection data.
"""

from ..registry import ComponentRegistry


class CodeGenerator:
    """Handles code generation for apparatus setup."""
    
    @staticmethod
    def generate_code(components, connections):
        """Generate MechWolf apparatus code."""
        if not components:
            return "# No components added yet"
        
        code_lines = []
        code_lines.append("# Generated MechWolf Apparatus Code")
        code_lines.append("import mechwolf as mw")
        code_lines.append("from mechwolf.components.contrib.harvardpump import HarvardSyringePump")
        code_lines.append("")
        
        # Generate component definitions
        code_lines.append("# Component Definitions")
        for name, comp in components.items():
            # Normalize component type and update if needed
            normalized_type = ComponentRegistry.normalize_component_type(comp.component_type)
            if comp.component_type != normalized_type:
                comp.component_type = normalized_type
            
            info = ComponentRegistry.get_component_info(comp.component_type)
            class_name = info['class_name']
            
            if comp.component_type == 'HarvardSyringePump':
                # Build parameters for Harvard pump (name first, then properties)
                params = [f'name="{name}"']
                for prop_name, prop_value in comp.properties.items():
                    if prop_value:  # Only include non-empty properties
                        params.append(f'{prop_name}="{prop_value}"')
                code_lines.append(f'{name} = HarvardSyringePump({", ".join(params)})')
            elif comp.component_type == 'Tube':
                # Tubes don't take a 'name' parameter, only properties with proper units
                tube_params = []
                for prop_name, prop_value in comp.properties.items():
                    if prop_value:  # Only include non-empty properties
                        # Ensure proper units for tube parameters
                        if prop_name in ['ID', 'OD']:
                            # For tube dimensions, ensure they have 'in' units
                            if 'in' not in prop_value:
                                prop_value = f"{prop_value} in"
                        elif prop_name == 'length':
                            # For length, ensure proper units (ft/foot)
                            if 'ft' not in prop_value and 'foot' not in prop_value and 'in' not in prop_value:
                                prop_value = f"{prop_value} ft"
                        tube_params.append(f'{prop_name}="{prop_value}"')
                code_lines.append(f'{name} = mw.{class_name}({", ".join(tube_params)})')
            else:
                # Handle different component types with their specific parameter patterns
                if comp.component_type == 'Vessel':
                    # Vessel takes description first, then name
                    description = comp.description if comp.description else ""
                    params = [f'description="{description}"', f'name="{name}"']
                    # Add other properties
                    for prop_name, prop_value in comp.properties.items():
                        if prop_value:  # Only include non-empty properties
                            params.append(f'{prop_name}="{prop_value}"')
                elif comp.component_type == 'TMixer':
                    # TMixer only takes name parameter (no description)
                    params = [f'name="{name}"']
                    # Add other properties
                    for prop_name, prop_value in comp.properties.items():
                        if prop_value:  # Only include non-empty properties
                            params.append(f'{prop_name}="{prop_value}"')
                else:
                    # Other components - default pattern with name first
                    params = [f'name="{name}"']
                    # Add other properties
                    for prop_name, prop_value in comp.properties.items():
                        if prop_value:  # Only include non-empty properties
                            params.append(f'{prop_name}="{prop_value}"')
                
                code_lines.append(f'{name} = mw.{class_name}({", ".join(params)})')
        
        code_lines.append("")
        
        # Generate TMixer connections (TMixer to vessel via tube)
        tmixer_connections = []
        for conn in connections:
            # Check if connection is from a TMixer to a Vessel via a tube
            if (conn.from_component in components and 
                conn.to_component in components and
                components[conn.from_component].component_type == 'TMixer' and
                components[conn.to_component].component_type == 'Vessel'):
                
                tmixer_connections.append(f'{conn.from_component} = mw.TMixer({conn.tube_type})')
        
        # Add TMixer connections if any exist
        if tmixer_connections:
            code_lines.append("# TMixer Connections")
            for tmixer_conn in tmixer_connections:
                code_lines.append(tmixer_conn)
            code_lines.append("")
        
        # Generate apparatus assembly
        code_lines.append("# Apparatus Assembly")
        code_lines.append('A = mw.Apparatus("Generated Apparatus")')
        
        for conn in connections:
            code_lines.append(f'A.add({conn.from_component}, {conn.to_component}, {conn.tube_type})')
        
        return "\n".join(code_lines)