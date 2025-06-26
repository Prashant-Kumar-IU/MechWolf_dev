"""
Business logic services for Phase 1 Reagent Entry.

This module contains service classes that handle business operations
separated from UI concerns for better testability and maintainability.
"""

from typing import Dict, Any, List, Optional, Tuple
from .models import ReagentModel, ExperimentModel
from .data_adapter import ReagentDataAdapter
from ..external.pubchem import PubChemService
from ..utils.chemistry import normalize_chemical_data


class ReagentService:
    """
    Service for managing individual reagent operations.
    
    This service handles business logic for creating, updating, and validating
    reagents without direct UI dependencies.
    """
    
    def __init__(self, data_adapter: ReagentDataAdapter):
        """
        Initialize with a data adapter.
        
        Args:
            data_adapter: ReagentDataAdapter instance for data persistence
        """
        self.data_adapter = data_adapter
        self.pubchem_service = PubChemService()
    
    def create_reagent_from_form_data(self, form_data: Dict[str, Any], reagent_type: str) -> Tuple[Optional[ReagentModel], List[str]]:
        """
        Create a ReagentModel from form data with validation.
        
        Args:
            form_data: Dictionary containing form input data
            reagent_type: "solid" or "liquid"
            
        Returns:
            Tuple of (ReagentModel or None, list of validation errors)
        """
        try:
            # Map form field names to model field names
            model_data = {
                'name': form_data.get('name', '').strip(),
                'molecular_weight': form_data.get('molecular_weight', 0.0),
                'equivalents': form_data.get('equivalents', 1.0),
                'position': form_data.get('position', 1),
                'smiles': form_data.get('smiles', '').strip() or None,
                'inchi': form_data.get('inchi', '').strip() or None,
                'inchi_key': form_data.get('inchi_key', '').strip() or None,
                'reagent_type': reagent_type
            }
            
            # Add density for liquid reagents
            if reagent_type == "liquid":
                model_data['density'] = form_data.get('density', 1.0)
            
            # Create reagent model
            reagent = ReagentModel(**model_data)
            
            if reagent.is_valid:
                return reagent, []
            else:
                return None, reagent.errors
                
        except Exception as e:
            return None, [f"Error creating reagent: {str(e)}"]
    
    def save_reagent(self, reagent: ReagentModel) -> Tuple[bool, List[str]]:
        """
        Save a reagent to persistent storage.
        
        Args:
            reagent: ReagentModel to save
            
        Returns:
            Tuple of (success boolean, list of error messages)
        """
        if not reagent.is_valid:
            return False, reagent.errors
        
        try:
            success = self.data_adapter.add_reagent_model(reagent)
            if success:
                return True, []
            else:
                return False, ["Failed to save reagent to storage"]
                
        except Exception as e:
            return False, [f"Error saving reagent: {str(e)}"]
    
    def update_reagent(self, old_reagent: ReagentModel, new_reagent: ReagentModel) -> Tuple[bool, List[str]]:
        """
        Update an existing reagent.
        
        Args:
            old_reagent: Original ReagentModel
            new_reagent: Updated ReagentModel
            
        Returns:
            Tuple of (success boolean, list of error messages)
        """
        if not new_reagent.is_valid:
            return False, new_reagent.errors
        
        try:
            success = self.data_adapter.update_reagent_model(old_reagent, new_reagent)
            if success:
                return True, []
            else:
                return False, ["Failed to update reagent in storage"]
                
        except Exception as e:
            return False, [f"Error updating reagent: {str(e)}"]
    
    def delete_reagent(self, reagent: ReagentModel) -> Tuple[bool, List[str]]:
        """
        Delete a reagent from storage.
        
        Args:
            reagent: ReagentModel to delete
            
        Returns:
            Tuple of (success boolean, list of error messages)
        """
        try:
            old_format_data = reagent.to_old_format()
            success = self.data_adapter.delete_reagent(old_format_data)
            if success:
                return True, []
            else:
                return False, ["Failed to delete reagent from storage"]
                
        except Exception as e:
            return False, [f"Error deleting reagent: {str(e)}"]
    
    def search_pubchem(self, query: str, search_type: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Search PubChem for compounds.
        
        Args:
            query: Search query
            search_type: Type of search ('name', 'smiles', 'inchi', 'cas')
            
        Returns:
            Tuple of (list of compound dictionaries, list of error messages)
        """
        try:
            results = self.pubchem_service.search(query, search_type)
            return results, []
            
        except Exception as e:
            return [], [f"PubChem search error: {str(e)}"]
    
    def create_reagent_from_pubchem(self, compound_data: Dict[str, Any], reagent_type: str,
                                   equivalents: float = 1.0, position: int = 1) -> Tuple[Optional[ReagentModel], List[str]]:
        """
        Create a ReagentModel from PubChem compound data.
        
        Args:
            compound_data: PubChem compound dictionary
            reagent_type: "solid" or "liquid"
            equivalents: Chemical equivalents
            position: Syringe position
            
        Returns:
            Tuple of (ReagentModel or None, list of validation errors)
        """
        try:
            reagent = ReagentModel.from_pubchem_data(
                compound_data, reagent_type, equivalents, position
            )
            
            if reagent.is_valid:
                return reagent, []
            else:
                return None, reagent.errors
                
        except Exception as e:
            return None, [f"Error creating reagent from PubChem data: {str(e)}"]


class ExperimentService:
    """
    Service for managing complete experiment operations.
    
    This service handles business logic for experiment-level operations
    including validation, calculations, and data management.
    """
    
    def __init__(self, data_adapter: ReagentDataAdapter):
        """
        Initialize with a data adapter.
        
        Args:
            data_adapter: ReagentDataAdapter instance for data persistence
        """
        self.data_adapter = data_adapter
    
    def get_current_experiment(self) -> ExperimentModel:
        """
        Get the current experiment data as a model.
        
        Returns:
            ExperimentModel with current data
        """
        return self.data_adapter.to_experiment_model()
    
    def save_experiment(self, experiment: ExperimentModel) -> Tuple[bool, List[str]]:
        """
        Save a complete experiment.
        
        Args:
            experiment: ExperimentModel to save
            
        Returns:
            Tuple of (success boolean, list of error messages)
        """
        if not experiment.is_valid:
            return False, experiment.errors
        
        try:
            success = self.data_adapter.from_experiment_model(experiment)
            if success:
                return True, []
            else:
                return False, ["Failed to save experiment to storage"]
                
        except Exception as e:
            return False, [f"Error saving experiment: {str(e)}"]
    
    def update_final_details(self, mass_scale: float, concentration: float, 
                           solvent: str) -> Tuple[bool, List[str]]:
        """
        Update experiment final details.
        
        Args:
            mass_scale: Mass scale in mg
            concentration: Concentration in mM
            solvent: Solvent name(s)
            
        Returns:
            Tuple of (success boolean, list of error messages)
        """
        # Validate input
        errors = []
        if mass_scale <= 0:
            errors.append("Mass scale must be greater than 0")
        if concentration <= 0:
            errors.append("Concentration must be greater than 0")
        if not solvent or not solvent.strip():
            errors.append("Solvent is required")
        
        if errors:
            return False, errors
        
        try:
            success = self.data_adapter.update_final_details(mass_scale, concentration, solvent)
            if success:
                return True, []
            else:
                return False, ["Failed to update final details"]
                
        except Exception as e:
            return False, [f"Error updating final details: {str(e)}"]
    
    def calculate_stoichiometry(self) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Calculate stoichiometry for the current experiment.
        
        Returns:
            Tuple of (stoichiometry data dict or None, list of error messages)
        """
        try:
            experiment = self.get_current_experiment()
            
            if not experiment.limiting_reagent:
                return None, ["No limiting reagent found (set equivalents = 1.0)"]
            
            if not experiment.mass_scale or not experiment.concentration:
                return None, ["Mass scale and concentration are required"]
            
            # Calculate volumes for liquid reagents
            volumes = experiment.calculate_volumes()
            
            # Prepare stoichiometry data
            limiting_reagent = experiment.limiting_reagent
            limiting_moles = (experiment.mass_scale / 1000) / limiting_reagent.molecular_weight
            
            stoich_data = {
                'limiting_reagent': limiting_reagent.name,
                'limiting_moles_mmol': limiting_moles * 1000,
                'mass_scale_mg': experiment.mass_scale,
                'concentration_mM': experiment.concentration,
                'solvent': experiment.solvent,
                'reagents': [],
                'volumes': volumes
            }
            
            # Add reagent calculations
            for reagent in experiment.all_reagents:
                reagent_moles = limiting_moles * reagent.equivalents
                reagent_mass_mg = reagent_moles * reagent.molecular_weight * 1000
                
                reagent_calc = {
                    'name': reagent.name,
                    'type': reagent.reagent_type,
                    'molecular_weight': reagent.molecular_weight,
                    'equivalents': reagent.equivalents,
                    'moles_mmol': reagent_moles * 1000,
                    'mass_mg': reagent_mass_mg,
                    'position': reagent.position
                }
                
                if reagent.reagent_type == "liquid" and reagent.density:
                    volume_ml = volumes.get(reagent.name, 0)
                    reagent_calc['density'] = reagent.density
                    reagent_calc['volume_ml'] = volume_ml
                    reagent_calc['volume_ul'] = volume_ml * 1000
                
                stoich_data['reagents'].append(reagent_calc)
            
            return stoich_data, []
            
        except Exception as e:
            return None, [f"Error calculating stoichiometry: {str(e)}"]
    
    def validate_experiment_completeness(self) -> Tuple[bool, List[str]]:
        """
        Validate that the experiment is complete and ready for execution.
        
        Returns:
            Tuple of (is_complete boolean, list of issues)
        """
        experiment = self.get_current_experiment()
        issues = []
        
        # Check for reagents
        if experiment.total_reagent_count == 0:
            issues.append("No reagents have been added")
        
        # Check for limiting reagent
        if not experiment.limiting_reagent:
            issues.append("No limiting reagent defined (set one reagent to eq=1.0)")
        
        # Check final details
        if not experiment.mass_scale:
            issues.append("Mass scale not set")
        if not experiment.concentration:
            issues.append("Concentration not set")
        if not experiment.solvent:
            issues.append("Solvent not specified")
        
        # Check reagent validity
        for reagent in experiment.all_reagents:
            if not reagent.is_valid:
                issues.extend([f"{reagent.name}: {error}" for error in reagent.errors])
        
        return len(issues) == 0, issues


__all__ = ['ReagentService', 'ExperimentService']