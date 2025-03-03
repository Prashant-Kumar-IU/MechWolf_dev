import platform
import subprocess
import glob
import os
from typing import List


class SerialPortViewer:
    """
    SerialPortViewer is a class that provides functionality to list serial ports available on the system.
    Methods:
        __init__():
            Initializes the SerialPortViewer instance.
        run():
            Executes the main functionality of the SerialPortViewer by calling the show_serial_ports method.
        show_serial_ports():
            Detects and lists the serial ports available on the system based on the operating system.
            - On Linux, it lists ports in the /dev/serial/by-id directory.
            - On Windows, it uses PowerShell to get the list of serial ports.
            - On macOS (Darwin), it lists ports matching the /dev/cu.* pattern.
            - For unsupported operating systems, it prints an error message.
    """

    def __init__(self) -> None:
        pass

    def run(self) -> None:
        self.show_serial_ports()

    def show_serial_ports(self) -> None:
        os_type = platform.system()

        if os_type == "Linux":
            if os.path.exists("/dev/serial/by-id"):
                ports: List[str] = os.listdir("/dev/serial/by-id")
                for port in ports:
                    print(port)
            else:
                print("No serial ports found.")
        elif os_type == "Windows":
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-WMIObject Win32_SerialPort | Select-Object -ExpandProperty DeviceID",
                ],
                capture_output=True,
                text=True,
            )
            print(result.stdout.strip())
        elif os_type == "Darwin":  # macOS
            serial_ports: List[str] = glob.glob("/dev/cu.*")
            print(serial_ports)
        else:
            print("Unsupported operating system.")
