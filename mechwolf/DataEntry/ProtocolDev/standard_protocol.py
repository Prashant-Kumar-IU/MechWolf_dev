"""
Standard protocol implementations with shared functionality.

This module provides a standard protocol algorithm that can be extended by specific protocol
implementations to reduce code duplication and ensure consistent behavior.
"""
from datetime import timedelta
from typing import Dict, Optional, List, Any

from IPython.display import display

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.DataEntry.ProtocolDev.protocol_core import BaseProtocolAlgorithm, ProtocolValidator, ProtocolCommon
from mechwolf.DataEntry.ProtocolDev.protocol_ui import ProtocolUI
from mechwolf.DataEntry.ProtocolDev.protocol_operations import ProtocolRinse


class StandardProtocolAlgorithm(BaseProtocolAlgorithm):
    """Standard protocol algorithm with configurable parameters."""
    
    def __init__(
        self, 
        protocol: Protocol, 
        *components: ActiveComponent, 
        data_file: str,
        protocol_name: str,
        protocol_description: str,
        display_title: str,
        channels_per_pump: int = 1,
        num_active_pumps: int = 2,
        with_delay: bool = False,
        use_modified_rates: bool = False
    ) -> None:
        """
        Initialize the StandardProtocolAlgorithm.
        
        Args:
            protocol: The protocol to be populated
            *components: Components to be used in the protocol
            data_file: Path to the data file for saving/loading protocol parameters
            protocol_name: Protocol name for saving
            protocol_description: Protocol description for saving
            display_title: Title to display on the UI form
            channels_per_pump: Number of channels per pump (default 1)
            num_active_pumps: Number of pumps to use in active phase (default 2)
            with_delay: Whether to use delay_time parameter (default False)
            use_modified_rates: Whether to use modified pump rates (default False)
        """
        super().__init__(protocol, *components, data_file=data_file)
        self.protocol_name = protocol_name
        self.protocol_description = protocol_description
        self.display_title = display_title
        self.channels_per_pump = channels_per_pump
        self.num_active_pumps = num_active_pumps
        self.with_delay = with_delay
        self.use_modified_rates = use_modified_rates
        self.switch_time = None  # Will be initialized during _build_protocol
    
    def _get_default_values(self) -> Dict[str, Any]:
        """
        Load previous protocol parameters if available.
        
        Returns:
            Dictionary containing default values for UI widgets
        """
        prev_values = super()._get_default_values()
        # Use the validator with appropriate delay setting
        return ProtocolValidator.get_default_values(prev_values, with_delay=self.with_delay)
    
    def _validate_inputs(self, values: Dict[str, float]) -> Optional[str]:
        """
        Validate input parameters.
        
        Args:
            values: Dictionary of parameter values
            
        Returns:
            Error message string if validation fails, None if valid
        """
        # Use the validator with appropriate delay setting
        return ProtocolValidator.validate_inputs(values, with_delay=self.with_delay)
    
    def get_pump_rates(self, base_rate: float) -> List[float]:
        """
        Generate pump rates for components.
        Override in subclasses for custom rate distributions.
        
        Args:
            base_rate: The base pump rate
            
        Returns:
            List of pump rates for each component
        """
        # Default implementation: all pumps get the same rate
        return [base_rate] * len(self.components)
    
    def add_delay_phase(self, current_time: timedelta, delay_time: timedelta, pump_rates: List[float]) -> timedelta:
        """
        Add a delay phase to the protocol.
        Override in subclasses for custom delay handling.
        
        Args:
            current_time: Current time in the protocol
            delay_time: Duration of the delay
            pump_rates: List of pump rates
            
        Returns:
            Updated current time
        """
        # Default implementation: no delay phase
        return current_time
    
    def _build_protocol(self, values: Dict[str, float]) -> None:
        """
        Build the protocol with the specified parameters.
        
        Args:
            values: Dictionary of parameter values
        """
        self.switch_time = timedelta(seconds=values["switch_time"])
        delay_time = timedelta(seconds=values.get("delay_time", 0))
        current = timedelta(seconds=0)

        # Calculate base pump rate
        pump_rate = values["flow_rate"] / self.num_active_pumps
        
        # Get pump-specific rates (same as base rate by default unless overridden)
        pump_rates = self.get_pump_rates(pump_rate)
        
        # Calculate rinse time using ProtocolRinse
        rinse_time = ProtocolRinse.calculate_rinse_time(
            rinse_volume=values["rinse_volume"],
            flow_rate=pump_rate,
            num_channels=self.channels_per_pump
        )
        # Calculate active time
        active_time = timedelta(seconds=(values["solvent_volume"] / abs(pump_rate) * 60))

        print("Active time =", active_time)
        print("Rinse time =", rinse_time)
        if self.with_delay:
            print("Delay time =", delay_time)

        # Detect Harvard pumps (dual-channel)
        has_harvard_pumps = isinstance(self.components[0], HarvardSyringePump)
        
        # Determine actual number of available components
        available_components = min(len(self.components), self.num_active_pumps)
        
        # Add components to protocol for active phase
        if has_harvard_pumps and self.num_active_pumps <= 2:
            # For dual-channel pumps (up to 2 channels)
            for i, component in enumerate(self.components[:self.num_active_pumps//2 + self.num_active_pumps%2]):
                start_time = current
                if i > 0 and self.with_delay and delay_time.total_seconds() > 0:
                    start_time += delay_time
                    duration = active_time - delay_time
                else:
                    duration = active_time
                    
                self.protocol.add(
                    component,
                    start=start_time,
                    duration=duration,
                    rate=f"{pump_rates[i]} mL/min",
                )
        else:
            # For single-channel pumps or more than 2 channels needed
            for i, component in enumerate(self.components[:available_components]):
                start_time = current
                if i > 0 and self.with_delay and delay_time.total_seconds() > 0:
                    start_time += delay_time
                    duration = active_time - delay_time
                else:
                    duration = active_time
                    
                self.protocol.add(
                    component,
                    start=start_time,
                    duration=duration,
                    rate=f"{pump_rates[i]} mL/min",
                )

        # Update current time
        current += active_time
        current += self.switch_time
        
        # Add delay phase if needed (for custom implementations)
        if self.with_delay:
            current = self.add_delay_phase(current, delay_time, pump_rates)

        # Handle rinse step based on pump configuration
        if self.use_modified_rates:
            # Make sure we have the right number of rates for available components
            # This prevents the "Number of components must match number of pump rates" error
            available_rates = pump_rates[:available_components]
            
            # Use variable rate rinse
            current = ProtocolRinse.add_variable_rate_rinse_step(
                protocol=self.protocol,
                components=self.components[:available_components],
                current_time=current,
                rinse_time=rinse_time,
                pump_rates=available_rates
            )
        else:
            # Use standard rinse
            is_dual_channel = has_harvard_pumps and self.num_active_pumps <= 2
            current = ProtocolRinse.add_rinse_step(
                protocol=self.protocol,
                components=self.components[:available_components],
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
            self.display_title
        )
        
        # Display the form and output
        display(form, output_widget)
        
        # Return the protocol but now it will be populated after the user clicks the submit button
        return self.protocol
        
    def _on_submit_clicked(self, b, ui_widgets, form, output_widget):
        """Handle submit button click."""
        fields = {"delay_time": self.with_delay}  # Only include delay_time if with_delay is True
        
        ProtocolCommon.handle_submit_click(
            self,
            b, 
            ui_widgets, 
            form, 
            output_widget, 
            self.protocol_name,
            self.protocol_description,
            fields
        )
