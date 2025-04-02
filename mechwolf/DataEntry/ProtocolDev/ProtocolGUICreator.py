from datetime import timedelta
import re
import ipywidgets as widgets
from IPython.display import display


class ProtocolInputGUI:
    """
    A class to create a GUI for collecting protocol parameters using ipywidgets.
    
    This class provides a graphical interface for entering parameters needed for protocol creation,
    such as flow rate, solvent volume, rinse volume, switch time, and delay time.
    
    Methods:
        collect_inputs() -> dict:
            Displays a GUI for parameter input and returns the collected values.
    """
    
    def __init__(self):
        self.output = {}
        
        # Create widgets for input
        self.flow_rate_widget = widgets.FloatText(
            description='Flow Rate (mL/min):',
            value=1.0,
            step=0.1,
            style={'description_width': 'initial'}
        )
        
        self.solvent_volume_widget = widgets.FloatText(
            description='Solvent Volume (mL):',
            value=1.0,
            step=0.1,
            style={'description_width': 'initial'}
        )
        
        self.rinse_volume_widget = widgets.FloatText(
            description='Rinse Volume (mL):',
            value=1.0,
            step=0.1,
            style={'description_width': 'initial'}
        )
        
        self.switch_time_widget = widgets.FloatText(
            description='Switch Time (s):',
            value=30.0,
            step=1.0,
            style={'description_width': 'initial'}
        )
        
        self.delay_time_widget = widgets.FloatText(
            description='Delay Time (s):',
            value=0.0,
            step=1.0,
            style={'description_width': 'initial'}
        )
        
        self.submit_button = widgets.Button(
            description='Submit',
            button_style='success',
            tooltip='Submit the protocol parameters'
        )
        
        self.submit_button.on_click(self._on_submit_clicked)
        
        self.status_output = widgets.Output()
        
    def _on_submit_clicked(self, b):
        """Handle the submit button click event."""
        with self.status_output:
            self.status_output.clear_output()
            
            # Validate inputs
            try:
                flow_rate = self.flow_rate_widget.value
                solvent_volume = self.solvent_volume_widget.value
                rinse_volume = self.rinse_volume_widget.value
                switch_time = self.switch_time_widget.value
                delay_time = self.delay_time_widget.value
                
                if flow_rate == 0:
                    print("Error: Flow rate cannot be zero")
                    return
                if flow_rate < 0:
                    display(widgets.HTML(
                        "<div style='background-color:#fff3cd; padding:10px; border-left:5px solid #ffc107; margin:10px 0;'>"
                        "<span style='color:red; font-weight:bold; font-size:14px;'>⚠️ WARNING: </span>"
                        "<span style='font-weight:bold;'>Negative flow rate detected!</span> "
                        "This is only supported by certain pumps (e.g., freestep_pump) and will reverse the flow direction."
                        "</div>"
                    ))
                if solvent_volume <= 0:
                    print("Error: Solvent volume must be positive")
                    return
                if rinse_volume < 0:
                    print("Error: Rinse volume cannot be negative")
                    return
                if switch_time < 0:
                    print("Error: Switch time cannot be negative")
                    return
                if delay_time < 0:
                    print("Error: Delay time cannot be negative")
                    return
                
                # Store values in output dictionary
                self.output = {
                    'flow_rate': flow_rate,
                    'solvent_volume': solvent_volume,
                    'rinse_volume': rinse_volume,
                    'switch_time': switch_time,
                    'delay_time': delay_time,
                }
                
                print("Parameters submitted successfully!")
                
            except Exception as e:
                print(f"Error: {str(e)}")
                
    def collect_inputs(self):
        """
        Display the GUI for parameter input and return the collected values.
        
        Returns:
            dict: A dictionary containing the protocol parameters:
                - flow_rate (float): The flow rate in mL/min
                - solvent_volume (float): The solvent volume in mL
                - rinse_volume (float): The rinse solvent volume in mL
                - switch_time (float): The switch time in seconds
                - delay_time (float): The delay time in seconds
        """
        # Clear any previous outputs
        self.output = {}
        
        # Create a container for the form
        form = widgets.VBox([
            widgets.HTML("<h3>Protocol Parameters</h3>"),
            self.flow_rate_widget,
            self.solvent_volume_widget,
            self.rinse_volume_widget,
            self.switch_time_widget,
            self.delay_time_widget,
            self.submit_button,
            self.status_output
        ])
        
        display(form)
        
        # The function will return immediately, but the user can fill out the form
        # and click submit. The output dictionary will be populated when they do.
        return self.output


class ProtocolInputGUINoDelay:
    """
    A class to create a GUI for collecting protocol parameters using ipywidgets,
    without the delay time parameter. Used for 1RCoil protocols.
    
    This class provides a graphical interface for entering parameters needed for protocol creation,
    such as flow rate, solvent volume, rinse volume, and switch time.
    
    Methods:
        collect_inputs() -> dict:
            Displays a GUI for parameter input and returns the collected values.
    """
    
    def __init__(self):
        self.output = {}
        
        # Create widgets for input
        self.flow_rate_widget = widgets.FloatText(
            description='Flow Rate (mL/min):',
            value=1.0,
            step=0.1,
            style={'description_width': 'initial'}
        )
        
        self.solvent_volume_widget = widgets.FloatText(
            description='Solvent Volume (mL):',
            value=1.0,
            step=0.1,
            style={'description_width': 'initial'}
        )
        
        self.rinse_volume_widget = widgets.FloatText(
            description='Rinse Volume (mL):',
            value=1.0,
            step=0.1,
            style={'description_width': 'initial'}
        )
        
        self.switch_time_widget = widgets.FloatText(
            description='Switch Time (s):',
            value=30.0,
            step=1.0,
            style={'description_width': 'initial'}
        )
        
        self.submit_button = widgets.Button(
            description='Submit',
            button_style='success',
            tooltip='Submit the protocol parameters'
        )
        
        self.submit_button.on_click(self._on_submit_clicked)
        
        self.status_output = widgets.Output()
        
    def _on_submit_clicked(self, b):
        """Handle the submit button click event."""
        with self.status_output:
            self.status_output.clear_output()
            
            # Validate inputs
            try:
                flow_rate = self.flow_rate_widget.value
                solvent_volume = self.solvent_volume_widget.value
                rinse_volume = self.rinse_volume_widget.value
                switch_time = self.switch_time_widget.value
                
                if flow_rate == 0:
                    print("Error: Flow rate cannot be zero")
                    return
                if flow_rate < 0:
                    display(widgets.HTML(
                        "<div style='background-color:#fff3cd; padding:10px; border-left:5px solid #ffc107; margin:10px 0;'>"
                        "<span style='color:red; font-weight:bold; font-size:14px;'>⚠️ WARNING: </span>"
                        "<span style='font-weight:bold;'>Negative flow rate detected!</span> "
                        "This is only supported by certain pumps (e.g., the 3D PRINTED SYRINGE PUMPS) and will reverse the flow direction."
                        "</div>"
                    ))
                if solvent_volume <= 0:
                    print("Error: Solvent volume must be positive")
                    return
                if rinse_volume < 0:
                    print("Error: Rinse volume cannot be negative")
                    return
                if switch_time < 0:
                    print("Error: Switch time cannot be negative")
                    return
                
                # Store values in output dictionary
                self.output = {
                    'flow_rate': flow_rate,
                    'solvent_volume': solvent_volume,
                    'rinse_volume': rinse_volume,
                    'switch_time': switch_time,
                }
                
                print("Parameters submitted successfully!")
                
            except Exception as e:
                print(f"Error: {str(e)}")
                
    def collect_inputs(self):
        """
        Display the GUI for parameter input and return the collected values.
        
        Returns:
            dict: A dictionary containing the protocol parameters:
                - flow_rate (float): The flow rate in mL/min
                - solvent_volume (float): The solvent volume in mL
                - rinse_volume (float): The rinse solvent volume in mL
                - switch_time (float): The switch time in seconds
        """
        # Clear any previous outputs
        self.output = {}
        
        # Create a container for the form
        form = widgets.VBox([
            widgets.HTML("<h3>Protocol Parameters</h3>"),
            self.flow_rate_widget,
            self.solvent_volume_widget,
            self.rinse_volume_widget,
            self.switch_time_widget,
            self.submit_button,
            self.status_output
        ])
        
        display(form)
        
        # The function will return immediately, but the user can fill out the form
        # and click submit. The output dictionary will be populated when they do.
        return self.output


def validate_inputs(input_dict):
    """
    Validate the input parameters collected from the GUI.
    
    Args:
        input_dict (dict): Dictionary containing the input parameters
        
    Returns:
        tuple: A tuple containing validated parameters
            (flow_rate, solvent_volume, rinse_volume, switch_time, delay_time=0)
    """
    flow_rate = input_dict.get('flow_rate', 0)
    solvent_volume = input_dict.get('solvent_volume', 0)
    rinse_volume = input_dict.get('rinse_volume', 0)
    switch_time = input_dict.get('switch_time', 0)
    delay_time = input_dict.get('delay_time', 0)  # Default to 0 if not provided
    
    return flow_rate, solvent_volume, rinse_volume, switch_time, delay_time


# Legacy parsing functions - kept for backwards compatibility
def parse_flow_rate(flow_rate: str) -> float:
    """Parse a flow rate string and return the flow rate as a float."""
    match = re.match(
        r"(-?\d+(\.\d+)?)\s*(mL/min|ML/Min|ml/min|ML/min|ML/MIN)?", flow_rate
    )
    if match:
        return float(match.group(1))
    else:
        raise ValueError(
            "Invalid flow rate format. Please enter a number followed by 'mL/min'."
        )

def parse_volume(volume: str) -> float:
    """Parse a volume string and return the volume as a float."""
    match = re.match(r"(\d+(\.\d+)?)\s*(mL|ML|ml|Ml)?", volume)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(
            "Invalid volume format. Please enter a number followed by 'mL'."
        )

def parse_time(time: str) -> float:
    """Parse a time string and return the time as a float."""
    match = re.match(
        r"(\d+(\.\d+)?)\s*(seconds|sec|s|S|SEC|SECONDS|SEc|Sec)?", time
    )
    if match:
        return float(match.group(1))
    else:
        raise ValueError(
            "Invalid time format. Please enter a number followed by 'seconds'."
        )
