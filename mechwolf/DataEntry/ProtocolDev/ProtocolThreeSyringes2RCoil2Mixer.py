from datetime import timedelta
from typing import Dict, Optional

from IPython.display import display

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.DataEntry.ProtocolDev.ProtocolBase import BaseProtocolAlgorithm
from mechwolf.DataEntry.ProtocolDev.ProtocolUI import ProtocolUI
from mechwolf.DataEntry.ProtocolDev.ProtocolCommon import ProtocolCommon


class ProtocolAlgorithm(BaseProtocolAlgorithm):
    """
    Class to create a protocol for controlling three syringe pumps with 2 reactor coils and 2 mixers.
    """
    
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
            data_file = "three_syringes_2rcoil_protocol_data.json"
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
            "delay_time": prev_values.get("delay_time", 10.0),
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
        if values["delay_time"] < 0:
            return "Delay time cannot be negative"
        return None
    
    def _build_protocol(self, values: Dict[str, float]) -> None:
        """
        Build the protocol with the specified parameters.
        
        Args:
            values: Dictionary of parameter values
        """
        switch_time = timedelta(seconds=values["switch_time"])
        delay_time = timedelta(seconds=values["delay_time"])
        
        # Four syringes in this setup (based on original code)
        pump_rate = values["flow_rate"] / 4
        
        # Use absolute values for time calculations but preserve rate sign
        abs_pump_rate = abs(pump_rate)
        active_time = timedelta(seconds=(values["solvent_volume"] / abs_pump_rate * 60))
        rinse_time = timedelta(seconds=(values["rinse_volume"] / abs_pump_rate * 60))

        print("active_time =", active_time)
        print("rinse_time =", rinse_time)
        print("delay =", delay_time)

        # current initialized to 0
        current = timedelta(seconds=0)

        if isinstance(self.components[0], HarvardSyringePump) and isinstance(
            self.components[1], HarvardSyringePump
        ):
            # Dual-channel pumps
            self.protocol.add(
                self.components[0],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )
            self.protocol.add(
                self.components[1],
                start=current + delay_time,
                duration=active_time - delay_time,
                rate=f"{pump_rate * 2} mL/min",
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
                start=current + delay_time,
                duration=active_time - delay_time,
                rate=f"{pump_rate * 2} mL/min",
            )

        current += active_time + switch_time

        if delay_time != timedelta(seconds=0):
            if isinstance(self.components[0], HarvardSyringePump) and isinstance(
                self.components[1], HarvardSyringePump
            ):
                # Dual-channel pumps
                self.protocol.add(
                    self.components[0],
                    start=current,
                    duration=delay_time,
                    rate=f"{pump_rate} mL/min",
                )
                self.protocol.add(
                    self.components[1],
                    start=current,
                    duration=delay_time,
                    rate=f"{pump_rate * 2} mL/min",
                )
                current += delay_time + switch_time
            else:
                # Single-channel pumps
                self.protocol.add(
                    self.components[0],
                    start=current,
                    duration=delay_time,
                    rate=f"{pump_rate} mL/min",
                )
                self.protocol.add(
                    self.components[1],
                    start=current,
                    duration=delay_time,
                    rate=f"{pump_rate} mL/min",
                )
                self.protocol.add(
                    self.components[2],
                    start=current,
                    duration=delay_time,
                    rate=f"{pump_rate * 2} mL/min",
                )
                current += delay_time + switch_time

        if isinstance(self.components[0], HarvardSyringePump) and isinstance(
            self.components[1], HarvardSyringePump
        ):
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
                rate=f"{pump_rate * 2} mL/min",
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
                rate=f"{pump_rate * 2} mL/min",
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
            "Three Syringes Protocol with 2 Reactor Coils and 2 Mixers"
        )
        
        # Display the form and output
        display(form, output_widget)
        
        # Return the protocol but now it will be populated after the user clicks the submit button
        return self.protocol
    
    def _on_submit_clicked(self, b, ui_widgets, form, output_widget):
        """Handle submit button click."""
        ProtocolCommon.handle_submit_click(
            self,
            b, 
            ui_widgets, 
            form, 
            output_widget, 
            "ThreeSyringes2RCoil2Mixer",
            "Protocol for three syringes with two reactor coils and two mixers",
            {"delay_time": True}  # Include delay_time field
        )