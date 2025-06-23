"""
Enhanced Network-Based Apparatus Designer for MechWolf

Extended version with advanced features like component deletion, property editing,
save/load functionality, and improved user interface.
"""

import json
import os
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, List, Any, Optional, Tuple
import mechwolf as mw
from collections import defaultdict
import networkx as nx

# Import base classes from the main designer
from .network_apparatus_designer import (
    ComponentLibrary, NetworkNode, NetworkConnection, ApparatusNetwork
)

class EnhancedPropertiesManager:
    """Enhanced properties manager with dynamic property widgets."""
    
    @staticmethod
    def create_property_widgets(component_type: str, current_props: Dict[str, Any]) -> List[widgets.Widget]:
        """Create appropriate widgets for component properties."""
        widgets_list = []
        
        if component_type in ComponentLibrary.ACTIVE_COMPONENTS:
            defaults = ComponentLibrary.ACTIVE_COMPONENTS[component_type]['default_props']
        else:
            defaults = ComponentLibrary.PASSIVE_COMPONENTS.get(component_type, {}).get('default_props', {})
        
        # Merge defaults with current properties
        all_props = {**defaults, **current_props}
        
        for prop_name, prop_value in all_props.items():
            if prop_name == 'serial_port':
                widget = widgets.Text(
                    value=str(prop_value),
                    description=f"{prop_name}:",
                    placeholder="e.g., /dev/ttyUSB0 or COM1",
                    layout=widgets.Layout(width='250px')
                )
            elif prop_name in ['syringe_volume', 'max_rate']:
                widget = widgets.Text(
                    value=str(prop_value),
                    description=f"{prop_name}:",
                    placeholder="e.g., 10 mL, 25mL/min",
                    layout=widgets.Layout(width='250px')
                )
            elif prop_name == 'mapping':
                widget = widgets.HTML(
                    value=f"<b>{prop_name}:</b> {prop_value}<br><small>Use connection settings to configure</small>"
                )
            elif isinstance(prop_value, bool):
                widget = widgets.Checkbox(
                    value=prop_value,
                    description=prop_name,
                    layout=widgets.Layout(width='250px')
                )
            elif isinstance(prop_value, (int, float)):
                widget = widgets.FloatText(
                    value=float(prop_value),
                    description=f"{prop_name}:",
                    layout=widgets.Layout(width='250px')
                )
            else:
                widget = widgets.Text(
                    value=str(prop_value),
                    description=f"{prop_name}:",
                    layout=widgets.Layout(width='250px')
                )
            
            # Store property name as metadata
            widget.property_name = prop_name
            widgets_list.append(widget)
        
        return widgets_list

class ConfigurationManager:
    """Handles saving and loading apparatus configurations."""
    
    @staticmethod
    def save_configuration(network: ApparatusNetwork, filename: str) -> bool:
        """Save apparatus network to JSON file."""
        try:
            config = {
                'metadata': {
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'components_count': len(network.nodes),
                    'connections_count': len(network.connections)
                },
                'nodes': {},
                'connections': []
            }
            
            # Save nodes
            for name, node in network.nodes.items():
                config['nodes'][name] = {
                    'component_type': node.component_type,
                    'x': node.x,
                    'y': node.y,
                    'properties': node.properties,
                    'input_ports': node.input_ports,
                    'output_ports': node.output_ports
                }
            
            # Save connections
            for conn in network.connections:
                config['connections'].append({
                    'from_node': conn.from_node,
                    'from_port': conn.from_port,
                    'to_node': conn.to_node,
                    'to_port': conn.to_port,
                    'tube_type': conn.tube_type,
                    'tube_length': conn.tube_length,
                    'tube_properties': conn.tube_properties
                })
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    @staticmethod
    def load_configuration(filename: str) -> Optional[ApparatusNetwork]:
        """Load apparatus network from JSON file."""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            network = ApparatusNetwork()
            
            # Load nodes
            for name, node_data in config['nodes'].items():
                node = NetworkNode(
                    node_data['component_type'],
                    name,
                    node_data.get('x', 0),
                    node_data.get('y', 0)
                )
                node.properties = node_data.get('properties', {})
                node.input_ports = node_data.get('input_ports', [])
                node.output_ports = node_data.get('output_ports', [])
                network.add_node(node)
            
            # Load connections
            for conn_data in config['connections']:
                connection = NetworkConnection(
                    conn_data['from_node'],
                    conn_data['from_port'],
                    conn_data['to_node'],
                    conn_data['to_port']
                )
                connection.tube_type = conn_data.get('tube_type', 'fat_tube')
                connection.tube_length = conn_data.get('tube_length', '1 ft')
                connection.tube_properties = conn_data.get('tube_properties', {})
                network.add_connection(connection)
            
            return network
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return None

class EnhancedNetworkApparatusDesigner:
    """Enhanced network apparatus designer with advanced features."""
    
    def __init__(self):
        self.network = ApparatusNetwork()
        self.selected_node_name = None
        self.selected_connection = None
        self.component_counter = defaultdict(int)
        self.config_manager = ConfigurationManager()
        
        # Create GUI components
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
    
    def _create_widgets(self):
        """Create all GUI widgets with enhanced features."""
        # Component Library Panel (Enhanced)
        self.component_library = self._create_enhanced_component_library()
        
        # Network Canvas Panel (Enhanced)
        self.network_canvas = self._create_enhanced_network_canvas()
        
        # Properties Panel (Enhanced)
        self.properties_panel = self._create_enhanced_properties_panel()
        
        # Code Preview Panel (Enhanced)
        self.code_preview = self._create_enhanced_code_preview()
        
        # Toolbar (Enhanced)
        self.toolbar = self._create_enhanced_toolbar()
    
    def _create_enhanced_component_library(self):
        """Create enhanced component library with search and categories."""
        library_widgets = []
        
        # Search box
        search_box = widgets.Text(
            placeholder="Search components...",
            layout=widgets.Layout(width='200px')
        )
        library_widgets.append(search_box)
        
        # Passive Components Section
        passive_header = widgets.HTML("<h4>📦 Passive Components</h4>")
        library_widgets.append(passive_header)
        
        for comp_type, info in ComponentLibrary.PASSIVE_COMPONENTS.items():
            button = widgets.Button(
                description=f"{info['icon']} {comp_type}",
                tooltip=info['description'],
                layout=widgets.Layout(width='200px', margin='2px'),
                style={'button_color': '#e8f4f8'}
            )
            button.on_click(lambda b, ct=comp_type: self._add_component(ct))
            library_widgets.append(button)
        
        # Active Components Section
        active_header = widgets.HTML("<h4>⚙️ Active Components</h4>")
        library_widgets.append(active_header)
        
        for comp_type, info in ComponentLibrary.ACTIVE_COMPONENTS.items():
            button = widgets.Button(
                description=f"{info['icon']} {comp_type}",
                tooltip=info['description'],
                layout=widgets.Layout(width='200px', margin='2px'),
                style={'button_color': '#f8f4e8'}
            )
            button.on_click(lambda b, ct=comp_type: self._add_component(ct))
            library_widgets.append(button)
        
        # Custom Components Section
        custom_header = widgets.HTML("<h4>🔧 Actions</h4>")
        library_widgets.append(custom_header)
        
        delete_button = widgets.Button(
            description="🗑️ Delete Selected",
            button_style='danger',
            layout=widgets.Layout(width='200px', margin='2px')
        )
        delete_button.on_click(self._delete_selected_component)
        library_widgets.append(delete_button)
        
        return widgets.VBox(library_widgets, 
                          layout=widgets.Layout(width='220px', height='600px', 
                                               overflow='auto', border='1px solid #ccc',
                                               padding='10px'))
    
    def _create_enhanced_network_canvas(self):
        """Create enhanced network canvas with component selection."""
        # Canvas header with enhanced controls
        canvas_header = widgets.HBox([
            widgets.HTML("<h3>🔗 Apparatus Network</h3>"),
            widgets.Button(description="🔄 Refresh", 
                         button_style='info',
                         layout=widgets.Layout(width='80px')),
            widgets.Button(description="✅ Validate", 
                         button_style='success',
                         layout=widgets.Layout(width='80px')),
            widgets.Button(description="📊 Stats", 
                         button_style='warning',
                         layout=widgets.Layout(width='80px'))
        ])
        
        # Component selection area
        component_selector = widgets.VBox([
            widgets.HTML("<b>Select Component:</b>"),
            widgets.Dropdown(
                options=[],
                description="Component:",
                layout=widgets.Layout(width='200px')
            )
        ])
        
        # Network visualization area (enhanced)
        self.network_display = widgets.Output(
            layout=widgets.Layout(height='400px', border='2px dashed #ccc',
                                background_color='#fafafa', overflow='auto')
        )
        
        # Enhanced connection controls
        connection_controls = widgets.VBox([
            widgets.HTML("<b>Create Connection:</b>"),
            widgets.HBox([
                widgets.Dropdown(options=[], description="From:",
                               layout=widgets.Layout(width='150px')),
                widgets.HTML(" → "),
                widgets.Dropdown(options=[], description="To:",
                               layout=widgets.Layout(width='150px')),
            ]),
            widgets.HBox([
                widgets.Dropdown(
                    options=list(ComponentLibrary.TUBE_TYPES.keys()),
                    value='fat_tube',
                    description="Tube:",
                    layout=widgets.Layout(width='120px')
                ),
                widgets.Text(
                    value="1 ft",
                    description="Length:",
                    layout=widgets.Layout(width='100px')
                ),
                widgets.Button(description="Connect", button_style='primary',
                             layout=widgets.Layout(width='80px'))
            ])
        ])
        
        return widgets.VBox([
            canvas_header, 
            widgets.HBox([component_selector, connection_controls]),
            self.network_display
        ], layout=widgets.Layout(width='600px'))
    
    def _create_enhanced_properties_panel(self):
        """Create enhanced properties panel with dynamic widgets."""
        # Component properties section
        comp_props_header = widgets.HTML("<h4>🔧 Component Properties</h4>")
        
        self.selected_component_display = widgets.HTML("Select a component to edit properties")
        
        # Dynamic properties container
        self.dynamic_props_container = widgets.VBox([])
        
        # Connection properties section
        conn_props_header = widgets.HTML("<h4>🔗 Connection Properties</h4>")
        
        self.connection_selector = widgets.Dropdown(
            options=[],
            description="Connection:",
            layout=widgets.Layout(width='220px')
        )
        
        self.tube_type_dropdown = widgets.Dropdown(
            options=list(ComponentLibrary.TUBE_TYPES.keys()),
            description="Tube Type:",
            layout=widgets.Layout(width='220px')
        )
        
        self.tube_length_input = widgets.Text(
            value="1 ft",
            description="Length:",
            layout=widgets.Layout(width='220px')
        )
        
        # Action buttons
        apply_comp_button = widgets.Button(
            description="Apply Component Props",
            button_style='success',
            layout=widgets.Layout(width='220px')
        )
        apply_comp_button.on_click(self._apply_component_properties)
        
        apply_conn_button = widgets.Button(
            description="Apply Connection Props",
            button_style='success',
            layout=widgets.Layout(width='220px')
        )
        apply_conn_button.on_click(self._apply_connection_properties)
        
        return widgets.VBox([
            comp_props_header,
            self.selected_component_display,
            self.dynamic_props_container,
            apply_comp_button,
            widgets.HTML("<hr>"),
            conn_props_header,
            self.connection_selector,
            self.tube_type_dropdown,
            self.tube_length_input,
            apply_conn_button
        ], layout=widgets.Layout(width='250px', height='600px', 
                               overflow='auto', border='1px solid #ccc',
                               padding='10px'))
    
    def _create_enhanced_code_preview(self):
        """Create enhanced code preview with additional options."""
        code_header = widgets.HBox([
            widgets.HTML("<h4>🐍 Generated Apparatus Code</h4>"),
            widgets.Button(description="📋 Copy", button_style='info',
                         layout=widgets.Layout(width='70px')),
            widgets.Button(description="💾 Save", button_style='success',
                         layout=widgets.Layout(width='70px')),
            widgets.Button(description="🔄 Refresh", button_style='warning',
                         layout=widgets.Layout(width='70px'))
        ])
        
        # Code generation options
        code_options = widgets.HBox([
            widgets.Checkbox(value=True, description="Include imports"),
            widgets.Checkbox(value=True, description="Include tube functions"),
            widgets.Checkbox(value=False, description="Add comments"),
            widgets.Text(value="Generated Apparatus", description="Name:",
                        layout=widgets.Layout(width='200px'))
        ])
        
        self.code_output = widgets.Textarea(
            value="# Apparatus code will appear here...",
            layout=widgets.Layout(width='100%', height='120px'),
            disabled=True
        )
        
        return widgets.VBox([code_header, code_options, self.code_output],
                          layout=widgets.Layout(height='200px', border='1px solid #ccc',
                                               padding='10px'))
    
    def _create_enhanced_toolbar(self):
        """Create enhanced toolbar with additional features."""
        file_operations = widgets.HBox([
            widgets.Button(description="🆕 New", button_style='primary'),
            widgets.Button(description="📁 Load", button_style='info'),
            widgets.Button(description="💾 Save", button_style='success'),
            widgets.Button(description="📤 Export", button_style='warning')
        ])
        
        apparatus_operations = widgets.HBox([
            widgets.Button(description="🗑️ Clear", button_style='danger'),
            widgets.Button(description="✅ Validate", button_style='success'),
            widgets.Button(description="⚡ Generate", button_style='warning'),
            widgets.Button(description="📊 Analyze", button_style='info')
        ])
        
        return widgets.VBox([
            widgets.HTML("<b>File Operations:</b>"),
            file_operations,
            widgets.HTML("<b>Apparatus Operations:</b>"),
            apparatus_operations
        ], layout=widgets.Layout(margin='10px 0'))
    
    def _setup_layout(self):
        """Setup the enhanced GUI layout."""
        # Top toolbar
        top_section = self.toolbar
        
        # Main content area with 3 panels
        main_content = widgets.HBox([
            self.component_library,    # Left panel
            self.network_canvas,       # Center panel  
            self.properties_panel      # Right panel
        ])
        
        # Bottom code preview
        bottom_section = self.code_preview
        
        # Complete layout
        self.main_widget = widgets.VBox([
            top_section,
            main_content,
            bottom_section
        ])
    
    def _bind_events(self):
        """Bind enhanced event handlers."""
        # File operations
        file_buttons = self.toolbar.children[1].children
        file_buttons[0].on_click(self._new_apparatus)      # New
        file_buttons[1].on_click(self._load_apparatus)     # Load  
        file_buttons[2].on_click(self._save_apparatus)     # Save
        file_buttons[3].on_click(self._export_apparatus)   # Export
        
        # Apparatus operations
        app_buttons = self.toolbar.children[3].children
        app_buttons[0].on_click(self._clear_apparatus)     # Clear
        app_buttons[1].on_click(self._validate_network)    # Validate
        app_buttons[2].on_click(self._generate_code)       # Generate
        app_buttons[3].on_click(self._analyze_network)     # Analyze
        
        # Canvas events
        canvas_buttons = self.network_canvas.children[0].children
        canvas_buttons[1].on_click(self._refresh_canvas)   # Refresh
        canvas_buttons[2].on_click(self._validate_network) # Validate
        canvas_buttons[3].on_click(self._show_stats)       # Stats
        
        # Component selection
        component_dropdown = self.network_canvas.children[1].children[0].children[1]
        component_dropdown.observe(self._on_component_selected, names='value')
        
        # Connection creation
        connection_button = self.network_canvas.children[1].children[1].children[2].children[2]
        connection_button.on_click(self._add_enhanced_connection)
        
        # Code preview events
        code_buttons = self.code_preview.children[0].children
        code_buttons[1].on_click(self._copy_code)          # Copy
        code_buttons[2].on_click(self._save_code)          # Save
        code_buttons[3].on_click(self._generate_code)      # Refresh
    
    def _add_component(self, component_type: str):
        """Add a new component with enhanced features."""
        self.component_counter[component_type] += 1
        name = f"{component_type.lower()}_{self.component_counter[component_type]}"
        
        node = NetworkNode(component_type, name)
        
        # Set default properties
        if component_type in ComponentLibrary.PASSIVE_COMPONENTS:
            node.properties = ComponentLibrary.PASSIVE_COMPONENTS[component_type]['default_props'].copy()
        elif component_type in ComponentLibrary.ACTIVE_COMPONENTS:
            node.properties = ComponentLibrary.ACTIVE_COMPONENTS[component_type]['default_props'].copy()
        
        if self.network.add_node(node):
            self._refresh_canvas()
            self._update_all_dropdowns()
            self._generate_code()
    
    def _delete_selected_component(self, button):
        """Delete the selected component."""
        if self.selected_node_name and self.selected_node_name in self.network.nodes:
            self.network.remove_node(self.selected_node_name)
            self.selected_node_name = None
            self._refresh_canvas()
            self._update_all_dropdowns()
            self._update_properties_panel()
            self._generate_code()
    
    def _on_component_selected(self, change):
        """Handle component selection."""
        self.selected_node_name = change['new']
        self._update_properties_panel()
    
    def _update_properties_panel(self):
        """Update the properties panel for the selected component."""
        if not self.selected_node_name or self.selected_node_name not in self.network.nodes:
            self.selected_component_display.value = "Select a component to edit properties"
            self.dynamic_props_container.children = []
            return
        
        node = self.network.nodes[self.selected_node_name]
        self.selected_component_display.value = f"<b>{node.name}</b> ({node.component_type})"
        
        # Create dynamic property widgets
        prop_widgets = EnhancedPropertiesManager.create_property_widgets(
            node.component_type, node.properties
        )
        self.dynamic_props_container.children = prop_widgets
    
    def _apply_component_properties(self, button):
        """Apply component property changes."""
        if not self.selected_node_name or self.selected_node_name not in self.network.nodes:
            return
        
        node = self.network.nodes[self.selected_node_name]
        
        # Extract values from property widgets
        for widget in self.dynamic_props_container.children:
            if hasattr(widget, 'property_name'):
                prop_name = widget.property_name
                if hasattr(widget, 'value'):
                    node.properties[prop_name] = widget.value
        
        self._generate_code()
        print(f"✅ Applied properties to {node.name}")
    
    def _apply_connection_properties(self, button):
        """Apply connection property changes."""
        # Implementation for connection property changes
        self._generate_code()
    
    def _update_all_dropdowns(self):
        """Update all dropdown options."""
        node_names = list(self.network.nodes.keys())
        
        # Update component selector
        component_dropdown = self.network_canvas.children[1].children[0].children[1]
        component_dropdown.options = node_names
        
        # Update connection dropdowns
        connection_controls = self.network_canvas.children[1].children[1].children
        from_dropdown = connection_controls[0].children[0]
        to_dropdown = connection_controls[0].children[2]
        
        from_dropdown.options = node_names
        to_dropdown.options = node_names
        
        # Update connection selector in properties
        connections = [f"{c.from_node} → {c.to_node}" for c in self.network.connections]
        self.connection_selector.options = connections
    
    def _add_enhanced_connection(self, button):
        """Add connection with enhanced tube settings."""
        connection_controls = self.network_canvas.children[1].children[1].children
        from_dropdown = connection_controls[0].children[0]
        to_dropdown = connection_controls[0].children[2]
        tube_dropdown = connection_controls[1].children[0]
        length_input = connection_controls[1].children[1]
        
        if (from_dropdown.value and to_dropdown.value and 
            from_dropdown.value != to_dropdown.value):
            
            connection = NetworkConnection(
                from_dropdown.value, 'out',
                to_dropdown.value, 'in'
            )
            connection.tube_type = tube_dropdown.value
            connection.tube_length = length_input.value
            connection.tube_properties = ComponentLibrary.TUBE_TYPES[tube_dropdown.value].copy()
            
            if self.network.add_connection(connection):
                self._refresh_canvas()
                self._update_all_dropdowns()
                self._generate_code()
    
    def _refresh_canvas(self, button=None):
        """Enhanced canvas refresh with more details."""
        with self.network_display:
            clear_output(wait=True)
            
            if not self.network.nodes:
                print("🏗️ Welcome to MechWolf Network Apparatus Designer!")
                print("📦 Click components in the library to add them to your apparatus")
                print("🔗 Use connection controls to link components together")
                print("⚙️ Configure properties in the right panel")
                print("🐍 Generated code appears at the bottom")
                return
            
            print("📊 Current Apparatus Network:")
            print("=" * 60)
            
            # Display nodes with enhanced information
            print("\n🔧 Components:")
            for name, node in self.network.nodes.items():
                icon = ComponentLibrary.PASSIVE_COMPONENTS.get(node.component_type, {}).get('icon', '🔧')
                if not icon or icon == '🔧':
                    icon = ComponentLibrary.ACTIVE_COMPONENTS.get(node.component_type, {}).get('icon', '🔧')
                
                status = "🔵 SELECTED" if name == self.selected_node_name else ""
                print(f"  {icon} {name} ({node.component_type}) {status}")
                
                # Show key properties
                if node.properties:
                    key_props = []
                    for key, value in list(node.properties.items())[:2]:  # Show first 2 properties
                        key_props.append(f"{key}: {value}")
                    if key_props:
                        print(f"      └─ {', '.join(key_props)}")
            
            # Display connections with enhanced information
            print("\n🔗 Connections:")
            if self.network.connections:
                for i, conn in enumerate(self.network.connections, 1):
                    tube_info = ComponentLibrary.TUBE_TYPES.get(conn.tube_type, {})
                    print(f"  {i}. {conn.from_node} → {conn.to_node}")
                    print(f"     └─ {conn.tube_type} ({conn.tube_length})")
                    if tube_info:
                        print(f"        ID: {tube_info.get('ID', 'N/A')}, "
                              f"OD: {tube_info.get('OD', 'N/A')}, "
                              f"Material: {tube_info.get('material', 'N/A')}")
            else:
                print("  ⚠️ No connections yet - use connection controls above")
            
            # Network statistics
            print(f"\n📈 Network Statistics:")
            print(f"  • Components: {len(self.network.nodes)}")
            print(f"  • Connections: {len(self.network.connections)}")
            print(f"  • Active Components: {sum(1 for n in self.network.nodes.values() if n.component_type in ComponentLibrary.ACTIVE_COMPONENTS)}")
            print(f"  • Passive Components: {sum(1 for n in self.network.nodes.values() if n.component_type in ComponentLibrary.PASSIVE_COMPONENTS)}")
    
    def _generate_code(self, button=None):
        """Enhanced code generation with options."""
        if not self.network.nodes:
            self.code_output.value = "# Add components to generate apparatus code"
            return
        
        # Get code generation options
        code_options = self.code_preview.children[1].children
        include_imports = code_options[0].value
        include_tube_functions = code_options[1].value
        add_comments = code_options[2].value
        apparatus_name = code_options[3].value or "Generated Apparatus"
        
        code_lines = []
        
        if add_comments:
            code_lines.extend([
                f"# MechWolf Apparatus: {apparatus_name}",
                f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"# Components: {len(self.network.nodes)}, Connections: {len(self.network.connections)}",
                ""
            ])
        
        if include_imports:
            code_lines.extend([
                "import mechwolf as mw",
                ""
            ])
        
        # Generate component definitions
        if add_comments:
            code_lines.append("# Component Definitions")
        
        for name, node in self.network.nodes.items():
            component_class = ComponentLibrary.PASSIVE_COMPONENTS.get(node.component_type, {}).get('class')
            if not component_class:
                component_class = ComponentLibrary.ACTIVE_COMPONENTS.get(node.component_type, {}).get('class')
            
            if component_class:
                params = []
                for key, value in node.properties.items():
                    if key == 'mapping':
                        continue  # Skip mapping for now
                    if isinstance(value, str):
                        params.append(f'{key}="{value}"')
                    else:
                        params.append(f'{key}={value}')
                params.append(f'name="{name}"')
                
                if add_comments:
                    code_lines.append(f'# {node.component_type}: {name}')
                code_lines.append(f'{name} = {component_class}({", ".join(params)})')
        
        code_lines.append("")
        
        # Generate tube functions
        if include_tube_functions:
            if add_comments:
                code_lines.append("# Tube Functions")
            
            tube_functions = set()
            for conn in self.network.connections:
                if conn.tube_type not in tube_functions:
                    tube_info = ComponentLibrary.TUBE_TYPES[conn.tube_type]
                    if add_comments:
                        code_lines.append(f'# {conn.tube_type}: {tube_info}')
                    code_lines.append(f'def {conn.tube_type}(length):')
                    code_lines.append(f'    return mw.Tube(length=length, ID="{tube_info["ID"]}", '
                                    f'OD="{tube_info["OD"]}", material="{tube_info["material"]}")')
                    tube_functions.add(conn.tube_type)
            
            code_lines.append("")
        
        # Generate apparatus assembly
        if add_comments:
            code_lines.append("# Apparatus Assembly")
        
        code_lines.append(f'A = mw.Apparatus("{apparatus_name}")')
        
        for conn in self.network.connections:
            if add_comments:
                code_lines.append(f'# Connect {conn.from_node} to {conn.to_node}')
            code_lines.append(f'A.add({conn.from_node}, {conn.to_node}, '
                            f'{conn.tube_type}("{conn.tube_length}"))')
        
        if add_comments:
            code_lines.extend([
                "",
                "# Apparatus is ready for use in protocols!",
                "# Example: protocol = mw.Protocol(A)"
            ])
        
        self.code_output.value = "\n".join(code_lines)
    
    def _save_apparatus(self, button):
        """Save apparatus configuration."""
        filename = f"apparatus_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join("./configs", filename)
        
        if self.config_manager.save_configuration(self.network, filepath):
            print(f"✅ Configuration saved to {filepath}")
        else:
            print("❌ Failed to save configuration")
    
    def _load_apparatus(self, button):
        """Load apparatus configuration."""
        # For demo purposes, try to load the most recent config
        config_dir = "./configs"
        if os.path.exists(config_dir):
            config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
            if config_files:
                latest_config = sorted(config_files)[-1]
                filepath = os.path.join(config_dir, latest_config)
                
                loaded_network = self.config_manager.load_configuration(filepath)
                if loaded_network:
                    self.network = loaded_network
                    self._refresh_canvas()
                    self._update_all_dropdowns()
                    self._generate_code()
                    print(f"✅ Configuration loaded from {filepath}")
                else:
                    print("❌ Failed to load configuration")
            else:
                print("❌ No configuration files found")
        else:
            print("❌ Config directory not found")
    
    def _new_apparatus(self, button):
        """Create new apparatus."""
        self.network = ApparatusNetwork()
        self.component_counter.clear()
        self.selected_node_name = None
        self._refresh_canvas()
        self._update_all_dropdowns()
        self._update_properties_panel()
        self.code_output.value = "# New apparatus - add components to begin"
    
    def _clear_apparatus(self, button):
        """Clear apparatus."""
        self._new_apparatus(button)
    
    def _export_apparatus(self, button):
        """Export apparatus code to file."""
        filename = f"apparatus_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        try:
            with open(filename, 'w') as f:
                f.write(self.code_output.value)
            print(f"✅ Code exported to {filename}")
        except Exception as e:
            print(f"❌ Failed to export code: {e}")
    
    def _validate_network(self, button):
        """Enhanced network validation."""
        errors = self.network.validate_network()
        
        with self.network_display:
            clear_output(wait=True)
            print("🔍 Network Validation Report")
            print("=" * 40)
            
            if errors:
                print("❌ Validation Issues Found:")
                for i, error in enumerate(errors, 1):
                    print(f"  {i}. {error}")
            else:
                print("✅ Network validation passed!")
                print("🎉 Your apparatus is ready for use!")
            
            print(f"\n📊 Validation Summary:")
            print(f"  • Total components: {len(self.network.nodes)}")
            print(f"  • Total connections: {len(self.network.connections)}")
            print(f"  • Issues found: {len(errors)}")
            
        self._refresh_canvas()
    
    def _show_stats(self, button):
        """Show detailed network statistics."""
        with self.network_display:
            clear_output(wait=True)
            print("📊 Detailed Network Statistics")
            print("=" * 50)
            
            # Component statistics
            comp_types = defaultdict(int)
            for node in self.network.nodes.values():
                comp_types[node.component_type] += 1
            
            print("\n🔧 Component Breakdown:")
            for comp_type, count in comp_types.items():
                print(f"  • {comp_type}: {count}")
            
            # Connection statistics
            tube_types = defaultdict(int)
            for conn in self.network.connections:
                tube_types[conn.tube_type] += 1
            
            print("\n🔗 Connection Breakdown:")
            for tube_type, count in tube_types.items():
                print(f"  • {tube_type}: {count}")
            
            # Network properties
            if self.network.graph:
                print(f"\n🌐 Network Properties:")
                print(f"  • Nodes: {self.network.graph.number_of_nodes()}")
                print(f"  • Edges: {self.network.graph.number_of_edges()}")
                print(f"  • Is connected: {nx.is_weakly_connected(self.network.graph) if self.network.graph.number_of_nodes() > 1 else 'N/A'}")
                print(f"  • Is DAG: {nx.is_directed_acyclic_graph(self.network.graph)}")
        
        self._refresh_canvas()
    
    def _analyze_network(self, button):
        """Analyze network for optimization suggestions."""
        print("🔍 Analyzing apparatus network...")
        # Implementation for network analysis
    
    def _copy_code(self, button):
        """Copy generated code to clipboard."""
        print("📋 Code copied to clipboard (feature would be implemented with pyperclip)")
    
    def _save_code(self, button):
        """Save generated code to file."""
        self._export_apparatus(button)
    
    def display(self):
        """Display the enhanced GUI."""
        display(self.main_widget)

# Factory function for enhanced designer
def create_enhanced_network_apparatus_designer():
    """Create and return a new EnhancedNetworkApparatusDesigner instance."""
    return EnhancedNetworkApparatusDesigner()