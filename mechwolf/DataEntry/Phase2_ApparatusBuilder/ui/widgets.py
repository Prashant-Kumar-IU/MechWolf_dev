"""
Custom UI widgets for Phase2_ApparatusBuilder.

Contains composite widgets that combine multiple ipywidgets for enhanced functionality.
"""

# Python version compatibility
from __future__ import annotations

# Handle missing ipywidgets gracefully
try:
    import ipywidgets as widgets
    _ipywidgets_available = True
except ImportError:
    # Create mock widgets for environments without ipywidgets
    class MockWidget:
        def __init__(self, **kwargs):
            self.value = kwargs.get('value', '')
            self.options = kwargs.get('options', [])
            self.layout = kwargs.get('layout')
            self.children = kwargs.get('children', [])
    
    class MockWidgets:
        HBox = MockWidget
        VBox = MockWidget
        Text = MockWidget
        Dropdown = MockWidget
        HTML = MockWidget
        Label = MockWidget
        Layout = lambda **kwargs: kwargs
    
    widgets = MockWidgets()
    _ipywidgets_available = False
    print("Warning: ipywidgets not available, using mock widgets")

from typing import Optional, List, Callable, Any, Dict, Tuple
from ..config.units import UnitSystem


class UnitValueInput(widgets.HBox if _ipywidgets_available else object):
    """
    Composite widget combining numeric input with unit dropdown.
    
    Provides a unified interface for entering values with units,
    automatic validation, and proper formatting.
    """
    
    def __init__(
        self, 
        property_name: str,
        initial_value: str = "",
        description: str = "",
        placeholder: str = "",
        width: str = "300px",
        value_width: str = "180px",
        unit_width: str = "100px"
    ):
        """
        Initialize UnitValueInput widget.
        
        Args:
            property_name: Name of the property (determines available units)
            initial_value: Initial value string (e.g., "1.5 ft")
            description: Label description
            placeholder: Placeholder text for value input
            width: Total widget width
            value_width: Width of value input
            unit_width: Width of unit dropdown
        """
        self.property_name = property_name
        self._on_change_callbacks = []
        
        # Parse initial value
        initial_numeric, initial_unit = UnitSystem.parse_value_with_unit(initial_value)
        
        # Get available units and default
        available_units = UnitSystem.get_available_units(property_name)
        default_unit = UnitSystem.get_default_unit(property_name)
        
        # Use initial unit if valid, otherwise default
        if initial_unit and initial_unit in available_units:
            selected_unit = initial_unit
        else:
            selected_unit = default_unit
        
        # Create value input widget
        self.value_input = widgets.Text(
            value=str(initial_numeric) if initial_numeric is not None else "",
            placeholder=placeholder or f"Enter {property_name}...",
            layout=widgets.Layout(width=value_width),
            style={'description_width': '0px'}
        )
        
        # Create unit dropdown
        self.unit_dropdown = widgets.Dropdown(
            options=available_units,
            value=selected_unit,
            layout=widgets.Layout(width=unit_width),
            style={'description_width': '0px'}
        )
        
        # Create label if description provided
        widgets_list = []
        if description:
            label = widgets.Label(
                value=description,
                layout=widgets.Layout(width='80px', margin='0 5px 0 0')
            )
            widgets_list.append(label)
        
        widgets_list.extend([self.value_input, self.unit_dropdown])
        
        # Initialize parent HBox
        super().__init__(
            children=widgets_list,
            layout=widgets.Layout(width=width, align_items='center')
        )
        
        # Bind change events
        self.value_input.observe(self._on_value_change, names='value')
        self.unit_dropdown.observe(self._on_unit_change, names='value')
    
    @property
    def value(self) -> str:
        """Get the current value as a formatted string (e.g., '1.5 ft')."""
        if not self.value_input.value.strip():
            return ""
        
        try:
            numeric_value = float(self.value_input.value.strip())
            return UnitSystem.format_value_with_unit(numeric_value, self.unit_dropdown.value)
        except ValueError:
            return self.value_input.value.strip()
    
    @value.setter
    def value(self, value_str: str):
        """Set the value from a formatted string (e.g., '1.5 ft')."""
        if not value_str:
            self.value_input.value = ""
            return
        
        numeric_value, unit = UnitSystem.parse_value_with_unit(value_str)
        
        if numeric_value is not None:
            self.value_input.value = str(numeric_value)
        
        if unit and unit in self.unit_dropdown.options:
            self.unit_dropdown.value = unit
    
    @property
    def numeric_value(self) -> Optional[float]:
        """Get the numeric value as a float."""
        if not self.value_input.value.strip():
            return None
        
        try:
            return float(self.value_input.value.strip())
        except ValueError:
            return None
    
    @property
    def unit(self) -> str:
        """Get the current unit."""
        return self.unit_dropdown.value
    
    def get_value_in_unit(self, target_unit: str) -> Optional[float]:
        """Get the numeric value converted to a specific unit."""
        numeric = self.numeric_value
        if numeric is None:
            return None
        
        return UnitSystem.convert_value(numeric, self.unit, target_unit)
    
    def set_unit_options(self, new_options: List[str]):
        """Update the available unit options."""
        current_unit = self.unit_dropdown.value
        self.unit_dropdown.options = new_options
        
        # Keep current unit if still available
        if current_unit in new_options:
            self.unit_dropdown.value = current_unit
        else:
            self.unit_dropdown.value = new_options[0] if new_options else ""
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the current value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.value_input.value.strip():
            return True, ""  # Empty is valid (optional field)
        
        # Check if numeric value is valid
        if self.numeric_value is None:
            return False, f"Invalid numeric value: '{self.value_input.value}'"
        
        # Check if unit is valid for this property
        if not UnitSystem.validate_unit_for_property(self.unit, self.property_name):
            available_units = UnitSystem.get_available_units(self.property_name)
            return False, f"Unit '{self.unit}' not valid for {self.property_name}. Use: {', '.join(available_units)}"
        
        # Property-specific validation
        if self.numeric_value <= 0:
            return False, f"{self.property_name} must be positive"
        
        return True, ""
    
    def set_error_state(self, has_error: bool, message: str = ""):
        """Set visual error state of the widget."""
        if has_error:
            self.value_input.style = {'description_width': '0px', 'text_color': 'red'}
            if message:
                # Could add tooltip or help text here
                pass
        else:
            self.value_input.style = {'description_width': '0px', 'text_color': 'black'}
    
    def observe_changes(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for when the value changes."""
        self._on_change_callbacks.append(callback)
    
    def _on_value_change(self, change):
        """Handle value input changes."""
        self._notify_change({'type': 'value', 'new': change['new'], 'old': change['old']})
    
    def _on_unit_change(self, change):
        """Handle unit dropdown changes."""
        self._notify_change({'type': 'unit', 'new': change['new'], 'old': change['old']})
    
    def _notify_change(self, change_info):
        """Notify all registered callbacks of changes."""
        for callback in self._on_change_callbacks:
            try:
                callback(change_info)
            except Exception as e:
                print(f"Error in UnitValueInput change callback: {e}")


class ValidatedUnitInput(UnitValueInput):
    """
    UnitValueInput with built-in validation display.
    
    Shows validation errors below the input and changes styling based on validation state.
    """
    
    def __init__(self, property_name: str, **kwargs):
        # Create validation message area
        self.validation_message = widgets.HTML(
            value="",
            layout=widgets.Layout(width='300px', height='20px')
        )
        
        # Initialize parent
        super().__init__(property_name, **kwargs)
        
        # Add validation display to layout
        self.children = list(self.children) + [self.validation_message]
        self.layout = widgets.Layout(flex_flow='column', align_items='flex-start')
        
        # Auto-validate on changes
        self.observe_changes(self._auto_validate)
    
    def _auto_validate(self, change_info):
        """Automatically validate when values change."""
        _ = change_info  # Acknowledge parameter
        is_valid, message = self.validate()
        
        if is_valid:
            self.validation_message.value = ""
            self.set_error_state(False)
        else:
            self.validation_message.value = f"<span style='color: red; font-size: 0.9em;'>⚠️ {message}</span>"
            self.set_error_state(True, message)


class PropertyEditorWidget(widgets.VBox if _ipywidgets_available else object):
    """
    Complete property editor with unit-aware inputs for component properties.
    
    Automatically creates appropriate input widgets based on property types.
    """
    
    def __init__(self, component_type: str):
        self.component_type = component_type
        self.property_widgets = {}
        
        # Will be populated by _create_property_inputs
        super().__init__()
        
        self._create_property_inputs()
    
    def _create_property_inputs(self):
        """Create input widgets for all component properties."""
        # This would be populated based on ComponentRegistry info
        # For now, create a basic structure
        
        widgets_list = [
            widgets.HTML(f"<b>Properties for {self.component_type}:</b>")
        ]
        
        # This would be expanded based on component registry data
        self.children = widgets_list
    
    def get_all_values(self) -> Dict[str, str]:
        """Get all property values as a dictionary."""
        values = {}
        for prop_name, widget in self.property_widgets.items():
            if isinstance(widget, UnitValueInput):
                values[prop_name] = widget.value
            elif hasattr(widget, 'value'):
                values[prop_name] = widget.value
        return values
    
    def set_values(self, values: Dict[str, str]):
        """Set property values from a dictionary."""
        for prop_name, value in values.items():
            if prop_name in self.property_widgets:
                widget = self.property_widgets[prop_name]
                if isinstance(widget, UnitValueInput):
                    widget.value = value
                elif hasattr(widget, 'value'):
                    widget.value = value
    
    def validate_all(self) -> Tuple[bool, List[str]]:
        """
        Validate all properties.
        
        Returns:
            Tuple of (all_valid, list_of_error_messages)
        """
        errors = []
        
        for prop_name, widget in self.property_widgets.items():
            if isinstance(widget, UnitValueInput):
                is_valid, message = widget.validate()
                if not is_valid:
                    errors.append(f"{prop_name}: {message}")
        
        return len(errors) == 0, errors