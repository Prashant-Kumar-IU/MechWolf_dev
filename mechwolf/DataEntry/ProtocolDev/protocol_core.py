"""
Core functionality for protocol algorithms with shared functionality.

This module provides base classes, utilities, and data management for creating MechWolf protocols
with consistent interfaces and parameter persistence.
"""
from datetime import timedelta
from typing import Dict, Tuple, Any, Optional, List
import time
import re
import json

from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent


class ProtocolDataManager:
    """
    Manages protocol data stored in a JSON file.
    Attributes:
        json_file (str): Path to the JSON file containing protocol data.
    Methods:
        load_full_config() -> Optional[Dict[str, Any]]:
            Loads the entire configuration file.
        load_protocol_config() -> Optional[Dict[str, Any]]:
            Loads the existing protocol configuration from the JSON file.
        save_protocol_config(protocol_config: Dict[str, Any]) -> None:
            Saves the protocol configuration while preserving all existing data.
    """

    def __init__(self, json_file: str) -> None:
        self.json_file = json_file

    def load_full_config(self) -> Optional[Dict[str, Any]]:
        """Load the entire configuration file"""
        try:
            with open(self.json_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading full configuration: {str(e)}")
            return None

    def load_protocol_config(self) -> Optional[Dict[str, Any]]:
        """Load existing protocol configuration from JSON file"""
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "protocol_configs" in data:
                    if data["protocol_configs"]:
                        return data["protocol_configs"][-1]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def save_protocol_config(self, protocol_config: Dict[str, Any]) -> None:
        """Save protocol configuration while preserving ALL existing data"""
        try:
            # Read existing data
            try:
                with open(self.json_file, "r") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Silently create new data file without printing messages
                data = {}

            # Create new protocol entry
            new_entry = {
                "name": protocol_config.get("name", ""),
                "description": protocol_config.get("description", ""),
                "pump_entries": protocol_config["pump_entries"],
            }

            # Ensure protocol_configs exists
            if "protocol_configs" not in data:
                data["protocol_configs"] = []

            # Update or append protocol
            found = False
            for i, existing_protocol in enumerate(data["protocol_configs"]):
                if existing_protocol.get("name") == new_entry["name"]:
                    data["protocol_configs"][i] = new_entry
                    found = True
                    break

            if not found:
                data["protocol_configs"].append(new_entry)

            # Write back to file with proper formatting
            with open(self.json_file, "w") as f:
                json.dump(data, f, indent=4)
                
            # Single simple confirmation instead of multiple messages
            print(f"Protocol configuration saved successfully.")
            
        except Exception as e:
            print(f"Error saving protocol: {str(e)}")
            raise


class ProtocolValidator:
    """Provides validation and default value handling for protocols."""
    
    @staticmethod
    def get_default_values(prev_values: Dict[str, Any], with_delay: bool = False) -> Dict[str, Any]:
        """
        Generate default values for protocol parameters.
        
        Args:
            prev_values: Previously saved values if available
            with_delay: Whether to include delay_time parameter
            
        Returns:
            Dictionary containing default values for UI widgets
        """
        defaults = {
            "flow_rate": prev_values.get("flow_rate", 1.0),
            "solvent_volume": prev_values.get("solvent_volume", 1.0),
            "rinse_volume": prev_values.get("rinse_volume", 1.0),
            "switch_time": prev_values.get("switch_time", 1.0),
            "timestamp": prev_values.get("timestamp", None)
        }
        
        # Add delay_time if requested
        if with_delay:
            defaults["delay_time"] = prev_values.get("delay_time", 1.0)
            
        return defaults

    @staticmethod
    def validate_inputs(values: Dict[str, float], with_delay: bool = False) -> Optional[str]:
        """
        Validate common protocol parameters.
        
        Args:
            values: Dictionary of parameter values
            with_delay: Whether to validate delay_time parameter
            
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
        
        # Validate delay_time if it exists
        if with_delay and "delay_time" in values and values["delay_time"] < 0:
            return "Delay time cannot be negative"
            
        return None


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

    def _validate_inputs(self, values: Dict[str, float]) -> Optional[str]:
        """
        Validate input parameters, to be implemented by subclasses.
        
        Args:
            values: Dictionary of parameter values
            
        Returns:
            Error message string if validation fails, None if valid
        """
        raise NotImplementedError("Subclasses must implement this method")

    def _build_protocol(self, values: Dict[str, float]) -> None:
        """
        Build the protocol with the specified parameters, to be implemented by subclasses.
        
        Args:
            values: Dictionary of parameter values
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
        # Always use absolute value of flow rate for time calculations
        abs_flow_rate = abs(flow_rate)
        active_time = timedelta(seconds=(volume / abs_flow_rate * 60))
        rinse_time = timedelta(seconds=(rinse_volume / abs_flow_rate * 60))
        return active_time, rinse_time


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
        from IPython.display import display, HTML
        
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
                
                # Display changed from "Processing Protocol with:" to "Summary of protocols:"
                display(HTML(f'<h3 style="color:green">Summary of protocols:</h3>'))
                
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
                
                # Build the protocol to get pump rates
                self_obj._build_protocol(values)
                
                # Add individual pump rates to the summary
                # First get the pump rates from the protocol algorithm
                pump_rate = values["flow_rate"] / self_obj.num_active_pumps
                pump_rates = self_obj.get_pump_rates(pump_rate)
                
                # Show individual pump rates
                html_list.append('<li>Individual pump rates:</li>')
                html_list.append('<ul>')
                for i, rate in enumerate(pump_rates[:self_obj.num_active_pumps]):
                    pump_direction = "infusing" if rate > 0 else "withdrawing"
                    html_list.append(f'<li>Pump {i+1}: {rate} mL/min ({pump_direction})</li>')
                html_list.append('</ul>')
                
                # Display the parameters
                display(HTML(f'<ul>{"".join(html_list)}</ul>'))
                
                display(HTML(f'<p style="color:green;font-weight:bold">Protocol successfully created!</p>'))
                
            except Exception as e:
                # Show the form again if there's an error
                form.layout.display = 'block'
                display(HTML(f'<p style="color:red;font-weight:bold">Error: {str(e)}</p>'))
