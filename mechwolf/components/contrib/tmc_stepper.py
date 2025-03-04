from ..stdlib.pump import Pump  # Change to inherit from Pump instead of ActiveComponent
import json
import serial
import time
from loguru import logger
from mechwolf import _ureg

class TMCPump(Pump):  # Change to inherit from Pump
    """
    A peristaltic pump using NEMA 17 stepper motor with TMC2209 driver.
    
    Arguments:
    - `serial_port`: Serial port through which device is connected (e.g. "COM3")
    - `step_pin`: Arduino pin connected to TMC2209 STEP pin
    - `dir_pin`: Arduino pin connected to TMC2209 DIR pin
    - `current`: Motor current in mA (default 800mA)
    - `microsteps`: Microstepping setting (default 16)
    - `steps_per_ml`: Calibration factor (steps per mL, default 200)
    - `name`: Optional name for the component
    """

    metadata = {
        "author": [
            {
                "first_name": "Your",
                "last_name": "Name",
                "email": "your.email@domain.com",
                "institution": "Your Institution",
                "github_username": "yourusername",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, serial_port, step_pin=2, dir_pin=3, current=800, microsteps=16, steps_per_ml=200, name=None):
        super().__init__(name=name)
        self.serial_port = serial_port
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.current = current
        self.microsteps = microsteps
        self.steps_per_ml = steps_per_ml
        self.rate = 0 * _ureg.mL/(_ureg.minute)  # Initialize with proper units
        self._ser = None

    def __enter__(self):
        logger.debug(f"Connecting to stepper motor on {self.serial_port}")
        self._ser = serial.Serial(self.serial_port, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino reset
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._ser:
            self.stop()
            self._ser.close()

    def _send_command(self, command):
        """Send a JSON command to the Arduino."""
        if not self._ser:
            raise RuntimeError("Serial connection not established")
        json_command = json.dumps(command)
        logger.trace(f"Sending command: {json_command}")
        self._ser.write(f"{json_command}\n".encode())

    def start_continuous(self, frequency, direction="forward"):
        """
        Start motor at specified frequency.
        
        Arguments:
        - `frequency`: Speed in Hz
        - `direction`: "forward" or "backward"
        """
        command = {
            "type": "basic",
            "stepPin": self.step_pin,
            "dirPin": self.dir_pin,
            "freq": frequency,
            "direction": direction,
            "current": self.current,
            "microsteps": self.microsteps
        }
        self._send_command(command)
        self.frequency = frequency

    def start_timed(self, frequency, duration, time_unit="s", direction="forward"):
        """
        Run motor for specified duration.
        
        Arguments:
        - `frequency`: Speed in Hz
        - `duration`: Run time
        - `time_unit`: Time unit ("ms", "s", "m", "hr")
        - `direction`: "forward" or "backward"
        """
        command = {
            "type": "timed",
            "stepPin": self.step_pin,
            "dirPin": self.dir_pin,
            "freq": frequency,
            "timeValue": duration,
            "timeUnit": time_unit,
            "direction": direction,
            "current": self.current,
            "microsteps": self.microsteps
        }
        self._send_command(command)
        self.frequency = frequency

    def stop(self):
        """Stop the motor."""
        command = {
            "type": "stop",
            "stepPin": self.step_pin,
            "dirPin": self.dir_pin
        }
        self._send_command(command)
        self.frequency = 0

    def _hz_from_flow_rate(self, flow_rate):
        """Convert flow rate to step frequency"""
        ml_per_min = float(flow_rate.to(_ureg.mL/_ureg.minute).magnitude)
        return (ml_per_min * self.steps_per_ml) / 60  # Convert to Hz

    async def _update(self):
        """Update method for Mechwolf protocols."""
        try:
            # Get flow rate in Hz
            hz = self._hz_from_flow_rate(self.rate)
            
            if hz == 0:
                command = {
                    "type": "stop",
                    "stepPin": self.step_pin,
                    "dirPin": self.dir_pin
                }
            else:
                # Determine direction based on flow rate sign
                direction = "forward" if self.rate.magnitude >= 0 else "backward"
                hz = abs(hz)  # Use absolute value for frequency
                
                command = {
                    "type": "basic",
                    "stepPin": self.step_pin,
                    "dirPin": self.dir_pin,
                    "freq": hz,
                    "direction": direction,
                    "current": self.current,
                    "microsteps": self.microsteps
                }
            
            self._send_command(command)
            
        except Exception as e:
            logger.error(f"Error updating TMC pump: {str(e)}")
            raise
