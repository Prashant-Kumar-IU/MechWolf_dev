"""
Factory for creating different flow setup configurations.

This module provides a simple factory interface for creating different types
of flow chemistry apparatus setups without needing to know the specific
implementation details.
"""
from typing import List, Dict, Any, Optional
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import mechwolf as mw

from .config_templates import FLOW_CONFIGS, get_config
from .two_syringes_setup import TwoSyringesApparatusCreator
from .three_syringes_1r1m_setup import ThreeSyringes1R1MApparatusCreator
from .three_syringes_2r2m_setup import ThreeSyringes2R2MApparatusCreator
from .flexible_setup import FlexibleSetupApparatusCreator


class FlowSetupFactory:
    """Factory for creating flow setups"""
      # Map setup types to their creator classes
    _CREATORS = {
        'two_syringes_1r_1m': TwoSyringesApparatusCreator,
        'three_syringes_1r_1m': ThreeSyringes1R1MApparatusCreator,
        'three_syringes_2r_2m': ThreeSyringes2R2MApparatusCreator,
        'flexible_setup': FlexibleSetupApparatusCreator,
    }
    
    @classmethod
    def create_setup(cls, setup_type: str, pumps: List[HarvardSyringePump], 
                    data_file: Optional[str] = None) -> mw.Apparatus:
        """
        Create apparatus setup based on type.
        
        Args:
            setup_type: Type of setup to create
            pumps: List of pumps to use
            data_file: Optional JSON file for configuration
            
        Returns:
            Configured MechWolf Apparatus
            
        Raises:
            ValueError: If setup_type is not supported
        """
        if setup_type not in cls._CREATORS:
            available = list(cls._CREATORS.keys())
            raise ValueError(f"Unknown setup type: {setup_type}. Available: {available}")
        
        creator_class = cls._CREATORS[setup_type]
        creator = creator_class(*pumps, data_file=data_file)
        
        return creator.create_apparatus()
    
    @classmethod
    def create_creator(cls, setup_type: str, pumps: List[HarvardSyringePump], 
                      data_file: Optional[str] = None):
        """
        Create apparatus creator without immediately building apparatus.
        
        This is useful when you want to configure the creator before building.
        
        Args:
            setup_type: Type of setup to create
            pumps: List of pumps to use
            data_file: Optional JSON file for configuration
            
        Returns:
            Apparatus creator instance
        """
        if setup_type not in cls._CREATORS:
            available = list(cls._CREATORS.keys())
            raise ValueError(f"Unknown setup type: {setup_type}. Available: {available}")
        
        creator_class = cls._CREATORS[setup_type]
        return creator_class(*pumps, data_file=data_file)
    
    @classmethod
    def available_setups(cls) -> List[str]:
        """Return list of available setup types"""
        return list(cls._CREATORS.keys())
    
    @classmethod
    def get_setup_info(cls, setup_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about available setups.
        
        Args:
            setup_type: Specific setup to get info for, or None for all
            
        Returns:
            Dictionary with setup information
        """
        if setup_type:
            if setup_type not in FLOW_CONFIGS:
                raise ValueError(f"Unknown setup type: {setup_type}")
            
            config = get_config(setup_type)
            return {
                'name': config.name,
                'description': config.description,
                'num_vessels': config.num_vessels,
                'num_coils': config.num_coils,
                'num_mixers': config.num_mixers,
                'coil_letters': config.coil_letters
            }
        else:
            # Return info for all setups
            return {
                setup_type: {
                    'name': config.name,
                    'description': config.description,
                    'num_vessels': config.num_vessels,
                    'num_coils': config.num_coils,
                    'num_mixers': config.num_mixers,
                    'coil_letters': config.coil_letters
                }
                for setup_type, config in FLOW_CONFIGS.items()
            }
    
    @classmethod
    def print_available_setups(cls) -> None:
        """Print a formatted list of available setups"""
        print("Available Flow Setup Types:")
        print("=" * 50)
        
        for setup_type in cls.available_setups():
            info = cls.get_setup_info(setup_type)
            print(f"\n{setup_type}:")
            print(f"  Name: {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  Vessels: {info['num_vessels']} (+ 1 product vessel)")
            print(f"  Coils: {info['num_coils']} ({', '.join(info['coil_letters'])})")
            print(f"  Mixers: {info['num_mixers']}")
