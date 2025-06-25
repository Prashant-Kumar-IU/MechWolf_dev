import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import time
import threading

class PumpController:
    def __init__(self, root):
        self.root = root
        self.root.title("💧 Precision Pump Controller")
        self.ser = None
        self.stop_flag = False

        self.root.configure(bg="#f2f2f7")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#f2f2f7", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", padding=5)
        style.configure("TFrame", background="#f2f2f7")

        self.main_frame = ttk.Frame(root, padding="20 10 20 10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.main_frame, text="Pump Controller", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Entry fields
        self.port_entry = self.create_labeled_entry("Port (e.g., COM5):", 1)
        self.rate_entry = self.create_labeled_entry("Rate (e.g., mh,uh,mm,um:", 2)
        self.unit_entry = self.create_labeled_entry("Unit (e.g., um):", 3)
        self.diameter_entry = self.create_labeled_entry("Diameter (e.g., mm):", 4)
        self.volume_entry = self.create_labeled_entry("Volume: ml/ul", 5)
        self.duration_entry = self.create_labeled_entry("Duration (s):", 6)
        self.Direction_entry = self.create_labeled_entry("infusion or Defusion (DIR INF or DIR WDR):", 7)

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)

        self.run_button = ttk.Button(button_frame, text="▶ Run Pump", command=self.run_pump_thread)
        self.run_button.grid(row=8, column=0, padx=1)

        self.stop_button = ttk.Button(button_frame, text="⛔ Stop Pump", command=self.stop_pump)
        self.stop_button.grid(row=8, column=1, padx=1)

        self.file_button = ttk.Button(button_frame, text="📂 Run Command File", command=self.run_file_thread)
        self.file_button.grid(row=8, column=2, padx=1)

        # Output area
        self.output_text = tk.StringVar()
        self.output_label = ttk.Label(self.main_frame, textvariable=self.output_text, foreground="#003366", wraplength=300)
        self.output_label.grid(row=8, column=0, columnspan=2, pady=(10, 0))

    def create_labeled_entry(self, label, row):
        ttk.Label(self.main_frame, text=label).grid(row=row, column=0, sticky="e", pady=3)
        entry = ttk.Entry(self.main_frame, width=25)
        entry.grid(row=row, column=1, sticky="w", pady=3)
        return entry

    def run_pump_thread(self):
        thread = threading.Thread(target=self.run_pump)
        thread.start()

    def run_file_thread(self):
        thread = threading.Thread(target=self.run_command_file)
        thread.start()

    def run_pump(self):
        self.stop_flag = False
        port = self.port_entry.get()
        rate = self.rate_entry.get()
        unit = self.unit_entry.get()
        diameter = self.diameter_entry.get()
        volume = self.volume_entry.get()
        Direction = self.Direction_entry.get()
        try:
            duration = int(self.duration_entry.get())
        except ValueError:
            self.update_output("❌ Invalid duration value.")
            return

        try:
            self.ser = serial.Serial(port, baudrate=19200, timeout=2)
            self.update_output(f"✅ Connected to {port}")
            self.ser.write(b'INF\r')
            time.sleep(0.5)

            self.send_command(f"DIA {diameter}")
            self.send_command(f"VOL {volume}")
            self.send_command(f"RAT {rate} {unit}")
            self.send_command(f"{Direction}")
            self.ser.write(b'RUN\r')
            self.update_output("🚀 Pump started")

            for _ in range(duration):
                if self.stop_flag:
                    self.update_output("🛑 Pump stopped early.")
                    break
                time.sleep(1)

            if not self.stop_flag:
                self.ser.write(b'STP\r')
                self.update_output("🧼 Pump automatically stopped.")

        except serial.SerialException as e:
            self.update_output(f"❌ Serial error: {e}")
        except Exception as e:
            self.update_output(f"⚠️ Error: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.update_output("🔒 Serial port closed.")
            self.ser = None

    def stop_pump(self):
        self.stop_flag = True
        if self.ser and self.ser.is_open:
            self.ser.write(b'STP\r')
            self.update_output("🛑 Stop command sent to pump.")

    def run_command_file(self):
        self.stop_flag = False
        port = self.port_entry.get()
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            self.update_output("❌ No file selected.")
            return

        try:
            self.ser = serial.Serial(port, baudrate=19200, timeout=2)
            self.update_output(f"✅ Connected to {port}")
            self.ser.write(b'INF\r')
            time.sleep(0.5)

            with open(file_path, 'r') as file:
                for line in file:
                    if self.stop_flag:
                        self.update_output("🛑 Stopped while processing file.")
                        break
                    line = line.strip()
                    if line:
                        self.update_output(f"➡️ Sending: {line}")
                        self.ser.write(f"{line}\r".encode())
                        time.sleep(1)

            if not self.stop_flag:
                self.ser.write(b'STP\r')
                self.update_output("✅ File execution complete.")

        except serial.SerialException as e:
            self.update_output(f"❌ Serial error: {e}")
        except Exception as e:
            self.update_output(f"⚠️ Error: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.update_output("🔒 Serial port closed.")
            self.ser = None

    def send_command(self, cmd):
        if not self.stop_flag:
            self.ser.write(f"{cmd}\r".encode())
            time.sleep(1)

    def update_output(self, message):
        print(message)
        self.output_text.set(message)

# Launch the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PumpController(root)
    root.mainloop()