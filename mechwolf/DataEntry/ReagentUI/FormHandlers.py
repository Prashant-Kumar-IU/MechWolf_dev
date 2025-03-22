"""Form handlers for reagent entry forms."""
import ipywidgets as widgets
from typing import Dict, Any, Optional, Callable, List, Tuple
from .StructureVisualization import StructureVisualizer
from mechwolf.DataEntry.ReagentUI.utils import validate_reagent_data

class ReagentFormHandler:
    """Handler for reagent entry forms."""
    
    @staticmethod
    def create_reagent_form(reagent_type: str, 
                           reagent: Optional[Dict[str, Any]] = None,
                           on_save: Callable = None,
                           on_lookup: Callable = None) -> widgets.Widget:
        """
        Create a form for adding or editing a reagent.
        
        Parameters:
        -----------
        reagent_type : str
            Type of reagent ('solid' or 'liquid')
        reagent : dict, optional
            Existing reagent data for editing
        on_save : callable
            Callback for save button
        on_lookup : callable
            Callback for lookup button
            
        Returns:
        --------
        ipywidgets.Widget
            Form widget
        """
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
            layout=widgets.Layout(width="200px", height="200px")
        )
        
        # Function to update structure visualization
        def update_structure(change=None):
            structure_area.clear_output()
            with structure_area:
                from IPython.display import display
                if smiles_input.value:
                    vis = StructureVisualizer.get_structure_image(smiles_input.value, size=(200, 200))
                    if vis:
                        display(vis)
                    else:
                        print("Could not render structure.\nCheck SMILES format.")
                else:
                    pass  # Empty output
        
        # Connect update to SMILES field
        smiles_input.observe(update_structure, names='value')
        
        # Add lookup button for structure
        lookup_button = widgets.Button(
            description="Lookup Structure",
            button_style="info",
            icon="search",
            layout=widgets.Layout(width="auto")
        )
        
        if on_lookup:
            lookup_button.on_click(lambda b: on_lookup(name_input.value, smiles_input, inchi_input, inchikey_input, mw_input, update_structure))
        
        # Add density field for liquid reagents
        density_input = None
        density_tooltip = None
        
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
        
        # Set up callback for save button
        if on_save:
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
                validation_errors = validate_reagent_data(new_reagent, reagent_type)
                
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
                
                # Call the save callback with the new reagent and old reagent (if editing)
                success = on_save(new_reagent, reagent)
                
                if success:
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
            
            save_button.on_click(validate_and_save)
        
        return form

class FinalDetailsFormHandler:
    """Handler for final details form."""
    
    @staticmethod
    def create_final_details_form(data: Dict[str, Any], on_submit: Callable) -> widgets.Widget:
        """
        Create a form for final details.
        
        Parameters:
        -----------
        data : dict
            Current data
        on_submit : callable
            Callback for submit button
            
        Returns:
        --------
        ipywidgets.Widget
            Form widget
        """
        # Get existing values if any
        mass_scale_value = data.get("mass scale (in mg)", None)
        concentration_value = data.get("concentration (in mM)", None)
        solvent_value = data.get("solvent", "")
        
        # Create form widgets
        form_title = widgets.HTML("<h4>Final Details</h4>")
        
        # Error/message display area
        message_area = widgets.HTML("")
        
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
                # Get form values
                mass_scale = mass_scale_input.value
                concentration = concentration_input.value
                solvent = solvent_input.value
                
                # Call the submit callback with the form values
                success = on_submit(mass_scale, concentration, solvent, message_area)
                
                # If not successful, the message will be displayed by the callback
                
            except Exception as e:
                # Display error message
                message_area.value = f"<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Error: {str(e)}</p>"
        
        submit_button.on_click(submit_handler)
        
        return form
