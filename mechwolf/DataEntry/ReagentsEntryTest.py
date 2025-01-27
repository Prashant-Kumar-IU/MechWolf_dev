import tkinter as tk
from tkinter import ttk
from astropy.table import QTable
from sigfig import round

class Reagent:
    def __init__(self, reagent, moles):
        assert 'name' in reagent, 'ERROR: one of the reagents does not have a name field'
        assert 'inChi' in reagent, f'Error: {reagent["name"]} does not have an inChi field'
        assert 'inChi Key' in reagent, f'Error: {reagent["name"]} does not have an inChi key field'
        assert 'molecular weight (in g/mol)' in reagent, f'Error: {reagent["name"]} does not have a molecular weight field'
        assert 'eq' in reagent, f'Error: {reagent["name"]} does not have an eq field'
        assert 'syringe' in reagent, f'Error: {reagent["name"]} does not have a syringe # field'
        
        self.name = reagent['name']
        self.inChi = reagent['inChi']
        self.mol_weight = reagent['molecular weight (in g/mol)']
        self.eq = reagent['eq']
        self.syringe = reagent['syringe']
        self.moles = round(moles * self.eq, decimals=4)
        self.mass = round(self.moles * self.mol_weight, decimals=4)
        
    def __str__(self):
        return f"{self.name}"

class Solid(Reagent):
    def __init__(self, reagent, moles):
        super().__init__(reagent, moles)

class Liquid(Reagent):
    def __init__(self, reagent, moles):
        super().__init__(reagent, moles)
        assert 'density (in g/mL)' in reagent, f'Error: {reagent["name"]} does not have a density field'
        self.density = reagent['density (in g/mL)']
        self.volume = round(self.eq * moles * (self.mol_weight / self.density), decimals=4)

class ReagentInputForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Reagent Input Form')
        self.geometry('500x400')
        
        self.data = {
            'solid reagents': [],
            'liquid reagents': []
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text='Mass scale (in mg):').grid(row=0, column=0, sticky='e')
        self.mass_scale_input = ttk.Entry(main_frame)
        self.mass_scale_input.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text='Concentration (in mM):').grid(row=1, column=0, sticky='e')
        self.concentration_input = ttk.Entry(main_frame)
        self.concentration_input.grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text='Solvent:').grid(row=2, column=0, sticky='e')
        self.solvent_input = ttk.Entry(main_frame)
        self.solvent_input.grid(row=2, column=1, pady=5)
        
        ttk.Button(main_frame, text='Add Solid Reagent', command=self.add_solid_reagent).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(main_frame, text='Add Liquid Reagent', command=self.add_liquid_reagent).grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Button(main_frame, text='Submit', command=self.submit).grid(row=5, column=0, columnspan=2, pady=10)
    
    def add_solid_reagent(self):
        self.reagent_window('solid')
    
    def add_liquid_reagent(self):
        self.reagent_window('liquid')
    
    def reagent_window(self, reagent_type):
        window = tk.Toplevel(self)
        window.title(f'Add {reagent_type.capitalize()} Reagent')
        window.geometry('400x300')
        
        frame = ttk.Frame(window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text='Name:').grid(row=0, column=0, sticky='e')
        name_input = ttk.Entry(frame)
        name_input.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text='InChi:').grid(row=1, column=0, sticky='e')
        inchi_input = ttk.Entry(frame)
        inchi_input.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text='SMILES:').grid(row=2, column=0, sticky='e')
        smiles_input = ttk.Entry(frame)
        smiles_input.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text='InChi Key:').grid(row=3, column=0, sticky='e')
        inchikey_input = ttk.Entry(frame)
        inchikey_input.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text='Molecular weight (in g/mol):').grid(row=4, column=0, sticky='e')
        mw_input = ttk.Entry(frame)
        mw_input.grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text='Eq:').grid(row=5, column=0, sticky='e')
        eq_input = ttk.Entry(frame)
        eq_input.grid(row=5, column=1, pady=5)
        
        if reagent_type == 'solid':
            ttk.Label(frame, text='Syringe:').grid(row=6, column=0, sticky='e')
            syringe_input = ttk.Entry(frame)
            syringe_input.grid(row=6, column=1, pady=5)
        else:
            ttk.Label(frame, text='Density (in g/mL):').grid(row=6, column=0, sticky='e')
            density_input = ttk.Entry(frame)
            density_input.grid(row=6, column=1, pady=5)
            
            ttk.Label(frame, text='Syringe:').grid(row=7, column=0, sticky='e')
            syringe_input = ttk.Entry(frame)
            syringe_input.grid(row=7, column=1, pady=5)
        
        def save_reagent():
            try:
                reagent = {
                    'name': name_input.get(),
                    'inChi': inchi_input.get(),
                    'SMILES': smiles_input.get(),
                    'inChi Key': inchikey_input.get(),
                    'molecular weight (in g/mol)': float(mw_input.get()),
                    'eq': float(eq_input.get())
                }
                
                if reagent_type == 'solid':
                    reagent['syringe'] = int(syringe_input.get())
                    self.data['solid reagents'].append(reagent)
                else:
                    reagent['density (in g/mL)'] = float(density_input.get())
                    reagent['syringe'] = int(syringe_input.get())
                    self.data['liquid reagents'].append(reagent)
                
                window.destroy()
            except ValueError:
                print("Invalid input: Please enter valid numerical values for molecular weight, eq, density, and syringe.")
        
        ttk.Button(frame, text='Save', command=save_reagent).grid(row=8, column=0, columnspan=2, pady=10)
    
    def submit(self):
        try:
            self.data['mass scale (in mg)'] = float(self.mass_scale_input.get())
            self.data['concentration (in mM)'] = float(self.concentration_input.get())
            self.data['solvent'] = self.solvent_input.get()
        except ValueError:
            print("Invalid input: Please enter valid numerical values for mass scale and concentration.")
            return
        
        self.process_data(self.data)
        self.destroy()  # Close the main window
    
    def process_data(self, data):
        limiting_reagent = None
        mw_limiting = None

        for reagent in data['solid reagents'] + data['liquid reagents']:
            if reagent['eq'] == 1:
                limiting_reagent = reagent['name']
                mw_limiting = reagent['molecular weight (in g/mol)']
                break

        if mw_limiting is not None:
            mass_scale = data['mass scale (in mg)']
            moles_limiting = mass_scale / mw_limiting

            for reagent in data['solid reagents']:
                reagent['moles'] = moles_limiting * reagent['eq']
                reagent['mass'] = reagent['moles'] * reagent['molecular weight (in g/mol)']

            for reagent in data['liquid reagents']:
                reagent['moles'] = moles_limiting * reagent['eq']
                reagent['mass'] = reagent['moles'] * reagent['molecular weight (in g/mol)']
                reagent['volume'] = reagent['mass'] / reagent['density (in g/mL)']

            # Print data with just the name of reagent and their InChi, InChi key, and SMILES
            print("Reagent Data:")
            for reagent in data['solid reagents'] + data['liquid reagents']:
                print(f"{reagent['name']}: InChi: {reagent['inChi']} | InChi Key: {reagent['inChi Key']} | SMILES: {reagent['SMILES']}\n")
      
            # Print the name of the limiting reagent and its moles
            print(f"\nLimiting Reagent: {limiting_reagent}, Moles: {moles_limiting:.4f}\n")

            # Generate stoichiometry table
            reagent_list = [Solid(reagent, moles_limiting) for reagent in data['solid reagents']] + \
                           [Liquid(reagent, moles_limiting) for reagent in data['liquid reagents']]

            reagent_table = QTable()
            reagent_table['Reagent'] = [reagent.name for reagent in reagent_list]
            reagent_table['Molecular Weight (g/mol)'] = [reagent.mol_weight for reagent in reagent_list]
            reagent_table['Amount (mmol)'] = [reagent.moles for reagent in reagent_list]
            reagent_table['Mass (mg)'] = [reagent.mass for reagent in reagent_list]
            reagent_table['Volume (mL)'] = [round((reagent.volume/1000), 4) if hasattr(reagent, 'volume') else "N/A" for reagent in reagent_list]
            reagent_table['Density (g/mL)'] = [reagent.density if hasattr(reagent, 'density') else "N/A" for reagent in reagent_list]
            reagent_table['eq'] = [reagent.eq for reagent in reagent_list]
            reagent_table['Syringe'] = [reagent.syringe for reagent in reagent_list]
            reagent_table['Concentration (M, mol/L)'] = [round(data['concentration (in mM)'] * reagent.eq / 1000, decimals=3) for reagent in reagent_list]

            reagent_table.pprint(max_lines=-1, max_width=-1)

            # Calculate volume of solution in the syringes
            volume_solution = moles_limiting / (data['concentration (in mM)'] / 1000)
            print(f'Volume of solution in the syringes: {volume_solution:.4f} mL')

if __name__ == "__main__":
    app = ReagentInputForm()
    app.mainloop()