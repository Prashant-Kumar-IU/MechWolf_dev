"""
Notebook Integration

Jupyter notebook integration helpers and utilities for the MechWolf DataEntry system.
"""

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
from typing import Dict, Any, List, Optional, Callable
import json
import os


class NotebookIntegration:
    """Jupyter notebook integration utilities"""
    
    @staticmethod
    def create_section_header(title: str, description: str = "", 
                            gradient: str = "135deg, #667eea 0%, #764ba2 100%") -> widgets.HTML:
        """Create a styled section header for notebook cells"""
        
        html_content = f"""
        <div style='background: linear-gradient({gradient}); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='color: white; margin: 0; text-align: center; font-weight: 600;'>
                {title}
            </h2>
        """
        
        if description:
            html_content += f"""
            <p style='color: #f0f0f0; margin: 10px 0 0 0; text-align: center; opacity: 0.9;'>
                {description}
            </p>
            """
        
        html_content += "</div>"
        
        return widgets.HTML(html_content)
    
    @staticmethod
    def create_info_box(content: str, box_type: str = "info") -> widgets.HTML:
        """Create styled info boxes for instructions or warnings"""
        
        colors = {
            'info': {'bg': '#e3f2fd', 'border': '#2196f3', 'icon': 'ℹ️'},
            'warning': {'bg': '#fff3e0', 'border': '#ff9800', 'icon': '⚠️'},
            'success': {'bg': '#e8f5e8', 'border': '#4caf50', 'icon': '✅'},
            'error': {'bg': '#ffebee', 'border': '#f44336', 'icon': '❌'}
        }
        
        style = colors.get(box_type, colors['info'])
        
        html_content = f"""
        <div style='background: {style["bg"]}; border-left: 4px solid {style["border"]}; 
                    padding: 15px; border-radius: 4px; margin: 10px 0;'>
            <div style='display: flex; align-items: flex-start; gap: 10px;'>
                <span style='font-size: 18px;'>{style["icon"]}</span>
                <div>{content}</div>
            </div>
        </div>
        """
        
        return widgets.HTML(html_content)
    
    @staticmethod
    def create_progress_indicator(steps: List[str], current_step: int = 0) -> widgets.HTML:
        """Create a progress indicator for multi-step workflows"""
        
        html_content = """
        <div style='display: flex; align-items: center; gap: 10px; padding: 15px; 
                    background: #f5f5f5; border-radius: 8px; margin: 10px 0;'>
        """
        
        for i, step in enumerate(steps):
            if i < current_step:
                # Completed step
                color = "#4caf50"
                icon = "✅"
            elif i == current_step:
                # Current step
                color = "#2196f3"
                icon = "⏳"
            else:
                # Future step
                color = "#9e9e9e"
                icon = "⭕"
            
            html_content += f"""
            <div style='display: flex; align-items: center; gap: 5px;'>
                <span style='color: {color}; font-size: 16px;'>{icon}</span>
                <span style='color: {color}; font-weight: {"bold" if i == current_step else "normal"};'>
                    {step}
                </span>
            </div>
            """
            
            # Add arrow between steps (except for last step)
            if i < len(steps) - 1:
                html_content += "<span style='color: #9e9e9e;'>→</span>"
        
        html_content += "</div>"
        
        return widgets.HTML(html_content)
    
    @staticmethod
    def create_code_cell_template(phase: str) -> str:
        """Generate code cell templates for different phases"""
        
        templates = {
            'setup': """
# MechWolf Experiment Setup
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
from mechwolf.DataEntry.utilities import get_notebook_json_name

# Create or load experiment
data_file = get_notebook_json_name()
experiment = ExperimentalMetadataManager(data_file, "Your Experiment Name")

print(f"📊 Experiment: {experiment.get_experiment_name()}")
print(f"📁 Data file: {data_file}")
""",
            
            'reagents': """
# Phase 1: Reagent Entry
from mechwolf.DataEntry import Phase1_ReagentEntry

# Launch reagent entry interface
reagent_gui = Phase1_ReagentEntry.launch_gui(experiment)
""",
            
            'apparatus': """
# Phase 2: Apparatus & Pump Configuration
from mechwolf.DataEntry import Phase2_ApparatusBuilder

# Launch integrated apparatus builder
apparatus_gui = Phase2_ApparatusBuilder.launch_gui(experiment)

# After configuration, get the objects:
# pumps = apparatus_gui.get_configured_pumps()
# A = apparatus_gui.get_apparatus()
""",
            
            'protocol': """
# Phase 3: Protocol Development
from mechwolf.DataEntry import Phase3_ProtocolDev
import mechwolf as mw

# Create protocol from apparatus
P = mw.Protocol(A)

# Launch protocol development interface
protocol_gui = Phase3_ProtocolDev.launch_gui(experiment, protocol=P, pumps=pumps)
""",
            
            'execution': """
# Protocol Execution
# Validate protocol
P.validate()

# Execute dry run first
print("🧪 Running dry run...")
dry_run_result = P.execute(dry_run=1000)

# Execute actual protocol
print("▶️ Executing protocol...")
executed_experiment = P.execute()

print("✅ Protocol execution completed!")
""",
            
            'analysis': """
# Results Analysis
from mechwolf.DataEntry.utilities import TLCInputForm

# Add TLC analysis
tlc_form = TLCInputForm(experiment)
tlc_form.run()

# Get experiment summary
print("📊 Experiment Summary:")
print(experiment.get_summary())
"""
        }
        
        return templates.get(phase, "# Template not found")
    
    @staticmethod
    def create_workflow_navigator(phases: List[Dict[str, str]], 
                                current_phase: int = 0) -> widgets.Widget:
        """Create an interactive workflow navigator"""
        
        # Create navigation buttons
        nav_buttons = []
        
        for i, phase in enumerate(phases):
            if i < current_phase:
                button_style = 'success'  # Completed
                icon = '✅'
            elif i == current_phase:
                button_style = 'info'     # Current
                icon = '⏳'
            else:
                button_style = ''         # Future
                icon = '⭕'
            
            button = widgets.Button(
                description=f"{icon} {phase['name']}",
                button_style=button_style,
                layout=widgets.Layout(width='200px', margin='2px'),
                tooltip=phase.get('description', '')
            )
            
            nav_buttons.append(button)
        
        # Create progress bar
        progress = widgets.IntProgress(
            value=current_phase,
            min=0,
            max=len(phases) - 1,
            description='Progress:',
            bar_style='info',
            style={'bar_color': '#2196f3'},
            layout=widgets.Layout(width='400px')
        )
        
        # Layout
        button_box = widgets.HBox(nav_buttons, layout=widgets.Layout(flex_wrap='wrap'))
        
        return widgets.VBox([
            widgets.HTML("<h4>Workflow Navigation</h4>"),
            progress,
            button_box
        ])
    
    @staticmethod
    def create_data_summary_widget(experiment_manager) -> widgets.Widget:
        """Create a summary widget showing current experiment status"""
        
        output = widgets.Output()
        
        def refresh_summary():
            with output:
                clear_output(wait=True)
                
                try:
                    # Get experiment info
                    exp_info = experiment_manager.get_experiment_info()
                    
                    print("📊 EXPERIMENT SUMMARY")
                    print("=" * 50)
                    print(f"Name: {exp_info.get('experiment_name', 'Unnamed')}")
                    print(f"ID: {exp_info.get('experiment_id', 'N/A')}")
                    print(f"Created: {exp_info.get('created', 'N/A')}")
                    print()
                    
                    # Chemistry summary
                    chemistry_data = experiment_manager.chemistry.get_data()
                    solid_reagents = len(chemistry_data.get('solid_reagents', []))
                    liquid_reagents = len(chemistry_data.get('liquid_reagents', []))
                    
                    print("🧪 CHEMISTRY DATA")
                    print(f"Solid reagents: {solid_reagents}")
                    print(f"Liquid reagents: {liquid_reagents}")
                    print(f"Solvent: {chemistry_data.get('solvent', 'Not set')}")
                    print()
                    
                    # Apparatus summary
                    apparatus_data = experiment_manager.apparatus.get_data()
                    components = apparatus_data.get('components', {})
                    active_count = len(components.get('active', []))
                    passive_count = len(components.get('passive', []))
                    connections = len(apparatus_data.get('connections', []))
                    
                    print("⚙️ APPARATUS DATA")
                    print(f"Active components: {active_count}")
                    print(f"Passive components: {passive_count}")
                    print(f"Connections: {connections}")
                    print()
                    
                    # Protocol summary
                    protocol_data = experiment_manager.protocol.get_data()
                    procedures = len(protocol_data.get('procedures', []))
                    
                    print("📋 PROTOCOL DATA")
                    print(f"Procedures: {procedures}")
                    print(f"Protocol name: {protocol_data.get('name', 'Not set')}")
                    
                except Exception as e:
                    print(f"Error loading summary: {e}")
        
        refresh_button = widgets.Button(
            description='🔄 Refresh',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        refresh_button.on_click(lambda x: refresh_summary())
        
        # Initial load
        refresh_summary()
        
        return widgets.VBox([
            widgets.HBox([widgets.HTML("<h4>Experiment Status</h4>"), refresh_button]),
            output
        ])
    
    @staticmethod
    def create_export_widget(experiment_manager) -> widgets.Widget:
        """Create widget for exporting experiment data"""
        
        export_format = widgets.Dropdown(
            options=[
                ('Complete JSON', 'json'),
                ('Summary Report', 'summary'),
                ('Protocol Code', 'protocol'),
                ('Component List', 'components')
            ],
            description='Format:',
            layout=widgets.Layout(width='200px')
        )
        
        output = widgets.Output(
            layout=widgets.Layout(height='300px', overflow_y='auto')
        )
        
        def export_data(button):
            with output:
                clear_output(wait=True)
                
                format_type = export_format.value
                
                try:
                    if format_type == 'json':
                        data = experiment_manager.get_all_data()
                        print(json.dumps(data, indent=2))
                    
                    elif format_type == 'summary':
                        print(experiment_manager.get_summary())
                    
                    elif format_type == 'protocol':
                        print("# Protocol code would be generated here")
                        print("# This requires apparatus and protocol configuration")
                    
                    elif format_type == 'components':
                        apparatus_data = experiment_manager.apparatus.get_data()
                        components = apparatus_data.get('components', {})
                        
                        print("COMPONENT LIST")
                        print("=" * 30)
                        
                        print("Active Components:")
                        for comp in components.get('active', []):
                            print(f"  • {comp.get('name')} ({comp.get('type')})")
                        
                        print("\nPassive Components:")
                        for comp in components.get('passive', []):
                            print(f"  • {comp.get('name')} ({comp.get('type')})")
                    
                except Exception as e:
                    print(f"Export error: {e}")
        
        export_button = widgets.Button(
            description='📋 Export',
            button_style='primary',
            layout=widgets.Layout(width='100px')
        )
        export_button.on_click(export_data)
        
        control_row = widgets.HBox([export_format, export_button])
        
        return widgets.VBox([
            widgets.HTML("<h4>Export Data</h4>"),
            control_row,
            output
        ])
    
    @staticmethod
    def inject_custom_css():
        """Inject custom CSS for enhanced styling"""
        css = """
        <style>
        .mechwolf-container {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .mechwolf-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .mechwolf-section {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .mechwolf-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .mechwolf-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
        """
        return widgets.HTML(css)