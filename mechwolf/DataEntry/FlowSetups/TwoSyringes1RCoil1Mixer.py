import tkinter as tk
from tkinter import simpledialog, font, messagebox
import mechwolf as mw
import re
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

class DynamicDialog(simpledialog.Dialog):
    def __init__(self, parent, title, fields, include_mixer=False):
        self.fields = fields
        self.include_mixer = include_mixer
        self.entries = {}
        super().__init__(parent, title)

    def body(self, master):
        if self.include_mixer:
            self.mixer_var = tk.BooleanVar()
            tk.Label(master, text="Are you using a mixer?", anchor='w').pack(fill='x')
            tk.Checkbutton(master, text="Yes", variable=self.mixer_var, anchor='w').pack(fill='x')

        for field, label_text in self.fields.items():
            tk.Label(master, text=label_text, anchor='w').pack(fill='x')
            entry = tk.Entry(master)
            entry.pack(fill='x')
            self.entries[field] = entry
        return list(self.entries.values())[0]  # initial focus

    def apply(self):
        self.result = {field: entry.get() for field, entry in self.entries.items()}
        if self.include_mixer:
            self.result["using_mixer"] = self.mixer_var.get()

class ComponentApp:
    def __init__(self, root, pumps):
        self.root = root
        self.root.title("Create the Setup")
        self.pumps = pumps
        self.pump_type = self.determine_pump_type()
        self.added_elements = []
        self.apparatus = None
        self.custom_font = font.Font(family="Helvetica", size=14)
        self.apply_font(self.root)
        self.create_widgets()

    def apply_font(self, widget):
        widget.option_add("*Font", self.custom_font)
        for child in widget.winfo_children():
            self.apply_font(child)

    def create_widgets(self):
        tk.Label(self.root, text="Apparatus Name:", anchor='w').pack(fill='x')
        self.apparatus_name_entry = tk.Entry(self.root)
        self.apparatus_name_entry.pack(pady=10, fill='x')

        buttons = [
            ("Fill Vessel Details", self.fill_vessel_details),
            ("Fill Tubing Details", self.fill_tubing_details),
            ("Fill Coil Lengths", self.fill_coil_lengths),
            ("Create Setup", self.create_setup)
        ]

        for text, command in buttons:
            tk.Button(self.root, text=text, command=command, anchor='w').pack(pady=10, fill='x')

        self.listbox = tk.Listbox(self.root)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def fill_vessel_details(self):
        fields = {
            "vessel_1_name": "Enter the name for vessel 1:",
            "vessel_1_description": "Enter the description for vessel 1:",
            "vessel_2_name": "Enter the name for vessel 2:",
            "vessel_2_description": "Enter the description for vessel 2:",
            "product_vessel_name": "Enter the name for the product vessel:",
            "product_vessel_description": "Enter the description for the product vessel:"
        }
        dialog = DynamicDialog(self.root, "Enter Vessel Details", fields)
        if dialog.result is None:
            return

        self.vessel_1_description = dialog.result["vessel_1_description"]
        self.vessel_1_name = dialog.result["vessel_1_name"]
        self.vessel_2_description = dialog.result["vessel_2_description"]
        self.vessel_2_name = dialog.result["vessel_2_name"]
        self.product_vessel_description = dialog.result["product_vessel_description"]
        self.product_vessel_name = dialog.result["product_vessel_name"]

        self.add_elements_to_listbox([
            f"Vessel 1: {self.vessel_1_name}",
            f"Vessel 2: {self.vessel_2_name}",
            f"Product Vessel: {self.product_vessel_name}"
        ])

    def fill_tubing_details(self):
        fields = {
            "thin_tube_ID": "Enter the ID for thin tube (e.g., '0.02 in'):",
            "thin_tube_OD": "Enter the OD for thin tube (e.g., '1/16 in'):",
            "thin_tube_material": "Enter the material for thin tube (e.g., 'PFA'):",
            "thick_tube_ID": "Enter the ID for thick tube (e.g., '0.0625 in'):",
            "thick_tube_OD": "Enter the OD for thick tube (e.g., '1/8 in'):",
            "thick_tube_material": "Enter the material for thick tube (e.g., 'PFA'):"
        }
        dialog = DynamicDialog(self.root, "Enter Tubing Details", fields, include_mixer=True)
        if dialog.result is None:
            return

        def parse_and_validate(value):
            try:
                number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
                return f"{number} in"
            except (IndexError, ValueError):
                return None

        self.using_mixer = dialog.result["using_mixer"]
        self.thin_tube_ID = parse_and_validate(dialog.result["thin_tube_ID"])
        self.thin_tube_OD = parse_and_validate(dialog.result["thin_tube_OD"])
        self.thin_tube_material = dialog.result["thin_tube_material"]
        self.thick_tube_ID = parse_and_validate(dialog.result["thick_tube_ID"])
        self.thick_tube_OD = parse_and_validate(dialog.result["thick_tube_OD"])
        self.thick_tube_material = dialog.result["thick_tube_material"]

        if None in [self.thin_tube_ID, self.thin_tube_OD, self.thick_tube_ID, self.thick_tube_OD]:
            messagebox.showerror("Input Error", "Please enter valid numeric values for tube dimensions.")
            return

        self.added_elements.append("Thin Tube")
        if self.using_mixer:
            self.added_elements.append("Thick Tube")
        self.update_listbox()

    def fill_coil_lengths(self):
        fields = {
            "coil_a_length": "Enter the length of coil A (e.g., '5 foot'):",
            "coil_x_length": "Enter the length of coil X (e.g., '5 foot'):"
        }
        dialog = DynamicDialog(self.root, "Enter Coil Lengths", fields)
        if dialog.result is None:
            return

        self.coil_a_length = dialog.result["coil_a_length"]
        self.coil_x_length = dialog.result["coil_x_length"]

        self.add_elements_to_listbox([
            f"Coil A: {self.coil_a_length}",
            f"Coil X: {self.coil_x_length}"
        ])

    def add_elements_to_listbox(self, elements):
        self.added_elements.extend(elements)
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for element in self.added_elements:
            self.listbox.insert(tk.END, element)

    def determine_pump_type(self):
        for pump in self.pumps:
            if isinstance(pump, HarvardSyringePump):
                return "dual-channel"
        return "single-channel"

    def create_setup(self):
        vessel_1 = mw.Vessel(self.vessel_1_description, name=self.vessel_1_name)
        vessel_2 = mw.Vessel(self.vessel_2_description, name=self.vessel_2_name)
        product_vessel = mw.Vessel(self.product_vessel_description, name=self.product_vessel_name)

        def thin_tube(length):
            return mw.Tube(length=length, ID=self.thin_tube_ID, OD=self.thin_tube_OD, material=self.thin_tube_material)

        def thick_tube(length):
            return mw.Tube(length=length, ID=self.thick_tube_ID, OD=self.thick_tube_OD, material=self.thick_tube_material)

        coil_a = thin_tube(length=self.coil_a_length)
        coil_x = thin_tube(length=self.coil_x_length)

        def Tmixer(name):
            return mw.TMixer(name=name)

        T1 = Tmixer("reactor_coil")

        apparatus_name = self.apparatus_name_entry.get()
        A = mw.Apparatus(apparatus_name)

        if self.pump_type == "single-channel":
            A.add(self.pumps[0], vessel_1, coil_a)
            A.add(self.pumps[1], vessel_2, coil_a)
        elif self.pump_type == "dual-channel":
            A.add(self.pumps[0], vessel_1, coil_a)
            A.add(self.pumps[0], vessel_2, coil_a)

        A.add(vessel_1, T1, coil_a)
        A.add(vessel_2, T1, coil_a)
        A.add(T1, product_vessel, coil_x)

        self.apparatus = A
        self.root.destroy()  # Properly close the window

class ApparatusCreator:
    def __init__(self, *pumps):
        self.pumps = pumps

    def create_apparatus(self):
        root = tk.Tk()
        app = ComponentApp(root, self.pumps)
        root.mainloop()
        return app.apparatus