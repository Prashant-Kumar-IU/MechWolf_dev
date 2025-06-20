"""
Reagent Validator

Provides validation logic for reagent data to ensure consistency and correctness.
"""

from typing import Dict, List, Any, Optional
import re


class ReagentValidator:
    """Validator for reagent data"""
    
    def __init__(self):
        """Initialize validator with validation rules"""
        
        # InChI pattern for basic validation
        self.inchi_pattern = re.compile(r'^InChI=1S?/')
        
        # InChI Key pattern (14-10-N format)
        self.inchi_key_pattern = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z]$')
        
        # Valid reagent name characters (letters, numbers, spaces, hyphens, common chemical symbols)
        self.name_pattern = re.compile(r'^[a-zA-Z0-9\s\-\(\)\[\],.′\+\−\·]+$')
    
    def validate_reagent(self, reagent_data: Dict[str, Any], reagent_type: str) -> List[str]:
        """
        Validate reagent data
        
        Args:
            reagent_data: Dictionary containing reagent information
            reagent_type: 'solid' or 'liquid'
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Basic required fields
        errors.extend(self._validate_basic_fields(reagent_data))
        
        # Type-specific validation
        if reagent_type == 'solid':
            errors.extend(self._validate_solid_reagent(reagent_data))
        elif reagent_type == 'liquid':
            errors.extend(self._validate_liquid_reagent(reagent_data))
        else:
            errors.append(f"Invalid reagent type: {reagent_type}")
        
        # Chemical data validation
        errors.extend(self._validate_chemical_data(reagent_data))
        
        return errors
    
    def _validate_basic_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate basic required fields"""
        errors = []
        
        # Name validation
        name = data.get("name", "").strip()
        if not name:
            errors.append("Reagent name is required")
        elif len(name) < 2:
            errors.append("Reagent name must be at least 2 characters")
        elif len(name) > 200:
            errors.append("Reagent name must be less than 200 characters")
        elif not self.name_pattern.match(name):
            errors.append("Reagent name contains invalid characters")
        
        # Molecular weight validation
        mw = data.get("molecular_weight", 0)
        if not isinstance(mw, (int, float)) or mw <= 0:
            errors.append("Molecular weight must be a positive number")
        elif mw < 1:
            errors.append("Molecular weight must be at least 1 g/mol")
        elif mw > 10000:
            errors.append("Molecular weight seems unusually high (>10,000 g/mol)")
        
        # Equivalents validation
        eq = data.get("eq")
        if eq is not None:
            if not isinstance(eq, (int, float)):
                errors.append("Equivalents must be a number")
            elif eq < 0:
                errors.append("Equivalents cannot be negative")
            elif eq > 100:
                errors.append("Equivalents seem unusually high (>100)")
        
        # Position validation
        position = data.get("position")
        if position is not None:
            if not isinstance(position, int):
                errors.append("Position must be an integer")
            elif position < 1:
                errors.append("Position must be at least 1")
            elif position > 20:
                errors.append("Position seems unusually high (>20)")
        
        return errors
    
    def _validate_solid_reagent(self, data: Dict[str, Any]) -> List[str]:
        """Validate solid reagent specific fields"""
        errors = []
        
        # Mass validation
        mass = data.get("mass", 0)
        if not isinstance(mass, (int, float)):
            errors.append("Mass must be a number")
        elif mass < 0:
            errors.append("Mass cannot be negative")
        elif mass == 0:
            errors.append("Mass must be greater than 0")
        elif mass > 100000:  # 100g
            errors.append("Mass seems unusually high (>100g)")
        
        return errors
    
    def _validate_liquid_reagent(self, data: Dict[str, Any]) -> List[str]:
        """Validate liquid reagent specific fields"""
        errors = []
        
        # Volume validation
        volume = data.get("volume")
        if volume is not None:
            if not isinstance(volume, (int, float)):
                errors.append("Volume must be a number")
            elif volume < 0:
                errors.append("Volume cannot be negative")
            elif volume > 10000:  # 10L
                errors.append("Volume seems unusually high (>10L)")
        
        # Density validation
        density = data.get("density", 1.0)
        if not isinstance(density, (int, float)):
            errors.append("Density must be a number")
        elif density <= 0:
            errors.append("Density must be positive")
        elif density < 0.1:
            errors.append("Density seems unusually low (<0.1 g/mL)")
        elif density > 20:
            errors.append("Density seems unusually high (>20 g/mL)")
        
        return errors
    
    def _validate_chemical_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate chemical identifier data"""
        errors = []
        
        # InChI validation
        inchi = data.get("inChi", "").strip()
        if inchi and not self.inchi_pattern.match(inchi):
            errors.append("InChI format appears invalid (should start with 'InChI=1S/')")
        
        # InChI Key validation
        inchi_key = data.get("inChi_Key", "").strip()
        if inchi_key and not self.inchi_key_pattern.match(inchi_key):
            errors.append("InChI Key format appears invalid (should be 14-10-1 format)")
        
        # Cross-validation: if InChI is provided, InChI Key should ideally be provided too
        if inchi and not inchi_key:
            # This is just a warning, not an error
            pass
        
        return errors
    
    def validate_reaction_scale(self, mass_scale: Optional[float], 
                              concentration: Optional[float], 
                              solvent: Optional[str]) -> List[str]:
        """
        Validate reaction scale parameters
        
        Args:
            mass_scale: Mass scale in mg
            concentration: Concentration in M
            solvent: Solvent name
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Mass scale validation
        if mass_scale is not None:
            if not isinstance(mass_scale, (int, float)):
                errors.append("Mass scale must be a number")
            elif mass_scale <= 0:
                errors.append("Mass scale must be positive")
            elif mass_scale > 100000:  # 100g
                errors.append("Mass scale seems unusually high (>100g)")
        
        # Concentration validation
        if concentration is not None:
            if not isinstance(concentration, (int, float)):
                errors.append("Concentration must be a number")
            elif concentration <= 0:
                errors.append("Concentration must be positive")
            elif concentration > 20:
                errors.append("Concentration seems unusually high (>20 M)")
        
        # Solvent validation
        if solvent is not None:
            solvent = solvent.strip()
            if len(solvent) > 100:
                errors.append("Solvent name is too long")
            elif not re.match(r'^[a-zA-Z0-9\s\-\(\)\[\],.]+$', solvent):
                errors.append("Solvent name contains invalid characters")
        
        return errors
    
    def check_duplicate_names(self, reagent_list: List[Dict[str, Any]], 
                             new_name: str, exclude_index: Optional[int] = None) -> bool:
        """
        Check if reagent name already exists
        
        Args:
            reagent_list: List of existing reagents
            new_name: Name to check
            exclude_index: Index to exclude from check (for updates)
            
        Returns:
            True if duplicate found, False otherwise
        """
        new_name = new_name.strip().lower()
        
        for i, reagent in enumerate(reagent_list):
            if exclude_index is not None and i == exclude_index:
                continue
                
            existing_name = reagent.get("name", "").strip().lower()
            if existing_name == new_name:
                return True
        
        return False
    
    def suggest_corrections(self, reagent_data: Dict[str, Any]) -> List[str]:
        """
        Suggest corrections for common issues
        
        Args:
            reagent_data: Reagent data to analyze
            
        Returns:
            List of suggestion messages
        """
        suggestions = []
        
        name = reagent_data.get("name", "").strip()
        
        # Common naming suggestions
        if name.lower().startswith("thf"):
            suggestions.append("Consider using full name: 'tetrahydrofuran' instead of 'THF'")
        elif name.lower().startswith("dcm"):
            suggestions.append("Consider using full name: 'dichloromethane' instead of 'DCM'")
        elif name.lower().startswith("dmf"):
            suggestions.append("Consider using full name: 'dimethylformamide' instead of 'DMF'")
        
        # MW suggestions based on common compounds
        mw = reagent_data.get("molecular_weight", 0)
        if name.lower() in ["water", "h2o"] and abs(mw - 18.02) > 0.1:
            suggestions.append("Water molecular weight should be ~18.02 g/mol")
        elif name.lower() in ["methanol", "meoh"] and abs(mw - 32.04) > 0.1:
            suggestions.append("Methanol molecular weight should be ~32.04 g/mol")
        
        # InChI suggestions
        inchi = reagent_data.get("inChi", "").strip()
        if not inchi:
            suggestions.append("Consider adding InChI for better compound identification")
        
        return suggestions