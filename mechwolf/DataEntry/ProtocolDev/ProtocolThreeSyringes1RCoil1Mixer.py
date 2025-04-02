from datetime import timedelta

"""
This module defines a `ProtocolAlgorithm` class that creates a protocol for controlling syringe pumps.
Classes:
    ProtocolAlgorithm: A class to create and manage a protocol for syringe pumps.
Methods:
    __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        Initializes the ProtocolAlgorithm with a given protocol and components.
    create_protocol(self) -> Protocol:
        Creates a protocol based on user inputs for flow rate, solvent volume, rinse volume, and switch time.
        Returns:
            Protocol: The created protocol with the specified parameters.
"""
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import re
from mechwolf.DataEntry.ProtocolDev.ProtocolGUICreator import ProtocolInputGUINoDelay, validate_inputs


class ProtocolAlgorithm:
    def __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        self.protocol = protocol
        self.components = components

    def create_protocol(self) -> Protocol:
        # Create GUI to collect inputs (without delay time parameter)
        input_gui = ProtocolInputGUINoDelay()
        input_dict = input_gui.collect_inputs()
        
        # Wait for user input (in Jupyter)
        # This is where the GUI will be displayed and the user will input data
        
        # Check if input_dict is empty (user hasn't submitted the form yet)
        if not input_dict:
            print("Please complete the form and click Submit to create the protocol.")
            # Add a placeholder procedure to make visualization work
            if len(self.components) > 0:
                self.protocol.add(
                    self.components[0],
                    start=timedelta(seconds=0),
                    duration=timedelta(seconds=1),
                    rate="0 mL/min"
                )
            return self.protocol
        
        # Once the user submits the form, validate and extract the inputs
        flow_rate, solvent_volume, rinse_volume, switch_time, _ = validate_inputs(input_dict)
        
        current = timedelta(seconds=0)

        # Three syringes are being used so dividing by 3:
        pump_rate = flow_rate / 3
        
        # Use absolute value for calculations when determining time
        # Direction is handled by the pump class based on sign of flow rate
        abs_pump_rate = abs(pump_rate)
        
        # Check for zero pump_rate to prevent division by zero
        if abs_pump_rate == 0:
            print("Error: Flow rate cannot be zero. Please submit the form with a non-zero flow rate.")
            return self.protocol

        rinse_time = timedelta(seconds=(rinse_volume / abs_pump_rate * 60))
        active_time = timedelta(seconds=(solvent_volume / abs_pump_rate * 60))

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

        current += active_time + timedelta(seconds=switch_time)

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

        current += active_time + rinse_time

        print(f"TOTAL TIME: {current}")
        return self.protocol
