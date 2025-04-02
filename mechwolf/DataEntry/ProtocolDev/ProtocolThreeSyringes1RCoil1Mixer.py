from datetime import timedelta
from typing import Dict, Optional, Any

from IPython.display import display, HTML

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.DataEntry.ProtocolDev.ProtocolBase import BaseProtocolAlgorithm, ProtocolUtils
from mechwolf.DataEntry.ProtocolDev.ProtocolUI import ProtocolUI


class ProtocolAlgorithm(BaseProtocolAlgorithm):
    """Creates and manages protocols for three syringe pumps with one reactor coil and one mixer."""
    
    def __init__(self, protocol: Protocol, *components: ActiveComponent, data_file: str = None) -> None:
        """
        Initialize the ProtocolAlgorithm with a protocol, components, and optional data file path.
        
        Args:
            protocol: The protocol to be populated
            *components: Components to be used in the protocol
            data_file: Path to the data file for saving/loading protocol parameters
        """
        # Default data file if not provided
        if data_file is None:
            data_file = "three_syringes_protocol_data.json"
        super().__init__(protocol, *components, data_file=data_file)
    
    def _get_default_values(self) -> Dict[str, float]:
        """
        Load previous protocol parameters if available.
        
        Returns:
            Dictionary containing default values for UI widgets
        """
        prev_values = super()._get_default_values()
        
        # Return defaults if no saved values are found
        return {
            "flow_rate": prev_values.get("flow_rate", 5.0),
            "solvent_volume": prev_values.get("solvent_volume", 10.0),
            "rinse_volume": prev_values.get("rinse_volume", 5.0),
            "switch_time": prev_values.get("switch_time", 30.0),
            "timestamp": prev_values.get("timestamp", None)
        }
    
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

        # Three syringes are being used so dividing by 3
        pump_rate = values["flow_rate"] / 3

        # Calculate times
        rinse_time = timedelta(seconds=(values["rinse_volume"] / pump_rate * 60))
        active_time = timedelta(seconds=(values["solvent_volume"] / pump_rate * 60))

        print("active_time =", active_time)
        print("rinse_time =", rinse_time)

        if isinstance(self.components[0], HarvardSyringePump):
            # Dual-channel pumps
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
            self.protocol.add(
                self.components[2],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )

        current += active_time + switch_time

        if isinstance(self.components[0], HarvardSyringePump):
            # Dual-channel pumps
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
            self.protocol.add(
                self.components[2],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )

        current += rinse_time

        print(f"TOTAL TIME: {current}")

    def create_protocol(self) -> Protocol:
        """
        Create a protocol based on user input and display the UI.
        
        Returns:
            Protocol: The created protocol with the specified parameters.
        """
        # Get default values
        defaults = self._get_default_values()
        
        # Create UI components
        ui_widgets, form, output_widget = ProtocolUI.create_protocol_form(
            defaults,
            lambda b: self._on_submit_clicked(b, ui_widgets, form, output_widget),
            defaults.get("timestamp"),
            "Three Syringes Protocol Parameters"
        )
        
        # Display the form and output
        display(form, output_widget)
        
        # Return the protocol but now it will be populated after the user clicks the submit button
        return self.protocol
    
    def _on_submit_clicked(self, b, ui_widgets, form, output_widget):
        """Handle submit button click."""
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
                self._save_protocol_config(
                    "ThreeSyringes1RCoil1Mixer",
                    "Protocol for three syringes with one reactor coil and one mixer",
                    values
                )
                
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