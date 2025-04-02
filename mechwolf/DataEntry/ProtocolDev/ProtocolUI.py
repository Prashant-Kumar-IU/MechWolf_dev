"""
UI components for protocol creation.

This module provides reusable UI components and widgets for creating
interactive protocol interfaces in Jupyter notebooks.
"""
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import time

import ipywidgets as widgets
from IPython.display import display, HTML


class ProtocolUI:
    """UI components for protocol creation."""
    
    @staticmethod
    def get_flow_direction_html(flow_rate: float) -> str:
        """
        Generate HTML for flow direction indicator based on flow rate.
        
        Args:
            flow_rate: The flow rate value
            
        Returns:
            HTML string for flow direction indicator
        """
        if flow_rate > 0:
            return '<span style="color:green;font-weight:bold">→ Infusing</span>'
        elif flow_rate < 0:
            return '<span style="color:blue;font-weight:bold">← Withdrawing</span>'
        else:
            return '<span style="color:gray;font-weight:bold">○ Stopped</span>'

    @staticmethod
    def create_float_input(label: str, default: float, unit: str = "") -> Tuple[widgets.HBox, widgets.FloatText]:
        """
        Create a labeled float input with unit.
        
        Args:
            label: Input label
            default: Default value
            unit: Unit label (optional)
            
        Returns:
            Tuple of (container, input_widget)
        """
        style = {'description_width': '150px'}
        layout = widgets.Layout(width='350px', margin='10px 0px 10px 0px')
        
        input_widget = widgets.FloatText(
            description=label,
            style=style,
            layout=layout,
            value=default
        )
        
        unit_widget = widgets.Label(value=unit) if unit else None
        
        if unit_widget:
            container = widgets.HBox([input_widget, unit_widget], 
                                   layout=widgets.Layout(align_items='center'))
        else:
            container = widgets.HBox([input_widget], 
                                   layout=widgets.Layout(align_items='center'))
            
        return container, input_widget

    @staticmethod
    def create_protocol_form(inputs: Dict[str, Any], 
                            submit_callback: Callable,
                            last_run_timestamp: Optional[float] = None,
                            title: str = "Protocol Parameters") -> Tuple[Dict[str, widgets.Widget], widgets.VBox, widgets.Output]:
        """
        Create a complete protocol form with inputs and submit button.
        
        Args:
            inputs: Dictionary mapping input names to their default values
            submit_callback: Function to call when submit button is clicked
            last_run_timestamp: Optional timestamp of last run
            title: Form title
            
        Returns:
            Tuple of (widgets_dict, form_container, output_widget)
        """
        # Display title
        display(HTML(f'<h2 style="color:#4682B4;">{title}</h2>'))
        
        # Help texts for common fields
        help_texts = {
            "flow_rate": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Final flow rate. Negative values indicate withdrawal.</p>',
            "solvent_volume": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Volume of solvent to be used.</p>',
            "rinse_volume": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Volume of rinse solvent.</p>',
            "switch_time": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Stall time to allow for syringe switching.</p>',
            "delay_time": '<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Delay time between pumps.</p>'
        }
        
        # Input widgets
        ui_elements = []
        widgets_dict = {}
        
        # Add last run info if available
        last_run_info = widgets.HTML(value='')
        if last_run_timestamp:
            last_run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_run_timestamp))
            last_run_info.value = f'<p style="color:#666;font-style:italic;">Last run: {last_run_time}</p>'
        ui_elements.append(last_run_info)
        widgets_dict["last_run_info"] = last_run_info
        
        # Create flow rate input with direction indicator
        if "flow_rate" in inputs:
            flow_box, flow_widget = ProtocolUI.create_float_input("Flow Rate:", inputs["flow_rate"], "mL/min")
            flow_direction = widgets.HTML(
                value=ProtocolUI.get_flow_direction_html(inputs["flow_rate"]),
                layout=widgets.Layout(margin='0px 0px 0px 10px')
            )
            flow_container = widgets.HBox([flow_box.children[0], flow_box.children[1], flow_direction], 
                                        layout=widgets.Layout(align_items='center'))
            flow_section = widgets.VBox([flow_container, widgets.HTML(value=help_texts.get("flow_rate", ""))])
            ui_elements.append(flow_section)
            widgets_dict["flow_rate"] = flow_widget
            widgets_dict["flow_direction"] = flow_direction
            
            # Set up observer for flow rate changes
            def update_flow_direction(change):
                widgets_dict["flow_direction"].value = ProtocolUI.get_flow_direction_html(change["new"])
            flow_widget.observe(update_flow_direction, names='value')
        
        # Create remaining inputs
        for key, value in inputs.items():
            if key == "flow_rate":
                continue  # Already handled above
                
            if key == "solvent_volume":
                box, widget = ProtocolUI.create_float_input("Solvent Volume:", value, "mL")
                help_html = widgets.HTML(value=help_texts.get("solvent_volume", ""))
            elif key == "rinse_volume":
                box, widget = ProtocolUI.create_float_input("Rinse Volume:", value, "mL")
                help_html = widgets.HTML(value=help_texts.get("rinse_volume", ""))
            elif key == "switch_time":
                box, widget = ProtocolUI.create_float_input("Switch Time:", value, "seconds")
                help_html = widgets.HTML(value=help_texts.get("switch_time", ""))
            elif key == "delay_time":
                box, widget = ProtocolUI.create_float_input("Delay Time:", value, "seconds")
                help_html = widgets.HTML(value=help_texts.get("delay_time", ""))
            else:
                box, widget = ProtocolUI.create_float_input(f"{key.replace('_', ' ').title()}:", value)
                help_html = widgets.HTML(value="")
                
            section = widgets.VBox([box, help_html])
            ui_elements.append(section)
            widgets_dict[key] = widget
        
        # Create submit button
        submit_button = widgets.Button(
            description='Create Protocol',
            button_style='primary',
            icon='check',
            layout=widgets.Layout(width='200px')
        )
        ui_elements.append(submit_button)
        widgets_dict["submit"] = submit_button
        
        # Create output widget
        output_widget = widgets.Output(layout=widgets.Layout(border='1px solid #ddd', padding='10px', margin='10px 0'))
        
        # Create form container
        form = widgets.VBox(ui_elements, layout=widgets.Layout(
            border='1px solid #ddd',
            padding='20px',
            margin='10px 0',
            border_radius='5px'
        ))
        
        # Set up submit button callback
        submit_button.on_click(submit_callback)
        
        return widgets_dict, form, output_widget
