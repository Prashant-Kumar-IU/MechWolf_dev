"""
Pump Configurator

Integrated pump configuration that replaces the separate Pump Code Generator notebook.
Provides visual interface for pump setup with automatic code generation.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, List, Optional, Tuple
import serial.tools.list_ports
import traceback


class PumpConfigurator:
    """Integrated pump configuration interface"""
    
    def __init__(self, experiment_manager):
        """
        Initialize pump configurator
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        self.pump_configs = {}  # {name: config_dict}
        self.pump_objects = {}  # {name: pump_object}
        
        # Pump type definitions
        self.pump_types = {
            'HarvardSyringePump': {
                'name': 'Harvard Syringe Pump',
                'parameters': ['syringe_volume', 'syringe_diameter', 'serial_port'],
                'defaults': {'syringe_volume': '10 mL', 'syringe_diameter': '10 mm'}
            },
            'VarianPump': {
                'name': 'Varian HPLC Pump',
                'parameters': ['serial_port', 'max_rate'],
                'defaults': {'max_rate': '25 mL/min'}
            },
            'FreeStepPump': {
                'name': 'FreeStep Syringe Pump',
                'parameters': ['MCU_ID', 'motor_ID', 'syringe_volume', 'syringe_diameter'],
                'defaults': {'MCU_ID': 'A', 'motor_ID': 1, 'syringe_volume': '10 mL', 'syringe_diameter': '11.99 mm'}
            }
        }
        
        # Syringe options
        self.syringe_volumes = [
            '1 mL', '3 mL', '5 mL', '10 mL', '20 mL', '30 mL', '50 mL', '100 mL'
        ]
        
        self.syringe_diameters = [
            '4.61 mm', '8.585 mm', '11.99 mm', '14.43 mm', '19.05 mm', '26.59 mm', '34.5 mm'
        ]
        
        self._create_widgets()
    
    def _validate_default_in_options(self, options, default_value, fallback_index=0):
        """
        Validate that default value exists in options list.
        Returns the default if valid, otherwise returns fallback option.
        """
        if default_value in options:
            return default_value
        else:
            print(f"⚠️ Warning: Default value '{default_value}' not in options {options}")
            print(f"💡 Using fallback: '{options[fallback_index]}'")
            return options[fallback_index]
    
    def _create_widgets(self):
        """Create pump configuration widgets"""
        
        # Pump selection
        self.pump_type_dropdown = widgets.Dropdown(
            options=[(info['name'], key) for key, info in self.pump_types.items()],
            description='Pump Type:',
            layout=widgets.Layout(width='300px')
        )
        self.pump_type_dropdown.observe(self._on_pump_type_change, names='value')
        
        self.pump_name_input = widgets.Text(
            placeholder='Enter pump name (e.g., pump_1)',
            description='Pump Name:',
            layout=widgets.Layout(width='300px')
        )
        
        # Dynamic parameter inputs
        self.parameter_container = widgets.VBox()
        self.parameter_widgets = {}
        
        # Serial port selection
        self.serial_port_dropdown = widgets.Dropdown(
            options=[],
            description='Serial Port:',
            layout=widgets.Layout(width='400px')
        )
        
        self.refresh_ports_button = widgets.Button(
            description='🔄 Refresh',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        self.refresh_ports_button.on_click(self._refresh_serial_ports)
        
        # Action buttons
        self.add_pump_button = widgets.Button(
            description='➕ Add Pump',
            button_style='success',
            layout=widgets.Layout(width='130px')
        )
        self.add_pump_button.on_click(self._add_pump)
        
        self.test_pump_button = widgets.Button(
            description='🧪 Test Connection',
            button_style='warning',
            layout=widgets.Layout(width='150px')
        )
        self.test_pump_button.on_click(self._test_selected_pump)
        
        # Current pumps display
        self.pumps_display = widgets.Output(
            layout=widgets.Layout(
                height='300px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Initialize
        self._on_pump_type_change({'new': self.pump_type_dropdown.value})
        self._refresh_serial_ports()
        self._refresh_pumps_display()
    
    def _on_pump_type_change(self, change):
        """Handle pump type change"""
        pump_type = change['new']
        pump_info = self.pump_types[pump_type]
        
        # Clear previous parameter widgets
        self.parameter_widgets.clear()
        
        # Create parameter inputs
        parameter_widgets = []
        
        for param in pump_info['parameters']:
            if param == 'serial_port':
                continue  # Handled separately
                
            if param == 'syringe_volume':
                default_val = pump_info['defaults'].get(param, self.syringe_volumes[3])
                validated_val = self._validate_default_in_options(self.syringe_volumes, default_val, 3)
                widget = widgets.Dropdown(
                    options=self.syringe_volumes,
                    value=validated_val,
                    description=f'{param.replace("_", " ").title()}:',
                    layout=widgets.Layout(width='200px')
                )
            elif param == 'syringe_diameter':
                default_val = pump_info['defaults'].get(param, self.syringe_diameters[3])
                validated_val = self._validate_default_in_options(self.syringe_diameters, default_val, 3)
                widget = widgets.Dropdown(
                    options=self.syringe_diameters,
                    value=validated_val,
                    description=f'{param.replace("_", " ").title()}:',
                    layout=widgets.Layout(width='200px')
                )
            elif param in ['MCU_ID']:
                mcu_options = ['A', 'B', 'C', 'D']
                default_val = pump_info['defaults'].get(param, 'A')
                validated_val = self._validate_default_in_options(mcu_options, default_val, 0)
                widget = widgets.Dropdown(
                    options=mcu_options,
                    value=validated_val,
                    description=f'{param}:',
                    layout=widgets.Layout(width='150px')
                )
            elif param in ['motor_ID']:
                widget = widgets.IntText(
                    value=pump_info['defaults'].get(param, 1),
                    description=f'{param}:',
                    layout=widgets.Layout(width='150px')
                )
            elif param == 'max_rate':
                widget = widgets.Text(
                    value=pump_info['defaults'].get(param, '10 mL/min'),
                    description='Max Rate:',
                    layout=widgets.Layout(width='200px')
                )
            else:
                widget = widgets.Text(
                    value=pump_info['defaults'].get(param, ''),
                    description=f'{param.replace("_", " ").title()}:',
                    layout=widgets.Layout(width='200px')
                )
            
            self.parameter_widgets[param] = widget
            parameter_widgets.append(widget)
        
        # Update parameter container
        self.parameter_container.children = parameter_widgets
    
    def _refresh_serial_ports(self, button=None):
        """Refresh available serial ports"""
        try:
            ports = self.scan_serial_ports()
            port_options = [('Select a port...', '')] + [(port, port) for port in ports]
            self.serial_port_dropdown.options = port_options
            
            if len(ports) > 0:
                self.serial_port_dropdown.value = ports[0]
                
        except Exception as e:
            print(f"Error refreshing ports: {e}")
    
    def scan_serial_ports(self) -> List[str]:
        """Scan for available serial ports"""
        try:
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except Exception as e:
            print(f"Error scanning serial ports: {e}")
            return []
    
    def _add_pump(self, button):
        """Add configured pump"""
        try:
            # Validate inputs
            pump_name = self.pump_name_input.value.strip()
            if not pump_name:
                print("❌ Please enter a pump name")
                return
                
            if pump_name in self.pump_configs:
                print(f"❌ Pump '{pump_name}' already exists")
                return
            
            pump_type = self.pump_type_dropdown.value
            serial_port = self.serial_port_dropdown.value
            
            if not serial_port:
                print("❌ Please select a serial port")
                return
            
            # Collect parameters
            parameters = {'serial_port': serial_port}
            for param, widget in self.parameter_widgets.items():
                parameters[param] = widget.value
            
            # Create pump configuration
            pump_config = {
                'type': pump_type,
                'name': pump_name,
                'parameters': parameters
            }
            
            # Validate configuration
            validation_errors = self._validate_pump_config(pump_config)
            if validation_errors:
                print("❌ Validation errors:")
                for error in validation_errors:
                    print(f"  • {error}")
                return
            
            # Add to configurations
            self.pump_configs[pump_name] = pump_config
            
            # Add to experimental metadata
            self.experiment.apparatus.add_active_component(pump_config)
            self.experiment.save()
            
            # Clear form
            self.pump_name_input.value = ''
            
            # Refresh display
            self._refresh_pumps_display()
            
            print(f"✅ Added pump '{pump_name}' successfully")
            
        except Exception as e:
            print(f"❌ Error adding pump: {e}")
            traceback.print_exc()
    
    def _validate_pump_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate pump configuration"""
        errors = []
        
        pump_type = config.get('type')
        parameters = config.get('parameters', {})
        
        # Type-specific validation
        if pump_type == 'HarvardSyringePump':
            if 'syringe_volume' not in parameters:
                errors.append("Syringe volume is required")
            if 'syringe_diameter' not in parameters:
                errors.append("Syringe diameter is required")
                
        elif pump_type == 'VarianPump':
            if 'max_rate' not in parameters:
                errors.append("Max rate is required")
                
        elif pump_type == 'FreeStepPump':
            if 'MCU_ID' not in parameters:
                errors.append("MCU ID is required")
            if 'motor_ID' not in parameters:
                errors.append("Motor ID is required")
        
        # Serial port validation
        if not parameters.get('serial_port'):
            errors.append("Serial port is required")
        
        return errors
    
    def _test_selected_pump(self, button):
        """Test connection to selected pump"""
        pump_name = self.pump_name_input.value.strip()
        if not pump_name or pump_name not in self.pump_configs:
            print("❌ Please add pump first or select existing pump")
            return
            
        config = self.pump_configs[pump_name]
        result = self._test_pump_connection(config)
        
        status = "✅" if result['success'] else "❌"
        print(f"{status} {pump_name}: {result['message']}")
    
    def _test_pump_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to a pump"""
        try:
            # This is a placeholder for actual pump testing
            # In practice, you would try to initialize and communicate with the pump
            serial_port = config['parameters'].get('serial_port')
            
            # Basic serial port availability check
            import serial
            try:
                ser = serial.Serial(serial_port, timeout=1)
                ser.close()
                return {'success': True, 'message': 'Serial port accessible'}
            except serial.SerialException:
                return {'success': False, 'message': 'Cannot access serial port'}
                
        except Exception as e:
            return {'success': False, 'message': f'Test failed: {e}'}
    
    def test_pumps(self) -> Dict[str, Dict[str, Any]]:
        """Test all configured pumps"""
        results = {}
        for pump_name, config in self.pump_configs.items():
            results[pump_name] = self._test_pump_connection(config)
        return results
    
    def _refresh_pumps_display(self):
        """Refresh the pumps display"""
        with self.pumps_display:
            clear_output(wait=True)
            
            if not self.pump_configs:
                print("No pumps configured yet.")
                return
            
            print("🔧 CONFIGURED PUMPS")
            print("=" * 50)
            
            for pump_name, config in self.pump_configs.items():
                pump_type = config['type']
                pump_info = self.pump_types[pump_type]
                parameters = config['parameters']
                
                print(f"📌 {pump_name} ({pump_info['name']})")
                print(f"   Serial Port: {parameters.get('serial_port', 'Not set')}")
                
                for param, value in parameters.items():
                    if param != 'serial_port':
                        param_display = param.replace('_', ' ').title()
                        print(f"   {param_display}: {value}")
                
                print()
    
    def generate_code(self) -> str:
        """Generate pump initialization code"""
        if not self.pump_configs:
            return "# No pumps configured"
        
        lines = [
            "# Pump initialization code",
            "# Generated by Phase2_ApparatusBuilder",
            ""
        ]
        
        for pump_name, config in self.pump_configs.items():
            pump_type = config['type']
            parameters = config['parameters']
            
            # Generate import if needed
            lines.append(f"# {pump_name} - {self.pump_types[pump_type]['name']}")
            
            # Generate pump creation code
            if pump_type == 'HarvardSyringePump':
                lines.append(f"{pump_name} = mw.HarvardSyringePump(")
                lines.append(f"    syringe_volume='{parameters['syringe_volume']}',")
                lines.append(f"    syringe_diameter='{parameters['syringe_diameter']}',")
                lines.append(f"    serial_port='{parameters['serial_port']}',")
                lines.append(f"    name='{pump_name}'")
                lines.append(")")
                
            elif pump_type == 'VarianPump':
                lines.append(f"{pump_name} = mw.VarianPump(")
                lines.append(f"    serial_port='{parameters['serial_port']}',")
                lines.append(f"    max_rate='{parameters['max_rate']}',")
                lines.append(f"    name='{pump_name}'")
                lines.append(")")
                
            elif pump_type == 'FreeStepPump':
                lines.append(f"{pump_name} = mw.FreeStepPump(")
                lines.append(f"    MCU_ID='{parameters['MCU_ID']}',")
                lines.append(f"    motor_ID={parameters['motor_ID']},")
                lines.append(f"    syringe_volume='{parameters['syringe_volume']}',")
                lines.append(f"    syringe_diameter='{parameters['syringe_diameter']}',")
                lines.append(f"    name='{pump_name}'")
                lines.append(")")
            
            lines.append("")
        
        # Add pump list
        pump_names = list(self.pump_configs.keys())
        if len(pump_names) > 1:
            lines.append("# Pump list for easy access")
            lines.append(f"pumps = [{', '.join(pump_names)}]")
        
        return "\n".join(lines)
    
    def get_configured_pumps(self) -> Dict[str, Dict[str, Any]]:
        """Get configured pump information"""
        return self.pump_configs.copy()
    
    def create_interface(self) -> widgets.Widget:
        """Create the pump configurator interface"""
        
        # Basic configuration section
        basic_config = widgets.VBox([
            widgets.HTML("<h4>Pump Configuration</h4>"),
            self.pump_type_dropdown,
            self.pump_name_input,
            self.parameter_container
        ])
        
        # Serial port section
        port_row = widgets.HBox([
            self.serial_port_dropdown,
            self.refresh_ports_button
        ])
        
        port_section = widgets.VBox([
            widgets.HTML("<h4>Serial Port</h4>"),
            port_row
        ])
        
        # Action buttons
        button_row = widgets.HBox([
            self.add_pump_button,
            self.test_pump_button
        ])
        
        # Left panel: Configuration
        left_panel = widgets.VBox([
            basic_config,
            port_section,
            button_row
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        # Right panel: Current pumps
        right_panel = widgets.VBox([
            widgets.HTML("<h4>Configured Pumps</h4>"),
            self.pumps_display
        ], layout=widgets.Layout(width='500px', padding='10px'))
        
        return widgets.HBox([left_panel, right_panel])