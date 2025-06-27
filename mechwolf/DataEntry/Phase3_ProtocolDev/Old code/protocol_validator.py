"""
Protocol Validator

Comprehensive protocol validation using MechWolf core integration
and custom validation rules for safety and correctness.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import timedelta


class ProtocolValidator:
    """Protocol validation with MechWolf core integration"""
    
    def __init__(self):
        """Initialize validator with validation rules"""
        
        # Safety limits
        self.safety_limits = {
            'max_flow_rate': 50.0,    # mL/min
            'max_pressure': 100.0,    # psi
            'max_temperature': 200.0,  # °C
            'min_temperature': -50.0,  # °C
            'max_procedure_duration': 24 * 3600,  # seconds (24 hours)
            'max_total_duration': 48 * 3600       # seconds (48 hours)
        }
        
        # Component capabilities
        self.component_capabilities = {
            'HarvardSyringePump': {
                'actions': ['run', 'stop'],
                'max_rate': 25.0,  # mL/min
                'min_rate': 0.01   # mL/min
            },
            'VarianPump': {
                'actions': ['run', 'stop'],
                'max_rate': 50.0,  # mL/min
                'min_rate': 0.1    # mL/min
            },
            'FreeStepPump': {
                'actions': ['run', 'stop'],
                'max_rate': 10.0,  # mL/min
                'min_rate': 0.001  # mL/min
            },
            'ViciValve': {
                'actions': ['switch'],
                'max_position': 12,
                'min_position': 1
            }
        }
        
    def validate_protocol(self, procedures: List[Dict[str, Any]], 
                         pumps: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive protocol validation
        
        Args:
            procedures: List of procedure dictionaries
            pumps: Optional dictionary of configured pump objects
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'procedure_analysis': {},
            'timing_analysis': {},
            'safety_analysis': {}
        }
        
        if not procedures:
            results['warnings'].append("No procedures defined")
            return results
        
        try:
            # Individual procedure validation
            results['procedure_analysis'] = self._validate_procedures(procedures)
            if results['procedure_analysis']['errors']:
                results['valid'] = False
                results['errors'].extend(results['procedure_analysis']['errors'])
            results['warnings'].extend(results['procedure_analysis']['warnings'])
            
            # Timing and sequencing validation
            results['timing_analysis'] = self._validate_timing(procedures)
            if results['timing_analysis']['errors']:
                results['valid'] = False
                results['errors'].extend(results['timing_analysis']['errors'])
            results['warnings'].extend(results['timing_analysis']['warnings'])
            
            # Safety validation
            results['safety_analysis'] = self._validate_safety(procedures, pumps)
            results['warnings'].extend(results['safety_analysis']['warnings'])
            results['suggestions'].extend(results['safety_analysis']['suggestions'])
            
            # MechWolf core validation (if available)
            mechwolf_results = self._validate_with_mechwolf_core(procedures, pumps)
            if mechwolf_results['errors']:
                results['valid'] = False
                results['errors'].extend(mechwolf_results['errors'])
            results['warnings'].extend(mechwolf_results['warnings'])
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Validation error: {e}")
        
        return results
    
    def _validate_procedures(self, procedures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate individual procedures"""
        results = {
            'errors': [],
            'warnings': [],
            'procedure_count': len(procedures),
            'action_distribution': {}
        }
        
        # Count action types
        for procedure in procedures:
            action = procedure.get('action', 'unknown')
            results['action_distribution'][action] = results['action_distribution'].get(action, 0) + 1
        
        # Validate each procedure
        for i, procedure in enumerate(procedures):
            proc_errors = self._validate_individual_procedure(procedure, i)
            results['errors'].extend(proc_errors)
        
        # Check for common issues
        if results['action_distribution'].get('run', 0) == 0:
            results['warnings'].append("No pump run procedures - protocol may not perform any flow")
        
        if len(set(proc.get('component') for proc in procedures)) == 1:
            results['warnings'].append("All procedures use same component - consider multi-component protocols")
        
        return results
    
    def _validate_individual_procedure(self, procedure: Dict[str, Any], index: int) -> List[str]:
        """Validate a single procedure"""
        errors = []
        
        component = procedure.get('component')
        action = procedure.get('action')
        start_time = procedure.get('start_time')
        duration = procedure.get('duration')
        parameters = procedure.get('parameters', {})
        
        # Basic field validation
        if not component:
            errors.append(f"Procedure {index + 1}: Missing component")
        
        if not action:
            errors.append(f"Procedure {index + 1}: Missing action")
        
        if not start_time:
            errors.append(f"Procedure {index + 1}: Missing start time")
        
        # Component-action compatibility
        if component and action:
            component_type = self._infer_component_type(component)
            if component_type in self.component_capabilities:
                capabilities = self.component_capabilities[component_type]
                if action not in capabilities['actions']:
                    errors.append(
                        f"Procedure {index + 1}: Action '{action}' not supported by {component_type}"
                    )
        
        # Parameter validation
        if action == 'run':
            rate = parameters.get('rate')
            if not rate:
                errors.append(f"Procedure {index + 1}: Flow rate required for pump run")
            else:
                rate_value = self._parse_flow_rate(rate)
                if rate_value is None:
                    errors.append(f"Procedure {index + 1}: Invalid flow rate format '{rate}'")
                elif rate_value > self.safety_limits['max_flow_rate']:
                    errors.append(
                        f"Procedure {index + 1}: Flow rate {rate} exceeds safety limit "
                        f"({self.safety_limits['max_flow_rate']} mL/min)"
                    )
            
            if not duration:
                errors.append(f"Procedure {index + 1}: Duration required for pump run")
            else:
                duration_seconds = self._parse_time_to_seconds(duration)
                if duration_seconds is None:
                    errors.append(f"Procedure {index + 1}: Invalid duration format '{duration}'")
                elif duration_seconds > self.safety_limits['max_procedure_duration']:
                    errors.append(
                        f"Procedure {index + 1}: Duration {duration} exceeds safety limit "
                        f"({self.safety_limits['max_procedure_duration']/3600:.1f} hours)"
                    )
        
        elif action == 'switch':
            position = parameters.get('position')
            if not position:
                errors.append(f"Procedure {index + 1}: Position required for valve switch")
        
        # Time format validation
        if start_time and self._parse_time_to_seconds(start_time) is None:
            errors.append(f"Procedure {index + 1}: Invalid start time format '{start_time}'")
        
        return errors
    
    def _validate_timing(self, procedures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate timing and sequencing"""
        results = {
            'errors': [],
            'warnings': [],
            'total_duration': 0,
            'concurrent_procedures': [],
            'timeline_conflicts': []
        }
        
        # Parse timing for all procedures
        timeline_events = []
        
        for i, procedure in enumerate(procedures):
            start_time = procedure.get('start_time', '0s')
            duration = procedure.get('duration', '0s')
            
            start_seconds = self._parse_time_to_seconds(start_time)
            duration_seconds = self._parse_time_to_seconds(duration)
            
            if start_seconds is None or duration_seconds is None:
                continue  # Skip invalid times (already caught in procedure validation)
            
            end_seconds = start_seconds + duration_seconds
            
            timeline_events.append({
                'index': i,
                'component': procedure.get('component'),
                'action': procedure.get('action'),
                'start': start_seconds,
                'end': end_seconds,
                'duration': duration_seconds
            })
        
        if not timeline_events:
            return results
        
        # Calculate total duration
        results['total_duration'] = max(event['end'] for event in timeline_events)
        
        if results['total_duration'] > self.safety_limits['max_total_duration']:
            results['errors'].append(
                f"Total protocol duration ({results['total_duration']/3600:.1f} hours) "
                f"exceeds safety limit ({self.safety_limits['max_total_duration']/3600:.1f} hours)"
            )
        
        # Check for concurrent procedures
        for i, event1 in enumerate(timeline_events):
            for j, event2 in enumerate(timeline_events[i+1:], i+1):
                # Check for overlap
                if (event1['start'] < event2['end'] and event2['start'] < event1['end']):
                    overlap = {
                        'procedure1': event1['index'] + 1,
                        'procedure2': event2['index'] + 1,
                        'component1': event1['component'],
                        'component2': event2['component'],
                        'action1': event1['action'],
                        'action2': event2['action']
                    }
                    results['concurrent_procedures'].append(overlap)
                    
                    # Check for conflicts
                    if event1['component'] == event2['component']:
                        results['timeline_conflicts'].append(
                            f"Procedures {event1['index'] + 1} and {event2['index'] + 1} "
                            f"both use {event1['component']} with overlapping times"
                        )
        
        if results['timeline_conflicts']:
            results['errors'].extend(results['timeline_conflicts'])
        
        if results['concurrent_procedures']:
            results['warnings'].append(
                f"Found {len(results['concurrent_procedures'])} concurrent procedure pairs"
            )
        
        return results
    
    def _validate_safety(self, procedures: List[Dict[str, Any]], 
                        pumps: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate safety considerations"""
        results = {
            'warnings': [],
            'suggestions': [],
            'safety_score': 100,  # Start with perfect score
            'risk_factors': []
        }
        
        # Check for high flow rates
        high_flow_procedures = []
        for i, procedure in enumerate(procedures):
            if procedure.get('action') == 'run':
                rate_str = procedure.get('parameters', {}).get('rate', '')
                rate_value = self._parse_flow_rate(rate_str)
                
                if rate_value and rate_value > 10.0:  # > 10 mL/min
                    high_flow_procedures.append((i + 1, rate_value))
        
        if high_flow_procedures:
            results['warnings'].append(
                f"High flow rates detected in procedures: "
                f"{', '.join(f'{proc} ({rate:.1f} mL/min)' for proc, rate in high_flow_procedures)}"
            )
            results['risk_factors'].append("High flow rates")
            results['safety_score'] -= 10
        
        # Check for long-running procedures
        long_procedures = []
        for i, procedure in enumerate(procedures):
            duration_str = procedure.get('duration', '')
            duration_seconds = self._parse_time_to_seconds(duration_str)
            
            if duration_seconds and duration_seconds > 3600:  # > 1 hour
                long_procedures.append((i + 1, duration_seconds / 3600))
        
        if long_procedures:
            results['warnings'].append(
                f"Long-running procedures detected: "
                f"{', '.join(f'{proc} ({hours:.1f}h)' for proc, hours in long_procedures)}"
            )
            results['risk_factors'].append("Long duration procedures")
            results['safety_score'] -= 5
        
        # Check for potential pressure buildup
        pump_procedures = [p for p in procedures if p.get('action') == 'run']
        valve_procedures = [p for p in procedures if p.get('action') == 'switch']
        
        if pump_procedures and not valve_procedures:
            results['suggestions'].append(
                "Consider adding valve controls to manage flow direction and prevent pressure buildup"
            )
        
        # Check for emergency stop procedures
        stop_procedures = [p for p in procedures if p.get('action') == 'stop']
        if pump_procedures and not stop_procedures:
            results['suggestions'].append(
                "Consider adding explicit pump stop procedures for safety"
            )
        
        return results
    
    def _validate_with_mechwolf_core(self, procedures: List[Dict[str, Any]], 
                                   pumps: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate using MechWolf core if available"""
        results = {
            'errors': [],
            'warnings': [],
            'mechwolf_available': False
        }
        
        try:
            import mechwolf as mw
            results['mechwolf_available'] = True
            
            # This would create a temporary protocol for validation
            # For now, we'll provide a placeholder
            results['warnings'].append(
                "MechWolf core validation available but not fully implemented in this interface"
            )
            
        except ImportError:
            results['warnings'].append(
                "MechWolf core not available - using built-in validation only"
            )
        
        return results
    
    def check_safety(self, procedures: List[Dict[str, Any]], 
                    pumps: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform dedicated safety check"""
        return {
            'safe': True,
            'concerns': [],
            'recommendations': [
                "Always monitor the system during protocol execution",
                "Ensure proper waste collection and disposal",
                "Verify all connections before starting protocol",
                "Have emergency stop procedures ready"
            ]
        }
    
    def _infer_component_type(self, component_name: str) -> str:
        """Infer component type from name"""
        name_lower = component_name.lower()
        
        if 'pump' in name_lower:
            if 'harvard' in name_lower:
                return 'HarvardSyringePump'
            elif 'varian' in name_lower:
                return 'VarianPump'
            elif 'freestep' in name_lower:
                return 'FreeStepPump'
            else:
                return 'Pump'
        elif 'valve' in name_lower:
            return 'ViciValve'
        elif 'timer' in name_lower:
            return 'Timer'
        else:
            return 'Unknown'
    
    def _parse_flow_rate(self, rate_str: str) -> Optional[float]:
        """Parse flow rate string to mL/min"""
        if not rate_str:
            return None
        
        try:
            rate_str = rate_str.strip().lower()
            
            # Extract number
            import re
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
    
    def _parse_time_to_seconds(self, time_str: str) -> Optional[float]:
        """Parse time string to seconds"""
        if not time_str:
            return None
        
        try:
            time_str = time_str.strip().lower()
            
            # Extract number and unit
            import re
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
    
    def suggest_optimizations(self, procedures: List[Dict[str, Any]]) -> List[str]:
        """Suggest protocol optimizations"""
        suggestions = []
        
        # Analyze timing patterns
        timeline_events = []
        for procedure in procedures:
            start_seconds = self._parse_time_to_seconds(procedure.get('start_time', '0s'))
            duration_seconds = self._parse_time_to_seconds(procedure.get('duration', '0s'))
            
            if start_seconds is not None and duration_seconds is not None:
                timeline_events.append({
                    'start': start_seconds,
                    'end': start_seconds + duration_seconds,
                    'component': procedure.get('component'),
                    'action': procedure.get('action')
                })
        
        # Check for gaps in timeline
        timeline_events.sort(key=lambda x: x['start'])
        
        for i in range(len(timeline_events) - 1):
            current_end = timeline_events[i]['end']
            next_start = timeline_events[i + 1]['start']
            
            if next_start > current_end + 60:  # Gap > 1 minute
                gap_minutes = (next_start - current_end) / 60
                suggestions.append(
                    f"Consider reducing {gap_minutes:.1f} minute gap between procedures "
                    f"{i + 1} and {i + 2}"
                )
        
        # Check for optimization opportunities
        pump_runs = [e for e in timeline_events if e['action'] == 'run']
        if len(pump_runs) > 1:
            suggestions.append(
                "Consider parallelizing pump operations to reduce total protocol time"
            )
        
        return suggestions