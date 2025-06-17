"""
Three Syringes, 2 Reaction Coils, 2 Mixers Setup

This module provides the specific implementation for a three-syringe flow setup
with two reaction coils and two mixers.
"""
from typing import Dict, Any, List
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

from .base_classes import BaseComponentApp, BaseApparatusCreator
from .config_templates import get_config
from .FlowSetupUtils import check_required_fields


class ThreeSyringes2R2MComponentApp(BaseComponentApp):
    """Component app for three syringes, 2 reaction coils, 2 mixers setup"""
    
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str):
        config = get_config('three_syringes_2r_2m')
        super().__init__(pumps, json_file, config)
    
    def _gather_inputs(self) -> None:
        """Gather inputs specific to three syringes, 2R2M setup"""
        widget_values = self.widget_manager.get_widget_values()
        
        self.data = {
            "apparatus_name": widget_values["apparatus_name"],
            "vessel1_name": widget_values["vessel1_name"],
            "vessel1_desc": widget_values["vessel1_desc"],
            "vessel2_name": widget_values["vessel2_name"],
            "vessel2_desc": widget_values["vessel2_desc"],
            "vessel3_name": widget_values["vessel3_name"],
            "vessel3_desc": widget_values["vessel3_desc"],
            "product_vessel_name": widget_values["product_vessel_name"],
            "product_vessel_desc": widget_values["product_vessel_desc"],
            "reaction_tube_id_raw": widget_values["reaction_tube1_id"],
            "reaction_tube_od_raw": widget_values["reaction_tube1_od"],
            "reaction_tube_material": widget_values["reaction_tube1_material"],
            "using_mixer": widget_values["using_mixer"],
            "mixer_tube_id_raw": widget_values["mixer1_tube_id"],
            "mixer_tube_od_raw": widget_values["mixer1_tube_od"],
            "mixer_tube_material": widget_values["mixer1_tube_material"],
            # All four coils for 2R2M setup
            "coil_a_raw": widget_values["coil_a"],
            "coil_x_raw": widget_values["coil_x"],
            "coil_b_raw": widget_values["coil_b"],
            "coil_y_raw": widget_values["coil_y"],
        }
        
        # Validate required fields
        required_fields = [
            "apparatus_name", "vessel1_name", "vessel1_desc",
            "vessel2_name", "vessel2_desc", "vessel3_name", "vessel3_desc",
            "product_vessel_name", "product_vessel_desc",
            "reaction_tube_id_raw", "reaction_tube_od_raw", "reaction_tube_material",
            "coil_a_raw", "coil_x_raw", "coil_b_raw", "coil_y_raw"
        ]
        check_required_fields(self.data, required_fields)
    
    def _create_apparatus_config(self) -> Dict[str, Any]:
        """Create apparatus config for three syringes, 2R2M setup"""
        config = {
            "apparatus_name": self.data["apparatus_name"],
            "setup_type": "three_syringes_2r_2m",
            "vessels": [
                {
                    "name": self.data["vessel1_name"],
                    "description": self.data["vessel1_desc"],
                },
                {
                    "name": self.data["vessel2_name"],
                    "description": self.data["vessel2_desc"],
                },
                {
                    "name": self.data["vessel3_name"],
                    "description": self.data["vessel3_desc"],
                },
                {
                    "name": self.data["product_vessel_name"],
                    "description": self.data["product_vessel_desc"],
                },
            ],
            "tubes": {
                "reaction": {
                    "ID": self.data["reaction_tube_ID"],
                    "OD": self.data["reaction_tube_OD"],
                    "material": self.data["reaction_tube_material"],
                }
            },
            "coils": [
                {"letter": "a", "length": self.data["coil_a_length"]},
                {"letter": "x", "length": self.data["coil_x_length"]},
                {"letter": "b", "length": self.data["coil_b_length"]},
                {"letter": "y", "length": self.data["coil_y_length"]},
            ],
            "using_mixer": self.data["using_mixer"],
        }
        
        # Add mixer tube details if using mixer
        if self.data["using_mixer"]:
            config["tubes"]["mixer"] = {
                "ID": self.data["mixer_tube_ID"],
                "OD": self.data["mixer_tube_OD"],
                "material": self.data["mixer_tube_material"],
            }
        
        return config


class ThreeSyringes2R2MApparatusCreator(BaseApparatusCreator):
    """Apparatus creator for three syringes, 2 reaction coils, 2 mixers setup"""
    
    def _create_component_app(self):
        """Create the three syringes 2R2M component app"""
        return ThreeSyringes2R2MComponentApp(self.pumps, self.json_file)
    
    def _build_apparatus(self) -> mw.Apparatus:
        """Build apparatus for three syringes, 2R2M setup"""
        config = self._load_config()
        print(f"Creating apparatus: {config['apparatus_name']}")
        
        # Create apparatus
        A = mw.Apparatus(config["apparatus_name"])
        
        # Create vessels
        vessels = [
            mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]
        ]
        vessel1, vessel2, vessel3, product_vessel = vessels
        
        # Create tubes and coils
        reaction_tube = lambda length: self._make_tube(config["tubes"]["reaction"], length)
        if config["using_mixer"]:
            mixer_tube = lambda length: self._make_tube(config["tubes"]["mixer"], length)
        
        # Get coil lengths by letter
        coil_lengths = {coil["letter"]: coil["length"] for coil in config["coils"]}
        coil_a = reaction_tube(coil_lengths["a"])
        coil_x = reaction_tube(coil_lengths["x"])
        coil_b = reaction_tube(coil_lengths["b"])
        coil_y = reaction_tube(coil_lengths["y"])
        
        # Create T Mixers
        def Tmixer(name: str) -> mw.TMixer:
            return mw.TMixer(name=name)
        
        T1 = Tmixer("T1")  # First mixer
        T2 = Tmixer("T2")  # Second mixer
        
        # Build apparatus connections for 2R2M setup
        # This is a more complex setup with two reaction pathways
        
        if self.pump_type == "single-channel":
            # Assuming we have at least 3 pumps for single-channel
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
            A.add(self.pumps[2], vessel3, coil_b)
        elif self.pump_type == "dual-channel":
            # Use dual-channel pump efficiently
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)
            if len(self.pumps) > 1:
                A.add(self.pumps[1], vessel3, coil_b)
            else:
                A.add(self.pumps[0], vessel3, coil_b)
        
        # Add mixer and coil connections for 2R2M configuration
        # First reaction pathway: vessels 1 & 2 -> T1 -> coil_x
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        
        # Second reaction pathway: vessel 3 -> coil_b -> T2
        A.add(vessel3, T2, coil_b)
        
        # Combine pathways: T1 -> coil_x -> T2 -> coil_y -> product
        A.add(T1, T2, coil_x)
        A.add(T2, product_vessel, coil_y)
        
        return A
