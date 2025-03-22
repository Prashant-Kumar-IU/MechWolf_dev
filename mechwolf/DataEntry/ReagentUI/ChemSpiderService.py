"""ChemSpider API service for chemical data retrieval."""
import requests
from typing import Dict, Any, List, Optional
from mechwolf.DataEntry.ReagentUI.utils import validate_smiles, suppress_stderr, safe_mol_from_smiles

class ChemSpiderService:
    """Service for interacting with the ChemSpider API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the service with an API key and empty cache.
        
        Parameters:
        -----------
        api_key : str, optional
            ChemSpider API key. Required for searches.
        """
        self.api_key = api_key
        self.cache = {}
        self.base_url = "https://api.rsc.org/compounds/v1"
        
    def set_api_key(self, api_key: str) -> None:
        """
        Set the ChemSpider API key.
        
        Parameters:
        -----------
        api_key : str
            ChemSpider API key
        """
        self.api_key = api_key
    
    def search(self, query: str, search_type: str) -> List[Dict[str, Any]]:
        """
        Search ChemSpider database and return results.
        
        Parameters:
        -----------
        query : str
            Search query
        search_type : str
            Type of search ('name', 'smiles', 'inchi', 'inchi key', 'cas')
            
        Returns:
        --------
        list
            List of compound dictionaries with chemical data
        """
        # Check if API key is set
        if not self.api_key:
            return [{"error": "ChemSpider API key is not set. Please set your API key in the settings."}]
        
        # Check if result is in cache
        cache_key = f"{search_type}:{query}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Validate input before sending to ChemSpider
            if search_type == 'smiles' and not validate_smiles(query):
                return []
            
            # Set up headers with API key
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Perform search based on search type
            if search_type == 'name':
                # Search by name/text
                search_url = f"{self.base_url}/filter/text"
                payload = {"text": query, "orderBy": "relevance", "orderDirection": "descending"}
            elif search_type == 'smiles':
                # Search by SMILES
                search_url = f"{self.base_url}/filter/smiles"
                payload = {"smiles": query}
            elif search_type == 'inchi':
                # Search by InChI
                search_url = f"{self.base_url}/filter/inchi"
                payload = {"inchi": query}
            elif search_type == 'inchi key':
                # Search by InChIKey
                search_url = f"{self.base_url}/filter/inchikey"
                payload = {"inchikey": query}
            elif search_type == 'cas':
                # Search by CAS Registry Number
                search_url = f"{self.base_url}/filter/registry-number"
                payload = {"registryNumber": query}
            else:
                # Default to name search
                search_url = f"{self.base_url}/filter/text"
                payload = {"text": query, "orderBy": "relevance", "orderDirection": "descending"}
            
            # Perform search with timeout
            response = requests.post(search_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Get query ID from response
            query_id = response.json().get('queryId')
            if not query_id:
                return []
            
            # Get results using query ID
            results_url = f"{self.base_url}/filter/{query_id}/results"
            results_response = requests.get(results_url, headers=headers, timeout=10)
            results_response.raise_for_status()
            
            # Extract record IDs
            record_ids = [item.get('id') for item in results_response.json().get('results', [])]
            if not record_ids:
                return []
            
            # Limit to first 5 results
            record_ids = record_ids[:5]
            
            # Get details for each record
            compounds = []
            for record_id in record_ids:
                details_url = f"{self.base_url}/records/{record_id}/details"
                details_response = requests.get(details_url, headers=headers, timeout=10)
                details_response.raise_for_status()
                details = details_response.json()
                
                # Get SMILES representation
                smiles = ""
                smiles_url = f"{self.base_url}/records/{record_id}/smiles"
                smiles_response = requests.get(smiles_url, headers=headers, timeout=10)
                if smiles_response.status_code == 200:
                    smiles = smiles_response.json().get('smiles', '')
                
                # Validate SMILES
                with suppress_stderr():
                    if not safe_mol_from_smiles(smiles):
                        smiles = ''
                
                # Get InChI representation
                inchi = ""
                inchi_url = f"{self.base_url}/records/{record_id}/inchi"
                inchi_response = requests.get(inchi_url, headers=headers, timeout=10)
                if inchi_response.status_code == 200:
                    inchi = inchi_response.json().get('inchi', '')
                
                # Create compound dictionary
                compound = {
                    'cid': str(record_id),  # ChemSpider ID
                    'name': details.get('commonName', ''),
                    'formula': details.get('molecularFormula', ''),
                    'molecular_weight': float(details.get('molecularWeight', 0)),
                    'inchi': inchi,
                    'inchikey': details.get('inchiKey', ''),
                    'smiles': smiles,
                    'density': self.get_density(record_id)  # Get density if available
                }
                
                compounds.append(compound)
            
            # Cache results
            self.cache[cache_key] = compounds
            return compounds
            
        except requests.exceptions.Timeout:
            print("ChemSpider search timed out. Please try again later.")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Network error during ChemSpider search: {e}")
            return []
        except Exception as e:
            print(f"ChemSpider search error: {e}")
            return []
    
    def get_density(self, record_id: str) -> Optional[float]:
        """
        Retrieve the density for a compound from ChemSpider if available.
        
        Parameters:
        -----------
        record_id : str
            ChemSpider Record ID
            
        Returns:
        --------
        float or None
            Density in g/mL if available, None otherwise
        """
        try:
            if not self.api_key:
                return None
            
            # Set up headers with API key
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Get properties that might contain density information
            props_url = f"{self.base_url}/records/{record_id}/properties"
            response = requests.get(props_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
                
            # Parse properties to find density
            properties = response.json().get('properties', [])
            for prop in properties:
                # Look for density in different possible property names
                if prop.get('name', '').lower() in ['density', 'specific gravity', 'relative density']:
                    try:
                        # Extract numeric value from description
                        import re
                        value_str = prop.get('value', '')
                        match = re.search(r'([0-9]*\.?[0-9]+)', value_str)
                        if match:
                            return float(match.group(1))
                    except (ValueError, TypeError):
                        pass
            
            return None
            
        except Exception:
            return None
