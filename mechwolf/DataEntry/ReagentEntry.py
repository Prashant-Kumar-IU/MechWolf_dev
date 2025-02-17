import json
import ipywidgets as widgets
from IPython.display import display, clear_output
from mechwolf.DataEntry.ProcessData import process_data

class ReagentInputForm:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = {
            'solid reagents': [],
            'liquid reagents': []
        }
        
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {
                'solid reagents': [],
                'liquid reagents': []
            }
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def create_widgets(self):
        self.reagents_list = widgets.VBox(layout=widgets.Layout(align_items='flex-end'))
        
        self.add_solid_button = widgets.Button(description='Add Solid Reagent')
        self.add_solid_button.on_click(self.add_solid_reagent)
        
        self.add_liquid_button = widgets.Button(description='Add Liquid Reagent')
        self.add_liquid_button.on_click(self.add_liquid_reagent)
        
        self.submit_button = widgets.Button(description='Submit')
        self.submit_button.on_click(self.submit)
        
        self.buttons_box = widgets.VBox([
            self.add_solid_button,
            self.add_liquid_button
        ], layout=widgets.Layout(width='30%', margin='0 10px 0 0'))
        
        display(widgets.VBox([
            widgets.HBox([
                self.buttons_box,
                self.reagents_list
            ])
        ]))
        
        self.update_display()
    
    def update_display(self):
        children = []
        for reagent in self.data['solid reagents'] + self.data['liquid reagents']:
            label = widgets.Label(f"{reagent['name']}: {reagent['eq']}")
            edit_button = widgets.Button(description='Edit', button_style='info', style={'button_color': '#cce5ff', 'font_color': 'black'})
            delete_button = widgets.Button(description='Delete', button_style='danger', style={'button_color': '#ffcccc', 'font_color': 'black'})
            edit_button.on_click(lambda b, r=reagent: self.edit_reagent(r))
            delete_button.on_click(lambda b, r=reagent: self.delete_reagent(r))
            children.append(widgets.HBox([label, edit_button, delete_button], layout=widgets.Layout(margin='0 0 10px 0')))
        self.reagents_list.children = children
        
        if self.data['solid reagents'] or self.data['liquid reagents']:
            if self.submit_button not in self.buttons_box.children:
                self.buttons_box.children += (self.submit_button,)
        else:
            if self.submit_button in self.buttons_box.children:
                self.buttons_box.children = tuple(child for child in self.buttons_box.children if child != self.submit_button)
    
    def delete_reagent(self, reagent):
        if reagent in self.data['solid reagents']:
            self.data['solid reagents'].remove(reagent)
        elif reagent in self.data['liquid reagents']:
            self.data['liquid reagents'].remove(reagent)
        self.update_display()
    
    def add_solid_reagent(self, b):
        self.reagent_window('solid')
    
    def add_liquid_reagent(self, b):
        self.reagent_window('liquid')
    
    def reagent_window(self, reagent_type, reagent=None):
        output_widget = widgets.Output()
        with output_widget:
            name_input = widgets.Text(value=reagent['name'] if reagent else '', layout=widgets.Layout(width='50%'))
            inchi_input = widgets.Text(value=reagent['inChi'] if reagent else '', layout=widgets.Layout(width='50%'))
            smiles_input = widgets.Text(value=reagent['SMILES'] if reagent else '', layout=widgets.Layout(width='50%'))
            inchikey_input = widgets.Text(value=reagent['inChi Key'] if reagent else '', layout=widgets.Layout(width='50%'))
            mw_input = widgets.FloatText(value=reagent['molecular weight (in g/mol)'] if reagent else 0, layout=widgets.Layout(width='50%'))
            eq_input = widgets.FloatText(value=reagent['eq'] if reagent else 0, layout=widgets.Layout(width='50%'))
            syringe_input = widgets.IntText(value=reagent['syringe'] if reagent else 0, layout=widgets.Layout(width='50%'))
            
            if reagent_type == 'solid':
                density_input = None
            else:
                density_input = widgets.FloatText(value=reagent['density (in g/mL)'] if reagent else 0, layout=widgets.Layout(width='50%'))
            
            save_button = widgets.Button(description='Save')
            
            def save_reagent(b):
                try:
                    new_reagent = {
                        'name': name_input.value,
                        'inChi': inchi_input.value,
                        'SMILES': smiles_input.value,
                        'inChi Key': inchikey_input.value,
                        'molecular weight (in g/mol)': mw_input.value,
                        'eq': eq_input.value,
                        'syringe': syringe_input.value
                    }
                    
                    if reagent_type == 'solid':
                        if reagent:
                            self.data['solid reagents'].remove(reagent)
                        self.data['solid reagents'].append(new_reagent)
                    else:
                        new_reagent['density (in g/mL)'] = density_input.value
                        if reagent:
                            self.data['liquid reagents'].remove(reagent)
                        self.data['liquid reagents'].append(new_reagent)
                    
                    self.update_display()
                    output_widget.clear_output()  # Clear the form after saving
                except ValueError:
                    print("Invalid input: Please enter valid numerical values for molecular weight, eq, density, and syringe.")
            
            save_button.on_click(save_reagent)
            
            display(widgets.VBox([
                widgets.Label('Name:'), name_input,
                widgets.Label('InChi:'), inchi_input,
                widgets.Label('SMILES:'), smiles_input,
                widgets.Label('InChi Key:'), inchikey_input,
                widgets.Label('Molecular weight (g/mol):'), mw_input,
                widgets.Label('Eq:'), eq_input,
                widgets.Label('Density (g/mL):') if density_input else widgets.Label(), density_input if density_input else widgets.Label(),
                widgets.Label('Syringe:'), syringe_input,
                save_button
            ]))
        
        display(output_widget)
    
    def edit_reagent(self, reagent):
        reagent_type = 'solid' if reagent in self.data['solid reagents'] else 'liquid'
        self.reagent_window(reagent_type, reagent)
    
    def submit(self, b):
        self.mass_scale_input = widgets.FloatText(layout=widgets.Layout(width='50%'))
        self.concentration_input = widgets.FloatText(layout=widgets.Layout(width='50%'))
        self.solvent_input = widgets.Text(layout=widgets.Layout(width='50%'))
        
        save_button = widgets.Button(description='Save')
        
        def save_data(b):
            try:
                self.data['mass scale (in mg)'] = self.mass_scale_input.value
                self.data['concentration (in mM)'] = self.concentration_input.value
                self.data['solvent'] = self.solvent_input.value
            except ValueError:
                print("Invalid input: Please enter valid numerical values for mass scale and concentration.")
                return
            
            self.save_data()
            clear_output()
            process_data(self.data_file)
        
        save_button.on_click(save_data)
        
        display(widgets.VBox([
            widgets.Label('Mass scale (mg):'), self.mass_scale_input,
            widgets.Label('Concentration (mM):'), self.concentration_input,
            widgets.Label('Solvents:'), self.solvent_input,
            save_button
        ]))
    
    def mainloop(self):
        # This method is just a placeholder to match the old interface
        pass

    def run(self):
        if not self.data['solid reagents'] and not self.data['liquid reagents']:
            self.create_widgets()
        else:
            process_data(self.data_file)
            make_changes = input("Do you want to make any changes? (yes/no): ").strip().lower()
            if make_changes == 'yes':
                self.create_widgets()
            else:
                return

if __name__ == "__main__":
    data_file = input("Enter the JSON file name: ").strip()
    app = ReagentInputForm(data_file)
    app.run()