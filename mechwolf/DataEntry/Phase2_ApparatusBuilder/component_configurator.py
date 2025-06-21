"""
Component Configurator

Interface for configuring passive components (vessels, tubes, mixers, etc.)
that integrates with the experimental metadata system.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, List, Optional
import traceback


class ComponentConfigurator:
    """Component configuration interface for passive apparatus components"""
    
    def __init__(self, experiment_manager):
        """
        Initialize component configurator
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        
        # Component type definitions
        self.component_types = {
            'Vessel': {
                'name': 'Vessel',
                'description': 'Container for reagents or products',
                'parameters': ['description', 'volume', 'material'],
                'defaults': {'material': 'Glass', 'volume': '50 mL'}
            },
            'Tube': {
                'name': 'Tube',
                'description': 'Connecting tubing',
                'parameters': ['length', 'ID', 'OD', 'material'],
                'defaults': {'material': 'PFA', 'length': '1 ft', 'ID': '1/16 in', 'OD': '1/8 in'}
            },
            'TMixer': {
                'name': 'T-Mixer',
                'description': 'T-shaped mixing junction',
                'parameters': ['material', 'ID'],
                'defaults': {'material': 'PEEK', 'ID': '1/16 in'}
            },
            'CrossMixer': {
                'name': 'Cross Mixer',
                'description': 'Four-way mixing junction',
                'parameters': ['material', 'ID'],
                'defaults': {'material': 'PEEK', 'ID': '1/16 in'}
            },
            'YMixer': {
                'name': 'Y-Mixer',
                'description': 'Y-shaped mixing junction',
                'parameters': ['material', 'ID'],
                'defaults': {'material': 'PEEK', 'ID': '1/16 in'}
            },
            'Reactor': {
                'name': 'Reactor',
                'description': 'Reaction vessel or coil',
                'parameters': ['volume', 'material', 'temperature_range'],
                'defaults': {'material': 'Stainless Steel', 'volume': '10 mL'}
            },
            'Sensor': {
                'name': 'Sensor',
                'description': 'Measurement sensor',
                'parameters': ['sensor_type', 'measurement_range'],
                'defaults': {'sensor_type': 'Temperature'}
            }
        }
        
        # Material options
        self.materials = {
            'tubes': ['PFA', 'PTFE', 'FEP', 'Stainless Steel', 'Glass', 'PEEK'],
            'vessels': ['Glass', 'Stainless Steel', 'PTFE', 'Plastic'],
            'mixers': ['PEEK', 'Stainless Steel', 'Glass', 'PTFE'],
            'reactors': ['Stainless Steel', 'Glass', 'PTFE', 'Hastelloy']
        }
        
        # Size options
        self.tube_sizes = {
            'ID': ['0.010 in', '0.020 in', '0.030 in', '1/32 in', '1/16 in', '1/8 in', '1/4 in'],
            'OD': ['1/32 in', '1/16 in', '1/8 in', '1/4 in', '3/8 in', '1/2 in'],
            'length': ['6 in', '1 ft', '2 ft', '3 ft', '5 ft', '10 ft']
        }
        
        self.volumes = ['1 mL', '5 mL', '10 mL', '25 mL', '50 mL', '100 mL', '250 mL', '500 mL', '1 L']
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create component configuration widgets"""
        
        # Component type selection
        self.component_type_dropdown = widgets.Dropdown(
            options=[(info['name'], key) for key, info in self.component_types.items()],
            description='Type:',
            layout=widgets.Layout(width='250px')
        )
        self.component_type_dropdown.observe(self._on_component_type_change, names='value')
        
        self.component_name_input = widgets.Text(
            placeholder='Enter component name',
            description='Name:',
            layout=widgets.Layout(width='300px')
        )
        
        # Description display
        self.type_description = widgets.HTML()
        
        # Dynamic parameter inputs
        self.parameter_container = widgets.VBox()
        self.parameter_widgets = {}
        
        # Action buttons
        self.add_component_button = widgets.Button(
            description='➕ Add Component',
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        self.add_component_button.on_click(self._add_component)
        
        self.clear_form_button = widgets.Button(
            description='🗑️ Clear Form',
            button_style='',
            layout=widgets.Layout(width='130px')
        )
        self.clear_form_button.on_click(self._clear_form)
        
        # Current components display
        self.components_display = widgets.Output(
            layout=widgets.Layout(
                height='350px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Initialize
        self._on_component_type_change({'new': self.component_type_dropdown.value})
        self._refresh_components_display()
    
    def _on_component_type_change(self, change):
        """Handle component type change"""
        component_type = change['new']
        component_info = self.component_types[component_type]
        
        # Update description
        self.type_description.value = f"<i>{component_info['description']}</i>"
        
        # Clear previous parameter widgets
        self.parameter_widgets.clear()
        
        # Create parameter inputs
        parameter_widgets = []
        
        for param in component_info['parameters']:
            widget = self._create_parameter_widget(param, component_type, component_info)
            if widget:
                self.parameter_widgets[param] = widget
                parameter_widgets.append(widget)
        
        # Update parameter container
        self.parameter_container.children = parameter_widgets
    
    def _create_parameter_widget(self, param: str, component_type: str, component_info: Dict[str, Any]):
        """Create widget for a specific parameter"""
        defaults = component_info.get('defaults', {})
        
        if param == 'description':
            return widgets.Text(
                placeholder='Enter description',
                description='Description:',
                layout=widgets.Layout(width='400px')
            )
        
        elif param == 'material':
            # Get material options based on component type
            if component_type == 'Tube':
                options = self.materials['tubes']
            elif component_type == 'Vessel':
                options = self.materials['vessels']
            elif component_type in ['TMixer', 'CrossMixer', 'YMixer']:
                options = self.materials['mixers']
            elif component_type == 'Reactor':
                options = self.materials['reactors']
            else:
                options = ['Glass', 'Stainless Steel', 'PTFE', 'PEEK']
            
            return widgets.Dropdown(
                options=options,
                value=defaults.get(param, options[0]),
                description='Material:',
                layout=widgets.Layout(width='200px')
            )
        
        elif param == 'volume':
            return widgets.Dropdown(
                options=self.volumes,
                value=defaults.get(param, '10 mL'),
                description='Volume:',
                layout=widgets.Layout(width='150px')
            )
        
        elif param == 'length':
            return widgets.Dropdown(
                options=self.tube_sizes['length'],
                value=defaults.get(param, '1 ft'),
                description='Length:',
                layout=widgets.Layout(width='150px')
            )
        
        elif param == 'ID':
            return widgets.Dropdown(
                options=self.tube_sizes['ID'],
                value=defaults.get(param, '1/16 in'),
                description='Inner Diameter:',
                layout=widgets.Layout(width='180px')
            )
        
        elif param == 'OD':
            return widgets.Dropdown(
                options=self.tube_sizes['OD'],
                value=defaults.get(param, '1/8 in'),
                description='Outer Diameter:',
                layout=widgets.Layout(width='180px')
            )
        
        elif param == 'sensor_type':
            return widgets.Dropdown(
                options=['Temperature', 'Pressure', 'Flow Rate', 'pH', 'Conductivity'],
                value='Temperature',
                description='Sensor Type:',
                layout=widgets.Layout(width='200px')
            )
        
        elif param == 'temperature_range':
            return widgets.Text(
                placeholder='e.g., -10°C to 200°C',
                description='Temp Range:',
                layout=widgets.Layout(width='250px')
            )
        
        elif param == 'measurement_range':
            return widgets.Text(
                placeholder='e.g., 0-100°C',
                description='Range:',
                layout=widgets.Layout(width='200px')
            )
        
        else:
            # Generic text input
            return widgets.Text(
                value=defaults.get(param, ''),
                description=f'{param.replace("_", " ").title()}:',
                layout=widgets.Layout(width='250px')
            )
    
    def _add_component(self, button):
        """Add configured component"""
        try:
            # Validate inputs
            component_name = self.component_name_input.value.strip()
            if not component_name:
                print("❌ Please enter a component name")
                return
            
            # Check for duplicate names
            existing_components = self.experiment.apparatus.get_data().get('components', {})
            all_existing = (existing_components.get('active', []) + 
                          existing_components.get('passive', []))
            
            if any(comp.get('name') == component_name for comp in all_existing):
                print(f"❌ Component '{component_name}' already exists")
                return
            
            component_type = self.component_type_dropdown.value
            
            # Collect parameters
            parameters = {}
            for param, widget in self.parameter_widgets.items():
                value = widget.value
                if value:  # Only include non-empty values
                    parameters[param] = value
            
            # Create component configuration
            component_config = {
                'type': component_type,
                'name': component_name,
                'parameters': parameters
            }
            
            # Validate configuration
            validation_errors = self._validate_component_config(component_config)
            if validation_errors:
                print("❌ Validation errors:")
                for error in validation_errors:
                    print(f"  • {error}")
                return
            
            # Add to experimental metadata
            success = self.experiment.apparatus.add_passive_component(component_config)
            
            if success:
                self.experiment.save()
                self._clear_form()
                self._refresh_components_display()
                print(f"✅ Added component '{component_name}' successfully")
            else:
                print("❌ Failed to add component")
            
        except Exception as e:
            print(f"❌ Error adding component: {e}")
            traceback.print_exc()
    
    def _validate_component_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate component configuration"""
        errors = []
        
        component_type = config.get('type')
        parameters = config.get('parameters', {})
        
        # Type-specific validation
        if component_type == 'Vessel':
            if not parameters.get('description'):
                errors.append("Description is required for vessels")
        
        elif component_type == 'Tube':
            required = ['length', 'ID', 'OD', 'material']
            for param in required:
                if not parameters.get(param):
                    errors.append(f"{param.replace('_', ' ').title()} is required for tubes")
        
        elif component_type in ['TMixer', 'CrossMixer', 'YMixer']:
            if not parameters.get('material'):
                errors.append("Material is required for mixers")
        
        # Name validation
        name = config.get('name', '').strip()
        if len(name) < 2:
            errors.append("Component name must be at least 2 characters")
        elif len(name) > 50:
            errors.append("Component name must be less than 50 characters")
        
        return errors
    
    def _clear_form(self, button=None):
        """Clear form inputs"""
        self.component_name_input.value = ''
        
        # Reset parameter widgets to defaults
        component_type = self.component_type_dropdown.value
        component_info = self.component_types[component_type]
        defaults = component_info.get('defaults', {})
        
        for param, widget in self.parameter_widgets.items():
            if hasattr(widget, 'options') and isinstance(widget, widgets.Dropdown):
                # Reset dropdown to default or first option
                if param in defaults and defaults[param] in widget.options:
                    widget.value = defaults[param]
                else:
                    widget.value = widget.options[0]
            else:
                # Reset text input
                widget.value = defaults.get(param, '')
    
    def _refresh_components_display(self):
        """Refresh the components display"""
        with self.components_display:
            clear_output(wait=True)
            
            apparatus_data = self.experiment.apparatus.get_data()
            passive_components = apparatus_data.get('components', {}).get('passive', [])
            
            if not passive_components:
                print("No passive components configured yet.")
                return
            
            print("📦 PASSIVE COMPONENTS")
            print("=" * 50)
            
            for i, component in enumerate(passive_components):
                name = component.get('name', 'Unknown')
                comp_type = component.get('type', 'Unknown')
                parameters = component.get('parameters', {})
                
                print(f"{i + 1}. {name} ({comp_type})")
                
                # Display key parameters
                if comp_type == 'Vessel':
                    desc = parameters.get('description', 'No description')
                    volume = parameters.get('volume', 'N/A')
                    material = parameters.get('material', 'N/A')
                    print(f"   Description: {desc}")
                    print(f"   Volume: {volume} | Material: {material}")
                
                elif comp_type == 'Tube':
                    length = parameters.get('length', 'N/A')
                    id_val = parameters.get('ID', 'N/A')
                    od_val = parameters.get('OD', 'N/A')
                    material = parameters.get('material', 'N/A')
                    print(f"   Length: {length} | ID: {id_val} | OD: {od_val}")
                    print(f"   Material: {material}")
                
                elif comp_type in ['TMixer', 'CrossMixer', 'YMixer']:
                    material = parameters.get('material', 'N/A')
                    id_val = parameters.get('ID', 'N/A')
                    print(f"   Material: {material} | ID: {id_val}")
                
                elif comp_type == 'Reactor':
                    volume = parameters.get('volume', 'N/A')
                    material = parameters.get('material', 'N/A')
                    temp_range = parameters.get('temperature_range', 'N/A')
                    print(f"   Volume: {volume} | Material: {material}")
                    if temp_range != 'N/A':
                        print(f"   Temperature Range: {temp_range}")
                
                elif comp_type == 'Sensor':
                    sensor_type = parameters.get('sensor_type', 'N/A')
                    measurement_range = parameters.get('measurement_range', 'N/A')
                    print(f"   Type: {sensor_type}")
                    if measurement_range != 'N/A':
                        print(f"   Range: {measurement_range}")
                
                print()
    
    def get_components(self) -> List[Dict[str, Any]]:
        """Get current passive components"""
        apparatus_data = self.experiment.apparatus.get_data()
        return apparatus_data.get('components', {}).get('passive', [])
    
    def create_interface(self) -> widgets.Widget:
        """Create the component configurator interface"""
        
        # Configuration section
        config_section = widgets.VBox([
            widgets.HTML("<h4>Component Configuration</h4>"),
            self.component_type_dropdown,
            self.type_description,
            self.component_name_input,
            widgets.HTML("<h5>Parameters:</h5>"),
            self.parameter_container
        ])
        
        # Action buttons
        button_row = widgets.HBox([
            self.add_component_button,
            self.clear_form_button
        ])
        
        # Left panel: Configuration
        left_panel = widgets.VBox([
            config_section,
            button_row
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        # Right panel: Current components
        right_panel = widgets.VBox([
            widgets.HTML("<h4>Configured Components</h4>"),
            self.components_display
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        return widgets.HBox([left_panel, right_panel])