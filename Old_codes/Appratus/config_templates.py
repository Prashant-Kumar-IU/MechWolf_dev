"""
Configuration templates for different flow setup types.

This module defines the available flow setup configurations that can be used
to create apparatus with different combinations of vessels, coils, and mixers.
"""
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class FlowSetupConfig:
    """Configuration template for different flow setups"""
    name: str
    num_vessels: int  # excluding product vessel
    num_coils: int
    num_mixers: int
    coil_letters: List[str]
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for widget creation"""
        return {
            'num_vessels': self.num_vessels + 1,  # +1 for product vessel
            'num_tubes': 1,  # assuming always 1 reaction tube type
            'num_coils': self.num_coils,
            'num_mixers': self.num_mixers,
            'coil_letters': self.coil_letters
        }


# Predefined configurations for common flow setups
FLOW_CONFIGS = {
    'two_syringes_1r_1m': FlowSetupConfig(
        name="Two Syringes, 1 Reaction Coil, 1 Mixer",
        description="Basic two-syringe setup with single reaction coil and mixer",
        num_vessels=2,
        num_coils=2,
        num_mixers=1,
        coil_letters=['a', 'x']
    ),
    'three_syringes_1r_1m': FlowSetupConfig(
        name="Three Syringes, 1 Reaction Coil, 1 Mixer", 
        description="Three-syringe setup with single reaction coil and mixer",
        num_vessels=3,
        num_coils=2,
        num_mixers=1,
        coil_letters=['a', 'x']
    ),
    'three_syringes_2r_2m': FlowSetupConfig(
        name="Three Syringes, 2 Reaction Coils, 2 Mixers",
        description="Advanced three-syringe setup with dual reaction coils and mixers",
        num_vessels=3,
        num_coils=4,
        num_mixers=2,
        coil_letters=['a', 'x', 'b', 'y']
    ),
    'flexible_setup': FlowSetupConfig(
        name="Flexible n-Syringes to Reaction Mix Vessel",
        description="Flexible setup allowing variable number of vessels",
        num_vessels=0,  # Variable - will be set dynamically
        num_coils=2,
        num_mixers=1,
        coil_letters=['a', 'x']
    )
}


def get_config(setup_type: str) -> FlowSetupConfig:
    """Get configuration by setup type"""
    if setup_type not in FLOW_CONFIGS:
        raise ValueError(f"Unknown setup type: {setup_type}. Available: {list(FLOW_CONFIGS.keys())}")
    return FLOW_CONFIGS[setup_type]


def list_available_configs() -> List[str]:
    """List all available configuration types"""
    return list(FLOW_CONFIGS.keys())


def add_custom_config(key: str, config: FlowSetupConfig) -> None:
    """Add a custom configuration"""
    FLOW_CONFIGS[key] = config
