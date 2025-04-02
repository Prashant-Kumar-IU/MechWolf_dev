"""
Protocol algorithm for two syringe pumps with one reactor coil and one mixer.

This module defines a class `ProtocolAlgorithm` that creates a protocol for controlling syringe pumps
with a user-friendly interface and parameter storage capabilities.

Classes:
    ProtocolAlgorithm: Creates and manages a protocol for syringe pumps.
"""
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
import time

import ipywidgets as widgets
from IPython.display import display, HTML

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.DataEntry.ProtocolDev.protocol_data_manager import ProtocolDataManager


class ProtocolAlgorithm:
    """Creates and manages protocols for syringe pump operations with parameter persistence."""
    
    def __init__(self, protocol: Protocol, *components: ActiveComponent, data_file: str) -> None:
        """
        Initialize the ProtocolAlgorithm with a protocol, components, and data file path.
        
        Args:
            protocol: The protocol to be populated
            *components: Components to be used in the protocol
            data_file: Path to the data file for saving/loading protocol parameters
        """
        self.protocol = protocol
        self.components = components
        self.data_manager = ProtocolDataManager(data_file)
        
    def _get_default_values(self) -> Dict[str, float]:
        """
        Load previous protocol parameters if available.
        
        Returns:
            Dictionary containing default values for UI widgets
        """
        saved_config = self.data_manager.load_protocol_config()
        
        # Extract previous values or use defaults
        prev_values: Dict[str, Any] = {}
        if saved_config and "pump_entries" in saved_config:
            entries = saved_config["pump_entries"]
            if entries:
                prev_values = entries[-1]  # Get the most recent entry
        
        # Return defaults if no saved values are found
        return {
            "flow_rate": prev_values.get("flow_rate", 5.0),
            "solvent_volume": prev_values.get("solvent_volume", 10.0),
            "rinse_volume": prev_values.get("rinse_volume", 5.0),
            "switch_time": prev_values.get("switch_time", 30.0),
            "timestamp": prev_values.get("timestamp", None)
        }

    def _create_ui_components(self, defaults: Dict[str, float]) -> Tuple[Dict[str, widgets.Widget], widgets.VBox, widgets.Output]:
        """
        Create and organize UI components for the protocol form.
        
        Args:
            defaults: Dictionary containing default values for UI widgets
            
        Returns:
            Tuple containing (widgets_dict, form, output_widget)
        """
        # Styling parameters
        style = {'description_width': '150px'}
        layout = widgets.Layout(width='350px', margin='10px 0px 10px 0px')
        
        # Create input widgets with better styling
        flow_rate_widget = widgets.FloatText(
            description='Flow Rate:',
            style=style,
            layout=layout,
            value=defaults["flow_rate"]
        )
        flow_rate_unit = widgets.Label(value='mL/min')
        
        # Add a dynamic indicator for flow direction
        initial_direction = self._get_flow_direction_html(defaults["flow_rate"])
        flow_direction_indicator = widgets.HTML(
            value=initial_direction,
            layout=widgets.Layout(margin='0px 0px 0px 10px')
        )
        
        solvent_volume_widget = widgets.FloatText(
            description='Solvent Volume:',
            style=style,
            layout=layout,
            value=defaults["solvent_volume"]
        )
        solvent_unit = widgets.Label(value='mL')
        
        rinse_volume_widget = widgets.FloatText(
            description='Rinse Volume:',
            style=style,
            layout=layout,
            value=defaults["rinse_volume"]
        )
        rinse_unit = widgets.Label(value='mL')
        
        switch_time_widget = widgets.FloatText(
            description='Switch Time:',
            style=style,
            layout=layout,
            value=defaults["switch_time"]
        )
        switch_time_unit = widgets.Label(value='seconds')
        
        # Display last run information if available
        last_run_info = widgets.HTML(value='')
        if defaults["timestamp"]:
            last_run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(defaults["timestamp"]))
            last_run_info.value = f'<p style="color:#666;font-style:italic;">Last run: {last_run_time}</p>'
        
        # Create output and button widgets
        output_widget = widgets.Output(layout=widgets.Layout(border='1px solid #ddd', padding='10px', margin='10px 0'))
        
        submit_button = widgets.Button(
            description='Create Protocol',
            button_style='primary',
            icon='check',
            layout=widgets.Layout(width='200px')
        )
        
        # Create horizontal layouts for inputs with their units
        flow_box = widgets.HBox([flow_rate_widget, flow_rate_unit, flow_direction_indicator], 
                               layout=widgets.Layout(align_items='center'))
        solvent_box = widgets.HBox([solvent_volume_widget, solvent_unit], 
                                  layout=widgets.Layout(align_items='center'))
        rinse_box = widgets.HBox([rinse_volume_widget, rinse_unit], 
                                layout=widgets.Layout(align_items='center'))
        switch_box = widgets.HBox([switch_time_widget, switch_time_unit], 
                                 layout=widgets.Layout(align_items='center'))
        
        # Help texts
        help_texts = {
            "flow": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Final flow rate for both syringes combined. Negative values indicate withdrawal.</p>',
            "solvent": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Volume of solvent to be used.</p>',
            "rinse": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Volume of rinse solvent.</p>',
            "switch": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Stall time to allow for syringe switching.</p>'
        }
        
        # Create sections with inputs and their help text
        flow_section = widgets.VBox([flow_box, widgets.HTML(value=help_texts["flow"])])
        solvent_section = widgets.VBox([solvent_box, widgets.HTML(value=help_texts["solvent"])])
        rinse_section = widgets.VBox([rinse_box, widgets.HTML(value=help_texts["rinse"])])
        switch_section = widgets.VBox([switch_box, widgets.HTML(value=help_texts["switch"])])
        
        # Create a container for the form
        form = widgets.VBox([
            last_run_info,
            flow_section, 
            solvent_section, 
            rinse_section, 
            switch_section, 
            submit_button
        ], layout=widgets.Layout(
            border='1px solid #ddd',
            padding='20px',
            margin='10px 0',
            border_radius='5px'
        ))
        
        # Store widgets for later access
        widgets_dict = {
            "flow_rate": flow_rate_widget,
            "solvent_volume": solvent_volume_widget,
            "rinse_volume": rinse_volume_widget,
            "switch_time": switch_time_widget,
            "flow_direction": flow_direction_indicator,
            "submit": submit_button,
            "last_run_info": last_run_info
        }
        
        return widgets_dict, form, output_widget
    
    def _get_flow_direction_html(self, flow_rate: float) -> str:
        """Generate HTML for flow direction indicator based on flow rate."""
        if flow_rate > 0:
            return '<span style="color:green;font-weight:bold">→ Infusing</span>'
        elif flow_rate < 0:
            return '<span style="color:blue;font-weight:bold">← Withdrawing</span>'
        else:
            return '<span style="color:gray;font-weight:bold">○ Stopped</span>'

    def _validate_inputs(self, values: Dict[str, float]) -> Optional[str]:
        """
        Validate input parameters.
        
        Args:
            values: Dictionary of parameter values
            
        Returns:
            Error message string if validation fails, None if valid
        """
        if values["flow_rate"] == 0:
            return "Flow rate cannot be zero"
        if values["solvent_volume"] <= 0:
            return "Solvent volume must be positive"
        if values["rinse_volume"] <= 0:
            return "Rinse volume must be positive"
        if values["switch_time"] < 0:
            return "Switch time cannot be negative"
        return None

    def _build_protocol(self, values: Dict[str, float]) -> None:
        """
        Build the protocol with the specified parameters.
        
        Args:
            values: Dictionary of parameter values
        """
        switch_time = timedelta(seconds=values["switch_time"])
        current = timedelta(seconds=0)

        # Two syringes are being used so dividing by 2:
        # Keep the sign for withdrawal/infusion direction
        pump_rate = values["flow_rate"] / 2

        # Use absolute values for time calculations but keep sign for rate
        abs_pump_rate = abs(pump_rate)
        rinse_time = timedelta(seconds=(values["rinse_volume"] / abs_pump_rate * 60))
        active_time = timedelta(seconds=(values["solvent_volume"] / abs_pump_rate * 60))

        print("Active time =", active_time)
        print("Rinse time =", rinse_time)

        # Add components to protocol for active phase
        if isinstance(self.components[0], HarvardSyringePump):
            # Dual-channel pump
            self.protocol.add(
                self.components[0],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )
        else:
            # Single-channel pumps
            self.protocol.add(
                self.components[0],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )
            self.protocol.add(
                self.components[1],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )

        current += active_time
        current += switch_time

        # Add components to protocol for rinse phase
        if isinstance(self.components[0], HarvardSyringePump):
            # Dual-channel pump
            self.protocol.add(
                self.components[0],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )
        else:
            # Single-channel pumps
            self.protocol.add(
                self.components[0],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )
            self.protocol.add(
                self.components[1],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )

        current += rinse_time
        print(f"TOTAL TIME: {current}")
        
    def _save_protocol_config(self, values: Dict[str, float]) -> None:
        """
        Save protocol configuration to the data file.
        
        Args:
            values: Dictionary of parameter values
        """
        protocol_config = {
            "name": "TwoSyringes1RCoil1Mixer",
            "description": "Protocol for two syringes with one reactor coil and one mixer",
            "pump_entries": [{
                "flow_rate": values["flow_rate"],
                "solvent_volume": values["solvent_volume"],
                "rinse_volume": values["rinse_volume"],
                "switch_time": values["switch_time"],
                "timestamp": time.time()
            }]
        }
        
        # Save the protocol config
        self.data_manager.save_protocol_config(protocol_config)

    def create_protocol(self) -> Protocol:
        """
        Create a protocol based on user input and display the UI.
        
        Returns:
            Protocol: The created protocol with the specified parameters.
        """
        # Display title
        display(HTML('<h2 style="color:#4682B4;">Protocol Parameters</h2>'))
        
        # Get default values
        defaults = self._get_default_values()
        
        # Create UI components
        ui_widgets, form, output_widget = self._create_ui_components(defaults)
        
        # Function to update flow direction indicator when flow rate changes
        def update_flow_direction(change):
            ui_widgets["flow_direction"].value = self._get_flow_direction_html(change["new"])
        
        # Observe changes to flow rate
        ui_widgets["flow_rate"].observe(update_flow_direction, names='value')
        
        # Handle submit button click
        def on_submit_clicked(b):
            # Hide the form when protocol is created
            form.layout.display = 'none'
            
            with output_widget:
                output_widget.clear_output()
                
                # Get values from widgets
                values = {
                    "flow_rate": ui_widgets["flow_rate"].value,
                    "solvent_volume": ui_widgets["solvent_volume"].value,
                    "rinse_volume": ui_widgets["rinse_volume"].value,
                    "switch_time": ui_widgets["switch_time"].value
                }
                
                # Validate inputs
                error = self._validate_inputs(values)
                if error:
                    # Show the form again if there's an error
                    form.layout.display = 'block'
                    display(HTML(f'<p style="color:red;font-weight:bold">Error: {error}</p>'))
                    return
                
                try:
                    # Determine if infusing or withdrawing
                    direction = "infusing" if values["flow_rate"] > 0 else "withdrawing"
                    
                    # Save the protocol config
                    self._save_protocol_config(values)
                    
                    # Display confirmation
                    display(HTML(f'<h3 style="color:green">Processing Protocol with:</h3>'))
                    display(HTML(f'''<ul>
                        <li>Flow Rate: {values["flow_rate"]} mL/min ({direction})</li>
                        <li>Solvent Volume: {values["solvent_volume"]} mL</li>
                        <li>Rinse Volume: {values["rinse_volume"]} mL</li>
                        <li>Switch Time: {values["switch_time"]} seconds</li>
                    </ul>'''))
                    
                    # Build the protocol
                    self._build_protocol(values)
                    
                    display(HTML(f'<p style="color:green;font-weight:bold">Protocol successfully created!</p>'))
                    
                except Exception as e:
                    # Show the form again if there's an error
                    form.layout.display = 'block'
                    display(HTML(f'<p style="color:red;font-weight:bold">Error: {str(e)}</p>'))
        
        # Attach the callback to the button click event
        ui_widgets["submit"].on_click(on_submit_clicked)
        
        # Display the form and output
        display(form, output_widget)
        
        # Return the protocol but now it will be populated after the user clicks the submit button
        return self.protocol