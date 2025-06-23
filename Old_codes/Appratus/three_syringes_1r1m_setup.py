"""
Three Syringes, 1 Reaction Coil, 1 Mixer Setup

This module provides the specific implementation for a three-syringe flow setup
with one reaction coil and one mixer.
"""
from typing import Dict, Any, List
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

from .base_classes import BaseComponentApp, BaseApparatusCreator
from .config_templates import get_config
from .FlowSetupUtils import check_required_fields


class ThreeSyringes1R1MComponentApp(BaseComponentApp):
    """Component app for three syringes, 1 reaction coil, 1 mixer setup"""
    
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str):
        config = get_config('three_syringes_1r_1m')
        super().__init__(pumps, json_file, config)
    
    def _gather_inputs(self) -> None:
        """Gather inputs specific to three syringes setup"""
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
            "coil_a_raw": widget_values["coil_a"],
            "coil_x_raw": widget_values["coil_x"],
        }
        
        # Validate required fields
        required_fields = [
            "apparatus_name", "vessel1_name", "vessel1_desc",
            "vessel2_name", "vessel2_desc", "vessel3_name", "vessel3_desc",
            "product_vessel_name", "product_vessel_desc",
            "reaction_tube_id_raw", "reaction_tube_od_raw", "reaction_tube_material",
            "coil_a_raw", "coil_x_raw"
        ]
        check_required_fields(self.data, required_fields)
    
    def _create_apparatus_config(self) -> Dict[str, Any]:
        """Create apparatus config for three syringes setup"""
        config = {
            "apparatus_name": self.data["apparatus_name"],
            "setup_type": "three_syringes_1r_1m",
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


class ThreeSyringes1R1MApparatusCreator(BaseApparatusCreator):
    """Apparatus creator for three syringes, 1 reaction coil, 1 mixer setup"""
    
    def _create_component_app(self):
        """Create the three syringes component app"""
        return ThreeSyringes1R1MComponentApp(self.pumps, self.json_file)
    
    def _build_apparatus(self) -> mw.Apparatus:
        """Build apparatus for three syringes setup"""
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
        
        # Create T Mixer
        def Tmixer(name: str) -> mw.TMixer:
            return mw.TMixer(name=name)
        
        T1 = Tmixer(coil_x)
        
        # Build apparatus connections for three vessels
        if self.pump_type == "single-channel":
            # Assuming we have at least 3 pumps for single-channel
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
            A.add(self.pumps[2], vessel3, coil_a)
        elif self.pump_type == "dual-channel":
            # Use dual-channel pump efficiently
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)
            if len(self.pumps) > 1:
                A.add(self.pumps[1], vessel3, coil_a)
            else:
                # If only one dual-channel pump, we might need to handle this differently
                # For now, assume we can connect vessel3 to the same pump
                A.add(self.pumps[0], vessel3, coil_a)
        
        # Add mixer and coil connections
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        A.add(vessel3, T1, coil_a)
        A.add(T1, product_vessel, coil_x)
        
        return A
