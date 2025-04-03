from datetime import timedelta
from typing import List, Dict, Any, Optional
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.DataEntry.ProtocolDev.standard_protocol import StandardProtocolAlgorithm


class ProtocolAlgorithm(StandardProtocolAlgorithm):
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
            
        super().__init__(
            protocol, 
            *components, 
            data_file=data_file,
            protocol_name="ThreeSyringes2RCoil2Mixer",
            protocol_description="Protocol for three syringes with two reactor coils and two mixers",
            display_title="Three Syringes Protocol with 2 Reactor Coils and 2 Mixers",
            channels_per_pump=1,   # Number of channels per pump
            num_active_pumps=3,    # Number of pumps for active phase
            with_delay=True,       # Include delay_time parameter
            use_modified_rates=True  # Use different rates for pumps
        )
    
    def get_pump_rates(self, base_rate: float) -> List[float]:
        """
        Calculate pump rates based on the flow network structure.
        Uses the flow_distribution from the network config if available.
        
        Args:
            base_rate: The base pump rate (final_flow_rate / num_active_pumps)
            
        Returns:
            List of pump rates for each component
        """
        # Try to get network flow distribution from the config
        network_flow = self._get_flow_distribution_from_config()
        
        if network_flow:
            # Use flow distribution from the network configuration
            final_flow_rate = base_rate * self.num_active_pumps
            pump_rates = []
            
            # Get pump rate for each vessel based on its fraction
            for i in range(self.num_active_pumps):
                vessel_key = f"vessel{i+1}"
                fraction = network_flow.get(vessel_key, {}).get("fraction", 1/self.num_active_pumps)
                pump_rates.append(final_flow_rate * fraction)
                
            return pump_rates
            
        # Default calculation if network flow distribution is not available
        # In this specific setup:
        # - Final flow = 4 mL/min
        # - T2 (mixer 2) receives flow from 2 sources: vessel3 and T1
        #   - Vessel3 (pump3) should provide 2 mL/min (half of final flow)
        #   - T1 should provide 2 mL/min (half of final flow)
        # - T1 (mixer 1) receives flow from 2 sources: vessel1 and vessel2
        #   - Each vessel (pump1, pump2) should provide 1 mL/min (half of T1 flow)
        
        # Calculate the actual rates - T2 has 2 inputs, T1 has 2 inputs
        final_flow_rate = base_rate * self.num_active_pumps
        
        # Flow through T2 is divided into 2 (one from vessel3/pump3, one from T1)
        flow_at_each_T2_input = final_flow_rate / 2
        
        # Flow through T1 equals one T2 input, divided between 2 inputs (vessel1/pump1 and vessel2/pump2)
        flow_at_each_T1_input = flow_at_each_T2_input / 2
        
        # Return the specific rates for each pump:
        # Pump1 = 1/2 of T1 flow, Pump2 = 1/2 of T1 flow, Pump3 = 1/2 of final flow
        return [flow_at_each_T1_input, flow_at_each_T1_input, flow_at_each_T2_input]
        
    def _get_flow_distribution_from_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the flow distribution from the loaded configuration.
        
        Returns:
            Dict with flow distribution information or None if not available
        """
        try:
            # Load the configuration data
            config = self._load_config()
            
            if config and "apparatus_config" in config:
                apparatus_config = config["apparatus_config"]
                if "network" in apparatus_config and "flow_distribution" in apparatus_config["network"]:
                    return apparatus_config["network"]["flow_distribution"]
        except Exception:
            # Silently handle any errors in getting flow distribution
            pass
            
        return None
        
    def add_delay_phase(self, current_time: timedelta, delay_time: timedelta, pump_rates: List[float]) -> timedelta:
        """
        Add a delay phase to the protocol.
        
        Args:
            current_time: Current time in the protocol
            delay_time: Duration of the delay
            pump_rates: List of pump rates
            
        Returns:
            Updated current time
        """
        # Skip if delay time is zero
        if delay_time.total_seconds() == 0:
            return current_time
            
        # Add pumps with their respective rates
        for i, component in enumerate(self.components):
            if i < len(pump_rates):
                self.protocol.add(
                    component,
                    start=current_time,
                    duration=delay_time,
                    rate=f"{pump_rates[i]} mL/min",
                )
                
        # Return updated time (delay + switch time)
        return current_time + delay_time + self.switch_time