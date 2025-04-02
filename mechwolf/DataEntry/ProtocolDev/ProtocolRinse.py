"""
Module providing standardized rinse functionality for MechWolf protocols.

This module contains reusable functions for performing rinse steps in various protocols,
allowing for consistent implementation across different protocol types.
"""
from datetime import timedelta
from typing import List, Union, Optional, Tuple, Dict, Any

from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.core.protocol import Protocol


class ProtocolRinse:
    """
    Provides standardized rinse operations for MechWolf protocols.
    """
    
    @staticmethod
    def add_rinse_step(
        protocol: Protocol,
        components: List[ActiveComponent],
        current_time: timedelta,
        rinse_time: timedelta,
        pump_rate: float,
        is_dual_channel: Optional[bool] = None
    ) -> timedelta:
        """
        Add a rinse step to the protocol.
        
        Args:
            protocol: The protocol to add the rinse step to
            components: List of components (pumps) to use for the rinse
            current_time: The current time in the protocol
            rinse_time: The duration of the rinse step
            pump_rate: The flow rate for the pumps in mL/min
            is_dual_channel: Override to specify whether components are dual channel pumps.
                             If None, will be auto-detected.
            
        Returns:
            The updated current time after the rinse step
        """
        # Auto-detect if components are dual-channel pumps if not specified
        if is_dual_channel is None:
            is_dual_channel = isinstance(components[0], HarvardSyringePump) and len(components) <= 2
        
        if is_dual_channel:
            # Dual-channel pumps
            protocol.add(
                components[0],
                start=current_time,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )
            
            # Add second channel if available
            if len(components) > 1:
                protocol.add(
                    components[1],
                    start=current_time,
                    duration=rinse_time,
                    rate=f"{pump_rate} mL/min",
                )
        else:
            # Single-channel pumps
            for component in components:
                protocol.add(
                    component,
                    start=current_time,
                    duration=rinse_time,
                    rate=f"{pump_rate} mL/min",
                )
        
        return current_time + rinse_time
    
    @staticmethod
    def add_variable_rate_rinse_step(
        protocol: Protocol,
        components: List[ActiveComponent],
        current_time: timedelta,
        rinse_time: timedelta,
        pump_rates: List[float]
    ) -> timedelta:
        """
        Add a rinse step to the protocol with different rates for each component.
        
        Args:
            protocol: The protocol to add the rinse step to
            components: List of components (pumps) to use for the rinse
            current_time: The current time in the protocol
            rinse_time: The duration of the rinse step
            pump_rates: List of flow rates (one for each component) in mL/min
            
        Returns:
            The updated current time after the rinse step
        """
        if len(components) != len(pump_rates):
            raise ValueError(
                f"Number of components ({len(components)}) must match "
                f"number of pump rates ({len(pump_rates)})"
            )
            
        for component, rate in zip(components, pump_rates):
            protocol.add(
                component,
                start=current_time,
                duration=rinse_time,
                rate=f"{rate} mL/min",
            )
        
        return current_time + rinse_time
    
    @staticmethod
    def calculate_rinse_time(
        rinse_volume: float, 
        flow_rate: float, 
        num_channels: int = 1
    ) -> timedelta:
        """
        Calculate the time required for a rinse operation.
        
        Args:
            rinse_volume: The volume of rinse solution in mL
            flow_rate: The absolute flow rate in mL/min
            num_channels: Number of channels to divide the flow rate by
            
        Returns:
            The calculated rinse time as a timedelta
        """
        # Always use absolute value for time calculation
        abs_flow_rate = abs(flow_rate)
        # Adjust for multiple channels if needed
        adjusted_flow_rate = abs_flow_rate / num_channels if num_channels > 0 else abs_flow_rate
        
        # Calculate time in seconds
        rinse_seconds = (rinse_volume / adjusted_flow_rate * 60)
        return timedelta(seconds=rinse_seconds)
