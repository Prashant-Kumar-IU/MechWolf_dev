"""
Protocol algorithm for two syringe pumps with one reactor coil and one mixer.

This module defines a class `ProtocolAlgorithm` that creates a protocol for controlling syringe pumps
with a user-friendly interface and parameter storage capabilities.
"""

from typing import List
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.DataEntry.ProtocolDev.standard_protocol import StandardProtocolAlgorithm


class ProtocolAlgorithm(StandardProtocolAlgorithm):
    """Creates and manages protocols for two syringe pumps with one reactor coil and one mixer."""
    
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
            data_file = "two_syringes_protocol_data.json"
            
        super().__init__(
            protocol, 
            *components, 
            data_file=data_file,
            protocol_name="TwoSyringes1RCoil1Mixer",
            protocol_description="Protocol for two syringes with one reactor coil and one mixer",
            display_title="Two Syringes Protocol Parameters",
            channels_per_pump=1,  # Number of channels per pump
            num_active_pumps=2,   # Number of pumps for active phase
            with_delay=False,     # No delay_time parameter needed
            use_modified_rates=True  # Use different rates for pumps
        )
    
    def get_pump_rates(self, base_rate: float) -> List[float]:
        """
        Calculate pump rates based on the flow network structure.
        
        For a TwoSyringes1RCoil1Mixer setup:
        - Single mixer T1 has 2 equal inputs from vessels 1 and 2
        - Each vessel has its own pump
        - Each pump should contribute equally (1/2 of the final flow rate)
        
        Args:
            base_rate: The base pump rate (final_flow_rate / num_active_pumps)
            
        Returns:
            List of pump rates for each component
        """
        # For this setup, all pumps contribute equally to the mixer (T1)
        # T1 has 2 inputs (both coil_a) from vessel1 and vessel2
        # Each pump should provide 1/2 of the total flow
        
        # The standard_protocol already calculates base_rate as final_flow_rate / num_active_pumps
        # Since all pumps contribute equally, we simply return the base rate for each pump
        return [base_rate] * self.num_active_pumps