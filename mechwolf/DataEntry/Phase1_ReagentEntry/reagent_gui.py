"""
Modern Reagent Entry GUI

Integrated reagent entry interface that works with the unified experimental 
metadata system. Provides modern UI with validation and PubChem integration.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, Optional, List
import traceback

# Import from ReagentUI components that we'll reuse
try:
    from ..ReagentUI.PubChemService import PubChemService
    from ..ReagentUI.StructureVisualization import StructureVisualization
    from ..ReagentUI.UIComponents import UIComponents
except ImportError:
    # Fallback if ReagentUI components are not available
    PubChemService = None
    StructureVisualization = None
    UIComponents = None

from .reagent_validator import ReagentValidator


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
        
        # Initialize services if available
        self.pubchem_service = PubChemService() if PubChemService else None
        self.structure_viz = StructureVisualization() if StructureVisualization else None
        self.ui_components = UIComponents() if UIComponents else None
        
        # GUI state
        self.current_reagent = {}
        self.editing_index = None
        self.reagent_type = "solid"  # 'solid' or 'liquid'
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the main UI widgets"""
        
        # Header
        self.header = widgets.HTML("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0; text-align: center;'>
                🧪 Phase 1: Reagent Entry
            </h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0; text-align: center;'>
                Add and manage reagents for your experiment
            </p>
        </div>
        """)
        
        # Reagent type selector
        self.reagent_type_selector = widgets.ToggleButtons(
            options=[('🧱 Solid Reagents', 'solid'), ('💧 Liquid Reagents', 'liquid')],
            value='solid',
            description='Type:',
            button_style='info',
            tooltips=['Solid reagents (powders, crystals)', 'Liquid reagents (solutions, solvents)']
        )
        self.reagent_type_selector.observe(self._on_reagent_type_change, names='value')
        
        # Reagent name input with PubChem lookup
        self.name_input = widgets.Text(
            placeholder="Enter reagent name",
            description="Name:",
            layout=widgets.Layout(width='300px')
        )
        
        self.pubchem_button = widgets.Button(
            description="🔍 PubChem",
            button_style='info',
            layout=widgets.Layout(width='100px'),
            disabled=self.pubchem_service is None
        )
        self.pubchem_button.on_click(self._lookup_pubchem)
        
        # Molecular data inputs
        self.mw_input = widgets.FloatText(
            description="MW (g/mol):",
            layout=widgets.Layout(width='150px')
        )
        
        self.inchi_input = widgets.Text(
            placeholder="InChI string (optional)",
            description="InChI:",
            layout=widgets.Layout(width='400px')
        )
        
        self.inchi_key_input = widgets.Text(
            placeholder="InChI Key (optional)",
            description="InChI Key:",
            layout=widgets.Layout(width='300px')
        )
        
        # Stoichiometry inputs
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
        
        # Reaction scale inputs
        self.scale_header = widgets.HTML("<h4>Reaction Scale</h4>")
        
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
        
        # Display area for current reagents
        self.reagents_display = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Status/feedback area
        self.status_output = widgets.Output()
        
        # Update initial display
        self._update_form_layout()
        self._refresh_reagents_display()
        self._update_limiting_reagent_options()
        
    def _create_main_layout(self):
        """Create the main layout structure"""
        
        # Input form layout
        name_row = widgets.HBox([
            self.name_input,
            self.pubchem_button
        ])
        
        molecular_row = widgets.HBox([
            self.mw_input,
            self.eq_input,
            self.position_input
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
            name_row,
            self.inchi_input,
            self.inchi_key_input,
            molecular_row,
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
            self.scale_header,
            scale_row1,
            scale_row2,
            self.save_scale_button
        ])
        
        # Left panel: Input forms
        left_panel = widgets.VBox([
            self.reagent_type_selector,
            widgets.HTML("<h4>Reagent Details</h4>"),
            form_section,
            widgets.HTML("<br>"),
            scale_section
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        # Right panel: Current reagents display
        right_panel = widgets.VBox([
            widgets.HTML("<h4>Current Reagents</h4>"),
            self.reagents_display
        ], layout=widgets.Layout(width='600px', padding='10px'))
        
        # Main layout
        main_content = widgets.HBox([left_panel, right_panel])
        
        self.main_layout = widgets.VBox([
            self.header,
            main_content,
            self.status_output
        ])
        
    def _update_form_layout(self):
        """Update form layout based on reagent type"""
        self._create_main_layout()
        
    def _on_reagent_type_change(self, change):
        """Handle reagent type change"""
        self.reagent_type = change['new']
        self._update_form_layout()
        self._refresh_reagents_display()
        
    def _lookup_pubchem(self, button):
        """Lookup reagent in PubChem"""
        if not self.pubchem_service or not self.name_input.value:
            return
            
        with self.status_output:
            clear_output(wait=True)
            print("🔍 Looking up in PubChem...")
            
        try:
            compound_data = self.pubchem_service.get_compound_by_name(self.name_input.value)
            
            if compound_data:
                # Fill in the form with PubChem data
                if 'molecular_weight' in compound_data:
                    self.mw_input.value = compound_data['molecular_weight']
                if 'inchi' in compound_data:
                    self.inchi_input.value = compound_data['inchi']
                if 'inchi_key' in compound_data:
                    self.inchi_key_input.value = compound_data['inchi_key']
                    
                with self.status_output:
                    clear_output(wait=True)
                    print("✅ PubChem data loaded successfully")
            else:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Compound not found in PubChem")
                    
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error looking up compound: {e}")
    
    def _add_reagent(self, button):
        """Add new reagent"""
        try:
            reagent_data = self._collect_form_data()
            
            # Validate reagent data
            validation_errors = self.validator.validate_reagent(reagent_data, self.reagent_type)
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
            validation_errors = self.validator.validate_reagent(reagent_data, self.reagent_type)
            if validation_errors:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Validation errors:")
                    for error in validation_errors:
                        print(f"  • {error}")
                return
            
            # Update in experiment
            if self.reagent_type == 'solid':
                success = self.experiment.chemistry.update_solid_reagent(self.editing_index, reagent_data)
            else:
                success = self.experiment.chemistry.update_liquid_reagent(self.editing_index, reagent_data)
            
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
            "name": self.name_input.value,
            "molecular_weight": self.mw_input.value,
            "eq": self.eq_input.value or None,
            "position": self.position_input.value or None
        }
        
        # Add optional fields if provided
        if self.inchi_input.value:
            data["inChi"] = self.inchi_input.value
        if self.inchi_key_input.value:
            data["inChi_Key"] = self.inchi_key_input.value
            
        # Add type-specific fields
        if self.reagent_type == 'solid':
            data["mass"] = self.mass_input.value
        else:
            data["volume"] = self.volume_input.value or None
            data["density"] = self.density_input.value
            
        return data
    
    def _save_reaction_scale(self, button):
        """Save reaction scale information"""
        try:
            self.experiment.chemistry.set_reaction_scale(
                mass_scale=self.mass_scale_input.value,
                concentration=self.concentration_input.value,
                solvent=self.solvent_input.value
            )
            
            if self.limiting_reagent_dropdown.value:
                self.experiment.chemistry.set_limiting_reagent(self.limiting_reagent_dropdown.value)
            
            self.experiment.save()
            
            with self.status_output:
                clear_output(wait=True)
                print("✅ Reaction scale saved successfully")
                
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error saving reaction scale: {e}")
    
    def _refresh_reagents_display(self):
        """Refresh the reagents display"""
        with self.reagents_display:
            clear_output(wait=True)
            
            chemistry_data = self.experiment.chemistry.get_data()
            
            # Display solid reagents
            solid_reagents = chemistry_data.get("solid_reagents", [])
            if solid_reagents:
                print("🧱 SOLID REAGENTS")
                print("=" * 50)
                for i, reagent in enumerate(solid_reagents):
                    self._display_reagent(reagent, i, 'solid')
                print()
            
            # Display liquid reagents
            liquid_reagents = chemistry_data.get("liquid_reagents", [])
            if liquid_reagents:
                print("💧 LIQUID REAGENTS")
                print("=" * 50)
                for i, reagent in enumerate(liquid_reagents):
                    self._display_reagent(reagent, i, 'liquid')
                print()
            
            # Display reaction scale
            mass_scale = chemistry_data.get("mass_scale")
            concentration = chemistry_data.get("concentration")
            solvent = chemistry_data.get("solvent")
            limiting_reagent = chemistry_data.get("limiting_reagent")
            
            if any([mass_scale, concentration, solvent, limiting_reagent]):
                print("⚗️ REACTION SCALE")
                print("=" * 50)
                if mass_scale:
                    print(f"Mass Scale: {mass_scale} mg")
                if concentration:
                    print(f"Concentration: {concentration} M")
                if solvent:
                    print(f"Solvent: {solvent}")
                if limiting_reagent:
                    print(f"Limiting Reagent: {limiting_reagent}")
    
    def _display_reagent(self, reagent: Dict[str, Any], index: int, reagent_type: str):
        """Display a single reagent with edit/delete buttons"""
        name = reagent.get("name", "Unknown")
        mw = reagent.get("molecular_weight", 0)
        eq = reagent.get("eq", "N/A")
        
        print(f"{index + 1}. {name}")
        print(f"   MW: {mw} g/mol | Eq: {eq}")
        
        if reagent_type == 'solid':
            mass = reagent.get("mass", 0)
            print(f"   Mass: {mass} mg")
        else:
            volume = reagent.get("volume", "N/A")
            density = reagent.get("density", 1.0)
            print(f"   Volume: {volume} mL | Density: {density} g/mL")
        
        print()
    
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