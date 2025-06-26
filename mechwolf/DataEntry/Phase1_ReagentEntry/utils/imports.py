"""
Centralized import handling for Phase1_ReagentEntry.

This module provides a single place to handle all the fallback import patterns
that were duplicated across multiple files in the original codebase.
"""

import sys
import os
from contextlib import contextmanager
from typing import Any, Optional, Callable


@contextmanager
def suppress_stderr():
    """
    Context manager to suppress stderr output.
    
    Yields:
        None
    """
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr


def safe_import(module_paths: list, fallback_factory: Optional[Callable] = None) -> Any:
    """
    Safely import a module with fallback paths.
    
    Args:
        module_paths: List of module paths to try in order
        fallback_factory: Function to create fallback if all imports fail
        
    Returns:
        Imported module or fallback object
        
    Example:
        >>> validate_smiles = safe_import([
        ...     'mechwolf.DataEntry.Phase1_ReagentEntry.utils.validation.validate_smiles',
        ...     'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.reagent_utils.validate_smiles'
        ... ], lambda smiles: bool(smiles))
    """
    for module_path in module_paths:
        try:
            # Split module path and attribute
            if '.' in module_path:
                parts = module_path.split('.')
                # Try to find the split point between module and attribute
                for i in range(len(parts) - 1, 0, -1):
                    module_name = '.'.join(parts[:i])
                    attr_path = parts[i:]
                    
                    try:
                        module = __import__(module_name, fromlist=[attr_path[0]])
                        result = module
                        
                        # Navigate through nested attributes
                        for attr in attr_path:
                            result = getattr(result, attr)
                        
                        return result
                    except (ImportError, AttributeError):
                        continue
            else:
                # Simple module import
                return __import__(module_path)
                
        except ImportError:
            continue
    
    # If all imports failed, use fallback
    if fallback_factory:
        return fallback_factory()
    
    raise ImportError(f"Could not import any of: {module_paths}")


def get_reagent_utils():
    """
    Get reagent utility functions with fallback handling.
    
    Returns:
        Dictionary of utility functions
    """
    # Try to import from new location first, then old location
    utils = {}
    
    # Validation functions
    utils['validate_smiles'] = safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.utils.validation.validate_smiles',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.reagent_utils.validate_smiles'
    ], lambda: lambda smiles: bool(smiles and isinstance(smiles, str)))
    
    utils['validate_reagent_data'] = safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.utils.validation.validate_reagent_data',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.reagent_utils.validate_reagent_data'
    ], lambda: lambda data, reagent_type: [])
    
    # Chemistry functions
    utils['safe_mol_from_smiles'] = safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.utils.chemistry.safe_mol_from_smiles',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.reagent_utils.safe_mol_from_smiles'
    ], lambda: lambda smiles: None)
    
    utils['is_rdkit_available'] = safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.utils.chemistry.is_rdkit_available',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.reagent_utils.is_rdkit_available'
    ], lambda: lambda: False)
    
    return utils


def get_structure_visualization():
    """
    Get structure visualization class with fallback handling.
    
    Returns:
        StructureVisualization class or fallback
    """
    return safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.external.visualization.StructureVisualization',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.structure_visualization.StructureVisualization'
    ], lambda: type('StructureVisualization', (), {
        'get_structure_image': staticmethod(lambda smiles, size=(150, 150): None),
        'get_structure_output': staticmethod(lambda smiles, size=(180, 180): None)
    }))


def get_pubchem_service():
    """
    Get PubChem service class with fallback handling.
    
    Returns:
        PubChemService class or fallback
    """
    return safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.external.pubchem.PubChemService',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.pubchem_service.PubChemService'
    ], lambda: type('PubChemService', (), {
        '__init__': lambda self: None,
        'search': lambda self, query, search_type: [],
        'get_compound_by_name': lambda self, name: None
    }))


def get_data_adapter():
    """
    Get reagent data adapter class with fallback handling.
    
    Returns:
        ReagentDataAdapter class or fallback
    """
    return safe_import([
        'mechwolf.DataEntry.Phase1_ReagentEntry.core.data_adapter.ReagentDataAdapter',
        'mechwolf.DataEntry.Phase1_ReagentEntry.OldCode.data_adapter.ReagentDataAdapter'
    ], lambda: type('ReagentDataAdapter', (), {
        '__init__': lambda self, experiment_manager: None,
        'load_data': lambda self: {"solid reagents": [], "liquid reagents": []},
        'save_data': lambda self: True
    }))


# Convenience function for the most common use case
def import_with_fallback(primary_path: str, fallback_path: str, fallback_factory: Optional[Callable] = None):
    """
    Simple wrapper for the most common import pattern in the codebase.
    
    Args:
        primary_path: Preferred import path
        fallback_path: Fallback import path
        fallback_factory: Function to create fallback object
        
    Returns:
        Imported object or fallback
    """
    return safe_import([primary_path, fallback_path], fallback_factory)


__all__ = [
    'suppress_stderr',
    'safe_import', 
    'get_reagent_utils',
    'get_structure_visualization',
    'get_pubchem_service', 
    'get_data_adapter',
    'import_with_fallback'
]