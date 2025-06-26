"""
Data models for Phase 1 Reagent Entry.

This module defines clear data structures and validation rules for reagents
and experiments, providing a clean interface between UI and data layers.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from ..utils.validation import validate_reagent_data, validate_experiment_data
from ..utils.chemistry import normalize_chemical_data


@dataclass
class ReagentModel:
    """
    Data model for a chemical reagent.
    
    This class provides a clean interface for reagent data with validation
    and automatic field normalization.
    """
    
    # Required fields
    name: str
    molecular_weight: float
    equivalents: float
    position: int  # Syringe position
    
    # Chemical identifiers (optional but recommended)
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    inchi_key: Optional[str] = None
    formula: Optional[str] = None
    
    # Liquid-specific fields
    density: Optional[float] = None  # g/mL, required for liquids
    
    # Additional metadata
    cas_number: Optional[str] = None
    pubchem_cid: Optional[str] = None
    supplier: Optional[str] = None
    catalog_number: Optional[str] = None
    
    # Internal fields
    reagent_type: str = field(default="solid")  # "solid" or "liquid"
    _validated: bool = field(default=False, init=False)
    _errors: List[str] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        self.validate()
        self.normalize()
    
    def validate(self) -> bool:
        """
        Validate reagent data and store errors.
        
        Returns:
            True if valid, False otherwise
        """
        # Convert to old format for validation
        old_format_data = self.to_old_format()
        self._errors = validate_reagent_data(old_format_data, self.reagent_type)
        self._validated = len(self._errors) == 0
        return self._validated
    
    def normalize(self) -> None:
        """Normalize chemical data using RDKit if available."""
        if self.smiles:
            # Create data dict for normalization
            data = {
                'smiles': self.smiles,
                'molecular_weight': self.molecular_weight,
                'formula': self.formula,
                'inchi': self.inchi,
                'inchikey': self.inchi_key
            }
            
            normalized = normalize_chemical_data(data)
            
            # Update fields with normalized data
            self.smiles = normalized.get('smiles', self.smiles)
            self.formula = normalized.get('formula', self.formula)
            self.inchi = normalized.get('inchi', self.inchi)
            self.inchi_key = normalized.get('inchikey', self.inchi_key)
            
            # Update molecular weight if it was auto-calculated
            if not self.molecular_weight or self.molecular_weight == 0:
                self.molecular_weight = normalized.get('molecular_weight', self.molecular_weight)
    
    @property
    def is_valid(self) -> bool:
        """Check if reagent data is valid."""
        return self._validated
    
    @property
    def errors(self) -> List[str]:
        """Get validation errors."""
        return self._errors.copy()
    
    @property
    def is_limiting(self) -> bool:
        """Check if this is the limiting reagent (eq = 1.0)."""
        return abs(self.equivalents - 1.0) < 1e-6
    
    def to_old_format(self) -> Dict[str, Any]:
        """
        Convert to old ReagentUI format for backward compatibility.
        
        Returns:
            Dictionary in old format
        """
        data = {
            "name": self.name,
            "molecular weight (in g/mol)": self.molecular_weight,
            "eq": self.equivalents,
            "syringe": self.position,
        }
        
        # Add chemical identifiers
        if self.smiles:
            data["SMILES"] = self.smiles
        if self.inchi:
            data["inChi"] = self.inchi
        if self.inchi_key:
            data["inChi Key"] = self.inchi_key
        
        # Add liquid-specific fields
        if self.reagent_type == "liquid" and self.density:
            data["density (in g/mL)"] = self.density
        
        return data
    
    @classmethod
    def from_old_format(cls, data: Dict[str, Any], reagent_type: str = "solid") -> 'ReagentModel':
        """
        Create ReagentModel from old format data.
        
        Args:
            data: Dictionary in old ReagentUI format
            reagent_type: "solid" or "liquid"
            
        Returns:
            ReagentModel instance
        """
        return cls(
            name=data.get("name", ""),
            molecular_weight=data.get("molecular weight (in g/mol)", 0.0),
            equivalents=data.get("eq", 1.0),
            position=data.get("syringe", 1),
            smiles=data.get("SMILES"),
            inchi=data.get("inChi"),
            inchi_key=data.get("inChi Key"),
            density=data.get("density (in g/mL)") if reagent_type == "liquid" else None,
            reagent_type=reagent_type
        )
    
    @classmethod
    def from_pubchem_data(cls, compound_data: Dict[str, Any], reagent_type: str = "solid",
                         equivalents: float = 1.0, position: int = 1) -> 'ReagentModel':
        """
        Create ReagentModel from PubChem compound data.
        
        Args:
            compound_data: PubChem compound dictionary
            reagent_type: "solid" or "liquid"
            equivalents: Chemical equivalents
            position: Syringe position
            
        Returns:
            ReagentModel instance
        """
        return cls(
            name=compound_data.get('name', ''),
            molecular_weight=compound_data.get('molecular_weight', 0.0),
            equivalents=equivalents,
            position=position,
            smiles=compound_data.get('smiles'),
            inchi=compound_data.get('inchi'),
            inchi_key=compound_data.get('inchikey'),
            formula=compound_data.get('formula'),
            density=compound_data.get('density') if reagent_type == "liquid" else None,
            reagent_type=reagent_type,
            pubchem_cid=str(compound_data.get('cid', '')) if compound_data.get('cid') else None
        )


@dataclass
class ExperimentModel:
    """
    Data model for a complete reagent entry experiment.
    
    This class manages collections of reagents and experiment parameters.
    """
    
    # Reagent collections
    solid_reagents: List[ReagentModel] = field(default_factory=list)
    liquid_reagents: List[ReagentModel] = field(default_factory=list)
    
    # Experiment parameters
    mass_scale: Optional[float] = None  # mg
    concentration: Optional[float] = None  # mM
    solvent: Optional[str] = None
    
    # Metadata
    experiment_name: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    
    # Internal fields
    _validated: bool = field(default=False, init=False)
    _errors: List[str] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate experiment after initialization."""
        self.validate()
    
    @property
    def all_reagents(self) -> List[ReagentModel]:
        """Get all reagents (solid + liquid)."""
        return self.solid_reagents + self.liquid_reagents
    
    @property
    def limiting_reagent(self) -> Optional[ReagentModel]:
        """Get the limiting reagent (eq = 1.0)."""
        for reagent in self.all_reagents:
            if reagent.is_limiting:
                return reagent
        return None
    
    @property
    def total_reagent_count(self) -> int:
        """Get total number of reagents."""
        return len(self.solid_reagents) + len(self.liquid_reagents)
    
    @property
    def is_valid(self) -> bool:
        """Check if experiment data is valid."""
        return self._validated
    
    @property
    def errors(self) -> List[str]:
        """Get validation errors."""
        return self._errors.copy()
    
    def add_reagent(self, reagent: ReagentModel) -> bool:
        """
        Add a reagent to the appropriate collection.
        
        Args:
            reagent: ReagentModel to add
            
        Returns:
            True if added successfully
        """
        if not reagent.is_valid:
            return False
        
        if reagent.reagent_type == "solid":
            self.solid_reagents.append(reagent)
        elif reagent.reagent_type == "liquid":
            self.liquid_reagents.append(reagent)
        else:
            return False
        
        self.validate()
        return True
    
    def remove_reagent(self, reagent: ReagentModel) -> bool:
        """
        Remove a reagent from the collections.
        
        Args:
            reagent: ReagentModel to remove
            
        Returns:
            True if removed successfully
        """
        try:
            if reagent in self.solid_reagents:
                self.solid_reagents.remove(reagent)
            elif reagent in self.liquid_reagents:
                self.liquid_reagents.remove(reagent)
            else:
                return False
            
            self.validate()
            return True
        except ValueError:
            return False
    
    def validate(self) -> bool:
        """
        Validate complete experiment data.
        
        Returns:
            True if valid, False otherwise
        """
        # Convert to old format for validation
        old_format_data = self.to_old_format()
        self._errors = validate_experiment_data(old_format_data)
        
        # Add reagent-specific errors
        for reagent in self.all_reagents:
            if not reagent.is_valid:
                for error in reagent.errors:
                    self._errors.append(f"{reagent.name}: {error}")
        
        self._validated = len(self._errors) == 0
        return self._validated
    
    def to_old_format(self) -> Dict[str, Any]:
        """
        Convert to old ReagentUI format for backward compatibility.
        
        Returns:
            Dictionary in old format
        """
        data = {
            "solid reagents": [r.to_old_format() for r in self.solid_reagents],
            "liquid reagents": [r.to_old_format() for r in self.liquid_reagents]
        }
        
        # Add experiment parameters
        if self.mass_scale is not None:
            data["mass scale (in mg)"] = self.mass_scale
        if self.concentration is not None:
            data["concentration (in mM)"] = self.concentration
        if self.solvent is not None:
            data["solvent"] = self.solvent
        
        return data
    
    @classmethod
    def from_old_format(cls, data: Dict[str, Any]) -> 'ExperimentModel':
        """
        Create ExperimentModel from old format data.
        
        Args:
            data: Dictionary in old ReagentUI format
            
        Returns:
            ExperimentModel instance
        """
        experiment = cls()
        
        # Load reagents
        for reagent_data in data.get("solid reagents", []):
            reagent = ReagentModel.from_old_format(reagent_data, "solid")
            experiment.solid_reagents.append(reagent)
        
        for reagent_data in data.get("liquid reagents", []):
            reagent = ReagentModel.from_old_format(reagent_data, "liquid")
            experiment.liquid_reagents.append(reagent)
        
        # Load experiment parameters
        experiment.mass_scale = data.get("mass scale (in mg)")
        experiment.concentration = data.get("concentration (in mM)")
        experiment.solvent = data.get("solvent")
        
        experiment.validate()
        return experiment
    
    def calculate_volumes(self) -> Dict[str, float]:
        """
        Calculate required volumes for all liquid reagents.
        
        Returns:
            Dictionary mapping reagent names to volumes in mL
        """
        if not self.limiting_reagent or not self.mass_scale or not self.concentration:
            return {}
        
        limiting_mw = self.limiting_reagent.molecular_weight
        limiting_moles = (self.mass_scale / 1000) / limiting_mw  # Convert mg to g, then to mol
        
        volumes = {}
        for reagent in self.liquid_reagents:
            if reagent.density:
                reagent_moles = limiting_moles * reagent.equivalents
                reagent_mass_g = reagent_moles * reagent.molecular_weight
                volume_ml = reagent_mass_g / reagent.density
                volumes[reagent.name] = volume_ml
        
        return volumes


__all__ = ['ReagentModel', 'ExperimentModel']