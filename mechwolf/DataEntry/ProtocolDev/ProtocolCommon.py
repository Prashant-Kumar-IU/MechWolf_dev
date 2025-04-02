"""
Common functionality for protocol implementations.

This module contains shared code used across different protocol implementations
to reduce duplication and ensure consistent behavior.
"""
from typing import Dict, Any, Callable, Optional
from IPython.display import display, HTML


class ProtocolCommon:
    """Common functionality for protocol implementations."""
    
    @staticmethod
    def handle_submit_click(
        self_obj,
        b, 
        ui_widgets, 
        form, 
        output_widget, 
        protocol_name: str, 
        protocol_description: str, 
        fields: Optional[Dict[str, bool]] = None
    ) -> None:
        """
        Handle submit button click for protocol forms.
        
        Args:
            self_obj: The protocol algorithm instance
            b: Button that triggered the callback
            ui_widgets: Dictionary of UI widgets
            form: The form container widget
            output_widget: Output widget for displaying results
            protocol_name: Name of the protocol
            protocol_description: Description of the protocol
            fields: Dictionary specifying which fields to include in values
                   (keys are field names, values are booleans indicating whether to include)
        """
        # Hide the form when protocol is created
        form.layout.display = 'none'
        
        with output_widget:
            output_widget.clear_output()
            
            # Get values from widgets
            values = {}
            
            # Standard fields all protocols use
            standard_fields = ["flow_rate", "solvent_volume", "rinse_volume", "switch_time"]
            
            # Add standard fields
            for field in standard_fields:
                if field in ui_widgets and (fields is None or fields.get(field, True)):
                    values[field] = ui_widgets[field].value
                    
            # Add optional fields if present
            if "delay_time" in ui_widgets and (fields is None or fields.get("delay_time", False)):
                values["delay_time"] = ui_widgets["delay_time"].value
            
            # Validate inputs
            error = self_obj._validate_inputs(values)
            if error:
                # Show the form again if there's an error
                form.layout.display = 'block'
                display(HTML(f'<p style="color:red;font-weight:bold">Error: {error}</p>'))
                return
            
            try:
                # Determine if infusing or withdrawing
                direction = "infusing" if values["flow_rate"] > 0 else "withdrawing"
                
                # Save the protocol config (timestamp will be added by _save_protocol_config)
                self_obj._save_protocol_config(
                    protocol_name,
                    protocol_description,
                    values
                )
                
                # Display confirmation
                display(HTML(f'<h3 style="color:green">Processing Protocol with:</h3>'))
                
                # Build the HTML list of parameters
                html_list = [
                    f'<li>Flow Rate: {values["flow_rate"]} mL/min ({direction})</li>',
                    f'<li>Solvent Volume: {values["solvent_volume"]} mL</li>',
                    f'<li>Rinse Volume: {values["rinse_volume"]} mL</li>',
                    f'<li>Switch Time: {values["switch_time"]} seconds</li>'
                ]
                
                # Add delay time if present
                if "delay_time" in values:
                    html_list.append(f'<li>Delay Time: {values["delay_time"]} seconds</li>')
                
                # Display the parameters
                display(HTML(f'<ul>{"".join(html_list)}</ul>'))
                
                # Build the protocol
                self_obj._build_protocol(values)
                
                display(HTML(f'<p style="color:green;font-weight:bold">Protocol successfully created!</p>'))
                
            except Exception as e:
                # Show the form again if there's an error
                form.layout.display = 'block'
                display(HTML(f'<p style="color:red;font-weight:bold">Error: {str(e)}</p>'))
