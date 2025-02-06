import ipywidgets as widgets
from IPython.display import display, clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import json

class ComponentApp:
    def __init__(self, pumps, json_file):
        self.pumps = pumps
        self.json_file = json_file
        self.data = {}
        self.setup_complete = False
        self.widget_container = None
        self.load_existing_config()  # Add this line

    def load_existing_config(self):
        """Load most recent configuration if it exists"""
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                if 'apparatus_configs' in data and data['apparatus_configs']:
                    last_config = data['apparatus_configs'][-1]
                    self.existing_config = last_config
                    return
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self.existing_config = None

    def create_widgets(self):
        # Create inputs starting with apparatus name
        self.apparatus_name_input = widgets.Text(placeholder="Enter apparatus name", layout=widgets.Layout(width='50%'))
        # Create Vessel 1 inputs
        self.vessel1_name_input = widgets.Text(placeholder="Enter Vessel 1 name", layout=widgets.Layout(width='50%'))
        self.vessel1_desc_input = widgets.Text(placeholder="Enter Vessel 1 description", layout=widgets.Layout(width='50%'))
        # Create Vessel 2 inputs
        self.vessel2_name_input = widgets.Text(placeholder="Enter Vessel 2 name", layout=widgets.Layout(width='50%'))
        self.vessel2_desc_input = widgets.Text(placeholder="Enter Vessel 2 description", layout=widgets.Layout(width='50%'))
        # Create Product Vessel inputs
        self.product_vessel_name_input = widgets.Text(placeholder="Enter Product Vessel name", layout=widgets.Layout(width='50%'))
        self.product_vessel_desc_input = widgets.Text(placeholder="Enter Product Vessel description", layout=widgets.Layout(width='50%'))
        # Create Tubing inputs - renamed for clarity
        self.reaction_tube_id_input = widgets.Text(placeholder="Reaction Tube ID", layout=widgets.Layout(width='50%'))
        self.reaction_tube_od_input = widgets.Text(placeholder="Reaction Tube OD", layout=widgets.Layout(width='50%'))
        self.reaction_tube_material_input = widgets.Text(placeholder="Reaction Tube Material", layout=widgets.Layout(width='50%'))
        # Checkbox and Mixer tubing inputs
        self.using_mixer_checkbox = widgets.Checkbox(value=False, description="Using Mixer")
        self.mixer_tube_id_input = widgets.Text(placeholder="Mixer Tube ID", layout=widgets.Layout(width='50%'))
        self.mixer_tube_od_input = widgets.Text(placeholder="Mixer Tube OD", layout=widgets.Layout(width='50%'))
        self.mixer_tube_material_input = widgets.Text(placeholder="Mixer Tube Material", layout=widgets.Layout(width='50%'))
        # Create Coil inputs
        self.coil_a_input = widgets.Text(placeholder="Coil A length", layout=widgets.Layout(width='50%'))
        self.coil_x_input = widgets.Text(placeholder="Coil X length", layout=widgets.Layout(width='50%'))
        self.setup_button = widgets.Button(description="Create Setup")
        self.setup_button.on_click(self.create_setup)
        
        # Add a checkbox to control whether to update existing config with better layout
        update_message = widgets.HTML(
            value="<b>Existing configuration found!</b> Check below if you wish to update it. Then make the necessary changes and click Create Setup. Otherwise, just click Create Setup button to go with the existing configuration.",
            layout=widgets.Layout(width='100%', margin='10px 0px')
        )
        
        self.update_existing = widgets.Checkbox(
            value=False,
            description='Update existing configuration',
            disabled=self.existing_config is None,
            layout=widgets.Layout(
                width='100%',
                margin='5px 0px 0px 0px',  # top, right, bottom, left margins
                display='flex',
                justify_content='flex-start'
            ),
            style={'description_width': 'auto'}
        )
        
        # Pre-fill values if updating existing config
        if self.existing_config:
            self.apparatus_name_input.value = self.existing_config['apparatus_name']
            vessel1, vessel2, product_vessel = self.existing_config['vessels']
            self.vessel1_name_input.value = vessel1['name']
            self.vessel1_desc_input.value = vessel1['description']
            self.vessel2_name_input.value = vessel2['name']
            self.vessel2_desc_input.value = vessel2['description']
            self.product_vessel_name_input.value = product_vessel['name']
            self.product_vessel_desc_input.value = product_vessel['description']
            self.reaction_tube_id_input.value = self.existing_config['tubes']['reaction']['ID']
            self.reaction_tube_od_input.value = self.existing_config['tubes']['reaction']['OD']
            self.reaction_tube_material_input.value = self.existing_config['tubes']['reaction']['material']
            self.using_mixer_checkbox.value = self.existing_config['using_mixer']
            if self.existing_config['using_mixer']:
                self.mixer_tube_id_input.value = self.existing_config['tubes']['mixer']['ID']
                self.mixer_tube_od_input.value = self.existing_config['tubes']['mixer']['OD']
                self.mixer_tube_material_input.value = self.existing_config['tubes']['mixer']['material']
            self.coil_a_input.value = self.existing_config['coils'][0]['length']
            self.coil_x_input.value = self.existing_config['coils'][1]['length']
            
        self.widget_container = widgets.VBox([
            update_message if self.existing_config else widgets.HTML("No existing configuration found."),
            self.update_existing,
            widgets.HTML("<hr>"),  # Add a separator line
            widgets.Label("Apparatus Name:"), 
            self.apparatus_name_input,
            widgets.Label("Vessel 1 Details:"),
            self.vessel1_name_input,
            self.vessel1_desc_input,
            widgets.Label("Vessel 2 Details:"),
            self.vessel2_name_input,
            self.vessel2_desc_input,
            widgets.Label("Product Vessel Details:"),
            self.product_vessel_name_input,
            self.product_vessel_desc_input,
            widgets.Label("Reaction Tube Details:"),
            self.reaction_tube_id_input,
            self.reaction_tube_od_input,
            self.reaction_tube_material_input,
            self.using_mixer_checkbox,
            widgets.Label("Mixer Tube Details (if using mixer):"),
            self.mixer_tube_id_input,
            self.mixer_tube_od_input,
            self.mixer_tube_material_input,
            widgets.Label("Coil Lengths:"),
            self.coil_a_input,
            self.coil_x_input,
            self.setup_button
        ], layout=widgets.Layout(width='100%'))
        display(self.widget_container)

    def create_setup(self, b):
        # First validate all inputs are present
        if self.using_mixer_checkbox.value:
            if not all([
                self.mixer_tube_id_input.value,
                self.mixer_tube_od_input.value,
                self.mixer_tube_material_input.value
            ]):
                print("Error: When using mixer, you must fill in all mixer tube details")
                return

        # Gather inputs with validation
        try:
            self.data.update({
                'vessel1_name': self.vessel1_name_input.value or "",
                'vessel1_desc': self.vessel1_desc_input.value or "",
                'vessel2_name': self.vessel2_name_input.value or "",
                'vessel2_desc': self.vessel2_desc_input.value or "",
                'product_vessel_name': self.product_vessel_name_input.value or "",
                'product_vessel_desc': self.product_vessel_desc_input.value or "",
                'reaction_tube_id_raw': self.reaction_tube_id_input.value or "",
                'reaction_tube_od_raw': self.reaction_tube_od_input.value or "",
                'reaction_tube_material': self.reaction_tube_material_input.value or "",
                'using_mixer': self.using_mixer_checkbox.value,
                'mixer_tube_id_raw': self.mixer_tube_id_input.value or "",
                'mixer_tube_od_raw': self.mixer_tube_od_input.value or "",
                'mixer_tube_material': self.mixer_tube_material_input.value or "",
                'coil_a_raw': self.coil_a_input.value or "",
                'coil_x_raw': self.coil_x_input.value or "",
                'apparatus_name': self.apparatus_name_input.value or ""
            })
        except Exception as e:
            print(f"Error gathering inputs: {str(e)}")
            return

        # Validate required fields first
        required_fields = {
            'Apparatus Name': self.data['apparatus_name'],
            'Vessel 1 Name': self.data['vessel1_name'],
            'Vessel 2 Name': self.data['vessel2_name'],
            'Product Vessel Name': self.data['product_vessel_name'],
            'Reaction Tube ID': self.data['reaction_tube_id_raw'],
            'Reaction Tube OD': self.data['reaction_tube_od_raw'],
            'Reaction Tube Material': self.data['reaction_tube_material'],
            'Coil A Length': self.data['coil_a_raw'],
            'Coil X Length': self.data['coil_x_raw']
        }

        missing = [name for name, value in required_fields.items() if not value]
        if missing:
            print(f"Error: Please fill in these required fields: {', '.join(missing)}")
            return

        # Error handling for tube dimensions with fraction support
        import re
        def parse_tube_dimension(value):
            """Parse tube dimension that could be fraction or decimal"""
            try:
                # Check for fraction format (e.g., "1/16 in" or "1/16")
                fraction_match = re.match(r'(\d+)/(\d+)\s*(?:in)?', value)
                if fraction_match:
                    num, denom = map(int, fraction_match.groups())
                    return f"{num}/{denom} in"
                
                # Handle decimal format
                number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
                return f"{number} in"
            except (IndexError, ValueError):
                return None
            
        self.data['reaction_tube_ID'] = parse_tube_dimension(self.data['reaction_tube_id_raw'])
        self.data['reaction_tube_OD'] = parse_tube_dimension(self.data['reaction_tube_od_raw'])
        if None in [self.data['reaction_tube_ID'], self.data['reaction_tube_OD']]:
            print("Error: Please enter valid values for reaction tube dimensions (e.g., '1/16 in' or '0.0625 in').")
            return
        
        # If using mixer, parse mixer tube dimensions
        if self.data['using_mixer']:
            self.data['mixer_tube_ID'] = parse_tube_dimension(self.data['mixer_tube_id_raw'])
            self.data['mixer_tube_OD'] = parse_tube_dimension(self.data['mixer_tube_od_raw'])
            if None in [self.data['mixer_tube_ID'], self.data['mixer_tube_OD']]:
                print("Error: Please enter valid values for mixer tube dimensions (e.g., '1/8 in' or '0.125 in').")
                return

        # Error handling for coil lengths
        def parse_numeric_foot(value):
            try:
                number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
                return f"{number} foot"
            except (IndexError, ValueError):
                return None
            
        self.data['coil_a_length'] = parse_numeric_foot(self.data['coil_a_raw'])
        self.data['coil_x_length'] = parse_numeric_foot(self.data['coil_x_raw'])
        if None in [self.data['coil_a_length'], self.data['coil_x_length']]:
            print("Error: Please enter valid numeric values for coil lengths.")
            return

        # Validate all required fields are filled
        required_fields = {
            'apparatus_name': self.data['apparatus_name'],
            'vessel1_name': self.data['vessel1_name'],
            'vessel2_name': self.data['vessel2_name'],
            'product_vessel_name': self.data['product_vessel_name'],
            'reaction_tube_ID': self.data['reaction_tube_ID'],
            'coil_lengths': [self.data['coil_a_length'], self.data['coil_x_length']]
        }

        # Check if any required field is empty
        missing_fields = [k for k, v in required_fields.items() if not v]
        if missing_fields:
            print(f"Error: Please fill in all required fields: {', '.join(missing_fields)}")
            return
            
        # Handle configuration update
        if self.update_existing.value and self.existing_config:
            try:
                with open(self.json_file, 'r') as f:
                    existing_data = json.load(f)
                # Remove the last config since we're updating it
                existing_data['apparatus_configs'].pop()
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = {'apparatus_configs': []}
        else:
            # Handle new configuration
            try:
                with open(self.json_file, 'r') as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = {'apparatus_configs': []}

        # Prepare apparatus config
        apparatus_config = {
            'apparatus_name': self.data['apparatus_name'],
            'vessels': [
                {'name': self.data['vessel1_name'], 'description': self.data['vessel1_desc']},
                {'name': self.data['vessel2_name'], 'description': self.data['vessel2_desc']},
                {'name': self.data['product_vessel_name'], 'description': self.data['product_vessel_desc']}
            ],
            'tubes': {
                'reaction': {
                    'ID': self.data['reaction_tube_ID'],
                    'OD': self.data['reaction_tube_OD'],
                    'material': self.data['reaction_tube_material']
                }
            },
            'coils': [
                {'length': self.data['coil_a_length']},
                {'length': self.data['coil_x_length']}
            ],
            'using_mixer': self.data['using_mixer']
        }

        if self.data['using_mixer']:
            apparatus_config['tubes']['mixer'] = {
                'ID': self.data['mixer_tube_ID'],
                'OD': self.data['mixer_tube_OD'],
                'material': self.data['mixer_tube_material']
            }

        # Append or update
        if 'apparatus_configs' not in existing_data:
            existing_data['apparatus_configs'] = []
        existing_data['apparatus_configs'].append(apparatus_config)

        # Write back to file
        with open(self.json_file, 'w') as f:
            json.dump(existing_data, f, indent=4)

        self.widget_container.close()  # Close the widget container
        self.setup_complete = True  # Signal completion
        clear_output()
        print("Configuration saved successfully!")

class ApparatusCreator:
    def __init__(self, *pumps, data_file=None):
        self.pumps = pumps
        self.json_file = data_file if data_file else "apparatus_config.json"
        # Add pump_type determination here
        self.pump_type = self.determine_pump_type()

    def determine_pump_type(self):
        for pump in self.pumps:
            if isinstance(pump, HarvardSyringePump):
                return "dual-channel"
        return "single-channel"

    def create_apparatus(self):
        import time
        from IPython import get_ipython
        import asyncio

        # Create and display widgets
        app = ComponentApp(self.pumps, self.json_file)
        app.create_widgets()
        
        # Block until setup is complete
        while not app.setup_complete:
            time.sleep(0.1)  # Small delay
            # Force IPython to process events properly
            if get_ipython():
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_ipython().kernel.do_one_iteration())
                
        # Now read the saved configuration and create apparatus
        with open(self.json_file, 'r') as f:
            data = json.load(f)
            
        if 'apparatus_configs' not in data or not data['apparatus_configs']:
            raise ValueError("No apparatus configuration found")
            
        config = data['apparatus_configs'][-1]
        print(f"Using configuration: {config['apparatus_name']}")
        
        # Create apparatus from config
        A = mw.Apparatus(config['apparatus_name'])
        
        # Create vessels
        vessels = [mw.Vessel(v['description'], name=v['name']) for v in config['vessels']]
        vessel1, vessel2, product_vessel = vessels
        
        # Create tubes function
        def make_tube(tube_config, length=None):
            return mw.Tube(
                length=length or "0 in",
                ID=tube_config['ID'],
                OD=tube_config['OD'],
                material=tube_config['material']
            )
        
        # Create tubes and coils with updated names
        reaction_tube = lambda length: make_tube(config['tubes']['reaction'], length)
        if config['using_mixer']:
            mixer_tube = lambda length: make_tube(config['tubes']['mixer'], length)
        
        coil_a = reaction_tube(config['coils'][0]['length'])
        coil_x = reaction_tube(config['coils'][1]['length'])
        
        # Create T Mixer component (matching main program)
        def Tmixer(name):
            """Returns a TMixer with the given name."""
            return mw.TMixer(name=name)

        T1 = Tmixer(coil_x)
        # Build apparatus with the pumps (matching main program order)
        A = mw.Apparatus(config['apparatus_name'])
        
        # Add pump connections first
        if self.pump_type == "single-channel":
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
        elif self.pump_type == "dual-channel":
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)

        # Add mixer and coil connections in same order as main program
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        A.add(T1, product_vessel, coil_x)
        
        return A

if __name__ == "__main__":
    from sys import argv
    pump_1 = HarvardSyringePump()
    pump_2 = HarvardSyringePump()
    creator = ApparatusCreator(pump_1, pump_2, json_file="apparatus_config.json")
    creator.create_apparatus()