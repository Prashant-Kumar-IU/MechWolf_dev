"""
Dynamic component discovery system.

Discovers components from contrib directory and provides fallback mechanisms.
"""

try:
    from ..config.component_definitions import COMPONENT_DEFINITIONS
except ImportError:
    # Fallback for direct testing
    from config.component_definitions import COMPONENT_DEFINITIONS


def discover_components():
    """Dynamically discover components from contrib directory."""
    components = {
        'active': {},
        'passive': {}
    }
    
    try:
        # Try to discover components dynamically
        try:
            from ..config.settings import DEFAULT_SETTINGS
        except ImportError:
            from config.settings import DEFAULT_SETTINGS
        contrib_path = DEFAULT_SETTINGS['contrib_path']
        
        # Add known components to registry
        for class_name, info in COMPONENT_DEFINITIONS['active'].items():
            component_info = {
                'class_name': class_name,
                'import_path': f'mechwolf.components.contrib.{info["module"]}',
                'display_name': info['display_name'],
                'icon': info['icon'],
                'default_properties': info['default_properties'],
                'required_properties': info['required_properties'],
                'property_types': {prop: 'text' for prop in info['required_properties']}
            }
            components[info['category']][class_name] = component_info
            
    except Exception as e:
        print(f"Warning: Could not discover components dynamically: {e}")
        # Fallback to hardcoded Harvard pump
        components['active']['HarvardSyringePump'] = {
            'class_name': 'HarvardSyringePump',
            'import_path': 'mechwolf.components.contrib.harvardpump',
            'display_name': 'Harvard Syringe Pump',
            'icon': '💉',
            'default_properties': {
                'syringe_volume': '3 mL',
                'syringe_diameter': '10 mm',
                'serial_port': 'COM1'
            },
            'required_properties': ['syringe_volume', 'syringe_diameter', 'serial_port'],
            'property_types': {
                'syringe_volume': 'text',
                'syringe_diameter': 'text', 
                'serial_port': 'text'
            }
        }
    
    # Add passive components (stdlib components)
    components['passive'].update(COMPONENT_DEFINITIONS['passive'])
    
    return components