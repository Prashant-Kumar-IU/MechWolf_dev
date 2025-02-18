import json
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
        self.inChiKey = reagent['inChi Key']
        self.SMILES = reagent['SMILES']
        self.mol_weight = reagent['molecular weight (in g/mol)']
        self.eq = reagent['eq']
        self.syringe = reagent['syringe']
        self.moles = round(moles * self.eq, decimals=4)
        self.mass = round(self.moles * self.mol_weight, decimals=4)
        
    def __str__(self):
        return f"{self.name}"
    
    def get_name_and_eq(self):
        return f"{self.name}: {self.eq}"

class Solid(Reagent):
    def __init__(self, reagent, moles):
        super().__init__(reagent, moles)

class Liquid(Reagent):
    def __init__(self, reagent, moles):
        super().__init__(reagent, moles)
        assert 'density (in g/mL)' in reagent, f'Error: {reagent["name"]} does not have a density field'
        self.density = reagent['density (in g/mL)']
        self.volume = round(self.eq * moles * (self.mol_weight / self.density), decimals=4)

def process_data(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)

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

        solid_reagents = [Solid(reagent, moles_limiting) for reagent in data['solid reagents']]
        liquid_reagents = [Liquid(reagent, moles_limiting) for reagent in data['liquid reagents']]

        # Print data with just the name of reagent and their InChi, InChi key, and SMILES
        print("Reagent Data:")
        for reagent in solid_reagents + liquid_reagents:
            print(f"{reagent.name}: InChi: {reagent.inChi} | InChi Key: {reagent.inChiKey} | SMILES: {reagent.SMILES}\n")
      
        # Print the name of the limiting reagent and its moles
        print(f"\nLimiting Reagent: {limiting_reagent} | Moles: {moles_limiting:.4f}\n")
        
        # Print the list of solvents
        print(f"Solvents: {data['solvent']}\n")

        # Generate stoichiometry table
        reagent_list = solid_reagents + liquid_reagents

        reagent_table = QTable()
        reagent_table['Reagent'] = [reagent.name for reagent in reagent_list]
        reagent_table['Molecular Weight (g/mol)'] = [reagent.mol_weight for reagent in reagent_list]
        reagent_table['Amount (mmol)'] = [round(reagent.moles, decimals=4) for reagent in reagent_list]
        reagent_table['Mass (mg)'] = [round(reagent.mass, decimals=4) for reagent in reagent_list]
        reagent_table['Volume (mL)'] = [round((reagent.volume/1000), decimals=4) if hasattr(reagent, 'volume') and reagent.volume != 0 else "N/A" for reagent in reagent_list]
        reagent_table['Density (g/mL)'] = [reagent.density if hasattr(reagent, 'density') else "N/A" for reagent in reagent_list]
        reagent_table['eq'] = [reagent.eq for reagent in reagent_list]
        reagent_table['Syringe'] = [reagent.syringe for reagent in reagent_list]
        reagent_table['Concentration (M, mol/L)'] = [round(data['concentration (in mM)'] * reagent.eq / 1000, decimals=3) for reagent in reagent_list]

        reagent_table.pprint(max_lines=-1, max_width=-1)

        # Calculate volume of solution in the syringes
        if data['concentration (in mM)'] != 0:
            volume_solution = moles_limiting / (data['concentration (in mM)'] / 1000)
            print(f'Volume of solution in the syringes: {volume_solution:.4f} mL')
        else:
            print('Error: Concentration cannot be zero.')

def main():
    # This function is no longer needed
    pass

if __name__ == "__main__":
    main()