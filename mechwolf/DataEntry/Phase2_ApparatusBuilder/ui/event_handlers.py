"""
Event handlers for the tabbed apparatus designer.

Contains all event binding and handling logic.
"""


class EventHandlers:
    """Static methods for handling UI events."""
    
    @staticmethod
    def bind_events(designer_instance):
        """Bind all event handlers to widgets."""
        # Active components tab
        designer_instance.active_tab.add_button.on_click(designer_instance._add_harvard_pump)
        
        # Passive components tab
        designer_instance.passive_tab.add_vessel_btn.on_click(
            lambda b: designer_instance._add_passive_component('Vessel')
        )
        designer_instance.passive_tab.add_tmixer_btn.on_click(
            lambda b: designer_instance._add_passive_component('TMixer')
        )
        designer_instance.passive_tab.add_tube_btn.on_click(
            lambda b: designer_instance._add_passive_component('Tube')
        )
        
        # Connections tab
        designer_instance.connections_tab.add_connection_btn.on_click(
            designer_instance._add_connection
        )
        
        # Code generation
        designer_instance.generate_button.on_click(designer_instance._generate_code)
        designer_instance.copy_button.on_click(designer_instance._copy_code)
        
        # Tab change events
        designer_instance.tab_widget.observe(designer_instance._on_tab_change, names='selected_index')
        
        # Component selector events
        designer_instance.active_tab.component_selector.observe(
            designer_instance._on_active_component_selected, names='value'
        )
        designer_instance.passive_tab.component_selector.observe(
            designer_instance._on_passive_component_selected, names='value'
        )
        
        # Connection selector events
        designer_instance.connections_tab.connection_selector.observe(
            designer_instance._on_connection_selected, names='value'
        )