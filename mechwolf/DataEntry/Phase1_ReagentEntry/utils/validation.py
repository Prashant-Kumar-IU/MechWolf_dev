"""
Data validation utilities for reagent entry.

This module contains validation functions extracted from the original
reagent_utils.py file, focusing specifically on data validation logic.
"""

from typing import Dict, Any, List
from .imports import suppress_stderr


def validate_reagent_data(data: Dict[str, Any], reagent_type: str) -> List[str]:
    """
    Validate reagent data and return a list of errors.
    
    Args:
        data: Dictionary containing reagent data (in old ReagentUI format)
        reagent_type: Type of reagent ('solid' or 'liquid')
        
    Returns:
        List of validation error messages, empty if valid
    """
    errors = []
    
    # Name validation
    if not data.get("name") or data["name"].strip() == "":
        errors.append("Name is required")
    
    # Equivalents validation
    if not data.get("eq") or data["eq"] <= 0:
        errors.append("Equivalents must be greater than 0")
        
    # Molecular weight validation (old format field name)
    mw_field = "molecular weight (in g/mol)"
    if not data.get(mw_field) or data[mw_field] <= 0:
        errors.append("Molecular weight must be greater than 0")
    
    # Syringe validation (old format uses 'syringe' instead of 'position')
    if not data.get("syringe") or data["syringe"] <= 0:
        errors.append("Syringe number must be greater than 0")
    
    # Type-specific validation
    if reagent_type == "liquid":
        density_field = "density (in g/mL)"
        if not data.get(density_field) or data[density_field] <= 0:
            errors.append("Density must be greater than 0 for liquid reagents")
    
    return errors


def validate_smiles(smiles_string: str) -> bool:
    """
    Validate a SMILES string with basic checks.
    
    Args:
        smiles_string: The SMILES string to validate
        
    Returns:
        True if the SMILES string passes basic validation, False otherwise
    """
    if not smiles_string or not isinstance(smiles_string, str):
        return False
    
    # Basic validation - must have letters and reasonable length
    if len(smiles_string) < 1 or not any(c.isalpha() for c in smiles_string):
        return False
    
    # Check for unmatched brackets/parentheses
    brackets = {'[': ']', '(': ')'}
    stack = []
    
    for char in smiles_string:
        if char in brackets.keys():
            stack.append(char)
        elif char in brackets.values():
            if not stack or char != brackets.get(stack.pop(), None):
                return False
    
    # Check for unclosed rings (numbers should appear in pairs)
    digits = [c for c in smiles_string if c.isdigit()]
    digit_counts = {}
    for d in digits:
        digit_counts[d] = digit_counts.get(d, 0) + 1
    
    # Each ring number should appear exactly twice
    for count in digit_counts.values():
        if count % 2 != 0:
            return False
    
    # Additional validation with RDKit if available
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        # Disable RDKit logging
        RDLogger.DisableLog('rdApp')
        # Suppress stderr during SMILES parsing
        with suppress_stderr():
            mol = Chem.MolFromSmiles(smiles_string, sanitize=False)
            return mol is not None
    except ImportError:
        # RDKit not available, just return the bracket validation result
        pass
    
    return len(stack) == 0  # All brackets should be matched


def try_sanitize_smiles(smiles_string: str) -> str:
    """
    Attempts to sanitize a SMILES string by handling common errors.
    
    Args:
        smiles_string: The potentially invalid SMILES string
        
    Returns:
        Sanitized SMILES string if possible, empty string if not salvageable
    """
    if not smiles_string or not isinstance(smiles_string, str):
        return ""
    
    # Remove any whitespace
    sanitized = smiles_string.strip()
    
    # Handle unclosed rings by removing the opening digit
    digits = [i for i, c in enumerate(sanitized) if c.isdigit()]
    digit_chars = [sanitized[i] for i in digits]
    
    # Find digits that appear only once
    from collections import Counter
    counts = Counter(digit_chars)
    single_digits = [d for d, count in counts.items() if count % 2 != 0]
    
    # Remove unclosed rings (risky but better than failing)
    for digit in single_digits:
        indices = [i for i, c in enumerate(sanitized) if c == digit]
        # Remove the first occurrence of each problematic digit
        if indices:
            sanitized = sanitized[:indices[0]] + sanitized[indices[0]+1:]
    
    return sanitized if validate_smiles(sanitized) else ""


def validate_experiment_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate complete experiment data.
    
    Args:
        data: Complete experiment data dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Check for reagents
    solid_reagents = data.get("solid reagents", [])
    liquid_reagents = data.get("liquid reagents", [])
    
    if not solid_reagents and not liquid_reagents:
        errors.append("At least one reagent must be added")
    
    # Validate individual reagents
    for reagent in solid_reagents:
        reagent_errors = validate_reagent_data(reagent, "solid")
        errors.extend([f"Solid reagent '{reagent.get('name', 'Unknown')}': {error}" 
                      for error in reagent_errors])
    
    for reagent in liquid_reagents:
        reagent_errors = validate_reagent_data(reagent, "liquid")
        errors.extend([f"Liquid reagent '{reagent.get('name', 'Unknown')}': {error}" 
                      for error in reagent_errors])
    
    # Check for limiting reagent
    all_reagents = solid_reagents + liquid_reagents
    limiting_reagents = [r for r in all_reagents if abs(r.get("eq", 0) - 1.0) < 1e-6]
    
    if not limiting_reagents:
        errors.append("One reagent must have equivalents = 1.0 (limiting reagent)")
    elif len(limiting_reagents) > 1:
        errors.append("Only one reagent should have equivalents = 1.0")
    
    # Validate final details if present
    mass_scale = data.get("mass scale (in mg)")
    concentration = data.get("concentration (in mM)")
    
    if mass_scale is not None and mass_scale <= 0:
        errors.append("Mass scale must be greater than 0")
    
    if concentration is not None and concentration <= 0:
        errors.append("Concentration must be greater than 0")
    
    return errors


__all__ = [
    'validate_reagent_data',
    'validate_smiles', 
    'try_sanitize_smiles',
    'validate_experiment_data'
]