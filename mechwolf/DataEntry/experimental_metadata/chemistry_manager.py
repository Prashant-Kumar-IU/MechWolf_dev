"""
Chemistry Data Manager - Handles reagent and chemical information

This module manages the chemistry section of experimental metadata, including
solid reagents, liquid reagents, stoichiometry, and reaction conditions.
"""

from typing import Dict, Any, List, Optional, Union
from .schema_definitions import get_current_timestamp


class ChemistryDataManager:
    """
    Manager for chemistry-related experimental data
    
    Handles:
    - Solid and liquid reagents with chemical properties
    - Stoichiometry and equivalents
    - Reaction scale and concentration
    - Solvent information
    """
    
    def __init__(self, metadata_manager):
        """Initialize with reference to main metadata manager"""
        self.metadata_manager = metadata_manager
        self.section_name = "chemistry"
    
    def get_data(self) -> Dict[str, Any]:
        """Get the chemistry section data"""
        return self.metadata_manager.get_section_data(self.section_name)
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save chemistry section data"""
        return self.metadata_manager.update_section_data(self.section_name, data)
    
    # Reagent Management
    def add_solid_reagent(self, reagent: Dict[str, Any]) -> bool:
        """
        Add a solid reagent to the experiment
        
        Args:
            reagent: Dictionary with reagent properties
                Required: name, molecular_weight
                Optional: inChi, inChi_Key, SMILES, eq, mass, position, syringe
        
        Returns:
            True if added successfully
        """
        # Validate required fields
        if not reagent.get("name") or not reagent.get("molecular_weight"):
            print("❌ Reagent must have 'name' and 'molecular_weight'")
            return False
        
        data = self.get_data()
        if "solid_reagents" not in data:
            data["solid_reagents"] = []
        
        # Check for duplicates
        existing_names = [r.get("name") for r in data["solid_reagents"]]
        if reagent["name"] in existing_names:
            print(f"⚠️  Solid reagent '{reagent['name']}' already exists. Use update_solid_reagent() to modify.")
            return False
        
        data["solid_reagents"].append(reagent)
        return self.save_data(data)
    
    def add_liquid_reagent(self, reagent: Dict[str, Any]) -> bool:
        """
        Add a liquid reagent to the experiment
        
        Args:
            reagent: Dictionary with reagent properties
                Required: name, molecular_weight
                Optional: inChi, inChi_Key, SMILES, eq, volume, density, position, syringe
        
        Returns:
            True if added successfully
        """
        # Validate required fields
        if not reagent.get("name") or not reagent.get("molecular_weight"):
            print("❌ Reagent must have 'name' and 'molecular_weight'")
            return False
        
        data = self.get_data()
        if "liquid_reagents" not in data:
            data["liquid_reagents"] = []
        
        # Check for duplicates
        existing_names = [r.get("name") for r in data["liquid_reagents"]]
        if reagent["name"] in existing_names:
            print(f"⚠️  Liquid reagent '{reagent['name']}' already exists. Use update_liquid_reagent() to modify.")
            return False
        
        data["liquid_reagents"].append(reagent)
        return self.save_data(data)
    
    def update_solid_reagent(self, reagent_name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing solid reagent"""
        data = self.get_data()
        
        for i, reagent in enumerate(data.get("solid_reagents", [])):
            if reagent.get("name") == reagent_name:
                data["solid_reagents"][i].update(updates)
                return self.save_data(data)
        
        print(f"❌ Solid reagent '{reagent_name}' not found")
        return False
    
    def update_liquid_reagent(self, reagent_name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing liquid reagent"""
        data = self.get_data()
        
        for i, reagent in enumerate(data.get("liquid_reagents", [])):
            if reagent.get("name") == reagent_name:
                data["liquid_reagents"][i].update(updates)
                return self.save_data(data)
        
        print(f"❌ Liquid reagent '{reagent_name}' not found")
        return False
    
    def remove_reagent(self, reagent_name: str, reagent_type: str = "auto") -> bool:
        """
        Remove a reagent from the experiment
        
        Args:
            reagent_name: Name of the reagent to remove
            reagent_type: "solid", "liquid", or "auto" to search both
        
        Returns:
            True if removed successfully
        """
        data = self.get_data()
        removed = False
        
        if reagent_type in ["solid", "auto"]:
            solid_reagents = data.get("solid_reagents", [])
            data["solid_reagents"] = [r for r in solid_reagents if r.get("name") != reagent_name]
            if len(data["solid_reagents"]) < len(solid_reagents):
                removed = True
        
        if reagent_type in ["liquid", "auto"]:
            liquid_reagents = data.get("liquid_reagents", [])
            data["liquid_reagents"] = [r for r in liquid_reagents if r.get("name") != reagent_name]
            if len(data["liquid_reagents"]) < len(liquid_reagents):
                removed = True
        
        if removed:
            return self.save_data(data)
        else:
            print(f"❌ Reagent '{reagent_name}' not found")
            return False
    
    # Bulk Operations
    def update_reagents(self, reagent_data: Dict[str, Any]) -> bool:
        """
        Update multiple reagents at once
        
        Args:
            reagent_data: Dictionary that may contain 'solid_reagents' and/or 'liquid_reagents'
        
        Returns:
            True if updated successfully
        """
        data = self.get_data()
        
        if "solid_reagents" in reagent_data:
            data["solid_reagents"] = reagent_data["solid_reagents"]
        
        if "liquid_reagents" in reagent_data:
            data["liquid_reagents"] = reagent_data["liquid_reagents"]
        
        return self.save_data(data)
    
    def clear_all_reagents(self) -> bool:
        """Clear all reagents (useful for starting fresh)"""
        data = self.get_data()
        data["solid_reagents"] = []
        data["liquid_reagents"] = []
        return self.save_data(data)
    
    # Reaction Conditions
    def set_reaction_scale(self, mass_scale: float, concentration: float, solvent: str) -> bool:
        """
        Set the overall reaction scale and conditions
        
        Args:
            mass_scale: Mass scale in mg
            concentration: Concentration in mM  
            solvent: Solvent name
        
        Returns:
            True if set successfully
        """
        data = self.get_data()
        data.update({
            "mass_scale": mass_scale,
            "concentration": concentration,
            "solvent": solvent
        })
        return self.save_data(data)
    
    def set_limiting_reagent(self, reagent_name: str) -> bool:
        """Set the limiting reagent for the reaction"""
        data = self.get_data()
        data["limiting_reagent"] = reagent_name
        return self.save_data(data)
    
    def set_solvent_volumes(self, volumes: List[float]) -> bool:
        """Set solvent volumes"""
        data = self.get_data()
        data["solvent_volume"] = volumes
        return self.save_data(data)
    
    # Query Methods
    def get_reagent_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific reagent by name"""
        data = self.get_data()
        
        # Search solid reagents
        for reagent in data.get("solid_reagents", []):
            if reagent.get("name") == name:
                return reagent.copy()
        
        # Search liquid reagents
        for reagent in data.get("liquid_reagents", []):
            if reagent.get("name") == name:
                return reagent.copy()
        
        return None
    
    def get_all_reagents(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all reagents organized by type"""
        data = self.get_data()
        return {
            "solid_reagents": data.get("solid_reagents", []).copy(),
            "liquid_reagents": data.get("liquid_reagents", []).copy()
        }
    
    def get_reagent_count(self) -> Dict[str, int]:
        """Get count of reagents by type"""
        data = self.get_data()
        return {
            "solid": len(data.get("solid_reagents", [])),
            "liquid": len(data.get("liquid_reagents", [])),
            "total": len(data.get("solid_reagents", [])) + len(data.get("liquid_reagents", []))
        }
    
    def get_reaction_conditions(self) -> Dict[str, Any]:
        """Get reaction scale and conditions"""
        data = self.get_data()
        return {
            "mass_scale": data.get("mass_scale"),
            "concentration": data.get("concentration"),
            "solvent": data.get("solvent"),
            "limiting_reagent": data.get("limiting_reagent"),
            "solvent_volume": data.get("solvent_volume", [])
        }
    
    # Validation and Utilities
    def validate_stoichiometry(self) -> List[str]:
        """Validate reagent stoichiometry and return any issues"""
        issues = []
        data = self.get_data()
        
        # Check if limiting reagent is defined and exists
        limiting_reagent = data.get("limiting_reagent")
        if limiting_reagent:
            if not self.get_reagent_by_name(limiting_reagent):
                issues.append(f"Limiting reagent '{limiting_reagent}' not found in reagent list")
        
        # Check for reagents without equivalents
        all_reagents = data.get("solid_reagents", []) + data.get("liquid_reagents", [])
        for reagent in all_reagents:
            if reagent.get("eq") is None and reagent.get("name") != limiting_reagent:
                issues.append(f"Reagent '{reagent.get('name')}' missing equivalents")
        
        # Check for missing masses/volumes
        for reagent in data.get("solid_reagents", []):
            if reagent.get("mass") is None:
                issues.append(f"Solid reagent '{reagent.get('name')}' missing mass")
        
        for reagent in data.get("liquid_reagents", []):
            if reagent.get("volume") is None and reagent.get("density") is None:
                issues.append(f"Liquid reagent '{reagent.get('name')}' missing volume or density")
        
        return issues
    
    def calculate_masses_from_scale(self) -> Dict[str, float]:
        """Calculate reagent masses based on reaction scale and stoichiometry"""
        data = self.get_data()
        masses = {}
        
        mass_scale = data.get("mass_scale")
        limiting_reagent_name = data.get("limiting_reagent")
        
        if not mass_scale or not limiting_reagent_name:
            return masses
        
        limiting_reagent = self.get_reagent_by_name(limiting_reagent_name)
        if not limiting_reagent:
            return masses
        
        limiting_mw = limiting_reagent.get("molecular_weight")
        if not limiting_mw:
            return masses
        
        # Calculate moles of limiting reagent
        limiting_moles = mass_scale / limiting_mw
        
        # Calculate masses for all reagents
        all_reagents = data.get("solid_reagents", []) + data.get("liquid_reagents", [])
        for reagent in all_reagents:
            name = reagent.get("name")
            eq = reagent.get("eq", 1.0)
            mw = reagent.get("molecular_weight")
            
            if name and eq is not None and mw:
                required_moles = limiting_moles * eq
                required_mass = required_moles * mw
                masses[name] = required_mass
        
        return masses
    
    def export_chemistry_summary(self) -> str:
        """Export a human-readable chemistry summary"""
        data = self.get_data()
        conditions = self.get_reaction_conditions()
        counts = self.get_reagent_count()
        
        summary = f"""
🧪 Chemistry Summary
═══════════════════
📊 Reaction Scale:
   • Mass Scale: {conditions['mass_scale']} mg
   • Concentration: {conditions['concentration']} mM  
   • Solvent: {conditions['solvent']}
   • Limiting Reagent: {conditions['limiting_reagent']}

📈 Reagent Count:
   • Solid Reagents: {counts['solid']}
   • Liquid Reagents: {counts['liquid']}
   • Total: {counts['total']}

⚗️  Solid Reagents:
        """
        
        for reagent in data.get("solid_reagents", []):
            summary += f"\n   • {reagent.get('name')} ({reagent.get('molecular_weight')} g/mol)"
            if reagent.get("eq"):
                summary += f" - {reagent.get('eq')} eq"
            if reagent.get("mass"):
                summary += f" - {reagent.get('mass')} mg"
        
        summary += "\n\n🧴 Liquid Reagents:"
        for reagent in data.get("liquid_reagents", []):
            summary += f"\n   • {reagent.get('name')} ({reagent.get('molecular_weight')} g/mol)"
            if reagent.get("eq"):
                summary += f" - {reagent.get('eq')} eq"
            if reagent.get("volume"):
                summary += f" - {reagent.get('volume')} mL"
        
        return summary.strip()