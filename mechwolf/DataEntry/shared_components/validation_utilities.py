"""
Validation Utilities

Common validation functions shared across all phases of the DataEntry system.
"""

import re
from typing import Any, Dict, List, Optional, Union
import json


class ValidationUtils:
    """Common validation utilities for the DataEntry system"""
    
    # Common regex patterns
    PATTERNS = {
        'time': r'^\d+\.?\d*\s*(s|sec|min|h|hr)$',
        'flow_rate': r'^\d+\.?\d*\s*(ml|μl|ul|nl)/min$',
        'temperature': r'^-?\d+\.?\d*\s*°?[CFK]?$',
        'pressure': r'^\d+\.?\d*\s*(psi|bar|atm|pa|kpa|mpa)$',
        'volume': r'^\d+\.?\d*\s*(ml|μl|ul|nl|l)$',
        'mass': r'^\d+\.?\d*\s*(mg|g|kg|μg)$',
        'concentration': r'^\d+\.?\d*\s*(m|mm|μm|nm)$',
        'inchi': r'^InChI=1S?/',
        'inchi_key': r'^[A-Z]{14}-[A-Z]{10}-[A-Z]$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    }
    
    @classmethod
    def validate_field(cls, value: Any, field_type: str, required: bool = True) -> Dict[str, Any]:
        """
        Validate a field value
        
        Args:
            value: Value to validate
            field_type: Type of validation to perform
            required: Whether field is required
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'normalized_value': value
        }
        
        # Check required fields
        if required and (value is None or value == ''):
            result['valid'] = False
            result['errors'].append(f"{field_type.replace('_', ' ').title()} is required")
            return result
        
        # Skip validation for optional empty fields
        if not required and (value is None or value == ''):
            return result
        
        # Convert to string for pattern matching
        str_value = str(value).strip()
        
        # Validate based on field type
        if field_type in cls.PATTERNS:
            if not re.match(cls.PATTERNS[field_type], str_value, re.IGNORECASE):
                result['valid'] = False
                result['errors'].append(f"Invalid {field_type.replace('_', ' ')} format")
        
        # Type-specific validation
        if field_type == 'flow_rate':
            parsed_rate = cls.parse_flow_rate(str_value)
            if parsed_rate is not None:
                result['normalized_value'] = parsed_rate
                if parsed_rate > 100:  # mL/min
                    result['warnings'].append("Very high flow rate - verify this is correct")
                elif parsed_rate < 0.001:  # mL/min
                    result['warnings'].append("Very low flow rate - verify this is correct")
        
        elif field_type == 'temperature':
            parsed_temp = cls.parse_temperature(str_value)
            if parsed_temp is not None:
                result['normalized_value'] = parsed_temp
                if parsed_temp > 200:  # °C
                    result['warnings'].append("High temperature - ensure safety measures")
                elif parsed_temp < -50:  # °C
                    result['warnings'].append("Very low temperature - verify cooling capability")
        
        elif field_type == 'time':
            parsed_time = cls.parse_time_to_seconds(str_value)
            if parsed_time is not None:
                result['normalized_value'] = parsed_time
                if parsed_time > 86400:  # > 24 hours
                    result['warnings'].append("Very long duration - consider breaking into steps")
        
        elif field_type == 'pressure':
            parsed_pressure = cls.parse_pressure(str_value)
            if parsed_pressure is not None:
                result['normalized_value'] = parsed_pressure
                if parsed_pressure > 100:  # psi
                    result['warnings'].append("High pressure - ensure system can handle safely")
        
        return result
    
    @classmethod
    def validate_component_name(cls, name: str) -> Dict[str, Any]:
        """Validate component name"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        if not name or not name.strip():
            result['valid'] = False
            result['errors'].append("Component name is required")
            return result
        
        name = name.strip()
        
        # Length checks
        if len(name) < 2:
            result['valid'] = False
            result['errors'].append("Component name must be at least 2 characters")
        elif len(name) > 50:
            result['valid'] = False
            result['errors'].append("Component name must be less than 50 characters")
        
        # Character validation
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', name):
            result['valid'] = False
            result['errors'].append("Component name contains invalid characters")
        
        # Naming convention suggestions
        if ' ' in name and '_' in name:
            result['warnings'].append("Consider using either spaces or underscores, not both")
        
        if name.lower() in ['test', 'temp', 'tmp']:
            result['warnings'].append("Consider using a more descriptive name")
        
        return result
    
    @classmethod
    def validate_json_structure(cls, data: Dict[str, Any], 
                              required_keys: List[str] = None) -> Dict[str, Any]:
        """Validate JSON structure"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        if not isinstance(data, dict):
            result['valid'] = False
            result['errors'].append("Data must be a dictionary")
            return result
        
        # Check required keys
        if required_keys:
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                result['valid'] = False
                result['errors'].append(f"Missing required keys: {', '.join(missing_keys)}")
        
        # Check for empty values in important fields
        empty_fields = [key for key, value in data.items() 
                       if value is None or value == '']
        if empty_fields:
            result['warnings'].append(f"Empty fields found: {', '.join(empty_fields)}")
        
        return result
    
    @classmethod
    def validate_experimental_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate experimental metadata structure"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check for required top-level sections
        required_sections = ['mechwolf_experiment', 'chemistry', 'apparatus_config']
        section_results = cls.validate_json_structure(metadata, required_sections)
        
        if not section_results['valid']:
            result['valid'] = False
            result['errors'].extend(section_results['errors'])
        
        result['warnings'].extend(section_results['warnings'])
        
        # Validate experiment metadata
        if 'mechwolf_experiment' in metadata:
            exp_meta = metadata['mechwolf_experiment']
            if not exp_meta.get('experiment_name'):
                result['warnings'].append("Experiment name is empty")
            
            if not exp_meta.get('experiment_id'):
                result['warnings'].append("Experiment ID is missing")
        
        return result
    
    @classmethod
    def parse_flow_rate(cls, rate_str: str) -> Optional[float]:
        """Parse flow rate string to mL/min"""
        try:
            rate_str = rate_str.strip().lower()
            match = re.match(r'^(\d+\.?\d*)\s*(ml|μl|ul|nl)/min$', rate_str)
            if not match:
                return None
            
            value = float(match.group(1))
            unit = match.group(2)
            
            # Convert to mL/min
            if unit == 'ml':
                return value
            elif unit in ['μl', 'ul']:
                return value / 1000.0
            elif unit == 'nl':
                return value / 1000000.0
        except:
            pass
        return None
    
    @classmethod
    def parse_temperature(cls, temp_str: str) -> Optional[float]:
        """Parse temperature string to Celsius"""
        try:
            temp_str = temp_str.strip().lower()
            match = re.match(r'^(-?\d+\.?\d*)\s*°?([cfk])?$', temp_str)
            if not match:
                return None
            
            value = float(match.group(1))
            unit = match.group(2) or 'c'
            
            # Convert to Celsius
            if unit == 'c':
                return value
            elif unit == 'f':
                return (value - 32) * 5/9
            elif unit == 'k':
                return value - 273.15
        except:
            pass
        return None
    
    @classmethod
    def parse_time_to_seconds(cls, time_str: str) -> Optional[float]:
        """Parse time string to seconds"""
        try:
            time_str = time_str.strip().lower()
            match = re.match(r'^(\d+\.?\d*)\s*(s|sec|min|h|hr)$', time_str)
            if not match:
                return None
            
            value = float(match.group(1))
            unit = match.group(2)
            
            # Convert to seconds
            if unit in ['s', 'sec']:
                return value
            elif unit == 'min':
                return value * 60
            elif unit in ['h', 'hr']:
                return value * 3600
        except:
            pass
        return None
    
    @classmethod
    def parse_pressure(cls, pressure_str: str) -> Optional[float]:
        """Parse pressure string to psi"""
        try:
            pressure_str = pressure_str.strip().lower()
            match = re.match(r'^(\d+\.?\d*)\s*(psi|bar|atm|pa|kpa|mpa)$', pressure_str)
            if not match:
                return None
            
            value = float(match.group(1))
            unit = match.group(2)
            
            # Convert to psi
            if unit == 'psi':
                return value
            elif unit == 'bar':
                return value * 14.504
            elif unit == 'atm':
                return value * 14.696
            elif unit == 'pa':
                return value * 0.000145
            elif unit == 'kpa':
                return value * 0.145
            elif unit == 'mpa':
                return value * 145.0
        except:
            pass
        return None
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove multiple consecutive underscores
        filename = re.sub(r'_{2,}', '_', filename)
        
        # Trim length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + ('.' + ext if ext else '')
        
        return filename.strip('._')
    
    @classmethod
    def format_duration(cls, seconds: float) -> str:
        """Format duration in seconds to human-readable string"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}min"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @classmethod
    def format_flow_rate(cls, ml_per_min: float) -> str:
        """Format flow rate to appropriate units"""
        if ml_per_min >= 1:
            return f"{ml_per_min:.2f} mL/min"
        elif ml_per_min >= 0.001:
            return f"{ml_per_min * 1000:.1f} μL/min"
        else:
            return f"{ml_per_min * 1000000:.0f} nL/min"
    
    @classmethod
    def check_material_compatibility(cls, material1: str, material2: str) -> Dict[str, Any]:
        """Check compatibility between two materials"""
        # Simple compatibility matrix
        compatibility_matrix = {
            'PFA': ['Glass', 'PTFE', 'FEP', 'Stainless Steel', 'PEEK'],
            'PTFE': ['Glass', 'PFA', 'FEP', 'Stainless Steel', 'PEEK'], 
            'Glass': ['PFA', 'PTFE', 'FEP', 'PEEK'],
            'Stainless Steel': ['PFA', 'PTFE', 'FEP', 'PEEK'],
            'PEEK': ['PFA', 'PTFE', 'Glass', 'Stainless Steel']
        }
        
        result = {
            'compatible': True,
            'warnings': [],
            'recommendations': []
        }
        
        if material1 in compatibility_matrix:
            if material2 not in compatibility_matrix[material1]:
                result['compatible'] = False
                result['warnings'].append(f"Potential incompatibility between {material1} and {material2}")
                result['recommendations'].append("Verify chemical compatibility for your specific application")
        
        return result