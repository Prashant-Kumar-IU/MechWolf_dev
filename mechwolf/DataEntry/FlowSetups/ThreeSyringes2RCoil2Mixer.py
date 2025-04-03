import json
"""
ComponentApp class handles the creation and management of widgets for configuring a multi-component apparatus setup.
Attributes:
    pumps (List[HarvardSyringePump]): List of syringe pumps used in the setup.
    data_manager (DataManager): Manages loading and saving of configuration data.
    data (Dict[str, Any]): Dictionary to store configuration data.
    setup_complete (bool): Flag indicating if the setup is complete.
    existing_config (Optional[Dict[str, Any]]): Existing configuration data if available.
    widget_manager (WidgetManager): Manages the creation and handling of widgets.
Methods:
    create_widgets(): Creates widgets for the apparatus setup using the widget manager.
    create_setup(b: Any): Gathers inputs, validates, processes, and saves the apparatus configuration.
    _gather_inputs(): Gathers all widget values using the widget manager.
    _prepare_data(values: Dict[str, Any]): Prepares data dictionary from widget values.
    _process_tube_dimensions(): Processes and validates tube dimensions.
    _process_coil_lengths(): Processes and validates coil lengths.
    _create_apparatus_config() -> Dict[str, Any]: Creates and returns the apparatus configuration dictionary.
"""
"""
ApparatusCreator class handles the creation and configuration of an apparatus with multiple syringe pumps.
Attributes:
    pumps (Tuple[HarvardSyringePump, ...]): Tuple of syringe pumps used in the setup.
    json_file (str): Path to the JSON file for saving/loading configuration.
    pump_type (str): Type of pump (single-channel or dual-channel).
Methods:
    _determine_pump_type() -> str: Determines the pump type based on the first pump.
    create_apparatus() -> mw.Apparatus: Creates and configures the apparatus.
    _process_events(): Processes IPython events.
    _build_apparatus() -> mw.Apparatus: Builds the apparatus from the saved configuration.
    _load_config() -> Dict[str, Any]: Loads configuration from the JSON file.
    _make_tube(tube_config: Dict[str, Any], length: float) -> mw.Tube: Creates a tube with the given configuration.
"""
from IPython.display import clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from typing import List, Dict, Any, Optional, Tuple
from .FlowSetupUtils import parse_tube_dimension, parse_numeric_foot
from .error_handler import ErrorHandler, ValidationError
from .data_manager import DataManager
from .widget_manager import WidgetManager


class ComponentApp:
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str) -> None:
        self.pumps: List[HarvardSyringePump] = pumps
        self.data_manager: DataManager = DataManager(json_file)
        self.data: Dict[str, Any] = {}
        self.setup_complete: bool = False
        self.existing_config: Optional[Dict[str, Any]] = self.data_manager.load_config()
        self.widget_manager: WidgetManager = WidgetManager(self)

    def create_widgets(self) -> None:
        """Create widgets using the widget manager"""
        self.widgets = self.widget_manager.create_all_widgets(
            num_vessels=4,  # 3 vessels + 1 product vessel
            num_tubes=1,
            num_coils=4,  # Four coils: a, x, b, y
            num_mixers=2,  # Two mixers for this setup
        )

        if self.existing_config:
            self.widget_manager.prefill_values(self.existing_config)

        self.widget_container = self.widget_manager.widget_container

    def create_setup(self, b: Any) -> None:
        try:
            # Gather all inputs
            self._gather_inputs()

            # Rest of validation and processing
            ErrorHandler.validate_mixer_inputs(self.data)
            self._process_tube_dimensions()
            self._process_coil_lengths()

            # Create and save apparatus configuration
            apparatus_config = self._create_apparatus_config()
            self.data_manager.save_config(apparatus_config)

            self.widget_container.close()
            self.setup_complete = True
            clear_output()
            print("Configuration saved successfully!")

        except ValidationError as e:
            print(f"Validation Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def _gather_inputs(self) -> None:
        """Gather all widget values using widget manager"""
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
            "coil_b_raw": widget_values["coil_b"],
            "coil_y_raw": widget_values["coil_y"],
        }

    def _prepare_data(self, values: Dict[str, Any]) -> None:
        """Prepare data dictionary from widget values"""
        self.data = {
            "apparatus_name": values["apparatus_name"],
            "vessel1_name": values["vessel1_name"],
            "vessel1_desc": values["vessel1_desc"],
            "vessel2_name": values["vessel2_name"],
            "vessel2_desc": values["vessel2_desc"],
            "vessel3_name": values["vessel3_name"],
            "vessel3_desc": values["vessel3_desc"],
            "product_vessel_name": values["product_vessel_name"],
            "product_vessel_desc": values["product_vessel_desc"],
            "reaction_tube_id_raw": values["reaction_tube1_id"],
            "reaction_tube_od_raw": values["reaction_tube1_od"],
            "reaction_tube_material": values["reaction_tube1_material"],
            "using_mixer": values["using_mixer"],
            "mixer_tube_id_raw": values["mixer1_tube_id"],
            "mixer_tube_od_raw": values["mixer1_tube_od"],
            "mixer_tube_material": values["mixer1_tube_material"],
            "coil_a_raw": values["coil_a"],  # Changed from 'coil_1'
            "coil_x_raw": values["coil_x"],  # Changed from 'coil_2'
            "coil_b_raw": values["coil_b"],  # For the second setup
            "coil_y_raw": values["coil_y"],  # For the second setup
        }

    def _process_tube_dimensions(self) -> None:
        self.data["reaction_tube_ID"] = parse_tube_dimension(
            self.data["reaction_tube_id_raw"]
        )
        self.data["reaction_tube_OD"] = parse_tube_dimension(
            self.data["reaction_tube_od_raw"]
        )

        tube_data = {
            "reaction_tubes": [
                (self.data["reaction_tube_ID"], self.data["reaction_tube_OD"])
            ]
        }

        if self.data["using_mixer"]:
            self.data["mixer_tube_ID"] = parse_tube_dimension(
                self.data["mixer_tube_id_raw"]
            )
            self.data["mixer_tube_OD"] = parse_tube_dimension(
                self.data["mixer_tube_od_raw"]
            )
            tube_data["mixer_tubes"] = [
                (self.data["mixer_tube_ID"], self.data["mixer_tube_OD"])
            ]

        ErrorHandler.validate_tube_dimensions(tube_data)

    def _process_coil_lengths(self) -> None:
        self.data.update(
            {
                "coil_a_length": parse_numeric_foot(self.data["coil_a_raw"]),
                "coil_x_length": parse_numeric_foot(self.data["coil_x_raw"]),
                "coil_b_length": parse_numeric_foot(self.data["coil_b_raw"]),
                "coil_y_length": parse_numeric_foot(self.data["coil_y_raw"]),
            }
        )

        coil_lengths = [
            self.data["coil_a_length"],
            self.data["coil_x_length"],
            self.data["coil_b_length"],
            self.data["coil_y_length"],
        ]
        ErrorHandler.validate_coil_lengths(coil_lengths)

    def _create_apparatus_config(self) -> Dict[str, Any]:
        config = {
            "apparatus_name": self.data["apparatus_name"],
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
                {"length": self.data["coil_a_length"], "index": "a"},
                {"length": self.data["coil_x_length"], "index": "x"},
                {"length": self.data["coil_b_length"], "index": "b"},
                {"length": self.data["coil_y_length"], "index": "y"},
            ],
            "using_mixer": self.data["using_mixer"],
            # Add network structure for the 2 mixer setup
            "network": {
                "pumps": [
                    {"id": "pump1", "connected_to": "vessel1"},
                    {"id": "pump2", "connected_to": "vessel2"},
                    {"id": "pump3", "connected_to": "vessel3"},
                ],
                "mixers": [
                    {"id": "T1", "inputs": ["vessel1", "vessel2"], "output": "T2"},
                    {"id": "T2", "inputs": ["T1", "vessel3"], "output": "product_vessel"}
                ],
                "connections": [
                    {"from": "vessel1", "to": "T1", "via": "coil_a"},
                    {"from": "vessel2", "to": "T1", "via": "coil_a"},
                    {"from": "vessel3", "to": "T2", "via": "coil_b"},
                    {"from": "T1", "to": "T2", "via": "coil_x"},
                    {"from": "T2", "to": "product_vessel", "via": "coil_y"}
                ],
                "topology": "3in-2mixer-1out",
                "flow_distribution": {
                    "description": "Flow division for pump rates calculation",
                    "T2": {
                        "inputs": 2,  # T2 has 2 input streams
                        "output_fraction": 1.0  # T2 outputs 100% of final flow rate
                    },
                    "T1": {
                        "inputs": 2,  # T1 has 2 input streams
                        "output_fraction": 0.5  # T1 outputs 50% of final flow rate (one input to T2)
                    },
                    "vessel1": {"fraction": 0.25},  # 25% of final flow
                    "vessel2": {"fraction": 0.25},  # 25% of final flow
                    "vessel3": {"fraction": 0.5}    # 50% of final flow
                }
            }
        }

        if self.data["using_mixer"]:
            config["tubes"]["mixer"] = {
                "ID": self.data["mixer_tube_ID"],
                "OD": self.data["mixer_tube_OD"],
                "material": self.data["mixer_tube_material"],
            }

        return config


class ApparatusCreator:
    def __init__(
        self, *pumps: HarvardSyringePump, data_file: Optional[str] = None
    ) -> None:
        self.pumps: Tuple[HarvardSyringePump, ...] = pumps
        self.json_file: str = data_file if data_file else "apparatus_config.json"
        self.pump_type: str = self._determine_pump_type()

    def _determine_pump_type(self) -> str:
        """Determine pump type based on first pump"""
        return (
            "dual-channel"
            if isinstance(self.pumps[0], HarvardSyringePump)
            else "single-channel"
        )

    def create_apparatus(self) -> mw.Apparatus:
        """Create and configure the apparatus"""
        app = ComponentApp(self.pumps, self.json_file)
        app.create_widgets()

        while not app.setup_complete:
            self._process_events()

        return self._build_apparatus()

    def _process_events(self) -> None:
        """Process IPython events"""
        import time
        from IPython import get_ipython
        import asyncio

        time.sleep(0.1)
        if get_ipython():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_ipython().kernel.do_one_iteration())

    def _build_apparatus(self) -> mw.Apparatus:
        """Build apparatus from saved configuration with three input vessels and two mixers"""
        config = self._load_config()
        A = mw.Apparatus(config["apparatus_name"])

        # Create vessels dictionary
        vessels_dict = {}
        for i, v in enumerate(config["vessels"]):
            vessel = mw.Vessel(v["description"], name=v["name"])
            vessel_key = f"vessel{i+1}" if i < len(config["vessels"]) - 1 else "product_vessel"
            vessels_dict[vessel_key] = vessel

        # Create tube factory function
        def make_tube(tube_config: Dict[str, Any], length: float) -> mw.Tube:
            return mw.Tube(
                length=length,
                ID=tube_config["ID"],
                OD=tube_config["OD"],
                material=tube_config["material"],
            )

        # Create coils dictionary
        coils_dict = {}
        for coil in config["coils"]:
            coil_id = f"coil_{coil['index']}"
            coils_dict[coil_id] = make_tube(config["tubes"]["reaction"], coil["length"])

        # Create mixers dictionary
        mixers_dict = {}
        for mixer in config["network"]["mixers"]:
            mixers_dict[mixer["id"]] = mw.TMixer(name=mixer["id"])

        # Add pump connections based on type
        pump_connections = config["network"]["pumps"]
        
        if self.pump_type == "single-channel":
            for i, conn in enumerate(pump_connections):
                if i < len(self.pumps):
                    vessel_key = conn["connected_to"]
                    via_coil = "coil_a" if i < 2 else "coil_b"
                    A.add(self.pumps[i], vessels_dict[vessel_key], coils_dict[via_coil])
        else:  # dual-channel
            # For dual channel, first pump connects to first two vessels, second pump to third vessel
            A.add(self.pumps[0], vessels_dict["vessel1"], coils_dict["coil_a"])
            A.add(self.pumps[0], vessels_dict["vessel2"], coils_dict["coil_a"])
            if len(self.pumps) > 1:
                A.add(self.pumps[1], vessels_dict["vessel3"], coils_dict["coil_b"])

        # Add all other connections from the network configuration
        for conn in config["network"]["connections"]:
            from_comp = None
            to_comp = None
            
            # Determine the correct component types
            if conn["from"].startswith("vessel"):
                from_comp = vessels_dict[conn["from"]]
            elif conn["from"] in mixers_dict:
                from_comp = mixers_dict[conn["from"]]
                
            if conn["to"].startswith("vessel") or conn["to"] == "product_vessel":
                to_comp = vessels_dict[conn["to"]]
            elif conn["to"] in mixers_dict:
                to_comp = mixers_dict[conn["to"]]
                
            # Add connection if components were found
            if from_comp and to_comp:
                via_coil = coils_dict[conn["via"]]
                A.add(from_comp, to_comp, via_coil)

        return A

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                if "apparatus_config" in data:
                    return data["apparatus_config"]
                raise ValueError("No apparatus configuration found")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading configuration: {str(e)}")

    def _make_tube(self, tube_config: Dict[str, Any], length: float) -> mw.Tube:
        """Create a tube with given configuration"""
        return mw.Tube(
            length=length,
            ID=tube_config["ID"],
            OD=tube_config["OD"],
            material=tube_config["material"],
        )


if __name__ == "__main__":
    pump_1 = HarvardSyringePump()
    pump_2 = HarvardSyringePump()
    pump_3 = HarvardSyringePump()
    creator = ApparatusCreator(
        pump_1, pump_2, pump_3, data_file="apparatus_config.json"
    )
    creator.create_apparatus()
