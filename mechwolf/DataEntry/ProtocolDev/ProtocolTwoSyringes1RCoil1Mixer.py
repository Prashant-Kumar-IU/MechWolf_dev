"""
Protocol algorithm for two syringe pumps with one reactor coil and one mixer.

This module defines a class `ProtocolAlgorithm` that creates a protocol for controlling syringe pumps
with a user-friendly interface and parameter storage capabilities.
"""
from datetime import timedelta
from typing import Dict, Optional

from IPython.display import display

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.DataEntry.ProtocolDev.ProtocolBase import BaseProtocolAlgorithm
from mechwolf.DataEntry.ProtocolDev.ProtocolUI import ProtocolUI
from mechwolf.DataEntry.ProtocolDev.ProtocolCommon import ProtocolCommon
from mechwolf.DataEntry.ProtocolDev.ProtocolRinse import ProtocolRinse


class ProtocolAlgorithm(BaseProtocolAlgorithm):
    """Creates and manages protocols for two syringe pumps with one reactor coil and one mixer."""
    
    def __init__(self, protocol: Protocol, *components: ActiveComponent, data_file: str) -> None:
        """
        Initialize the ProtocolAlgorithm with a protocol, components, and data file path.
        
        Args:
            protocol: The protocol to be populated
            *components: Components to be used in the protocol
            data_file: Path to the data file for saving/loading protocol parameters
        """
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
            "flow_rate": prev_values.get("flow_rate", 1.0),
            "solvent_volume": prev_values.get("solvent_volume", 1.0),
            "rinse_volume": prev_values.get("rinse_volume", 1.0),
            "switch_time": prev_values.get("switch_time", 1.0),
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

        # Two syringes are being used so dividing by 2:
        # Keep the sign for withdrawal/infusion direction
        pump_rate = values["flow_rate"] / 2

        # Calculate rinse time using ProtocolRinse
        rinse_time = ProtocolRinse.calculate_rinse_time(
            rinse_volume=values["rinse_volume"],
            flow_rate=pump_rate,
            num_channels=1
        )
        # Calculate active time
        active_time = timedelta(seconds=(values["solvent_volume"] / abs(pump_rate) * 60))

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

        # Use the ProtocolRinse module for the rinse step
        is_dual_channel = isinstance(self.components[0], HarvardSyringePump)
        current = ProtocolRinse.add_rinse_step(
            protocol=self.protocol,
            components=self.components,
            current_time=current,
            rinse_time=rinse_time,
            pump_rate=pump_rate,
            is_dual_channel=is_dual_channel
        )

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
            "Two Syringes Protocol Parameters"
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
            "TwoSyringes1RCoil1Mixer",
            "Protocol for two syringes with one reactor coil and one mixer"
        )