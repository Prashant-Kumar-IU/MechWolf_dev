"""
Component and connection editors for the apparatus designer.

Contains logic for editing component properties and connections.
"""

# Python version compatibility
from __future__ import annotations

# Handle missing ipywidgets gracefully
try:
    import ipywidgets as widgets
except ImportError:
    # Create mock widgets for environments without ipywidgets
    class MockWidget:
        def __init__(self, **kwargs):
            self.value = kwargs.get('value', '')
            self.description = kwargs.get('description', '')
            self.layout = kwargs.get('layout')
            self.children = kwargs.get('children', [])
            self.style = kwargs.get('style', {})
        
        def on_click(self, callback):
            pass
        
        def observe(self, callback, names=None):
            pass
    
    class MockWidgets:
        Text = MockWidget
        HTML = MockWidget
        HBox = MockWidget
        VBox = MockWidget
        Button = MockWidget
        Dropdown = MockWidget
        Layout = lambda **kwargs: kwargs
        ButtonStyle = lambda **kwargs: kwargs
    
    widgets = MockWidgets()
    print("Warning: ipywidgets not available in editors, using mock widgets")
from ..registry import ComponentRegistry
from ..ui.widgets import UnitValueInput
from ..config.units import UnitSystem
from ..models import ComponentValidationError, ConnectionValidationError


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
            
            # Use UnitValueInput for properties that have units
            if prop_name in ['length', 'ID', 'OD', 'diameter', 'syringe_diameter', 'syringe_volume']:
                widget = UnitValueInput(
                    property_name=prop_name,
                    initial_value=str(current_value),
                    description=f"{prop_name}:",
                    placeholder=f"Enter {prop_name}...",
                    width='400px'
                )
            else:
                # Use regular text input for non-unit properties
                widget = widgets.Text(
                    value=str(current_value),
                    description=f"{prop_name}:",
                    layout=widgets.Layout(width='300px')
                )
            
            input_widgets[prop_name] = widget
            prop_widgets.append(widget)
        
        # Error display widget
        error_display = widgets.HTML(value="", layout=widgets.Layout(margin='5px 0px'))
        
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
                if isinstance(widget, UnitValueInput):
                    component.properties[prop_name] = widget.value
                else:
                    component.properties[prop_name] = widget.value
            
            # Clear any previous error messages
            error_display.value = ""
            
            # Validate component properties after update
            try:
                component.validate_properties()
            except ComponentValidationError as e:
                error_message = f"<div style='color: red; background: #ffe6e6; padding: 8px; border: 1px solid #ff6666; border-radius: 4px; margin: 5px 0;'><b>⚠️ Validation Error:</b> {str(e)}</div>"
                error_display.value = error_message
                # Also print to console for visibility (matching old program style)
                print(f"⚠️ Validation Error: {str(e)}")
                return  # Don't proceed with updates if validation fails
            
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
        
        # Add error display and button row
        prop_widgets.append(error_display)
        button_row = widgets.HBox([apply_btn, delete_btn, cancel_btn])
        prop_widgets.append(button_row)
        
        # Update appropriate property editor
        if component.component_type in ComponentRegistry.ACTIVE_COMPONENTS:
            designer_instance.active_property_editor.children = prop_widgets
        else:
            designer_instance.passive_property_editor.children = prop_widgets
    
    @staticmethod
    def _reset_property_editor(component_type: str, designer_instance):
        """Reset property editor to default state"""
        if component_type in ComponentRegistry.ACTIVE_COMPONENTS:
            # Reset active component editor
            designer_instance.active_component_selector.value = None
            designer_instance.active_property_editor.children = [
                widgets.HTML("<b>Component Properties:</b>"),
                designer_instance.active_component_selector,
                widgets.HTML("<i>Select a component above to edit properties</i>")
            ]
        else:
            # Reset passive component editor
            designer_instance.passive_component_selector.value = None
            designer_instance.passive_property_editor.children = [
                widgets.HTML("<b>Component Properties:</b>"),
                designer_instance.passive_component_selector,
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
        
        # Tube length input with units
        length_input = UnitValueInput(
            property_name='length',
            initial_value=connection.tube_length,
            description="Length:",
            placeholder="Enter tube length...",
            width='300px'
        )
        prop_widgets.append(length_input)
        
        prop_widgets.append(widgets.HTML("<hr>"))
        
        # Error display widget for connections
        conn_error_display = widgets.HTML(value="", layout=widgets.Layout(margin='5px 0px'))
        
        # Action buttons
        apply_btn = widgets.Button(description="Apply Changes", button_style='success')
        delete_btn = widgets.Button(description="Delete Connection", button_style='danger')
        cancel_btn = widgets.Button(description="Cancel", button_style='warning')
        
        def apply_changes(_):
            # Update connection properties
            connection.from_component = from_dropdown.value
            connection.to_component = to_dropdown.value
            connection.tube_type = tube_dropdown.value
            connection.tube_length = length_input.value
            
            # Clear any previous error messages
            conn_error_display.value = ""
            
            # Validate connection
            try:
                connection.validate_connection(designer_instance.components)
            except ConnectionValidationError as e:
                error_message = f"<div style='color: red; background: #ffe6e6; padding: 8px; border: 1px solid #ff6666; border-radius: 4px; margin: 5px 0;'><b>⚠️ Connection Error:</b> {str(e)}</div>"
                conn_error_display.value = error_message
                # Also print to console for visibility (matching old program style)
                print(f"⚠️ Connection Error: {str(e)}")
                return  # Don't proceed with updates if validation fails
            
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
        
        # Add error display and button row
        prop_widgets.append(conn_error_display)
        button_row = widgets.HBox([apply_btn, delete_btn, cancel_btn])
        prop_widgets.append(button_row)
        
        # Update connection property editor
        designer_instance.connection_property_editor.children = prop_widgets
    
    @staticmethod
    def _reset_connection_editor(designer_instance):
        """Reset connection property editor to default state."""
        designer_instance.connection_selector.value = None
        designer_instance.connection_property_editor.children = [
            widgets.HTML("<b>Edit Connection:</b>"),
            designer_instance.connection_selector,
            widgets.HTML("<i>Select a connection above to edit or delete</i>")
        ]