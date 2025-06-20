"""
Connection GUI - Interactive interface for connecting components using A.add() logic

This module provides an intuitive interface for creating apparatus connections
with real-time validation and visual feedback.
"""
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, List, Any, Optional, Tuple
import json

from .connection_validator import ConnectionValidator
from .apparatus_visualizer import ApparatusVisualizer


class ConnectionGUI:
    """Interactive GUI for building apparatus connections"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.validator = ConnectionValidator()
        self.visualizer = ApparatusVisualizer()
        
        # Connection data
        self.connections: List[Dict[str, Any]] = []
        self.components: Dict[str, Dict[str, Any]] = {}
        
        # UI elements
        self.main_container = None
        self.connections_display = None
        self.form_container = None
        
        # Form widgets
        self.from_component_dropdown = None
        self.to_component_dropdown = None
        self.tube_dropdown = None
        
    def initialize(self, components: Dict[str, Dict[str, Any]]):
        """Initialize with configured components"""
        self.components = components.copy()
        
        # Load existing connections if available
        self._load_existing_connections()
        
        # Create the main interface
        self.create_main_interface()
    
    def create_main_interface(self):
        """Create the main connection building interface"""
        
        # Header
        header = widgets.HTML("""
            <div style='background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%); 
                        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='margin: 0; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
                    🔗 Apparatus Builder
                </h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>
                    Connect your components to build the complete apparatus
                </p>
            </div>
        """)
        
        # Check if we have components
        if not self.components:
            no_components_msg = widgets.HTML("""
                <div style='text-align: center; padding: 40px; color: #666;'>
                    <h3>No Components Available</h3>
                    <p>Please configure components first before building connections.</p>
                    <p>Use the Component Configurator to add pumps, valves, vessels, and tubes.</p>
                </div>
            """)
            self.main_container = widgets.VBox([header, no_components_msg])
            display(self.main_container)
            return
        
        # Create connection form
        self._create_connection_form()
        
        # Create connections display
        self._create_connections_display()
        
        # Layout
        left_panel = widgets.VBox([
            widgets.HTML("<h3>Add Connection</h3>"),
            self.form_container
        ], layout=widgets.Layout(width='45%', padding='20px'))
        
        right_panel = widgets.VBox([
            widgets.HTML("<h3>Current Connections</h3>"),
            self.connections_display
        ], layout=widgets.Layout(width='55%', padding='20px'))
        
        # Action buttons
        action_buttons = self._create_action_buttons()
        
        self.main_container = widgets.VBox([
            header,
            widgets.HBox([left_panel, right_panel]),
            action_buttons
        ])
        
        display(self.main_container)
        
        # Update displays
        self._update_connections_display()
    
    def _create_connection_form(self):
        """Create the connection form widgets"""
        
        # Get component options
        active_components = self._get_components_by_category(['active_contrib', 'active_stdlib'])
        passive_components = self._get_components_by_category(['passive'])
        all_components = active_components + passive_components
        
        # Component dropdowns
        self.from_component_dropdown = widgets.Dropdown(
            options=[('Select component...', None)] + all_components,
            description='From:',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='300px')
        )
        
        self.to_component_dropdown = widgets.Dropdown(
            options=[('Select component...', None)] + all_components,
            description='To:',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='300px')
        )
        
        # Tube selection
        tube_options = self._get_tube_options()
        self.tube_dropdown = widgets.Dropdown(
            options=[('Select tube...', None)] + tube_options,
            description='Tube:',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='300px')
        )
        
        # Validation output
        self.validation_output = widgets.Output()
        
        # Add connection button
        add_btn = widgets.Button(
            description='Add Connection',
            button_style='primary',
            icon='plus',
            layout=widgets.Layout(width='150px')
        )
        add_btn.on_click(self._add_connection)
        
        # Connection preview
        self.connection_preview = widgets.HTML("")
        
        # Update preview when selections change
        def update_preview(*args):
            self._update_connection_preview()
        
        self.from_component_dropdown.observe(update_preview, names='value')
        self.to_component_dropdown.observe(update_preview, names='value')
        self.tube_dropdown.observe(update_preview, names='value')
        
        # Form layout
        self.form_container = widgets.VBox([
            widgets.HTML("<h4>Select Components and Tube</h4>"),
            self.from_component_dropdown,
            self.to_component_dropdown,
            self.tube_dropdown,
            widgets.HTML("<h4>Connection Preview</h4>"),
            self.connection_preview,
            widgets.HTML("<br>"),
            add_btn,
            self.validation_output
        ])
    
    def _create_connections_display(self):
        """Create the connections display area"""
        self.connections_display = widgets.VBox([])
    
    def _create_action_buttons(self):
        """Create action buttons for the apparatus"""
        
        save_btn = widgets.Button(
            description='Save Apparatus',
            button_style='success',
            icon='save',
            layout=widgets.Layout(width='150px')
        )
        
        clear_btn = widgets.Button(
            description='Clear All',
            button_style='danger',
            icon='trash',
            layout=widgets.Layout(width='100px')
        )
        
        visualize_btn = widgets.Button(
            description='Visualize',
            button_style='info',
            icon='eye',
            layout=widgets.Layout(width='100px')
        )
        
        generate_code_btn = widgets.Button(
            description='Generate Code',
            button_style='warning',
            icon='code',
            layout=widgets.Layout(width='150px')
        )
        
        # Event handlers
        save_btn.on_click(self._save_apparatus)
        clear_btn.on_click(self._clear_all_connections)
        visualize_btn.on_click(self._visualize_apparatus)
        generate_code_btn.on_click(self._generate_code)
        
        return widgets.HBox([
            save_btn, clear_btn, visualize_btn, generate_code_btn
        ], layout=widgets.Layout(justify_content='center', margin='20px 0'))
    
    def _get_components_by_category(self, categories: List[str]) -> List[Tuple[str, str]]:
        """Get component options by category for dropdowns"""
        options = []
        
        for comp_id, comp_data in self.components.items():
            if comp_data.get('category') in categories:
                comp_type = comp_data.get('type', 'Unknown')
                comp_name = comp_data.get('name', comp_id)
                label = f"{comp_name} ({comp_type})"
                options.append((label, comp_name))
        
        return sorted(options)
    
    def _get_tube_options(self) -> List[Tuple[str, str]]:
        """Get tube options for dropdown"""
        options = []
        
        for comp_id, comp_data in self.components.items():
            if comp_data.get('type') == 'Tube':
                tube_name = comp_data.get('name', comp_id)
                tube_info = self._get_tube_info_string(comp_data)
                label = f"{tube_name} ({tube_info})"
                options.append((label, tube_name))
        
        return sorted(options)
    
    def _get_tube_info_string(self, tube_data: Dict[str, Any]) -> str:
        """Create a descriptive string for tube selection"""
        length = tube_data.get('length', '')
        preset = tube_data.get('preset', '')
        
        if preset and preset != 'custom':
            return f"{preset}, {length}"
        else:
            id_val = tube_data.get('ID', '')
            od_val = tube_data.get('OD', '')
            return f"{id_val} ID, {od_val} OD, {length}"
    
    def _update_connection_preview(self):
        """Update the connection preview text"""
        from_comp = self.from_component_dropdown.value
        to_comp = self.to_component_dropdown.value
        tube = self.tube_dropdown.value
        
        if from_comp and to_comp and tube:
            preview_html = f"""
                <div style='background: #f0f8ff; padding: 10px; border-left: 4px solid #2196f3; border-radius: 4px;'>
                    <strong>Connection:</strong> {from_comp} → {to_comp}<br>
                    <strong>Tube:</strong> {tube}
                </div>
            """
        else:
            preview_html = """
                <div style='background: #f5f5f5; padding: 10px; border-radius: 4px; color: #666;'>
                    Select components and tube to preview connection
                </div>
            """
        
        self.connection_preview.value = preview_html
    
    def _add_connection(self, button):
        """Add a new connection"""
        with self.validation_output:
            clear_output()
            
            # Get form values
            from_comp = self.from_component_dropdown.value
            to_comp = self.to_component_dropdown.value
            tube = self.tube_dropdown.value
            
            # Validate selection
            if not from_comp or not to_comp or not tube:
                print("❌ Please select all fields (From, To, Tube)")
                return
            
            if from_comp == to_comp:
                print("❌ From and To components cannot be the same")
                return
            
            # Check for duplicate connections
            for existing_conn in self.connections:
                if (existing_conn['from'] == from_comp and 
                    existing_conn['to'] == to_comp):
                    print(f"❌ Connection from {from_comp} to {to_comp} already exists")
                    return
            
            # Get component data for validation
            from_comp_data = self._get_component_by_name(from_comp)
            to_comp_data = self._get_component_by_name(to_comp)
            tube_data = self._get_component_by_name(tube)
            
            if not from_comp_data or not to_comp_data or not tube_data:
                print("❌ Error: Could not find component data")
                return
            
            # Validate connection
            validation_errors = self.validator.validate_connection(
                from_comp_data, to_comp_data, tube_data, self.connections
            )
            
            if validation_errors:
                print("❌ Validation Errors:")
                for error in validation_errors:
                    print(f"  • {error}")
                return
            
            # Add connection
            connection = {
                'from': from_comp,
                'to': to_comp,
                'tube': tube,
                'from_type': from_comp_data.get('type'),
                'to_type': to_comp_data.get('type'),
                'tube_type': tube_data.get('type')
            }
            
            self.connections.append(connection)
            
            # Clear form
            self.from_component_dropdown.value = None
            self.to_component_dropdown.value = None
            self.tube_dropdown.value = None
            
            # Update display
            self._update_connections_display()
            
            print("✅ Connection added successfully!")
    
    def _get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get component data by name"""
        for comp_data in self.components.values():
            if comp_data.get('name') == name:
                return comp_data
        return None
    
    def _update_connections_display(self):
        """Update the connections display"""
        if not self.connections:
            self.connections_display.children = [
                widgets.HTML("<p style='color: #666;'>No connections defined yet.</p>")
            ]
            return
        
        # Create connection widgets
        connection_widgets = []
        
        for i, conn in enumerate(self.connections):
            conn_widget = self._create_connection_widget(i, conn)
            connection_widgets.append(conn_widget)
        
        # Add summary
        summary_html = f"""
            <div style='background: #e8f5e8; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                <strong>Total Connections:</strong> {len(self.connections)}
            </div>
        """
        
        summary_widget = widgets.HTML(summary_html)
        
        self.connections_display.children = [summary_widget] + connection_widgets
    
    def _create_connection_widget(self, index: int, connection: Dict[str, Any]) -> widgets.Widget:
        """Create a widget to display a connection"""
        
        from_comp = connection['from']
        to_comp = connection['to']
        tube = connection['tube']
        
        # Get tube info for display
        tube_data = self._get_component_by_name(tube)
        tube_info = self._get_tube_info_string(tube_data) if tube_data else tube
        
        info_html = f"""
            <div style='border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px; background: white;'>
                <strong>{index + 1}.</strong> {from_comp} → {to_comp}<br>
                <span style='color: #666; font-size: 12px;'>via {tube} ({tube_info})</span>
            </div>
        """
        
        info_widget = widgets.HTML(info_html)
        
        # Delete button
        delete_btn = widgets.Button(
            description='Delete',
            button_style='danger',
            layout=widgets.Layout(width='70px', height='30px')
        )
        
        def delete_connection(b, idx=index):
            self._delete_connection(idx)
        
        delete_btn.on_click(delete_connection)
        
        return widgets.HBox([
            info_widget,
            delete_btn
        ], layout=widgets.Layout(align_items='center'))
    
    def _delete_connection(self, index: int):
        """Delete a connection by index"""
        if 0 <= index < len(self.connections):
            deleted_conn = self.connections.pop(index)
            self._update_connections_display()
            print(f"✅ Deleted connection: {deleted_conn['from']} → {deleted_conn['to']}")
    
    def _save_apparatus(self, button):
        """Save the apparatus configuration"""
        if not self.connections:
            print("❌ No connections to save. Add some connections first.")
            return
        
        if not self.data_manager:
            print("❌ No data manager available for saving")
            return
        
        try:
            # Prepare apparatus configuration
            apparatus_config = {
                'connections': self.connections,
                'components': self.components
            }
            
            # Get existing config and update
            existing_config = self.data_manager.load_config() or {}
            existing_config.update(apparatus_config)
            
            # Save
            self.data_manager.save_config(existing_config)
            
            print(f"✅ Apparatus saved successfully with {len(self.connections)} connections!")
            
        except Exception as e:
            print(f"❌ Error saving apparatus: {e}")
    
    def _clear_all_connections(self, button):
        """Clear all connections with confirmation"""
        if not self.connections:
            print("No connections to clear.")
            return
        
        # Simple confirmation (could be enhanced with a proper dialog)
        print(f"Clearing {len(self.connections)} connections...")
        self.connections.clear()
        self._update_connections_display()
        print("✅ All connections cleared.")
    
    def _visualize_apparatus(self, button):
        """Create a visual representation of the apparatus"""
        if not self.connections:
            print("❌ No connections to visualize. Add some connections first.")
            return
        
        try:
            # Use the visualizer to create a diagram
            self.visualizer.create_network_diagram(self.components, self.connections)
            print("✅ Apparatus visualization created!")
            
        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
    
    def _generate_code(self, button):
        """Generate Python code for the apparatus"""
        if not self.connections:
            print("❌ No connections to generate code for.")
            return
        
        try:
            code = self._generate_apparatus_code()
            
            # Display code in a text area
            code_output = widgets.Textarea(
                value=code,
                layout=widgets.Layout(width='100%', height='400px'),
                description='Generated Code:'
            )
            
            clear_output()
            display(widgets.VBox([
                widgets.HTML("<h3>Generated MechWolf Apparatus Code</h3>"),
                code_output,
                widgets.Button(description='Back to Builder', button_style='primary')
            ]))
            
        except Exception as e:
            print(f"❌ Error generating code: {e}")
    
    def _generate_apparatus_code(self) -> str:
        """Generate Python code for the apparatus"""
        code_lines = [
            "# Generated MechWolf Apparatus Code",
            "import mechwolf as mw",
            "",
            "# Define Vessels and Passive Components"
        ]
        
        # Add vessel definitions
        vessels = []
        tubes = []
        mixers = []
        active_components = []
        
        for comp_data in self.components.values():
            comp_type = comp_data.get('type')
            comp_name = comp_data.get('name')
            
            if comp_type == 'Vessel':
                description = comp_data.get('description', '')
                if description:
                    vessels.append(f'{comp_name} = mw.Vessel("{description}", name="{comp_name}")')
                else:
                    vessels.append(f'{comp_name} = mw.Vessel("{comp_name}")')
            
            elif comp_type == 'Tube':
                length = comp_data.get('length', '')
                id_val = comp_data.get('ID', '')
                od_val = comp_data.get('OD', '')
                material = comp_data.get('material', 'PFA')
                
                tubes.append(f'{comp_name} = mw.Tube(length="{length}", ID="{id_val}", OD="{od_val}", material="{material}")')
            
            elif 'Mixer' in comp_type:
                mixers.append(f'{comp_name} = mw.{comp_type}(name="{comp_name}")')
            
            else:  # Active components
                active_components.append(comp_data)
        
        code_lines.extend(vessels)
        if tubes:
            code_lines.extend([""] + tubes)
        if mixers:
            code_lines.extend([""] + mixers)
        
        # Add active component definitions
        if active_components:
            code_lines.extend(["", "# Define Active Components"])
            
            for comp_data in active_components:
                comp_type = comp_data.get('type')
                comp_name = comp_data.get('name')
                
                if comp_type == 'HarvardSyringePump':
                    serial_port = comp_data.get('serial_port', '')
                    syringe_volume = comp_data.get('syringe_volume', '')
                    syringe_diameter = comp_data.get('syringe_diameter', '')
                    
                    code_lines.append(f'{comp_name} = mw.HarvardSyringePump(')
                    code_lines.append(f'    syringe_volume="{syringe_volume}",')
                    code_lines.append(f'    syringe_diameter="{syringe_diameter}",')
                    code_lines.append(f'    serial_port="{serial_port}",')
                    code_lines.append(f'    name="{comp_name}"')
                    code_lines.append(')')
                
                elif comp_type == 'ViciValve':
                    serial_port = comp_data.get('serial_port', '')
                    mapping = comp_data.get('mapping', {})
                    
                    # Create mapping dictionary
                    mapping_items = [f'{vessel}: {port}' for vessel, port in mapping.items()]
                    mapping_str = '{' + ', '.join(mapping_items) + '}'
                    
                    code_lines.append(f'{comp_name}_mapping = {mapping_str}')
                    code_lines.append(f'{comp_name} = mw.ViciValve(')
                    code_lines.append(f'    serial_port="{serial_port}",')
                    code_lines.append(f'    mapping={comp_name}_mapping,')
                    code_lines.append(f'    name="{comp_name}"')
                    code_lines.append(')')
                
                # Add other component types as needed
        
        # Add apparatus definition
        code_lines.extend([
            "",
            "# Building the Apparatus",
            'A = mw.Apparatus("Generated Apparatus")'
        ])
        
        # Add connections
        for conn in self.connections:
            from_comp = conn['from']
            to_comp = conn['to']
            tube = conn['tube']
            
            code_lines.append(f'A.add({from_comp}, {to_comp}, {tube})')
        
        # Add visualization and description
        code_lines.extend([
            "",
            "# Visualize and describe the apparatus",
            "A.visualize()",
            "A.describe()"
        ])
        
        return '\n'.join(code_lines)
    
    def _load_existing_connections(self):
        """Load existing connections from data manager"""
        if not self.data_manager:
            return
        
        try:
            config = self.data_manager.load_config()
            if config and 'connections' in config:
                self.connections = config['connections'].copy()
                
        except Exception as e:
            print(f"Error loading existing connections: {e}")
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Return current connections"""
        return self.connections.copy()
    
    def return_to_component_configurator(self):
        """Return to the component configurator"""
        # This would be called by the main orchestrator
        pass