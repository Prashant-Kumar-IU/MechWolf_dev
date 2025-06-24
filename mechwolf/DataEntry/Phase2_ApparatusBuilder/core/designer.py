"""
Main TabbedApparatusDesigner class.

Core orchestration logic for the apparatus designer interface.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, List, Any, Optional
from collections import defaultdict

from ..models import (
    ApparatusComponent, 
    ApparatusConnection,
    ComponentValidationError,
    ConnectionValidationError,
    MetadataError
)
from ..registry import ComponentRegistry
from ..ui import TabBuilders, EventHandlers
from .editors import ComponentEditor, ConnectionEditor
from .code_generator import CodeGenerator

# Import experimental metadata system
try:
    from ...experimental_metadata import ExperimentalMetadataManager
    _metadata_available = True
except ImportError:
    _metadata_available = False
    print("Warning: Experimental metadata system not available")


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
        # Create tabs using TabBuilders
        self.active_tab = TabBuilders.create_active_components_tab()
        self.passive_tab = TabBuilders.create_passive_components_tab()
        self.connections_tab = TabBuilders.create_connections_tab()
        
        # Code generation area
        self.code_output = widgets.Textarea(
            value="# Apparatus code will appear here...",
            layout=widgets.Layout(width='100%', height='200px'),
            disabled=True
        )
    
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
        EventHandlers.bind_events(self)
    
    def _add_harvard_pump(self, button):
        """Add a Harvard pump to the apparatus."""
        self.component_counters['HarvardSyringePump'] += 1
        name = f"pump_{self.component_counters['HarvardSyringePump']}"
        # Replace any spaces with underscores in the generated name
        name = name.replace(" ", "_")
        
        component = ApparatusComponent('HarvardSyringePump', name, self.component_counters['HarvardSyringePump'])
        
        # Validate component before adding
        try:
            component.validate_properties()
            self.components[name] = component
            
            self._update_active_components_display()
            self._update_connection_dropdowns()
            self._safe_save_to_metadata()
        except ComponentValidationError as e:
            print(f"⚠️ Component validation failed: {e}")
            # Still add component but warn user
            self.components[name] = component
            self._update_active_components_display()
            self._update_connection_dropdowns()
    
    def _add_passive_component(self, component_type: str):
        """Add a passive component (Vessel or TMixer)."""
        self.component_counters[component_type] += 1
        name = f"{component_type.lower()}_{self.component_counters[component_type]}"
        # Replace any spaces with underscores in the generated name
        name = name.replace(" ", "_")
        
        component = ApparatusComponent(component_type, name, self.component_counters[component_type])
        
        # Validate component before adding
        try:
            component.validate_properties()
            self.components[name] = component
            
            self._update_passive_components_display()
            self._update_connection_dropdowns()
            self._safe_save_to_metadata()
        except ComponentValidationError as e:
            print(f"⚠️ Component validation failed: {e}")
            # Still add component but warn user
            self.components[name] = component
            self._update_passive_components_display()
            self._update_connection_dropdowns()
    
    def _add_connection(self, button):
        """Add a connection between components."""
        from_comp = self.connections_tab.from_component_dropdown.value
        to_comp = self.connections_tab.to_component_dropdown.value
        selected_tube = self.connections_tab.tube_selection_dropdown.value
        
        if from_comp and to_comp and selected_tube and from_comp != to_comp:
            # Find the tube component to get its properties
            if selected_tube in self.components:
                tube_comp = self.components[selected_tube]
                connection = ApparatusConnection(from_comp, to_comp, selected_tube, "")
                # Store tube properties from the user-created tube
                connection.tube_properties = tube_comp.properties.copy()
                connection.tube_type = selected_tube  # Use tube name as type
                
                # Validate connection before adding
                try:
                    connection.validate_connection(self.components)
                    self.connections.append(connection)
                    
                    self._update_connections_display()
                    self._update_connection_dropdowns()
                    self._update_network_visualization()
                    self._safe_save_to_metadata()
                except ConnectionValidationError as e:
                    print(f"⚠️ Connection validation failed: {e}")
                    # Still add connection but warn user
                    self.connections.append(connection)
                    self._update_connections_display()
                    self._update_connection_dropdowns()
                    self._update_network_visualization()
            else:
                print(f"⚠️ Tube '{selected_tube}' not found")
    
    def _generate_code(self, _=None):
        """Generate MechWolf apparatus code."""
        self.code_output.value = CodeGenerator.generate_code(self.components, self.connections)
    
    def _on_tab_change(self, change):
        """Handle tab change events."""
        if change['new'] == 2:  # Connections tab
            self._update_network_visualization()
    
    def _on_active_component_selected(self, change):
        """Handle active component selection for editing."""
        component_name = change['new']
        if component_name and component_name in self.components:
            component = self.components[component_name]
            ComponentEditor.edit_component(component, self)
    
    def _on_passive_component_selected(self, change):
        """Handle passive component selection for editing."""
        component_name = change['new']
        if component_name and component_name in self.components:
            component = self.components[component_name]
            ComponentEditor.edit_component(component, self)
    
    def _on_connection_selected(self, change):
        """Handle connection selection for editing."""
        connection_index = change['new']
        if connection_index is not None and 0 <= connection_index < len(self.connections):
            connection = self.connections[connection_index]
            ConnectionEditor.edit_connection(connection, connection_index, self)
    
    def _update_active_components_display(self):
        """Update the active components list display."""
        active_comps = []
        for comp in self.components.values():
            # Normalize component type
            normalized_type = ComponentRegistry.normalize_component_type(comp.component_type)
            if comp.component_type != normalized_type:
                comp.component_type = normalized_type
            if comp.component_type in ComponentRegistry.ACTIVE_COMPONENTS:
                active_comps.append(comp)
        
        if not active_comps:
            self.active_tab.components_display.value = "<i>No active components added yet</i>"
            return
        
        # Create compact table-style display
        html_lines = [f"<div style='font-weight: bold; margin-bottom: 8px;'>Active Components ({len(active_comps)})</div>"]
        html_lines.append("""
        <table style='width: 100%; border-collapse: collapse; font-size: 0.9em;'>
        <thead>
            <tr style='background: #f0f0f0; border-bottom: 2px solid #ddd;'>
                <th style='padding: 4px 8px; text-align: left; width: 60px;'>Type</th>
                <th style='padding: 4px 8px; text-align: left; width: 120px;'>Name</th>
                <th style='padding: 4px 8px; text-align: left;'>Description</th>
            </tr>
        </thead>
        <tbody>
        """)
        
        for comp in active_comps:
            info = ComponentRegistry.get_component_info(comp.component_type)
            # Truncate description if too long
            description = comp.description if comp.description else "<i>No description</i>"
            if len(description) > 40:
                description = description[:37] + "..."
            
            html_lines.append(f"""
            <tr style='border-bottom: 1px solid #eee; hover: background: #f9f9f9;' 
                onmouseover='this.style.backgroundColor="#f9f9f9"' 
                onmouseout='this.style.backgroundColor=""'>
                <td style='padding: 4px 8px;'>{info['icon']}</td>
                <td style='padding: 4px 8px;'><b>{comp.name}</b></td>
                <td style='padding: 4px 8px; color: #666;' title='{comp.description}'>{description}</td>
            </tr>
            """)
        
        html_lines.append("</tbody></table>")
        self.active_tab.components_display.value = "".join(html_lines)
    
    def _update_passive_components_display(self):
        """Update the passive components list display."""
        passive_comps = [comp for comp in self.components.values() 
                        if comp.component_type in ComponentRegistry.PASSIVE_COMPONENTS]
        
        if not passive_comps:
            self.passive_tab.components_display.value = "<i>No passive components added yet</i>"
            return
        
        # Create compact table-style display
        html_lines = [f"<div style='font-weight: bold; margin-bottom: 8px;'>Passive Components ({len(passive_comps)})</div>"]
        html_lines.append("""
        <table style='width: 100%; border-collapse: collapse; font-size: 0.9em;'>
        <thead>
            <tr style='background: #f0f0f0; border-bottom: 2px solid #ddd;'>
                <th style='padding: 4px 8px; text-align: left; width: 60px;'>Type</th>
                <th style='padding: 4px 8px; text-align: left; width: 120px;'>Name</th>
                <th style='padding: 4px 8px; text-align: left;'>Description</th>
            </tr>
        </thead>
        <tbody>
        """)
        
        for comp in passive_comps:
            info = ComponentRegistry.PASSIVE_COMPONENTS[comp.component_type]
            # Truncate description if too long
            description = comp.description if comp.description else "<i>No description</i>"
            if len(description) > 40:
                description = description[:37] + "..."
            
            html_lines.append(f"""
            <tr style='border-bottom: 1px solid #eee;' 
                onmouseover='this.style.backgroundColor="#f9f9f9"' 
                onmouseout='this.style.backgroundColor=""'>
                <td style='padding: 4px 8px;'>{info['icon']}</td>
                <td style='padding: 4px 8px;'><b>{comp.name}</b></td>
                <td style='padding: 4px 8px; color: #666;' title='{comp.description}'>{description}</td>
            </tr>
            """)
        
        html_lines.append("</tbody></table>")
        self.passive_tab.components_display.value = "".join(html_lines)
    
    def _update_connections_display(self):
        """Update the connections list display."""
        if not self.connections:
            self.connections_tab.connections_display.value = "<i>No connections created yet</i>"
            return
        
        # Create compact table-style display
        html_lines = [f"<div style='font-weight: bold; margin-bottom: 8px;'>Connections ({len(self.connections)})</div>"]
        html_lines.append("""
        <table style='width: 100%; border-collapse: collapse; font-size: 0.9em;'>
        <thead>
            <tr style='background: #f0f0f0; border-bottom: 2px solid #ddd;'>
                <th style='padding: 4px 8px; text-align: left; width: 30px;'>#</th>
                <th style='padding: 4px 8px; text-align: left; width: 120px;'>From</th>
                <th style='padding: 4px 8px; text-align: left; width: 120px;'>To</th>
                <th style='padding: 4px 8px; text-align: left;'>Tube</th>
            </tr>
        </thead>
        <tbody>
        """)
        
        for i, conn in enumerate(self.connections):
            # Get tube component info if it exists
            tube_info_text = conn.tube_type
            if conn.tube_type in self.components:
                tube_comp = self.components[conn.tube_type]
                tube_props = tube_comp.properties
                tube_info_text = f"{conn.tube_type} (ID:{tube_props.get('ID', '?')}, L:{tube_props.get('length', '?')})"
            
            html_lines.append(f"""
            <tr style='border-bottom: 1px solid #eee;' 
                onmouseover='this.style.backgroundColor="#f9f9f9"' 
                onmouseout='this.style.backgroundColor=""'>
                <td style='padding: 4px 8px; color: #999;'>{i+1}</td>
                <td style='padding: 4px 8px;'><b>{conn.from_component}</b></td>
                <td style='padding: 4px 8px;'><b>{conn.to_component}</b></td>
                <td style='padding: 4px 8px; color: #666;'>{tube_info_text}</td>
            </tr>
            """)
        
        html_lines.append("</tbody></table>")
        self.connections_tab.connections_display.value = "".join(html_lines)
    
    def _update_connection_dropdowns(self):
        """Update the connection dropdown options."""
        # Get non-tube components for from/to connections
        non_tube_components = [name for name, comp in self.components.items() 
                              if comp.component_type != 'Tube']
        self.connections_tab.from_component_dropdown.options = non_tube_components
        self.connections_tab.to_component_dropdown.options = non_tube_components
        
        # Get tube components for tube selection
        tube_components = [name for name, comp in self.components.items() 
                          if comp.component_type == 'Tube']
        self.connections_tab.tube_selection_dropdown.options = tube_components
        
        # Update property editor dropdowns
        active_components = []
        passive_components = []
        
        for name, comp in self.components.items():
            comp_type = comp.component_type
            # Handle backward compatibility
            if comp_type == 'HarvardPump':
                comp_type = 'HarvardSyringePump'
                comp.component_type = 'HarvardSyringePump'  # Update for consistency
            
            if comp_type in ComponentRegistry.ACTIVE_COMPONENTS:
                active_components.append(name)
            elif comp_type in ComponentRegistry.PASSIVE_COMPONENTS:
                passive_components.append(name)
        
        self.active_tab.component_selector.options = active_components
        self.passive_tab.component_selector.options = passive_components
        
        # Update connection selector with readable connection descriptions
        # Force clear the dropdown first
        self.connections_tab.connection_selector.options = []
        self.connections_tab.connection_selector.value = None
        
        if self.connections:
            connection_options = []
            for i, conn in enumerate(self.connections):
                tube_info = conn.tube_type
                if conn.tube_type in self.components:
                    tube_comp = self.components[conn.tube_type]
                    tube_props = tube_comp.properties
                    tube_info = f"{conn.tube_type} (ID:{tube_props.get('ID', '?')}, L:{tube_props.get('length', '?')})"
                
                connection_desc = f"#{i+1}: {conn.from_component} → {conn.to_component} via {tube_info}"
                connection_options.append((connection_desc, i))
            
            # Set new options
            self.connections_tab.connection_selector.options = connection_options
    
    def _update_network_visualization(self):
        """Update the network visualization display."""
        with self.connections_tab.network_display:
            clear_output(wait=True)
            
            if not self.components:
                print("🏗️ Add components to see network visualization")
                return
            
            print("📊 Current Apparatus Network:")
            print("=" * 40)
            
            # Show components
            print("\n🔧 Components:")
            for name, comp in self.components.items():
                comp_type = comp.component_type
                # Handle backward compatibility
                if comp_type == 'HarvardPump':
                    comp_type = 'HarvardSyringePump'
                    comp.component_type = 'HarvardSyringePump'
                info = ComponentRegistry.get_all_components().get(comp_type, {})
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
    
    def _safe_save_to_metadata(self):
        """Safely save current apparatus to experimental metadata with validation."""
        if not self.experiment_manager or not _metadata_available:
            return
        
        try:
            # Validate all components before saving
            validation_errors = []
            
            for name, comp in self.components.items():
                try:
                    comp.validate_properties()
                except ComponentValidationError as e:
                    validation_errors.append(f"Component {name}: {e.message}")
            
            # Validate all connections before saving
            for i, conn in enumerate(self.connections):
                try:
                    conn.validate_connection(self.components)
                except ConnectionValidationError as e:
                    validation_errors.append(f"Connection #{i+1}: {e.message}")
            
            # Warn about validation errors but continue saving
            if validation_errors:
                print(f"⚠️ Validation warnings during save:")
                for error in validation_errors[:5]:  # Show max 5 errors
                    print(f"  • {error}")
                if len(validation_errors) > 5:
                    print(f"  ... and {len(validation_errors) - 5} more issues")
            
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
            raise MetadataError(f"Failed to save apparatus data: {str(e)}")
    
    def _save_to_metadata(self):
        """Legacy save method - calls safe save with error handling."""
        try:
            self._safe_save_to_metadata()
        except MetadataError as e:
            print(f"Warning: Could not save to metadata: {e}")
        except Exception as e:
            print(f"Warning: Unexpected error during save: {e}")
    
    def _load_from_metadata(self):
        """Load apparatus from experimental metadata."""
        if not self.experiment_manager or not _metadata_available:
            return
        
        try:
            apparatus_data = self.experiment_manager.apparatus.get_data()
            
            if apparatus_data:
                # Load active components with validation
                for comp_data in apparatus_data.get('components', {}).get('active', []):
                    try:
                        comp = ApparatusComponent.from_dict(comp_data)
                        self.components[comp.name] = comp
                        # Update counter
                        self.component_counters[comp.component_type] = max(
                            self.component_counters[comp.component_type], 
                            comp.instance_id
                        )
                    except (ComponentValidationError, KeyError, ValueError) as e:
                        print(f"⚠️ Skipping invalid active component: {e}")
                
                # Load passive components with validation
                for comp_data in apparatus_data.get('components', {}).get('passive', []):
                    try:
                        comp = ApparatusComponent.from_dict(comp_data)
                        self.components[comp.name] = comp
                        # Update counter
                        self.component_counters[comp.component_type] = max(
                            self.component_counters[comp.component_type], 
                            comp.instance_id
                        )
                    except (ComponentValidationError, KeyError, ValueError) as e:
                        print(f"⚠️ Skipping invalid passive component: {e}")
                
                # Load connections with validation
                for conn_data in apparatus_data.get('connections', []):
                    try:
                        conn = ApparatusConnection.from_dict(conn_data)
                        self.connections.append(conn)
                    except (ConnectionValidationError, KeyError, ValueError) as e:
                        print(f"⚠️ Skipping invalid connection: {e}")
                
                # Update displays
                self._update_active_components_display()
                self._update_passive_components_display()
                self._update_connections_display()
                self._update_connection_dropdowns()
                
        except MetadataError as e:
            print(f"Warning: Metadata loading error: {e}")
        except Exception as e:
            print(f"Warning: Unexpected error during load: {e}")
    
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