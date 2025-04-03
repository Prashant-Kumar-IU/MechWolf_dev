import json
from typing import Optional, Dict, Any


class DataManager:
    def __init__(self, json_file: str) -> None:
        """
        Initializes the DataManager with the given JSON file.

        Args:
            json_file (str): The path to the JSON file to be managed.
        """
        self.json_file: str = json_file

    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load existing apparatus configuration from JSON file"""
        try:
            with open(self.json_file, "r") as f:
                data: Dict[str, Any] = json.load(f)
                if isinstance(data, dict) and "apparatus_config" in data:
                    return data["apparatus_config"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def save_config(self, apparatus_config: Dict[str, Any]) -> None:
        """Save configuration while preserving other data"""
        try:
            # Try to read existing data
            with open(self.json_file, "r") as f:
                existing_data: Dict[str, Any] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        # Preserve all existing data except apparatus config
        existing_data["apparatus_config"] = apparatus_config

        # Ensure coils have both length and index if not already present
        if "coils" in apparatus_config:
            for coil in apparatus_config["coils"]:
                if "index" not in coil and "length" in coil:
                    # If index is missing but we have order, infer index
                    idx: int = apparatus_config["coils"].index(coil)
                    coil["index"] = ["a", "x", "b", "y"][idx]

        # Ensure network structure exists
        if "network" not in apparatus_config:
            # Create a default network structure based on number of vessels
            vessels = apparatus_config.get("vessels", [])
            num_vessels = len(vessels) - 1  # Subtract one for product vessel
            
            if num_vessels == 2:
                apparatus_config["network"] = self._create_default_network_2vessels()
            elif num_vessels == 3:
                # Check if we have 2 or 4 coils to determine setup type
                coils = apparatus_config.get("coils", [])
                if len(coils) >= 4:
                    apparatus_config["network"] = self._create_default_network_3vessels_2mixers()
                else:
                    apparatus_config["network"] = self._create_default_network_3vessels_1mixer()

        # Preserve specific reaction setup data if it exists
        reaction_fields = [
            "solid reagents",
            "liquid reagents",
            "mass scale (in mg)",
            "concentration (in mM)",
            "solvent",
        ]

        # Write back all data
        with open(self.json_file, "w") as f:
            json.dump(existing_data, f, indent=4)

    def _create_default_network_2vessels(self) -> Dict[str, Any]:
        """Create default network structure for 2 vessel setup"""
        return {
            "pumps": [
                {"id": "pump1", "connected_to": "vessel1"},
                {"id": "pump2", "connected_to": "vessel2"},
            ],
            "mixers": [
                {"id": "T1", "inputs": ["vessel1", "vessel2"], "output": "product_vessel"}
            ],
            "connections": [
                {"from": "vessel1", "to": "T1", "via": "coil_a"},
                {"from": "vessel2", "to": "T1", "via": "coil_a"},
                {"from": "T1", "to": "product_vessel", "via": "coil_x"}
            ],
            "topology": "2in-1mixer-1out",
            "flow_distribution": {
                "vessel1": {"fraction": 0.5},
                "vessel2": {"fraction": 0.5}
            }
        }

    def _create_default_network_3vessels_1mixer(self) -> Dict[str, Any]:
        """Create default network structure for 3 vessel setup with 1 mixer"""
        return {
            "pumps": [
                {"id": "pump1", "connected_to": "vessel1"},
                {"id": "pump2", "connected_to": "vessel2"},
                {"id": "pump3", "connected_to": "vessel3"},
            ],
            "mixers": [
                {"id": "T1", "inputs": ["vessel1", "vessel2", "vessel3"], "output": "product_vessel"}
            ],
            "connections": [
                {"from": "vessel1", "to": "T1", "via": "coil_a"},
                {"from": "vessel2", "to": "T1", "via": "coil_a"},
                {"from": "vessel3", "to": "T1", "via": "coil_a"},
                {"from": "T1", "to": "product_vessel", "via": "coil_x"}
            ],
            "topology": "3in-1mixer-1out",
            "flow_distribution": {
                "vessel1": {"fraction": 1/3},
                "vessel2": {"fraction": 1/3},
                "vessel3": {"fraction": 1/3}
            }
        }

    def _create_default_network_3vessels_2mixers(self) -> Dict[str, Any]:
        """Create default network structure for 3 vessel setup with 2 mixers"""
        return {
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
                    "inputs": 2,
                    "output_fraction": 1.0
                },
                "T1": {
                    "inputs": 2, 
                    "output_fraction": 0.5
                },
                "vessel1": {"fraction": 0.25},
                "vessel2": {"fraction": 0.25},
                "vessel3": {"fraction": 0.5}
            }
        }
