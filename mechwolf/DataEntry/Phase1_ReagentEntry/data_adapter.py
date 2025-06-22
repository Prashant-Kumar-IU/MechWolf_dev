"""
Data Adapter for ReagentUI to ExperimentalMetadata Integration

This adapter translates between the old ReagentUI data format and the new
experimental_metadata system while preserving all original functionality.
"""

from typing import Dict, Any, List
import copy

class ReagentDataAdapter:
    """
    Adapter class to make experimental_metadata work with original ReagentUI interface
    
    This class provides the same interface as the old ReagentDataManager but uses
    the new experimental_metadata system as the backend.
    """
    
    def __init__(self, experiment_manager):
        """
        Initialize with an ExperimentalMetadataManager instance
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        self._cached_data = None
    
    def _convert_to_old_format(self, reagent: Dict[str, Any]) -> Dict[str, Any]:
        """Convert new format reagent to old format"""
        old_reagent = copy.deepcopy(reagent)
        
        # Convert field names from new format to old format
        field_mapping = {
            "molecular_weight": "molecular weight (in g/mol)",
            "inChi": "inChi",  # Keep as is
            "inChi_Key": "inChi Key",
            "SMILES": "SMILES",  # Keep as is
            "density": "density (in g/mL)",
            "position": "syringe"  # Position maps to syringe in old format
        }
        
        for new_field, old_field in field_mapping.items():
            if new_field in old_reagent:
                old_reagent[old_field] = old_reagent.pop(new_field)
        
        return old_reagent
    
    def _convert_to_new_format(self, reagent: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old format reagent to new format"""
        new_reagent = copy.deepcopy(reagent)
        
        # Convert field names from old format to new format
        field_mapping = {
            "molecular weight (in g/mol)": "molecular_weight",
            "inChi Key": "inChi_Key",
            "density (in g/mL)": "density",
            "syringe": "position"  # Syringe maps to position in new format
        }
        
        for old_field, new_field in field_mapping.items():
            if old_field in new_reagent:
                new_reagent[new_field] = new_reagent.pop(old_field)
        
        return new_reagent
    
    @property
    def data(self) -> Dict[str, Any]:
        """
        Get data in old ReagentUI format
        
        Returns:
            Dictionary with old format structure
        """
        if self._cached_data is None:
            self._refresh_cache()
        return self._cached_data
    
    def _refresh_cache(self):
        """Refresh the cached data from experimental_metadata"""
        chemistry_data = self.experiment.chemistry.get_data()
        
        # Convert to old format
        self._cached_data = {
            "solid reagents": [],
            "liquid reagents": []
        }
        
        # Convert solid reagents
        for reagent in chemistry_data.get("solid_reagents", []):
            old_reagent = self._convert_to_old_format(reagent)
            self._cached_data["solid reagents"].append(old_reagent)
        
        # Convert liquid reagents
        for reagent in chemistry_data.get("liquid_reagents", []):
            old_reagent = self._convert_to_old_format(reagent)
            self._cached_data["liquid reagents"].append(old_reagent)
        
        # Add final details
        scale_fields = {
            "mass_scale": "mass scale (in mg)",
            "concentration": "concentration (in mM)",
            "solvent": "solvent"
        }
        
        for new_field, old_field in scale_fields.items():
            if new_field in chemistry_data:
                self._cached_data[old_field] = chemistry_data[new_field]
    
    def load_data(self) -> Dict[str, Any]:
        """
        Load reagent data (compatibility method)
        
        Returns:
            Dictionary with reagent data in old format
        """
        self._refresh_cache()
        return self.data
    
    def save_data(self) -> None:
        """
        Save reagent data (compatibility method)
        
        The data is automatically saved through experimental_metadata
        """
        # Data is automatically saved when using experimental_metadata methods
        # We'll refresh the cache to stay in sync
        self._refresh_cache()
    
    def add_reagent(self, reagent: Dict[str, Any], reagent_type: str) -> bool:
        """
        Add a reagent to the data
        
        Args:
            reagent: Dictionary containing reagent data in old format
            reagent_type: Type of reagent ('solid' or 'liquid')
            
        Returns:
            True if successful
        """
        try:
            # Convert to new format
            new_reagent = self._convert_to_new_format(reagent)
            
            # Add to experimental_metadata
            if reagent_type == "solid":
                success = self.experiment.chemistry.add_solid_reagent(new_reagent)
            else:
                success = self.experiment.chemistry.add_liquid_reagent(new_reagent)
            
            if success:
                self.experiment.save()
                self._refresh_cache()
            
            return success
            
        except Exception as e:
            print(f"Error adding reagent: {e}")
            return False
    
    def update_reagent(self, old_reagent: Dict[str, Any], new_reagent: Dict[str, Any], reagent_type: str) -> bool:
        """
        Update an existing reagent
        
        Args:
            old_reagent: Original reagent data in old format
            new_reagent: New reagent data in old format
            reagent_type: Type of reagent ('solid' or 'liquid')
            
        Returns:
            True if successful
        """
        try:
            # Convert to new format
            new_reagent_converted = self._convert_to_new_format(new_reagent)
            
            # Find the reagent by name and update it
            chemistry_data = self.experiment.chemistry.get_data()
            reagents_key = "solid_reagents" if reagent_type == "solid" else "liquid_reagents"
            
            if reagents_key in chemistry_data:
                for i, reagent in enumerate(chemistry_data[reagents_key]):
                    if reagent.get("name") == old_reagent.get("name"):
                        chemistry_data[reagents_key][i] = new_reagent_converted
                        success = self.experiment.chemistry.save_data(chemistry_data)
                        if success:
                            self.experiment.save()
                            self._refresh_cache()
                        return success
            
            # If not found, add as new
            return self.add_reagent(new_reagent, reagent_type)
            
        except Exception as e:
            print(f"Error updating reagent: {e}")
            return False
    
    def delete_reagent(self, reagent: Dict[str, Any]) -> bool:
        """
        Remove a reagent from the data
        
        Args:
            reagent: Reagent data to remove in old format
            
        Returns:
            True if successful
        """
        try:
            chemistry_data = self.experiment.chemistry.get_data()
            reagent_name = reagent.get("name")
            
            # Check solid reagents
            solid_reagents = chemistry_data.get("solid_reagents", [])
            for i, r in enumerate(solid_reagents):
                if r.get("name") == reagent_name:
                    del chemistry_data["solid_reagents"][i]
                    success = self.experiment.chemistry.save_data(chemistry_data)
                    if success:
                        self.experiment.save()
                        self._refresh_cache()
                    return success
            
            # Check liquid reagents
            liquid_reagents = chemistry_data.get("liquid_reagents", [])
            for i, r in enumerate(liquid_reagents):
                if r.get("name") == reagent_name:
                    del chemistry_data["liquid_reagents"][i]
                    success = self.experiment.chemistry.save_data(chemistry_data)
                    if success:
                        self.experiment.save()
                        self._refresh_cache()
                    return success
            
            return False
            
        except Exception as e:
            print(f"Error deleting reagent: {e}")
            return False
    
    def get_reagent_type(self, reagent: Dict[str, Any]) -> str:
        """
        Determine the type of a reagent
        
        Args:
            reagent: Reagent data in old format
            
        Returns:
            'solid' or 'liquid'
        """
        reagent_name = reagent.get("name", "")
        
        # Check the current data
        if self._cached_data is None:
            self._refresh_cache()
        
        # Check solid reagents
        for solid in self._cached_data["solid reagents"]:
            if solid.get("name") == reagent_name:
                return "solid"
        
        # Check liquid reagents
        for liquid in self._cached_data["liquid reagents"]:
            if liquid.get("name") == reagent_name:
                return "liquid"
        
        # Check by presence of density field (liquid-specific)
        return "liquid" if "density (in g/mL)" in reagent else "solid"
    
    def update_final_details(self, mass_scale: float, concentration: float, solvent: str) -> bool:
        """
        Update the final details in the data
        
        Args:
            mass_scale: Mass scale in mg
            concentration: Concentration in mM
            solvent: Solvent name(s)
            
        Returns:
            True if successful
        """
        try:
            chemistry_data = self.experiment.chemistry.get_data()
            
            if mass_scale is not None:
                chemistry_data["mass_scale"] = mass_scale
            if concentration is not None:
                chemistry_data["concentration"] = concentration
            if solvent is not None:
                chemistry_data["solvent"] = solvent
            
            success = self.experiment.chemistry.save_data(chemistry_data)
            if success:
                self.experiment.save()
                self._refresh_cache()
            
            return success
            
        except Exception as e:
            print(f"Error updating final details: {e}")
            return False
    
    def has_limiting_reagent(self) -> bool:
        """
        Check if at least one reagent has an equivalent of 1.0
        
        Returns:
            True if a limiting reagent exists
        """
        if self._cached_data is None:
            self._refresh_cache()
        
        all_reagents = self._cached_data["solid reagents"] + self._cached_data["liquid reagents"]
        return any(
            abs(reagent.get("eq", 0) - 1.0) < 1e-6
            for reagent in all_reagents
        )