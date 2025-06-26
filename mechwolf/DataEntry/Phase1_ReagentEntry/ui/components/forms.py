"""
Form components for reagent entry.

This module contains reusable form creation and management components,
extracted from the original monolithic UI to eliminate code duplication.
"""

import ipywidgets as widgets
from typing import Dict, Any, Callable, Optional, List, Tuple
from .base import BaseFormField, MessageArea, StructurePreview, ButtonFactory, FormContainer
from ...core.models import ReagentModel
from ...utils.validation import validate_reagent_data


class ReagentFormData:
    """Container for reagent form data with field mappings."""
    
    def __init__(self, reagent_type: str):
        """
        Initialize form data container.
        
        Args:
            reagent_type: "solid" or "liquid"
        """
        self.reagent_type = reagent_type
        self.widgets = {}
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all form input widgets."""
        self.widgets = {
            'name': widgets.Text(
                description="Name:",
                layout=widgets.Layout(width="80%")
            ),
            'inchi': widgets.Text(
                description="InChI:",
                layout=widgets.Layout(width="80%")
            ),
            'smiles': widgets.Text(
                description="SMILES:",
                layout=widgets.Layout(width="80%")
            ),
            'inchikey': widgets.Text(
                description="InChI Key:",
                layout=widgets.Layout(width="80%")
            ),
            'molecular_weight': widgets.FloatText(
                description="MW (g/mol):",
                layout=widgets.Layout(width="80%")
            ),
            'equivalents': widgets.FloatText(
                description="Equivalents:",
                value=1.0,
                layout=widgets.Layout(width="80%")
            ),
            'position': widgets.IntText(
                description="Syringe:",
                value=1,
                layout=widgets.Layout(width="80%")
            )
        }
        
        # Add density for liquid reagents
        if self.reagent_type == "liquid":
            self.widgets['density'] = widgets.FloatText(
                description="Density (g/mL):",
                value=1.0,
                layout=widgets.Layout(width="80%")
            )
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get current form data as dictionary.
        
        Returns:
            Dictionary with form values
        """
        data = {}
        for key, widget in self.widgets.items():
            if key == 'inchi':
                # Handle InChI prefix removal
                value = widget.value
                if value and value.startswith("InChI="):
                    value = value[6:]
                data[key] = value
            else:
                data[key] = widget.value
        
        return data
    
    def set_data(self, data: Dict[str, Any]):
        """
        Set form data from dictionary.
        
        Args:
            data: Dictionary with values to set
        """
        for key, widget in self.widgets.items():
            if key in data and data[key] is not None:
                widget.value = data[key]
    
    def clear(self):
        """Clear all form fields to defaults."""
        self.widgets['name'].value = ""
        self.widgets['inchi'].value = ""
        self.widgets['smiles'].value = ""
        self.widgets['inchikey'].value = ""
        self.widgets['molecular_weight'].value = 0.0
        self.widgets['equivalents'].value = 1.0
        self.widgets['position'].value = 1
        
        if 'density' in self.widgets:
            self.widgets['density'].value = 1.0
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate current form data.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # Convert to old format for validation
        data = self.get_data()
        old_format_data = {
            "name": data['name'],
            "molecular weight (in g/mol)": data['molecular_weight'],
            "eq": data['equivalents'],
            "syringe": data['position'],
            "inChi": data['inchi'],
            "SMILES": data['smiles'],
            "inChi Key": data['inchikey']
        }
        
        if self.reagent_type == "liquid" and 'density' in data:
            old_format_data["density (in g/mL)"] = data['density']
        
        errors = validate_reagent_data(old_format_data, self.reagent_type)
        return len(errors) == 0, errors


class ReagentForm:
    """Complete reagent entry form with validation and structure preview."""
    
    def __init__(self, reagent_type: str, on_save: Optional[Callable] = None):
        """
        Initialize reagent form.
        
        Args:
            reagent_type: "solid" or "liquid"
            on_save: Callback function for save button (receives form_data, errors)
        """
        self.reagent_type = reagent_type
        self.on_save = on_save
        self.is_editing = False
        self.editing_reagent = None
        
        # Create form components
        self.form_data = ReagentFormData(reagent_type)
        self.message_area = MessageArea()
        self.structure_preview = StructurePreview(size=(200, 200))
        
        # Create the form UI
        self._create_form()
        
        # Set up SMILES change observer for structure preview
        self.form_data.widgets['smiles'].observe(
            self._on_smiles_change, names='value'
        )
    
    def _create_form(self):
        """Create the complete form UI."""
        # Create form fields with tooltips
        form_fields = [
            widgets.HTML(f"<h4>{'Edit' if self.is_editing else 'Add'} {self.reagent_type.capitalize()} Reagent</h4>"),
            self.message_area.widget
        ]
        
        # Add form fields with helpful tooltips
        tooltips = {
            'name': "Required: Chemical name",
            'inchi': "Example: InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3",
            'smiles': "Example: CCO (ethanol)",
            'inchikey': "Example: LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            'molecular_weight': "Required: Must be > 0",
            'equivalents': "Required: Must be > 0. Set to 1.0 for limiting reagent.",
            'position': "Required: Must be > 0"
        }
        
        if self.reagent_type == "liquid":
            tooltips['density'] = "Required for liquids: Must be > 0"
        
        for key, widget in self.form_data.widgets.items():
            tooltip = tooltips.get(key, "")
            form_fields.append(BaseFormField.create_field(widget, tooltip))
        
        # Add structure preview
        structure_section = widgets.VBox([
            widgets.HTML("<h4>Structure Preview</h4>"),
            self.structure_preview.widget
        ], layout=widgets.Layout(
            align_items="center",
            border="1px solid #ddd",
            margin="10px 0",
            padding="10px"
        ))
        form_fields.append(structure_section)
        
        # Add save button
        self.save_button = ButtonFactory.create_success("Save Reagent")
        self.save_button.on_click(self._handle_save)
        form_fields.append(self.save_button)
        
        # Create form container
        self.widget = FormContainer.create(form_fields, self.reagent_type)
    
    def _on_smiles_change(self, change):
        """Handle SMILES field changes to update structure preview."""
        smiles = change['new']
        self.structure_preview.update(smiles)
    
    def _handle_save(self, button):
        """Handle save button click."""
        # Validate form data
        is_valid, errors = self.form_data.validate()
        
        if not is_valid:
            self.message_area.show_errors(errors)
            return
        
        # Get form data
        form_data = self.form_data.get_data()
        
        # Call save callback if provided
        if self.on_save:
            try:
                success = self.on_save(form_data, self.editing_reagent)
                if success:
                    if self.is_editing:
                        self.message_area.show_success("Reagent updated successfully!")
                        self.stop_editing()
                    else:
                        self.message_area.show_success("Reagent saved successfully!")
                        self.clear_form()
                else:
                    self.message_area.show_error("Failed to save reagent")
            except Exception as e:
                self.message_area.show_error(f"Error saving reagent: {str(e)}")
        else:
            self.message_area.show_warning("No save handler configured")
    
    def populate_from_pubchem(self, compound_data: Dict[str, Any]):
        """
        Populate form with PubChem compound data.
        
        Args:
            compound_data: Dictionary with compound information
        """
        form_data = {
            'name': compound_data.get('name', ''),
            'molecular_weight': compound_data.get('molecular_weight', 0.0),
            'smiles': compound_data.get('smiles', ''),
            'inchi': compound_data.get('inchi', ''),
            'inchikey': compound_data.get('inchikey', ''),
            'equivalents': 1.0,  # Default
            'position': 1  # Default
        }
        
        if self.reagent_type == "liquid" and 'density' in compound_data:
            form_data['density'] = compound_data.get('density', 1.0)
        
        self.form_data.set_data(form_data)
        self.message_area.show_success(
            f"Imported from PubChem: {compound_data.get('name', 'Unknown')}"
        )
    
    def start_editing(self, reagent: ReagentModel):
        """
        Start editing an existing reagent.
        
        Args:
            reagent: ReagentModel to edit
        """
        self.is_editing = True
        self.editing_reagent = reagent
        
        # Update form title
        title_widget = self.widget.children[0]
        title_widget.value = f"<h4>Edit {self.reagent_type.capitalize()} Reagent</h4>"
        
        # Populate form with reagent data
        form_data = {
            'name': reagent.name,
            'molecular_weight': reagent.molecular_weight,
            'equivalents': reagent.equivalents,
            'position': reagent.position,
            'smiles': reagent.smiles or '',
            'inchi': reagent.inchi or '',
            'inchikey': reagent.inchi_key or ''
        }
        
        if self.reagent_type == "liquid" and reagent.density:
            form_data['density'] = reagent.density
        
        self.form_data.set_data(form_data)
        
        self.message_area.show_info(
            f"Editing reagent: {reagent.name}. Modify data and click Save to update."
        )
    
    def stop_editing(self):
        """Stop editing mode and return to add mode."""
        self.is_editing = False
        self.editing_reagent = None
        
        # Update form title
        title_widget = self.widget.children[0]
        title_widget.value = f"<h4>Add {self.reagent_type.capitalize()} Reagent</h4>"
    
    def clear_form(self):
        """Clear all form fields and reset to add mode."""
        self.form_data.clear()
        self.message_area.clear()
        self.structure_preview.update("")  # Clear structure
        self.stop_editing()


class SearchForm:
    """Form for PubChem compound search."""
    
    def __init__(self, on_search: Optional[Callable] = None):
        """
        Initialize search form.
        
        Args:
            on_search: Callback function for search (receives query, search_type)
        """
        self.on_search = on_search
        self._create_form()
    
    def _create_form(self):
        """Create the search form UI."""
        # Search input
        self.search_input = widgets.Text(
            placeholder="Enter compound name, SMILES, InChI, or CAS number",
            description="Search:",
            layout=widgets.Layout(width="400px")
        )
        
        # Search type dropdown
        self.search_type = widgets.Dropdown(
            options=['name', 'smiles', 'inchi', 'inchi key', 'cas'],
            value='name',
            description='Type:',
            layout=widgets.Layout(width="180px")
        )
        
        # Search button
        self.search_button = ButtonFactory.create_primary("🔍 Search PubChem")
        self.search_button.on_click(self._handle_search)
        
        # Status area
        self.status_area = MessageArea()
        
        # Arrange components
        search_controls = widgets.HBox([
            self.search_input,
            self.search_type,
            self.search_button
        ], layout=widgets.Layout(
            align_items='flex-end',
            margin='0 0 10px 0'
        ))
        
        self.widget = widgets.VBox([
            widgets.HTML("<h4>Search PubChem Database</h4>"),
            widgets.HTML("<p style='color: #666; margin: 5px 0;'>Search for compounds and import them directly into your reagent forms</p>"),
            search_controls,
            self.status_area.widget
        ])
    
    def _handle_search(self, button):
        """Handle search button click."""
        query = self.search_input.value.strip()
        search_type = self.search_type.value
        
        if not query:
            self.status_area.show_error("Please enter a search term")
            return
        
        self.status_area.show_info(f"Searching PubChem for '{query}' ({search_type})...")
        
        if self.on_search:
            try:
                self.on_search(query, search_type)
            except Exception as e:
                self.status_area.show_error(f"Search error: {str(e)}")
    
    def show_search_status(self, message: str, message_type: str = "info"):
        """
        Show search status message.
        
        Args:
            message: Message to display
            message_type: "info", "success", "error", or "warning"
        """
        if message_type == "info":
            self.status_area.show_info(message)
        elif message_type == "success":
            self.status_area.show_success(message)
        elif message_type == "error":
            self.status_area.show_error(message)
        elif message_type == "warning":
            self.status_area.show_warning(message)


__all__ = ['ReagentFormData', 'ReagentForm', 'SearchForm']