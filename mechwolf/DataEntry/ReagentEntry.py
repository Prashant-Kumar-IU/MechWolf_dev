import json
import ipywidgets as widgets
from IPython.display import display, clear_output, Image
from mechwolf.DataEntry.Reagents.ProcessData import process_data
from mechwolf.DataEntry.Reagents.utils import validate_smiles  # Import the validation function
from typing import Dict, Any, Optional, List, Callable, Union
import requests
import io
import base64
import sys
import os
from contextlib import contextmanager
from PIL import Image as PILImage

# Context manager to suppress stdout/stderr
@contextmanager
def suppress_stderr():
    # Save the original stderr
    old_stderr = sys.stderr
    # Redirect stderr to devnull
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        # Restore stderr
        sys.stderr.close()
        sys.stderr = old_stderr

try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    from rdkit import RDLogger
    # Disable RDKit logging as much as possible
    RDLogger.DisableLog('rdApp')
    RDLogger.DisableLog('rdKit')
    rdkit_available = True
except ImportError:
    rdkit_available = False

# Create a safe version of MolFromSmiles to suppress errors
def safe_mol_from_smiles(smiles):
    with suppress_stderr():
        try:
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            if mol is not None:
                try:
                    Chem.SanitizeMol(mol)
                except:
                    pass
            return mol
        except:
            return None

class ReagentInputForm:
    def __init__(self, data_file: str) -> None:
        """Initialize the form with a data file path."""
        self.data_file: str = data_file
        self.data: Dict[str, Any] = {"solid reagents": [], "liquid reagents": []}
        self.load_data()
        
        # Main UI components
        self.main_container = None
        self.tab_container = None  # New tabs container
        self.header_container = None
        self.form_area = None
        self.reagent_list = None
        self.current_form = None
        self.final_details_form = None  # Form for final details
        
        # Button references
        self.add_solid_button = None
        self.add_liquid_button = None
        self.submit_button = None
        
        # Tab references
        self.add_reagents_tab = None
        self.current_reagents_tab = None
        self.final_details_tab = None
        self.search_tab = None  # New search tab
        
        # Search components
        self.search_input = None
        self.search_results = None
        self.search_status = None
        
        # PubChem cache to avoid repeated API calls
        self.pubchem_cache = {}

    def load_data(self) -> None:
        """Load reagent data from JSON file."""
        try:
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"solid reagents": [], "liquid reagents": []}

    def save_data(self) -> None:
        """Save reagent data to JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def setup_ui(self) -> None:
        """Create the main UI structure with tabs."""
        # Create the tab container
        self.tab_container = widgets.Tab()
        
        # Create the add reagents tab content
        self.add_reagents_tab = self.create_add_reagents_tab()
        
        # Create the current reagents tab content
        self.current_reagents_tab = self.create_current_reagents_tab()
        
        # Create the final details tab content
        self.final_details_tab = self.create_final_details_tab()
        
        # Create the search tab content
        self.search_tab = self.create_search_tab()
        
        # Set the tab children and titles
        self.tab_container.children = [
            self.add_reagents_tab,
            self.current_reagents_tab,
            self.search_tab,
            self.final_details_tab
        ]
        self.tab_container.set_title(0, "Add Reagents")
        self.tab_container.set_title(1, "Current Reagents")
        self.tab_container.set_title(2, "Search Chemical")
        self.tab_container.set_title(3, "Final Details")
        
        # Main container now just includes the tabs
        self.main_container = widgets.VBox([
            widgets.HTML("<h3>Reagent Entry Form</h3>"),
            self.tab_container
        ])
        
        # Display the main container
        display(self.main_container)
        
        # Update the reagent list
        self.update_reagent_list()

    def create_add_reagents_tab(self) -> widgets.Widget:
        """Create the tab content for adding reagents with forms directly displayed."""
        # Create an accordion for organizing solid and liquid forms
        reagent_accordion = widgets.Accordion()
        
        # Create solid reagent form directly
        solid_form = self.create_reagent_form("solid")
        
        # Create liquid reagent form directly
        liquid_form = self.create_reagent_form("liquid")
        
        # Set accordion children and titles
        reagent_accordion.children = [solid_form, liquid_form]
        reagent_accordion.set_title(0, "Solid Reagent")
        reagent_accordion.set_title(1, "Liquid Reagent")
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Add New Reagents</h4>"),
            reagent_accordion
        ], layout=widgets.Layout(padding="10px"))
    
    def create_reagent_form(self, reagent_type: str, reagent: Optional[Dict[str, Any]] = None) -> widgets.Widget:
        """Create a form for adding or editing a reagent."""
        # Set background color based on reagent type
        bg_color = "#F0F7F4" if reagent_type == "solid" else "#EFF7FF"
        
        # Create form widgets
        form_title = widgets.HTML(
            f"<h4 style='color: {'#3F704D' if reagent_type == 'solid' else '#3A5D9F'};'>{'Edit' if reagent else 'Add'} {reagent_type.capitalize()} Reagent</h4>"
        )
        
        # Error message area
        error_area = widgets.HTML("")
        
        # Create input fields with validation styles
        name_input = widgets.Text(
            value=reagent["name"] if reagent else "",
            description="Name:",
            layout=widgets.Layout(width="80%")
        )
        name_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Required: Chemical name</span>"
        )
        
        inchi_input = widgets.Text(
            value=reagent["inChi"] if reagent else "",
            description="InChi:",
            layout=widgets.Layout(width="80%")
        )
        inchi_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Example: InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3</span>"
        )
        
        smiles_input = widgets.Text(
            value=reagent["SMILES"] if reagent else "",
            description="SMILES:",
            layout=widgets.Layout(width="80%")
        )
        smiles_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Example: CCO (ethanol)</span>"
        )
        
        inchikey_input = widgets.Text(
            value=reagent["inChi Key"] if reagent else "",
            description="InChi Key:",
            layout=widgets.Layout(width="80%")
        )
        inchikey_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Example: LFQSCWFLJHTTHZ-UHFFFAOYSA-N</span>"
        )
        
        mw_input = widgets.FloatText(
            value=reagent["molecular weight (in g/mol)"] if reagent else 0,
            description="MW (g/mol):",
            layout=widgets.Layout(width="80%")
        )
        mw_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Required: Must be > 0</span>"
        )
        
        eq_input = widgets.FloatText(
            value=reagent["eq"] if reagent else 0,
            description="Equivalents:",
            layout=widgets.Layout(width="80%")
        )
        eq_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Required: Must be > 0. Set to 1.0 for limiting reagent.</span>"
        )
        
        syringe_input = widgets.IntText(
            value=reagent["syringe"] if reagent else 0,
            description="Syringe:",
            layout=widgets.Layout(width="80%")
        )
        syringe_tooltip = widgets.HTML(
            "<span style='font-size: 0.8em; color: #666;'>Required: Must be > 0</span>"
        )
        
        # Add structure visualization area
        structure_area = widgets.Output(
            layout=widgets.Layout(
                height="200px",
                width="200px",
                margin="10px auto",
                border="1px solid #ddd"
            )
        )
        
        # Function to update structure visualization
        def update_structure(change=None):
            structure_area.clear_output()
            if not rdkit_available:
                with structure_area:
                    print("RDKit not available")
                return
                
            smiles = smiles_input.value
            if not smiles:
                return
                
            try:
                with structure_area:
                    # Use safe_mol_from_smiles to avoid error messages
                    mol = safe_mol_from_smiles(smiles)
                    if mol:
                        img = Draw.MolToImage(mol, size=(180, 180))
                        display(img)
                    else:
                        print("Could not render structure. Please check SMILES format.")
            except Exception:
                with structure_area:
                    print("Could not render structure. Please check SMILES format.")
        
        # Connect update to SMILES field
        smiles_input.observe(update_structure, names='value')
        
        # Add lookup button for structure
        lookup_button = widgets.Button(
            description="Lookup Structure",
            button_style="info",
            icon="search",
            layout=widgets.Layout(width="auto")
        )
        
        def on_lookup(b):
            if smiles_input.value:
                update_structure()
            elif name_input.value:
                # Try to lookup by name
                results = self.search_pubchem(name_input.value, 'name')
                if results:
                    compound = results[0]
                    smiles_input.value = compound['smiles']
                    inchi_input.value = compound['inchi']
                    inchikey_input.value = compound['inchikey']
                    mw_input.value = compound['molecular_weight']
                    update_structure()
        
        lookup_button.on_click(on_lookup)
        
        # Add density field for liquid reagents
        density_input = None
        density_tooltip = None
        form_fields = []
        
        if reagent_type == "liquid":
            density_input = widgets.FloatText(
                value=reagent["density (in g/mL)"] if reagent else 0,
                description="Density (g/mL):",
                layout=widgets.Layout(width="80%")
            )
            density_tooltip = widgets.HTML(
                "<span style='font-size: 0.8em; color: #666;'>Required for liquids: Must be > 0</span>"
            )
        
        # Create save button
        save_button = widgets.Button(
            description="Save Reagent",
            button_style="success",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#3F704D" if reagent_type == "solid" else "#3A5D9F"}
        )
        
        # Create form fields list with tooltips
        form_fields = [
            form_title,
            error_area,
            widgets.VBox([name_input, name_tooltip]),
            widgets.VBox([inchi_input, inchi_tooltip]),
            widgets.VBox([smiles_input, smiles_tooltip]),
            widgets.VBox([inchikey_input, inchikey_tooltip]),
            widgets.VBox([mw_input, mw_tooltip]),
            widgets.VBox([eq_input, eq_tooltip])
        ]
        
        if density_input and density_tooltip:
            form_fields.append(widgets.VBox([density_input, density_tooltip]))
            
        form_fields.append(widgets.VBox([syringe_input, syringe_tooltip]))
        
        # Add structure visualization
        form_fields.append(widgets.VBox([
            widgets.HTML("<h4>Structure Preview</h4>"),
            structure_area,
            lookup_button
        ], layout=widgets.Layout(
            align_items="center",
            border="1px solid #ddd",
            margin="10px 0",
            padding="10px"
        )))
        
        form_fields.append(widgets.HBox([save_button]))
        
        # Create form container with color coding
        form = widgets.VBox(
            form_fields,
            layout=widgets.Layout(
                border=f"1px solid {'#90BE6D' if reagent_type == 'solid' else '#577590'}",
                padding="15px",
                margin="10px 0",
                background_color=bg_color
            )
        )
        
        # Update structure if SMILES is available
        if smiles_input.value:
            update_structure()
        
        # Validation function
        def validate_and_save(b):
            # Collect form data
            new_reagent = {
                "name": name_input.value,
                "inChi": inchi_input.value,
                "SMILES": smiles_input.value,
                "inChi Key": inchikey_input.value,
                "molecular weight (in g/mol)": mw_input.value,
                "eq": eq_input.value,
                "syringe": syringe_input.value
            }
            
            # Add density for liquid reagents
            if reagent_type == "liquid" and density_input:
                new_reagent["density (in g/mL)"] = density_input.value
            
            # Validate data
            validation_errors = self.validate_reagent(new_reagent, reagent_type)
            
            # Reset error displays
            error_area.value = ""
            
            # If errors, show them
            if validation_errors:
                error_html = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'>"
                error_html += "<b>Please correct the following errors:</b><ul>"
                for field, message in validation_errors.items():
                    error_html += f"<li>{message}</li>"
                error_html += "</ul></div>"
                error_area.value = error_html
                return
            
            # Update data structure
            key = f"{reagent_type} reagents"
            if reagent:
                self.data[key].remove(reagent)
            self.data[key].append(new_reagent)
            
            # Save to file
            self.save_data()
            
            # Show success message
            error_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px; margin-bottom: 10px;'><b>Reagent saved successfully!</b></div>"
            
            # Clear the form inputs for next entry
            name_input.value = ""
            inchi_input.value = ""
            smiles_input.value = ""
            inchikey_input.value = ""
            mw_input.value = 0
            eq_input.value = 0
            syringe_input.value = 0
            if density_input:
                density_input.value = 0
            
            # Update the reagent list
            self.update_reagent_list()
            
            # Switch to Current Reagents tab to show the new reagent
            self.tab_container.selected_index = 1
        
        # Set up button callback
        save_button.on_click(validate_and_save)
        
        return form

    def create_current_reagents_tab(self) -> widgets.Widget:
        """Create the tab content for viewing current reagents."""
        # Create reagent list container
        self.reagent_list = widgets.VBox(
            layout=widgets.Layout(
                margin="10px 0 10px 0",
                border="1px solid #ddd",
                padding="10px",
                min_height="100px"
            )
        )
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Current Reagents</h4>"),
            self.reagent_list
        ], layout=widgets.Layout(padding="10px"))
    
    def create_final_details_tab(self) -> widgets.Widget:
        """Create the tab content for entering final details with form directly displayed."""
        # Get existing values if any
        mass_scale_value = self.data.get("mass scale (in mg)", None)
        concentration_value = self.data.get("concentration (in mM)", None)
        solvent_value = self.data.get("solvent", "")
        
        # Create form widgets
        form_title = widgets.HTML("<h4>Final Details</h4>")
        
        mass_scale_input = widgets.FloatText(
            value=mass_scale_value,
            description="Mass scale (mg):",
            layout=widgets.Layout(width="80%")
        )
        
        concentration_input = widgets.FloatText(
            value=concentration_value,
            description="Concentration (mM):",
            layout=widgets.Layout(width="80%")
        )
        
        solvent_input = widgets.Text(
            value=solvent_value,
            description="Solvents:",
            layout=widgets.Layout(width="80%")
        )
        
        submit_button = widgets.Button(
            description="Process Data",
            button_style="success",
            layout=widgets.Layout(width="auto")
        )
        
        # Error/message display area
        message_area = widgets.HTML("")
        
        # Create form container
        form = widgets.VBox(
            [
                form_title,
                message_area,
                mass_scale_input,
                concentration_input,
                solvent_input,
                submit_button
            ],
            layout=widgets.Layout(
                border="1px solid #ddd",
                padding="10px",
                margin="10px 0"
            )
        )
        
        # Set up button callback
        def submit_handler(b):
            try:
                # Update data with form values
                self.data["mass scale (in mg)"] = mass_scale_input.value
                self.data["concentration (in mM)"] = concentration_input.value
                self.data["solvent"] = solvent_input.value
                
                # Validate that at least one reagent has eq=1.0
                if not any(
                    abs(reagent["eq"] - 1.0) < 1e-6
                    for reagent in self.data["solid reagents"] + self.data["liquid reagents"]
                ):
                    raise ValueError("At least one reagent must have an equivalent (eq) value of 1.0")
                
                # Save data
                self.save_data()
                
                # Remove the form widgets first
                self.main_container.layout.display = 'none'
                
                # Process data without relying on clear_output
                import IPython.display as display
                import time
                
                # Force a complete reset of output
                display.clear_output(wait=True)
                display.display(display.HTML("<h3>Processing Data:</h3>"))
                
                # Small delay to ensure file operations complete
                time.sleep(0.5)
                
                # Force reload from disk to get fresh data
                with open(self.data_file, "r") as f:
                    fresh_data = json.load(f)
                
                # Process the fresh data to ensure the table shows the latest information
                from importlib import reload
                from mechwolf.DataEntry.Reagents import ProcessData
                reload(ProcessData)  # Reload the module to avoid any caching issues
                ProcessData.process_data(self.data_file)
                
            except ValueError as e:
                # Display error message
                message_area.value = f"<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Error: {str(e)}</p>"
        
        submit_button.on_click(submit_handler)
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Final Details and Submission</h4>"),
            form
        ], layout=widgets.Layout(padding="10px"))

    def create_search_tab(self) -> widgets.Widget:
        """Create the tab content for searching chemicals from PubChem."""
        # Create search input area
        self.search_input = widgets.Text(
            placeholder="Enter chemical name, SMILES, InChI, or CAS",
            description="Search:",
            layout=widgets.Layout(width="80%")
        )
        
        search_type = widgets.Dropdown(
            options=['Name', 'SMILES', 'InChI', 'InChI Key', 'CAS'],
            value='Name',
            description='Search by:',
            layout=widgets.Layout(width="50%")
        )
        
        search_button = widgets.Button(
            description="Search PubChem",
            button_style="info",
            icon="search"
        )
        
        # Create status area
        self.search_status = widgets.HTML("")
        
        # Create results area
        self.search_results = widgets.VBox([])
        
        # Set up search button callback
        def on_search_click(b):
            query = self.search_input.value.strip()
            if not query:
                self.search_status.value = "<p style='color: orange;'>Please enter a search term</p>"
                return
                
            self.search_status.value = "<p style='color: blue;'>Searching PubChem...</p>"
            self.search_results.children = ()
            
            # Perform the search
            results = self.search_pubchem(query, search_type.value.lower())
            
            if not results:
                self.search_status.value = "<p style='color: red;'>No results found</p>"
                return
                
            self.search_status.value = f"<p style='color: green;'>Found {len(results)} results</p>"
            
            # Create result widgets
            result_widgets = []
            for compound in results:
                result_widgets.append(self.create_search_result_widget(compound))
                
            self.search_results.children = tuple(result_widgets)
            
        search_button.on_click(on_search_click)
        
        # Input area arrangement
        input_area = widgets.VBox([
            widgets.HBox([self.search_input, search_type]), 
            search_button,
            self.search_status
        ], layout=widgets.Layout(margin="10px 0"))
        
        # Results area with scrolling
        results_container = widgets.VBox([
            widgets.HTML("<h4>Search Results</h4>"),
            self.search_results
        ], layout=widgets.Layout(
            border="1px solid #ddd",
            padding="10px",
            margin="10px 0",
            max_height="500px",
            overflow_y="auto"
        ))
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Search Chemical Databases</h4>"),
            input_area,
            results_container
        ], layout=widgets.Layout(padding="10px"))
    
    def search_pubchem(self, query: str, search_type: str) -> List[Dict[str, Any]]:
        """Search PubChem database and return results."""
        base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        
        # Check if result is in cache
        cache_key = f"{search_type}:{query}"
        if cache_key in self.pubchem_cache:
            return self.pubchem_cache[cache_key]
        
        try:
            # Validate input before sending to PubChem
            if search_type == 'smiles' and not validate_smiles(query):
                # Silently fail instead of printing
                return []
            
            # Map search type to PubChem's input types
            input_type = {
                'name': 'name',
                'smiles': 'smiles',
                'inchi': 'inchi',
                'inchi key': 'inchikey',
                'cas': 'xref/rn'
            }.get(search_type, 'name')
            
            # Different endpoint based on search type
            if input_type.startswith('xref'):
                parts = input_type.split('/')
                url = f"{base_url}/{parts[0]}/{parts[1]}/{query}/cids/JSON"
            else:
                url = f"{base_url}/compound/{input_type}/{query}/cids/JSON"
            
            # Get compound IDs with timeout and error handling
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'IdentifierList' not in data:
                return []
                
            cids = data['IdentifierList']['CID'][:5]  # Limit to first 5 results
            
            # Get compound data for each CID
            results = []
            for cid in cids:
                # Get properties
                prop_url = f"{base_url}/compound/cid/{cid}/property/IUPACName,MolecularFormula,MolecularWeight,InChI,InChIKey,CanonicalSMILES/JSON"
                prop_response = requests.get(prop_url, timeout=10)
                prop_response.raise_for_status()
                
                props = prop_response.json()['PropertyTable']['Properties'][0]
                
                # Validate SMILES before including in result
                smiles = props.get('CanonicalSMILES', '')
                if rdkit_available and smiles:
                    # Use safe mol creation that doesn't print errors
                    with suppress_stderr():
                        if not safe_mol_from_smiles(smiles):
                            smiles = ''  # Invalid SMILES, clear it
                
                # Create result object
                compound = {
                    'cid': cid,
                    'name': props.get('IUPACName', ''),
                    'formula': props.get('MolecularFormula', ''),
                    'molecular_weight': float(props.get('MolecularWeight', 0)),
                    'inchi': props.get('InChI', ''),
                    'inchikey': props.get('InChIKey', ''),
                    'smiles': smiles
                }
                
                results.append(compound)
            
            # Cache results
            self.pubchem_cache[cache_key] = results
            return results
            
        except requests.exceptions.Timeout:
            print("PubChem search timed out. Please try again later.")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Network error during PubChem search: {e}")
            return []
        except Exception as e:
            print(f"PubChem search error: {e}")
            return []

    def create_search_result_widget(self, compound: Dict[str, Any]) -> widgets.Widget:
        """Create a widget to display a search result with import button."""
        # Generate structure image if RDKit is available
        structure_img = None
        if rdkit_available and compound['smiles']:
            try:
                # Use safe_mol_from_smiles to avoid error messages
                mol = safe_mol_from_smiles(compound['smiles'])
                if mol:
                    img = Draw.MolToImage(mol, size=(150, 150))
                    
                    # Convert PIL image to widget
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    
                    structure_img = widgets.Image(
                        value=buffer.getvalue(),
                        format='png',
                        width=150,
                        height=150
                    )
            except Exception:
                # Silently fail without error messages
                pass
        
        # Create info widget
        info_html = f"""
        <div style="padding-left: 10px;">
            <h4>{compound['name'] or 'Unknown'}</h4>
            <p><b>Formula:</b> {compound['formula']}</p>
            <p><b>Molecular Weight:</b> {compound['molecular_weight']} g/mol</p>
            <p><b>InChI Key:</b> {compound['inchikey']}</p>
            <p><b>SMILES:</b> {compound['smiles']}</p>
        </div>
        """
        
        info_widget = widgets.HTML(info_html)
        
        # Create import buttons
        import_solid_button = widgets.Button(
            description="Import as Solid",
            button_style="success",
            style={"button_color": "#3F704D"}
        )
        
        import_liquid_button = widgets.Button(
            description="Import as Liquid",
            button_style="info",
            style={"button_color": "#3A5D9F"}
        )
        
        # Import button callbacks
        def import_as_solid(b):
            self.import_from_pubchem(compound, "solid")
            
        def import_as_liquid(b):
            self.import_from_pubchem(compound, "liquid")
            
        import_solid_button.on_click(import_as_solid)
        import_liquid_button.on_click(import_as_liquid)
        
        # Arrange buttons
        buttons = widgets.VBox([
            import_solid_button,
            import_liquid_button
        ])
        
        # Create result container with structure + info + buttons
        if structure_img:
            result = widgets.HBox([
                structure_img,
                info_widget,
                buttons
            ])
        else:
            result = widgets.HBox([
                info_widget,
                buttons
            ])
        
        return widgets.VBox([
            result,
            widgets.HTML("<hr style='margin: 10px 0;'>")
        ], layout=widgets.Layout(margin="5px 0"))
    
    def import_from_pubchem(self, compound: Dict[str, Any], reagent_type: str) -> None:
        """Import PubChem data into a new reagent form."""
        # Switch to Add Reagents tab
        self.tab_container.selected_index = 0
        
        # Select the appropriate accordion section
        accordion_index = 0 if reagent_type == "solid" else 1
        accordion = self.add_reagents_tab.children[1]  # Get the accordion widget
        accordion.selected_index = accordion_index
        
        # Get the form
        form = accordion.children[accordion_index]
        
        # Find the input widgets within the form
        for child in form.children:
            if isinstance(child, widgets.VBox):
                for input_child in child.children:
                    if isinstance(input_child, widgets.Text) or isinstance(input_child, widgets.FloatText):
                        # Set values based on input description
                        if hasattr(input_child, 'description'):
                            if input_child.description == "Name:":
                                input_child.value = compound['name']
                            elif input_child.description == "InChi:":
                                input_child.value = compound['inchi']
                            elif input_child.description == "SMILES:":
                                input_child.value = compound['smiles']
                            elif input_child.description == "InChi Key:":
                                input_child.value = compound['inchikey']
                            elif input_child.description == "MW (g/mol):":
                                input_child.value = compound['molecular_weight']
                            # Default equivalents to 1.0 for convenience
                            elif input_child.description == "Equivalents:":
                                input_child.value = 1.0
        
        # Display success message
        self.search_status.value = f"<p style='color: green;'>Data imported as {reagent_type}. Please complete any remaining fields.</p>"

    def update_reagent_list(self) -> None:
        """Update the display of reagent items with grouped and styled items."""
        items = []
        
        # Create heading for solid reagents if any exist
        if self.data["solid reagents"]:
            items.append(widgets.HTML(
                "<h3 style='color: #3F704D; margin: 10px 0 5px 0; border-bottom: 2px solid #90BE6D;'>Solid Reagents</h3>"
            ))
            for reagent in self.data["solid reagents"]:
                items.append(self.create_reagent_item(reagent))
        
        # Create heading for liquid reagents if any exist
        if self.data["liquid reagents"]:
            items.append(widgets.HTML(
                "<h3 style='color: #3A5D9F; margin: 15px 0 5px 0; border-bottom: 2px solid #577590;'>Liquid Reagents</h3>"
            ))
            for reagent in self.data["liquid reagents"]:
                items.append(self.create_reagent_item(reagent))
        
        # If no reagents, show a message
        if not items:
            items.append(widgets.HTML(
                "<div style='text-align: center; padding: 20px; color: #666; font-style: italic;'>"
                "No reagents added yet. Go to the 'Add Reagents' tab to add reagents."
                "</div>"
            ))
        
        # Update the reagent list with the items
        self.reagent_list.children = tuple(items)

    def create_reagent_item(self, reagent: Dict[str, Any]) -> widgets.Widget:
        """Create a widget to display a reagent with edit/delete buttons."""
        # Create a more detailed display with grouping by color
        is_solid = reagent in self.data["solid reagents"]
        bg_color = "#F0F7F4" if is_solid else "#EFF7FF"  # Light green for solids, light blue for liquids
        
        # Create structure visualization if possible
        structure_widget = None
        if rdkit_available and reagent["SMILES"]:
            try:
                # Use safe_mol_from_smiles function to avoid error messages
                smiles = reagent["SMILES"]
                mol = safe_mol_from_smiles(smiles)
                if mol:
                    img = Draw.MolToImage(mol, size=(120, 120))
                    
                    # Convert PIL image to widget
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    
                    structure_widget = widgets.Image(
                        value=buffer.getvalue(),
                        format='png',
                        width=120,
                        height=120
                    )
            except Exception:
                # Silently fail without error messages
                pass
        
        # Style for reagent item
        item_style = f"""
        <div style="padding: 8px; background-color: {bg_color}; border-radius: 4px; margin-bottom: 4px;">
            <h4 style="margin: 0 0 5px 0;">{reagent['name']}</h4>
            <div style="display: flex; flex-direction: row;">
                <div style="flex: 1;">
                    <p style="margin: 2px 0;"><b>Eq:</b> {reagent['eq']}</p>
                    <p style="margin: 2px 0;"><b>MW:</b> {reagent['molecular weight (in g/mol)']} g/mol</p>
                </div>
                <div style="flex: 1;">
                    <p style="margin: 2px 0;"><b>Syringe:</b> {reagent['syringe']}</p>
                    {f'<p style="margin: 2px 0;"><b>Density:</b> {reagent.get("density (in g/mL)", "N/A")} g/mL</p>' if not is_solid else ''}
                </div>
            </div>
        </div>
        """
        
        # HTML widget for the reagent details
        html_widget = widgets.HTML(item_style)
        
        # Create buttons
        edit_button = widgets.Button(
            description="Edit",
            button_style="info",
            layout=widgets.Layout(width="60px"),
            style={"button_color": "#1E3A8A"}
        )
        
        delete_button = widgets.Button(
            description="Delete",
            button_style="danger",
            layout=widgets.Layout(width="70px"),
            style={"button_color": "#D72638"}
        )
        
        # Setup callbacks with proper closure for reagent
        edit_button.on_click(lambda b, r=reagent: self.edit_reagent(r))
        delete_button.on_click(lambda b, r=reagent: self.delete_reagent(r))
        
        # Container for buttons
        button_container = widgets.VBox(
            [edit_button, delete_button],
            layout=widgets.Layout(margin="0 0 0 10px", align_items="flex-start")
        )
        
        # Return an HBox containing the structure, HTML and buttons
        if structure_widget:
            return widgets.HBox(
                [structure_widget, html_widget, button_container],
                layout=widgets.Layout(
                    margin="2px 0",
                    align_items="center",
                    border=f"1px solid {'#90BE6D' if is_solid else '#577590'}",
                    border_radius="5px",
                    padding="5px"
                )
            )
        else:
            return widgets.HBox(
                [html_widget, button_container],
                layout=widgets.Layout(
                    margin="2px 0",
                    align_items="center",
                    border=f"1px solid {'#90BE6D' if is_solid else '#577590'}",
                    border_radius="5px",
                    padding="5px"
                )
            )

    def validate_reagent(self, data: Dict[str, Any], reagent_type: str) -> Dict[str, str]:
        """Validate reagent data and return a dictionary of errors."""
        errors = {}
        
        # Name validation
        if not data["name"] or data["name"].strip() == "":
            errors["name"] = "Name is required"
        
        # Equivalents validation
        if data["eq"] <= 0:
            errors["eq"] = "Equivalents must be greater than 0"
            
        # Molecular weight validation
        if data["molecular weight (in g/mol)"] <= 0:
            errors["mw"] = "Molecular weight must be greater than 0"
        
        # Density validation for liquids
        if reagent_type == "liquid" and data.get("density (in g/mL)", 0) <= 0:
            errors["density"] = "Density must be greater than 0"
        
        # Syringe validation - must be an integer > 0
        if data["syringe"] <= 0:
            errors["syringe"] = "Syringe must be greater than 0"
        
        return errors

    def update_submit_button(self) -> None:
        """Show or hide the submit button based on whether reagents exist."""
        has_reagents = bool(self.data["solid reagents"] or self.data["liquid reagents"])
        
        # Get the current buttons from the header
        current_buttons = list(self.header_container.children[0].children)
        
        # Check if submit button should be added or removed
        if has_reagents and self.submit_button not in current_buttons:
            current_buttons.append(self.submit_button)
            self.header_container.children[0].children = tuple(current_buttons)
        elif not has_reagents and self.submit_button in current_buttons:
            current_buttons.remove(self.submit_button)
            self.header_container.children[0].children = tuple(current_buttons)

    def delete_reagent(self, reagent: Dict[str, Any]) -> None:
        """Remove a reagent from the data."""
        if reagent in self.data["solid reagents"]:
            self.data["solid reagents"].remove(reagent)
        elif reagent in self.data["liquid reagents"]:
            self.data["liquid reagents"].remove(reagent)
        
        # Update the display
        self.update_reagent_list()

    def edit_reagent(self, reagent: Dict[str, Any]) -> None:
        """Open the form to edit an existing reagent."""
        # Determine reagent type
        reagent_type = "solid" if reagent in self.data["solid reagents"] else "liquid"
        
        # Switch to the Add Reagents tab
        self.tab_container.selected_index = 0
        
        # Select the appropriate accordion section
        accordion_index = 0 if reagent_type == "solid" else 1
        accordion = self.add_reagents_tab.children[1]  # Get the accordion widget
        accordion.selected_index = accordion_index
        
        # Get the form
        form = accordion.children[accordion_index]
        
        # Find and update the input widgets within the form
        for child in form.children:
            if isinstance(child, widgets.VBox):
                for input_child in child.children:
                    if isinstance(input_child, widgets.Text) or isinstance(input_child, widgets.FloatText) or isinstance(input_child, widgets.IntText):
                        # Set values based on input description
                        if hasattr(input_child, 'description'):
                            if input_child.description == "Name:":
                                input_child.value = reagent['name']
                            elif input_child.description == "InChi:":
                                input_child.value = reagent['inChi']
                            elif input_child.description == "SMILES:":
                                input_child.value = reagent['SMILES']
                            elif input_child.description == "InChi Key:":
                                input_child.value = reagent['inChi Key']
                            elif input_child.description == "MW (g/mol):":
                                input_child.value = reagent['molecular weight (in g/mol)']
                            elif input_child.description == "Equivalents:":
                                input_child.value = reagent['eq']
                            elif input_child.description == "Syringe:":
                                input_child.value = reagent['syringe']
                            elif input_child.description == "Density (g/mL):" and reagent_type == "liquid":
                                input_child.value = reagent['density (in g/mL)']

    def clear_form_area(self) -> None:
        """Clear any forms from the form area."""
        self.form_area.children = ()
        self.current_form = None

    def run(self) -> None:
        """Run the application."""
        # If there's no data, create the widgets
        if not self.data["solid reagents"] and not self.data["liquid reagents"]:
            self.setup_ui()
        else:
            # First show the current data as a table
            from mechwolf.DataEntry.Reagents import ProcessData
            ProcessData.process_data(self.data_file)
            
            # Then ask if user wants to edit or proceed
            display(widgets.HTML("<h3>What would you like to do with this data?</h3>"))
            edit_btn = widgets.Button(
                description="Edit Data", 
                button_style="info",
                style={"button_color": "#3A5D9F"}
            )
            continue_btn = widgets.Button(
                description="Continue without editing", 
                button_style="success",
                style={"button_color": "#3F704D"}
            )
            
            def on_edit(b):
                clear_output(wait=True)
                self.setup_ui()
            
            def on_continue(b):
                # User chooses to use data as is
                pass  # You can add additional actions if needed
                
            edit_btn.on_click(on_edit)
            continue_btn.on_click(on_continue)
            
            display(widgets.HBox([edit_btn, continue_btn], 
                                layout=widgets.Layout(margin="20px 0")))

if __name__ == "__main__":
    data_file = input("Enter the JSON file name: ").strip()
    app = ReagentInputForm(data_file)
    app.run()
