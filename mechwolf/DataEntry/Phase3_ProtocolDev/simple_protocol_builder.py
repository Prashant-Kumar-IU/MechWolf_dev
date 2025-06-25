"""
Simple Protocol Builder for Phase 3 Protocol Development

A streamlined, table-based interface for building MechWolf protocols that generates
clean, readable code with proper timedelta variable handling.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import timedelta

from .time_variable_manager import TimeVariableManager
from .protocol_code_generator import ProtocolCodeGenerator
from ..shared_components.apparatus_factory import ApparatusFactory


class SimpleProtocolBuilder:
    """Simple, table-based protocol builder interface"""
    
    def __init__(self, experiment_manager):
        """
        Initialize simple protocol builder
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment = experiment_manager
        self.apparatus = None
        self.available_components = {}
        
        # Initialize managers
        self.time_manager = TimeVariableManager()
        self.code_generator = ProtocolCodeGenerator(self.time_manager)
        
        # Current procedures
        self.procedures = []
        
        # Load apparatus and components
        self._load_apparatus()
        self._create_widgets()
        self._load_saved_protocol()
    
    def _load_apparatus(self):
        """Load apparatus from experimental metadata"""
        try:
            # Create apparatus from experimental metadata
            self.apparatus = ApparatusFactory.create_apparatus_from_experiment(self.experiment)
            
            # Extract available components
            apparatus_data = self.experiment.get_section_data("apparatus_config")
            if apparatus_data and "components" in apparatus_data:
                components = apparatus_data["components"]
                
                # Active components (pumps, valves, etc.)
                for comp_config in components.get("active", []):
                    name = comp_config.get("name", "")
                    comp_type = comp_config.get("type", "")
                    if name:
                        self.available_components[name] = {
                            "type": comp_type,
                            "category": "active",
                            "config": comp_config
                        }
                
                # Some passive components might be controllable
                for comp_config in components.get("passive", []):
                    name = comp_config.get("name", "")
                    comp_type = comp_config.get("type", "")
                    if name and comp_type in ["TemperatureController"]:
                        self.available_components[name] = {
                            "type": comp_type,
                            "category": "passive",
                            "config": comp_config
                        }
            
            print(f"✅ Loaded apparatus with {len(self.available_components)} controllable components")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not load apparatus from metadata: {e}")
            self.available_components = {
                "pump_1": {"type": "HarvardSyringePump", "category": "active"},
                "pump_2": {"type": "HarvardSyringePump", "category": "active"}
            }
    
    def _create_widgets(self):
        """Create the GUI widgets"""
        
        # Header
        self.header = widgets.HTML("""
        <div style='background: linear-gradient(135deg, #4CAF50 0%, #2196F3 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0; text-align: center;'>
                🧪 Simple Protocol Builder
            </h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0; text-align: center;'>
                Build protocols with clean, readable MechWolf code generation
            </p>
        </div>
        """)
        
        # Main tabs
        self.tabs = widgets.Tab()
        
        # Tab 1: Time Variables
        self.time_vars_tab = self.time_manager.create_interface()
        
        # Tab 2: Add Procedures
        self.add_procedure_tab = self._create_add_procedure_tab()
        
        # Tab 3: View Procedures
        self.view_procedures_tab = self._create_view_procedures_tab()
        
        # Tab 4: Generated Code
        self.code_tab = self._create_code_tab()
        
        # Set up tabs
        self.tabs.children = [
            self.time_vars_tab,
            self.add_procedure_tab,
            self.view_procedures_tab,
            self.code_tab
        ]
        
        tab_titles = [
            "⏱️ Time Variables",
            "➕ Add Procedures", 
            "📋 View Procedures",
            "💻 Generated Code"
        ]
        
        for i, title in enumerate(tab_titles):
            self.tabs.set_title(i, title)
        
        # Action buttons
        self.save_button = widgets.Button(
            description="💾 Save Protocol",
            button_style='primary',
            layout=widgets.Layout(width='150px')
        )
        self.save_button.on_click(self._save_protocol)
        
        self.load_button = widgets.Button(
            description="📂 Load Protocol",
            button_style='info',
            layout=widgets.Layout(width='150px')
        )
        self.load_button.on_click(self._load_protocol)
        
        self.clear_button = widgets.Button(
            description="🗑️ Clear All",
            button_style='warning',
            layout=widgets.Layout(width='130px')
        )
        self.clear_button.on_click(self._clear_all)
        
        # Status output
        self.status_output = widgets.Output()
    
    def _create_add_procedure_tab(self):
        """Create the add procedure tab"""
        
        # Instructions
        instructions = widgets.HTML("""
        <div style='background: #f3e5f5; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #7b1fa2;'>➕ Add Procedure</h4>
            <p style='margin-bottom: 5px;'>Add procedures to your protocol step by step.</p>
            <p style='margin-bottom: 0; font-size: 0.9em;'>
                💡 Use time variables like <code>current</code>, <code>PPh3</code>, <code>H2O + switch</code> for timing
            </p>
        </div>
        """)
        
        # Component selection
        component_options = [("Select component...", "")]
        for name, info in self.available_components.items():
            component_options.append((f"{name} ({info['type']})", name))
        
        self.component_dropdown = widgets.Dropdown(
            options=component_options,
            description="Component:",
            layout=widgets.Layout(width='300px')
        )
        self.component_dropdown.observe(self._on_component_change, names='value')
        
        # Action selection
        self.action_dropdown = widgets.Dropdown(
            options=[("Select action...", "")],
            description="Action:",
            layout=widgets.Layout(width='200px')
        )
        
        # Timing inputs
        self.start_time_input = widgets.Text(
            value="current",
            placeholder="e.g., current, PPh3 + H2O",
            description="Start time:",
            layout=widgets.Layout(width='250px')
        )
        
        self.duration_input = widgets.Text(
            placeholder="e.g., PPh3, H2O + switch, 30s",
            description="Duration:",
            layout=widgets.Layout(width='250px')
        )
        
        # Parameter inputs (dynamic based on action)
        self.rate_input = widgets.Text(
            placeholder="e.g., 0.5 mL/min, 2 mL/min",
            description="Flow rate:",
            layout=widgets.Layout(width='200px')
        )
        
        self.position_input = widgets.Text(
            placeholder="e.g., 1, 2, THF, Li",
            description="Position:",
            layout=widgets.Layout(width='200px')
        )
        
        self.temperature_input = widgets.Text(
            placeholder="e.g., 25°C, 80°C",
            description="Temperature:",
            layout=widgets.Layout(width='200px')
        )
        
        # Description
        self.description_input = widgets.Text(
            placeholder="Optional description for this step",
            description="Description:",
            layout=widgets.Layout(width='400px')
        )
        
        # Time increment option
        self.increment_time_checkbox = widgets.Checkbox(
            value=True,
            description="Increment current time after this procedure",
            layout=widgets.Layout(width='350px')
        )
        
        # Add button
        self.add_procedure_button = widgets.Button(
            description="➕ Add Procedure",
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        self.add_procedure_button.on_click(self._add_procedure)
        
        # Dynamic parameter container
        self.parameter_container = widgets.VBox()
        
        # Layout
        selection_row = widgets.HBox([self.component_dropdown, self.action_dropdown])
        timing_row = widgets.HBox([self.start_time_input, self.duration_input])
        
        return widgets.VBox([
            instructions,
            selection_row,
            timing_row,
            self.parameter_container,
            self.description_input,
            self.increment_time_checkbox,
            self.add_procedure_button
        ])
    
    def _create_view_procedures_tab(self):
        """Create the view procedures tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #2e7d32;'>📋 Current Procedures</h4>
            <p style='margin-bottom: 0;'>Review and manage your protocol procedures.</p>
        </div>
        """)
        
        # Procedures display
        self.procedures_display = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Management buttons
        self.delete_procedure_input = widgets.IntText(
            value=1,
            description="Delete step #:",
            layout=widgets.Layout(width='150px')
        )
        
        self.delete_procedure_button = widgets.Button(
            description="🗑️ Delete",
            button_style='danger',
            layout=widgets.Layout(width='100px')
        )
        self.delete_procedure_button.on_click(self._delete_procedure)
        
        self.refresh_button = widgets.Button(
            description="🔄 Refresh",
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        self.refresh_button.on_click(self._refresh_displays)
        
        management_row = widgets.HBox([
            self.delete_procedure_input,
            self.delete_procedure_button,
            self.refresh_button
        ])
        
        return widgets.VBox([
            instructions,
            self.procedures_display,
            management_row
        ])
    
    def _create_code_tab(self):
        """Create the generated code tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #1976d2;'>💻 Generated Protocol Code</h4>
            <p style='margin-bottom: 0;'>Ready-to-use MechWolf protocol code.</p>
        </div>
        """)
        
        # Code display
        self.code_display = widgets.Output(
            layout=widgets.Layout(
                height='500px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Code actions
        self.copy_code_button = widgets.Button(
            description="📋 Copy Code",
            button_style='primary',
            layout=widgets.Layout(width='120px')
        )
        self.copy_code_button.on_click(self._copy_code)
        
        self.export_code_button = widgets.Button(
            description="💾 Export Code",
            button_style='success',
            layout=widgets.Layout(width='120px')
        )
        self.export_code_button.on_click(self._export_code)
        
        self.update_code_button = widgets.Button(
            description="🔄 Update Code",
            button_style='info',
            layout=widgets.Layout(width='120px')
        )
        self.update_code_button.on_click(self._update_code_display)
        
        code_actions = widgets.HBox([
            self.copy_code_button,
            self.export_code_button,
            self.update_code_button
        ])
        
        return widgets.VBox([
            instructions,
            self.code_display,
            code_actions
        ])
    
    def _on_component_change(self, change):
        """Handle component selection change"""
        component_name = change['new']
        
        if not component_name:
            self.action_dropdown.options = [("Select action...", "")]
            self._update_parameter_inputs("")
            return
        
        # Get component info
        component_info = self.available_components.get(component_name, {})
        component_type = component_info.get("type", "")
        
        # Update action options based on component type
        actions = []
        
        if "Pump" in component_type:
            actions = [("Run", "run"), ("Stop", "stop")]
        elif "Valve" in component_type:
            actions = [("Switch", "switch")]
        elif "Temperature" in component_type:
            actions = [("Set Temperature", "set_temperature")]
        else:
            actions = [("Custom", "custom")]
        
        if not actions:
            actions = [("No actions available", "")]
        
        self.action_dropdown.options = actions
        if actions and actions[0][1]:
            self.action_dropdown.value = actions[0][1]
            self._update_parameter_inputs(actions[0][1])
    
    def _update_parameter_inputs(self, action: str):
        """Update parameter inputs based on selected action"""
        
        parameter_widgets = []
        
        if action == "run":
            parameter_widgets = [self.rate_input]
        elif action == "switch":
            parameter_widgets = [self.position_input]
        elif action == "set_temperature":
            parameter_widgets = [self.temperature_input]
        
        self.parameter_container.children = parameter_widgets
    
    def _add_procedure(self, button):
        """Add a new procedure"""
        try:
            # Validate inputs
            component = self.component_dropdown.value
            if not component:
                self._show_status("❌ Please select a component")
                return
            
            action = self.action_dropdown.value
            if not action:
                self._show_status("❌ Please select an action")
                return
            
            start_time = self.start_time_input.value.strip()
            if not start_time:
                self._show_status("❌ Please specify start time")
                return
            
            # Validate start time expression
            is_valid, error_msg = self.time_manager.validate_expression(start_time)
            if not is_valid:
                self._show_status(f"❌ Invalid start time: {error_msg}")
                return
            
            # Collect parameters
            parameters = {}
            
            if action == "run":
                rate = self.rate_input.value.strip()
                if not rate:
                    self._show_status("❌ Flow rate required for pump run")
                    return
                parameters["rate"] = rate
                
                duration = self.duration_input.value.strip()
                if not duration:
                    self._show_status("❌ Duration required for pump run")
                    return
                
                # Validate duration expression
                is_valid, error_msg = self.time_manager.validate_expression(duration)
                if not is_valid:
                    self._show_status(f"❌ Invalid duration: {error_msg}")
                    return
            
            elif action == "switch":
                position = self.position_input.value.strip()
                if not position:
                    self._show_status("❌ Position required for valve switch")
                    return
                parameters["position"] = position
            
            elif action == "set_temperature":
                temperature = self.temperature_input.value.strip()
                if not temperature:
                    self._show_status("❌ Temperature required")
                    return
                parameters["temperature"] = temperature
            
            # Create procedure
            procedure = {
                "component": component,
                "action": action,
                "start_expression": start_time,
                "parameters": parameters,
                "description": self.description_input.value.strip(),
                "increment_current_time": self.increment_time_checkbox.value
            }
            
            # Add duration for actions that need it
            duration = self.duration_input.value.strip()
            if duration and action in ["run"]:
                procedure["duration_expression"] = duration
            
            # Add to procedures list
            self.procedures.append(procedure)
            self.code_generator.set_procedures(self.procedures)
            
            # Clear form
            self._clear_add_form()
            
            # Refresh displays
            self._refresh_displays()
            
            self._show_status(f"✅ Added procedure: {component} {action}")
            
        except Exception as e:
            self._show_status(f"❌ Error adding procedure: {e}")
    
    def _delete_procedure(self, button):
        """Delete a procedure"""
        try:
            step_num = self.delete_procedure_input.value
            if step_num < 1 or step_num > len(self.procedures):
                self._show_status(f"❌ Invalid step number. Must be 1-{len(self.procedures)}")
                return
            
            # Remove procedure
            deleted_proc = self.procedures.pop(step_num - 1)
            self.code_generator.set_procedures(self.procedures)
            
            # Refresh displays
            self._refresh_displays()
            
            self._show_status(f"✅ Deleted step {step_num}: {deleted_proc.get('component')} {deleted_proc.get('action')}")
            
        except Exception as e:
            self._show_status(f"❌ Error deleting procedure: {e}")
    
    def _clear_add_form(self):
        """Clear the add procedure form"""
        self.start_time_input.value = "current"
        self.duration_input.value = ""
        self.rate_input.value = ""
        self.position_input.value = ""
        self.temperature_input.value = ""
        self.description_input.value = ""
        self.increment_time_checkbox.value = True
    
    def _refresh_displays(self, button=None):
        """Refresh all displays"""
        self._refresh_procedures_display()
        self._update_code_display()
    
    def _refresh_procedures_display(self):
        """Refresh the procedures display"""
        with self.procedures_display:
            clear_output(wait=True)
            
            if not self.procedures:
                print("No procedures defined yet.")
                print("\n💡 Add procedures using the 'Add Procedures' tab")
                return
            
            print("📋 PROTOCOL PROCEDURES")
            print("=" * 60)
            
            for i, procedure in enumerate(self.procedures):
                step_num = i + 1
                component = procedure.get("component", "Unknown")
                action = procedure.get("action", "Unknown")
                start_expr = procedure.get("start_expression", "")
                duration_expr = procedure.get("duration_expression", "")
                parameters = procedure.get("parameters", {})
                description = procedure.get("description", "")
                increment = procedure.get("increment_current_time", False)
                
                print(f"{step_num:2d}. {component} - {action.upper()}")
                print(f"     Start: {start_expr}")
                
                if duration_expr:
                    print(f"     Duration: {duration_expr}")
                
                if parameters:
                    param_str = ", ".join(f"{k}: {v}" for k, v in parameters.items())
                    print(f"     Parameters: {param_str}")
                
                if description:
                    print(f"     Description: {description}")
                
                if increment:
                    print(f"     ⏱️ Increments current time")
                
                print()
    
    def _update_code_display(self, button=None):
        """Update the code display"""
        with self.code_display:
            clear_output(wait=True)
            
            try:
                # Generate code
                code = self.code_generator.generate_protocol_code()
                
                print("💻 GENERATED MECHWOLF PROTOCOL CODE")
                print("=" * 60)
                print(code)
                print("=" * 60)
                print("💡 Copy this code to your notebook for execution")
                
            except Exception as e:
                print(f"❌ Error generating code: {e}")
    
    def _copy_code(self, button):
        """Copy code to clipboard (show code for manual copying)"""
        try:
            code = self.code_generator.generate_protocol_code()
            
            with self.status_output:
                clear_output(wait=True)
                print("📋 Code ready for copying:")
                print("=" * 50)
                print(code)
                print("=" * 50)
                print("💡 Select all text above and copy manually")
                
        except Exception as e:
            self._show_status(f"❌ Error copying code: {e}")
    
    def _export_code(self, button):
        """Export code to file"""
        try:
            code = self.code_generator.generate_protocol_code()
            
            # Save to a Python file
            filename = f"protocol_{self.experiment.experiment_id[:8]}.py"
            with open(filename, 'w') as f:
                f.write(code)
            
            self._show_status(f"✅ Code exported to {filename}")
            
        except Exception as e:
            self._show_status(f"❌ Error exporting code: {e}")
    
    def _save_protocol(self, button):
        """Save protocol to experimental metadata"""
        try:
            success = self.code_generator.save_procedures_to_metadata(self.experiment)
            
            if success:
                self._show_status("✅ Protocol saved to experimental metadata")
            else:
                self._show_status("❌ Failed to save protocol")
                
        except Exception as e:
            self._show_status(f"❌ Error saving protocol: {e}")
    
    def _load_protocol(self, button):
        """Load protocol from experimental metadata"""
        try:
            success = self.code_generator.load_procedures_from_metadata(self.experiment)
            
            if success:
                self.procedures = self.code_generator.procedures
                self._refresh_displays()
                self._show_status("✅ Protocol loaded from experimental metadata")
            else:
                self._show_status("ℹ️ No saved protocol found in experimental metadata")
                
        except Exception as e:
            self._show_status(f"❌ Error loading protocol: {e}")
    
    def _clear_all(self, button):
        """Clear all procedures"""
        self.procedures = []
        self.code_generator.clear_procedures()
        self._refresh_displays()
        self._show_status("🗑️ All procedures cleared")
    
    def _load_saved_protocol(self):
        """Load any saved protocol data"""
        try:
            self.code_generator.load_procedures_from_metadata(self.experiment)
            self.procedures = self.code_generator.procedures
        except:
            # No saved data or error loading - start fresh
            pass
    
    def _show_status(self, message: str):
        """Show status message"""
        with self.status_output:
            clear_output(wait=True)
            print(message)
    
    def display(self):
        """Display the simple protocol builder interface"""
        
        # Action buttons row
        action_buttons = widgets.HBox([
            self.save_button,
            self.load_button,
            self.clear_button
        ])
        
        # Main layout
        main_layout = widgets.VBox([
            self.header,
            self.tabs,
            action_buttons,
            self.status_output
        ])
        
        display(main_layout)
        
        # Initial refresh
        self._refresh_displays()
    
    def get_generated_code(self) -> str:
        """Get the current generated protocol code"""
        return self.code_generator.generate_protocol_code()
    
    def get_apparatus(self):
        """Get the loaded apparatus object"""
        return self.apparatus
    
    def get_procedure_summary(self) -> Dict[str, Any]:
        """Get summary of current procedures"""
        return self.code_generator.get_procedure_summary()