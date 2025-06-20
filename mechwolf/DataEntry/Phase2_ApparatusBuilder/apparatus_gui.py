"""
Integrated Apparatus Builder GUI

Main interface that combines pump configuration with apparatus building,
eliminating the need for separate pump code generation steps.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from typing import Dict, Any, Optional, List, Tuple
import traceback

from .pump_configurator import PumpConfigurator
from .component_configurator import ComponentConfigurator  
from .connection_builder import ConnectionBuilder
from .apparatus_validator import ApparatusValidator
from .apparatus_visualizer import ApparatusVisualizer


class ApparatusBuilderGUI:
    """Integrated apparatus and pump builder interface"""
    
    def __init__(self, experiment_manager):
        """
        Initialize apparatus builder GUI
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        
        # Initialize submodules
        self.pump_configurator = PumpConfigurator(experiment_manager)
        self.component_configurator = ComponentConfigurator(experiment_manager)
        self.connection_builder = ConnectionBuilder(experiment_manager)
        self.validator = ApparatusValidator()
        self.visualizer = ApparatusVisualizer()
        
        # GUI state
        self.current_tab = 0
        self.configured_pumps = {}  # {name: pump_object}
        self.apparatus = None
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the main UI widgets"""
        
        # Header
        self.header = widgets.HTML("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0; text-align: center;'>
                ⚙️ Phase 2: Integrated Apparatus & Pump Builder
            </h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0; text-align: center;'>
                Configure pumps and build apparatus in one integrated workflow
            </p>
        </div>
        """)
        
        # Progress indicator
        self.progress_html = widgets.HTML()
        self._update_progress()
        
        # Main tabs
        self.tabs = widgets.Tab()
        self.tabs.observe(self._on_tab_change, names='selected_index')
        
        # Tab 1: Pump Configuration
        self.pump_tab = self._create_pump_tab()
        
        # Tab 2: Component Configuration
        self.component_tab = self._create_component_tab()
        
        # Tab 3: Connection Building
        self.connection_tab = self._create_connection_tab()
        
        # Tab 4: Validation & Visualization
        self.validation_tab = self._create_validation_tab()
        
        # Tab 5: Code Generation & Export
        self.export_tab = self._create_export_tab()
        
        # Set up tabs
        self.tabs.children = [
            self.pump_tab,
            self.component_tab, 
            self.connection_tab,
            self.validation_tab,
            self.export_tab
        ]
        
        tab_titles = [
            "🔧 Pumps",
            "📦 Components", 
            "🔗 Connections",
            "✅ Validation",
            "💾 Export"
        ]
        
        for i, title in enumerate(tab_titles):
            self.tabs.set_title(i, title)
        
        # Status area
        self.status_output = widgets.Output()
        
    def _create_pump_tab(self):
        """Create pump configuration tab"""
        
        # Instructions
        instructions = widgets.HTML("""
        <div style='background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #1976d2;'>🔧 Pump Configuration</h4>
            <p style='margin-bottom: 0;'>
                Configure your pumps with serial ports, syringes, and parameters. 
                This replaces the separate Pump Code Generator notebook.
            </p>
        </div>
        """)
        
        # Pump configurator interface
        pump_config_widget = self.pump_configurator.create_interface()
        
        # Action buttons
        scan_ports_button = widgets.Button(
            description="🔍 Scan Serial Ports",
            button_style='info',
            layout=widgets.Layout(width='180px')
        )
        scan_ports_button.on_click(self._scan_serial_ports)
        
        test_pumps_button = widgets.Button(
            description="🧪 Test Pumps",
            button_style='warning',
            layout=widgets.Layout(width='150px')
        )
        test_pumps_button.on_click(self._test_pumps)
        
        generate_code_button = widgets.Button(
            description="📝 Generate Code",
            button_style='success',
            layout=widgets.Layout(width='160px')
        )
        generate_code_button.on_click(self._generate_pump_code)
        
        button_row = widgets.HBox([
            scan_ports_button,
            test_pumps_button,
            generate_code_button
        ])
        
        # Generated code display
        self.pump_code_output = widgets.Output(
            layout=widgets.Layout(
                height='200px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        return widgets.VBox([
            instructions,
            pump_config_widget,
            button_row,
            widgets.HTML("<h4>Generated Pump Code:</h4>"),
            self.pump_code_output
        ])
    
    def _create_component_tab(self):
        """Create component configuration tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #f57c00;'>📦 Component Configuration</h4>
            <p style='margin-bottom: 0;'>
                Add vessels, tubes, mixers, and other passive components to your apparatus.
            </p>
        </div>
        """)
        
        # Component configurator interface
        component_config_widget = self.component_configurator.create_interface()
        
        return widgets.VBox([
            instructions,
            component_config_widget
        ])
    
    def _create_connection_tab(self):
        """Create connection building tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #2e7d32;'>🔗 Connection Building</h4>
            <p style='margin-bottom: 0;'>
                Connect your components to build the complete apparatus flow network.
            </p>
        </div>
        """)
        
        # Connection builder interface
        connection_widget = self.connection_builder.create_interface()
        
        return widgets.VBox([
            instructions,
            connection_widget
        ])
    
    def _create_validation_tab(self):
        """Create validation and visualization tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #f3e5f5; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #7b1fa2;'>✅ Validation & Visualization</h4>
            <p style='margin-bottom: 0;'>
                Validate your apparatus configuration and visualize the flow network.
            </p>
        </div>
        """)
        
        # Validation controls
        validate_button = widgets.Button(
            description="🔍 Validate Apparatus",
            button_style='primary',
            layout=widgets.Layout(width='180px')
        )
        validate_button.on_click(self._validate_apparatus)
        
        visualize_button = widgets.Button(
            description="📊 Visualize Network",
            button_style='info',
            layout=widgets.Layout(width='180px')
        )
        visualize_button.on_click(self._visualize_apparatus)
        
        # Validation results
        self.validation_output = widgets.Output(
            layout=widgets.Layout(
                height='300px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        # Visualization area
        self.visualization_output = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        control_row = widgets.HBox([validate_button, visualize_button])
        
        return widgets.VBox([
            instructions,
            control_row,
            widgets.HTML("<h4>Validation Results:</h4>"),
            self.validation_output,
            widgets.HTML("<h4>Network Visualization:</h4>"),
            self.visualization_output
        ])
    
    def _create_export_tab(self):
        """Create code generation and export tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #fff8e1; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #f9a825;'>💾 Export & Code Generation</h4>
            <p style='margin-bottom: 0;'>
                Generate complete apparatus and pump initialization code for your notebook.
            </p>
        </div>
        """)
        
        # Export options
        self.export_format = widgets.Dropdown(
            options=[
                ('Complete Notebook Code', 'notebook'),
                ('Pump Objects Only', 'pumps'),
                ('Apparatus Object Only', 'apparatus'),
                ('Configuration JSON', 'json')
            ],
            value='notebook',
            description='Export Format:'
        )
        
        export_button = widgets.Button(
            description="📋 Generate Code",
            button_style='success',
            layout=widgets.Layout(width='160px')
        )
        export_button.on_click(self._export_code)
        
        copy_button = widgets.Button(
            description="📋 Copy to Clipboard",
            button_style='info',
            layout=widgets.Layout(width='180px')
        )
        copy_button.on_click(self._copy_to_clipboard)
        
        save_config_button = widgets.Button(
            description="💾 Save Configuration",
            button_style='primary',
            layout=widgets.Layout(width='180px')
        )
        save_config_button.on_click(self._save_configuration)
        
        # Generated code display
        self.export_output = widgets.Output(
            layout=widgets.Layout(
                height='500px',
                border='1px solid #ccc',
                padding='10px',
                overflow='auto'
            )
        )
        
        control_row = widgets.HBox([
            self.export_format,
            export_button,
            copy_button,
            save_config_button
        ])
        
        return widgets.VBox([
            instructions,
            control_row,
            widgets.HTML("<h4>Generated Code:</h4>"),
            self.export_output
        ])
    
    def _update_progress(self):
        """Update progress indicator"""
        # Count completed sections
        pumps_configured = len(self.pump_configurator.get_configured_pumps()) > 0
        components_added = len(self.component_configurator.get_components()) > 0
        connections_made = len(self.connection_builder.get_connections()) > 0
        
        progress_items = [
            ("🔧 Pumps", pumps_configured),
            ("📦 Components", components_added),
            ("🔗 Connections", connections_made)
        ]
        
        progress_html = "<div style='display: flex; gap: 20px; padding: 10px; background: #f5f5f5; border-radius: 8px;'>"
        
        for item, completed in progress_items:
            status_icon = "✅" if completed else "⏳"
            color = "#4caf50" if completed else "#ff9800"
            progress_html += f"""
            <div style='display: flex; align-items: center; gap: 5px;'>
                <span style='color: {color};'>{status_icon}</span>
                <span>{item}</span>
            </div>
            """
        
        progress_html += "</div>"
        self.progress_html.value = progress_html
    
    def _on_tab_change(self, change):
        """Handle tab change"""
        self.current_tab = change['new']
        self._update_progress()
    
    def _scan_serial_ports(self, button):
        """Scan for available serial ports"""
        with self.status_output:
            clear_output(wait=True)
            print("🔍 Scanning for serial ports...")
            
        try:
            ports = self.pump_configurator.scan_serial_ports()
            
            with self.status_output:
                clear_output(wait=True)
                if ports:
                    print(f"✅ Found {len(ports)} serial ports:")
                    for port in ports:
                        print(f"  • {port}")
                else:
                    print("❌ No serial ports found")
                    
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error scanning ports: {e}")
    
    def _test_pumps(self, button):
        """Test configured pumps"""
        with self.status_output:
            clear_output(wait=True)
            print("🧪 Testing pump connections...")
            
        try:
            test_results = self.pump_configurator.test_pumps()
            
            with self.status_output:
                clear_output(wait=True)
                print("🧪 Pump Test Results:")
                for pump_name, result in test_results.items():
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} {pump_name}: {result['message']}")
                    
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error testing pumps: {e}")
    
    def _generate_pump_code(self, button):
        """Generate pump initialization code"""
        try:
            code = self.pump_configurator.generate_code()
            
            with self.pump_code_output:
                clear_output(wait=True)
                print("# Generated Pump Initialization Code")
                print("# Copy this to your notebook cell")
                print("-" * 50)
                print(code)
                
        except Exception as e:
            with self.pump_code_output:
                clear_output(wait=True)
                print(f"❌ Error generating code: {e}")
    
    def _validate_apparatus(self, button):
        """Validate apparatus configuration"""
        with self.validation_output:
            clear_output(wait=True)
            print("🔍 Validating apparatus configuration...")
            
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            validation_results = self.validator.validate_apparatus(apparatus_data)
            
            with self.validation_output:
                clear_output(wait=True)
                
                if validation_results['valid']:
                    print("✅ Apparatus configuration is valid!")
                else:
                    print("❌ Validation errors found:")
                    for error in validation_results['errors']:
                        print(f"  • {error}")
                
                if validation_results['warnings']:
                    print("\n⚠️ Warnings:")
                    for warning in validation_results['warnings']:
                        print(f"  • {warning}")
                        
                if validation_results['suggestions']:
                    print("\n💡 Suggestions:")
                    for suggestion in validation_results['suggestions']:
                        print(f"  • {suggestion}")
                        
        except Exception as e:
            with self.validation_output:
                clear_output(wait=True)
                print(f"❌ Error during validation: {e}")
                traceback.print_exc()
    
    def _visualize_apparatus(self, button):
        """Visualize apparatus network"""
        with self.visualization_output:
            clear_output(wait=True)
            print("📊 Generating apparatus visualization...")
            
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            visualization = self.visualizer.create_network_diagram(apparatus_data)
            
            with self.visualization_output:
                clear_output(wait=True)
                if visualization:
                    display(visualization)
                else:
                    print("❌ Could not generate visualization")
                    
        except Exception as e:
            with self.visualization_output:
                clear_output(wait=True)
                print(f"❌ Error creating visualization: {e}")
    
    def _export_code(self, button):
        """Export code based on selected format"""
        try:
            export_format = self.export_format.value
            
            if export_format == 'notebook':
                code = self._generate_complete_notebook_code()
            elif export_format == 'pumps':
                code = self.pump_configurator.generate_code()
            elif export_format == 'apparatus':
                code = self._generate_apparatus_code()
            elif export_format == 'json':
                code = self._export_json_config()
            else:
                code = "# Unknown export format"
            
            with self.export_output:
                clear_output(wait=True)
                print(code)
                
        except Exception as e:
            with self.export_output:
                clear_output(wait=True)
                print(f"❌ Error exporting code: {e}")
                traceback.print_exc()
    
    def _generate_complete_notebook_code(self) -> str:
        """Generate complete notebook code"""
        lines = [
            "# Complete Apparatus and Pump Setup",
            "# Generated by MechWolf Phase2_ApparatusBuilder",
            "",
            "import mechwolf as mw",
            "",
            "# Pump Configuration",
            self.pump_configurator.generate_code(),
            "",
            "# Apparatus Creation",
            self._generate_apparatus_code(),
            "",
            "# Apparatus Summary",
            "print(f'Apparatus: {A.name}')",
            "print(f'Components: {len(A.components)}')",
            "A.describe()",
        ]
        
        return "\n".join(lines)
    
    def _generate_apparatus_code(self) -> str:
        """Generate apparatus creation code"""
        try:
            from ..FlowSetups_New.apparatus_factory import ApparatusFactory
            
            lines = [
                "# Create apparatus from experimental metadata",
                "from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory",
                f"A = ApparatusFactory.create_apparatus_from_experiment(experiment)",
            ]
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"# Error generating apparatus code: {e}"
    
    def _export_json_config(self) -> str:
        """Export JSON configuration"""
        import json
        
        try:
            apparatus_data = self.experiment.apparatus.get_data()
            return json.dumps(apparatus_data, indent=2)
        except Exception as e:
            return f"# Error exporting JSON: {e}"
    
    def _copy_to_clipboard(self, button):
        """Copy generated code to clipboard"""
        # Note: Clipboard access in Jupyter requires additional setup
        with self.status_output:
            clear_output(wait=True)
            print("💡 To copy code: Select all text in the export area and use Ctrl+C")
    
    def _save_configuration(self, button):
        """Save configuration to experimental metadata"""
        try:
            self.experiment.save()
            
            with self.status_output:
                clear_output(wait=True)
                print("✅ Configuration saved to experimental metadata")
                
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error saving configuration: {e}")
    
    def display(self):
        """Display the GUI"""
        main_layout = widgets.VBox([
            self.header,
            self.progress_html,
            self.tabs,
            self.status_output
        ])
        
        display(main_layout)
    
    def get_configured_pumps(self) -> Dict[str, Any]:
        """Get configured pump objects"""
        return self.pump_configurator.get_configured_pumps()
    
    def get_apparatus(self):
        """Get created apparatus object"""
        try:
            from ..FlowSetups_New.apparatus_factory import ApparatusFactory
            return ApparatusFactory.create_apparatus_from_experiment(self.experiment)
        except Exception as e:
            print(f"Error creating apparatus: {e}")
            return None