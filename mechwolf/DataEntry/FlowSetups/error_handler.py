from .utils import convert_dimension_to_float

class SetupError(Exception):
    """Base exception for setup errors"""
    pass

class ValidationError(SetupError):
    """Exception for validation errors"""
    pass

class ErrorHandler:
    @staticmethod
    def validate_mixer_inputs(data):
        if data['using_mixer'] and not all([
            data['mixer_tube_id_raw'],
            data['mixer_tube_od_raw'],
            data['mixer_tube_material']
        ]):
            raise ValidationError("When using mixer, you must fill in all mixer tube details")

    @staticmethod
    def validate_tube_dimensions(tube_data):
        """Validate tube dimensions ensuring OD > ID for all tubes"""
        # Validate reaction tubes
        for id_val, od_val in tube_data.get('reaction_tubes', []):
            if None in [id_val, od_val]:
                raise ValidationError("Please enter valid values for reaction tube dimensions (e.g., '1/16 in' or '0.0625 in').")
            
            r_id = convert_dimension_to_float(id_val)
            r_od = convert_dimension_to_float(od_val)
            
            if r_od <= r_id:
                raise ValidationError(f"Reaction tube outer diameter ({od_val}) must be greater than inner diameter ({id_val})")
        
        # Validate mixer tubes if present
        for id_val, od_val in tube_data.get('mixer_tubes', []):
            if None in [id_val, od_val]:
                raise ValidationError("Please enter valid values for mixer tube dimensions (e.g., '1/8 in' or '0.125 in').")
            
            m_id = convert_dimension_to_float(id_val)
            m_od = convert_dimension_to_float(od_val)
            
            if m_od <= m_id:
                raise ValidationError(f"Mixer tube outer diameter ({od_val}) must be greater than inner diameter ({id_val})")

    @staticmethod
    def validate_coil_lengths(coil_lengths):
        """Validate coil lengths are valid numeric values"""
        if any(length is None for length in coil_lengths):
            raise ValidationError("Please enter valid numeric values for coil lengths.")

    @staticmethod
    def validate_coil_config(coils):
        """Validate coil configuration including indices"""
        valid_indices = ['a', 'x', 'b', 'y']
        used_indices = set()
        
        for coil in coils:
            if 'index' not in coil:
                raise ValidationError("Missing coil index")
            if coil['index'] not in valid_indices:
                raise ValidationError(f"Invalid coil index: {coil['index']}")
            if coil['index'] in used_indices:
                raise ValidationError(f"Duplicate coil index: {coil['index']}")
            used_indices.add(coil['index'])
            
            if 'length' not in coil:
                raise ValidationError(f"Missing length for coil {coil['index']}")
