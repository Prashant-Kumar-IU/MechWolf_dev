"""
Base classes for creating modular flow setup applications.

This module provides abstract base classes that define the common structure
and functionality for different flow setup types, reducing code duplication
and improving maintainability.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from IPython.display import clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump

from .config_templates import FlowSetupConfig
from .data_manager import DataManager
from .widget_manager import WidgetManager
from .error_handler import ErrorHandler, ValidationError
from .FlowSetupUtils import parse_tube_dimension, parse_numeric_foot


class BaseComponentApp(ABC):
    """Base class for all component apps"""
    
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str, config: FlowSetupConfig):
        self.pumps: List[HarvardSyringePump] = pumps
        self.config: FlowSetupConfig = config
        self.data_manager: DataManager = DataManager(json_file)
        self.data: Dict[str, Any] = {}
        self.setup_complete: bool = False
        self.existing_config: Optional[Dict[str, Any]] = self.data_manager.load_config()
        self.widget_manager: WidgetManager = WidgetManager(self)
    
    def create_widgets(self) -> None:
        """Create widgets using the configuration"""
        self.widgets = self.widget_manager.create_all_widgets(**self.config.to_dict())
        
        if self.existing_config:
            self.widget_manager.prefill_values(self.existing_config)
        
        self.widget_container = self.widget_manager.widget_container
    
    def create_setup(self, b: Any) -> None:
        """Standard setup creation flow"""
        try:
            self._gather_inputs()
            self._validate_inputs()
            self._process_data()
            apparatus_config = self._create_apparatus_config()
            self.data_manager.save_config(apparatus_config)
            
            self.widget_container.close()
            self.setup_complete = True
            clear_output()
            print(f"Configuration saved successfully for {self.config.name}!")
            
        except ValidationError as e:
            print(f"Validation Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    @abstractmethod
    def _gather_inputs(self) -> None:
        """Gather inputs specific to this setup type"""
        pass
    
    @abstractmethod
    def _create_apparatus_config(self) -> Dict[str, Any]:
        """Create apparatus config specific to this setup type"""
        pass
    
    def _validate_inputs(self) -> None:
        """Common validation logic"""
        ErrorHandler.validate_mixer_inputs(self.data)
    
    def _process_data(self) -> None:
        """Common data processing"""
        self._process_tube_dimensions()
        self._process_coil_lengths()
    
    def _process_tube_dimensions(self) -> None:
        """Process and validate tube dimensions"""
        if "reaction_tube_id_raw" in self.data:
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
            
            if self.data.get("using_mixer"):
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
        """Process and validate coil lengths"""
        coil_lengths = []
        for letter in self.config.coil_letters:
            if f"coil_{letter}_raw" in self.data:
                length = parse_numeric_foot(self.data[f"coil_{letter}_raw"])
                self.data[f"coil_{letter}_length"] = length
                coil_lengths.append(length)
        
        if coil_lengths:
            ErrorHandler.validate_coil_lengths(coil_lengths)


class BaseApparatusCreator(ABC):
    """Base apparatus creator with common functionality"""
    
    def __init__(self, *pumps: HarvardSyringePump, data_file: Optional[str] = None):
        self.pumps = pumps
        self.json_file: str = data_file or "apparatus_config.json"
        self.pump_type: str = self._determine_pump_type()
        
    def _determine_pump_type(self) -> str:
        """Determine pump type based on the pumps provided"""
        for pump in self.pumps:
            if isinstance(pump, HarvardSyringePump):
                return "dual-channel"
        return "single-channel"
    
    def create_apparatus(self) -> mw.Apparatus:
        """Template method for apparatus creation"""
        app = self._create_component_app()
        app.create_widgets()
        
        # Block until setup is complete
        self._wait_for_setup_completion(app)
        
        return self._build_apparatus()
    
    def _wait_for_setup_completion(self, app) -> None:
        """Wait for setup to complete with proper event handling"""
        import time
        from IPython import get_ipython
        import asyncio
        
        while not app.setup_complete:
            time.sleep(0.1)
            if get_ipython():
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_ipython().kernel.do_one_iteration())
    
    @abstractmethod
    def _create_component_app(self):
        """Create the appropriate component app"""
        pass
    
    @abstractmethod 
    def _build_apparatus(self) -> mw.Apparatus:
        """Build the specific apparatus configuration"""
        pass
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        import json
        with open(self.json_file, "r") as f:
            data = json.load(f)
        
        if "apparatus_config" not in data:
            raise ValueError("No apparatus configuration found")
        
        return data["apparatus_config"]
    
    def _make_tube(self, tube_config: Dict[str, Any], length: Optional[float] = None) -> mw.Tube:
        """Create a tube with the given configuration and length"""
        return mw.Tube(
            length=length or "0 in",
            ID=tube_config["ID"],
            OD=tube_config["OD"],
            material=tube_config["material"],
        )
