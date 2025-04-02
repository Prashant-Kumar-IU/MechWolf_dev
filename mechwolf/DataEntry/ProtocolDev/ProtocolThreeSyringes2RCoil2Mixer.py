from datetime import timedelta
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import re
from mechwolf.DataEntry.ProtocolDev.ProtocolGUICreator import ProtocolInputGUI, validate_inputs


class ProtocolAlgorithm:
    """
    Class to create a protocol for controlling syringe pumps.
    Args:
        protocol (Protocol): The protocol object to which the steps will be added.
        *components (ActiveComponent): Variable length argument list of active components (e.g., syringe pumps).
    Methods:
        create_protocol() -> Protocol:
            Creates the protocol based on user inputs for flow rate, solvent volume, rinse volume, switch time, and delay_time time.
            Returns the protocol object with the added steps.
    """

    def __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        self.protocol = protocol
        self.components = components

    def create_protocol(self) -> Protocol:
        # Create GUI to collect inputs
        input_gui = ProtocolInputGUI()
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
        flow_rate, solvent_volume, rinse_volume, switch_time, delay_time = validate_inputs(input_dict)
        
        pump_rate = flow_rate / 4  # for three syringes in this setup

        # Use absolute value for calculations when determining time
        # Direction is handled by the pump class based on sign of flow rate
        abs_pump_rate = abs(pump_rate)
        
        # Check for zero pump_rate to prevent division by zero
        if abs_pump_rate == 0:
            print("Error: Flow rate cannot be zero. Please submit the form with a non-zero flow rate.")
            return self.protocol

        active_time = timedelta(seconds=(solvent_volume / abs_pump_rate * 60))
        rinse_time = timedelta(seconds=(rinse_volume / abs_pump_rate * 60))

        print("active_time =", active_time)
        print("rinse_time =", rinse_time)
        print("delay_time =", timedelta(seconds=delay_time))

        # current initialized to 0. That is, time, t = 0 s
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

        current += active_time + timedelta(seconds=switch_time)

        if delay_time != 0:
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
                current += timedelta(seconds=delay_time) + timedelta(seconds=switch_time)
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
                current += timedelta(seconds=delay_time) + timedelta(seconds=switch_time)

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
        return self.protocol
