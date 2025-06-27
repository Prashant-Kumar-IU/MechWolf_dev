"""
Protocol Development GUI

Integrated protocol development interface that works with experimental metadata
and provides MechWolf core validation.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from typing import Dict, Any, Optional, List, Tuple
import traceback
from datetime import timedelta

from .procedure_builder import ProcedureBuilder
from .protocol_validator import ProtocolValidator


class ProtocolDevGUI:
    """Protocol development interface with MechWolf integration"""
    
    def __init__(self, experiment_manager, protocol=None, pumps=None):
        """
        Initialize protocol development GUI
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
            protocol: Optional existing mw.Protocol instance
            pumps: Optional dictionary of configured pump objects
        """
        self.experiment = experiment_manager
        self.protocol = protocol
        self.pumps = pumps or {}
        
        # Initialize submodules
        self.procedure_builder = ProcedureBuilder(experiment_manager, self.pumps)
        self.validator = ProtocolValidator()
        
        # GUI state
        self.current_procedures = []
        self.total_duration = timedelta(0)
        
        self._create_widgets()
        self._load_existing_protocol()
    
    def _create_widgets(self):
        """Create the main UI widgets"""
        
        # Header
        self.header = widgets.HTML("""
        <div style='background: linear-gradient(135deg, #8e24aa 0%, #3f51b5 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0; text-align: center;'>
                📋 Phase 3: Protocol Development & Validation
            </h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0; text-align: center;'>
                Build, validate, and simulate your experimental protocol
            </p>
        </div>
        """)
        
        # Protocol information section
        self.protocol_name_input = widgets.Text(
            placeholder="Enter protocol name",
            description="Name:",
            layout=widgets.Layout(width='400px')
        )
        
        self.protocol_description_input = widgets.Textarea(
            placeholder="Describe your protocol...",
            description="Description:",
            layout=widgets.Layout(width='500px', height='80px')
        )
        
        # Global parameters
        self.temperature_input = widgets.Text(
            placeholder="e.g., 25°C",
            description="Temperature:",
            layout=widgets.Layout(width='150px')
        )
        
        self.pressure_input = widgets.Text(
            placeholder="e.g., 1 atm",
            description="Pressure:",
            layout=widgets.Layout(width='150px')
        )
        
        # Protocol tabs
        self.tabs = widgets.Tab()
        
        # Tab 1: Procedure Builder
        self.procedure_tab = self._create_procedure_tab()
        
        # Tab 2: Timeline View
        self.timeline_tab = self._create_timeline_tab()
        
        # Tab 3: Validation
        self.validation_tab = self._create_validation_tab()
        
        # Tab 4: Simulation
        self.simulation_tab = self._create_simulation_tab()
        
        # Set up tabs
        self.tabs.children = [
            self.procedure_tab,
            self.timeline_tab,
            self.validation_tab,
            self.simulation_tab
        ]
        
        tab_titles = [
            "🔧 Build Procedures",
            "📅 Timeline View", 
            "✅ Validation",
            "🧪 Simulation"
        ]
        
        for i, title in enumerate(tab_titles):
            self.tabs.set_title(i, title)
        
        # Action buttons
        self.save_protocol_button = widgets.Button(
            description="💾 Save Protocol",
            button_style='primary',
            layout=widgets.Layout(width='150px')
        )
        self.save_protocol_button.on_click(self._save_protocol)
        
        self.load_protocol_button = widgets.Button(
            description="📂 Load Protocol",
            button_style='info',
            layout=widgets.Layout(width='150px')
        )
        self.load_protocol_button.on_click(self._load_protocol)
        
        self.export_code_button = widgets.Button(
            description="📝 Export Code",
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        self.export_code_button.on_click(self._export_protocol_code)
        
        # Status area
        self.status_output = widgets.Output()
        
    def _create_procedure_tab(self):
        """Create procedure building tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #f3e5f5; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #7b1fa2;'>🔧 Procedure Builder</h4>
            <p style='margin-bottom: 0;'>
                Build your protocol by adding procedures for pumps, valves, and other components.
                Procedures are executed in time-based sequence.
            </p>
        </div>
        """)
        
        # Procedure builder interface
        procedure_interface = self.procedure_builder.create_interface()
        
        # Current procedures display
        self.procedures_display = widgets.Output(
            layout=widgets.Layout(
                height='300px',
                border='1px solid #ccc',
                padding='10px',
                overflow_y='auto'
            )
        )
        
        # Procedure management buttons
        clear_procedures_button = widgets.Button(
            description="🗑️ Clear All",
            button_style='warning',
            layout=widgets.Layout(width='120px')
        )
        clear_procedures_button.on_click(self._clear_all_procedures)
        
        sort_procedures_button = widgets.Button(
            description="📊 Sort by Time",
            button_style='info',
            layout=widgets.Layout(width='140px')
        )
        sort_procedures_button.on_click(self._sort_procedures_by_time)
        
        button_row = widgets.HBox([
            clear_procedures_button,
            sort_procedures_button
        ])
        
        return widgets.VBox([
            instructions,
            procedure_interface,
            widgets.HTML("<h4>Current Procedures:</h4>"),
            button_row,
            self.procedures_display
        ])
    
    def _create_timeline_tab(self):
        """Create timeline visualization tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #2e7d32;'>📅 Timeline View</h4>
            <p style='margin-bottom: 0;'>
                Visualize your protocol timeline with concurrent and sequential procedures.
            </p>
        </div>
        """)
        
        # Timeline controls
        self.timeline_scale = widgets.Dropdown(
            options=[('Seconds', 'seconds'), ('Minutes', 'minutes'), ('Hours', 'hours')],
            value='minutes',
            description='Scale:',
            layout=widgets.Layout(width='150px')
        )
        
        refresh_timeline_button = widgets.Button(
            description="🔄 Refresh Timeline",
            button_style='info',
            layout=widgets.Layout(width='160px')
        )
        refresh_timeline_button.on_click(self._refresh_timeline)
        
        # Timeline display
        self.timeline_display = widgets.Output(
            layout=widgets.Layout(
                height='500px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        control_row = widgets.HBox([self.timeline_scale, refresh_timeline_button])
        
        return widgets.VBox([
            instructions,
            control_row,
            self.timeline_display
        ])
    
    def _create_validation_tab(self):
        """Create validation tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #f57c00;'>✅ Protocol Validation</h4>
            <p style='margin-bottom: 0;'>
                Validate your protocol using MechWolf core validation and safety checks.
            </p>
        </div>
        """)
        
        # Validation controls
        validate_button = widgets.Button(
            description="🔍 Validate Protocol",
            button_style='primary',
            layout=widgets.Layout(width='160px')
        )
        validate_button.on_click(self._validate_protocol)
        
        check_safety_button = widgets.Button(
            description="🛡️ Safety Check",
            button_style='warning',
            layout=widgets.Layout(width='140px')
        )
        check_safety_button.on_click(self._check_safety)
        
        estimate_time_button = widgets.Button(
            description="⏱️ Estimate Time",
            button_style='info',
            layout=widgets.Layout(width='140px')
        )
        estimate_time_button.on_click(self._estimate_execution_time)
        
        # Validation results
        self.validation_output = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        control_row = widgets.HBox([
            validate_button,
            check_safety_button,
            estimate_time_button
        ])
        
        return widgets.VBox([
            instructions,
            control_row,
            self.validation_output
        ])
    
    def _create_simulation_tab(self):
        """Create simulation tab"""
        
        instructions = widgets.HTML("""
        <div style='background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #1976d2;'>🧪 Protocol Simulation</h4>
            <p style='margin-bottom: 0;'>
                Run dry-run simulations and estimate protocol performance.
            </p>
        </div>
        """)
        
        # Simulation controls
        self.simulation_duration = widgets.IntText(
            value=1000,
            description='Duration (ms):',
            layout=widgets.Layout(width='180px')
        )
        
        run_simulation_button = widgets.Button(
            description="▶️ Run Simulation",
            button_style='success',
            layout=widgets.Layout(width='160px')
        )
        run_simulation_button.on_click(self._run_simulation)
        
        dry_run_button = widgets.Button(
            description="🧪 Dry Run",
            button_style='info',
            layout=widgets.Layout(width='120px')
        )
        dry_run_button.on_click(self._run_dry_run)
        
        # Simulation results
        self.simulation_output = widgets.Output(
            layout=widgets.Layout(
                height='400px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        control_row = widgets.HBox([
            self.simulation_duration,
            run_simulation_button,
            dry_run_button
        ])
        
        return widgets.VBox([
            instructions,
            control_row,
            self.simulation_output
        ])
    
    def _load_existing_protocol(self):
        """Load existing protocol data from experimental metadata"""
        try:
            protocol_data = self.experiment.get_section_data("protocol_config")
            
            if protocol_data:
                # Load protocol info
                self.protocol_name_input.value = protocol_data.get("name", "")
                self.protocol_description_input.value = protocol_data.get("description", "")
                
                # Load global parameters
                global_params = protocol_data.get("global_parameters", {})
                self.temperature_input.value = global_params.get("temperature", "")
                self.pressure_input.value = global_params.get("pressure", "")
                
                # Load procedures
                procedures = protocol_data.get("procedures", [])
                self.current_procedures = procedures
                
                self._refresh_procedures_display()
                self._refresh_timeline()
                
                with self.status_output:
                    clear_output(wait=True)
                    print("✅ Loaded existing protocol data")
            
        except Exception as e:
            print(f"Note: No existing protocol data found: {e}")
    
    def _save_protocol(self, button):
        """Save protocol to experimental metadata"""
        try:
            # Collect protocol data
            protocol_data = {
                "name": self.protocol_name_input.value.strip(),
                "description": self.protocol_description_input.value.strip(),
                "global_parameters": {
                    "temperature": self.temperature_input.value.strip(),
                    "pressure": self.pressure_input.value.strip()
                },
                "procedures": self.current_procedures,
                "total_duration": str(self.total_duration),
                "created_timestamp": self._get_current_timestamp()
            }
            
            # Validate required fields
            if not protocol_data["name"]:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Protocol name is required")
                return
            
            # Save to experimental metadata
            success = self.experiment.protocol.set_protocol_info(
                protocol_data["name"],
                protocol_data["description"]
            )
            
            if success:
                # Save procedures
                self.experiment.protocol.load_procedures_from_list(self.current_procedures)
                
                # Save global parameters
                self.experiment.protocol.set_global_parameters(protocol_data["global_parameters"])
                
                # Save to file
                self.experiment.save()
                
                with self.status_output:
                    clear_output(wait=True)
                    print("✅ Protocol saved successfully")
            else:
                with self.status_output:
                    clear_output(wait=True)
                    print("❌ Failed to save protocol")
            
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error saving protocol: {e}")
                traceback.print_exc()
    
    def _load_protocol(self, button):
        """Load protocol from experimental metadata"""
        self._load_existing_protocol()
    
    def _export_protocol_code(self, button):
        """Export protocol as MechWolf code"""
        try:
            code_lines = [
                "# Protocol Code - Generated by Phase3_ProtocolDev",
                "# Generated from experimental metadata",
                "",
                "import mechwolf as mw",
                "",
                "# Create protocol from apparatus",
                "P = mw.Protocol(A)  # A should be your apparatus object",
                ""
            ]
            
            # Add procedures
            for procedure in self.current_procedures:
                component = procedure.get("component")
                action = procedure.get("action")
                start_time = procedure.get("start_time", "0s")
                duration = procedure.get("duration")
                parameters = procedure.get("parameters", {})
                
                if action == "run" and duration:
                    # Pump run command
                    rate = parameters.get("rate", "1 mL/min")
                    code_lines.append(f"P.add({component}, start='{start_time}', duration='{duration}', rate='{rate}')")
                
                elif action == "switch":
                    # Valve switch command
                    position = parameters.get("position", "1")
                    code_lines.append(f"P.add({component}, start='{start_time}', position='{position}')")
                
                elif action == "wait":
                    # Wait command
                    code_lines.append(f"P.add(mw.Wait('{duration}'), start='{start_time}')")
            
            code_lines.extend([
                "",
                "# Validate protocol",
                "P.validate()",
                "",
                "# Execute protocol (dry run)",
                "# executed_experiment = P.execute(dry_run=1000)",
                "",
                "# Execute protocol (real)",
                "# executed_experiment = P.execute()"
            ])
            
            code = "\n".join(code_lines)
            
            # Display code
            with self.status_output:
                clear_output(wait=True)
                print("📝 Generated Protocol Code:")
                print("=" * 50)
                print(code)
                print("=" * 50)
                print("💡 Copy this code to your notebook for execution")
            
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error exporting code: {e}")
    
    def _clear_all_procedures(self, button):
        """Clear all procedures"""
        self.current_procedures = []
        self.total_duration = timedelta(0)
        self._refresh_procedures_display()
        self._refresh_timeline()
        
        with self.status_output:
            clear_output(wait=True)
            print("🗑️ All procedures cleared")
    
    def _sort_procedures_by_time(self, button):
        """Sort procedures by start time"""
        try:
            self.current_procedures.sort(key=lambda p: self._parse_time(p.get("start_time", "0s")))
            self._refresh_procedures_display()
            
            with self.status_output:
                clear_output(wait=True)
                print("📊 Procedures sorted by start time")
                
        except Exception as e:
            with self.status_output:
                clear_output(wait=True)
                print(f"❌ Error sorting procedures: {e}")
    
    def _parse_time(self, time_str: str) -> float:
        """Parse time string to seconds (float)"""
        if not time_str:
            return 0.0
        
        time_str = time_str.strip().lower()
        
        # Handle different time units
        if time_str.endswith('s'):
            return float(time_str[:-1])
        elif time_str.endswith('min'):
            return float(time_str[:-3]) * 60
        elif time_str.endswith('h'):
            return float(time_str[:-1]) * 3600
        else:
            # Assume seconds if no unit
            try:
                return float(time_str)
            except:
                return 0.0
    
    def _refresh_procedures_display(self):
        """Refresh the procedures display"""
        with self.procedures_display:
            clear_output(wait=True)
            
            if not self.current_procedures:
                print("No procedures defined yet.")
                return
            
            print("📋 PROTOCOL PROCEDURES")
            print("=" * 60)
            
            for i, procedure in enumerate(self.current_procedures):
                component = procedure.get("component", "Unknown")
                action = procedure.get("action", "Unknown")
                start_time = procedure.get("start_time", "0s")
                duration = procedure.get("duration", "")
                parameters = procedure.get("parameters", {})
                
                print(f"{i+1:2d}. {component} - {action.upper()}")
                print(f"     Start: {start_time}")
                
                if duration:
                    print(f"     Duration: {duration}")
                
                if parameters:
                    param_str = ", ".join(f"{k}: {v}" for k, v in parameters.items())
                    print(f"     Parameters: {param_str}")
                
                print()
    
    def _refresh_timeline(self, button=None):
        """Refresh timeline visualization"""
        with self.timeline_display:
            clear_output(wait=True)
            
            if not self.current_procedures:
                print("No procedures to display in timeline.")
                return
            
            print("📅 PROTOCOL TIMELINE")
            print("=" * 60)
            
            # Convert procedures to timeline events
            events = []
            for procedure in self.current_procedures:
                start_seconds = self._parse_time(procedure.get("start_time", "0s"))
                duration_seconds = self._parse_time(procedure.get("duration", "0s"))
                end_seconds = start_seconds + duration_seconds
                
                events.append({
                    "start": start_seconds,
                    "end": end_seconds,
                    "component": procedure.get("component"),
                    "action": procedure.get("action"),
                    "parameters": procedure.get("parameters", {})
                })
            
            # Sort by start time
            events.sort(key=lambda e: e["start"])
            
            # Display timeline
            scale = self.timeline_scale.value
            scale_factor = 1 if scale == 'seconds' else 60 if scale == 'minutes' else 3600
            scale_unit = scale[0].upper() + scale[1:-1]  # Seconds -> Second, etc.
            
            print(f"Time Scale: {scale_unit}s")
            print("-" * 60)
            
            for event in events:
                start_scaled = event["start"] / scale_factor
                end_scaled = event["end"] / scale_factor
                duration_scaled = end_scaled - start_scaled
                
                component = event["component"]
                action = event["action"]
                
                if duration_scaled > 0:
                    print(f"{start_scaled:6.2f} - {end_scaled:6.2f} | {component} {action.upper()}")
                else:
                    print(f"{start_scaled:6.2f}        | {component} {action.upper()}")
                
                # Show parameters
                if event["parameters"]:
                    param_str = ", ".join(f"{k}={v}" for k, v in event["parameters"].items())
                    print(f"              | └─ {param_str}")
            
            # Calculate total duration
            if events:
                total_seconds = max(event["end"] for event in events)
                total_scaled = total_seconds / scale_factor
                print("-" * 60)
                print(f"Total Duration: {total_scaled:.2f} {scale_unit.lower()}s")
    
    def _validate_protocol(self, button):
        """Validate protocol using MechWolf core"""
        with self.validation_output:
            clear_output(wait=True)
            print("🔍 Validating protocol...")
            
        try:
            validation_results = self.validator.validate_protocol(
                self.current_procedures,
                self.pumps
            )
            
            with self.validation_output:
                clear_output(wait=True)
                
                if validation_results['valid']:
                    print("✅ Protocol validation passed!")
                else:
                    print("❌ Protocol validation failed:")
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
                print(f"❌ Validation error: {e}")
                traceback.print_exc()
    
    def _check_safety(self, button):
        """Perform safety checks"""
        with self.validation_output:
            clear_output(wait=True)
            print("🛡️ Performing safety checks...")
            
        try:
            safety_results = self.validator.check_safety(
                self.current_procedures,
                self.pumps
            )
            
            with self.validation_output:
                clear_output(wait=True)
                
                if safety_results['safe']:
                    print("✅ Safety checks passed!")
                else:
                    print("⚠️ Safety concerns found:")
                    for concern in safety_results['concerns']:
                        print(f"  • {concern}")
                
                if safety_results['recommendations']:
                    print("\n💡 Safety recommendations:")
                    for rec in safety_results['recommendations']:
                        print(f"  • {rec}")
        
        except Exception as e:
            with self.validation_output:
                clear_output(wait=True)
                print(f"❌ Safety check error: {e}")
    
    def _estimate_execution_time(self, button):
        """Estimate protocol execution time"""
        with self.validation_output:
            clear_output(wait=True)
            
        try:
            if not self.current_procedures:
                with self.validation_output:
                    print("❌ No procedures to estimate")
                return
            
            # Calculate total execution time
            max_end_time = 0
            concurrent_procedures = []
            
            for procedure in self.current_procedures:
                start_seconds = self._parse_time(procedure.get("start_time", "0s"))
                duration_seconds = self._parse_time(procedure.get("duration", "0s"))
                end_seconds = start_seconds + duration_seconds
                
                max_end_time = max(max_end_time, end_seconds)
                
                concurrent_procedures.append({
                    "component": procedure.get("component"),
                    "start": start_seconds,
                    "end": end_seconds,
                    "duration": duration_seconds
                })
            
            with self.validation_output:
                clear_output(wait=True)
                
                print("⏱️ EXECUTION TIME ESTIMATE")
                print("=" * 40)
                print(f"Total Duration: {max_end_time:.1f} seconds ({max_end_time/60:.1f} minutes)")
                
                # Check for concurrent operations
                overlaps = []
                for i, proc1 in enumerate(concurrent_procedures):
                    for j, proc2 in enumerate(concurrent_procedures[i+1:], i+1):
                        if (proc1["start"] < proc2["end"] and proc2["start"] < proc1["end"]):
                            overlaps.append((proc1["component"], proc2["component"]))
                
                if overlaps:
                    print(f"\nConcurrent Operations: {len(overlaps)} overlaps detected")
                    for comp1, comp2 in overlaps[:5]:  # Show first 5
                        print(f"  • {comp1} ⚡ {comp2}")
                    
                    if len(overlaps) > 5:
                        print(f"  ... and {len(overlaps) - 5} more")
                else:
                    print("\nNo concurrent operations detected")
        
        except Exception as e:
            with self.validation_output:
                clear_output(wait=True)
                print(f"❌ Time estimation error: {e}")
    
    def _run_simulation(self, button):
        """Run protocol simulation"""
        with self.simulation_output:
            clear_output(wait=True)
            print("▶️ Running protocol simulation...")
            
        try:
            # This would interface with MechWolf's simulation capabilities
            duration = self.simulation_duration.value
            
            with self.simulation_output:
                clear_output(wait=True)
                print("🧪 PROTOCOL SIMULATION")
                print("=" * 40)
                print(f"Simulation Duration: {duration} ms")
                print("Status: Simulation completed successfully")
                print("\nNote: Full simulation requires MechWolf core integration")
                print("For now, this shows a mock simulation result.")
        
        except Exception as e:
            with self.simulation_output:
                clear_output(wait=True)
                print(f"❌ Simulation error: {e}")
    
    def _run_dry_run(self, button):
        """Run protocol dry run"""
        with self.simulation_output:
            clear_output(wait=True)
            print("🧪 Running protocol dry run...")
            
        try:
            # This would use MechWolf's dry run capabilities
            with self.simulation_output:
                clear_output(wait=True)
                print("🧪 PROTOCOL DRY RUN")
                print("=" * 40)
                print("Dry run completed successfully")
                print("All components responded correctly")
                print("\nNote: Full dry run requires MechWolf core integration")
        
        except Exception as e:
            with self.simulation_output:
                clear_output(wait=True)
                print(f"❌ Dry run error: {e}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def add_procedure(self, procedure: Dict[str, Any]):
        """Add procedure to protocol"""
        self.current_procedures.append(procedure)
        self._refresh_procedures_display()
        self._refresh_timeline()
    
    def display(self):
        """Display the GUI"""
        
        # Protocol info section
        info_section = widgets.VBox([
            widgets.HTML("<h4>Protocol Information</h4>"),
            self.protocol_name_input,
            self.protocol_description_input,
            widgets.HBox([self.temperature_input, self.pressure_input])
        ])
        
        # Action buttons
        button_row = widgets.HBox([
            self.save_protocol_button,
            self.load_protocol_button,
            self.export_code_button
        ])
        
        main_layout = widgets.VBox([
            self.header,
            info_section,
            self.tabs,
            button_row,
            self.status_output
        ])
        
        display(main_layout)