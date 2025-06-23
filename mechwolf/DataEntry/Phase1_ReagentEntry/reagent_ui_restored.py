"""
Original ReagentUI Interface with Modern Backend

This is the restored original ReagentUI with the excellent tabbed interface,
now using the modern experimental_metadata system for data persistence.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, Optional, List, Callable
import traceback

# Import the components we've already created
from .data_adapter import ReagentDataAdapter
from .pubchem_service import PubChemService
from .structure_visualization import StructureVisualization
from .ui_components import UIComponents
from .reagent_utils import validate_reagent_data

# Import the original form handlers but we'll recreate them here for integration
class ReagentFormHandler:
    """Handler for reagent entry forms - restored original version"""
    
    @staticmethod
    def create_form_field(widget: widgets.Widget, tooltip_text: str, error_style: bool = False) -> widgets.VBox:
        """Create a form field with tooltip"""
        tooltip_color = "red" if error_style else "#666"
        tooltip_weight = "bold" if error_style else "normal"
        
        tooltip = widgets.HTML(
            f"<span style='font-size: 0.8em; color: {tooltip_color}; font-weight: {tooltip_weight};'>{tooltip_text}</span>"
        )
        
        if error_style:
            widget.layout.border = "2px solid red"
        else:
            widget.layout.border = ""
            
        return widgets.VBox([widget, tooltip])
    
    @staticmethod
    def create_reagent_form(reagent_type: str, reagent: Optional[Dict[str, Any]] = None,
                           on_save: Callable = None, warning_message: str = None) -> widgets.Widget:
        """Create a form for adding or editing a reagent"""
        
        # Set background color based on reagent type
        bg_color = "#F0F7F4" if reagent_type == "solid" else "#EFF7FF"
        
        # Create form widgets
        form_title = widgets.HTML(
            f"<h4 style='color: {'#3F704D' if reagent_type == 'solid' else '#3A5D9F'};'>"
            f"{'Edit' if reagent else 'Add'} {reagent_type.capitalize()} Reagent</h4>"
        )
        
        # Error message area
        error_area = widgets.HTML("")
        
        # Warning message area (if provided)
        warning_area = widgets.HTML("")
        if warning_message and reagent_type == "liquid":
            warning_area.value = f"""
            <div style='color: red; font-weight: bold; background-color: #FFEEEE; 
                        padding: 8px; margin: 10px 0; border-radius: 4px; 
                        border: 1px solid #FFD2D2;'>
              Warning: {warning_message}
            </div>
            """
        
        # Create input fields
        name_input = widgets.Text(
            value=reagent.get("name", "") if reagent else "",
            description="Name:",
            layout=widgets.Layout(width="80%")
        )
        
        inchi_input = widgets.Text(
            value=reagent.get("inChi", "") if reagent else "",
            description="InChi:",
            layout=widgets.Layout(width="80%")
        )
        
        smiles_input = widgets.Text(
            value=reagent.get("SMILES", "") if reagent else "",
            description="SMILES:",
            layout=widgets.Layout(width="80%")
        )
        
        inchikey_input = widgets.Text(
            value=reagent.get("inChi Key", "") if reagent else "",
            description="InChi Key:",
            layout=widgets.Layout(width="80%")
        )
        
        mw_input = widgets.FloatText(
            value=reagent.get("molecular weight (in g/mol)", 0) if reagent else 0,
            description="MW (g/mol):",
            layout=widgets.Layout(width="80%")
        )
        
        eq_input = widgets.FloatText(
            value=reagent.get("eq", 0) if reagent else 0,
            description="Equivalents:",
            layout=widgets.Layout(width="80%")
        )
        
        syringe_input = widgets.IntText(
            value=reagent.get("syringe", 0) if reagent else 0,
            description="Syringe:",
            layout=widgets.Layout(width="80%")
        )
        
        # Create form fields with tooltips
        form_fields = [
            form_title,
            error_area
        ]
        
        # Add warning area if there's a warning message
        if warning_message and reagent_type == "liquid":
            form_fields.append(warning_area)
            
        # Add standard form fields with tooltips
        form_fields.extend([
            ReagentFormHandler.create_form_field(
                name_input, "Required: Chemical name"),
            ReagentFormHandler.create_form_field(
                inchi_input, "Example: InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"),
            ReagentFormHandler.create_form_field(
                smiles_input, "Example: CCO (ethanol)"),
            ReagentFormHandler.create_form_field(
                inchikey_input, "Example: LFQSCWFLJHTTHZ-UHFFFAOYSA-N"),
            ReagentFormHandler.create_form_field(
                mw_input, "Required: Must be > 0"),
            ReagentFormHandler.create_form_field(
                eq_input, "Required: Must be > 0. Set to 1.0 for limiting reagent."),
            ReagentFormHandler.create_form_field(
                syringe_input, "Required: Must be > 0")
        ])
        
        # Add density field for liquid reagents
        density_input = None
        if reagent_type == "liquid":
            density_input = widgets.FloatText(
                value=reagent.get("density (in g/mL)", 0) if reagent else 0,
                description="Density (g/mL):",
                layout=widgets.Layout(width="80%")
            )
            
            density_tooltip = "Required for liquids: Please update this value!" if warning_message else "Required for liquids: Must be > 0"
            form_fields.append(
                ReagentFormHandler.create_form_field(
                    density_input, density_tooltip, error_style=bool(warning_message)
                )
            )
        
        # Add structure visualization area
        structure_area = widgets.Output(
            layout=widgets.Layout(width="200px", height="200px")
        )
        
        # Function to update structure visualization
        def update_structure(change=None):
            structure_area.clear_output()
            with structure_area:
                if smiles_input.value:
                    vis = StructureVisualization.get_structure_image(smiles_input.value, size=(200, 200))
                    if vis:
                        display(vis)
                    else:
                        print("Could not render structure.\\nCheck SMILES format.")
        
        # Connect update to SMILES field
        smiles_input.observe(update_structure, names='value')
        
        # Add structure visualization
        form_fields.append(widgets.VBox([
            widgets.HTML("<h4>Structure Preview</h4>"),
            structure_area
        ], layout=widgets.Layout(
            align_items="center",
            border="1px solid #ddd",
            margin="10px 0",
            padding="10px"
        )))
        
        # Create save button
        save_button = widgets.Button(
            description="Save Reagent",
            button_style="success",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#3F704D" if reagent_type == "solid" else "#3A5D9F"}
        )
        
        form_fields.append(save_button)
        
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
        if reagent and smiles_input.value:
            update_structure()
        
        # Set up callback for save button
        if on_save:
            def validate_and_save(b):
                # Collect form data
                inchi_value = inchi_input.value
                if inchi_value and inchi_value.startswith("InChI="):
                    inchi_value = inchi_value[6:]  # Remove 'InChI=' prefix
                
                new_reagent = {
                    "name": name_input.value,
                    "inChi": inchi_value,
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
                validation_errors = validate_reagent_data(new_reagent, reagent_type)
                
                # Reset error displays
                error_area.value = ""
                
                # If errors, show them
                if validation_errors:
                    error_html = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'>"
                    error_html += "<b>Please correct the following errors:</b><ul>"
                    for error in validation_errors:
                        error_html += f"<li>{error}</li>"
                    error_html += "</ul></div>"
                    error_area.value = error_html
                    return
                
                try:
                    # Clear any existing error message
                    error_area.value = ""
                    
                    # Call the save callback with the new reagent and old reagent (if editing)
                    success = on_save(new_reagent, reagent)
                    
                    if success:
                        # Show success message
                        error_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px; margin-bottom: 10px;'><b>Reagent saved successfully!</b></div>"
                        
                        # Clear form only for new entries (not editing)
                        if not reagent:
                            name_input.value = ""
                            inchi_input.value = ""
                            smiles_input.value = ""
                            inchikey_input.value = ""
                            mw_input.value = 0
                            eq_input.value = 0
                            syringe_input.value = 0
                            if density_input:
                                density_input.value = 0
                    else:
                        error_area.value = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'><b>Failed to save reagent. Check console for errors.</b></div>"
                except Exception as e:
                    error_area.value = f"<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'><b>Error: {str(e)}</b></div>"
                    import traceback
                    traceback.print_exc()
            
            save_button.on_click(validate_and_save)
        
        return form


class ReagentUI:
    """
    Original ReagentUI with tabbed interface and modern backend
    
    This class provides the exact same interface as the original ReagentUI
    but uses the experimental_metadata system for data persistence.
    """
    
    def __init__(self, experiment_manager):
        """
        Initialize ReagentUI with experiment manager
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        self.data_manager = ReagentDataAdapter(experiment_manager)
        self.pubchem_service = PubChemService()
        
        # Initialize UI state
        self.current_editing_reagent = None
        self.search_results = []
        
        # Store form widget references for import functionality
        self.solid_form_widgets = {}
        self.liquid_form_widgets = {}
        
        # Create the tabbed interface
        self._create_interface()
    
    def _create_interface(self):
        """Create the main tabbed interface"""
        
        # Create tabs
        self.solid_tab = self._create_solid_reagent_tab()
        self.liquid_tab = self._create_liquid_reagent_tab()
        self.search_tab = self._create_pubchem_search_tab()
        self.display_tab = self._create_reagents_display_tab()
        self.final_tab = self._create_final_details_tab()
        
        # Create tab widget
        self.tab_widget = widgets.Tab()
        self.tab_widget.children = [
            self.solid_tab,
            self.liquid_tab,
            self.search_tab,
            self.display_tab,
            self.final_tab
        ]
        
        # Set tab titles
        self.tab_widget.set_title(0, "🧱 Solid Reagents")
        self.tab_widget.set_title(1, "💧 Liquid Reagents")
        self.tab_widget.set_title(2, "🔍 PubChem Search")
        self.tab_widget.set_title(3, "📋 Current Reagents")
        self.tab_widget.set_title(4, "⚗️ Final Details")
        
        # Create main container
        header = widgets.HTML("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🧪 ReagentUI - Phase 1: Reagent Entry</h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0;'>
                Original interface with modern experimental metadata backend
            </p>
        </div>
        """)
        
        self.main_widget = widgets.VBox([
            header,
            self.tab_widget
        ])
    
    def _create_solid_reagent_tab(self):
        """Create the solid reagent entry tab"""
        form, form_widgets = self._create_enhanced_reagent_form(
            "solid",
            on_save=self._save_solid_reagent
        )
        
        # Store widget references for import functionality
        self.solid_form_widgets = form_widgets
        
        return widgets.VBox([
            widgets.HTML("<p>Add solid reagents (powders, crystals, etc.)</p>"),
            form
        ])
    
    def _create_liquid_reagent_tab(self):
        """Create the liquid reagent entry tab"""
        form, form_widgets = self._create_enhanced_reagent_form(
            "liquid",
            on_save=self._save_liquid_reagent
        )
        
        # Store widget references for import functionality
        self.liquid_form_widgets = form_widgets
        
        return widgets.VBox([
            widgets.HTML("<p>Add liquid reagents (solutions, solvents, etc.)</p>"),
            form
        ])
    
    def _create_enhanced_reagent_form(self, reagent_type: str, on_save):
        """Create an enhanced reagent form that returns both form and widget references"""
        
        # Create form widgets with references
        name_input = widgets.Text(
            description="Name:",
            layout=widgets.Layout(width="80%")
        )
        
        inchi_input = widgets.Text(
            description="InChi:",
            layout=widgets.Layout(width="80%")
        )
        
        smiles_input = widgets.Text(
            description="SMILES:",
            layout=widgets.Layout(width="80%")
        )
        
        inchikey_input = widgets.Text(
            description="InChi Key:",
            layout=widgets.Layout(width="80%")
        )
        
        mw_input = widgets.FloatText(
            description="MW (g/mol):",
            layout=widgets.Layout(width="80%")
        )
        
        eq_input = widgets.FloatText(
            description="Equivalents:",
            value=1.0,
            layout=widgets.Layout(width="80%")
        )
        
        syringe_input = widgets.IntText(
            description="Syringe:",
            value=1,
            layout=widgets.Layout(width="80%")
        )
        
        # Store widget references
        form_widgets = {
            'name': name_input,
            'inchi': inchi_input,
            'smiles': smiles_input,
            'inchikey': inchikey_input,
            'mw': mw_input,
            'eq': eq_input,
            'syringe': syringe_input
        }
        
        # Add density for liquid reagents
        density_input = None
        if reagent_type == "liquid":
            density_input = widgets.FloatText(
                description="Density (g/mL):",
                value=1.0,
                layout=widgets.Layout(width="80%")
            )
            form_widgets['density'] = density_input
        
        # Create structure visualization area
        structure_area = widgets.Output(
            layout=widgets.Layout(width="200px", height="200px")
        )
        
        # Function to update structure visualization
        def update_structure(change=None):
            structure_area.clear_output()
            with structure_area:
                if smiles_input.value:
                    vis = StructureVisualization.get_structure_image(smiles_input.value, size=(200, 200))
                    if vis:
                        display(vis)
                    else:
                        print("Could not render structure.\\nCheck SMILES format.")
        
        # Connect update to SMILES field
        smiles_input.observe(update_structure, names='value')
        
        # Create save button
        save_button = widgets.Button(
            description="Save Reagent",
            button_style="success",
            layout=widgets.Layout(width="auto")
        )
        
        # Error/status area
        status_area = widgets.HTML("")
        form_widgets['status'] = status_area
        
        # Create form layout
        form_fields = [
            widgets.HTML(f"<h4>Add {reagent_type.capitalize()} Reagent</h4>"),
            status_area,
            ReagentFormHandler.create_form_field(name_input, "Required: Chemical name"),
            ReagentFormHandler.create_form_field(inchi_input, "Example: InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"),
            ReagentFormHandler.create_form_field(smiles_input, "Example: CCO (ethanol)"),
            ReagentFormHandler.create_form_field(inchikey_input, "Example: LFQSCWFLJHTTHZ-UHFFFAOYSA-N"),
            ReagentFormHandler.create_form_field(mw_input, "Required: Must be > 0"),
            ReagentFormHandler.create_form_field(eq_input, "Required: Must be > 0. Set to 1.0 for limiting reagent."),
            ReagentFormHandler.create_form_field(syringe_input, "Required: Must be > 0")
        ]
        
        if density_input:
            form_fields.append(
                ReagentFormHandler.create_form_field(density_input, "Required for liquids: Must be > 0")
            )
        
        # Add structure visualization
        form_fields.append(widgets.VBox([
            widgets.HTML("<h4>Structure Preview</h4>"),
            structure_area
        ], layout=widgets.Layout(
            align_items="center",
            border="1px solid #ddd",
            margin="10px 0",
            padding="10px"
        )))
        
        form_fields.append(save_button)
        
        # Set up save callback
        def save_reagent(b):
            try:
                # Collect form data
                inchi_value = inchi_input.value
                if inchi_value and inchi_value.startswith("InChI="):
                    inchi_value = inchi_value[6:]  # Remove 'InChI=' prefix
                
                reagent_data = {
                    "name": name_input.value,
                    "inChi": inchi_value,
                    "SMILES": smiles_input.value,
                    "inChi Key": inchikey_input.value,
                    "molecular weight (in g/mol)": mw_input.value,
                    "eq": eq_input.value,
                    "syringe": syringe_input.value
                }
                
                if density_input:
                    reagent_data["density (in g/mL)"] = density_input.value
                
                # Validate
                validation_errors = validate_reagent_data(reagent_data, reagent_type)
                if validation_errors:
                    status_area.value = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>"
                    status_area.value += "<b>Please correct the following errors:</b><ul>"
                    for error in validation_errors:
                        status_area.value += f"<li>{error}</li>"
                    status_area.value += "</ul></div>"
                    return
                
                # Save
                success = on_save(reagent_data, None)
                if success:
                    status_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px;'><b>Reagent saved successfully!</b></div>"
                    # Clear form
                    self._clear_form(form_widgets)
                else:
                    status_area.value = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'><b>Failed to save reagent.</b></div>"
                    
            except Exception as e:
                status_area.value = f"<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'><b>Error: {str(e)}</b></div>"
        
        save_button.on_click(save_reagent)
        
        # Create form container
        bg_color = "#F0F7F4" if reagent_type == "solid" else "#EFF7FF"
        form = widgets.VBox(
            form_fields,
            layout=widgets.Layout(
                border=f"1px solid {'#90BE6D' if reagent_type == 'solid' else '#577590'}",
                padding="15px",
                margin="10px 0",
                background_color=bg_color
            )
        )
        
        return form, form_widgets
    
    def _clear_form(self, form_widgets):
        """Clear all form inputs"""
        form_widgets['name'].value = ""
        form_widgets['inchi'].value = ""
        form_widgets['smiles'].value = ""
        form_widgets['inchikey'].value = ""
        form_widgets['mw'].value = 0.0
        form_widgets['eq'].value = 1.0
        form_widgets['syringe'].value = 1
        if 'density' in form_widgets:
            form_widgets['density'].value = 1.0
        if 'status' in form_widgets:
            form_widgets['status'].value = ""
    
    def _populate_form(self, form_widgets, compound_data):
        """Populate form with compound data"""
        try:
            form_widgets['name'].value = compound_data.get('name', '')
            form_widgets['inchi'].value = compound_data.get('inchi', '')
            form_widgets['smiles'].value = compound_data.get('smiles', '')
            form_widgets['inchikey'].value = compound_data.get('inchikey', '')
            form_widgets['mw'].value = compound_data.get('molecular_weight', 0.0)
            form_widgets['eq'].value = 1.0  # Default
            form_widgets['syringe'].value = 1  # Default
            if 'density' in form_widgets and 'density' in compound_data:
                form_widgets['density'].value = compound_data.get('density', 1.0)
            
            # Show success message
            if 'status' in form_widgets:
                form_widgets['status'].value = f"""
                <div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px; border: 1px solid #90BE6D;'>
                    <b>✅ Imported from PubChem!</b><br>
                    Compound: {compound_data.get('name', 'Unknown')}<br>
                    Review the data and click "Save Reagent" to add to your experiment.
                </div>
                """
            
        except Exception as e:
            print(f"❌ Error populating form: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _create_pubchem_search_tab(self):
        """Create the PubChem search tab"""
        
        # Search controls
        search_input = widgets.Text(
            placeholder="Enter compound name, SMILES, InChI, or CAS number",
            description="Search:",
            layout=widgets.Layout(width="400px")
        )
        
        search_type = widgets.Dropdown(
            options=['name', 'smiles', 'inchi', 'inchi key', 'cas'],
            value='name',
            description='Type:',
            layout=widgets.Layout(width="180px")
        )
        
        search_button = widgets.Button(
            description="🔍 Search PubChem",
            button_style='primary'
        )
        
        # Results area
        results_output = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ddd',
                overflow_y='auto',
                padding='10px'
            )
        )
        
        # Status area
        status_output = widgets.Output()
        
        def perform_search(button):
            query = search_input.value.strip()
            search_type_value = search_type.value
            
            if not query:
                with status_output:
                    clear_output(wait=True)
                    print("❌ Please enter a search term")
                return
            
            with status_output:
                clear_output(wait=True)
                print(f"🔍 Searching PubChem for '{query}' ({search_type_value})...")
            
            try:
                results = self.pubchem_service.search(query, search_type_value)
                self.search_results = results
                
                with results_output:
                    clear_output(wait=True)
                    
                    if not results:
                        print("No compounds found")
                    else:
                        for i, compound in enumerate(results):
                            self._display_search_result(compound, i)
                
                with status_output:
                    clear_output(wait=True)
                    print(f"✅ Found {len(results)} results")
                    
            except Exception as e:
                with status_output:
                    clear_output(wait=True)
                    print(f"❌ Search error: {e}")
        
        search_button.on_click(perform_search)
        
        # Improved search controls layout with better spacing
        search_controls = widgets.HBox([
            search_input, 
            search_type, 
            search_button
        ], layout=widgets.Layout(
            align_items='flex-end',
            margin='0 0 10px 0'
        ))
        
        return widgets.VBox([
            widgets.HTML("<h4>Search PubChem Database</h4>"),
            widgets.HTML("<p style='color: #666; margin: 5px 0;'>Search for compounds and import them directly into your reagent forms</p>"),
            search_controls,
            status_output,
            widgets.HTML("<h5>Search Results:</h5>"),
            results_output
        ])
    
    def _display_search_result(self, compound: Dict[str, Any], index: int):
        """Display a single search result with import options"""
        
        # Create structure image
        smiles = compound.get('smiles', '')
        structure_widget = None
        if smiles:
            structure_widget = StructureVisualization.get_structure_image(smiles, size=(150, 150))
        
        # Create compound info
        info_html = f"""
        <div style="padding: 10px;">
            <h4>{compound.get('name', 'Unknown')}</h4>
            <p><b>Formula:</b> {compound.get('formula', 'N/A')}</p>
            <p><b>Molecular Weight:</b> {compound.get('molecular_weight', 'N/A')} g/mol</p>
            <p><b>InChI Key:</b> {compound.get('inchikey', 'N/A')}</p>
            <p><b>SMILES:</b> {smiles}</p>
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
        
        def import_as_solid(b):
            self._import_compound(compound, "solid")
        
        def import_as_liquid(b):
            self._import_compound(compound, "liquid")
        
        import_solid_button.on_click(import_as_solid)
        import_liquid_button.on_click(import_as_liquid)
        
        buttons = widgets.VBox([import_solid_button, import_liquid_button])
        
        # Arrange the result
        if structure_widget:
            result_widget = widgets.HBox([structure_widget, info_widget, buttons])
        else:
            result_widget = widgets.HBox([info_widget, buttons])
        
        # Add border and display
        container = widgets.VBox([
            result_widget,
            widgets.HTML("<hr style='margin: 10px 0;'>")
        ], layout=widgets.Layout(
            border="1px solid #ddd",
            margin="5px 0",
            padding="10px"
        ))
        
        display(container)
    
    def _import_compound(self, compound: Dict[str, Any], reagent_type: str):
        """Import a compound from search results and populate the form"""
        
        # Switch to appropriate tab
        if reagent_type == "solid":
            self.tab_widget.selected_index = 0  # Solid tab
            form_widgets = self.solid_form_widgets
        else:
            self.tab_widget.selected_index = 1  # Liquid tab
            form_widgets = self.liquid_form_widgets
        
        # Ensure form widgets are available
        if not form_widgets:
            print(f"❌ Error: Form widgets not available for {reagent_type} tab")
            return
        
        # Populate the form with compound data
        self._populate_form(form_widgets, compound)
    
    def _create_reagents_display_tab(self):
        """Create the current reagents display tab"""
        
        self.reagents_output = widgets.Output(
            layout=widgets.Layout(
                height='500px',
                border='1px solid #ddd',
                overflow_y='auto',
                padding='10px'
            )
        )
        
        refresh_button = widgets.Button(
            description="🔄 Refresh",
            button_style='info'
        )
        
        refresh_button.on_click(lambda b: self._refresh_display_tab())
        
        return widgets.VBox([
            widgets.HTML("<h4>Current Reagents in Experiment</h4>"),
            refresh_button,
            self.reagents_output
        ])
    
    def _refresh_display_tab(self):
        """Refresh the reagents display"""
        with self.reagents_output:
            clear_output(wait=True)
            
            data = self.data_manager.load_data()
            
            # Display solid reagents
            solid_reagents = data.get("solid reagents", [])
            if solid_reagents:
                print("🧱 SOLID REAGENTS")
                print("=" * 50)
                for i, reagent in enumerate(solid_reagents):
                    self._display_reagent_item(reagent, i, "solid")
                print()
            
            # Display liquid reagents
            liquid_reagents = data.get("liquid reagents", [])
            if liquid_reagents:
                print("💧 LIQUID REAGENTS")
                print("=" * 50)
                for i, reagent in enumerate(liquid_reagents):
                    self._display_reagent_item(reagent, i, "liquid")
                print()
            
            if not solid_reagents and not liquid_reagents:
                print("No reagents added yet. Use the solid or liquid reagent tabs to add reagents.")
    
    def _display_reagent_item(self, reagent: Dict[str, Any], index: int, reagent_type: str):
        """Display a single reagent with edit/delete options"""
        
        name = reagent.get("name", "Unknown")
        mw = reagent.get("molecular weight (in g/mol)", 0)
        eq = reagent.get("eq", "N/A")
        syringe = reagent.get("syringe", "N/A")
        
        print(f"{index + 1}. {name}")
        print(f"   MW: {mw} g/mol | Eq: {eq} | Syringe: {syringe}")
        
        if reagent_type == "liquid":
            density = reagent.get("density (in g/mL)", "N/A")
            print(f"   Density: {density} g/mL")
        
        # Create edit and delete buttons
        edit_button = widgets.Button(
            description=f"Edit {name}",
            button_style="warning",
            layout=widgets.Layout(width="200px")
        )
        
        delete_button = widgets.Button(
            description=f"Delete {name}",
            button_style="danger",
            layout=widgets.Layout(width="200px")
        )
        
        def edit_reagent(b):
            self._edit_reagent(reagent, reagent_type)
        
        def delete_reagent(b):
            self._delete_reagent(reagent)
        
        edit_button.on_click(edit_reagent)
        delete_button.on_click(delete_reagent)
        
        button_row = widgets.HBox([edit_button, delete_button])
        display(button_row)
        print()
    
    def _edit_reagent(self, reagent: Dict[str, Any], reagent_type: str):
        """Edit an existing reagent"""
        # Switch to appropriate tab
        if reagent_type == "solid":
            self.tab_widget.selected_index = 0
        else:
            self.tab_widget.selected_index = 1
        
        # Note: In full implementation, we would populate the form with reagent data
        print(f"Editing {reagent.get('name', 'reagent')} - form would be populated")
    
    def _delete_reagent(self, reagent: Dict[str, Any]):
        """Delete a reagent"""
        success = self.data_manager.delete_reagent(reagent)
        if success:
            print(f"✅ Deleted {reagent.get('name', 'reagent')}")
            self._refresh_display_tab()
            # Also refresh the final details display to update limiting reagent
            self._refresh_final_details_display()
        else:
            print(f"❌ Failed to delete {reagent.get('name', 'reagent')}")
    
    def _create_final_details_tab(self):
        """Create the final details tab with original functionality"""
        
        # Status/message area
        self.final_message_area = widgets.HTML("")
        
        # Limiting reagent display (will be updated dynamically)
        self.limiting_reagent_display = widgets.HTML(value="")
        
        # Initialize the limiting reagent display
        self._refresh_final_details_display()
        
        # Load current data for form initialization
        data = self.data_manager.load_data()
        
        # Form fields
        mass_scale_input = widgets.FloatText(
            value=data.get("mass scale (in mg)", None),
            description="Mass scale (mg):",
            layout=widgets.Layout(width="80%")
        )
        
        concentration_input = widgets.FloatText(
            value=data.get("concentration (in mM)", None),
            description="Concentration (mM):",
            layout=widgets.Layout(width="80%")
        )
        
        # Volume calculation display
        volume_display = widgets.HTML(
            value="<p><b>Volume needed:</b> Calculate by entering values above</p>"
        )
        
        # Function to calculate and update volume
        def update_volume(*args):
            try:
                mass_scale = mass_scale_input.value
                concentration = concentration_input.value
                
                # Get current limiting reagent info
                _, limiting_reagent_mw = self._get_limiting_reagent_info()
                
                if not limiting_reagent_mw or mass_scale <= 0 or concentration <= 0:
                    volume_display.value = "<p><b>Volume needed:</b> Please enter valid mass scale and concentration values</p>"
                    return
                
                # Calculate moles of limiting reagent (mg to mmol)
                moles_limiting = mass_scale / limiting_reagent_mw
                
                # Calculate volume in mL (convert from mM to M)
                volume_solution = moles_limiting / (concentration / 1000)
                
                volume_display.value = f"<p><b>Volume needed:</b> {volume_solution:.4f} mL</p>"
            except Exception as e:
                volume_display.value = f"<p><b>Volume needed:</b> Error in calculation: {str(e)}</p>"
        
        # Observe changes to update volume calculation
        mass_scale_input.observe(update_volume, names='value')
        concentration_input.observe(update_volume, names='value')
        
        solvent_input = widgets.Text(
            value=data.get("solvent", ""),
            description="Solvents:",
            layout=widgets.Layout(width="80%")
        )
        
        # Submit button
        submit_button = widgets.Button(
            description="💾 Process Data",
            button_style="success",
            layout=widgets.Layout(width="auto")
        )
        
        def save_final_details(b):
            try:
                # Get form values
                mass_scale = mass_scale_input.value
                concentration = concentration_input.value
                solvent = solvent_input.value
                
                # Get current limiting reagent info
                limiting_reagent, _ = self._get_limiting_reagent_info()
                
                # Validate
                if not limiting_reagent:
                    self.final_message_area.value = "<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Please set one reagent to eq=1.0 as the limiting reagent first.</p>"
                    return
                
                if mass_scale <= 0:
                    self.final_message_area.value = "<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Mass scale must be greater than 0.</p>"
                    return
                
                if concentration <= 0:
                    self.final_message_area.value = "<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Concentration must be greater than 0.</p>"
                    return
                
                # Save the final details
                success = self.data_manager.update_final_details(
                    mass_scale,
                    concentration,
                    solvent
                )
                
                if success:
                    self.final_message_area.value = """
                    <div style='color: green; padding: 15px; background-color: #EEFFEE; border-radius: 5px; border: 1px solid #90BE6D;'>
                        <h4 style='margin-top: 0;'>✅ Final Details Saved Successfully!</h4>
                        <p>Your experiment data has been saved with the unified experimental metadata system.</p>
                        <p><b>Next Steps:</b></p>
                        <ul>
                            <li>Proceed to Phase 2: Apparatus Builder</li>
                            <li>Your reagent data will be automatically available in subsequent phases</li>
                        </ul>
                    </div>
                    """
                else:
                    self.final_message_area.value = "<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>❌ Failed to save final details. Please try again.</p>"
                    
            except Exception as e:
                self.final_message_area.value = f"<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>❌ Error: {str(e)}</p>"
        
        submit_button.on_click(save_final_details)
        
        # Create form with original styling
        form_container = widgets.VBox([
            widgets.HTML("<h4>Final Experiment Details</h4>"),
            self.final_message_area,
            self.limiting_reagent_display,
            mass_scale_input,
            concentration_input,
            volume_display,
            solvent_input,
            submit_button
        ], layout=widgets.Layout(
            border="1px solid #ddd",
            padding="15px",
            margin="10px 0"
        ))
        
        # Initial volume calculation if all values are available
        current_mass = data.get("mass scale (in mg)")
        current_concentration = data.get("concentration (in mM)")
        if current_mass and current_concentration:
            update_volume()
        
        return form_container
    
    def _get_limiting_reagent_info(self):
        """Get current limiting reagent name and molecular weight"""
        data = self.data_manager.load_data()
        
        # Find the limiting reagent (eq = 1.0)
        limiting_reagent = None
        limiting_reagent_mw = None
        
        all_reagents = data.get("solid reagents", []) + data.get("liquid reagents", [])
        for reagent in all_reagents:
            if abs(reagent.get("eq", 0) - 1.0) < 1e-6:
                limiting_reagent = reagent["name"]
                limiting_reagent_mw = reagent["molecular weight (in g/mol)"]
                break
        
        return limiting_reagent, limiting_reagent_mw
    
    def _refresh_final_details_display(self):
        """Refresh the limiting reagent display in final details tab"""
        # Only refresh if the final details tab has been created
        if not hasattr(self, 'limiting_reagent_display'):
            return
            
        limiting_reagent, _ = self._get_limiting_reagent_info()
        
        if limiting_reagent:
            reagent_html = f"<p><b>Limiting Reagent:</b> {limiting_reagent}</p>"
        else:
            reagent_html = "<p><b>Limiting Reagent:</b> <span style='color:red'>None selected (set eq=1.0 for limiting reagent)</span></p>"
        
        self.limiting_reagent_display.value = reagent_html
    
    def _save_solid_reagent(self, new_reagent: Dict[str, Any], old_reagent: Optional[Dict[str, Any]] = None) -> bool:
        """Save a solid reagent"""
        try:
            if old_reagent:
                # Update existing
                success = self.data_manager.update_reagent(old_reagent, new_reagent, "solid")
            else:
                # Add new
                success = self.data_manager.add_reagent(new_reagent, "solid")
            
            if success:
                self._refresh_display_tab()
                # Also refresh the final details display to update limiting reagent
                self._refresh_final_details_display()
            
            return success
        except Exception as e:
            print(f"Error saving solid reagent: {e}")
            return False
    
    def _save_liquid_reagent(self, new_reagent: Dict[str, Any], old_reagent: Optional[Dict[str, Any]] = None) -> bool:
        """Save a liquid reagent"""
        try:
            if old_reagent:
                # Update existing
                success = self.data_manager.update_reagent(old_reagent, new_reagent, "liquid")
            else:
                # Add new
                success = self.data_manager.add_reagent(new_reagent, "liquid")
            
            if success:
                self._refresh_display_tab()
                # Also refresh the final details display to update limiting reagent
                self._refresh_final_details_display()
            
            return success
        except Exception as e:
            print(f"Error saving liquid reagent: {e}")
            return False
    
    def display(self):
        """Display the ReagentUI interface"""
        # Initialize the display
        self._refresh_display_tab()
        display(self.main_widget)
    
    def get_data(self) -> Dict[str, Any]:
        """Get current reagent data"""
        return self.data_manager.load_data()