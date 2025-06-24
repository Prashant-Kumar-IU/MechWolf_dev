"""
Flexible n-Syringes to Reaction Mix Vessel Setup

This module provides a flexible implementation that allows users to define
variable numbers of vessels for more complex flow chemistry setups.
"""
from typing import Dict, Any, List, Optional
import json
import ipywidgets as widgets
from IPython.display import display, clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

from .base_classes import BaseApparatusCreator
from .config_templates import get_config
from .data_manager import DataManager
from .FlowSetupUtils import (
    parse_tube_dimension,
    parse_numeric_foot,
    validate_required_fields_with_rmv,
)
from .error_handler import ValidationError


class FlexibleSetupComponentApp:
    """Component app for flexible n-syringes setup"""
    
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str):
        self.pumps: List[HarvardSyringePump] = pumps
        self.data_manager: DataManager = DataManager(json_file)
        self.data: Dict[str, Any] = {}
        self.setup_complete: bool = False
        self.temp_vessels: List[Dict[str, Any]] = []
        self.save_setup_button: Optional[widgets.Button] = None
        self.existing_config: Optional[Dict[str, Any]] = self.data_manager.load_config()
    
    def create_widgets(self) -> None:
        """Create widgets for flexible setup"""
        # Apparatus name
        apparatus_name_label = widgets.Label("Apparatus Name:")
        self.apparatus_name_widget = widgets.Text(
            value=self.existing_config.get("apparatus_name", "") if self.existing_config else "",
            layout=widgets.Layout(width="50%"),
        )
        
        # Reaction mixture vessel
        rmv_name_label = widgets.Label("Reaction Mixture Vessel Name:")
        self.product_vessel_name_widget = widgets.Text(
            value=self.existing_config.get("reaction_mixture_vessel", {}).get("name", "")
            if self.existing_config else "",
            layout=widgets.Layout(width="50%"),
        )
        
        rmv_desc_label = widgets.Label("Reaction Mixture Vessel Description:")
        self.product_vessel_desc_widget = widgets.Text(
            value=self.existing_config.get("reaction_mixture_vessel", {}).get("description", "")
            if self.existing_config else "",
            layout=widgets.Layout(width="50%"),
        )
        
        # Buttons
        add_vessel_button = widgets.Button(description="Add Vessel", button_style="info")
        add_vessel_button.on_click(self.vessel_window)
        
        self.save_setup_button = widgets.Button(description="Save Setup", button_style="success")
        self.save_setup_button.on_click(self.create_setup)
        
        # Layout
        left_container = widgets.VBox([
            widgets.VBox([apparatus_name_label, self.apparatus_name_widget]),
            widgets.VBox([rmv_name_label, self.product_vessel_name_widget]),
            widgets.VBox([rmv_desc_label, self.product_vessel_desc_widget]),
            add_vessel_button,
            self.save_setup_button,
        ], layout=widgets.Layout(width="40%", margin="0 20px 0 0"))
        
        # Vessel display area
        self.vessel_display_area = widgets.VBox([])
        right_container = widgets.VBox([
            widgets.Label("Vessels:", style={'font_weight': 'bold'}),
            self.vessel_display_area
        ], layout=widgets.Layout(width="55%"))
        
        # Main container
        self.widget_container = widgets.HBox([left_container, right_container])
        display(self.widget_container)
        
        # Load existing vessels if available
        if self.existing_config and "vessels" in self.existing_config:
            self.temp_vessels = self.existing_config["vessels"].copy()
            self.update_vessel_display()
    
    def vessel_window(self, b: widgets.Button, vessel: Optional[Dict[str, Any]] = None) -> None:
        """Open vessel configuration window"""
        clear_output()
        
        # Create vessel input widgets
        name_widget = widgets.Text(
            value=vessel.get("name", "") if vessel else "",
            placeholder="Vessel Name",
            layout=widgets.Layout(width="50%")
        )
        
        desc_widget = widgets.Text(
            value=vessel.get("description", "") if vessel else "",
            placeholder="Vessel Description",
            layout=widgets.Layout(width="50%")
        )
        
        # Buttons
        save_button = widgets.Button(description="Save Vessel", button_style="success")
        cancel_button = widgets.Button(description="Cancel", button_style="warning")
        
        def save_vessel(b):
            vessel_data = {
                "name": name_widget.value.strip(),
                "description": desc_widget.value.strip()
            }
            
            if not vessel_data["name"] or not vessel_data["description"]:
                print("Error: Both name and description are required!")
                return
            
            if vessel:  # Editing existing vessel
                index = self.temp_vessels.index(vessel)
                self.temp_vessels[index] = vessel_data
            else:  # Adding new vessel
                self.temp_vessels.append(vessel_data)
            
            self.create_widgets()  # Refresh the main interface
        
        def cancel_edit(b):
            self.create_widgets()  # Return to main interface
        
        save_button.on_click(save_vessel)
        cancel_button.on_click(cancel_edit)
        
        # Display vessel configuration interface
        vessel_config = widgets.VBox([
            widgets.Label("Configure Vessel:", style={'font_weight': 'bold'}),
            widgets.VBox([widgets.Label("Vessel Name:"), name_widget]),
            widgets.VBox([widgets.Label("Vessel Description:"), desc_widget]),
            widgets.HBox([save_button, cancel_button])
        ])
        
        display(vessel_config)
    
    def update_vessel_display(self) -> None:
        """Update the display of vessels"""
        vessel_items = []
        
        for i, vessel in enumerate(self.temp_vessels):
            # Create vessel display with edit/delete buttons
            edit_button = widgets.Button(description="Edit", button_style="info", layout=widgets.Layout(width="60px"))
            delete_button = widgets.Button(description="Delete", button_style="danger", layout=widgets.Layout(width="60px"))
            
            # Use closures to capture the vessel reference
            def make_edit_handler(v):
                return lambda b: self.vessel_window(b, v)
            
            def make_delete_handler(v):
                return lambda b: self.delete_vessel(v)
            
            edit_button.on_click(make_edit_handler(vessel))
            delete_button.on_click(make_delete_handler(vessel))
            
            vessel_item = widgets.HBox([
                widgets.Label(f"{i+1}. {vessel['name']}: {vessel['description']}", 
                            layout=widgets.Layout(width="300px")),
                edit_button,
                delete_button
            ])
            
            vessel_items.append(vessel_item)
        
        self.vessel_display_area.children = vessel_items
    
    def delete_vessel(self, vessel: Dict[str, Any]) -> None:
        """Delete a vessel from the temporary list"""
        if vessel in self.temp_vessels:
            self.temp_vessels.remove(vessel)
            self.update_vessel_display()
    
    def create_setup(self, b: widgets.Button) -> None:
        """Create and save the setup"""
        try:
            self._gather_inputs()
            
            # Validate inputs
            validate_required_fields_with_rmv(
                self.data["apparatus_name"],
                self.data["product_vessel_name"],
                self.data["product_vessel_desc"],
                self.temp_vessels
            )
            
            # Create apparatus configuration
            apparatus_config = self._create_apparatus_config()
            self.data_manager.save_config(apparatus_config)
            
            self.widget_container.close()
            self.setup_complete = True
            clear_output()
            print("Flexible setup configuration saved successfully!")
            
        except ValidationError as e:
            print(f"Validation Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def _gather_inputs(self) -> None:
        """Gather inputs from widgets"""
        self.data = {
            "apparatus_name": self.apparatus_name_widget.value.strip(),
            "product_vessel_name": self.product_vessel_name_widget.value.strip(),
            "product_vessel_desc": self.product_vessel_desc_widget.value.strip(),
        }
    
    def _create_apparatus_config(self) -> Dict[str, Any]:
        """Create apparatus configuration"""
        return {
            "apparatus_name": self.data["apparatus_name"],
            "setup_type": "flexible_setup",
            "vessels": self.temp_vessels.copy(),
            "reaction_mixture_vessel": {
                "name": self.data["product_vessel_name"],
                "description": self.data["product_vessel_desc"]
            }
        }


class FlexibleSetupApparatusCreator(BaseApparatusCreator):
    """Apparatus creator for flexible setup"""
    
    def _create_component_app(self):
        """Create the flexible setup component app"""
        return FlexibleSetupComponentApp(self.pumps, self.json_file)
    
    def _build_apparatus(self) -> mw.Apparatus:
        """Build apparatus for flexible setup"""
        config = self._load_config()
        print(f"Creating apparatus: {config['apparatus_name']}")
        
        # Create apparatus
        A = mw.Apparatus(config["apparatus_name"])
        
        # Create vessels from configuration
        input_vessels = [
            mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]
        ]
        
        rmv_config = config["reaction_mixture_vessel"]
        product_vessel = mw.Vessel(rmv_config["description"], name=rmv_config["name"])
        
        # For flexible setup, create a simple connection pattern
        # This is a basic implementation - could be extended for more complex topologies
        
        # Create basic tubing (this could be made configurable)
        basic_tube = mw.Tube(length="12 in", ID="1/16 in", OD="1/8 in", material="PFA")
        
        # Connect each input vessel to pumps (if available)
        for i, vessel in enumerate(input_vessels):
            if i < len(self.pumps):
                A.add(self.pumps[i], vessel, basic_tube)
                A.add(vessel, product_vessel, basic_tube)
        
        return A
