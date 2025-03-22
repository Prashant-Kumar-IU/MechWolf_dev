import json
import ipywidgets as widgets
from IPython.display import display, clear_output
from mechwolf.DataEntry.ProcessData import process_data
from typing import Dict, Any, Optional, List, Callable, Union

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
        
        # Set the tab children and titles
        self.tab_container.children = [
            self.add_reagents_tab,
            self.current_reagents_tab,
            self.final_details_tab
        ]
        self.tab_container.set_title(0, "Add Reagents")
        self.tab_container.set_title(1, "Current Reagents")
        self.tab_container.set_title(2, "Final Details")
        
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
        """Create the tab content for adding reagents with accordion."""
        # Create accordion for different reagent types
        reagent_accordion = widgets.Accordion()
        
        # Create solid reagent form button
        add_solid_button = widgets.Button(
            description="Add Solid Reagent",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#90BE6D"}
        )
        add_solid_button.on_click(lambda b: self.show_reagent_form("solid"))
        
        # Create liquid reagent form button
        add_liquid_button = widgets.Button(
            description="Add Liquid Reagent",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#577590"}
        )
        add_liquid_button.on_click(lambda b: self.show_reagent_form("liquid"))
        
        # Create containers for buttons
        solid_form_container = widgets.VBox([add_solid_button])
        liquid_form_container = widgets.VBox([add_liquid_button])
        
        # Set accordion children and titles
        reagent_accordion.children = [solid_form_container, liquid_form_container]
        reagent_accordion.set_title(0, "Solid Reagent")
        reagent_accordion.set_title(1, "Liquid Reagent")
        
        # Create form area for displaying the actual forms
        self.form_area = widgets.VBox(
            layout=widgets.Layout(
                margin="10px 0 10px 0",
                min_height="100px"
            )
        )
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Add a New Reagent</h4>"),
            reagent_accordion,
            self.form_area
        ], layout=widgets.Layout(padding="10px"))
    
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
        """Create the tab content for entering final details and submission."""
        # Create a button to show the submission form
        submit_button = widgets.Button(
            description="Enter Final Details",
            button_style="success",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#007F5F"}
        )
        submit_button.on_click(self.show_submit_form)
        
        # Create a container for the final details form
        self.final_details_form = widgets.VBox(
            layout=widgets.Layout(
                margin="10px 0 10px 0",
                min_height="100px"
            )
        )
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Final Details and Submission</h4>"),
            submit_button,
            self.final_details_form
        ], layout=widgets.Layout(padding="10px"))

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
        
        # Return an HBox containing the HTML and buttons
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

    def show_reagent_form(self, reagent_type: str, reagent: Optional[Dict[str, Any]] = None) -> None:
        """Display a form for adding or editing a reagent with validation."""
        # Clear any existing form
        self.clear_form_area()
        
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
        
        # Create buttons
        save_button = widgets.Button(
            description="Save Reagent",
            button_style="success",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#3F704D" if reagent_type == "solid" else "#3A5D9F"}
        )
        
        cancel_button = widgets.Button(
            description="Cancel",
            button_style="warning",
            layout=widgets.Layout(width="auto")
        )
        
        # Function to update field style based on validation
        def update_field_style(field, has_error):
            if has_error:
                field.style = {"description_width": "initial"}
                field.layout.border = "1px solid red"
            else:
                field.style = {}
                field.layout.border = ""
        
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
        form_fields.append(widgets.HBox([save_button, cancel_button]))
        
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
        
        # Validation function
        def validate_and_save():
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
            
            # Reset styles
            update_field_style(name_input, False)
            update_field_style(mw_input, False)
            update_field_style(eq_input, False)
            update_field_style(syringe_input, False)
            if density_input:
                update_field_style(density_input, False)
            
            # If errors, show them and highlight fields
            if validation_errors:
                error_html = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'>"
                error_html += "<b>Please correct the following errors:</b><ul>"
                for field, message in validation_errors.items():
                    error_html += f"<li>{message}</li>"
                    # Highlight fields with errors
                    if field == "name":
                        update_field_style(name_input, True)
                    elif field == "mw":
                        update_field_style(mw_input, True)
                    elif field == "eq":
                        update_field_style(eq_input, True)
                    elif field == "syringe":
                        update_field_style(syringe_input, True)
                    elif field == "density" and density_input:
                        update_field_style(density_input, True)
                error_html += "</ul></div>"
                error_area.value = error_html
                return False
            
            # Clear any error messages
            error_area.value = ""
            return new_reagent
        
        # Set up button callbacks
        def save_handler(b):
            new_reagent = validate_and_save()
            if new_reagent:
                # Update data structure
                key = f"{reagent_type} reagents"
                if reagent:
                    self.data[key].remove(reagent)
                self.data[key].append(new_reagent)
                
                # Save to show the auto-save feature
                self.save_data()
                
                # Show success message
                error_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px; margin-bottom: 10px;'><b>Reagent saved successfully!</b></div>"
                
                # Clear the form and update the display after a brief delay
                import threading
                def delayed_clear():
                    import time
                    time.sleep(1)  # Show success message for 1 second
                    self.clear_form_area()
                    self.update_reagent_list()
                    # Switch to Current Reagents tab to show the new reagent
                    self.tab_container.selected_index = 1
                
                threading.Thread(target=delayed_clear).start()
                
        save_button.on_click(save_handler)
        cancel_button.on_click(lambda b: self.clear_form_area())
        
        # Display the form
        self.form_area.children = (form,)
        self.current_form = form
        
        # Switch to the Add Reagents tab if not already there
        self.tab_container.selected_index = 0

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
        reagent_type = "solid" if reagent in self.data["solid reagents"] else "liquid"
        self.show_reagent_form(reagent_type, reagent)
        
        # Switch to the Add Reagents tab
        self.tab_container.selected_index = 0

    def clear_form_area(self) -> None:
        """Clear any forms from the form area."""
        self.form_area.children = ()
        self.current_form = None

    def show_submit_form(self, b: widgets.Button) -> None:
        """Display the final submission form."""
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
        
        cancel_button = widgets.Button(
            description="Cancel",
            button_style="warning",
            layout=widgets.Layout(width="auto")
        )
        
        # Create form container
        form = widgets.VBox(
            [
                form_title,
                mass_scale_input,
                concentration_input,
                solvent_input,
                widgets.HBox([submit_button, cancel_button])
            ],
            layout=widgets.Layout(
                border="1px solid #ddd",
                padding="10px",
                margin="10px 0"
            )
        )
        
        # Set up button callbacks
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
                from mechwolf.DataEntry import ProcessData
                reload(ProcessData)  # Reload the module to avoid any caching issues
                ProcessData.process_data(self.data_file)
                
            except ValueError as e:
                # Display error message
                error_widget = widgets.HTML(
                    f"<p style='color: red'>Error: {str(e)}</p>"
                )
                self.final_details_form.children = (widgets.VBox([error_widget, form]),)
        
        submit_button.on_click(submit_handler)
        
        def clear_final_form(b):
            self.final_details_form.children = ()
            
        cancel_button.on_click(clear_final_form)
        
        # Display the form in the final details tab
        self.final_details_form.children = (form,)
        self.current_form = form
        
        # Switch to the Final Details tab
        self.tab_container.selected_index = 2

    def run(self) -> None:
        """Run the application."""
        # If there's no data, create the widgets
        if not self.data["solid reagents"] and not self.data["liquid reagents"]:
            self.setup_ui()
        else:
            # Ask if user wants to edit or process
            display(widgets.HTML("<h3>Existing reagent data found</h3>"))
            process_btn = widgets.Button(description="Process Data", button_style="success")
            edit_btn = widgets.Button(description="Edit Data", button_style="info")
            
            def on_process(b):
                clear_output(wait=True)
                process_data(self.data_file)
                
            def on_edit(b):
                clear_output(wait=True)
                self.setup_ui()
            
            process_btn.on_click(on_process)
            edit_btn.on_click(on_edit)
            
            display(widgets.HBox([process_btn, edit_btn]))

if __name__ == "__main__":
    data_file = input("Enter the JSON file name: ").strip()
    app = ReagentInputForm(data_file)
    app.run()
