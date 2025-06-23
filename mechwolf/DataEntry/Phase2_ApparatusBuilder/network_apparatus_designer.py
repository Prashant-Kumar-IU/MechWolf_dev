"""
Network-Based Apparatus Designer for MechWolf

A visual interface for designing apparatus networks by dragging and dropping components,
creating connections, and automatically generating MechWolf A.add() code.
"""

import json
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, List, Any, Optional, Tuple
import mechwolf as mw
from collections import defaultdict
import networkx as nx

class ComponentLibrary:
    """Component library containing all available MechWolf components organized by category."""
    
    PASSIVE_COMPONENTS = {
        'Vessel': {
            'class': 'mw.Vessel',
            'icon': '📦',
            'description': 'Container for reagents and products',
            'default_props': {'description': 'New vessel'}
        },
        'TMixer': {
            'class': 'mw.TMixer',
            'icon': '🔀',
            'description': 'T-shaped mixing junction',
            'default_props': {}
        },
        'CrossMixer': {
            'class': 'mw.CrossMixer',
            'icon': '✚',
            'description': 'Four-way mixing junction',
            'default_props': {}
        },
        'YMixer': {
            'class': 'mw.YMixer',
            'icon': '🔁',
            'description': 'Y-shaped mixing junction',
            'default_props': {}
        }
    }
    
    ACTIVE_COMPONENTS = {
        'FreeStepPump': {
            'class': 'mw.FreeStepPump',
            'icon': '⚙️',
            'description': '3D syringe pump with MCU control',
            'default_props': {
                'serial_port': '/dev/ttyUSB0',
                'mcu_id': 'A',
                'motor_id': 1,
                'syringe_volume': '10 mL',
                'syringe_diameter': '11.99 mm'
            }
        },
        'HarvardPump': {
            'class': 'mw.HarvardPump',
            'icon': '💉',
            'description': 'Harvard syringe pump',
            'default_props': {
                'serial_port': 'COM1',
                'syringe_volume': '3 mL',
                'syringe_diameter': '10 mm'
            }
        },
        'VarianPump': {
            'class': 'mw.VarianPump',
            'icon': '🔧',
            'description': 'Varian HPLC pump',
            'default_props': {
                'serial_port': '/dev/serial/by-id/...',
                'max_rate': '25mL/min'
            }
        },
        'ViciValve': {
            'class': 'mw.ViciValve',
            'icon': '🔀',
            'description': 'VICI multi-port valve',
            'default_props': {
                'serial_port': '/dev/serial/by-id/...',
                'mapping': {}
            }
        }
    }
    
    TUBE_TYPES = {
        'fat_tube': {
            'ID': '1/16 in',
            'OD': '1/8 in',
            'material': 'PFA'
        },
        'thin_tube': {
            'ID': '0.030 in',
            'OD': '1/16 in',
            'material': 'PFA'
        },
        'thinner_tube': {
            'ID': '0.020 in',
            'OD': '1/16 in',
            'material': 'PFA'
        },
        'custom_tube': {
            'ID': '1/32 in',
            'OD': '1/16 in',
            'material': 'PTFE'
        }
    }

class NetworkNode:
    """Represents a component node in the apparatus network."""
    
    def __init__(self, component_type: str, name: str, x: int = 0, y: int = 0):
        self.component_type = component_type
        self.name = name
        self.x = x
        self.y = y
        self.properties = {}
        self.input_ports = []
        self.output_ports = []
        self._setup_ports()
    
    def _setup_ports(self):
        """Setup input/output ports based on component type."""
        if self.component_type in ['Vessel']:
            self.output_ports = ['out']
        elif self.component_type in ['TMixer', 'YMixer']:
            self.input_ports = ['in1', 'in2']
            self.output_ports = ['out']
        elif self.component_type in ['CrossMixer']:
            self.input_ports = ['in1', 'in2', 'in3', 'in4']
            self.output_ports = ['out']
        elif self.component_type.endswith('Pump'):
            self.input_ports = ['in']
            self.output_ports = ['out']
        elif self.component_type.endswith('Valve'):
            self.input_ports = ['in']
            self.output_ports = ['out1', 'out2', 'out3', 'out4']  # Multiple outputs
        else:
            # Default: single input and output
            self.input_ports = ['in']
            self.output_ports = ['out']

class NetworkConnection:
    """Represents a connection between two components via a tube."""
    
    def __init__(self, from_node: str, from_port: str, to_node: str, to_port: str):
        self.from_node = from_node
        self.from_port = from_port
        self.to_node = to_node
        self.to_port = to_port
        self.tube_type = 'fat_tube'
        self.tube_length = '1 ft'
        self.tube_properties = ComponentLibrary.TUBE_TYPES['fat_tube'].copy()

class ApparatusNetwork:
    """Manages the apparatus network graph and validation."""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.connections: List[NetworkConnection] = []
        self.graph = nx.DiGraph()
    
    def add_node(self, node: NetworkNode) -> bool:
        """Add a component node to the network."""
        if node.name in self.nodes:
            return False
        self.nodes[node.name] = node
        self.graph.add_node(node.name, component=node)
        return True
    
    def remove_node(self, name: str):
        """Remove a component node and all its connections."""
        if name in self.nodes:
            # Remove connections
            self.connections = [conn for conn in self.connections 
                             if conn.from_node != name and conn.to_node != name]
            # Remove from graph
            if self.graph.has_node(name):
                self.graph.remove_node(name)
            del self.nodes[name]
    
    def add_connection(self, connection: NetworkConnection) -> bool:
        """Add a connection between two nodes."""
        if (connection.from_node not in self.nodes or 
            connection.to_node not in self.nodes):
            return False
        
        self.connections.append(connection)
        self.graph.add_edge(connection.from_node, connection.to_node, 
                          connection=connection)
        return True
    
    def remove_connection(self, from_node: str, to_node: str):
        """Remove a connection between two nodes."""
        self.connections = [conn for conn in self.connections 
                          if not (conn.from_node == from_node and conn.to_node == to_node)]
        if self.graph.has_edge(from_node, to_node):
            self.graph.remove_edge(from_node, to_node)
    
    def validate_network(self) -> List[str]:
        """Validate the network and return list of errors."""
        errors = []
        
        # Check for disconnected components
        if len(self.nodes) > 1 and not nx.is_weakly_connected(self.graph):
            errors.append("Network contains disconnected components")
        
        # Check for cycles (optional warning)
        if not nx.is_directed_acyclic_graph(self.graph):
            errors.append("Network contains cycles (may be intentional)")
        
        # Check that vessels are properly connected
        for name, node in self.nodes.items():
            if node.component_type == 'Vessel':
                if not list(self.graph.successors(name)):
                    errors.append(f"Vessel '{name}' has no output connections")
        
        return errors

class NetworkApparatusDesigner:
    """Main GUI application for network-based apparatus design."""
    
    def __init__(self):
        self.network = ApparatusNetwork()
        self.selected_node = None
        self.selected_connection = None
        self.component_counter = defaultdict(int)
        
        # Create GUI components
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Component Library Panel
        self.component_library = self._create_component_library()
        
        # Network Canvas Panel  
        self.network_canvas = self._create_network_canvas()
        
        # Properties Panel
        self.properties_panel = self._create_properties_panel()
        
        # Code Preview Panel
        self.code_preview = self._create_code_preview()
        
        # Toolbar
        self.toolbar = self._create_toolbar()
    
    def _create_component_library(self):
        """Create the component library panel."""
        library_widgets = []
        
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
        
        return widgets.VBox(library_widgets, 
                          layout=widgets.Layout(width='220px', height='600px', 
                                               overflow='auto', border='1px solid #ccc',
                                               padding='10px'))
    
    def _create_network_canvas(self):
        """Create the network canvas panel."""
        # Canvas header with controls
        canvas_header = widgets.HBox([
            widgets.HTML("<h3>🔗 Apparatus Network</h3>"),
            widgets.Button(description="🔄 Refresh", 
                         button_style='info',
                         layout=widgets.Layout(width='100px')),
            widgets.Button(description="✅ Validate", 
                         button_style='success',
                         layout=widgets.Layout(width='100px'))
        ])
        
        # Network visualization area
        self.network_display = widgets.Output(
            layout=widgets.Layout(height='500px', border='2px dashed #ccc',
                                background_color='#fafafa', overflow='auto')
        )
        
        # Connection controls
        connection_controls = widgets.HBox([
            widgets.HTML("Connect: "),
            widgets.Dropdown(options=[], description="From:",
                           layout=widgets.Layout(width='150px')),
            widgets.HTML(" → "),
            widgets.Dropdown(options=[], description="To:",
                           layout=widgets.Layout(width='150px')),
            widgets.Button(description="Add Connection", button_style='primary')
        ])
        
        return widgets.VBox([canvas_header, self.network_display, connection_controls],
                          layout=widgets.Layout(width='600px'))
    
    def _create_properties_panel(self):
        """Create the properties configuration panel."""
        # Component properties section
        comp_props_header = widgets.HTML("<h4>🔧 Component Properties</h4>")
        self.comp_name_input = widgets.Text(description="Name:", 
                                          layout=widgets.Layout(width='200px'))
        self.comp_type_display = widgets.HTML("Type: <i>None selected</i>")
        
        # Dynamic properties area
        self.dynamic_props = widgets.VBox([])
        
        # Connection properties section
        conn_props_header = widgets.HTML("<h4>🔗 Connection Properties</h4>")
        self.tube_type_dropdown = widgets.Dropdown(
            options=list(ComponentLibrary.TUBE_TYPES.keys()),
            description="Tube Type:",
            layout=widgets.Layout(width='200px')
        )
        self.tube_length_input = widgets.Text(
            value="1 ft",
            description="Length:",
            layout=widgets.Layout(width='200px')
        )
        
        # Apply button
        apply_button = widgets.Button(
            description="Apply Changes",
            button_style='success',
            layout=widgets.Layout(width='200px')
        )
        apply_button.on_click(self._apply_properties)
        
        return widgets.VBox([
            comp_props_header,
            self.comp_name_input,
            self.comp_type_display,
            self.dynamic_props,
            widgets.HTML("<hr>"),
            conn_props_header,
            self.tube_type_dropdown,
            self.tube_length_input,
            widgets.HTML("<hr>"),
            apply_button
        ], layout=widgets.Layout(width='250px', height='600px', 
                               overflow='auto', border='1px solid #ccc',
                               padding='10px'))
    
    def _create_code_preview(self):
        """Create the generated code preview panel."""
        code_header = widgets.HBox([
            widgets.HTML("<h4>🐍 Generated Apparatus Code</h4>"),
            widgets.Button(description="📋 Copy Code", button_style='info'),
            widgets.Button(description="💾 Save Config", button_style='success')
        ])
        
        self.code_output = widgets.Textarea(
            value="# Apparatus code will appear here...",
            layout=widgets.Layout(width='100%', height='150px'),
            disabled=True
        )
        
        return widgets.VBox([code_header, self.code_output],
                          layout=widgets.Layout(height='200px', border='1px solid #ccc',
                                               padding='10px'))
    
    def _create_toolbar(self):
        """Create the main toolbar."""
        return widgets.HBox([
            widgets.Button(description="🆕 New", button_style='primary'),
            widgets.Button(description="📁 Load", button_style='info'),
            widgets.Button(description="💾 Save", button_style='success'),
            widgets.Button(description="🗑️ Clear", button_style='danger'),
            widgets.HTML(" | "),
            widgets.Button(description="⚡ Generate Code", button_style='warning')
        ], layout=widgets.Layout(margin='10px 0'))
    
    def _setup_layout(self):
        """Setup the main GUI layout."""
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
        """Bind event handlers."""
        # Toolbar events
        toolbar_buttons = self.toolbar.children
        toolbar_buttons[0].on_click(self._new_apparatus)      # New
        toolbar_buttons[1].on_click(self._load_apparatus)     # Load  
        toolbar_buttons[2].on_click(self._save_apparatus)     # Save
        toolbar_buttons[3].on_click(self._clear_apparatus)    # Clear
        toolbar_buttons[5].on_click(self._generate_code)      # Generate Code
        
        # Canvas events
        canvas_buttons = self.network_canvas.children[0].children
        canvas_buttons[1].on_click(self._refresh_canvas)      # Refresh
        canvas_buttons[2].on_click(self._validate_network)    # Validate
        
        # Connection events
        connection_button = self.network_canvas.children[2].children[4]
        connection_button.on_click(self._add_connection)
    
    def _add_component(self, component_type: str):
        """Add a new component to the network."""
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
            self._update_connection_dropdowns()
    
    def _refresh_canvas(self, button=None):
        """Refresh the network canvas display."""
        with self.network_display:
            clear_output(wait=True)
            
            if not self.network.nodes:
                print("🏗️ Drag components from the library to start building your apparatus")
                return
            
            print("📊 Current Apparatus Network:")
            print("=" * 50)
            
            # Display nodes
            for name, node in self.network.nodes.items():
                icon = ComponentLibrary.PASSIVE_COMPONENTS.get(node.component_type, {}).get('icon', '🔧')
                if not icon or icon == '🔧':
                    icon = ComponentLibrary.ACTIVE_COMPONENTS.get(node.component_type, {}).get('icon', '🔧')
                print(f"{icon} {name} ({node.component_type})")
            
            print("\n🔗 Connections:")
            if self.network.connections:
                for conn in self.network.connections:
                    print(f"  {conn.from_node} → {conn.to_node} ({conn.tube_type}, {conn.tube_length})")
            else:
                print("  No connections yet")
            
            print(f"\n📈 Network Stats: {len(self.network.nodes)} components, {len(self.network.connections)} connections")
    
    def _update_connection_dropdowns(self):
        """Update the connection dropdown options."""
        node_names = list(self.network.nodes.keys())
        connection_controls = self.network_canvas.children[2].children
        from_dropdown = connection_controls[1]
        to_dropdown = connection_controls[3]
        
        from_dropdown.options = node_names
        to_dropdown.options = node_names
    
    def _add_connection(self, button):
        """Add a connection between two components."""
        connection_controls = self.network_canvas.children[2].children
        from_dropdown = connection_controls[1]
        to_dropdown = connection_controls[3]
        
        if from_dropdown.value and to_dropdown.value and from_dropdown.value != to_dropdown.value:
            connection = NetworkConnection(
                from_dropdown.value, 'out',
                to_dropdown.value, 'in'
            )
            
            if self.network.add_connection(connection):
                self._refresh_canvas()
                self._generate_code()
    
    def _generate_code(self, button=None):
        """Generate MechWolf apparatus code."""
        if not self.network.nodes:
            self.code_output.value = "# No components added yet"
            return
        
        code_lines = []
        code_lines.append("# Generated MechWolf Apparatus Code")
        code_lines.append("import mechwolf as mw")
        code_lines.append("")
        
        # Generate component definitions
        code_lines.append("# Component Definitions")
        for name, node in self.network.nodes.items():
            component_class = ComponentLibrary.PASSIVE_COMPONENTS.get(node.component_type, {}).get('class')
            if not component_class:
                component_class = ComponentLibrary.ACTIVE_COMPONENTS.get(node.component_type, {}).get('class')
            
            if component_class:
                params = []
                for key, value in node.properties.items():
                    if isinstance(value, str):
                        params.append(f'{key}="{value}"')
                    else:
                        params.append(f'{key}={value}')
                params.append(f'name="{name}"')
                
                code_lines.append(f'{name} = {component_class}({", ".join(params)})')
        
        code_lines.append("")
        
        # Generate tube functions
        code_lines.append("# Tube Functions")
        tube_functions = set()
        for conn in self.network.connections:
            if conn.tube_type not in tube_functions:
                tube_info = ComponentLibrary.TUBE_TYPES[conn.tube_type]
                code_lines.append(f'def {conn.tube_type}(length):')
                code_lines.append(f'    return mw.Tube(length=length, ID="{tube_info["ID"]}", '
                                f'OD="{tube_info["OD"]}", material="{tube_info["material"]}")')
                tube_functions.add(conn.tube_type)
        
        code_lines.append("")
        
        # Generate apparatus assembly
        code_lines.append("# Apparatus Assembly")
        code_lines.append('A = mw.Apparatus("Generated Apparatus")')
        
        for conn in self.network.connections:
            code_lines.append(f'A.add({conn.from_node}, {conn.to_node}, '
                            f'{conn.tube_type}("{conn.tube_length}"))')
        
        self.code_output.value = "\n".join(code_lines)
    
    def _validate_network(self, button):
        """Validate the current network."""
        errors = self.network.validate_network()
        
        with self.network_display:
            clear_output(wait=True)
            if errors:
                print("❌ Network Validation Errors:")
                for error in errors:
                    print(f"  • {error}")
            else:
                print("✅ Network validation passed!")
            print("\n" + "="*50)
            
        self._refresh_canvas()
    
    def _apply_properties(self, button):
        """Apply property changes to selected component."""
        # Implementation for applying property changes
        pass
    
    def _new_apparatus(self, button):
        """Create a new apparatus."""
        self.network = ApparatusNetwork()
        self.component_counter.clear()
        self._refresh_canvas()
        self._update_connection_dropdowns()
        self.code_output.value = "# New apparatus - add components to begin"
    
    def _load_apparatus(self, button):
        """Load apparatus from file."""
        # Implementation for loading apparatus
        pass
    
    def _save_apparatus(self, button):
        """Save apparatus to file."""
        # Implementation for saving apparatus
        pass
    
    def _clear_apparatus(self, button):
        """Clear the current apparatus."""
        self._new_apparatus(button)
    
    def display(self):
        """Display the GUI."""
        display(self.main_widget)

# Factory function for easy instantiation
def create_network_apparatus_designer():
    """Create and return a new NetworkApparatusDesigner instance."""
    return NetworkApparatusDesigner()