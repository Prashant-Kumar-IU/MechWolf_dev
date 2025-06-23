"""
Connection Builder

Visual interface for building connections between apparatus components.
Provides drag-and-drop style connection management with validation.
"""

import ipywidgets as widgets
from IPython.display import clear_output
from typing import Dict, Any, List, Tuple
import traceback

# Import enhanced input components
try:
    from ..shared_components import EnhancedInputComponents
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False
    print("Warning: Modern UI components not available, using fallback widgets")


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
        
        # Component selection inputs with autocomplete
        if MODERN_UI_AVAILABLE:
            def validate_component(value: str) -> Tuple[bool, str]:
                """Validate component selection"""
                if not value.strip():
                    return False, "Component selection is required"
                # Note: Validation will be updated when components are refreshed
                return True, ""
            
            self.from_component_input_field = EnhancedInputComponents.create_autocomplete_input(
                description="From Component:",
                suggestions=[],
                placeholder="Select source component",
                validation_function=validate_component,
                help_text="Select or type the source component name",
                required=True
            )
            self.from_component_input = self.from_component_input_field.children[1]
            self.from_component_widget = self.from_component_input_field
            
            self.to_component_input_field = EnhancedInputComponents.create_autocomplete_input(
                description="To Component:",
                suggestions=[],
                placeholder="Select destination component",
                validation_function=validate_component,
                help_text="Select or type the destination component name",
                required=True
            )
            self.to_component_input = self.to_component_input_field.children[1]
            self.to_component_widget = self.to_component_input_field
            
            self.tube_input_field = EnhancedInputComponents.create_autocomplete_input(
                description="Via Tube:",
                suggestions=[],
                placeholder="Select connecting tube (optional)",
                help_text="Select tube component for connection or leave empty for direct connection"
            )
            self.tube_input = self.tube_input_field.children[1]
            self.tube_widget = self.tube_input_field
        else:
            # Fallback to text inputs instead of dropdowns
            self.from_component_input = widgets.Text(
                placeholder='Enter source component name',
                description='From:',
                layout=widgets.Layout(width='250px')
            )
            self.from_component_widget = self.from_component_input
            
            self.to_component_input = widgets.Text(
                placeholder='Enter destination component name',
                description='To:',
                layout=widgets.Layout(width='250px')
            )
            self.to_component_widget = self.to_component_input
            
            self.tube_input = widgets.Text(
                placeholder='Enter tube component name (optional)',
                description='Via Tube:',
                layout=widgets.Layout(width='250px')
            )
            self.tube_widget = self.tube_input
        
        # Refresh button to update component lists
        self.refresh_components_button = widgets.Button(
            description='🔄 Refresh',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        self.refresh_components_button.on_click(self._refresh_component_lists)
        
        # Connection type selector
        connection_type_options = ['Direct Connection', 'Via Tube', 'Custom']
        if MODERN_UI_AVAILABLE:
            def validate_connection_type(value: str) -> Tuple[bool, str]:
                """Validate connection type"""
                valid_types = ['Direct Connection', 'Via Tube', 'Custom', 'direct', 'tube', 'custom']
                if value.strip() in valid_types:
                    return True, ""
                return False, f"Connection type must be one of: {', '.join(connection_type_options)}"
            
            self.connection_type_input_field = EnhancedInputComponents.create_autocomplete_input(
                description="Connection Type:",
                suggestions=connection_type_options,
                default_value="Via Tube",
                validation_function=validate_connection_type,
                help_text="Select how components are connected",
                required=True
            )
            self.connection_type_input = self.connection_type_input_field.children[1]
            self.connection_type_widget = self.connection_type_input_field
        else:
            # Fallback to text input
            self.connection_type_input = widgets.Text(
                value='Via Tube',
                placeholder='e.g., Direct Connection, Via Tube',
                description='Connection Type:',
                layout=widgets.Layout(width='200px')
            )
            self.connection_type_widget = self.connection_type_input
        
        self.connection_type_input.observe(self._on_connection_type_change, names='value')
        
        # Additional connection parameters
        if MODERN_UI_AVAILABLE:
            self.connection_notes_input_field = EnhancedInputComponents.create_validated_text_input(
                description="Connection Notes:",
                placeholder="Optional notes about this connection",
                help_text="Add any additional information about this connection"
            )
            self.connection_notes_input = self.connection_notes_input_field.children[1]
            self.connection_notes_widget = self.connection_notes_input_field
        else:
            self.connection_notes_input = widgets.Text(
                placeholder='Optional notes about this connection',
                description='Notes:',
                layout=widgets.Layout(width='400px')
            )
            self.connection_notes_widget = self.connection_notes_input
        
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
        if MODERN_UI_AVAILABLE:
            self._on_connection_type_change({'new': 'Via Tube'})
        else:
            self._on_connection_type_change({'new': self.connection_type_input.value})
        self._refresh_connections_display()
        self._update_connection_diagram()
    
    def _refresh_component_lists(self, _=None):
        """Refresh the component lists"""
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            # Get all components (active and passive)
            active_components = components.get('active', [])
            passive_components = components.get('passive', [])
            
            all_components = active_components + passive_components
            
            # Create component suggestions
            component_suggestions = []
            tube_suggestions = []
            
            for comp in all_components:
                name = comp.get('name', 'Unknown')
                comp_type = comp.get('type', 'Unknown')
                display_name = f"{name} ({comp_type})"
                component_suggestions.append(display_name)
                
                # Separate tubes for tube selection
                if comp_type.lower() == 'tube':
                    tube_suggestions.append(display_name)
            
            if MODERN_UI_AVAILABLE:
                # Update autocomplete suggestions
                self.from_component_input.options = component_suggestions
                self.to_component_input.options = component_suggestions
                self.tube_input.options = tube_suggestions
            else:
                # Fallback: clear current values for text inputs
                self.from_component_input.value = ''
                self.to_component_input.value = ''
                self.tube_input.value = ''
            
        except Exception as e:
            print(f"Error refreshing component lists: {e}")
    
    def _get_connection_type_key(self, input_value: str) -> str:
        """Convert connection type input to internal key"""
        type_mapping = {
            'Direct Connection': 'direct',
            'Via Tube': 'tube', 
            'Custom': 'custom',
            'direct': 'direct',
            'tube': 'tube',
            'custom': 'custom'
        }
        return type_mapping.get(input_value, 'tube')
    
    def _on_connection_type_change(self, change):
        """Handle connection type change"""
        connection_type_input = change['new']
        connection_type = self._get_connection_type_key(connection_type_input)
        
        # Show/hide tube input based on connection type
        if MODERN_UI_AVAILABLE:
            if connection_type == 'tube':
                self.tube_input_field.layout.display = 'flex'
            else:
                self.tube_input_field.layout.display = 'none'
        else:
            # For text inputs, we don't need to hide/show widgets
            pass
    
    def _extract_component_name(self, component_input: str) -> str:
        """Extract component name from display string"""
        # Handle format "ComponentName (ComponentType)"
        if ' (' in component_input:
            return component_input.split(' (')[0]
        return component_input.strip()
    
    def _add_connection(self, _):
        """Add a new connection"""
        try:
            # Get inputs based on UI type
            if MODERN_UI_AVAILABLE:
                from_component_input = self.from_component_input.value.strip()
                to_component_input = self.to_component_input.value.strip()
                connection_type_input = self.connection_type_input.value.strip()
                tube_component_input = self.tube_input.value.strip()
                notes = self.connection_notes_input.value.strip()
            else:
                from_component_input = self.from_component_input.value
                to_component_input = self.to_component_input.value 
                connection_type_input = self.connection_type_input.value
                tube_component_input = self.tube_input.value
                notes = self.connection_notes_input.value.strip()
            
            # Extract component names
            from_component = self._extract_component_name(from_component_input)
            to_component = self._extract_component_name(to_component_input)
            tube_component = self._extract_component_name(tube_component_input) if tube_component_input else ''
            connection_type = self._get_connection_type_key(connection_type_input)
            
            # Validate inputs
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
                if not tube_component:
                    print("❌ Please select a tube for tube connection")
                    return
                connection_config['tube'] = tube_component
            
            # Add notes if provided
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
    
    def _validate_all_connections(self, _):
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
    
    def _auto_connect(self, _):
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
                        # Use tube if available
                        if i < len(tubes):
                            tube = tubes[i]
                            suggestions.append({
                                'from': pump['name'],
                                'to': mixer['name'],
                                'tube': tube['name'],
                                'reason': f'Pump to mixer via {tube["name"]}'
                            })
                        else:
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
        self.from_component_input.value = ''
        self.to_component_input.value = ''
        self.tube_input.value = ''
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
            
            print(f"Components: {len(component_names)} total")
            
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
            self.from_component_widget,
            widgets.HTML("<span style='padding: 20px; font-size: 16px;'>→</span>"),
            self.to_component_widget
        ])
        
        config_row2 = widgets.HBox([
            self.connection_type_widget,
            self.tube_widget
        ])
        
        config_section = widgets.VBox([
            widgets.HTML("<h4>Connection Configuration</h4>"),
            config_row1,
            config_row2,
            self.connection_notes_widget
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