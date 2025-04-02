from datetime import timedelta
import ipywidgets as widgets
from IPython.display import display, HTML

"""
This module defines a class `ProtocolAlgorithm` that creates a protocol for controlling syringe pumps.
Classes:
    ProtocolAlgorithm: A class to create and manage a protocol for syringe pumps.
Methods:
    __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        Initializes the ProtocolAlgorithm with a given protocol and components.
    create_protocol(self) -> Protocol:
        Creates a protocol based on user input for flow rate, solvent volume, rinse volume, and switch time.
        Returns:
            Protocol: The created protocol with the specified parameters.
"""
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import re


class ProtocolAlgorithm:
    def __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        self.protocol = protocol
        self.components = components

    def create_protocol(self) -> Protocol:
        # Create improved widgets with better styling
        style = {'description_width': '150px'}
        layout = widgets.Layout(width='350px', margin='10px 0px 10px 0px')
        
        # Display title
        display(HTML('<h2 style="color:#4682B4;">Protocol Parameters</h2>'))
        
        # Create widgets with numeric inputs and units
        flow_rate_widget = widgets.FloatText(
            description='Flow Rate:',
            style=style,
            layout=layout,
            value=5.0
        )
        flow_rate_unit = widgets.Label(value='mL/min')
        
        # Add a dynamic indicator for flow direction
        flow_direction_indicator = widgets.HTML(
            value='<span style="color:green;font-weight:bold">→ Infusing</span>',
            layout=widgets.Layout(margin='0px 0px 0px 10px')
        )
        
        solvent_volume_widget = widgets.FloatText(
            description='Solvent Volume:',
            style=style,
            layout=layout,
            value=10.0
        )
        solvent_unit = widgets.Label(value='mL')
        
        rinse_volume_widget = widgets.FloatText(
            description='Rinse Volume:',
            style=style,
            layout=layout,
            value=5.0
        )
        rinse_unit = widgets.Label(value='mL')
        
        switch_time_widget = widgets.FloatText(
            description='Switch Time:',
            style=style,
            layout=layout,
            value=30.0
        )
        switch_time_unit = widgets.Label(value='seconds')
        
        # Create better output and button widgets
        output_widget = widgets.Output(layout=widgets.Layout(border='1px solid #ddd', padding='10px', margin='10px 0'))
        
        submit_button = widgets.Button(
            description='Create Protocol',
            button_style='primary',
            icon='check',
            layout=widgets.Layout(width='200px')
        )
        
        # Create horizontal layouts for inputs with their units
        flow_box = widgets.HBox([flow_rate_widget, flow_rate_unit, flow_direction_indicator], layout=widgets.Layout(align_items='center'))
        solvent_box = widgets.HBox([solvent_volume_widget, solvent_unit], layout=widgets.Layout(align_items='center'))
        rinse_box = widgets.HBox([rinse_volume_widget, rinse_unit], layout=widgets.Layout(align_items='center'))
        switch_box = widgets.HBox([switch_time_widget, switch_time_unit], layout=widgets.Layout(align_items='center'))
        
        # Add descriptions with help text
        flow_help = widgets.HTML(value='<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Final flow rate for both syringes combined. Negative values indicate withdrawal.</p>')
        solvent_help = widgets.HTML(value='<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Volume of solvent to be used.</p>')
        rinse_help = widgets.HTML(value='<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Volume of rinse solvent.</p>')
        switch_help = widgets.HTML(value='<p style="color:#666;font-style:italic;margin:0px 0px 15px 10px;">Stall time to allow for syringe switching.</p>')
        
        # Create sections with inputs and their help text
        flow_section = widgets.VBox([flow_box, flow_help])
        solvent_section = widgets.VBox([solvent_box, solvent_help])
        rinse_section = widgets.VBox([rinse_box, rinse_help])
        switch_section = widgets.VBox([switch_box, switch_help])
        
        # Create a container for the form
        form = widgets.VBox([
            flow_section, 
            solvent_section, 
            rinse_section, 
            switch_section, 
            submit_button
        ], layout=widgets.Layout(
            border='1px solid #ddd',
            padding='20px',
            margin='10px 0',
            border_radius='5px'
        ))
        
        # Display the form and output
        display(form, output_widget)
        
        # Function to update flow direction indicator when flow rate changes
        def update_flow_direction(_):
            current_rate = flow_rate_widget.value
            if current_rate > 0:
                flow_direction_indicator.value = '<span style="color:green;font-weight:bold">→ Infusing</span>'
            elif current_rate < 0:
                flow_direction_indicator.value = '<span style="color:blue;font-weight:bold">← Withdrawing</span>'
            else:
                flow_direction_indicator.value = '<span style="color:gray;font-weight:bold">○ Stopped</span>'
        
        # Observe changes to flow rate
        flow_rate_widget.observe(update_flow_direction, names='value')
        
        def on_submit_clicked(b):
            # Hide the form when protocol is created
            form.layout.display = 'none'
            
            with output_widget:
                output_widget.clear_output()
                try:
                    flow_rate = flow_rate_widget.value
                    solvent_volume = solvent_volume_widget.value
                    rinse_volume = rinse_volume_widget.value
                    switch_time = switch_time_widget.value
                    
                    # Validate inputs - allow negative flow rate for withdrawal
                    if flow_rate == 0:
                        raise ValueError("Flow rate cannot be zero")
                    if solvent_volume <= 0:
                        raise ValueError("Solvent volume must be positive")
                    if rinse_volume <= 0:
                        raise ValueError("Rinse volume must be positive")
                    if switch_time < 0:
                        raise ValueError("Switch time cannot be negative")
                    
                    # Determine if infusing or withdrawing
                    direction = "infusing" if flow_rate > 0 else "withdrawing"
                    
                    display(HTML(f'<h3 style="color:green">Processing Protocol with:</h3>'))
                    display(HTML(f'<ul><li>Flow Rate: {flow_rate} mL/min ({direction})</li><li>Solvent Volume: {solvent_volume} mL</li><li>Rinse Volume: {rinse_volume} mL</li><li>Switch Time: {switch_time} seconds</li></ul>'))
                    
                    switch = timedelta(seconds=switch_time)
                    current = timedelta(seconds=0)

                    # Two syringes are being used so dividing by 2:
                    # Keep the sign for withdrawal/infusion direction
                    pump_rate = flow_rate / 2

                    # Use absolute values for time calculations but keep sign for rate
                    abs_pump_rate = abs(pump_rate)
                    rinse_time = timedelta(seconds=(rinse_volume / abs_pump_rate * 60))
                    active_time = timedelta(seconds=(solvent_volume / abs_pump_rate * 60))

                    print("Active time =", active_time)
                    print("Rinse time =", rinse_time)

                    # ...existing code for protocol creation...
                    if isinstance(self.components[0], HarvardSyringePump):
                        # Dual-channel pump
                        self.protocol.add(
                            self.components[0],
                            start=current,
                            duration=active_time,
                            rate=f"{pump_rate} mL/min",
                        )
                    else:
                        # Single-channel pumps
                        self.protocol.add(
                            self.components[0],
                            start=current,
                            duration=active_time,
                            rate=f"{pump_rate} mL/min",
                        )
                        self.protocol.add(
                            self.components[1],
                            start=current,
                            duration=active_time,
                            rate=f"{pump_rate} mL/min",
                        )

                    current += active_time
                    current += switch

                    if isinstance(self.components[0], HarvardSyringePump):
                        # Dual-channel pump
                        self.protocol.add(
                            self.components[0],
                            start=current,
                            duration=rinse_time,
                            rate=f"{pump_rate} mL/min",
                        )
                    else:
                        # Single-channel pumps
                        self.protocol.add(
                            self.components[0],
                            start=current,
                            duration=rinse_time,
                            rate=f"{pump_rate} mL/min",
                        )
                        self.protocol.add(
                            self.components[1],
                            start=current,
                            duration=rinse_time,
                            rate=f"{pump_rate} mL/min",
                        )

                    current += rinse_time

                    print(f"TOTAL TIME: {current}")
                    display(HTML(f'<p style="color:green;font-weight:bold">Protocol successfully created!</p>'))
                    
                except ValueError as e:
                    # Show the form again if there's an error
                    form.layout.display = 'block'
                    display(HTML(f'<p style="color:red;font-weight:bold">Error: {e}</p>'))
                
        # Attach the callback to the button click event
        submit_button.on_click(on_submit_clicked)
        
        # Return the protocol but now it will be populated after the user clicks the submit button
        return self.protocol