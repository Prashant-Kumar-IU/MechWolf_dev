"""
Connection Builder

Visual interface for building connections between apparatus components.
Provides drag-and-drop style connection management with validation.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, List, Optional, Tuple
import traceback


class ConnectionBuilder:
    """Visual connection building interface"""
    
    def __init__(self, experiment_manager):
        """
        Initialize connection builder
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        self.selected_connections = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create connection building widgets"""
        
        # Component selection dropdowns
        self.from_component_dropdown = widgets.Dropdown(
            description='From:',
            layout=widgets.Layout(width='250px')
        )
        
        self.to_component_dropdown = widgets.Dropdown(
            description='To:',
            layout=widgets.Layout(width='250px')
        )
        
        self.tube_dropdown = widgets.Dropdown(
            description='Via Tube:',
            layout=widgets.Layout(width='250px')
        )
        
        # Refresh button to update component lists
        self.refresh_components_button = widgets.Button(
            description='🔄 Refresh',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        self.refresh_components_button.on_click(self._refresh_component_lists)
        
        # Connection type selector
        self.connection_type_dropdown = widgets.Dropdown(
            options=[
                ('Direct Connection', 'direct'),
                ('Via Tube', 'tube'),
                ('Custom', 'custom')
            ],
            value='tube',
            description='Connection Type:',
            layout=widgets.Layout(width='200px')
        )
        self.connection_type_dropdown.observe(self._on_connection_type_change, names='value')
        
        # Additional connection parameters
        self.connection_notes_input = widgets.Text(
            placeholder='Optional notes about this connection',
            description='Notes:',
            layout=widgets.Layout(width='400px')
        )
        
        # Action buttons
        self.add_connection_button = widgets.Button(
            description='🔗 Add Connection',
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        self.add_connection_button.on_click(self._add_connection)
        
        self.validate_connections_button = widgets.Button(
            description='✅ Validate All',
            button_style='warning',
            layout=widgets.Layout(width='130px')
        )
        self.validate_connections_button.on_click(self._validate_all_connections)
        
        self.auto_connect_button = widgets.Button(
            description='🤖 Auto-Connect',
            button_style='info',
            layout=widgets.Layout(width='130px'),
            tooltip='Automatically suggest connections based on naming'
        )
        self.auto_connect_button.on_click(self._auto_connect)
        
        # Connection visualization
        self.connection_diagram = widgets.Output(
            layout=widgets.Layout(
                height='300px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        # Current connections display
        self.connections_display = widgets.Output(
            layout=widgets.Layout(
                height='300px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Initialize
        self._refresh_component_lists()
        self._on_connection_type_change({'new': self.connection_type_dropdown.value})
        self._refresh_connections_display()
        self._update_connection_diagram()
    
    def _refresh_component_lists(self, button=None):
        """Refresh the component dropdown lists"""
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            # Get all components (active and passive)
            active_components = components.get('active', [])
            passive_components = components.get('passive', [])
            
            all_components = active_components + passive_components
            
            # Create component options
            component_options = [('Select component...', '')]
            for comp in all_components:
                name = comp.get('name', 'Unknown')
                comp_type = comp.get('type', 'Unknown')
                component_options.append((f"{name} ({comp_type})", name))
            
            # Update dropdowns
            self.from_component_dropdown.options = component_options
            self.to_component_dropdown.options = component_options
            
            # Get tubes for tube dropdown
            tube_options = [('Select tube...', '')]
            for comp in passive_components:
                if comp.get('type') == 'Tube':
                    name = comp.get('name', 'Unknown')
                    tube_options.append((name, name))
            
            self.tube_dropdown.options = tube_options
            
        except Exception as e:
            print(f"Error refreshing component lists: {e}")
    
    def _on_connection_type_change(self, change):
        """Handle connection type change"""
        connection_type = change['new']
        
        # Show/hide tube dropdown based on connection type
        if connection_type == 'tube':
            self.tube_dropdown.layout.display = 'flex'
        else:
            self.tube_dropdown.layout.display = 'none'
    
    def _add_connection(self, button):
        """Add a new connection"""
        try:
            # Validate inputs
            from_component = self.from_component_dropdown.value
            to_component = self.to_component_dropdown.value
            connection_type = self.connection_type_dropdown.value
            
            if not from_component:
                print("❌ Please select a 'From' component")
                return
            
            if not to_component:
                print("❌ Please select a 'To' component")
                return
            
            if from_component == to_component:
                print("❌ Cannot connect component to itself")
                return
            
            # Check for duplicate connections
            existing_connections = self.get_connections()
            for conn in existing_connections:
                if (conn.get('from') == from_component and 
                    conn.get('to') == to_component):
                    print(f"❌ Connection from {from_component} to {to_component} already exists")
                    return
            
            # Build connection configuration
            connection_config = {
                'from': from_component,
                'to': to_component,
                'from_type': self._get_component_type(from_component),
                'to_type': self._get_component_type(to_component)
            }
            
            # Add tube if specified
            if connection_type == 'tube':
                tube_name = self.tube_dropdown.value
                if not tube_name:
                    print("❌ Please select a tube for tube connection")
                    return
                connection_config['tube'] = tube_name
            
            # Add notes if provided
            notes = self.connection_notes_input.value.strip()
            if notes:
                connection_config['notes'] = notes
            
            # Validate connection
            validation_errors = self._validate_connection(connection_config)
            if validation_errors:
                print("❌ Connection validation errors:")
                for error in validation_errors:
                    print(f"  • {error}")
                return
            
            # Add to experimental metadata
            success = self.experiment.apparatus.add_connection(connection_config)
            
            if success:
                self.experiment.save()
                self._clear_form()
                self._refresh_connections_display()
                self._update_connection_diagram()
                print(f"✅ Connected {from_component} → {to_component}")
            else:
                print("❌ Failed to add connection")
            
        except Exception as e:
            print(f"❌ Error adding connection: {e}")
            traceback.print_exc()
    
    def _get_component_type(self, component_name: str) -> str:
        """Get the type of a component by name"""
        apparatus_data = self.experiment.apparatus.get_data()
        components = apparatus_data.get('components', {})
        
        # Search in active components
        for comp in components.get('active', []):
            if comp.get('name') == component_name:
                return comp.get('type', 'Unknown')
        
        # Search in passive components
        for comp in components.get('passive', []):
            if comp.get('name') == component_name:
                return comp.get('type', 'Unknown')
        
        return 'Unknown'
    
    def _validate_connection(self, connection: Dict[str, Any]) -> List[str]:
        """Validate a connection configuration"""
        errors = []
        
        from_component = connection.get('from')
        to_component = connection.get('to')
        from_type = connection.get('from_type')
        to_type = connection.get('to_type')
        
        # Basic validation
        if not from_component or not to_component:
            errors.append("Both 'from' and 'to' components are required")
            return errors
        
        # Type compatibility checks
        # Vessels can connect to pumps or mixers
        if from_type == 'Vessel':
            if to_type not in ['HarvardSyringePump', 'VarianPump', 'FreeStepPump', 
                              'TMixer', 'CrossMixer', 'YMixer', 'Tube']:
                errors.append(f"Vessel cannot connect directly to {to_type}")
        
        # Pumps should typically connect to vessels, mixers, or reactors
        elif from_type in ['HarvardSyringePump', 'VarianPump', 'FreeStepPump']:
            if to_type not in ['Vessel', 'TMixer', 'CrossMixer', 'YMixer', 'Reactor', 'Tube']:
                errors.append(f"Pump cannot connect directly to {to_type}")
        
        # Tubes can connect most things
        elif from_type == 'Tube':
            pass  # Tubes are generally flexible
        
        # Mixers should connect to vessels, reactors, or other mixers
        elif from_type in ['TMixer', 'CrossMixer', 'YMixer']:
            if to_type not in ['Vessel', 'Reactor', 'TMixer', 'CrossMixer', 'YMixer', 'Tube']:
                errors.append(f"Mixer cannot connect directly to {to_type}")
        
        # Check if tube is required but not provided
        tube_name = connection.get('tube')
        if not tube_name and from_type != 'Tube' and to_type != 'Tube':
            # Most connections should have a tube
            pass  # Allow direct connections for now
        
        return errors
    
    def _validate_all_connections(self, button):
        """Validate all current connections"""
        try:
            connections = self.get_connections()
            
            if not connections:
                print("ℹ️ No connections to validate")
                return
            
            all_valid = True
            print("🔍 Validating all connections...")
            print("=" * 40)
            
            for i, connection in enumerate(connections):
                errors = self._validate_connection(connection)
                
                from_comp = connection.get('from', 'Unknown')
                to_comp = connection.get('to', 'Unknown')
                
                if errors:
                    all_valid = False
                    print(f"❌ Connection {i+1}: {from_comp} → {to_comp}")
                    for error in errors:
                        print(f"   • {error}")
                else:
                    print(f"✅ Connection {i+1}: {from_comp} → {to_comp}")
            
            print("=" * 40)
            if all_valid:
                print("✅ All connections are valid!")
            else:
                print("❌ Some connections have validation errors")
                
        except Exception as e:
            print(f"❌ Error validating connections: {e}")
    
    def _auto_connect(self, button):
        """Automatically suggest connections based on component names and types"""
        try:
            print("🤖 Analyzing components for auto-connection suggestions...")
            
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            active_components = components.get('active', [])
            passive_components = components.get('passive', [])
            
            suggestions = []
            
            # Simple heuristics for auto-connection
            # 1. Connect vessels with matching reagent names to pumps
            # 2. Connect pumps to mixers
            # 3. Connect mixers to product vessels
            
            # Find vessels and pumps
            vessels = [c for c in passive_components if c.get('type') == 'Vessel']
            pumps = [c for c in active_components if c.get('type') in 
                    ['HarvardSyringePump', 'VarianPump', 'FreeStepPump']]
            mixers = [c for c in passive_components if c.get('type') in 
                     ['TMixer', 'CrossMixer', 'YMixer']]
            tubes = [c for c in passive_components if c.get('type') == 'Tube']
            
            # Suggest pump-to-vessel connections
            for i, pump in enumerate(pumps):
                if i < len(vessels):
                    vessel = vessels[i]
                    suggestions.append({
                        'from': vessel['name'],
                        'to': pump['name'],
                        'reason': 'Vessel to pump for reagent delivery'
                    })
            
            # Suggest pump-to-mixer connections
            if pumps and mixers:
                for i, pump in enumerate(pumps):
                    if i < len(mixers):
                        mixer = mixers[i]
                        suggestions.append({
                            'from': pump['name'],
                            'to': mixer['name'],
                            'reason': 'Pump to mixer for mixing'
                        })
            
            if suggestions:
                print(f"\n💡 Found {len(suggestions)} connection suggestions:")
                for i, suggestion in enumerate(suggestions):
                    print(f"{i+1}. {suggestion['from']} → {suggestion['to']}")
                    print(f"   Reason: {suggestion['reason']}")
                print("\nUse the manual interface above to add these connections.")
            else:
                print("❌ No automatic connection suggestions found")
                print("Try adding more components or use manual connection mode")
                
        except Exception as e:
            print(f"❌ Error generating auto-connections: {e}")
    
    def _clear_form(self):
        """Clear the connection form"""
        self.from_component_dropdown.value = ''
        self.to_component_dropdown.value = ''
        self.tube_dropdown.value = ''
        self.connection_notes_input.value = ''
    
    def _refresh_connections_display(self):
        """Refresh the connections display"""
        with self.connections_display:
            clear_output(wait=True)
            
            connections = self.get_connections()
            
            if not connections:
                print("No connections configured yet.")
                return
            
            print("🔗 APPARATUS CONNECTIONS")
            print("=" * 50)
            
            for i, connection in enumerate(connections):
                from_comp = connection.get('from', 'Unknown')
                to_comp = connection.get('to', 'Unknown')
                tube = connection.get('tube')
                notes = connection.get('notes', '')
                
                if tube:
                    print(f"{i+1}. {from_comp} → {tube} → {to_comp}")
                else:
                    print(f"{i+1}. {from_comp} → {to_comp} (direct)")
                
                if notes:
                    print(f"   Notes: {notes}")
                
                print()
    
    def _update_connection_diagram(self):
        """Update the connection diagram"""
        with self.connection_diagram:
            clear_output(wait=True)
            
            connections = self.get_connections()
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            if not connections:
                print("📊 Connection Diagram")
                print("=" * 30)
                print("No connections to display")
                return
            
            print("📊 CONNECTION DIAGRAM")
            print("=" * 40)
            
            # Create a simple text-based flow diagram
            all_components = (components.get('active', []) + 
                            components.get('passive', []))
            component_names = [c.get('name') for c in all_components]
            
            # Build connection graph
            graph = {}
            for connection in connections:
                from_comp = connection.get('from')
                to_comp = connection.get('to')
                tube = connection.get('tube')
                
                if from_comp not in graph:
                    graph[from_comp] = []
                
                if tube:
                    graph[from_comp].append(f"{tube} → {to_comp}")
                else:
                    graph[from_comp].append(to_comp)
            
            # Display graph
            for component, connections_list in graph.items():
                comp_type = self._get_component_type(component)
                print(f"📌 {component} ({comp_type})")
                for connection in connections_list:
                    print(f"   └─ {connection}")
                print()
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get current connections"""
        apparatus_data = self.experiment.apparatus.get_data()
        return apparatus_data.get('connections', [])
    
    def create_interface(self) -> widgets.Widget:
        """Create the connection builder interface"""
        
        # Connection configuration section
        config_row1 = widgets.HBox([
            self.from_component_dropdown,
            widgets.HTML("<span style='padding: 20px; font-size: 16px;'>→</span>"),
            self.to_component_dropdown
        ])
        
        config_row2 = widgets.HBox([
            self.connection_type_dropdown,
            self.tube_dropdown
        ])
        
        config_section = widgets.VBox([
            widgets.HTML("<h4>Connection Configuration</h4>"),
            config_row1,
            config_row2,
            self.connection_notes_input
        ])
        
        # Control buttons
        button_row1 = widgets.HBox([
            self.refresh_components_button,
            self.add_connection_button
        ])
        
        button_row2 = widgets.HBox([
            self.validate_connections_button,
            self.auto_connect_button
        ])
        
        # Left panel: Configuration
        left_panel = widgets.VBox([
            config_section,
            button_row1,
            button_row2,
            widgets.HTML("<h4>Connection Diagram</h4>"),
            self.connection_diagram
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        # Right panel: Current connections
        right_panel = widgets.VBox([
            widgets.HTML("<h4>Current Connections</h4>"),
            self.connections_display
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        return widgets.HBox([left_panel, right_panel])