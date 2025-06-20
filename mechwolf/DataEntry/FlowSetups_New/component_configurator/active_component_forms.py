"""
Active Component Forms - Configuration forms for pumps, valves, sensors, etc.

This module provides specialized forms for configuring active components
with appropriate validation and user guidance.
"""
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, Optional, Type, List
import re


class ActiveComponentForms:
    """Handles configuration forms for active components"""
    
    def __init__(self, parent_selector):
        self.parent = parent_selector
        self.current_form = None
        self.editing_component_id = None
    
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
        if 'Pump' in component_type:
            self._show_pump_form(component_type, component_class, existing_data)
        elif 'Valve' in component_type:
            self._show_valve_form(component_type, component_class, existing_data)
        elif 'Sensor' in component_type:
            self._show_sensor_form(component_type, component_class, existing_data)
        elif 'TempControl' in component_type:
            self._show_temp_control_form(component_type, component_class, existing_data)
        else:
            self._show_generic_active_form(component_type, component_class, existing_data)
    
    def _show_pump_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show pump configuration form"""
        
        # Header
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>⚡ Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure pump parameters and serial connection</p>
            </div>
        """)
        
        # Form fields
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter pump name (e.g., Li_activator_pump)',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='300px')
        )
        
        serial_port_field = widgets.Text(
            value=existing_data.get('serial_port', '') if existing_data else '',
            placeholder='/dev/serial/by-id/...',
            description='Serial Port:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        # Serial port helper
        serial_help = widgets.HTML("""
            <div style='color: #666; font-size: 12px; margin-left: 120px;'>
                💡 Use full device path for reliable connection<br>
                Example: /dev/serial/by-id/usb-FTDI_USB-RS422_Cable_FT1UIC5M-if00-port0
            </div>
        """)
        
        # Component-specific fields
        if component_type == 'HarvardSyringePump':
            syringe_volume_field = widgets.Text(
                value=existing_data.get('syringe_volume', '') if existing_data else '',
                placeholder='e.g., 3 mL',
                description='Syringe Volume:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            syringe_diameter_field = widgets.Text(
                value=existing_data.get('syringe_diameter', '') if existing_data else '',
                placeholder='e.g., 10 mm',
                description='Syringe Diameter:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            specific_fields = [syringe_volume_field, syringe_diameter_field]
            
        elif 'Varian' in component_type:
            max_rate_field = widgets.Text(
                value=existing_data.get('max_rate', '') if existing_data else '',
                placeholder='e.g., 25mL/min',
                description='Max Rate:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            specific_fields = [max_rate_field]
            
        elif component_type == 'FreeStepPump':
            mcu_id_field = widgets.Text(
                value=existing_data.get('mcu_id', '') if existing_data else '',
                placeholder='MCU profile ID',
                description='MCU ID:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            motor_id_field = widgets.Text(
                value=existing_data.get('motor_id', '') if existing_data else '',
                placeholder='Motor profile ID',
                description='Motor ID:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            syringe_volume_field = widgets.Text(
                value=existing_data.get('syringe_volume', '') if existing_data else '',
                placeholder='e.g., 5 mL',
                description='Syringe Volume:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            syringe_diameter_field = widgets.Text(
                value=existing_data.get('syringe_diameter', '') if existing_data else '',
                placeholder='e.g., 12 mm',
                description='Syringe Diameter:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='200px')
            )
            
            specific_fields = [mcu_id_field, motor_id_field, syringe_volume_field, syringe_diameter_field]
        else:
            specific_fields = []
        
        # Validation display
        validation_output = widgets.Output()
        
        # Action buttons
        save_btn = widgets.Button(
            description='Save Component',
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
                
                # Collect form data
                component_data = {
                    'type': component_type,
                    'category': 'active_contrib' if component_type in self.parent.component_types['active_contrib'] else 'active_stdlib',
                    'name': name_field.value.strip(),
                    'serial_port': serial_port_field.value.strip(),
                }
                
                # Add component-specific fields
                if component_type == 'HarvardSyringePump':
                    component_data.update({
                        'syringe_volume': syringe_volume_field.value.strip(),
                        'syringe_diameter': syringe_diameter_field.value.strip(),
                    })
                elif 'Varian' in component_type:
                    component_data['max_rate'] = max_rate_field.value.strip()
                elif component_type == 'FreeStepPump':
                    component_data.update({
                        'mcu_id': mcu_id_field.value.strip(),
                        'motor_id': motor_id_field.value.strip(),
                        'syringe_volume': syringe_volume_field.value.strip(),
                        'syringe_diameter': syringe_diameter_field.value.strip(),
                    })
                
                # Validate
                errors = self._validate_pump_data(component_data)
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
                
                print("✅ Component saved successfully!")
                
                # Return to main interface after short delay
                import time
                time.sleep(1)
                self.parent.return_to_main()
        
        def cancel_form(b):
            self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(cancel_form)
        
        # Layout
        form_fields = [
            widgets.HTML("<h4>Basic Information</h4>"),
            name_field,
            serial_port_field,
            serial_help,
        ]
        
        if specific_fields:
            form_fields.append(widgets.HTML("<h4>Component-Specific Parameters</h4>"))
            form_fields.extend(specific_fields)
        
        form_fields.extend([
            widgets.HTML("<br>"),
            widgets.HBox([save_btn, cancel_btn]),
            validation_output
        ])
        
        form_container = widgets.VBox(form_fields, layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_valve_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show valve configuration form"""
        
        # Header
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>🔄 Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure valve parameters and port mappings</p>
            </div>
        """)
        
        # Basic fields
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter valve name (e.g., reagent_valve)',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='300px')
        )
        
        serial_port_field = widgets.Text(
            value=existing_data.get('serial_port', '') if existing_data else '',
            placeholder='/dev/serial/by-id/...',
            description='Serial Port:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        # Mapping configuration
        mapping_html = widgets.HTML("<h4>Port Mapping</h4><p>Define which components connect to which valve ports:</p>")
        
        # Dynamic mapping fields
        mapping_container = widgets.VBox([])
        
        def add_mapping_field(vessel_name='', port_number=''):
            vessel_field = widgets.Text(
                value=vessel_name,
                placeholder='Vessel/Component name',
                layout=widgets.Layout(width='200px')
            )
            
            port_field = widgets.IntText(
                value=int(port_number) if port_number else 1,
                description='Port:',
                layout=widgets.Layout(width='100px')
            )
            
            remove_btn = widgets.Button(
                description='Remove',
                button_style='danger',
                layout=widgets.Layout(width='80px')
            )
            
            mapping_row = widgets.HBox([
                widgets.Label('Component:', layout=widgets.Layout(width='80px')),
                vessel_field,
                port_field,
                remove_btn
            ])
            
            def remove_mapping(b):
                mapping_container.children = [child for child in mapping_container.children if child != mapping_row]
            
            remove_btn.on_click(remove_mapping)
            
            mapping_container.children = mapping_container.children + (mapping_row,)
        
        # Load existing mappings
        if existing_data and 'mapping' in existing_data:
            for vessel, port in existing_data['mapping'].items():
                add_mapping_field(vessel, str(port))
        else:
            add_mapping_field()  # Start with one empty mapping
        
        add_mapping_btn = widgets.Button(
            description='Add Mapping',
            button_style='info',
            icon='plus'
        )
        add_mapping_btn.on_click(lambda b: add_mapping_field())
        
        # Validation display
        validation_output = widgets.Output()
        
        # Action buttons
        save_btn = widgets.Button(
            description='Save Component',
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
                
                # Collect mapping data
                mapping = {}
                for row in mapping_container.children:
                    vessel_field = row.children[1]  # vessel text field
                    port_field = row.children[2]    # port int field
                    
                    if vessel_field.value.strip():
                        mapping[vessel_field.value.strip()] = port_field.value
                
                component_data = {
                    'type': component_type,
                    'category': 'active_contrib',
                    'name': name_field.value.strip(),
                    'serial_port': serial_port_field.value.strip(),
                    'mapping': mapping
                }
                
                # Validate
                errors = self._validate_valve_data(component_data)
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
                
                print("✅ Component saved successfully!")
                
                # Return to main interface
                import time
                time.sleep(1)
                self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(lambda b: self.parent.return_to_main())
        
        # Layout
        form_container = widgets.VBox([
            widgets.HTML("<h4>Basic Information</h4>"),
            name_field,
            serial_port_field,
            mapping_html,
            mapping_container,
            add_mapping_btn,
            widgets.HTML("<br>"),
            widgets.HBox([save_btn, cancel_btn]),
            validation_output
        ], layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_sensor_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show sensor configuration form"""
        
        # Header
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #2196f3 0%, #64b5f6 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>📊 Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure sensor parameters and data collection settings</p>
            </div>
        """)
        
        # Form fields
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter sensor name',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='300px')
        )
        
        if component_type != 'Sensor':  # Generic stdlib sensor doesn't need serial port
            serial_port_field = widgets.Text(
                value=existing_data.get('serial_port', '') if existing_data else '',
                placeholder='/dev/serial/by-id/...',
                description='Serial Port:',
                style={'description_width': '120px'},
                layout=widgets.Layout(width='400px')
            )
        else:
            serial_port_field = None
        
        unit_field = widgets.Text(
            value=existing_data.get('unit', '') if existing_data else '',
            placeholder='e.g., pH, °C, bar',
            description='Unit:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='200px')
        )
        
        # Validation and buttons
        validation_output = widgets.Output()
        
        save_btn = widgets.Button(description='Save Component', button_style='success', icon='check')
        cancel_btn = widgets.Button(description='Cancel', button_style='', icon='times')
        
        def save_component(b):
            with validation_output:
                clear_output()
                
                component_data = {
                    'type': component_type,
                    'category': 'active_stdlib' if component_type == 'Sensor' else 'active_contrib',
                    'name': name_field.value.strip(),
                    'unit': unit_field.value.strip(),
                }
                
                if serial_port_field:
                    component_data['serial_port'] = serial_port_field.value.strip()
                
                # Validate
                errors = self._validate_sensor_data(component_data)
                if errors:
                    print("❌ Validation Errors:")
                    for error in errors:
                        print(f"  • {error}")
                    return
                
                # Save
                if self.editing_component_id:
                    self.parent.configured_components[self.editing_component_id] = component_data
                    self.parent._update_component_display()
                    if self.parent.data_manager:
                        self.parent._save_components()
                else:
                    self.parent.add_configured_component(component_data)
                
                print("✅ Component saved successfully!")
                import time
                time.sleep(1)
                self.parent.return_to_main()
        
        save_btn.on_click(save_component)
        cancel_btn.on_click(lambda b: self.parent.return_to_main())
        
        # Layout
        form_fields = [name_field]
        if serial_port_field:
            form_fields.append(serial_port_field)
        form_fields.extend([unit_field, widgets.HBox([save_btn, cancel_btn]), validation_output])
        
        form_container = widgets.VBox(form_fields, layout=widgets.Layout(padding='20px'))
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_temp_control_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show temperature control configuration form"""
        
        # Similar to sensor form but with temperature-specific fields
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #f44336 0%, #ef5350 100%); 
                        color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h3 style='margin: 0;'>🌡️ Configure {component_type}</h3>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Configure temperature control parameters</p>
            </div>
        """)
        
        # Basic implementation - can be expanded
        name_field = widgets.Text(
            value=existing_data.get('name', '') if existing_data else '',
            placeholder='Enter temperature controller name',
            description='Name:',
            style={'description_width': '120px'}
        )
        
        # Save/cancel buttons and validation
        validation_output = widgets.Output()
        save_btn = widgets.Button(description='Save Component', button_style='success')
        cancel_btn = widgets.Button(description='Cancel', button_style='')
        
        def save_component(b):
            component_data = {
                'type': component_type,
                'category': 'active_stdlib',
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
            widgets.HBox([save_btn, cancel_btn]),
            validation_output
        ], layout=widgets.Layout(padding='20px'))
        
        self.current_form = widgets.VBox([header, form_container])
        display(self.current_form)
    
    def _show_generic_active_form(self, component_type: str, component_class: Type, existing_data: Optional[Dict[str, Any]] = None):
        """Show generic form for unknown active component types"""
        
        header = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #9c27b0 0%, #ba68c8 100%); 
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
                'category': 'active_contrib',
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
    
    def _validate_pump_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate pump configuration data"""
        errors = []
        
        # Name validation
        if not data.get('name'):
            errors.append("Name is required")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', data['name']):
            errors.append("Name must be a valid Python identifier (letters, numbers, underscore)")
        
        # Serial port validation
        if not data.get('serial_port'):
            errors.append("Serial port is required")
        elif not data['serial_port'].startswith('/dev/') and not data['serial_port'].startswith('COM'):
            errors.append("Serial port should start with /dev/ (Linux/Mac) or COM (Windows)")
        
        # Component-specific validation
        if data['type'] == 'HarvardSyringePump':
            if not data.get('syringe_volume'):
                errors.append("Syringe volume is required")
            elif not re.match(r'^\d+(\.\d+)?\s*(mL|ml|ML|Ml)$', data['syringe_volume']):
                errors.append("Syringe volume must include units (e.g., '3 mL')")
                
            if not data.get('syringe_diameter'):
                errors.append("Syringe diameter is required")
            elif not re.match(r'^\d+(\.\d+)?\s*(mm|cm|in)$', data['syringe_diameter']):
                errors.append("Syringe diameter must include units (e.g., '10 mm')")
        
        elif 'Varian' in data['type']:
            if not data.get('max_rate'):
                errors.append("Max rate is required")
            elif not re.match(r'^\d+(\.\d+)?\s*(mL/min|ml/min)$', data['max_rate']):
                errors.append("Max rate must include units (e.g., '25mL/min')")
        
        return errors
    
    def _validate_valve_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate valve configuration data"""
        errors = []
        
        # Name validation
        if not data.get('name'):
            errors.append("Name is required")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', data['name']):
            errors.append("Name must be a valid Python identifier")
        
        # Serial port validation
        if not data.get('serial_port'):
            errors.append("Serial port is required")
        
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
                    errors.append(f"Port for {vessel} must be a positive integer")
        
        return errors
    
    def _validate_sensor_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate sensor configuration data"""
        errors = []
        
        if not data.get('name'):
            errors.append("Name is required")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', data['name']):
            errors.append("Name must be a valid Python identifier")
        
        if data.get('serial_port') and not (data['serial_port'].startswith('/dev/') or data['serial_port'].startswith('COM')):
            errors.append("Serial port should start with /dev/ or COM")
        
        return errors