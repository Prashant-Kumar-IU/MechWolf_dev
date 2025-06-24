"""
UI tab builders for the tabbed apparatus designer.

Contains methods for creating the various tabs in the interface.
"""

import ipywidgets as widgets


class TabBuilders:
    """Static methods for building UI tabs."""
    
    @staticmethod
    def create_active_components_tab():
        """Create Tab 1: Active Components (Harvard Pumps)."""
        # Header
        header = widgets.HTML("<h3>💉 Active Components - Harvard Pumps</h3>")
        
        # Add component section
        add_section = widgets.VBox([
            widgets.HTML("<b>Add Harvard Pump:</b>"),
            widgets.Button(
                description="+ Add Harvard Pump",
                button_style='success',
                layout=widgets.Layout(width='200px')
            )
        ])
        
        # Component list container (scrollable HTML)
        active_components_display = widgets.HTML(
            value="<i>No active components added yet</i>",
            layout=widgets.Layout(height='300px', overflow='auto', 
                                border='1px solid #eee', padding='5px')
        )
        
        # Property editor with component selector
        active_component_selector = widgets.Dropdown(
            options=[],
            description="Select:",
            layout=widgets.Layout(width='200px')
        )
        
        active_property_editor = widgets.VBox([
            widgets.HTML("<b>Component Properties:</b>"),
            active_component_selector,
            widgets.HTML("<i>Select a component above to edit properties</i>")
        ])
        
        tab = widgets.VBox([
            header,
            add_section,
            widgets.HTML("<hr>"),
            active_property_editor,
            widgets.HTML("<hr>"),
            active_components_display
        ])
        
        # Store references for external access
        tab.add_button = add_section.children[1]
        tab.components_display = active_components_display
        tab.component_selector = active_component_selector
        tab.property_editor = active_property_editor
        
        return tab
    
    @staticmethod
    def create_passive_components_tab():
        """Create Tab 2: Passive Components (Vessels, T-Mixers)."""
        # Header
        header = widgets.HTML("<h3>🧪 Passive Components - Vessels, Mixers & Tubes</h3>")
        
        # Add component buttons
        add_vessel_btn = widgets.Button(
            description="🧪 Add Vessel",
            button_style='info',
            layout=widgets.Layout(width='140px', margin='2px')
        )
        
        add_tmixer_btn = widgets.Button(
            description="🔀 Add T-Mixer", 
            button_style='info',
            layout=widgets.Layout(width='140px', margin='2px')
        )
        
        add_tube_btn = widgets.Button(
            description="🔗 Add Tube",
            button_style='info', 
            layout=widgets.Layout(width='140px', margin='2px')
        )
        
        add_section = widgets.VBox([
            widgets.HTML("<b>Add Components:</b>"),
            widgets.HBox([add_vessel_btn, add_tmixer_btn, add_tube_btn])
        ])
        
        # Component list container (scrollable HTML)
        passive_components_display = widgets.HTML(
            value="<i>No passive components added yet</i>",
            layout=widgets.Layout(height='300px', overflow='auto',
                                border='1px solid #eee', padding='5px')
        )
        
        # Property editor with component selector
        passive_component_selector = widgets.Dropdown(
            options=[],
            description="Select:",
            layout=widgets.Layout(width='200px')
        )
        
        passive_property_editor = widgets.VBox([
            widgets.HTML("<b>Component Properties:</b>"),
            passive_component_selector,
            widgets.HTML("<i>Select a component above to edit properties</i>")
        ])
        
        tab = widgets.VBox([
            header,
            add_section,
            widgets.HTML("<hr>"),
            passive_property_editor,
            widgets.HTML("<hr>"),
            passive_components_display
        ])
        
        # Store references for external access
        tab.add_vessel_btn = add_vessel_btn
        tab.add_tmixer_btn = add_tmixer_btn
        tab.add_tube_btn = add_tube_btn
        tab.components_display = passive_components_display
        tab.component_selector = passive_component_selector
        tab.property_editor = passive_property_editor
        
        return tab
    
    @staticmethod
    def create_connections_tab():
        """Create Tab 3: Network Connections."""
        # Header
        header = widgets.HTML("<h3>🔗 Network Connections</h3>")
        
        # Connection builder
        from_component_dropdown = widgets.Dropdown(
            options=[],
            description="From:",
            layout=widgets.Layout(width='200px')
        )
        
        to_component_dropdown = widgets.Dropdown(
            options=[],
            description="To:",
            layout=widgets.Layout(width='200px')
        )
        
        tube_selection_dropdown = widgets.Dropdown(
            options=[],
            description="Tube:",
            layout=widgets.Layout(width='200px')
        )
        
        add_connection_btn = widgets.Button(
            description="Add Connection",
            button_style='primary',
            layout=widgets.Layout(width='150px')
        )
        
        connection_builder = widgets.VBox([
            widgets.HTML("<b>Create Connection:</b>"),
            widgets.HBox([
                from_component_dropdown,
                widgets.HTML(" → "),
                to_component_dropdown
            ]),
            widgets.HBox([
                tube_selection_dropdown,
                add_connection_btn
            ])
        ])
        
        # Connection editor section
        connection_selector = widgets.Dropdown(
            options=[],
            description="Select:",
            layout=widgets.Layout(width='300px')
        )
        
        connection_property_editor = widgets.VBox([
            widgets.HTML("<b>Edit Connection:</b>"),
            connection_selector,
            widgets.HTML("<i>Select a connection above to edit or delete</i>")
        ])
        
        # Connections list container (scrollable HTML)
        connections_display = widgets.HTML(
            value="<i>No connections created yet</i>",
            layout=widgets.Layout(height='200px', overflow='auto',
                                border='1px solid #eee', padding='5px')
        )
        
        # Network visualization (scrollable)
        network_display = widgets.Output(
            layout=widgets.Layout(height='200px', border='1px solid #ccc', overflow='auto')
        )
        
        tab = widgets.VBox([
            header,
            connection_builder,
            widgets.HTML("<hr>"),
            connection_property_editor,
            widgets.HTML("<hr>"),
            connections_display,
            widgets.HTML("<hr>"),
            widgets.HTML("<b>Network Overview:</b>"),
            network_display
        ])
        
        # Store references for external access
        tab.from_component_dropdown = from_component_dropdown
        tab.to_component_dropdown = to_component_dropdown
        tab.tube_selection_dropdown = tube_selection_dropdown
        tab.add_connection_btn = add_connection_btn
        tab.connection_selector = connection_selector
        tab.connection_property_editor = connection_property_editor
        tab.connections_display = connections_display
        tab.network_display = network_display
        
        return tab