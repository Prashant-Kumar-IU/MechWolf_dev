"""
PubChem Integration

Enhanced PubChem integration that works with the existing ReagentUI PubChemService
or provides fallback functionality.
"""

from typing import Dict, Any, Optional
import warnings

try:
    from ..ReagentUI.PubChemService import PubChemService as BasePubChemService
    PUBCHEM_AVAILABLE = True
except ImportError:
    BasePubChemService = None
    PUBCHEM_AVAILABLE = False


class PubChemIntegration:
    """Enhanced PubChem integration for reagent lookup"""
    
    def __init__(self):
        """Initialize PubChem integration"""
        if PUBCHEM_AVAILABLE:
            self.service = BasePubChemService()
        else:
            self.service = None
            warnings.warn("PubChem service not available - reagent lookup disabled")
    
    def lookup_compound(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Look up compound by name
        
        Args:
            name: Compound name to search for
            
        Returns:
            Dictionary with compound data or None if not found
        """
        if not self.service:
            return None
            
        try:
            return self.service.get_compound_by_name(name)
        except Exception as e:
            print(f"Warning: PubChem lookup failed: {e}")
            return None
    
    def lookup_by_inchi(self, inchi: str) -> Optional[Dict[str, Any]]:
        """
        Look up compound by InChI
        
        Args:
            inchi: InChI string to search for
            
        Returns:
            Dictionary with compound data or None if not found
        """
        if not self.service or not hasattr(self.service, 'get_compound_by_inchi'):
            return None
            
        try:
            return self.service.get_compound_by_inchi(inchi)
        except Exception as e:
            print(f"Warning: PubChem InChI lookup failed: {e}")
            return None
    
    def get_structure_image(self, compound_id: str) -> Optional[str]:
        """
        Get structure image URL for compound
        
        Args:
            compound_id: PubChem compound ID
            
        Returns:
            Image URL or None if not available
        """
        if not compound_id:
            return None
            
        try:
            # PubChem structure image URL format
            return f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{compound_id}/PNG"
        except Exception:
            return None
    
    def validate_molecular_data(self, name: str, molecular_weight: float, 
                              inchi: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate molecular data against PubChem
        
        Args:
            name: Compound name
            molecular_weight: Provided molecular weight
            inchi: Optional InChI string
            
        Returns:
            Dictionary with validation results and suggestions
        """
        result = {
            "valid": True,
            "warnings": [],
            "suggestions": {},
            "pubchem_data": None
        }
        
        if not self.service:
            result["warnings"].append("PubChem validation not available")
            return result
        
        try:
            # Look up compound
            pubchem_data = self.lookup_compound(name)
            
            if not pubchem_data:
                result["warnings"].append(f"Compound '{name}' not found in PubChem")
                return result
            
            result["pubchem_data"] = pubchem_data
            
            # Validate molecular weight
            pubchem_mw = pubchem_data.get("molecular_weight")
            if pubchem_mw:
                mw_diff = abs(molecular_weight - pubchem_mw)
                mw_percent_diff = (mw_diff / pubchem_mw) * 100
                
                if mw_percent_diff > 5:  # More than 5% difference
                    result["warnings"].append(
                        f"Molecular weight differs from PubChem: "
                        f"provided {molecular_weight}, PubChem {pubchem_mw}"
                    )
                    result["suggestions"]["molecular_weight"] = pubchem_mw
            
            # Validate InChI if provided
            if inchi:
                pubchem_inchi = pubchem_data.get("inchi")
                if pubchem_inchi and inchi != pubchem_inchi:
                    result["warnings"].append("InChI differs from PubChem data")
                    result["suggestions"]["inchi"] = pubchem_inchi
            else:
                # Suggest InChI if not provided
                pubchem_inchi = pubchem_data.get("inchi")
                if pubchem_inchi:
                    result["suggestions"]["inchi"] = pubchem_inchi
            
            # Suggest InChI Key if not provided
            pubchem_inchi_key = pubchem_data.get("inchi_key")
            if pubchem_inchi_key:
                result["suggestions"]["inchi_key"] = pubchem_inchi_key
                
        except Exception as e:
            result["warnings"].append(f"PubChem validation error: {e}")
        
        return result
    
    def is_available(self) -> bool:
        """Check if PubChem service is available"""
        return self.service is not None
    
    def search_similar_compounds(self, name: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Search for similar compounds (if supported by service)
        
        Args:
            name: Compound name to search for
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similar compounds
        """
        if not self.service or not hasattr(self.service, 'search_similar'):
            return []
            
        try:
            return self.service.search_similar(name, threshold)
        except Exception as e:
            print(f"Warning: Similar compound search failed: {e}")
            return []