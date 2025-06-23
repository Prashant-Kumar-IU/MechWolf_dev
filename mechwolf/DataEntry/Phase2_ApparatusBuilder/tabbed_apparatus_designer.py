"""
Tabbed Apparatus Designer for MechWolf Development

A clean 3-tab interface focused on Harvard pumps, tubing, and T-mixers for 
development purposes. Uses the experimental metadata system for data management.

Tab Structure:
- Tab 1: Active Components (Harvard Pumps)
- Tab 2: Passive Components (Vessels, T-Mixers, Tubing)
- Tab 3: Network Connections

Designed for extensibility to add more components later.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

# Import experimental metadata system
try:
    from ..experimental_metadata import ExperimentalMetadataManager
    _metadata_available = True
except ImportError:
    _metadata_available = False
    print("Warning: Experimental metadata system not available")

class ComponentRegistry:
    """Registry for available components - designed for easy extension."""
    
    # Active Components (Tab 1)
    ACTIVE_COMPONENTS = {
        'HarvardPump': {
            'class_name': 'HarvardPump',
            'import_path': 'mechwolf.components.contrib.harvardpump',
            'display_name': 'Harvard Syringe Pump',
            'icon': '💉',
            'default_properties': {
                'syringe_volume': '3 mL',
                'syringe_diameter': '10 mm',
                'serial_port': 'COM1'
            },
            'required_properties': ['syringe_volume', 'syringe_diameter', 'serial_port'],
            'property_types': {
                'syringe_volume': 'text',
                'syringe_diameter': 'text', 
                'serial_port': 'text'
            }
        }
    }
    
    # Passive Components (Tab 2)
    PASSIVE_COMPONENTS = {
        'Vessel': {
            'class_name': 'Vessel',
            'import_path': 'mechwolf',
            'display_name': 'Reagent Vessel',
            'icon': '🧪',
            'default_properties': {},
            'required_properties': [],  # Remove description to avoid duplicate with main description field
            'property_types': {}
        },
        'TMixer': {
            'class_name': 'TMixer',
            'import_path': 'mechwolf',
            'display_name': 'T-Mixer',
            'icon': '🔀',
            'default_properties': {},
            'required_properties': [],
            'property_types': {}
        },
        'Tube': {
            'class_name': 'Tube',
            'import_path': 'mechwolf',
            'display_name': 'Tubing',
            'icon': '🔗',
            'default_properties': {
                'length': '1 ft',
                'ID': '1/16 in',
                'OD': '1/8 in',
                'material': 'PFA'
            },
            'required_properties': ['length', 'ID', 'OD', 'material'],
            'property_types': {
                'length': 'text',
                'ID': 'text',
                'OD': 'text',
                'material': 'text'
            }
        }
    }
    
    # Tube Specifications (used in connections)
    TUBE_TYPES = {
        'fat_tube': {
            'ID': '1/16 in',
            'OD': '1/8 in', 
            'material': 'PFA',
            'description': 'Standard fat tube'
        },
        'thin_tube': {
            'ID': '0.030 in',
            'OD': '1/16 in',
            'material': 'PFA',
            'description': 'Thin precision tube'
        },
        'thinner_tube': {
            'ID': '0.020 in',
            'OD': '1/16 in',
            'material': 'PFA',
            'description': 'Ultra-thin tube'
        },
        'valve_tube': {
            'ID': '0.020 in',
            'OD': '1/16 in',
            'material': 'PFA',
            'description': 'Valve connection tube'
        }
    }
    
    @classmethod
    def get_all_components(cls):
        """Get all available components for dropdown menus."""
        all_comps = {}
        all_comps.update(cls.ACTIVE_COMPONENTS)
        all_comps.update(cls.PASSIVE_COMPONENTS)
        return all_comps
    
    @classmethod
    def add_component_type(cls, category: str, comp_type: str, config: Dict[str, Any]):
        """Add a new component type for future extensibility."""
        if category == 'active':
            cls.ACTIVE_COMPONENTS[comp_type] = config
        elif category == 'passive':
            cls.PASSIVE_COMPONENTS[comp_type] = config

class ApparatusComponent:
    """Represents a single component in the apparatus."""
    
    def __init__(self, component_type: str, name: str, instance_id: int):
        self.component_type = component_type
        self.name = name
        self.instance_id = instance_id
        self.description = ""  # User-defined description
        self.properties = {}
        self.registry_info = ComponentRegistry.get_all_components().get(component_type, {})
        
        # Set default properties
        if 'default_properties' in self.registry_info:
            self.properties = self.registry_info['default_properties'].copy()
    
    def to_dict(self):
        """Convert to dictionary for metadata storage."""
        return {
            'type': self.component_type,  # Match ApparatusDataManager expected format
            'name': self.name,
            'description': self.description,
            'instance_id': self.instance_id,
            'properties': self.properties,
            'registry_info': self.registry_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create component from dictionary."""
        comp_type = data.get('type', data.get('component_type', ''))
        comp = cls(comp_type, data['name'], data.get('instance_id', 0))
        comp.description = data.get('description', '')
        comp.properties = data.get('properties', {})
        return comp

class ApparatusConnection:
    """Represents a connection between two components."""
    
    def __init__(self, from_component: str, to_component: str, tube_type: str = 'fat_tube', tube_length: str = '1 ft'):
        self.from_component = from_component
        self.to_component = to_component
        self.tube_type = tube_type
        self.tube_length = tube_length
        self.tube_properties = ComponentRegistry.TUBE_TYPES.get(tube_type, {}).copy()
    
    def to_dict(self):
        """Convert to dictionary for metadata storage."""
        return {
            'from': self.from_component,  # Match ApparatusDataManager expected format
            'to': self.to_component,
            'tube_type': self.tube_type,
            'tube_length': self.tube_length,
            'tube_properties': self.tube_properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create connection from dictionary."""
        from_comp = data.get('from', data.get('from_component', ''))
        to_comp = data.get('to', data.get('to_component', ''))
        conn = cls(
            from_comp,
            to_comp, 
            data.get('tube_type', 'fat_tube'),
            data.get('tube_length', '1 ft')
        )
        conn.tube_properties = data.get('tube_properties', {})
        return conn

class TabbedApparatusDesigner:
    """
    Main tabbed interface for apparatus design.
    
    Uses simple network representation (components + connections lists)
    for development simplicity - not NetworkX graphs.
    """
    
    def __init__(self, experiment_manager: Optional[Any] = None):
        self.experiment_manager = experiment_manager
        self.components: Dict[str, ApparatusComponent] = {}
        self.connections: List[ApparatusConnection] = []
        self.component_counters = defaultdict(int)
        
        # Create the interface
        self._create_widgets()
        self._setup_tabs()
        self._bind_events()
        
        # Load existing data if available
        if self.experiment_manager:
            self._load_from_metadata()
    
    def _create_widgets(self):
        """Create all widget components."""
        # Tab 1: Active Components
        self.active_tab = self._create_active_components_tab()
        
        # Tab 2: Passive Components
        self.passive_tab = self._create_passive_components_tab()
        
        # Tab 3: Network Connections
        self.connections_tab = self._create_connections_tab()
        
        # Code generation area
        self.code_output = widgets.Textarea(
            value="# Apparatus code will appear here...",
            layout=widgets.Layout(width='100%', height='200px'),
            disabled=True
        )
    
    def _create_active_components_tab(self):
        """Create Tab 1: Active Components (Harvard Pumps)."""
        # Header
        header = widgets.HTML("<h3>💉 Active Components - Harvard Pumps</h3>")
        
        # Add component section
        add_section = widgets.VBox([
            widgets.HTML("<b>Add Harvard Pump:</b>"),
            widgets.Button(
                description="+ Add Harvard Pump",
                button_style='success',
                layout=widgets.Layout(width='200px')
            )
        ])
        
        # Component list container (scrollable HTML)
        self.active_components_display = widgets.HTML(
            value="<i>No active components added yet</i>",
            layout=widgets.Layout(height='300px', overflow='auto', 
                                border='1px solid #eee', padding='5px')
        )
        
        # Property editor with component selector
        self.active_component_selector = widgets.Dropdown(
            options=[],
            description="Select:",
            layout=widgets.Layout(width='200px')
        )
        
        self.active_property_editor = widgets.VBox([
            widgets.HTML("<b>Component Properties:</b>"),
            self.active_component_selector,
            widgets.HTML("<i>Select a component above to edit properties</i>")
        ])
        
        return widgets.VBox([
            header,
            add_section,
            widgets.HTML("<hr>"),
            widgets.HTML("<b>Active Components List:</b>"),
            self.active_components_display,
            widgets.HTML("<hr>"),
            self.active_property_editor
        ])
    
    def _create_passive_components_tab(self):
        """Create Tab 2: Passive Components (Vessels, T-Mixers)."""
        # Header
        header = widgets.HTML("<h3>🧪 Passive Components - Vessels, Mixers & Tubes</h3>")
        
        # Add component buttons
        add_vessel_btn = widgets.Button(
            description="🧪 Add Vessel",
            button_style='info',
            layout=widgets.Layout(width='140px', margin='2px')
        )
        
        add_tmixer_btn = widgets.Button(
            description="🔀 Add T-Mixer", 
            button_style='info',
            layout=widgets.Layout(width='140px', margin='2px')
        )
        
        add_tube_btn = widgets.Button(
            description="🔗 Add Tube",
            button_style='info', 
            layout=widgets.Layout(width='140px', margin='2px')
        )
        
        add_section = widgets.VBox([
            widgets.HTML("<b>Add Components:</b>"),
            widgets.HBox([add_vessel_btn, add_tmixer_btn, add_tube_btn])
        ])
        
        # Component list container (scrollable HTML)
        self.passive_components_display = widgets.HTML(
            value="<i>No passive components added yet</i>",
            layout=widgets.Layout(height='300px', overflow='auto',
                                border='1px solid #eee', padding='5px')
        )
        
        # Property editor with component selector
        self.passive_component_selector = widgets.Dropdown(
            options=[],
            description="Select:",
            layout=widgets.Layout(width='200px')
        )
        
        self.passive_property_editor = widgets.VBox([
            widgets.HTML("<b>Component Properties:</b>"),
            self.passive_component_selector,
            widgets.HTML("<i>Select a component above to edit properties</i>")
        ])
        
        return widgets.VBox([
            header,
            add_section,
            widgets.HTML("<hr>"),
            widgets.HTML("<b>Passive Components List:</b>"),
            self.passive_components_display,
            widgets.HTML("<hr>"),
            self.passive_property_editor
        ])
    
    def _create_connections_tab(self):
        """Create Tab 3: Network Connections."""
        # Header
        header = widgets.HTML("<h3>🔗 Network Connections</h3>")
        
        # Connection builder
        self.from_component_dropdown = widgets.Dropdown(
            options=[],
            description="From:",
            layout=widgets.Layout(width='200px')
        )
        
        self.to_component_dropdown = widgets.Dropdown(
            options=[],
            description="To:",
            layout=widgets.Layout(width='200px')
        )
        
        self.tube_selection_dropdown = widgets.Dropdown(
            options=[],
            description="Tube:",
            layout=widgets.Layout(width='200px')
        )
        
        add_connection_btn = widgets.Button(
            description="Add Connection",
            button_style='primary',
            layout=widgets.Layout(width='150px')
        )
        
        connection_builder = widgets.VBox([
            widgets.HTML("<b>Create Connection:</b>"),
            widgets.HBox([
                self.from_component_dropdown,
                widgets.HTML(" → "),
                self.to_component_dropdown
            ]),
            widgets.HBox([
                self.tube_selection_dropdown,
                add_connection_btn
            ])
        ])
        
        # Connections list container (scrollable HTML)
        self.connections_display = widgets.HTML(
            value="<i>No connections created yet</i>",
            layout=widgets.Layout(height='200px', overflow='auto',
                                border='1px solid #eee', padding='5px')
        )
        
        # Network visualization (scrollable)
        self.network_display = widgets.Output(
            layout=widgets.Layout(height='200px', border='1px solid #ccc', overflow='auto')
        )
        
        return widgets.VBox([
            header,
            connection_builder,
            widgets.HTML("<hr>"),
            widgets.HTML("<b>Connections List:</b>"),
            self.connections_display,
            widgets.HTML("<hr>"),
            widgets.HTML("<b>Network Overview:</b>"),
            self.network_display
        ])
    
    def _setup_tabs(self):
        """Setup the main tab widget."""
        self.tab_widget = widgets.Tab()
        self.tab_widget.children = [
            self.active_tab,
            self.passive_tab, 
            self.connections_tab
        ]
        
        self.tab_widget.set_title(0, "Active Components")
        self.tab_widget.set_title(1, "Passive Components")
        self.tab_widget.set_title(2, "Network Connections")
        
        # Code generation section
        code_header = widgets.HBox([
            widgets.HTML("<h4>🐍 Generated Apparatus Code</h4>"),
            widgets.Button(description="🔄 Generate Code", button_style='warning')
        ])
        
        # Main layout
        self.main_widget = widgets.VBox([
            self.tab_widget,
            widgets.HTML("<hr>"),
            code_header,
            self.code_output
        ])
    
    def _bind_events(self):
        """Bind event handlers to widgets."""
        # Active components tab
        add_pump_btn = self.active_tab.children[1].children[1]
        add_pump_btn.on_click(self._add_harvard_pump)
        
        # Passive components tab
        passive_buttons = self.passive_tab.children[1].children[1].children
        passive_buttons[0].on_click(lambda b: self._add_passive_component('Vessel'))
        passive_buttons[1].on_click(lambda b: self._add_passive_component('TMixer'))
        passive_buttons[2].on_click(lambda b: self._add_passive_component('Tube'))
        
        # Connections tab
        add_conn_btn = self.connections_tab.children[1].children[2].children[1]
        add_conn_btn.on_click(self._add_connection)
        
        # Code generation
        gen_code_btn = self.main_widget.children[2].children[1]
        gen_code_btn.on_click(self._generate_code)
        
        # Tab change events
        self.tab_widget.observe(self._on_tab_change, names='selected_index')
        
        # Component selector events
        self.active_component_selector.observe(self._on_active_component_selected, names='value')
        self.passive_component_selector.observe(self._on_passive_component_selected, names='value')
    
    def _add_harvard_pump(self, button):
        """Add a Harvard pump to the apparatus."""
        self.component_counters['HarvardPump'] += 1
        name = f"pump_{self.component_counters['HarvardPump']}"
        
        component = ApparatusComponent('HarvardPump', name, self.component_counters['HarvardPump'])
        self.components[name] = component
        
        self._update_active_components_display()
        self._update_connection_dropdowns()
        self._save_to_metadata()
    
    def _add_passive_component(self, component_type: str):
        """Add a passive component (Vessel or TMixer)."""
        self.component_counters[component_type] += 1
        name = f"{component_type.lower()}_{self.component_counters[component_type]}"
        
        component = ApparatusComponent(component_type, name, self.component_counters[component_type])
        self.components[name] = component
        
        self._update_passive_components_display()
        self._update_connection_dropdowns()
        self._save_to_metadata()
    
    def _add_connection(self, button):
        """Add a connection between components."""
        from_comp = self.from_component_dropdown.value
        to_comp = self.to_component_dropdown.value
        selected_tube = self.tube_selection_dropdown.value
        
        if from_comp and to_comp and selected_tube and from_comp != to_comp:
            # Find the tube component to get its properties
            if selected_tube in self.components:
                tube_comp = self.components[selected_tube]
                connection = ApparatusConnection(from_comp, to_comp, selected_tube, "")
                # Store tube properties from the user-created tube
                connection.tube_properties = tube_comp.properties.copy()
                connection.tube_type = selected_tube  # Use tube name as type
                self.connections.append(connection)
                
                self._update_connections_display()
                self._update_network_visualization()
                self._save_to_metadata()
            else:
                print(f"⚠️ Tube '{selected_tube}' not found")
    
    def _update_active_components_display(self):
        """Update the active components list display."""
        active_comps = [comp for comp in self.components.values() 
                       if comp.component_type in ComponentRegistry.ACTIVE_COMPONENTS]
        
        if not active_comps:
            self.active_components_display.value = "<i>No active components added yet</i>"
            return
        
        html_lines = []
        for comp in active_comps:
            info = ComponentRegistry.ACTIVE_COMPONENTS[comp.component_type]
            description_text = f"<br>&nbsp;&nbsp;&nbsp;&nbsp;<i>{comp.description}</i>" if comp.description else ""
            
            # Create simple HTML display
            html_lines.append(f"""
            <div style="margin: 5px 0; padding: 8px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
                {info['icon']} <b>{comp.name}</b> ({info['display_name']}){description_text}
            </div>
            """)
        
        self.active_components_display.value = "".join(html_lines)
    
    def _update_passive_components_display(self):
        """Update the passive components list display."""
        passive_comps = [comp for comp in self.components.values() 
                        if comp.component_type in ComponentRegistry.PASSIVE_COMPONENTS]
        
        if not passive_comps:
            self.passive_components_display.value = "<i>No passive components added yet</i>"
            return
        
        html_lines = []
        for comp in passive_comps:
            info = ComponentRegistry.PASSIVE_COMPONENTS[comp.component_type]
            description_text = f"<br>&nbsp;&nbsp;&nbsp;&nbsp;<i>{comp.description}</i>" if comp.description else ""
            
            # Create simple HTML display
            html_lines.append(f"""
            <div style="margin: 5px 0; padding: 8px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
                {info['icon']} <b>{comp.name}</b> ({info['display_name']}){description_text}
            </div>
            """)
        
        self.passive_components_display.value = "".join(html_lines)
    
    def _update_connections_display(self):
        """Update the connections list display."""
        if not self.connections:
            self.connections_display.value = "<i>No connections created yet</i>"
            return
        
        html_lines = []
        for i, conn in enumerate(self.connections):
            # Get tube component info if it exists
            tube_info_text = conn.tube_type
            if conn.tube_type in self.components:
                tube_comp = self.components[conn.tube_type]
                tube_props = tube_comp.properties
                tube_info_text = f"{conn.tube_type} (ID: {tube_props.get('ID', 'N/A')}, {tube_props.get('length', 'N/A')})"
            
            # Create simple HTML display 
            html_lines.append(f"""
            <div style="margin: 5px 0; padding: 8px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
                🔗 <b>{conn.from_component}</b> → <b>{conn.to_component}</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;via {tube_info_text}
                <div style="font-size: 0.9em; color: #666; margin-top: 4px;">
                    Connection #{i+1}
                </div>
            </div>
            """)
        
        self.connections_display.value = "".join(html_lines)
    
    def _update_connection_dropdowns(self):
        """Update the connection dropdown options."""
        # Get non-tube components for from/to connections
        non_tube_components = [name for name, comp in self.components.items() 
                              if comp.component_type != 'Tube']
        self.from_component_dropdown.options = non_tube_components
        self.to_component_dropdown.options = non_tube_components
        
        # Get tube components for tube selection
        tube_components = [name for name, comp in self.components.items() 
                          if comp.component_type == 'Tube']
        self.tube_selection_dropdown.options = tube_components
        
        # Update property editor dropdowns
        active_components = [name for name, comp in self.components.items() 
                           if comp.component_type in ComponentRegistry.ACTIVE_COMPONENTS]
        self.active_component_selector.options = active_components
        
        passive_components = [name for name, comp in self.components.items() 
                            if comp.component_type in ComponentRegistry.PASSIVE_COMPONENTS]
        self.passive_component_selector.options = passive_components
    
    def _update_network_visualization(self):
        """Update the network visualization display."""
        with self.network_display:
            clear_output(wait=True)
            
            if not self.components:
                print("🏗️ Add components to see network visualization")
                return
            
            print("📊 Current Apparatus Network:")
            print("=" * 40)
            
            # Show components
            print("\n🔧 Components:")
            for name, comp in self.components.items():
                info = ComponentRegistry.get_all_components().get(comp.component_type, {})
                icon = info.get('icon', '🔧')
                display_name = info.get('display_name', comp.component_type)
                description_text = f" - {comp.description}" if comp.description else ""
                print(f"  {icon} {name} ({display_name}){description_text}")
            
            # Show connections
            print(f"\n🔗 Connections ({len(self.connections)}):")
            if self.connections:
                for conn in self.connections:
                    tube_info = ""
                    if conn.tube_type in self.components:
                        tube_comp = self.components[conn.tube_type]
                        tube_props = tube_comp.properties
                        tube_info = f" (ID: {tube_props.get('ID', 'N/A')}, Length: {tube_props.get('length', 'N/A')})"
                    print(f"  {conn.from_component} → {conn.to_component} via {conn.tube_type}{tube_info}")
            else:
                print("  No connections yet")
            
            print(f"\n📈 Stats: {len(self.components)} components, {len(self.connections)} connections")
    
    def _edit_component(self, component: ApparatusComponent):
        """Edit component properties."""
        # Create property editor widgets
        prop_widgets = []
        info = ComponentRegistry.get_all_components().get(component.component_type, {})
        
        prop_widgets.append(widgets.HTML(f"<b>Editing: {component.name}</b>"))
        
        # Component name and description editors
        name_widget = widgets.Text(
            value=component.name,
            description="Name:",
            layout=widgets.Layout(width='300px')
        )
        prop_widgets.append(name_widget)
        
        description_widget = widgets.Text(
            value=component.description,
            description="Description:",
            placeholder="Enter component description...",
            layout=widgets.Layout(width='300px')
        )
        prop_widgets.append(description_widget)
        
        prop_widgets.append(widgets.HTML("<hr>"))
        
        # Create input widgets for each property
        input_widgets = {}
        for prop_name in info.get('required_properties', []):
            current_value = component.properties.get(prop_name, '')
            widget = widgets.Text(
                value=str(current_value),
                description=f"{prop_name}:",
                layout=widgets.Layout(width='300px')
            )
            input_widgets[prop_name] = widget
            prop_widgets.append(widget)
        
        # Action buttons
        apply_btn = widgets.Button(description="Apply Changes", button_style='success')
        delete_btn = widgets.Button(description="Delete Component", button_style='danger')
        cancel_btn = widgets.Button(description="Cancel", button_style='warning')
        
        def apply_changes(_):
            # Update name and description
            old_name = component.name
            component.name = name_widget.value
            component.description = description_widget.value
            
            # Update component properties
            for prop_name, widget in input_widgets.items():
                component.properties[prop_name] = widget.value
            
            # Update components dict if name changed
            if old_name != component.name:
                self.components[component.name] = self.components.pop(old_name)
                # Update connections that reference this component
                for conn in self.connections:
                    if conn.from_component == old_name:
                        conn.from_component = component.name
                    if conn.to_component == old_name:
                        conn.to_component = component.name
                
                # Update dropdowns
                self._update_connection_dropdowns()
                self._update_connections_display()
            
            # Update displays
            self._update_active_components_display()
            self._update_passive_components_display()
            self._save_to_metadata()
            print(f"✅ Updated properties for {component.name}")
            
            # Reset property editor
            self._reset_property_editor(component.component_type)
        
        def delete_component(_):
            self._delete_component(component)
            print(f"🗑️ Deleted component: {component.name}")
            # Reset property editor
            self._reset_property_editor(component.component_type)
        
        def cancel_edit(_):
            # Reset property editor without saving
            self._reset_property_editor(component.component_type)
        
        apply_btn.on_click(apply_changes)
        delete_btn.on_click(delete_component)
        cancel_btn.on_click(cancel_edit)
        
        # Button row
        button_row = widgets.HBox([apply_btn, delete_btn, cancel_btn])
        prop_widgets.append(button_row)
        
        # Update appropriate property editor
        if component.component_type in ComponentRegistry.ACTIVE_COMPONENTS:
            self.active_property_editor.children = prop_widgets
        else:
            self.passive_property_editor.children = prop_widgets
    
    def _reset_property_editor(self, component_type: str):
        """Reset property editor to default state"""
        if component_type in ComponentRegistry.ACTIVE_COMPONENTS:
            # Reset active component editor
            self.active_component_selector.value = None
            self.active_property_editor.children = [
                widgets.HTML("<b>Component Properties:</b>"),
                self.active_component_selector,
                widgets.HTML("<i>Select a component above to edit properties</i>")
            ]
        else:
            # Reset passive component editor
            self.passive_component_selector.value = None
            self.passive_property_editor.children = [
                widgets.HTML("<b>Component Properties:</b>"),
                self.passive_component_selector,
                widgets.HTML("<i>Select a component above to edit properties</i>")
            ]
    
    def _delete_component(self, component: ApparatusComponent):
        """Delete a component from the apparatus."""
        # Remove component
        if component.name in self.components:
            del self.components[component.name]
        
        # Remove any connections involving this component
        self.connections = [conn for conn in self.connections 
                          if conn.from_component != component.name and conn.to_component != component.name]
        
        # Update displays
        self._update_active_components_display()
        self._update_passive_components_display()
        self._update_connections_display()
        self._update_connection_dropdowns()
        self._update_network_visualization()
        self._save_to_metadata()
    
    def _delete_connection(self, index: int):
        """Delete a connection."""
        if 0 <= index < len(self.connections):
            del self.connections[index]
            self._update_connections_display()
            self._update_network_visualization()
            self._save_to_metadata()
    
    def _generate_code(self, _=None):
        """Generate MechWolf apparatus code."""
        if not self.components:
            self.code_output.value = "# No components added yet"
            return
        
        code_lines = []
        code_lines.append("# Generated MechWolf Apparatus Code")
        code_lines.append("import mechwolf as mw")
        code_lines.append("from mechwolf.components.contrib.harvardpump import HarvardPump")
        code_lines.append("")
        
        # Generate component definitions
        code_lines.append("# Component Definitions")
        for name, comp in self.components.items():
            info = ComponentRegistry.get_all_components()[comp.component_type]
            class_name = info['class_name']
            
            # Build parameters
            params = []
            for prop_name, prop_value in comp.properties.items():
                if prop_value:  # Only include non-empty properties
                    params.append(f'{prop_name}="{prop_value}"')
            params.append(f'name="{name}"')
            
            if comp.component_type == 'HarvardPump':
                code_lines.append(f'{name} = HarvardPump({", ".join(params)})')
            else:
                code_lines.append(f'{name} = mw.{class_name}({", ".join(params)})')
        
        code_lines.append("")
        
        # No need for tube functions since tubes are components
        code_lines.append("")
        
        # Generate apparatus assembly
        code_lines.append("# Apparatus Assembly")
        code_lines.append('A = mw.Apparatus("Generated Apparatus")')
        
        for conn in self.connections:
            code_lines.append(f'A.add({conn.from_component}, {conn.to_component}, {conn.tube_type})')
        
        self.code_output.value = "\n".join(code_lines)
    
    def _on_tab_change(self, change):
        """Handle tab change events."""
        if change['new'] == 2:  # Connections tab
            self._update_network_visualization()
    
    def _on_active_component_selected(self, change):
        """Handle active component selection for editing."""
        component_name = change['new']
        if component_name and component_name in self.components:
            component = self.components[component_name]
            self._edit_component(component)
    
    def _on_passive_component_selected(self, change):
        """Handle passive component selection for editing."""
        component_name = change['new']
        if component_name and component_name in self.components:
            component = self.components[component_name]
            self._edit_component(component)
    
    def _save_to_metadata(self):
        """Save current apparatus to experimental metadata."""
        if not self.experiment_manager or not _metadata_available:
            return
        
        try:
            # Clear existing apparatus data and rebuild
            self.experiment_manager.apparatus.save_data({
                'components': {'active': [], 'passive': []},
                'connections': []
            })
            
            # Save components separately as active/passive
            for name, comp in self.components.items():
                comp_dict = comp.to_dict()
                if comp.component_type in ComponentRegistry.ACTIVE_COMPONENTS:
                    self.experiment_manager.apparatus.add_active_component(comp_dict)
                else:
                    self.experiment_manager.apparatus.add_passive_component(comp_dict)
            
            # Save connections
            for conn in self.connections:
                self.experiment_manager.apparatus.add_connection(conn.to_dict())
            
            self.experiment_manager.save()
        except Exception as e:
            print(f"Warning: Could not save to metadata: {e}")
    
    def _load_from_metadata(self):
        """Load apparatus from experimental metadata."""
        if not self.experiment_manager or not _metadata_available:
            return
        
        try:
            apparatus_data = self.experiment_manager.apparatus.get_data()
            
            if apparatus_data:
                # Load active components
                for comp_data in apparatus_data.get('components', {}).get('active', []):
                    comp = ApparatusComponent.from_dict(comp_data)
                    self.components[comp.name] = comp
                    # Update counter
                    self.component_counters[comp.component_type] = max(
                        self.component_counters[comp.component_type], 
                        comp.instance_id
                    )
                
                # Load passive components
                for comp_data in apparatus_data.get('components', {}).get('passive', []):
                    comp = ApparatusComponent.from_dict(comp_data)
                    self.components[comp.name] = comp
                    # Update counter
                    self.component_counters[comp.component_type] = max(
                        self.component_counters[comp.component_type], 
                        comp.instance_id
                    )
                
                # Load connections
                for conn_data in apparatus_data.get('connections', []):
                    conn = ApparatusConnection.from_dict(conn_data)
                    self.connections.append(conn)
                
                # Update displays
                self._update_active_components_display()
                self._update_passive_components_display()
                self._update_connections_display()
                self._update_connection_dropdowns()
                
        except Exception as e:
            print(f"Warning: Could not load from metadata: {e}")
    
    def display(self):
        """Display the tabbed apparatus designer."""
        display(self.main_widget)
    
    def get_apparatus_data(self):
        """Get current apparatus data for external use."""
        return {
            'components': {name: comp.to_dict() for name, comp in self.components.items()},
            'connections': [conn.to_dict() for conn in self.connections],
            'generated_code': self.code_output.value
        }

# Factory function
def create_tabbed_apparatus_designer(experiment_manager=None):
    """Create and return a TabbedApparatusDesigner instance."""
    return TabbedApparatusDesigner(experiment_manager)