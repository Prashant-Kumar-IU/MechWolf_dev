"""
Procedure Builder

Visual interface for building protocol procedures with drag-and-drop style
component selection and parameter configuration.
"""

import ipywidgets as widgets
from IPython.display import clear_output
from typing import Dict, Any, List, Optional, Tuple


class ProcedureBuilder:
    """Visual procedure building interface"""
    
    def __init__(self, experiment_manager, pumps=None):
        """
        Initialize procedure builder
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
            pumps: Dictionary of configured pump objects
        """
        self.experiment = experiment_manager
        self.pumps = pumps or {}
        
        # Procedure templates
        self.procedure_templates = {
            'pump_run': {
                'name': 'Pump Run',
                'description': 'Run pump for specified duration and rate',
                'parameters': ['rate', 'duration'],
                'applicable_components': ['HarvardSyringePump', 'VarianPump', 'FreeStepPump']
            },
            'valve_switch': {
                'name': 'Valve Switch',
                'description': 'Switch valve to specified position',
                'parameters': ['position'],
                'applicable_components': ['ViciValve']
            },
            'wait': {
                'name': 'Wait',
                'description': 'Wait for specified duration',
                'parameters': ['duration'],
                'applicable_components': ['Timer']
            },
            'temperature_set': {
                'name': 'Set Temperature',
                'description': 'Set temperature controller to target',
                'parameters': ['temperature'],
                'applicable_components': ['TemperatureController']
            }
        }
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create procedure builder widgets"""
        
        # Component selection
        self.component_dropdown = widgets.Dropdown(
            description='Component:',
            layout=widgets.Layout(width='300px')
        )
        
        # Action selection
        self.action_dropdown = widgets.Dropdown(
            description='Action:',
            layout=widgets.Layout(width='200px')
        )
        self.action_dropdown.observe(self._on_action_change, names='value')
        
        # Timing inputs
        self.start_time_input = widgets.Text(
            value='0s',
            placeholder='e.g., 0s, 5min, 1h',
            description='Start Time:',
            layout=widgets.Layout(width='200px')
        )
        
        self.duration_input = widgets.Text(
            placeholder='e.g., 10min, 30s',
            description='Duration:',
            layout=widgets.Layout(width='200px')
        )
        
        # Dynamic parameter inputs
        self.parameter_container = widgets.VBox()
        self.parameter_widgets = {}
        
        # Action buttons
        self.add_procedure_button = widgets.Button(
            description='➕ Add Procedure',
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        self.add_procedure_button.on_click(self._add_procedure)
        
        self.template_button = widgets.Button(
            description='📋 Use Template',
            button_style='info',
            layout=widgets.Layout(width='140px')
        )
        self.template_button.on_click(self._show_templates)
        
        # Template selection
        self.template_dropdown = widgets.Dropdown(
            options=[(template['name'], key) for key, template in self.procedure_templates.items()],
            description='Template:',
            layout=widgets.Layout(width='250px')
        )
        self.template_dropdown.observe(self._on_template_change, names='value')
        
        # Initialize
        self._refresh_component_options()
        self._update_action_options()
        
    def _refresh_component_options(self):
        """Refresh available component options"""
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            # Get all components
            all_components = (components.get('active', []) + 
                            components.get('passive', []))
            
            # Create options
            component_options = [('Select component...', '')]
            
            for component in all_components:
                name = component.get('name', 'Unknown')
                comp_type = component.get('type', 'Unknown')
                component_options.append((f"{name} ({comp_type})", name))
            
            # Add timer option
            component_options.append(('Timer (Wait)', 'Timer'))
            
            self.component_dropdown.options = component_options
            
        except Exception as e:
            print(f"Error refreshing components: {e}")
    
    def _update_action_options(self):
        """Update available action options based on selected component"""
        component_name = self.component_dropdown.value
        
        if not component_name:
            self.action_dropdown.options = [('Select action...', '')]
            return
        
        # Get component type
        component_type = self._get_component_type(component_name)
        
        # Determine available actions
        actions = []
        
        if component_type in ['HarvardSyringePump', 'VarianPump', 'FreeStepPump']:
            actions = [('Run', 'run'), ('Stop', 'stop')]
        elif component_type == 'ViciValve':
            actions = [('Switch Position', 'switch')]
        elif component_name == 'Timer':
            actions = [('Wait', 'wait')]
        elif component_type == 'TemperatureController':
            actions = [('Set Temperature', 'set_temperature')]
        else:
            actions = [('Custom Action', 'custom')]
        
        if not actions:
            actions = [('No actions available', '')]
        
        self.action_dropdown.options = actions
        if actions and actions[0][1]:
            self.action_dropdown.value = actions[0][1]
    
    def _get_component_type(self, component_name: str) -> str:
        """Get component type by name"""
        if component_name == 'Timer':
            return 'Timer'
        
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            # Search in all components
            all_components = (components.get('active', []) + 
                            components.get('passive', []))
            
            for component in all_components:
                if component.get('name') == component_name:
                    return component.get('type', 'Unknown')
        except:
            pass
        
        return 'Unknown'
    
    def _on_action_change(self, change):
        """Handle action selection change"""
        self._update_parameter_inputs()
    
    def _update_parameter_inputs(self):
        """Update parameter input widgets based on selected action"""
        action = self.action_dropdown.value
        component_type = self._get_component_type(self.component_dropdown.value)
        
        # Clear previous widgets
        self.parameter_widgets.clear()
        
        # Create parameter widgets based on action
        parameter_widgets = []
        
        if action == 'run':
            # Pump run parameters
            rate_widget = widgets.Text(
                placeholder='e.g., 5 mL/min',
                description='Flow Rate:',
                layout=widgets.Layout(width='200px')
            )
            self.parameter_widgets['rate'] = rate_widget
            parameter_widgets.append(rate_widget)
            
            # Duration is handled separately
            
        elif action == 'switch':
            # Valve switch parameters
            if component_type == 'ViciValve':
                # Get valve mapping if available
                position_options = self._get_valve_positions(self.component_dropdown.value)
                
                if position_options:
                    position_widget = widgets.Dropdown(
                        options=position_options,
                        description='Position:',
                        layout=widgets.Layout(width='200px')
                    )
                else:
                    position_widget = widgets.Text(
                        placeholder='e.g., 1, 2, THF, Li',
                        description='Position:',
                        layout=widgets.Layout(width='200px')
                    )
                
                self.parameter_widgets['position'] = position_widget
                parameter_widgets.append(position_widget)
        
        elif action == 'set_temperature':
            # Temperature controller parameters
            temp_widget = widgets.Text(
                placeholder='e.g., 25°C, 80°C',
                description='Temperature:',
                layout=widgets.Layout(width='200px')
            )
            self.parameter_widgets['temperature'] = temp_widget
            parameter_widgets.append(temp_widget)
        
        # Update parameter container
        self.parameter_container.children = parameter_widgets
    
    def _get_valve_positions(self, valve_name: str) -> List[Tuple[str, str]]:
        """Get valve position options if mapping is available"""
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            components = apparatus_data.get('components', {})
            
            # Find valve component
            for component in components.get('active', []):
                if component.get('name') == valve_name and component.get('type') == 'ViciValve':
                    mapping = component.get('parameters', {}).get('mapping', {})
                    if mapping:
                        options = [('Select position...', '')]
                        for reagent, position in mapping.items():
                            options.append((f"{reagent} (Port {position})", reagent))
                        return options
            
        except Exception:
            pass
        
        return []
    
    def _on_template_change(self, change):
        """Handle template selection change"""
        template_key = change['new']
        if not template_key:
            return
        
        template = self.procedure_templates[template_key]
        
        # Update component dropdown to show only applicable components
        apparatus_data = self.experiment.apparatus.get_data()
        components = apparatus_data.get('components', {})
        all_components = (components.get('active', []) + 
                        components.get('passive', []))
        
        applicable_components = template['applicable_components']
        
        # Filter components
        filtered_options = [('Select component...', '')]
        for component in all_components:
            comp_type = component.get('type', 'Unknown')
            if comp_type in applicable_components:
                name = component.get('name', 'Unknown')
                filtered_options.append((f"{name} ({comp_type})", name))
        
        # Add special cases
        if 'Timer' in applicable_components:
            filtered_options.append(('Timer (Wait)', 'Timer'))
        
        # Temporarily disconnect observer to avoid recursion
        self.component_dropdown.unobserve(self._update_action_options, names='value')
        self.component_dropdown.options = filtered_options
        self.component_dropdown.observe(self._update_action_options, names='value')
        
        # Set default action based on template
        if template_key == 'pump_run':
            self.action_dropdown.options = [('Run', 'run')]
            self.action_dropdown.value = 'run'
        elif template_key == 'valve_switch':
            self.action_dropdown.options = [('Switch Position', 'switch')]
            self.action_dropdown.value = 'switch'
        elif template_key == 'wait':
            self.action_dropdown.options = [('Wait', 'wait')]
            self.action_dropdown.value = 'wait'
        
        self._update_parameter_inputs()
    
    def _show_templates(self, button):
        """Show template information"""
        template_key = self.template_dropdown.value
        if template_key:
            template = self.procedure_templates[template_key]
            print(f"📋 Template: {template['name']}")
            print(f"Description: {template['description']}")
            print(f"Parameters: {', '.join(template['parameters'])}")
            print(f"Applicable to: {', '.join(template['applicable_components'])}")
    
    def _add_procedure(self, button):
        """Add procedure to protocol"""
        try:
            # Validate inputs
            component = self.component_dropdown.value
            if not component:
                print("❌ Please select a component")
                return
            
            action = self.action_dropdown.value
            if not action:
                print("❌ Please select an action")
                return
            
            start_time = self.start_time_input.value.strip()
            if not start_time:
                print("❌ Please specify start time")
                return
            
            # Collect parameters
            parameters = {}
            for param_name, widget in self.parameter_widgets.items():
                value = widget.value.strip()
                if value:
                    parameters[param_name] = value
            
            # Build procedure
            procedure = {
                'component': component,
                'action': action,
                'start_time': start_time,
                'parameters': parameters
            }
            
            # Add duration for actions that need it
            duration = self.duration_input.value.strip()
            if duration and action in ['run', 'wait']:
                procedure['duration'] = duration
            elif action in ['run', 'wait'] and not duration:
                print("❌ Duration required for this action")
                return
            
            # Validate procedure
            validation_errors = self._validate_procedure(procedure)
            if validation_errors:
                print("❌ Procedure validation errors:")
                for error in validation_errors:
                    print(f"  • {error}")
                return
            
            # Add to parent GUI (this would be called by the parent)
            print(f"✅ Procedure added: {component} {action} at {start_time}")
            
            # Return procedure for parent to handle
            return procedure
            
        except Exception as e:
            print(f"❌ Error adding procedure: {e}")
            return None
    
    def _validate_procedure(self, procedure: Dict[str, Any]) -> List[str]:
        """Validate procedure configuration"""
        errors = []
        
        component = procedure.get('component')
        action = procedure.get('action')
        parameters = procedure.get('parameters', {})
        
        # Component validation
        if component != 'Timer':
            component_type = self._get_component_type(component)
            if component_type == 'Unknown':
                errors.append(f"Unknown component: {component}")
        
        # Action-specific validation
        if action == 'run':
            if 'rate' not in parameters:
                errors.append("Flow rate required for pump run")
            elif not self._validate_flow_rate(parameters['rate']):
                errors.append("Invalid flow rate format")
        
        elif action == 'switch':
            if 'position' not in parameters:
                errors.append("Position required for valve switch")
        
        elif action == 'set_temperature':
            if 'temperature' not in parameters:
                errors.append("Temperature required for temperature set")
        
        # Time validation
        start_time = procedure.get('start_time')
        if not self._validate_time_format(start_time):
            errors.append("Invalid start time format")
        
        duration = procedure.get('duration')
        if duration and not self._validate_time_format(duration):
            errors.append("Invalid duration format")
        
        return errors
    
    def _validate_flow_rate(self, rate_str: str) -> bool:
        """Validate flow rate format"""
        try:
            # Should contain number and unit
            rate_str = rate_str.strip().lower()
            
            # Common patterns: "5 ml/min", "2.5mL/min", "10 μL/min"
            import re
            pattern = r'^\d+\.?\d*\s*(ml|μl|ul|nl)/min$'
            return bool(re.match(pattern, rate_str))
            
        except:
            return False
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format"""
        try:
            if not time_str:
                return False
            
            time_str = time_str.strip().lower()
            
            # Common patterns: "5s", "10min", "1h", "2.5min"
            import re
            pattern = r'^\d+\.?\d*\s*(s|sec|min|h|hr)$'
            return bool(re.match(pattern, time_str))
            
        except:
            return False
    
    def create_interface(self) -> widgets.Widget:
        """Create the procedure builder interface"""
        
        # Component and action selection
        selection_row1 = widgets.HBox([
            self.component_dropdown,
            self.action_dropdown
        ])
        
        # Timing inputs
        timing_row = widgets.HBox([
            self.start_time_input,
            self.duration_input
        ])
        
        # Template selection
        template_row = widgets.HBox([
            self.template_dropdown,
            self.template_button
        ])
        
        # Configuration section
        config_section = widgets.VBox([
            widgets.HTML("<h5>Procedure Configuration</h5>"),
            selection_row1,
            timing_row,
            widgets.HTML("<h6>Parameters:</h6>"),
            self.parameter_container
        ])
        
        # Template section
        template_section = widgets.VBox([
            widgets.HTML("<h5>Quick Templates</h5>"),
            template_row
        ])
        
        # Left panel
        left_panel = widgets.VBox([
            config_section,
            template_section,
            self.add_procedure_button
        ], layout=widgets.Layout(width='400px', padding='10px'))
        
        # Instructions panel
        instructions = widgets.HTML("""
        <div style='background: #f5f5f5; padding: 15px; border-radius: 8px;'>
            <h5>Instructions:</h5>
            <ol style='margin-bottom: 0; padding-left: 20px;'>
                <li>Select component and action</li>
                <li>Set start time and duration</li>
                <li>Configure parameters</li>
                <li>Click "Add Procedure"</li>
            </ol>
            <br>
            <h6>Time Format Examples:</h6>
            <ul style='margin-bottom: 0; padding-left: 20px;'>
                <li>5s, 30s (seconds)</li>
                <li>2min, 10min (minutes)</li>
                <li>1h, 2.5h (hours)</li>
            </ul>
        </div>
        """)
        
        right_panel = widgets.VBox([
            instructions
        ], layout=widgets.Layout(width='300px', padding='10px'))
        
        return widgets.HBox([left_panel, right_panel])