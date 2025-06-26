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
# Note: data_adapter removed - now using direct experimental_metadata integration
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
        # Direct integration with experimental metadata (no adapter needed)
        self.chemistry_manager = experiment_manager.chemistry
        self.pubchem_service = PubChemService()
        
        # Initialize UI state
        self.current_editing_reagent = None
        self.search_results = []
        
        # Store form widget references for import functionality
        self.solid_form_widgets = {}
        self.liquid_form_widgets = {}
        
        # Track editing state
        self.editing_reagent = {'solid': None, 'liquid': None}
        
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
                
                # Check if we're editing an existing reagent
                editing_reagent = self.editing_reagent.get(reagent_type, None)
                
                # Save
                success = on_save(reagent_data, editing_reagent)
                if success:
                    if editing_reagent:
                        status_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px;'><b>Reagent updated successfully!</b></div>"
                        # Clear editing state
                        self.editing_reagent[reagent_type] = None
                    else:
                        status_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px;'><b>Reagent saved successfully!</b></div>"
                    
                    # Clear form only if not editing, or after successful edit
                    self._clear_form(form_widgets)
                else:
                    action = "update" if editing_reagent else "save"
                    status_area.value = f"<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'><b>Failed to {action} reagent.</b></div>"
                    
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
    
    def _clear_form_and_editing_state(self, form_widgets, reagent_type):
        """Clear form and reset editing state"""
        self._clear_form(form_widgets)
        self.editing_reagent[reagent_type] = None
    
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
        
        # Clear any existing editing state when importing
        self.editing_reagent[reagent_type] = None
        
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
            
            data = self.chemistry_manager.get_data()
            
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
            form_widgets = self.solid_form_widgets
        else:
            self.tab_widget.selected_index = 1
            form_widgets = self.liquid_form_widgets
        
        # Ensure form widgets are available
        if not form_widgets:
            print(f"❌ Error: Form widgets not available for {reagent_type} tab")
            return
        
        # Convert reagent data to the format expected by _populate_form
        # The reagent data is in old format, need to map to the expected keys
        compound_data = {
            'name': reagent.get('name', ''),
            'inchi': reagent.get('inChi', ''),
            'smiles': reagent.get('SMILES', ''),
            'inchikey': reagent.get('inChi Key', ''),
            'molecular_weight': reagent.get('molecular weight (in g/mol)', 0.0),
            'density': reagent.get('density (in g/mL)', 1.0)  # For liquid reagents
        }
        
        # Set editing state
        self.editing_reagent[reagent_type] = reagent
        
        # Populate the form with reagent data for editing
        self._populate_form_for_editing(form_widgets, compound_data, reagent)
        
        print(f"✅ Ready to edit {reagent.get('name', 'reagent')}")
    
    def _populate_form_for_editing(self, form_widgets, compound_data, original_reagent):
        """Populate form with reagent data for editing, preserving all fields"""
        try:
            # Populate chemical data
            form_widgets['name'].value = compound_data.get('name', '')
            form_widgets['inchi'].value = compound_data.get('inchi', '')
            form_widgets['smiles'].value = compound_data.get('smiles', '')
            form_widgets['inchikey'].value = compound_data.get('inchikey', '')
            form_widgets['mw'].value = compound_data.get('molecular_weight', 0.0)
            
            # Populate reagent-specific data (equivalents, syringe)
            form_widgets['eq'].value = original_reagent.get('eq', 1.0)
            form_widgets['syringe'].value = original_reagent.get('syringe', 1)
            
            # Populate density for liquid reagents
            if 'density' in form_widgets:
                form_widgets['density'].value = compound_data.get('density', 1.0)
            
            # Show editing message
            if 'status' in form_widgets:
                form_widgets['status'].value = f"""
                <div style='color: blue; padding: 10px; background-color: #EEF7FF; border-radius: 5px; border: 1px solid #66B2FF;'>
                    <b>✏️ Editing Reagent</b><br>
                    Compound: {compound_data.get('name', 'Unknown')}<br>
                    Modify the data as needed and click "Save Reagent" to update.
                </div>
                """
                
        except Exception as e:
            print(f"❌ Error populating form for editing: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _delete_reagent(self, reagent: Dict[str, Any]):
        """Delete a reagent"""
        success = self.chemistry_manager.remove_reagent(reagent.get('name', ''), reagent.get('type', 'solid'))
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
        data = self.chemistry_manager.get_data()
        
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
                # Update final details directly through chemistry manager
                success = self.chemistry_manager.update_reagent_scale(
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
        
        # Create stoichiometry table button
        stoichiometry_button = widgets.Button(
            description="📊 Create Stoichiometry Table",
            button_style="info",
            layout=widgets.Layout(width="auto")
        )
        
        def show_stoichiometry_table(b):
            self._show_stoichiometry_table()
        
        stoichiometry_button.on_click(show_stoichiometry_table)
        
        # Create button row
        button_row = widgets.HBox([submit_button, stoichiometry_button], 
                                  layout=widgets.Layout(gap="10px"))
        
        # Store original form components for state management
        self.final_form_components = {
            'title': widgets.HTML("<h4>Final Experiment Details</h4>"),
            'message_area': self.final_message_area,
            'limiting_reagent': self.limiting_reagent_display,
            'mass_scale': mass_scale_input,
            'concentration': concentration_input,
            'volume': volume_display,
            'solvent': solvent_input,
            'buttons': button_row
        }
        
        # Create form with original styling
        form_container = widgets.VBox([
            self.final_form_components['title'],
            self.final_form_components['message_area'],
            self.final_form_components['limiting_reagent'],
            self.final_form_components['mass_scale'],
            self.final_form_components['concentration'],
            self.final_form_components['volume'],
            self.final_form_components['solvent'],
            self.final_form_components['buttons']
        ], layout=widgets.Layout(
            border="1px solid #ddd",
            padding="15px",
            margin="10px 0"
        ))
        
        # Store form container for state management
        self.final_details_container = form_container
        
        # Initial volume calculation if all values are available
        current_mass = data.get("mass scale (in mg)")
        current_concentration = data.get("concentration (in mM)")
        if current_mass and current_concentration:
            update_volume()
        
        return self.final_details_container
    
    def _get_limiting_reagent_info(self):
        """Get current limiting reagent name and molecular weight"""
        data = self.chemistry_manager.get_data()
        
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
                success = self.chemistry_manager.update_solid_reagent(old_reagent, new_reagent)
            else:
                # Add new
                success = self.chemistry_manager.add_solid_reagent(new_reagent)
            
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
                success = self.chemistry_manager.update_liquid_reagent(old_reagent, new_reagent)
            else:
                # Add new
                success = self.chemistry_manager.add_liquid_reagent(new_reagent)
            
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
    
    def _show_stoichiometry_table(self):
        """Show the stoichiometry table view, replacing the form"""
        try:
            # Clear the current final details tab and show table
            final_tab = self.tab_widget.children[4]  # Final Details is 5th tab (index 4)
            
            # Generate stoichiometry table
            table_html = self._generate_stoichiometry_table()
            
            if table_html:
                # Create table display
                table_display = widgets.HTML(table_html)
                
                # Replace tab content with table view
                final_tab.children = [table_display]
                
            else:
                # Show error message
                error_msg = widgets.HTML(
                    "<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>"
                    "❌ Cannot create stoichiometry table. Please ensure you have added reagents and set a limiting reagent (eq=1.0)."
                    "</p>"
                )
                final_tab.children = [error_msg]
                
        except Exception as e:
            print(f"Error showing stoichiometry table: {e}")
    
    def _generate_stoichiometry_table(self) -> str:
        """Generate HTML for stoichiometry table based on current reagents"""
        try:
            data = self.chemistry_manager.get_data()
            
            # Get all reagents
            solid_reagents = data.get("solid reagents", [])
            liquid_reagents = data.get("liquid reagents", [])
            all_reagents = solid_reagents + liquid_reagents
            
            if not all_reagents:
                return None
            
            # Find limiting reagent
            limiting_reagent = None
            for reagent in all_reagents:
                if abs(reagent.get("eq", 0) - 1.0) < 1e-6:
                    limiting_reagent = reagent
                    break
            
            if not limiting_reagent:
                return None
            
            # Get experiment parameters
            mass_scale = data.get("mass scale (in mg)", 100)  # Default 100mg
            concentration = data.get("concentration (in mM)", 100)  # Default 100mM
            solvent = data.get("solvent", "THF")
            
            # Calculate stoichiometry
            limiting_mw = limiting_reagent["molecular weight (in g/mol)"]
            limiting_moles = (mass_scale / 1000) / limiting_mw  # Convert mg to g, then to moles
            
            # Volume calculation
            volume_ml = (limiting_moles * 1000) / concentration  # moles to mmol, then volume
            
            # Generate table HTML
            html = f"""
            <div style="max-width: 1200px; margin: 20px auto; font-family: Arial, sans-serif;">
                <h2 style="color: #2563eb; text-align: center; margin-bottom: 30px;">
                    📊 Stoichiometry Table
                </h2>
                
                <!-- Experiment Summary -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                    <h3 style="color: #1e40af; margin-top: 0;">Experiment Parameters</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div><strong>Limiting Reagent:</strong> {limiting_reagent['name']}</div>
                        <div><strong>Mass Scale:</strong> {mass_scale} mg</div>
                        <div><strong>Concentration:</strong> {concentration} mM</div>
                        <div><strong>Solvent:</strong> {solvent}</div>
                        <div><strong>Total Volume:</strong> {volume_ml:.2f} mL</div>
                        <div><strong>Limiting Reagent Moles:</strong> {limiting_moles*1000:.3f} mmol</div>
                    </div>
                </div>
                
                <!-- Reagents Table -->
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white;">
                                <th style="padding: 15px; text-align: left; font-weight: 600;">Reagent</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">MW (g/mol)</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">Equivalents</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">Amount (mmol)</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">Mass (mg)</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">Volume (μL)</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">Density (g/mL)</th>
                                <th style="padding: 15px; text-align: center; font-weight: 600;">Syringe</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add reagent rows
            for i, reagent in enumerate(all_reagents):
                reagent_name = reagent["name"]
                reagent_mw = reagent["molecular weight (in g/mol)"]
                reagent_eq = reagent.get("eq", 1.0)
                reagent_syringe = reagent.get("syringe", "N/A")
                
                # Calculate amounts
                reagent_moles = limiting_moles * reagent_eq
                reagent_mass_mg = reagent_moles * reagent_mw * 1000
                
                # Volume and density for liquids
                is_liquid = reagent in liquid_reagents
                if is_liquid:
                    density = reagent.get("density (in g/mL)", 1.0)
                    volume_ul = (reagent_mass_mg / 1000) / density * 1000  # Convert to μL
                    density_display = f"{density:.3f}"
                    volume_display = f"{volume_ul:.1f}"
                else:
                    density_display = "—"
                    volume_display = "—"
                
                # Row styling
                row_style = "background: #f8fafc;" if i % 2 == 0 else "background: white;"
                
                html += f"""
                        <tr style="{row_style}">
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                                <strong>{reagent_name}</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent_mw:.1f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent_eq:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent_moles*1000:.3f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent_mass_mg:.1f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{volume_display}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{density_display}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent_syringe}</td>
                        </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
                
                <!-- Position Summary -->
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-top: 30px;">
                    <h3 style="color: #15803d; margin-top: 0;">Syringe Positions</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px;">
            """
            
            # Group reagents by syringe position
            syringe_groups = {}
            for reagent in all_reagents:
                syringe = reagent.get("syringe", "Unknown")
                if syringe not in syringe_groups:
                    syringe_groups[syringe] = []
                syringe_groups[syringe].append(reagent)
            
            for syringe, reagents in sorted(syringe_groups.items(), key=lambda x: str(x[0])):
                reagent_names = [r["name"] for r in reagents]
                html += f"""
                        <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #d1fae5;">
                            <strong>Syringe {syringe}:</strong><br>
                            {', '.join(reagent_names)}
                        </div>
                """
            
            html += """
                    </div>
                </div>
                
                <!-- Notes -->
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 20px; margin-top: 20px;">
                    <h4 style="color: #1e40af; margin-top: 0;">Notes</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #374151;">
                        <li>Calculations based on limiting reagent and mass scale</li>
                        <li>Volume calculations for liquid reagents only</li>
                        <li>Uses densities from reagent properties</li>
                    </ul>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            print(f"Error generating stoichiometry table: {e}")
            return None

    def get_data(self) -> Dict[str, Any]:
        """Get current reagent data"""
        return self.chemistry_manager.get_data()