"""
Phase2_ApparatusBuilder - Streamlined Tabbed Apparatus Designer

This module provides a clean, focused 3-tab interface for apparatus design
optimized for development purposes with Harvard pumps, vessels, T-mixers, 
and tubing.

Tab Structure:
    Tab 1: Active Components (Harvard Pumps)
    Tab 2: Passive Components (Vessels, T-Mixers) 
    Tab 3: Network Connections (Tubing and flow paths)

Key Features:
    - Clean tabbed interface for organized development
    - Focus on core components (Harvard pumps, vessels, T-mixers)
    - Integration with experimental metadata system
    - Extensible architecture for adding components later
    - Automatic A.add() code generation
    - Real-time network visualization

Main Component:
    tabbed_apparatus_designer: Clean 3-tab interface for apparatus building
"""

try:
    from .legacy.apparatus_gui import ApparatusBuilderGUI
except ImportError as e:
    # Handle missing dependencies gracefully - create fallback class
    class ApparatusBuilderGUI:
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print(f"Warning: Legacy ApparatusBuilderGUI not available: {e}")
            print("Note: Legacy GUI has been archived. Use TabbedApparatusDesigner v2 instead.")
        
        def display(self):
            print("Legacy ApparatusBuilderGUI not available.")
            print("Use create_tabbed_apparatus_designer_v2() for the modern interface.")
            
        def get_configured_pumps(self):
            return {}
            
        def get_apparatus(self):
            return None

# Import enhanced tabbed apparatus designer (v2 - modular)
try:
    from .tabbed_designer import (
        TabbedApparatusDesigner,
        ComponentRegistry,
        ApparatusComponent,
        ApparatusConnection,
        create_tabbed_apparatus_designer
    )
    
    _enhanced_designer_available = True
    _enhanced_import_error = None
    
except ImportError as e:
    _enhanced_designer_available = False
    _enhanced_import_error = str(e)
    
    # Try fallback to original tabbed designer
    try:
        from .tabbed_apparatus_designer import (
            TabbedApparatusDesigner,
            ComponentRegistry,
            ApparatusComponent,
            ApparatusConnection,
            create_tabbed_apparatus_designer
        )
        
        _enhanced_designer_available = True
        _enhanced_import_error = None
        print(f"Info: Using original tabbed designer as fallback")
        
    except ImportError as e2:
        _enhanced_designer_available = False
        _enhanced_import_error = str(e2)
        
        # Define fallback function
        def create_tabbed_apparatus_designer(experiment_manager=None):
            """Fallback function when tabbed designer imports fail."""
            raise ImportError(f"Cannot create tabbed apparatus designer: {_enhanced_import_error}")
        
        print(f"Warning: Enhanced tabbed apparatus designer not available: {e}")
        print(f"Warning: Original tabbed apparatus designer also not available: {e2}")

# Backward compatibility aliases
_tabbed_designer_available = _enhanced_designer_available
_tabbed_import_error = _enhanced_import_error

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

# New convenience function for tabbed designer
def launch_tabbed_designer(experiment_manager=None):
    """
    Launch the tabbed apparatus designer
    
    Args:
        experiment_manager: Optional ExperimentalMetadataManager instance
        
    Returns:
        TabbedApparatusDesigner instance
    """
    if not _tabbed_designer_available:
        raise ImportError(f"Tabbed designer not available: {_tabbed_import_error}")
    
    designer = create_tabbed_apparatus_designer(experiment_manager)
    designer.display()
    return designer

# Enhanced v2 designer function
def create_tabbed_apparatus_designer_v2(experiment_manager=None):
    """Create the enhanced modular v2 designer."""
    try:
        from .tabbed_designer import create_tabbed_apparatus_designer
        return create_tabbed_apparatus_designer(experiment_manager)
    except ImportError:
        # Fallback to original if v2 not available
        return create_tabbed_apparatus_designer(experiment_manager)

def get_designer_info():
    """Get information about available designers."""
    info = {
        'legacy_gui_available': True,  # ApparatusBuilderGUI is always available (with fallbacks)
        'tabbed_designer_available': _tabbed_designer_available,
        'enhanced_designer_available': _enhanced_designer_available,
        'tabbed_import_error': _tabbed_import_error,
        'enhanced_import_error': _enhanced_import_error
    }
    
    available_designers = ['ApparatusBuilderGUI (legacy)']
    if _enhanced_designer_available:
        available_designers.append('TabbedApparatusDesigner v2 (enhanced modular)')
    elif _tabbed_designer_available:
        available_designers.append('TabbedApparatusDesigner (original)')
    
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
    
    print(f"\n🔧 Tabbed Designer Status: {'✅ Available' if info['tabbed_designer_available'] else '❌ Not Available'}")
    if not info['tabbed_designer_available']:
        print(f"   Error: {info['tabbed_import_error']}")
    
    print(f"\n🚀 Quick Start Options:")
    print("  # Legacy GUI (with experiment manager):")
    print("  gui = launch_gui(experiment_manager)")
    
    if info['tabbed_designer_available']:
        print("  # Tabbed Designer (recommended for development):")
        print("  designer = launch_tabbed_designer(experiment_manager)")
    
    print("=" * 60)

# Update __all__ to include new functions
base_exports = ['ApparatusBuilderGUI', 'launch_gui', 'get_designer_info', 'print_designer_info']

if _tabbed_designer_available:
    tabbed_exports = [
        'TabbedApparatusDesigner',
        'ComponentRegistry', 
        'ApparatusComponent',
        'ApparatusConnection',
        'create_tabbed_apparatus_designer',
        'launch_tabbed_designer'
    ]
    __all__ = base_exports + tabbed_exports
else:
    __all__ = base_exports + [
        'create_tabbed_apparatus_designer',
        'launch_tabbed_designer'
    ]