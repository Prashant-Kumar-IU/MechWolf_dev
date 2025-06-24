"""
Component and connection editors for the apparatus designer.

Contains logic for editing component properties and connections.
"""

import ipywidgets as widgets
from ..registry import ComponentRegistry


class ComponentEditor:
    """Handles component property editing."""
    
    @staticmethod
    def edit_component(component, designer_instance):
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
            # Replace spaces with underscores in component name
            component.name = name_widget.value.replace(" ", "_")
            component.description = description_widget.value
            
            # Update component properties
            for prop_name, widget in input_widgets.items():
                component.properties[prop_name] = widget.value
            
            # Update components dict if name changed
            if old_name != component.name:
                designer_instance.components[component.name] = designer_instance.components.pop(old_name)
                # Update connections that reference this component
                for conn in designer_instance.connections:
                    if conn.from_component == old_name:
                        conn.from_component = component.name
                    if conn.to_component == old_name:
                        conn.to_component = component.name
                
                # Update dropdowns
                designer_instance._update_connection_dropdowns()
                designer_instance._update_connections_display()
            
            # Update displays
            designer_instance._update_active_components_display()
            designer_instance._update_passive_components_display()
            designer_instance._save_to_metadata()
            print(f"✅ Updated properties for {component.name}")
            
            # Reset property editor
            ComponentEditor._reset_property_editor(component.component_type, designer_instance)
        
        def delete_component(_):
            ComponentEditor._delete_component(component, designer_instance)
            print(f"🗑️ Deleted component: {component.name}")
            # Reset property editor
            ComponentEditor._reset_property_editor(component.component_type, designer_instance)
        
        def cancel_edit(_):
            # Reset property editor without saving
            ComponentEditor._reset_property_editor(component.component_type, designer_instance)
        
        apply_btn.on_click(apply_changes)
        delete_btn.on_click(delete_component)
        cancel_btn.on_click(cancel_edit)
        
        # Button row
        button_row = widgets.HBox([apply_btn, delete_btn, cancel_btn])
        prop_widgets.append(button_row)
        
        # Update appropriate property editor
        if component.component_type in ComponentRegistry.ACTIVE_COMPONENTS:
            designer_instance.active_tab.property_editor.children = prop_widgets
        else:
            designer_instance.passive_tab.property_editor.children = prop_widgets
    
    @staticmethod
    def _reset_property_editor(component_type: str, designer_instance):
        """Reset property editor to default state"""
        if component_type in ComponentRegistry.ACTIVE_COMPONENTS:
            # Reset active component editor
            designer_instance.active_tab.component_selector.value = None
            designer_instance.active_tab.property_editor.children = [
                widgets.HTML("<b>Component Properties:</b>"),
                designer_instance.active_tab.component_selector,
                widgets.HTML("<i>Select a component above to edit properties</i>")
            ]
        else:
            # Reset passive component editor
            designer_instance.passive_tab.component_selector.value = None
            designer_instance.passive_tab.property_editor.children = [
                widgets.HTML("<b>Component Properties:</b>"),
                designer_instance.passive_tab.component_selector,
                widgets.HTML("<i>Select a component above to edit properties</i>")
            ]
    
    @staticmethod
    def _delete_component(component, designer_instance):
        """Delete a component from the apparatus."""
        # Remove component
        if component.name in designer_instance.components:
            del designer_instance.components[component.name]
        
        # Remove any connections involving this component
        designer_instance.connections = [conn for conn in designer_instance.connections 
                      if conn.from_component != component.name and conn.to_component != component.name]
        
        # Update displays
        designer_instance._update_active_components_display()
        designer_instance._update_passive_components_display()
        designer_instance._update_connections_display()
        designer_instance._update_connection_dropdowns()
        designer_instance._update_network_visualization()
        designer_instance._save_to_metadata()


class ConnectionEditor:
    """Handles connection editing."""
    
    @staticmethod
    def edit_connection(connection, connection_index, designer_instance):
        """Edit connection properties with edit/delete functionality."""
        # Create connection editor widgets
        prop_widgets = []
        
        prop_widgets.append(widgets.HTML(f"<b>Editing Connection #{connection_index + 1}</b>"))
        
        # From component selector
        from_dropdown = widgets.Dropdown(
            options=[name for name, comp in designer_instance.components.items() if comp.component_type != 'Tube'],
            value=connection.from_component,
            description="From:",
            layout=widgets.Layout(width='250px')
        )
        prop_widgets.append(from_dropdown)
        
        # To component selector
        to_dropdown = widgets.Dropdown(
            options=[name for name, comp in designer_instance.components.items() if comp.component_type != 'Tube'],
            value=connection.to_component,
            description="To:",
            layout=widgets.Layout(width='250px')
        )
        prop_widgets.append(to_dropdown)
        
        # Tube selector
        tube_options = [name for name, comp in designer_instance.components.items() if comp.component_type == 'Tube']
        tube_dropdown = widgets.Dropdown(
            options=tube_options,
            value=connection.tube_type if connection.tube_type in tube_options else (tube_options[0] if tube_options else None),
            description="Tube:",
            layout=widgets.Layout(width='250px')
        )
        prop_widgets.append(tube_dropdown)
        
        prop_widgets.append(widgets.HTML("<hr>"))
        
        # Action buttons
        apply_btn = widgets.Button(description="Apply Changes", button_style='success')
        delete_btn = widgets.Button(description="Delete Connection", button_style='danger')
        cancel_btn = widgets.Button(description="Cancel", button_style='warning')
        
        def apply_changes(_):
            # Update connection properties
            connection.from_component = from_dropdown.value
            connection.to_component = to_dropdown.value
            connection.tube_type = tube_dropdown.value
            
            # Update tube properties if tube component exists
            if connection.tube_type in designer_instance.components:
                tube_comp = designer_instance.components[connection.tube_type]
                connection.tube_properties = tube_comp.properties.copy()
            
            # Update displays
            designer_instance._update_connections_display()
            designer_instance._update_connection_dropdowns()
            designer_instance._update_network_visualization()
            designer_instance._save_to_metadata()
            print(f"✅ Updated connection #{connection_index + 1}")
            
            # Reset connection editor
            ConnectionEditor._reset_connection_editor(designer_instance)
        
        def delete_connection(_):
            # Remove the connection
            if 0 <= connection_index < len(designer_instance.connections):
                del designer_instance.connections[connection_index]
                
                # Update displays
                designer_instance._update_connections_display()
                designer_instance._update_connection_dropdowns()
                designer_instance._update_network_visualization()
                designer_instance._save_to_metadata()
                print(f"🗑️ Deleted connection #{connection_index + 1}")
                
                # Reset connection editor
                ConnectionEditor._reset_connection_editor(designer_instance)
        
        def cancel_edit(_):
            # Reset connection editor without saving
            ConnectionEditor._reset_connection_editor(designer_instance)
        
        apply_btn.on_click(apply_changes)
        delete_btn.on_click(delete_connection)
        cancel_btn.on_click(cancel_edit)
        
        # Button row
        button_row = widgets.HBox([apply_btn, delete_btn, cancel_btn])
        prop_widgets.append(button_row)
        
        # Update connection property editor
        designer_instance.connections_tab.connection_property_editor.children = prop_widgets
    
    @staticmethod
    def _reset_connection_editor(designer_instance):
        """Reset connection property editor to default state."""
        designer_instance.connections_tab.connection_selector.value = None
        designer_instance.connections_tab.connection_property_editor.children = [
            widgets.HTML("<b>Edit Connection:</b>"),
            designer_instance.connections_tab.connection_selector,
            widgets.HTML("<i>Select a connection above to edit or delete</i>")
        ]