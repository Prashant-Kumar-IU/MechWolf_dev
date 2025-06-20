"""
Component Validator - Input validation and error checking for components

This module provides comprehensive validation for component configurations
including serial ports, units, naming conventions, and component-specific rules.
"""
import re
import os
import glob
from typing import Dict, Any, List, Optional, Set
from pathlib import Path


class ComponentValidator:
    """Comprehensive validation for component configurations"""
    
    def __init__(self):
        # Cache for available serial ports
        self._available_ports: Optional[List[str]] = None
        
        # Valid unit patterns
        self.unit_patterns = {
            'volume': r'^\d+(\.\d+)?\s*(mL|ml|ML|Ml|L|l)$',
            'length': r'^\d+(\.\d+)?\s*(ft|in|cm|mm|m)$',
            'flow_rate': r'^\d+(\.\d+)?\s*(mL/min|ml/min|ML/min|L/min|l/min)$',
            'diameter': r'^\d+(\.\d+)?\s*(mm|cm|in|")$',
            'frequency': r'^\d+(\.\d+)?\s*(Hz|hz|HZ|kHz|khz|KHZ)$',
            'temperature': r'^-?\d+(\.\d+)?\s*(°C|C|degC|°F|F|degF|K)$',
            'pressure': r'^\d+(\.\d+)?\s*(bar|Bar|BAR|psi|PSI|Pa|pa|kPa|kpa|KPA|atm|ATM)$'
        }
        
        # Common validation errors and suggestions
        self.error_suggestions = {
            'invalid_name': "Name must start with a letter or underscore, followed by letters, numbers, or underscores",
            'invalid_serial_port': "Serial port should start with /dev/ (Linux/Mac) or COM (Windows)",
            'invalid_volume': "Volume must include units like '3 mL', '5.5 L'",
            'invalid_flow_rate': "Flow rate must include units like '2.5 mL/min', '10 L/min'",
            'invalid_length': "Length must include units like '1 ft', '12 cm', '0.5 m'",
            'duplicate_name': "Component name is already in use",
            'missing_required': "This field is required",
            'invalid_port_number': "Port number must be a positive integer",
            'duplicate_port': "Port number is already assigned to another component"
        }
    
    def validate_component(self, component_data: Dict[str, Any], existing_components: Dict[str, Dict[str, Any]], editing_id: Optional[str] = None) -> List[str]:
        """
        Comprehensive validation for any component type
        
        Args:
            component_data: The component configuration to validate
            existing_components: Dictionary of existing components to check for conflicts
            editing_id: ID of component being edited (to exclude from conflict checks)
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Basic validation
        errors.extend(self._validate_basic_fields(component_data))
        
        # Name uniqueness check
        errors.extend(self._validate_name_uniqueness(component_data, existing_components, editing_id))
        
        # Component-specific validation
        component_type = component_data.get('type', '')
        category = component_data.get('category', '')
        
        if category in ['active_contrib', 'active_stdlib']:
            errors.extend(self._validate_active_component(component_data))
        elif category == 'passive':
            errors.extend(self._validate_passive_component(component_data))
        
        return errors
    
    def _validate_basic_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate basic required fields"""
        errors = []
        
        # Name validation
        name = data.get('name', '').strip()
        if not name:
            errors.append("Name is required")
        elif not self._is_valid_python_identifier(name):
            errors.append(self.error_suggestions['invalid_name'])
        
        # Type validation
        if not data.get('type'):
            errors.append("Component type is required")
        
        return errors
    
    def _validate_name_uniqueness(self, data: Dict[str, Any], existing_components: Dict[str, Dict[str, Any]], editing_id: Optional[str] = None) -> List[str]:
        """Check for name conflicts with existing components"""
        errors = []
        
        name = data.get('name', '').strip()
        if not name:
            return errors  # Skip if no name (handled by basic validation)
        
        for comp_id, comp_data in existing_components.items():
            if comp_id != editing_id and comp_data.get('name') == name:
                errors.append(f"Name '{name}' is already used by another {comp_data.get('type', 'component')}")
                break
        
        return errors
    
    def _validate_active_component(self, data: Dict[str, Any]) -> List[str]:
        """Validate active component specific fields"""
        errors = []
        component_type = data.get('type', '')
        
        # Serial port validation (most active components need this)
        if 'serial_port' in data:
            errors.extend(self._validate_serial_port(data['serial_port']))
        
        # Component-specific validation
        if 'Pump' in component_type:
            errors.extend(self._validate_pump_fields(data))
        elif 'Valve' in component_type:
            errors.extend(self._validate_valve_fields(data))
        elif 'Sensor' in component_type:
            errors.extend(self._validate_sensor_fields(data))
        
        return errors
    
    def _validate_passive_component(self, data: Dict[str, Any]) -> List[str]:
        """Validate passive component specific fields"""
        errors = []
        component_type = data.get('type', '')
        
        if component_type == 'Vessel':
            errors.extend(self._validate_vessel_fields(data))
        elif component_type == 'Tube':
            errors.extend(self._validate_tube_fields(data))
        elif 'Mixer' in component_type:
            errors.extend(self._validate_mixer_fields(data))
        
        return errors
    
    def _validate_pump_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate pump-specific fields"""
        errors = []
        component_type = data.get('type', '')
        
        # Harvard Syringe Pump validation
        if component_type == 'HarvardSyringePump':
            if 'syringe_volume' in data:
                if not self._validate_unit(data['syringe_volume'], 'volume'):
                    errors.append("Syringe volume must include units (e.g., '3 mL', '5 L')")
            
            if 'syringe_diameter' in data:
                if not self._validate_unit(data['syringe_diameter'], 'diameter'):
                    errors.append("Syringe diameter must include units (e.g., '10 mm', '0.5 in')")
        
        # Varian Pump validation
        elif 'Varian' in component_type:
            if 'max_rate' in data and data['max_rate']:
                if not self._validate_unit(data['max_rate'], 'flow_rate'):
                    errors.append("Max rate must include units (e.g., '25 mL/min')")
        
        # FreeStep Pump validation
        elif component_type == 'FreeStepPump':
            required_fields = ['mcu_id', 'motor_id', 'syringe_volume', 'syringe_diameter']
            for field in required_fields:
                if field in data and not data[field]:
                    errors.append(f"{field.replace('_', ' ').title()} is required for FreeStep pumps")
            
            if 'syringe_volume' in data and data['syringe_volume']:
                if not self._validate_unit(data['syringe_volume'], 'volume'):
                    errors.append("Syringe volume must include units")
                    
            if 'syringe_diameter' in data and data['syringe_diameter']:
                if not self._validate_unit(data['syringe_diameter'], 'diameter'):
                    errors.append("Syringe diameter must include units")
        
        return errors
    
    def _validate_valve_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate valve-specific fields"""
        errors = []
        
        # Mapping validation
        mapping = data.get('mapping', {})
        if not mapping:
            errors.append("At least one port mapping is required")
        else:
            # Check for duplicate ports
            ports = list(mapping.values())
            if len(ports) != len(set(ports)):
                errors.append("Port numbers must be unique")
            
            # Check port number validity
            for vessel, port in mapping.items():
                if not isinstance(port, int) or port < 1:
                    errors.append(f"Port number for '{vessel}' must be a positive integer")
                elif port > 16:  # Reasonable upper limit for valve ports
                    errors.append(f"Port number {port} for '{vessel}' seems unusually high (max recommended: 16)")
        
        return errors
    
    def _validate_sensor_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate sensor-specific fields"""
        errors = []
        
        # Unit validation
        if 'unit' in data and data['unit']:
            unit = data['unit'].strip()
            # Common sensor units
            common_units = ['pH', '°C', 'C', 'bar', 'psi', 'Pa', 'V', 'A', 'mA', 'Hz', '%', 'ppm', 'mg/L']
            if unit not in common_units and not any(pattern for pattern in self.unit_patterns.values() if re.match(pattern, f"1 {unit}")):
                # This is just a warning, not an error
                pass  # Could add warning system later
        
        return errors
    
    def _validate_vessel_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate vessel-specific fields"""
        errors = []
        
        # Description is optional but helpful
        if 'description' in data and len(data['description']) > 200:
            errors.append("Description should be shorter than 200 characters")
        
        return errors
    
    def _validate_tube_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate tube-specific fields"""
        errors = []
        
        # Length validation
        if 'length' in data:
            if not data['length']:
                errors.append("Length is required")
            elif not self._validate_unit(data['length'], 'length'):
                errors.append("Length must include units (e.g., '1 ft', '12 cm')")
        
        # Diameter validation (for custom tubes)
        preset = data.get('preset', 'custom')
        if preset == 'custom':
            if 'ID' in data and not data['ID']:
                errors.append("Inner diameter is required for custom tubes")
            if 'OD' in data and not data['OD']:
                errors.append("Outer diameter is required for custom tubes")
            
            # Validate diameter formats
            if 'ID' in data and data['ID'] and not self._validate_diameter_format(data['ID']):
                errors.append("Inner diameter format invalid (e.g., '1/16 in', '0.5 mm')")
            if 'OD' in data and data['OD'] and not self._validate_diameter_format(data['OD']):
                errors.append("Outer diameter format invalid (e.g., '1/8 in', '2.0 mm')")
        
        return errors
    
    def _validate_mixer_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate mixer-specific fields"""
        errors = []
        
        # Mixers are generally simple, just basic validation
        # Could add specific validation for different mixer types in the future
        
        return errors
    
    def _validate_serial_port(self, serial_port: str) -> List[str]:
        """Validate serial port format and availability"""
        errors = []
        
        if not serial_port:
            return errors  # Skip if empty (might be optional)
        
        # Format validation
        if not (serial_port.startswith('/dev/') or serial_port.startswith('COM') or serial_port.startswith('com')):
            errors.append("Serial port should start with /dev/ (Linux/Mac) or COM (Windows)")
            return errors
        
        # Check if port exists (Linux/Mac only for now)
        if serial_port.startswith('/dev/'):
            if not os.path.exists(serial_port):
                # Try to find similar ports as suggestions
                base_path = os.path.dirname(serial_port)
                if os.path.exists(base_path):
                    similar_ports = glob.glob(f"{base_path}/*")
                    if similar_ports:
                        errors.append(f"Serial port {serial_port} not found. Available ports: {', '.join(similar_ports[:5])}")
                    else:
                        errors.append(f"Serial port {serial_port} not found")
                else:
                    errors.append(f"Serial port {serial_port} not found")
        
        return errors
    
    def _validate_unit(self, value: str, unit_type: str) -> bool:
        """Validate that a value matches the expected unit pattern"""
        if not value or unit_type not in self.unit_patterns:
            return False
        
        pattern = self.unit_patterns[unit_type]
        return bool(re.match(pattern, value.strip()))
    
    def _validate_diameter_format(self, diameter: str) -> bool:
        """Validate diameter format (handles fractions and decimals)"""
        if not diameter:
            return False
        
        # Handle fractional inches (e.g., "1/16 in")
        fraction_pattern = r'^\d+/\d+\s*(in|")$'
        if re.match(fraction_pattern, diameter.strip()):
            return True
        
        # Handle decimal measurements
        decimal_pattern = r'^\d+(\.\d+)?\s*(mm|cm|in|")$'
        if re.match(decimal_pattern, diameter.strip()):
            return True
        
        return False
    
    def _is_valid_python_identifier(self, name: str) -> bool:
        """Check if name is a valid Python identifier"""
        if not name:
            return False
        
        # Must start with letter or underscore
        if not (name[0].isalpha() or name[0] == '_'):
            return False
        
        # Rest can be letters, numbers, or underscores
        for char in name[1:]:
            if not (char.isalnum() or char == '_'):
                return False
        
        # Check against Python keywords
        python_keywords = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class', 
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 
            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 
            'while', 'with', 'yield'
        }
        
        if name in python_keywords:
            return False
        
        return True
    
    def get_available_serial_ports(self) -> List[str]:
        """Get list of available serial ports on the system"""
        if self._available_ports is None:
            self._available_ports = self._discover_serial_ports()
        
        return self._available_ports
    
    def _discover_serial_ports(self) -> List[str]:
        """Discover available serial ports on the system"""
        ports = []
        
        try:
            # Linux/Mac serial ports
            dev_paths = [
                '/dev/ttyUSB*',
                '/dev/ttyACM*', 
                '/dev/ttyS*',
                '/dev/cu.*',  # Mac
                '/dev/serial/by-id/*'  # Linux by-id
            ]
            
            for pattern in dev_paths:
                ports.extend(glob.glob(pattern))
            
            # Windows COM ports (basic check)
            for i in range(1, 21):  # COM1-COM20
                com_port = f"COM{i}"
                # Would need pyserial to properly check Windows ports
                # For now, just add common ones
                if i <= 10:
                    ports.append(com_port)
                    
        except Exception:
            pass  # Ignore errors in port discovery
        
        return sorted(list(set(ports)))
    
    def suggest_serial_port_format(self, partial_port: str) -> List[str]:
        """Suggest proper serial port format based on partial input"""
        suggestions = []
        
        if not partial_port:
            suggestions.extend([
                "/dev/serial/by-id/usb-FTDI_...",
                "/dev/ttyUSB0",
                "/dev/ttyACM0", 
                "COM1",
                "COM3"
            ])
        elif partial_port.startswith('/dev/'):
            available = self.get_available_serial_ports()
            matching = [port for port in available if port.startswith(partial_port)]
            suggestions.extend(matching[:5])
        elif partial_port.upper().startswith('COM'):
            for i in range(1, 11):
                suggestions.append(f"COM{i}")
        
        return suggestions
    
    def validate_connection_compatibility(self, from_component: Dict[str, Any], to_component: Dict[str, Any]) -> List[str]:
        """Validate that two components can be connected"""
        errors = []
        
        # Basic compatibility checks
        from_type = from_component.get('type', '')
        to_type = to_component.get('type', '')
        
        # Example rules (can be expanded)
        
        # Vessels should generally not connect directly to vessels
        if from_type == 'Vessel' and to_type == 'Vessel':
            errors.append("Vessels should not connect directly to other vessels without active components")
        
        # Pumps should have input from vessels/mixers and output to vessels/mixers
        if 'Pump' in from_type and 'Pump' in to_type:
            errors.append("Pumps should not connect directly to other pumps")
        
        # More complex validation rules can be added here
        
        return errors