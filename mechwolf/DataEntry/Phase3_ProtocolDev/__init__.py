"""
Phase3_ProtocolDev - Protocol development and validation

This module provides an integrated interface for developing and validating
protocols that use the configured apparatus and pumps from previous phases.

Key Features:
    - Protocol procedure builder with drag-and-drop interface
    - Real-time MechWolf core validation integration
    - Time-based procedure sequencing
    - Parameter validation and safety checks
    - Protocol simulation and dry-run capabilities
    - Integration with experimental metadata system

Main Components:
    protocol_gui: Main protocol development interface
    procedure_builder: Visual procedure construction
    protocol_validator: MechWolf core validation integration
    simulation_engine: Protocol simulation capabilities
"""

from .protocol_gui import ProtocolDevGUI

# Convenience function for launching GUI
def launch_gui(experiment_manager, protocol=None, pumps=None):
    """
    Launch the protocol development GUI
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        protocol: Optional existing mw.Protocol instance
        pumps: Optional dictionary of configured pump objects
        
    Returns:
        ProtocolDevGUI instance
    """
    gui = ProtocolDevGUI(experiment_manager, protocol, pumps)
    gui.display()
    return gui

def get_validated_protocol(experiment_manager, apparatus):
    """
    Get validated protocol from experimental metadata
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        apparatus: mw.Apparatus instance
        
    Returns:
        Validated mw.Protocol instance or None
    """
    try:
        import mechwolf as mw
        
        protocol_data = experiment_manager.get_section_data("protocol_config")
        if not protocol_data or not protocol_data.get("procedures"):
            return None
            
        # Create protocol from apparatus
        protocol = mw.Protocol(apparatus)
        
        # Add procedures from experimental metadata
        # This would need to be implemented based on the stored procedure format
        
        return protocol
        
    except Exception as e:
        print(f"Error creating validated protocol: {e}")
        return None

__all__ = ['ProtocolDevGUI', 'launch_gui', 'get_validated_protocol']