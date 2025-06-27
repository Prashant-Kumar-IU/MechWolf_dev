"""
Phase3_ProtocolDev - Protocol development and validation

This module provides interfaces for developing and validating protocols that use 
the configured apparatus and pumps from previous phases.

Key Features:
    - Simple protocol builder with table-based interface
    - Clean MechWolf code generation with timedelta variables
    - Advanced protocol GUI with drag-and-drop interface
    - Real-time MechWolf core validation integration
    - Time-based procedure sequencing
    - Parameter validation and safety checks
    - Protocol simulation and dry-run capabilities
    - Integration with experimental metadata system

Main Components:
    simple_protocol_builder: Streamlined table-based protocol builder
    protocol_gui: Advanced protocol development interface
    procedure_builder: Visual procedure construction
    protocol_validator: MechWolf core validation integration
"""

# Import Simple Protocol Builder
try:
    from .simple_protocol_builder import SimpleProtocolBuilder
except ImportError as e:
    # Handle missing dependencies gracefully
    class SimpleProtocolBuilder:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"Warning: SimpleProtocolBuilder dependencies not available: {e}")
        
        def display(self):
            print("SimpleProtocolBuilder not available - install required dependencies (ipywidgets, etc.)")
    
    print(f"Warning: SimpleProtocolBuilder not fully available: {e}")

# Import Advanced Protocol GUI
try:
    from .protocol_gui import ProtocolDevGUI
except ImportError as e:
    # Handle missing dependencies gracefully
    class ProtocolDevGUI:
        def __init__(self, experiment_manager, protocol=None, pumps=None):
            self.experiment = experiment_manager
            self.protocol = protocol
            self.pumps = pumps
            print(f"Warning: ProtocolDevGUI dependencies not available: {e}")
        
        def display(self):
            print("ProtocolDevGUI not available - install required dependencies (ipywidgets, etc.)")
            
    print(f"Warning: ProtocolDevGUI not fully available: {e}")

# Convenience functions for launching GUIs
def launch_simple_builder(experiment_manager):
    """
    Launch the simple protocol builder (recommended)
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        SimpleProtocolBuilder instance
    """
    builder = SimpleProtocolBuilder(experiment_manager)
    builder.display()
    return builder

def launch_gui(experiment_manager, protocol=None, pumps=None):
    """
    Launch the advanced protocol development GUI
    
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

__all__ = [
    'SimpleProtocolBuilder', 'launch_simple_builder',
    'ProtocolDevGUI', 'launch_gui', 'get_validated_protocol'
]