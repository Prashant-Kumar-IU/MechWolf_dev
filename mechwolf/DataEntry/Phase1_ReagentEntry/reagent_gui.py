"""
Modern Reagent Entry GUI with Enhanced UI

Integrated reagent entry interface that works with the unified experimental 
metadata system. Provides a polished UI with validation, PubChem integration,
and structure visualization.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, Optional, List
import traceback

# Import our enhanced components
try:
    from .pubchem_service import PubChemService
    from .structure_visualization import StructureVisualization
    from .ui_components import UIComponents
    from .reagent_utils import validate_reagent_data
    from .reagent_validator import ReagentValidator
except ImportError:
    try:
        from mechwolf.DataEntry.Phase1_ReagentEntry.pubchem_service import PubChemService
        from mechwolf.DataEntry.Phase1_ReagentEntry.structure_visualization import StructureVisualization
        from mechwolf.DataEntry.Phase1_ReagentEntry.ui_components import UIComponents
        from mechwolf.DataEntry.Phase1_ReagentEntry.reagent_utils import validate_reagent_data
        from mechwolf.DataEntry.Phase1_ReagentEntry.reagent_validator import ReagentValidator
    except ImportError:
        # Create fallback classes
        class PubChemService:
            def search(self, query, search_type):
                return []
        
        class StructureVisualization:
            pass
        
        class UIComponents:
            @staticmethod
            def create_section_header(title, icon=""):
                import ipywidgets as widgets
                return widgets.HTML(f"<h3>{icon} {title}</h3>")
            
            @staticmethod
            def create_reagent_item(reagent, is_solid, on_edit, on_delete, index):
                import ipywidgets as widgets
                return widgets.HTML(f"<div>{reagent.get('name', 'Unknown')}</div>")
            
            @staticmethod
            def create_search_result_widget(compound, on_import_solid, on_import_liquid):
                import ipywidgets as widgets
                return widgets.HTML(f"<div>{compound.get('name', 'Unknown')}</div>")
        
        def validate_reagent_data(data, reagent_type):
            return []
        
        class ReagentValidator:
            def validate_reagent(self, data, reagent_type):
                return []

class ReagentEntryGUI:
    """Modern reagent entry interface using experimental metadata"""
    
    def __init__(self, experiment_manager):
        """
        Initialize reagent entry GUI
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        self.validator = ReagentValidator()
        
        # Initialize services
        self.pubchem_service = PubChemService()
        self.structure_viz = StructureVisualization()
        self.ui_components = UIComponents()
        
        # GUI state
        self.current_reagent = {}
        self.editing_index = None
        self.reagent_type = "solid"  # 'solid' or 'liquid'
        self.search_results = []
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the main UI widgets"""
        
        # Main header
        self.header = self.ui_components.create_section_header(
            "🧪 Phase 1: Reagent Entry", 
            ""
        )
        
        # Reagent type selector
        self.reagent_type_selector = widgets.ToggleButtons(
            options=[('🧱 Solid Reagents', 'solid'), ('💧 Liquid Reagents', 'liquid')],
            value='solid',
            description='Type:',
            button_style='info',
            tooltips=['Solid reagents (powders, crystals)', 'Liquid reagents (solutions, solvents)'],
            layout=widgets.Layout(width='400px')
        )
        self.reagent_type_selector.observe(self._on_reagent_type_change, names='value')
        
        # Search section
        self._create_search_widgets()
        
        # Entry form section
        self._create_form_widgets()
        
        # Reaction scale section
        self._create_scale_widgets()
        
        # Display and status areas
        self.reagents_display = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        self.status_output = widgets.Output()
        
        # Initialize display
        self._refresh_reagents_display()
        self._update_limiting_reagent_options()
        
    def _create_search_widgets(self):
        """Create PubChem search widgets"""
        
        # Search input and button
        self.search_input = widgets.Text(
            placeholder="Search PubChem (name, SMILES, InChI, CAS)",
            description="Search:",
            layout=widgets.Layout(width='300px')
        )
        
        self.search_type_dropdown = widgets.Dropdown(
            options=['name', 'smiles', 'inchi', 'inchi key', 'cas'],
            value='name',
            description='Type:',
            layout=widgets.Layout(width='120px')
        )
        
        self.search_button = widgets.Button(
            description="🔍 Search",
            button_style='primary',
            layout=widgets.Layout(width='100px')
        )
        self.search_button.on_click(self._search_pubchem)
        
        # Search results area
        self.search_results_output = widgets.Output(
            layout=widgets.Layout(
                height='300px',
                border='1px solid #ddd',
                overflow_y='auto',
                padding='10px'
            )
        )
        
    def _create_form_widgets(self):
        """Create reagent entry form widgets"""
        
        # Basic reagent information
        self.name_input = widgets.Text(
            placeholder="Enter reagent name",
            description="Name:",
            layout=widgets.Layout(width='300px')
        )
        
        self.mw_input = widgets.FloatText(
            description="MW (g/mol):",
            layout=widgets.Layout(width='150px')
        )
        
        self.eq_input = widgets.FloatText(
            description="Equivalents:",
            value=1.0,
            layout=widgets.Layout(width='150px')
        )
        
        self.position_input = widgets.IntText(
            description="Position:",
            value=1,
            layout=widgets.Layout(width='120px')
        )
        
        # Chemical identifiers
        self.inchi_input = widgets.Text(
            placeholder="InChI string (optional)",
            description="InChI:",
            layout=widgets.Layout(width='500px')
        )
        
        self.inchi_key_input = widgets.Text(
            placeholder="InChI Key (optional)",
            description="InChI Key:",
            layout=widgets.Layout(width='350px')
        )
        
        self.smiles_input = widgets.Text(
            placeholder="SMILES string (optional)",
            description="SMILES:",
            layout=widgets.Layout(width='350px')
        )
        
        # Amount inputs (different for solid vs liquid)
        self.mass_input = widgets.FloatText(
            description="Mass (mg):",
            layout=widgets.Layout(width='150px')
        )
        
        self.volume_input = widgets.FloatText(
            description="Volume (mL):",
            layout=widgets.Layout(width='150px')
        )
        
        self.density_input = widgets.FloatText(
            description="Density (g/mL):",
            value=1.0,
            layout=widgets.Layout(width='150px')
        )
        
        # Action buttons
        self.add_button = widgets.Button(
            description="➕ Add Reagent",
            button_style='success',
            layout=widgets.Layout(width='140px')
        )
        self.add_button.on_click(self._add_reagent)
        
        self.update_button = widgets.Button(
            description="📝 Update",
            button_style='warning',
            layout=widgets.Layout(width='120px'),
            disabled=True
        )
        self.update_button.on_click(self._update_reagent)
        
        self.cancel_button = widgets.Button(
            description="❌ Cancel",
            button_style='',
            layout=widgets.Layout(width='120px'),
            disabled=True
        )
        self.cancel_button.on_click(self._cancel_edit)
        
        self.clear_button = widgets.Button(
            description="🗑️ Clear",
            button_style='',
            layout=widgets.Layout(width='120px')
        )
        self.clear_button.on_click(self._clear_form)
        
    def _create_scale_widgets(self):
        """Create reaction scale widgets"""
        
        self.mass_scale_input = widgets.FloatText(
            description="Mass Scale (mg):",
            layout=widgets.Layout(width='180px')
        )
        
        self.concentration_input = widgets.FloatText(
            description="Concentration (M):",
            layout=widgets.Layout(width='180px')
        )
        
        self.solvent_input = widgets.Text(
            description="Solvent:",
            placeholder="e.g., THF, DCM",
            layout=widgets.Layout(width='200px')
        )
        
        self.limiting_reagent_dropdown = widgets.Dropdown(
            description="Limiting Reagent:",
            layout=widgets.Layout(width='250px')
        )
        
        self.save_scale_button = widgets.Button(
            description="💾 Save Scale",
            button_style='primary',
            layout=widgets.Layout(width='130px')
        )
        self.save_scale_button.on_click(self._save_reaction_scale)
        
    def _create_main_layout(self):
        """Create the main layout structure"""
        
        # Search section layout
        search_row = widgets.HBox([
            self.search_input,
            self.search_type_dropdown,
            self.search_button
        ])
        
        search_section = widgets.VBox([
            self.ui_components.create_section_header("🔍 PubChem Search"),
            search_row,
            widgets.HTML("<h5>Search Results:</h5>"),
            self.search_results_output
        ])
        
        # Form section layout
        name_row = widgets.HBox([self.name_input])
        
        molecular_row = widgets.HBox([
            self.mw_input,
            self.eq_input,
            self.position_input
        ])
        
        identifiers_section = widgets.VBox([
            self.inchi_input,
            widgets.HBox([self.inchi_key_input, self.smiles_input])
        ])
        
        # Amount inputs depend on reagent type
        if self.reagent_type == 'solid':
            amount_row = widgets.HBox([self.mass_input])
        else:
            amount_row = widgets.HBox([
                self.volume_input,
                self.density_input
            ])
        
        button_row = widgets.HBox([
            self.add_button,
            self.update_button,
            self.cancel_button,
            self.clear_button
        ])
        
        form_section = widgets.VBox([
            self.ui_components.create_section_header(f"📝 {self.reagent_type.title()} Reagent Entry"),
            name_row,
            molecular_row,
            identifiers_section,
            amount_row,
            button_row
        ])
        
        # Reaction scale section
        scale_row1 = widgets.HBox([
            self.mass_scale_input,
            self.concentration_input
        ])
        
        scale_row2 = widgets.HBox([
            self.solvent_input,
            self.limiting_reagent_dropdown
        ])
        
        scale_section = widgets.VBox([
            self.ui_components.create_section_header("⚗️ Reaction Scale"),
            scale_row1,
            scale_row2,
            self.save_scale_button
        ])
        
        # Left panel: Search and forms
        left_panel = widgets.VBox([
            self.reagent_type_selector,
            search_section,
            form_section,
            scale_section
        ], layout=widgets.Layout(width='600px', padding='10px'))
        
        # Right panel: Current reagents display
        right_panel = widgets.VBox([
            self.ui_components.create_section_header("📋 Current Reagents"),
            self.reagents_display
        ], layout=widgets.Layout(width='600px', padding='10px'))
        
        # Main layout
        main_content = widgets.HBox([left_panel, right_panel])
        
        self.main_layout = widgets.VBox([
            self.header,
            main_content,
            self.status_output
        ])
        
    def _on_reagent_type_change(self, change):
        """Handle reagent type change"""
        self.reagent_type = change['new']
        self._update_form_layout()
        self._refresh_reagents_display()
        
    def _update_form_layout(self):
        """Update form layout based on reagent type"""
        self._create_main_layout()
        
    def _search_pubchem(self, button):
        """Search PubChem and display results"""
        query = self.search_input.value.strip()
        search_type = self.search_type_dropdown.value
        
        if not query:
            with self.status_output:
                clear_output(wait=True)
                print("❌ Please enter a search term")
            return
            
        with self.status_output:
            clear_output(wait=True)
            print(f"🔍 Searching PubChem for '{query}' ({search_type})...")
            
        try:
            results = self.pubchem_service.search(query, search_type)
            self.search_results = results
            
            with self.search_results_output:
                clear_output(wait=True)
                
                if not results:
                    print("No compounds found")
                else:
                    print(f"Found {len(results)} compound(s):")
                    print("=" * 50)
                    
                    for i, compound in enumerate(results):
                        # Create search result widget
                        result_widget = self.ui_components.create_search_result_widget(
                            compound,
                            self._import_as_solid,
                            self._import_as_liquid
                        )
                        display(result_widget)
                        
            with self.status_output:
                clear_output(wait=True)
                print(f"✅ Found {len(results)} results")
                
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Search error: {e}")
    
    def _import_as_solid(self, compound: Dict[str, Any]):
        """Import compound as solid reagent"""
        self.reagent_type = 'solid'
        self.reagent_type_selector.value = 'solid'
        self._fill_form_from_compound(compound)
        
    def _import_as_liquid(self, compound: Dict[str, Any]):
        """Import compound as liquid reagent"""
        self.reagent_type = 'liquid'
        self.reagent_type_selector.value = 'liquid'
        self._fill_form_from_compound(compound)
        
    def _fill_form_from_compound(self, compound: Dict[str, Any]):
        """Fill form with compound data"""
        self.name_input.value = compound.get('name', '')
        self.mw_input.value = compound.get('molecular_weight', 0.0)
        self.inchi_input.value = compound.get('inchi', '')
        self.inchi_key_input.value = compound.get('inchikey', '')
        self.smiles_input.value = compound.get('smiles', '')
        
        if self.reagent_type == 'liquid' and compound.get('density'):
            self.density_input.value = compound['density']
        
        self._update_form_layout()
        
        with self.status_output:
            clear_output(wait=True)
            print(f"✅ Imported {compound.get('name', 'compound')} as {self.reagent_type}")
    
    def _add_reagent(self, button):
        """Add new reagent"""
        try:
            reagent_data = self._collect_form_data()
            
            # Validate reagent data
            validation_errors = validate_reagent_data(reagent_data, self.reagent_type)
            if validation_errors:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Validation errors:")
                    for error in validation_errors:
                        print(f"  • {error}")
                return
            
            # Add to experiment
            if self.reagent_type == 'solid':
                success = self.experiment.chemistry.add_solid_reagent(reagent_data)
            else:
                success = self.experiment.chemistry.add_liquid_reagent(reagent_data)
            
            if success:
                self.experiment.save()
                self._clear_form()
                self._refresh_reagents_display()
                self._update_limiting_reagent_options()
                
                with self.status_output:
                    clear_output(wait=True)
                    print(f"✅ Added {reagent_data['name']} successfully")
            else:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Failed to add reagent")
                    
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error adding reagent: {e}")
                traceback.print_exc()
    
    def _update_reagent(self, button):
        """Update existing reagent"""
        if self.editing_index is None:
            return
            
        try:
            reagent_data = self._collect_form_data()
            
            # Validate reagent data
            validation_errors = validate_reagent_data(reagent_data, self.reagent_type)
            if validation_errors:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Validation errors:")
                    for error in validation_errors:
                        print(f"  • {error}")
                return
            
            # Update in experiment
            chemistry_data = self.experiment.chemistry.get_data()
            # Use reagent type from current GUI state (which was set during _edit_reagent)
            if self.reagent_type == 'solid':
                if 'solid_reagents' in chemistry_data and self.editing_index < len(chemistry_data['solid_reagents']):
                    chemistry_data['solid_reagents'][self.editing_index] = reagent_data
                    success = self.experiment.chemistry.save_data(chemistry_data)
                else:
                    success = False
            else:
                if 'liquid_reagents' in chemistry_data and self.editing_index < len(chemistry_data['liquid_reagents']):
                    chemistry_data['liquid_reagents'][self.editing_index] = reagent_data
                    success = self.experiment.chemistry.save_data(chemistry_data)
                else:
                    success = False
            
            if success:
                self.experiment.save()
                self._cancel_edit()
                self._refresh_reagents_display()
                self._update_limiting_reagent_options()
                
                with self.status_output:
                    clear_output(wait=True)
                    print(f"✅ Updated {reagent_data['name']} successfully")
            else:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Failed to update reagent")
                    
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error updating reagent: {e}")
    
    def _edit_reagent(self, index: int, reagent: Dict[str, Any]):
        """Enter edit mode for a reagent"""
        self.editing_index = index
        
        # Determine reagent type based on data structure and set GUI state
        is_solid = 'mass' in reagent
        self.reagent_type = 'solid' if is_solid else 'liquid'
        self.reagent_type_selector.value = self.reagent_type
        
        # Fill form with reagent data
        self.name_input.value = reagent.get("name", "")
        self.mw_input.value = reagent.get("molecular_weight", 0.0)
        self.eq_input.value = reagent.get("eq", 1.0)
        self.position_input.value = reagent.get("position", 1)
        self.inchi_input.value = reagent.get("inChi", "")
        self.inchi_key_input.value = reagent.get("inChi_Key", "")
        self.smiles_input.value = reagent.get("SMILES", "")
        
        if is_solid:
            self.mass_input.value = reagent.get("mass", 0.0)
        else:
            self.volume_input.value = reagent.get("volume", 0.0)
            self.density_input.value = reagent.get("density", 1.0)
        
        # Update button states
        self.add_button.disabled = True
        self.update_button.disabled = False
        self.cancel_button.disabled = False
        
        # Update layout to match reagent type
        self._update_form_layout()
        
        with self.status_output:
            clear_output(wait=True)
            print(f"📝 Editing {reagent.get('name', 'reagent')}")
    
    def _delete_reagent(self, index: int, reagent: Dict[str, Any]):
        """Delete a reagent"""
        try:
            chemistry_data = self.experiment.chemistry.get_data()
            
            # Determine reagent type based on data structure (solid reagents have 'mass', liquid have 'volume')
            is_solid = 'mass' in reagent
            
            if is_solid:
                if 'solid_reagents' in chemistry_data and index < len(chemistry_data['solid_reagents']):
                    del chemistry_data['solid_reagents'][index]
                    success = True
                else:
                    success = False
            else:
                if 'liquid_reagents' in chemistry_data and index < len(chemistry_data['liquid_reagents']):
                    del chemistry_data['liquid_reagents'][index]
                    success = True
                else:
                    success = False
            
            if success:
                self.experiment.chemistry.save_data(chemistry_data)
                self.experiment.save()
                self._refresh_reagents_display()
                self._update_limiting_reagent_options()
                
                with self.status_output:
                    clear_output(wait=True)
                    print(f"🗑️ Deleted {reagent.get('name', 'reagent')}")
            else:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Failed to delete reagent")
                    
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error deleting reagent: {e}")
    
    def _cancel_edit(self, button=None):
        """Cancel editing mode"""
        self.editing_index = None
        self.add_button.disabled = False
        self.update_button.disabled = True
        self.cancel_button.disabled = True
        self._clear_form()
        
    def _clear_form(self, button=None):
        """Clear all form inputs"""
        self.name_input.value = ""
        self.mw_input.value = 0.0
        self.inchi_input.value = ""
        self.inchi_key_input.value = ""
        self.smiles_input.value = ""
        self.eq_input.value = 1.0
        self.position_input.value = 1
        self.mass_input.value = 0.0
        self.volume_input.value = 0.0
        self.density_input.value = 1.0
        
        with self.status_output:
            clear_output(wait=True)
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Collect data from form inputs"""
        data = {
            "name": self.name_input.value.strip(),
            "molecular_weight": self.mw_input.value,
            "eq": self.eq_input.value,
            "position": self.position_input.value
        }
        
        # Add optional fields if provided
        if self.inchi_input.value.strip():
            data["inChi"] = self.inchi_input.value.strip()
        if self.inchi_key_input.value.strip():
            data["inChi_Key"] = self.inchi_key_input.value.strip()
        if self.smiles_input.value.strip():
            data["SMILES"] = self.smiles_input.value.strip()
            
        # Add type-specific fields
        if self.reagent_type == 'solid':
            data["mass"] = self.mass_input.value
        else:
            data["volume"] = self.volume_input.value
            data["density"] = self.density_input.value
            
        return data
    
    def _save_reaction_scale(self, button):
        """Save reaction scale information"""
        try:
            chemistry_data = self.experiment.chemistry.get_data()
            
            if self.mass_scale_input.value:
                chemistry_data["mass_scale"] = self.mass_scale_input.value
            if self.concentration_input.value:
                chemistry_data["concentration"] = self.concentration_input.value
            if self.solvent_input.value.strip():
                chemistry_data["solvent"] = self.solvent_input.value.strip()
            if self.limiting_reagent_dropdown.value:
                chemistry_data["limiting_reagent"] = self.limiting_reagent_dropdown.value
            
            self.experiment.chemistry.save_data(chemistry_data)
            self.experiment.save()
            
            with self.status_output:
                clear_output(wait=True)
                print("✅ Reaction scale saved successfully")
                
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error saving reaction scale: {e}")
    
    def _refresh_reagents_display(self):
        """Refresh the reagents display using enhanced widgets"""
        with self.reagents_display:
            clear_output(wait=True)
            
            chemistry_data = self.experiment.chemistry.get_data()
            
            # Display solid reagents
            solid_reagents = chemistry_data.get("solid_reagents", [])
            if solid_reagents:
                display(self.ui_components.create_section_header("🧱 Solid Reagents"))
                for i, reagent in enumerate(solid_reagents):
                    reagent_widget = self.ui_components.create_reagent_item(
                        reagent, True, self._edit_reagent, self._delete_reagent, i
                    )
                    display(reagent_widget)
            
            # Display liquid reagents
            liquid_reagents = chemistry_data.get("liquid_reagents", [])
            if liquid_reagents:
                display(self.ui_components.create_section_header("💧 Liquid Reagents"))
                for i, reagent in enumerate(liquid_reagents):
                    reagent_widget = self.ui_components.create_reagent_item(
                        reagent, False, self._edit_reagent, self._delete_reagent, i
                    )
                    display(reagent_widget)
            
            # Display reaction scale info
            scale_info = []
            if chemistry_data.get("mass_scale"):
                scale_info.append(f"Mass Scale: {chemistry_data['mass_scale']} mg")
            if chemistry_data.get("concentration"):
                scale_info.append(f"Concentration: {chemistry_data['concentration']} M")
            if chemistry_data.get("solvent"):
                scale_info.append(f"Solvent: {chemistry_data['solvent']}")
            if chemistry_data.get("limiting_reagent"):
                scale_info.append(f"Limiting Reagent: {chemistry_data['limiting_reagent']}")
            
            if scale_info:
                display(self.ui_components.create_section_header("⚗️ Reaction Scale"))
                scale_html = "<br>".join(scale_info)
                display(widgets.HTML(f"<div style='padding: 10px;'>{scale_html}</div>"))
            
            if not solid_reagents and not liquid_reagents:
                display(widgets.HTML(
                    "<div style='text-align: center; color: #666; padding: 40px;'>"
                    "No reagents added yet. Use the form to add reagents."
                    "</div>"
                ))
    
    def _update_limiting_reagent_options(self):
        """Update limiting reagent dropdown options"""
        chemistry_data = self.experiment.chemistry.get_data()
        
        options = [""]  # Empty option
        
        # Add solid reagents
        for reagent in chemistry_data.get("solid_reagents", []):
            if reagent.get("name"):
                options.append(reagent["name"])
        
        # Add liquid reagents
        for reagent in chemistry_data.get("liquid_reagents", []):
            if reagent.get("name"):
                options.append(reagent["name"])
        
        self.limiting_reagent_dropdown.options = options
        
        # Set current value if it exists
        current_limiting = chemistry_data.get("limiting_reagent")
        if current_limiting and current_limiting in options:
            self.limiting_reagent_dropdown.value = current_limiting
    
    def display(self):
        """Display the GUI"""
        self._create_main_layout()
        display(self.main_layout)
    
    def get_current_data(self) -> Dict[str, Any]:
        """Get current chemistry data"""
        return self.experiment.chemistry.get_data()