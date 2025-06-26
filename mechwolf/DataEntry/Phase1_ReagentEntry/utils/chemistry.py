"""
Chemistry-specific utility functions.

This module contains functions for handling chemical data, SMILES strings,
and molecular representations, extracted from the original reagent_utils.py.
"""

from typing import Optional, Any
from .imports import suppress_stderr


def is_rdkit_available() -> bool:
    """
    Check if RDKit is available in the environment.
    
    Returns:
        True if RDKit is available, False otherwise
    """
    try:
        import rdkit
        return True
    except ImportError:
        return False


def safe_mol_from_smiles(smiles: str) -> Optional[Any]:
    """
    Create a molecule from SMILES with error suppression.
    
    Args:
        smiles: The SMILES string to convert
        
    Returns:
        RDKit Mol object if successful, None otherwise
    """
    if not smiles or not isinstance(smiles, str):
        return None
        
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        # Disable RDKit logging
        RDLogger.DisableLog('rdApp')
        
        with suppress_stderr():
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            if mol is not None:
                try:
                    Chem.SanitizeMol(mol)
                except:
                    pass
            return mol
    except ImportError:
        return None
    except:
        return None


def canonical_smiles(smiles: str) -> Optional[str]:
    """
    Convert SMILES to canonical form using RDKit.
    
    Args:
        smiles: Input SMILES string
        
    Returns:
        Canonical SMILES string if successful, None otherwise
    """
    mol = safe_mol_from_smiles(smiles)
    if mol is None:
        return None
    
    try:
        from rdkit import Chem
        return Chem.MolToSmiles(mol)
    except ImportError:
        return None
    except:
        return None


def mol_weight_from_smiles(smiles: str) -> Optional[float]:
    """
    Calculate molecular weight from SMILES string.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Molecular weight in g/mol if successful, None otherwise
    """
    mol = safe_mol_from_smiles(smiles)
    if mol is None:
        return None
    
    try:
        from rdkit.Chem import rdMolDescriptors
        return rdMolDescriptors.CalcExactMolWt(mol)
    except ImportError:
        return None
    except:
        return None


def mol_formula_from_smiles(smiles: str) -> Optional[str]:
    """
    Get molecular formula from SMILES string.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Molecular formula if successful, None otherwise
    """
    mol = safe_mol_from_smiles(smiles)
    if mol is None:
        return None
    
    try:
        from rdkit.Chem import rdMolDescriptors
        return rdMolDescriptors.CalcMolFormula(mol)
    except ImportError:
        return None
    except:
        return None


def inchi_from_smiles(smiles: str) -> Optional[str]:
    """
    Convert SMILES to InChI string.
    
    Args:
        smiles: SMILES string
        
    Returns:
        InChI string if successful, None otherwise
    """
    mol = safe_mol_from_smiles(smiles)
    if mol is None:
        return None
    
    try:
        from rdkit import Chem
        return Chem.MolToInchi(mol)
    except ImportError:
        return None
    except:
        return None


def inchi_key_from_smiles(smiles: str) -> Optional[str]:
    """
    Convert SMILES to InChI Key.
    
    Args:
        smiles: SMILES string
        
    Returns:
        InChI Key if successful, None otherwise
    """
    mol = safe_mol_from_smiles(smiles)
    if mol is None:
        return None
    
    try:
        from rdkit import Chem
        return Chem.MolToInchiKey(mol)
    except ImportError:
        return None
    except:
        return None


def normalize_chemical_data(compound_data: dict) -> dict:
    """
    Normalize chemical data by auto-filling missing fields when possible.
    
    Args:
        compound_data: Dictionary with chemical data
        
    Returns:
        Updated dictionary with auto-filled fields
    """
    normalized = compound_data.copy()
    
    # If we have SMILES, try to auto-fill other fields
    smiles = normalized.get('smiles') or normalized.get('SMILES')
    if smiles and is_rdkit_available():
        
        # Auto-fill molecular weight if missing
        if not normalized.get('molecular_weight') and not normalized.get('molecular weight (in g/mol)'):
            mw = mol_weight_from_smiles(smiles)
            if mw:
                normalized['molecular_weight'] = mw
                normalized['molecular weight (in g/mol)'] = mw
        
        # Auto-fill molecular formula if missing
        if not normalized.get('formula'):
            formula = mol_formula_from_smiles(smiles)
            if formula:
                normalized['formula'] = formula
        
        # Auto-fill InChI if missing
        if not normalized.get('inchi') and not normalized.get('inChi'):
            inchi = inchi_from_smiles(smiles)
            if inchi:
                # Remove the 'InChI=' prefix for storage
                clean_inchi = inchi[6:] if inchi.startswith('InChI=') else inchi
                normalized['inchi'] = clean_inchi
                normalized['inChi'] = clean_inchi
        
        # Auto-fill InChI Key if missing
        if not normalized.get('inchikey') and not normalized.get('inChi Key'):
            inchi_key = inchi_key_from_smiles(smiles)
            if inchi_key:
                normalized['inchikey'] = inchi_key
                normalized['inChi Key'] = inchi_key
        
        # Canonicalize SMILES
        canonical = canonical_smiles(smiles)
        if canonical:
            normalized['smiles'] = canonical
            normalized['SMILES'] = canonical
    
    return normalized


__all__ = [
    'is_rdkit_available',
    'safe_mol_from_smiles',
    'canonical_smiles',
    'mol_weight_from_smiles',
    'mol_formula_from_smiles', 
    'inchi_from_smiles',
    'inchi_key_from_smiles',
    'normalize_chemical_data'
]