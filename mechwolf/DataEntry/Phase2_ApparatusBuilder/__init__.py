"""
Phase2_ApparatusBuilder - Integrated apparatus and pump configuration

This module provides a unified interface for configuring both pumps and apparatus
components, eliminating the need for separate pump code generation steps.

Key Innovation:
    - Integrated pump configuration with apparatus building
    - Auto-generation of pump initialization code
    - Visual apparatus building with connection management
    - Real-time validation and error checking
    - Seamless integration with experimental metadata

Main Components:
    apparatus_gui: Main integrated interface (legacy)
    pump_configurator: Pump configuration and code generation
    component_configurator: Component selection and configuration  
    connection_builder: Visual connection management
    apparatus_validator: Real-time validation
    apparatus_visualizer: Network diagram visualization

NEW Network-Based Designer:
    network_apparatus_designer: Basic visual network designer
    enhanced_network_designer: Advanced network designer with full features
    - Visual drag-and-drop apparatus building
    - Component library with all MechWolf components
    - Network validation and analysis tools
    - Automatic A.add() code generation
    - Save/load apparatus configurations
"""

try:
    from .apparatus_gui import ApparatusBuilderGUI
except ImportError as e:
    # Handle missing dependencies gracefully
    class ApparatusBuilderGUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"Warning: ApparatusBuilderGUI dependencies not available: {e}")
        
        def display(self):
            print("ApparatusBuilderGUI not available - install required dependencies (ipywidgets, etc.)")
            
        def get_configured_pumps(self):
            return {}
            
        def get_apparatus(self):
            return None
            
    print(f"Warning: ApparatusBuilderGUI not fully available: {e}")

# Import new network-based designers
try:
    from .network_apparatus_designer import (
        NetworkApparatusDesigner,
        ComponentLibrary,
        NetworkNode,
        NetworkConnection,
        ApparatusNetwork,
        create_network_apparatus_designer
    )
    
    from .enhanced_network_designer import (
        EnhancedNetworkApparatusDesigner,
        EnhancedPropertiesManager,
        ConfigurationManager,
        create_enhanced_network_apparatus_designer
    )
    
    _network_designer_available = True
    _network_import_error = None
    
except ImportError as e:
    _network_designer_available = False
    _network_import_error = str(e)
    
    # Define fallback functions
    def create_network_apparatus_designer():
        """Fallback function when network designer imports fail."""
        raise ImportError(f"Cannot create network apparatus designer: {_network_import_error}")
    
    def create_enhanced_network_apparatus_designer():
        """Fallback function when enhanced network designer imports fail."""
        raise ImportError(f"Cannot create enhanced network apparatus designer: {_network_import_error}")
    
    print(f"Warning: Network designers not available: {e}")

# Convenience function for launching GUI
def launch_gui(experiment_manager):
    """
    Launch the integrated apparatus and pump builder GUI
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        ApparatusBuilderGUI instance
    """
    gui = ApparatusBuilderGUI(experiment_manager)
    gui.display()
    return gui

# New convenience functions for network designers
def launch_network_designer():
    """
    Launch the basic network apparatus designer
    
    Returns:
        NetworkApparatusDesigner instance
    """
    if not _network_designer_available:
        raise ImportError(f"Network designer not available: {_network_import_error}")
    
    designer = create_network_apparatus_designer()
    designer.display()
    return designer

def launch_enhanced_designer():
    """
    Launch the enhanced network apparatus designer
    
    Returns:
        EnhancedNetworkApparatusDesigner instance
    """
    if not _network_designer_available:
        raise ImportError(f"Enhanced network designer not available: {_network_import_error}")
    
    designer = create_enhanced_network_apparatus_designer()
    designer.display()
    return designer

def get_designer_info():
    """Get information about available designers."""
    info = {
        'legacy_gui_available': True,  # ApparatusBuilderGUI is always available (with fallbacks)
        'network_designer_available': _network_designer_available,
        'enhanced_designer_available': _network_designer_available,
        'network_import_error': _network_import_error
    }
    
    available_designers = ['ApparatusBuilderGUI (legacy)']
    if _network_designer_available:
        available_designers.extend([
            'NetworkApparatusDesigner (basic)',
            'EnhancedNetworkApparatusDesigner (advanced)'
        ])
    
    info['available_designers'] = available_designers
    return info

def print_designer_info():
    """Print information about available apparatus designers."""
    info = get_designer_info()
    
    print("=" * 60)
    print("MechWolf Phase 2 Apparatus Builder - Available Designers")
    print("=" * 60)
    
    print("📋 Available Designers:")
    for i, designer in enumerate(info['available_designers'], 1):
        print(f"  {i}. {designer}")
    
    print(f"\n🔧 Network Designer Status: {'✅ Available' if info['network_designer_available'] else '❌ Not Available'}")
    if not info['network_designer_available']:
        print(f"   Error: {info['network_import_error']}")
    
    print(f"\n🚀 Quick Start Options:")
    print("  # Legacy GUI (with experiment manager):")
    print("  gui = launch_gui(experiment_manager)")
    
    if info['network_designer_available']:
        print("  # Basic Network Designer:")
        print("  designer = launch_network_designer()")
        print("  # Enhanced Network Designer:")
        print("  enhanced = launch_enhanced_designer()")
    
    print("=" * 60)

# Update __all__ to include new functions
base_exports = ['ApparatusBuilderGUI', 'launch_gui', 'get_designer_info', 'print_designer_info']

if _network_designer_available:
    network_exports = [
        'NetworkApparatusDesigner',
        'EnhancedNetworkApparatusDesigner', 
        'ComponentLibrary',
        'ConfigurationManager',
        'NetworkNode',
        'NetworkConnection',
        'ApparatusNetwork',
        'EnhancedPropertiesManager',
        'create_network_apparatus_designer',
        'create_enhanced_network_apparatus_designer',
        'launch_network_designer',
        'launch_enhanced_designer'
    ]
    __all__ = base_exports + network_exports
else:
    __all__ = base_exports + [
        'create_network_apparatus_designer',
        'create_enhanced_network_apparatus_designer',
        'launch_network_designer',
        'launch_enhanced_designer'
    ]