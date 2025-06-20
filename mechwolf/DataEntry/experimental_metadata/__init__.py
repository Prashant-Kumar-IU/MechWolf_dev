"""
Experimental Metadata - Unified JSON Management for MechWolf Experiments

This package provides a comprehensive system for managing all experimental data
in a single, structured JSON file that serves as complete metadata for each
lab experiment. The data is machine-readable for LLM analysis and future
data mining.

Main Components:
    ExperimentalMetadataManager: Central coordinator for all experiment data
    ChemistryDataManager: Reagents, stoichiometry, and chemical information
    ApparatusDataManager: Component configurations and connections
    ProtocolDataManager: Procedures, timing, and execution parameters
    AnalysisDataManager: TLC, NMR, yields, and other analytical data

Usage:
    from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
    
    # Create or load experiment metadata
    experiment = ExperimentalMetadataManager("birch_reduction_experiment.json")
    
    # Work with individual sections
    experiment.chemistry.update_reagents(reagent_data)
    experiment.apparatus.configure_components(components)
    experiment.protocol.add_procedures(procedures)
    experiment.analysis.add_tlc_data(tlc_results)  # Future
"""

from .experimental_metadata_manager import ExperimentalMetadataManager
from .chemistry_manager import ChemistryDataManager
from .apparatus_manager import ApparatusDataManager
from .protocol_manager import ProtocolDataManager
from .analysis_manager import AnalysisDataManager
from .schema_definitions import UNIFIED_SCHEMA, validate_section
from .migration_utilities import migrate_legacy_files, convert_reagent_json, convert_apparatus_json

__version__ = "3.0.0"
__author__ = "MechWolf Experimental Metadata Team"

# Main entry points
def create_experiment_metadata(experiment_file: str, experiment_name: str = None) -> ExperimentalMetadataManager:
    """Create a new experimental metadata file"""
    return ExperimentalMetadataManager(experiment_file, experiment_name)

def load_experiment_metadata(experiment_file: str) -> ExperimentalMetadataManager:
    """Load existing experimental metadata"""
    return ExperimentalMetadataManager(experiment_file)

# Export main classes
__all__ = [
    'ExperimentalMetadataManager',
    'ChemistryDataManager', 
    'ApparatusDataManager',
    'ProtocolDataManager',
    'AnalysisDataManager',
    'create_experiment_metadata',
    'load_experiment_metadata',
    'migrate_legacy_files',
    'UNIFIED_SCHEMA',
    'validate_section'
]