"""
Component definitions and specifications.

Contains the static definitions for all supported component types.
"""

# Known component mappings from contrib directory analysis
COMPONENT_DEFINITIONS = {
    'active': {
        'HarvardSyringePump': {
            'module': 'harvardpump',
            'category': 'active',
            'display_name': 'Harvard Syringe Pump',
            'icon': '💉',
            'default_properties': {
                'syringe_volume': '3 mL',
                'syringe_diameter': '10 mm',
                'serial_port': 'COM1'
            },
            'required_properties': ['syringe_volume', 'syringe_diameter', 'serial_port']
        },
        'VarianPump': {
            'module': 'varian',
            'category': 'active',
            'display_name': 'Varian HPLC Pump',
            'icon': '⚙️',
            'default_properties': {
                'serial_port': '/dev/ttyUSB0',
                'max_rate': '5 ml/min'
            },
            'required_properties': ['serial_port', 'max_rate']
        },
        'ViciPump': {
            'module': 'vicipump',
            'category': 'active',
            'display_name': 'Vici M50 Pump',
            'icon': '🔧',
            'default_properties': {
                'serial_port': '/dev/ttyUSB0',
                'volume_per_rev': '1 mL'
            },
            'required_properties': ['serial_port', 'volume_per_rev']
        },
        'ViciValve': {
            'module': 'vici',
            'category': 'active',
            'display_name': 'VICI Valve',
            'icon': '🔀',
            'default_properties': {
                'serial_port': '/dev/ttyUSB0'
            },
            'required_properties': ['serial_port', 'mapping']
        }
    },
    'passive': {
        'Vessel': {
            'class_name': 'Vessel',
            'import_path': 'mechwolf',
            'display_name': 'Reagent Vessel',
            'icon': '🧪',
            'default_properties': {},
            'required_properties': [],
            'property_types': {}
        },
        'TMixer': {
            'class_name': 'TMixer',
            'import_path': 'mechwolf',
            'display_name': 'T-Mixer',
            'icon': '🔀',
            'default_properties': {},
            'required_properties': [],
            'property_types': {}
        },
        'Tube': {
            'class_name': 'Tube',
            'import_path': 'mechwolf',
            'display_name': 'Tubing',
            'icon': '🔗',
            'default_properties': {
                'length': '1 ft',
                'ID': '1/16 in',
                'OD': '1/8 in',
                'material': 'PFA'
            },
            'required_properties': ['length', 'ID', 'OD', 'material'],
            'property_types': {
                'length': 'text',
                'ID': 'text',
                'OD': 'text',
                'material': 'text'
            }
        }
    }
}

# Tube specifications for connections
TUBE_TYPES = {
    'fat_tube': {
        'ID': '1/16 in',
        'OD': '1/8 in', 
        'material': 'PFA',
        'description': 'Standard fat tube'
    },
    'thin_tube': {
        'ID': '0.030 in',
        'OD': '1/16 in',
        'material': 'PFA',
        'description': 'Thin precision tube'
    },
    'thinner_tube': {
        'ID': '0.020 in',
        'OD': '1/16 in',
        'material': 'PFA',
        'description': 'Ultra-thin tube'
    },
    'valve_tube': {
        'ID': '0.020 in',
        'OD': '1/16 in',
        'material': 'PFA',
        'description': 'Valve connection tube'
    }
}