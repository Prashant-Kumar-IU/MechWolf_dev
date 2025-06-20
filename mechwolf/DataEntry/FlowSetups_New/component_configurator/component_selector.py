"""
Component Selector - Main GUI for selecting and configuring components

This module provides the main interface for selecting component types
and launching appropriate configuration forms.
"""
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, List, Any, Optional, Type
import inspect

# Import MechWolf components
import mechwolf as mw
from mechwolf.components.stdlib import *
from mechwolf.components.contrib import *

from .active_component_forms import ActiveComponentForms
from .passive_component_forms import PassiveComponentForms
from .component_validator import ComponentValidator


class ComponentSelector:
    """Main component selection and configuration interface"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.configured_components: Dict[str, Dict[str, Any]] = {}
        self.validator = ComponentValidator()
        
        # Discover available component types
        self.component_types = self._discover_component_types()
        
        # Initialize form handlers
        self.active_forms = ActiveComponentForms(self)
        self.passive_forms = PassiveComponentForms(self)
        
        # UI elements
        self.main_container = None
        self.component_list_display = None
        
    def _discover_component_types(self) -> Dict[str, Dict[str, Type]]:
        """Automatically discover available MechWolf component types"""
        
        # Active components from contrib
        active_contrib = {
            'HarvardSyringePump': HarvardSyringePump,
            'FreeStepPump': FreeStepPump,
            'ViciValve': ViciValve,
            'ViciPump': ViciPump,
            'VarianHPLC': VarianHPLC,
            'LabJackSensor': LabJackSensor,
            'ArduinoComponent': ArduinoComponent,
        }
        
        # Active components from stdlib
        active_stdlib = {
            'Pump': Pump,
            'Valve': Valve,
            'Sensor': Sensor,
            'TempControl': TempControl,
        }
        
        # Passive components
        passive_components = {
            'Vessel': Vessel,
            'Tube': Tube,
            'Mixer': Mixer,
            'TMixer': TMixer,
            'CrossMixer': CrossMixer,
            'YMixer': YMixer,
        }
        
        return {
            'active_contrib': active_contrib,
            'active_stdlib': active_stdlib,
            'passive': passive_components
        }
    
    def create_main_interface(self):
        """Create the main component selection interface"""
        
        # Header
        header = widgets.HTML("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='margin: 0; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
                    🔧 Component Configurator
                </h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>
                    Select and configure components for your flow chemistry apparatus
                </p>
            </div>
        """)
        
        # Component type selector
        component_categories = widgets.Dropdown(
            options=[
                ('Active Components (Contrib)', 'active_contrib'),
                ('Active Components (Stdlib)', 'active_stdlib'), 
                ('Passive Components', 'passive')
            ],
            description='Category:',
            value='active_contrib',
            style={'description_width': '120px'}
        )
        
        component_type = widgets.Dropdown(
            options=list(self.component_types['active_contrib'].keys()),
            description='Component:',
            style={'description_width': '120px'}
        )
        
        # Update component types when category changes
        def update_component_types(change):
            category = change['new']
            component_type.options = list(self.component_types[category].keys())
            if component_type.options:
                component_type.value = component_type.options[0]
        
        component_categories.observe(update_component_types, names='value')
        
        # Action buttons
        configure_btn = widgets.Button(
            description='Configure Component',
            button_style='primary',
            icon='cog',
            layout=widgets.Layout(width='200px')
        )
        
        # Component list display
        self.component_list_display = widgets.VBox([
            widgets.HTML("<h3>Configured Components</h3>"),
            widgets.HTML("<p style='color: #666;'>No components configured yet.</p>")
        ])
        
        # Event handlers
        configure_btn.on_click(lambda b: self._open_component_form(
            component_categories.value, 
            component_type.value
        ))
        
        # Layout
        selector_section = widgets.VBox([
            widgets.HTML("<h3>Select Component Type</h3>"),
            component_categories,
            component_type,
            configure_btn
        ], layout=widgets.Layout(width='40%', padding='20px'))
        
        list_section = widgets.VBox([
            self.component_list_display
        ], layout=widgets.Layout(width='60%', padding='20px'))
        
        self.main_container = widgets.VBox([
            header,
            widgets.HBox([selector_section, list_section])
        ])
        
        display(self.main_container)
        
        # Load existing components if available
        self._load_existing_components()
    
    def _open_component_form(self, category: str, component_type: str):
        """Open the appropriate configuration form for the selected component"""
        
        component_class = self.component_types[category][component_type]
        
        # Clear output and show form
        clear_output(wait=True)
        
        if category in ['active_contrib', 'active_stdlib']:
            self.active_forms.show_form(component_type, component_class)
        else:
            self.passive_forms.show_form(component_type, component_class)
    
    def add_configured_component(self, component_data: Dict[str, Any]):
        """Add a successfully configured component to the list"""
        
        component_id = f"{component_data['type']}_{len(self.configured_components)}"
        self.configured_components[component_id] = component_data
        
        # Update display
        self._update_component_display()
        
        # Save to data manager if available
        if self.data_manager:
            self._save_components()
    
    def remove_component(self, component_id: str):
        """Remove a component from the configured list"""
        if component_id in self.configured_components:
            del self.configured_components[component_id]
            self._update_component_display()
            if self.data_manager:
                self._save_components()
    
    def _update_component_display(self):
        """Update the display of configured components"""
        
        if not self.configured_components:
            self.component_list_display.children = [
                widgets.HTML("<h3>Configured Components</h3>"),
                widgets.HTML("<p style='color: #666;'>No components configured yet.</p>")
            ]
            return
        
        # Group components by type
        active_components = []
        passive_components = []
        
        for comp_id, comp_data in self.configured_components.items():
            comp_type = comp_data['type']
            comp_name = comp_data.get('name', comp_id)
            
            # Create component display widget
            comp_widget = self._create_component_widget(comp_id, comp_data)
            
            if comp_data.get('category') == 'passive':
                passive_components.append(comp_widget)
            else:
                active_components.append(comp_widget)
        
        # Build display
        display_children = [widgets.HTML("<h3>Configured Components</h3>")]
        
        if active_components:
            display_children.append(widgets.HTML("<h4>Active Components</h4>"))
            display_children.extend(active_components)
        
        if passive_components:
            display_children.append(widgets.HTML("<h4>Passive Components</h4>"))
            display_children.extend(passive_components)
        
        self.component_list_display.children = display_children
    
    def _create_component_widget(self, comp_id: str, comp_data: Dict[str, Any]) -> widgets.Widget:
        """Create a widget to display a configured component"""
        
        comp_type = comp_data['type']
        comp_name = comp_data.get('name', comp_id)
        
        # Create info display
        info_html = f"""
        <div style='border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px;'>
            <strong>{comp_type}</strong>: {comp_name}<br>
        """
        
        # Add key parameters
        key_params = ['serial_port', 'description', 'max_rate', 'length', 'ID', 'OD']
        for param in key_params:
            if param in comp_data and comp_data[param]:
                info_html += f"<span style='color: #666;'>{param}: {comp_data[param]}</span><br>"
        
        info_html += "</div>"
        
        info_label = widgets.HTML(info_html)
        
        # Action buttons
        edit_btn = widgets.Button(
            description='Edit',
            button_style='info',
            layout=widgets.Layout(width='60px')
        )
        
        delete_btn = widgets.Button(
            description='Delete',
            button_style='danger', 
            layout=widgets.Layout(width='60px')
        )
        
        # Event handlers
        edit_btn.on_click(lambda b: self._edit_component(comp_id))
        delete_btn.on_click(lambda b: self.remove_component(comp_id))
        
        return widgets.HBox([
            info_label,
            widgets.VBox([edit_btn, delete_btn], layout=widgets.Layout(width='80px'))
        ])
    
    def _edit_component(self, component_id: str):
        """Edit an existing component"""
        comp_data = self.configured_components[component_id]
        
        # Determine component category and open appropriate form
        category = comp_data.get('category', 'active_contrib')
        component_type = comp_data['type']
        component_class = self.component_types[category][component_type]
        
        clear_output(wait=True)
        
        if category == 'passive':
            self.passive_forms.show_form(component_type, component_class, existing_data=comp_data)
        else:
            self.active_forms.show_form(component_type, component_class, existing_data=comp_data)
    
    def _load_existing_components(self):
        """Load existing components from data manager"""
        if not self.data_manager:
            return
        
        try:
            config = self.data_manager.load_config()
            if config and 'components' in config:
                components = config['components']
                
                # Load active components
                for comp_data in components.get('active', []):
                    comp_id = f"{comp_data['type']}_{len(self.configured_components)}"
                    self.configured_components[comp_id] = comp_data
                
                # Load passive components  
                for comp_data in components.get('passive', []):
                    comp_id = f"{comp_data['type']}_{len(self.configured_components)}"
                    self.configured_components[comp_id] = comp_data
                
                self._update_component_display()
                
        except Exception as e:
            print(f"Error loading existing components: {e}")
    
    def _save_components(self):
        """Save current components to data manager"""
        if not self.data_manager:
            return
        
        try:
            # Organize components by type
            active_components = []
            passive_components = []
            
            for comp_data in self.configured_components.values():
                if comp_data.get('category') == 'passive':
                    passive_components.append(comp_data)
                else:
                    active_components.append(comp_data)
            
            # Save to data manager
            components_config = {
                'active': active_components,
                'passive': passive_components
            }
            
            # Get existing config and update components section
            existing_config = self.data_manager.load_config() or {}
            existing_config['components'] = components_config
            
            self.data_manager.save_config(existing_config)
            
        except Exception as e:
            print(f"Error saving components: {e}")
    
    def get_configured_components(self) -> Dict[str, Dict[str, Any]]:
        """Return all configured components"""
        return self.configured_components.copy()
    
    def return_to_main(self):
        """Return to the main component selector interface"""
        clear_output(wait=True)
        display(self.main_container)