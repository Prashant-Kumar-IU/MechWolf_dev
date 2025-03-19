import mechwolf as mw
import time
from mechwolf.components.contrib.freestep_3DSyringePump_controller import FreeStepController

class FreeStepPump(mw.Pump):
    """
    A MechWolf component for controlling FreeStep 3D syringe pumps.

    Arguments:
    - `serial_port`: Serial port through which the device is connected (e.g., "COM3" or "/dev/ttyUSB0").
    - `mcu_id`: The unique ID of the MCU profile.
    - `motor_id`: The unique ID of the motor profile.
    - `syringe_volume`: The volume of the syringe (in mL).
    - `syringe_diameter`: The diameter of the syringe (in mm).
    - `name` (optional): The name of the syringe pump instance. Defaults to `None`.
    """

    metadata = {
        "author": [
            {
                "first_name": "Prashant",
                "last_name": "Kumar",
                "email": "pprashan@iu.edu",
                "institution": "Indiana University Bloomington, Departemnt of Chemistry",
                "github_username": "Prashant-Kumar-IU",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, serial_port, mcu_id, motor_id, syringe_volume, syringe_diameter, name=None):
        super().__init__(name=name)
        self.serial_port = serial_port
        self.mcu_id = mcu_id
        self.motor_id = motor_id
        self.syringe_volume = mw._ureg.parse_expression(syringe_volume)
        self.syringe_diameter = mw._ureg.parse_expression(syringe_diameter)
        self._controller = None
        self._mcu_profile = None
        self._motor_profile = None
        
    def __enter__(self):
        # Initialize the FreeStep controller - this is key to making it work like the calibration tool
        self._controller = FreeStepController()
        
        print(f"Connecting {self.name} to {self.serial_port}...")
        # Connect to the port
        if not self._controller.connect_port(self.serial_port):
            raise RuntimeError(f"Failed to connect to {self.serial_port}")
            
        # Get MCU and motor profiles
        mcus = self._controller.get_mcus()
        motors = self._controller.get_motors()
        
        # Find the specified MCU and motor profiles
        self._mcu_profile = next((mcu for mcu in mcus if mcu.get("uniqueID") == self.mcu_id), None)
        self._motor_profile = next((motor for motor in motors if motor.get("uniqueID") == self.motor_id), None)
        
        if not self._mcu_profile:
            raise RuntimeError(f"MCU with ID {self.mcu_id} not found")
            
        if not self._motor_profile:
            raise RuntimeError(f"Motor with ID {self.motor_id} not found")
            
        if not self._motor_profile.get("calibrated", False):
            raise RuntimeError(f"Motor with ID {self.motor_id} is not calibrated")
            
        # Update syringe info if needed
        if "syringeInfo" not in self._motor_profile:
            self._motor_profile["syringeInfo"] = {
                "brand": "User Defined",
                "model": "User Defined",
                "volumeML": self.syringe_volume.to(mw._ureg.ml).magnitude,
                "innerDiameterMM": self.syringe_diameter.to(mw._ureg.mm).magnitude,
                "calibrationDate": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self._controller.profile_manager.update_motor(self._motor_profile)
        
        # Stop the pump initially to make sure it's in a known state
        self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
        
        # Initialize last_rate to track rate changes
        self._last_rate = 0
        
        print(f"FreeStepPump {self.name} initialized on {self.serial_port}")
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        if self._controller:
            try:
                # Stop the pump before closing
                if self._mcu_profile and self._motor_profile:
                    self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
                
                # Disconnect and clean up
                self._controller.disconnect_port(self.serial_port)
                self._controller.cleanup()
                print(f"FreeStepPump {self.name} stopped and disconnected")
            except Exception as e:
                print(f"Error during cleanup: {e}")

    async def _update(self):
        """Update pump flow rate - called by MechWolf"""
        if not self._controller or not self._mcu_profile or not self._motor_profile:
            raise RuntimeError("Pump not properly initialized")
            
        # Convert flow rate to mL/min
        rate_mlmin = self.rate.to(mw._ureg.ml / mw._ureg.min).magnitude
        
        # Only send commands if the rate has changed
        if rate_mlmin != self._last_rate:
            print(f"Rate change detected for {self.name}: {self._last_rate} -> {rate_mlmin} mL/min")
            self._last_rate = rate_mlmin
            
            # Determine operation direction - negative rate means backward/aspiration
            direction = "backward" if rate_mlmin < 0 else "forward"
            # Use absolute value for calculations
            abs_rate = abs(rate_mlmin)
            
            if abs_rate <= 0.000001:  # Near-zero rate threshold for stopping
                # Stop the pump
                print(f"Stopping pump {self.name}")
                self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
                print(f"Pump {self.name} stopped")
            else:
                # Run at the specified rate and direction
                print(f"Setting pump {self.name} to {abs_rate} mL/min ({direction})")
                
                # Force pump to run by stopping first
                self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
                time.sleep(0.5)  # Small delay to ensure stop takes effect
                
                # Now run with the new rate and direction
                success = self._controller.run_basic_command(
                    self.serial_port, 
                    self._motor_profile, 
                    self._mcu_profile,
                    abs_rate,  # Always use positive flow rate value
                    direction  # Direction determined by sign of original rate
                )
                
                if success:
                    print(f"Pump {self.name} now running at {abs_rate} mL/min ({direction})")
                else:
                    print(f"Failed to set flow rate for {self.name}")
