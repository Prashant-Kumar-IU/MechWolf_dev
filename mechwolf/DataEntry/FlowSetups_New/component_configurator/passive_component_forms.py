"""
Passive Component Forms - Configuration forms for vessels, tubes, mixers, etc.

This module provides specialized forms for configuring passive components
with appropriate validation and preset options.
"""
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, Optional, Type, List
import re


class PassiveComponentForms:
    """Handles configuration forms for passive components"""
    
    def __init__(self, parent_selector):
        self.parent = parent_selector
        self.current_form = None
        self.editing_component_id = None
        
        # Tube presets matching the user's example
        self.tube_presets = {
            'fat_tube': {
                'ID': '1/16 in',
                'OD': '1/8 in', 
                'material': 'PFA',
                'description': 'Fat tube preset'
            },
            'thin_tube': {
                'ID': '0.030 in',
                'OD': '1/16 in',
                'material': 'PFA', 
                'description': 'Thin tube preset'
            },
            'thinner_tube': {
                'ID': '0.020 in',
                'OD': '1/16 in',
                'material': 'PFA',
                'description': 'Thinner tube preset'
            },
            'custom': {
                'ID': '',
                'OD': '',
                'material': 'PFA',
                'description': 'Custom tube configuration'
            }
        }
    
    def show_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show the appropriate form for the component type"""
        
        self.editing_component_id = None
        if existing_data:
            # Find the component ID if editing
            for comp_id, comp_data in self.parent.configured_components.items():
                if comp_data == existing_data:
                    self.editing_component_id = comp_id
                    break
        
        # Route to appropriate form based on component type
        if component_type == 'Vessel':
            self._show_vessel_form(component_type, component_class, existing_data)
        elif component_type == 'Tube':
            self._show_tube_form(component_type, component_class, existing_data)
        elif 'Mixer' in component_type:
            self._show_mixer_form(component_type, component_class, existing_data)
        else:
            self._show_generic_passive_form(component_type, component_class, existing_data)
    
    def _show_vessel_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show vessel configuration form"""
        
        # Header
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #9c27b0 0%, #ba68c8 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>🧪 Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure vessel name and contents description</p>
            </div>
        """)
        
        # Form fields
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter vessel name (e.g., THF, SM, Product)',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='300px')
        )
        
        description_field = widgets.Textarea(
            value=existing_data.get('description', '') if existing_data else '',
            placeholder='Describe vessel contents (e.g., Tetrahydrofuran, Starting_material_and_tbutanol_THF)',
            description='Description:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px', height='100px')
        )
        
        # Helper text
        helper_text = widgets.HTML("""
            <div style='color: #666; font-size: 12px; margin: 10px 0;'>
                💡 <strong>Tips:</strong><br>
                • Name should be short and unique (used as Python variable)<br>
                • Description can be detailed and include chemical information<br>
                • Examples: THF → "Tetrahydrofuran", Product → "Reaction product vessel"
            </div>
        """)
        
        # Validation display
        validation_output = widgets.Output()
        
        # Action buttons
        save_btn = widgets.Button(
            description='Save Vessel',
            button_style='success',
            icon='check',
            layout=widgets.Layout(width='150px')
        )
        
        cancel_btn = widgets.Button(
            description='Cancel',
            button_style='',
            icon='times',
            layout=widgets.Layout(width='100px')
        )
        
        # Event handlers
        def save_component(b):
            with validation_output:
                clear_output()
                
                component_data = {
                    'type': component_type,
                    'category': 'passive',
                    'name': name_field.value.strip(),
                    'description': description_field.value.strip(),
                }
                
                # Validate
                errors = self._validate_vessel_data(component_data)
                if errors:
                    print("❌ Validation Errors:")
                    for error in errors:
                        print(f"  • {error}")
                    return
                
                # Save component
                if self.editing_component_id:
                    self.parent.configured_components[self.editing_component_id] = component_data
                    self.parent._update_component_display()
                    if self.parent.data_manager:
                        self.parent._save_components()
                else:
                    self.parent.add_configured_component(component_data)
                
                print("✅ Vessel saved successfully!")
                
                # Return to main interface
                import time
                time.sleep(1)
                self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(lambda b: self.parent.return_to_main())
        
        # Layout
        form_container = widgets.VBox([
            widgets.HTML("<h4>Vessel Information</h4>"),
            name_field,
            description_field,
            helper_text,
            widgets.HTML("<br>"),
            widgets.HBox([save_btn, cancel_btn]),
            validation_output
        ], layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_tube_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show tube configuration form with presets"""
        
        # Header
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #607d8b 0%, #90a4ae 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>🔗 Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure tube dimensions and material properties</p>
            </div>
        """)
        
        # Preset selector
        preset_selector = widgets.Dropdown(
            options=[
                ('Fat Tube (1/16" ID, 1/8" OD)', 'fat_tube'),
                ('Thin Tube (0.030" ID, 1/16" OD)', 'thin_tube'),
                ('Thinner Tube (0.020" ID, 1/16" OD)', 'thinner_tube'),
                ('Custom Configuration', 'custom')
            ],
            value='fat_tube',
            description='Preset:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='350px')
        )
        
        # Form fields
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter tube name (e.g., valve_tube, connection_tube)',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='300px')
        )
        
        length_field = widgets.Text(
            value=existing_data.get('length', '') if existing_data else '',
            placeholder='e.g., 1 ft, 12 cm, 0.5 m',
            description='Length:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='200px')
        )
        
        id_field = widgets.Text(
            description='Inner Diameter:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='200px')
        )
        
        od_field = widgets.Text(
            description='Outer Diameter:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='200px')
        )
        
        material_field = widgets.Dropdown(
            options=['PFA', 'PTFE', 'Stainless Steel', 'PEEK', 'FEP'],
            value='PFA',
            description='Material:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='200px')
        )
        
        # Update fields when preset changes
        def update_preset(change):
            preset = self.tube_presets[change['new']]
            id_field.value = preset['ID']
            od_field.value = preset['OD']
            material_field.value = preset['material']
            
            # Enable/disable fields for custom preset
            custom_mode = change['new'] == 'custom'
            id_field.disabled = not custom_mode
            od_field.disabled = not custom_mode
            material_field.disabled = not custom_mode
        
        preset_selector.observe(update_preset, names='value')
        
        # Initialize with existing data or default preset
        if existing_data:
            # Try to match existing data to a preset
            preset_match = None
            for preset_name, preset_data in self.tube_presets.items():
                if (existing_data.get('ID') == preset_data['ID'] and 
                    existing_data.get('OD') == preset_data['OD'] and
                    existing_data.get('material') == preset_data['material']):
                    preset_match = preset_name
                    break
            
            if preset_match:
                preset_selector.value = preset_match
            else:
                preset_selector.value = 'custom'
            
            id_field.value = existing_data.get('ID', '')
            od_field.value = existing_data.get('OD', '')
            material_field.value = existing_data.get('material', 'PFA')
        else:
            # Set initial preset
            update_preset({'new': 'fat_tube'})
        
        # Validation display
        validation_output = widgets.Output()
        
        # Action buttons
        save_btn = widgets.Button(
            description='Save Tube',
            button_style='success',
            icon='check',
            layout=widgets.Layout(width='150px')
        )
        
        cancel_btn = widgets.Button(
            description='Cancel',
            button_style='',
            icon='times',
            layout=widgets.Layout(width='100px')
        )
        
        # Event handlers
        def save_component(b):
            with validation_output:
                clear_output()
                
                component_data = {
                    'type': component_type,
                    'category': 'passive',
                    'name': name_field.value.strip(),
                    'length': length_field.value.strip(),
                    'ID': id_field.value.strip(),
                    'OD': od_field.value.strip(),
                    'material': material_field.value,
                    'preset': preset_selector.value
                }
                
                # Validate
                errors = self._validate_tube_data(component_data)
                if errors:
                    print("❌ Validation Errors:")
                    for error in errors:
                        print(f"  • {error}")
                    return
                
                # Save component
                if self.editing_component_id:
                    self.parent.configured_components[self.editing_component_id] = component_data
                    self.parent._update_component_display()
                    if self.parent.data_manager:
                        self.parent._save_components()
                else:
                    self.parent.add_configured_component(component_data)
                
                print("✅ Tube saved successfully!")
                
                # Return to main interface
                import time
                time.sleep(1)
                self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(lambda b: self.parent.return_to_main())
        
        # Helper text
        helper_text = widgets.HTML("""
            <div style='color: #666; font-size: 12px; margin: 10px 0;'>
                💡 <strong>Tube Presets:</strong><br>
                • <strong>Fat Tube:</strong> General connections, high flow rate<br>
                • <strong>Thin Tube:</strong> Standard connections<br>
                • <strong>Thinner Tube:</strong> Precise flow control, lower volume<br>
                • <strong>Custom:</strong> Define your own specifications
            </div>
        """)
        
        # Layout
        form_container = widgets.VBox([
            widgets.HTML("<h4>Tube Configuration</h4>"),
            preset_selector,
            helper_text,
            widgets.HTML("<h4>Tube Properties</h4>"),
            name_field,
            length_field,
            id_field,
            od_field,
            material_field,
            widgets.HTML("<br>"),
            widgets.HBox([save_btn, cancel_btn]),
            validation_output
        ], layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_mixer_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show mixer configuration form"""
        
        # Header with mixer-specific styling
        mixer_colors = {
            'Mixer': '#4caf50',
            'TMixer': '#ff9800', 
            'CrossMixer': '#f44336',
            'YMixer': '#2196f3'
        }
        color = mixer_colors.get(component_type, '#9c27b0')
        
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, {color} 0%, {color}88 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>🌀 Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure mixer junction and mixing parameters</p>
            </div>
        """)
        
        # Form fields
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder=f'Enter {component_type.lower()} name (e.g., T_mixer, main_mixer)',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='300px')
        )
        
        # Description field for mixer purpose
        description_field = widgets.Textarea(
            value=existing_data.get('description', '') if existing_data else '',
            placeholder='Describe mixer purpose (optional)',
            description='Description:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px', height='80px')
        )
        
        # Mixer-specific info
        mixer_info = {
            'Mixer': 'Generic mixer component for fluid mixing',
            'TMixer': 'T-junction mixer - combines two fluid streams',
            'CrossMixer': 'Cross mixer - combines multiple streams with cross-flow',
            'YMixer': 'Y-junction mixer - merges two streams at an angle'
        }
        
        info_html = widgets.HTML(f"""
            <div style='background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <strong>{component_type} Info:</strong><br>
                {mixer_info.get(component_type, 'Mixer component for combining fluid streams')}
            </div>
        """)
        
        # Validation display
        validation_output = widgets.Output()
        
        # Action buttons
        save_btn = widgets.Button(
            description='Save Mixer',
            button_style='success',
            icon='check',
            layout=widgets.Layout(width='150px')
        )
        
        cancel_btn = widgets.Button(
            description='Cancel',
            button_style='',
            icon='times',
            layout=widgets.Layout(width='100px')
        )
        
        # Event handlers
        def save_component(b):
            with validation_output:
                clear_output()
                
                component_data = {
                    'type': component_type,
                    'category': 'passive',
                    'name': name_field.value.strip(),
                    'description': description_field.value.strip(),
                }
                
                # Validate
                errors = self._validate_mixer_data(component_data)
                if errors:
                    print("❌ Validation Errors:")
                    for error in errors:
                        print(f"  • {error}")
                    return
                
                # Save component
                if self.editing_component_id:
                    self.parent.configured_components[self.editing_component_id] = component_data
                    self.parent._update_component_display()
                    if self.parent.data_manager:
                        self.parent._save_components()
                else:
                    self.parent.add_configured_component(component_data)
                
                print("✅ Mixer saved successfully!")
                
                # Return to main interface
                import time
                time.sleep(1)
                self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(lambda b: self.parent.return_to_main())
        
        # Layout
        form_container = widgets.VBox([
            widgets.HTML("<h4>Mixer Configuration</h4>"),
            info_html,
            name_field,
            description_field,
            widgets.HTML("<br>"),
            widgets.HBox([save_btn, cancel_btn]),
            validation_output
        ], layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_generic_passive_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show generic form for unknown passive component types"""
        
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #795548 0%, #8d6e63 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>⚙️ Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure basic component parameters</p>
            </div>
        """)
        
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter component name',
            description='Name:',
            style={'description_width': '120px'}
        )
        
        # Save/cancel logic
        save_btn = widgets.Button(description='Save Component', button_style='success')
        cancel_btn = widgets.Button(description='Cancel', button_style='')
        
        def save_component(b):
            component_data = {
                'type': component_type,
                'category': 'passive',
                'name': name_field.value.strip(),
            }
            
            if self.editing_component_id:
                self.parent.configured_components[self.editing_component_id] = component_data
                self.parent._update_component_display()
                if self.parent.data_manager:
                    self.parent._save_components()
            else:
                self.parent.add_configured_component(component_data)
            
            self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(lambda b: self.parent.return_to_main())
        
        form_container = widgets.VBox([
            name_field,
            widgets.HBox([save_btn, cancel_btn])
        ], layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _validate_vessel_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate vessel configuration data"""
        errors = []
        
        # Name validation
        if not data.get('name'):
            errors.append("Name is required")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', data['name']):
            errors.append("Name must be a valid Python identifier (letters, numbers, underscore)")
        
        # Check for name conflicts
        for comp_id, comp_data in self.parent.configured_components.items():
            if (comp_id != self.editing_component_id and 
                comp_data.get('name') == data['name']):
                errors.append(f"Name '{data['name']}' is already used by another component")
        
        return errors
    
    def _validate_tube_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate tube configuration data"""
        errors = []
        
        # Name validation
        if not data.get('name'):
            errors.append("Name is required")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', data['name']):
            errors.append("Name must be a valid Python identifier")
        
        # Length validation
        if not data.get('length'):
            errors.append("Length is required")
        elif not re.match(r'^\d+(\.\d+)?\s*(ft|in|cm|mm|m)$', data['length']):
            errors.append("Length must include units (e.g., '1 ft', '12 cm')")
        
        # Diameter validation (only for custom tubes)
        if data.get('preset') == 'custom':
            if not data.get('ID'):
                errors.append("Inner diameter is required for custom tubes")
            if not data.get('OD'):
                errors.append("Outer diameter is required for custom tubes")
        
        # Check for name conflicts
        for comp_id, comp_data in self.parent.configured_components.items():
            if (comp_id != self.editing_component_id and 
                comp_data.get('name') == data['name']):
                errors.append(f"Name '{data['name']}' is already used by another component")
        
        return errors
    
    def _validate_mixer_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate mixer configuration data"""
        errors = []
        
        # Name validation
        if not data.get('name'):
            errors.append("Name is required")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', data['name']):
            errors.append("Name must be a valid Python identifier")
        
        # Check for name conflicts
        for comp_id, comp_data in self.parent.configured_components.items():
            if (comp_id != self.editing_component_id and 
                comp_data.get('name') == data['name']):
                errors.append(f"Name '{data['name']}' is already used by another component")
        
        return errors