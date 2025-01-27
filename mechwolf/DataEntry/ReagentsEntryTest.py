import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

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
        
        ttk.Label(main_frame, text='Limiting reagent:').grid(row=3, column=0, sticky='e')
        self.limiting_reagent_input = ttk.Entry(main_frame)
        self.limiting_reagent_input.grid(row=3, column=1, pady=5)
        
        ttk.Button(main_frame, text='Add Solid Reagent', command=self.add_solid_reagent).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(main_frame, text='Add Liquid Reagent', command=self.add_liquid_reagent).grid(row=5, column=0, columnspan=2, pady=5)
        
        ttk.Button(main_frame, text='Submit', command=self.submit).grid(row=6, column=0, columnspan=2, pady=10)
    
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
        
        if reagent_type == 'solid':
            ttk.Label(frame, text='Eq:').grid(row=5, column=0, sticky='e')
            eq_input = ttk.Entry(frame)
            eq_input.grid(row=5, column=1, pady=5)
            
            ttk.Label(frame, text='Syringe:').grid(row=6, column=0, sticky='e')
            syringe_input = ttk.Entry(frame)
            syringe_input.grid(row=6, column=1, pady=5)
        else:
            ttk.Label(frame, text='Eq:').grid(row=5, column=0, sticky='e')
            eq_input = ttk.Entry(frame)
            eq_input.grid(row=5, column=1, pady=5)

            ttk.Label(frame, text='Density (in g/mL):').grid(row=5, column=0, sticky='e')
            density_input = ttk.Entry(frame)
            density_input.grid(row=5, column=1, pady=5)
            
            ttk.Label(frame, text='Syringe:').grid(row=6, column=0, sticky='e')
            syringe_input = ttk.Entry(frame)
            syringe_input.grid(row=6, column=1, pady=5)
        
        def save_reagent():
            try:
                reagent = {
                    'name': name_input.get(),
                    'inChi': inchi_input.get(),
                    'SMILES': smiles_input.get(),
                    'inChi Key': inchikey_input.get(),
                    'molecular weight (in g/mol)': float(mw_input.get())
                }
                
                if reagent_type == 'solid':
                    reagent['eq'] = float(eq_input.get())
                    reagent['syringe'] = int(syringe_input.get())
                    self.data['solid reagents'].append(reagent)
                else:
                    reagent['eq'] = float(eq_input.get())
                    reagent['density (in g/mL)'] = float(density_input.get())
                    reagent['syringe'] = int(syringe_input.get())
                    self.data['liquid reagents'].append(reagent)
                
                window.destroy()
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter valid numerical values for molecular weight, eq, density, and syringe.")
        
        ttk.Button(frame, text='Save', command=save_reagent).grid(row=7, column=0, columnspan=2, pady=10)
    
    def submit(self):
        try:
            self.data['mass scale (in mg)'] = float(self.mass_scale_input.get())
            self.data['concentration (in mM)'] = float(self.concentration_input.get())
            self.data['solvent'] = self.solvent_input.get()
            self.data['limiting reagent'] = self.limiting_reagent_input.get()
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numerical values for mass scale and concentration.")
            return
        
        self.process_data(self.data)
        self.destroy()  # Close the main window
        print(self.data)  # Print the data to the console
        print("\n\n")  # Leave a couple of lines of space
        self.print_limiting_reagent_info(self.data)
    
    def process_data(self, data):
        limiting_reagent = data['limiting reagent']
        mw_limiting = None

        for reagent in data['solid reagents'] + data['liquid reagents']:
            if reagent['name'] == limiting_reagent:
                mw_limiting = reagent['molecular weight (in g/mol)']
                break

        if mw_limiting is not None:
            try:
                mass_scale = float(data['mass scale (in mg)'])
            except ValueError:
                messagebox.showerror("Error", "Invalid input: numerical values only")
                mass_scale = 0

            moles = mass_scale / mw_limiting

            messagebox.showinfo("Result", f'The amount of limiting reagent = {moles * 1000:.4f} mmol')
        else:
            messagebox.showerror("Error", f'Limiting reagent {limiting_reagent} not found in the reagents list.')

        messagebox.showinfo("Data", f'Data: {data}')
    
    def print_limiting_reagent_info(self, data):
        limiting_reagent = data['limiting reagent']
        mw_limiting = None

        for reagent in data['solid reagents'] + data['liquid reagents']:
            if reagent['name'] == limiting_reagent:
                mw_limiting = reagent['molecular weight (in g/mol)']
                break

        if mw_limiting is not None:
            print(f"The limiting reagent is {limiting_reagent}")
            print(f"Molecular weight of limiting reagent: {mw_limiting} g/mol")
            print("I am at the end of the code")
        else:
            print(f"Limiting reagent {limiting_reagent} not found in the reagents list.")