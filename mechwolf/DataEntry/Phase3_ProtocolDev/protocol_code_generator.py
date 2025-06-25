"""
Protocol Code Generator for Phase 3 Protocol Development

Generates clean, readable MechWolf protocol code in the exact format
specified by the user, with proper timedelta variable handling.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import timedelta
import re


class ProtocolCodeGenerator:
    """Generates MechWolf protocol code from procedure definitions"""
    
    def __init__(self, time_variable_manager):
        """
        Initialize code generator
        
        Args:
            time_variable_manager: TimeVariableManager instance
        """
        self.time_var_manager = time_variable_manager
        self.procedures = []
        self.apparatus_name = "A"  # Default apparatus variable name
    
    def set_apparatus_name(self, name: str):
        """Set the apparatus variable name"""
        self.apparatus_name = name
    
    def add_procedure(self, procedure: Dict[str, Any]):
        """Add a procedure to the protocol"""
        self.procedures.append(procedure)
    
    def clear_procedures(self):
        """Clear all procedures"""
        self.procedures = []
    
    def set_procedures(self, procedures: List[Dict[str, Any]]):
        """Set the complete list of procedures"""
        self.procedures = procedures.copy()
    
    def generate_protocol_code(self) -> str:
        """
        Generate complete MechWolf protocol code
        
        Returns:
            Complete protocol code as string
        """
        lines = []
        
        # Add header comment
        lines.extend([
            "# Generated MechWolf Protocol Code",
            "# Created by Phase 3 Protocol Development Tool",
            ""
        ])
        
        # Add imports
        lines.extend([
            "import mechwolf as mw",
            "from datetime import timedelta",
            ""
        ])
        
        # Add time variable definitions
        time_var_lines = self.time_var_manager.get_variable_definitions_code()
        if time_var_lines:
            lines.append("# Time variable definitions")
            lines.extend(time_var_lines)
            lines.append("")
        
        # Create protocol object
        lines.extend([
            f"# Create protocol from apparatus",
            f"P = mw.Protocol({self.apparatus_name})",
            ""
        ])
        
        # Add procedures
        if self.procedures:
            lines.append("# Protocol procedures")
            procedure_lines = self._generate_procedure_lines()
            lines.extend(procedure_lines)
        else:
            lines.append("# No procedures defined yet")
        
        # Add execution template
        lines.extend([
            "",
            "# Calculate total time",
            f"print(f'TOTAL TIME: {{{self.time_var_manager.current_time_var}}}')",
            "",
            "# Execute protocol (uncomment to run)",
            "# P.execute(confirm = True)"
        ])
        
        return "\n".join(lines)
    
    def _generate_procedure_lines(self) -> List[str]:
        """Generate code lines for all procedures"""
        lines = []
        current_time_var = self.time_var_manager.current_time_var
        
        for i, procedure in enumerate(self.procedures):
            proc_lines = self._generate_single_procedure(procedure, i)
            lines.extend(proc_lines)
            
            # Add time increment if specified
            if procedure.get('increment_current_time'):
                duration_expr = procedure.get('duration_expression', procedure.get('duration', ''))
                if duration_expr:
                    increment_line = self.time_var_manager.generate_time_increment_code(duration_expr)
                    lines.append(increment_line)
                    lines.append("")
        
        return lines
    
    def _generate_single_procedure(self, procedure: Dict[str, Any], index: int) -> List[str]:
        """Generate code lines for a single procedure"""
        lines = []
        
        component = procedure.get('component', 'pump_1')
        action = procedure.get('action', 'run')
        start_expr = procedure.get('start_expression', procedure.get('start_time', 'current'))
        duration_expr = procedure.get('duration_expression', procedure.get('duration', ''))
        parameters = procedure.get('parameters', {})
        
        # Add comment if procedure has a description
        description = procedure.get('description')
        if description:
            lines.append(f"# {description}")
        
        # Generate the P.add() call based on action type
        if action == 'run' and 'rate' in parameters:
            # Pump run procedure
            rate = parameters['rate']
            
            if duration_expr:
                # With duration
                lines.append(
                    f"P.add({component}, start = {start_expr},"
                )
                lines.append(
                    f"              duration = {duration_expr}, rate = \"{rate}\")"
                )
            else:
                # Without duration (continuous)
                lines.append(
                    f"P.add({component}, start = {start_expr}, rate = \"{rate}\")"
                )
        
        elif action == 'switch' and 'position' in parameters:
            # Valve switch procedure
            position = parameters['position']
            lines.append(
                f"P.add({component}, start = {start_expr}, setting = \"{position}\")"
            )
        
        elif action == 'stop':
            # Stop procedure
            lines.append(
                f"P.add({component}, start = {start_expr}, rate = \"0 mL/min\")"
            )
        
        else:
            # Generic procedure
            param_strs = []
            for key, value in parameters.items():
                if isinstance(value, str):
                    param_strs.append(f'{key} = "{value}"')
                else:
                    param_strs.append(f'{key} = {value}')
            
            if param_strs:
                lines.append(
                    f"P.add({component}, start = {start_expr}, {', '.join(param_strs)})"
                )
            else:
                lines.append(
                    f"P.add({component}, start = {start_expr})"
                )
        
        lines.append("")
        return lines
    
    def validate_procedures(self) -> Tuple[bool, List[str]]:
        """
        Validate all procedures for code generation
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        for i, procedure in enumerate(self.procedures):
            proc_errors = self._validate_single_procedure(procedure, i)
            errors.extend(proc_errors)
        
        return len(errors) == 0, errors
    
    def _validate_single_procedure(self, procedure: Dict[str, Any], index: int) -> List[str]:
        """Validate a single procedure"""
        errors = []
        proc_num = index + 1
        
        # Check required fields
        if not procedure.get('component'):
            errors.append(f"Procedure {proc_num}: Missing component")
        
        if not procedure.get('action'):
            errors.append(f"Procedure {proc_num}: Missing action")
        
        # Validate start time expression
        start_expr = procedure.get('start_expression', procedure.get('start_time', ''))
        if start_expr:
            is_valid, error_msg = self.time_var_manager.validate_expression(start_expr)
            if not is_valid:
                errors.append(f"Procedure {proc_num}: Invalid start time - {error_msg}")
        
        # Validate duration expression
        duration_expr = procedure.get('duration_expression', procedure.get('duration', ''))
        if duration_expr:
            is_valid, error_msg = self.time_var_manager.validate_expression(duration_expr)
            if not is_valid:
                errors.append(f"Procedure {proc_num}: Invalid duration - {error_msg}")
        
        # Action-specific validation
        action = procedure.get('action')
        parameters = procedure.get('parameters', {})
        
        if action == 'run':
            if 'rate' not in parameters:
                errors.append(f"Procedure {proc_num}: Flow rate required for pump run")
            elif not self._validate_flow_rate(parameters['rate']):
                errors.append(f"Procedure {proc_num}: Invalid flow rate format")
        
        elif action == 'switch':
            if 'position' not in parameters:
                errors.append(f"Procedure {proc_num}: Position required for valve switch")
        
        return errors
    
    def _validate_flow_rate(self, rate_str: str) -> bool:
        """Validate flow rate format"""
        if not rate_str:
            return False
        
        # Common patterns: "5 mL/min", "2.5 mL/min", "10 μL/min"
        pattern = r'^\d+\.?\d*\s*(mL|μL|uL|nL)/min$'
        return bool(re.match(pattern, rate_str, re.IGNORECASE))
    
    def generate_code_preview(self, max_lines: int = 50) -> str:
        """
        Generate a preview of the protocol code
        
        Args:
            max_lines: Maximum number of lines to include in preview
            
        Returns:
            Code preview as string
        """
        full_code = self.generate_protocol_code()
        lines = full_code.split('\n')
        
        if len(lines) <= max_lines:
            return full_code
        
        preview_lines = lines[:max_lines]
        preview_lines.append(f"# ... ({len(lines) - max_lines} more lines)")
        
        return '\n'.join(preview_lines)
    
    def get_procedure_summary(self) -> Dict[str, Any]:
        """Get summary information about the procedures"""
        if not self.procedures:
            return {
                'total_procedures': 0,
                'components_used': [],
                'actions_used': [],
                'estimated_duration': 'Unknown'
            }
        
        components = set()
        actions = set()
        
        for proc in self.procedures:
            if proc.get('component'):
                components.add(proc['component'])
            if proc.get('action'):
                actions.add(proc['action'])
        
        return {
            'total_procedures': len(self.procedures),
            'components_used': sorted(list(components)),
            'actions_used': sorted(list(actions)),
            'estimated_duration': 'See TOTAL TIME in generated code'
        }
    
    def export_to_clipboard(self) -> str:
        """
        Generate code formatted for clipboard export
        
        Returns:
            Code ready for copying to clipboard
        """
        return self.generate_protocol_code()
    
    def save_procedures_to_metadata(self, experiment_manager) -> bool:
        """
        Save procedures to experimental metadata
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
            
        Returns:
            True if successful
        """
        try:
            # Convert procedures to metadata format
            metadata_procedures = []
            
            for proc in self.procedures:
                metadata_proc = {
                    'component_id': proc.get('component', ''),
                    'action': proc.get('action', ''),
                    'start_time_expression': proc.get('start_expression', proc.get('start_time', '')),
                    'duration_expression': proc.get('duration_expression', proc.get('duration', '')),
                    'parameters': proc.get('parameters', {}),
                    'description': proc.get('description', ''),
                    'increment_current_time': proc.get('increment_current_time', False)
                }
                metadata_procedures.append(metadata_proc)
            
            # Save to protocol section
            protocol_data = {
                'procedures': metadata_procedures,
                'time_variables': {
                    name: str(duration.total_seconds()) + 's' 
                    for name, duration in self.time_var_manager.variables.items()
                },
                'current_time_variable': self.time_var_manager.current_time_var,
                'apparatus_variable_name': self.apparatus_name
            }
            
            # Update experimental metadata
            experiment_manager.protocol.load_procedures_from_list(metadata_procedures)
            success = experiment_manager.save()
            
            return success
            
        except Exception as e:
            print(f"Error saving procedures: {e}")
            return False
    
    def load_procedures_from_metadata(self, experiment_manager) -> bool:
        """
        Load procedures from experimental metadata
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
            
        Returns:
            True if successful
        """
        try:
            protocol_data = experiment_manager.get_section_data("protocol_config")
            
            if not protocol_data:
                return False
            
            # Load procedures
            metadata_procedures = protocol_data.get('procedures', [])
            self.procedures = []
            
            for meta_proc in metadata_procedures:
                procedure = {
                    'component': meta_proc.get('component_id', ''),
                    'action': meta_proc.get('action', ''),
                    'start_expression': meta_proc.get('start_time_expression', ''),
                    'duration_expression': meta_proc.get('duration_expression', ''),
                    'parameters': meta_proc.get('parameters', {}),
                    'description': meta_proc.get('description', ''),
                    'increment_current_time': meta_proc.get('increment_current_time', False)
                }
                self.procedures.append(procedure)
            
            # Load time variables
            time_vars = protocol_data.get('time_variables', {})
            if time_vars:
                self.time_var_manager.set_variables_from_dict(time_vars)
            
            # Load other settings
            self.apparatus_name = protocol_data.get('apparatus_variable_name', 'A')
            current_time_var = protocol_data.get('current_time_variable', 'current')
            self.time_var_manager.current_time_var = current_time_var
            
            return True
            
        except Exception as e:
            print(f"Error loading procedures: {e}")
            return False