"""
Base module for protocol algorithms with shared functionality.

This module provides base classes and utilities for creating MechWolf protocols
with consistent interfaces and parameter persistence.
"""
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
import time
import re

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from mechwolf.DataEntry.ProtocolDev.ProtocolDataManager import ProtocolDataManager


class BaseProtocolAlgorithm:
    """Base class for protocol algorithms with common functionality."""
    
    def __init__(self, protocol: Protocol, *components: ActiveComponent, data_file: str) -> None:
        """
        Initialize the protocol algorithm with a protocol, components, and data file path.
        
        Args:
            protocol: The protocol to be populated
            *components: Components to be used in the protocol
            data_file: Path to the data file for saving/loading protocol parameters
        """
        self.protocol = protocol
        self.components = components
        self.data_manager = ProtocolDataManager(data_file)
        
    def _get_default_values(self) -> Dict[str, Any]:
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
        
        return prev_values

    def _save_protocol_config(self, name: str, description: str, values: Dict[str, Any]) -> None:
        """
        Save protocol configuration to the data file.
        
        Args:
            name: Protocol name
            description: Protocol description
            values: Dictionary of parameter values
        """
        # Add timestamp to values
        values["timestamp"] = time.time()
        
        protocol_config = {
            "name": name,
            "description": description,
            "pump_entries": [values]
        }
        
        # Save the protocol config
        self.data_manager.save_protocol_config(protocol_config)

    def create_protocol(self) -> Protocol:
        """
        Create a protocol based on user input.
        To be implemented by subclasses.
        
        Returns:
            Protocol: The created protocol with the specified parameters.
        """
        raise NotImplementedError("Subclasses must implement this method")


class ProtocolUtils:
    """Utility methods for protocol parameter parsing and validation."""
    
    @staticmethod
    def parse_flow_rate(flow_rate: str) -> float:
        """
        Parse a flow rate string and return the flow rate as a float.
        
        Args:
            flow_rate: The flow rate string to parse (e.g., "5 mL/min")
            
        Returns:
            The parsed flow rate as a float
            
        Raises:
            ValueError: If the flow rate format is invalid
        """
        match = re.match(r"(-?\d+(\.\d+)?)\s*(mL/min|ML/Min|ml/min|ML/min|ML/MIN)?", flow_rate)
        if match:
            return float(match.group(1))
        else:
            raise ValueError("Invalid flow rate format. Please enter a number followed by 'mL/min'.")

    @staticmethod
    def parse_volume(volume: str) -> float:
        """
        Parse a volume string and return the volume as a float.
        
        Args:
            volume: The volume string to parse (e.g., "10 mL")
            
        Returns:
            The parsed volume as a float
            
        Raises:
            ValueError: If the volume format is invalid
        """
        match = re.match(r"(\d+(\.\d+)?)\s*(mL|ML|ml|Ml)?", volume)
        if match:
            return float(match.group(1))
        else:
            raise ValueError("Invalid volume format. Please enter a number followed by 'mL'.")

    @staticmethod
    def parse_time(time_str: str) -> float:
        """
        Parse a time string and return the time as a float.
        
        Args:
            time_str: The time string to parse (e.g., "30 seconds")
            
        Returns:
            The parsed time as a float
            
        Raises:
            ValueError: If the time format is invalid
        """
        match = re.match(r"(\d+(\.\d+)?)\s*(seconds|sec|s|S|SEC|SECONDS|SEc|Sec)?", time_str)
        if match:
            return float(match.group(1))
        else:
            raise ValueError("Invalid time format. Please enter a number followed by 'seconds'.")

    @staticmethod
    def calculate_times(flow_rate: float, volume: float, rinse_volume: float) -> Tuple[timedelta, timedelta]:
        """
        Calculate active and rinse times based on flow rate and volumes.
        
        Args:
            flow_rate: Flow rate in mL/min (absolute value used for calculations)
            volume: Solvent volume in mL
            rinse_volume: Rinse volume in mL
            
        Returns:
            Tuple of (active_time, rinse_time) as timedelta objects
        """
        abs_flow_rate = abs(flow_rate)
        active_time = timedelta(seconds=(volume / abs_flow_rate * 60))
        rinse_time = timedelta(seconds=(rinse_volume / abs_flow_rate * 60))
        return active_time, rinse_time
