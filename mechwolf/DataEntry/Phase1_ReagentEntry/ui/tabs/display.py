"""
Reagents display tab implementation.

This module handles the current reagents display interface, extracted from the
original monolithic UI file for better maintainability and separation of concerns.
"""

import ipywidgets as widgets
from typing import Dict, Any, List, Callable, Optional
from IPython.display import display, clear_output
from ..components.base import SectionHeader, ButtonFactory, MessageArea
from ...core.services import ReagentService, ExperimentService
from ...core.models import ReagentModel


class ReagentDisplayItem:
    """Component for displaying a single reagent with edit/delete options."""
    
    def __init__(self, reagent: ReagentModel, index: int):
        """
        Initialize reagent display item.
        
        Args:
            reagent: ReagentModel to display
            index: Index in the reagent list
        """
        self.reagent = reagent
        self.index = index
        self.on_edit = None
        self.on_delete = None
        
        self._create_display()
    
    def _create_display(self):
        """Create the reagent display UI."""
        # Basic reagent info
        name = self.reagent.name
        mw = self.reagent.molecular_weight
        eq = self.reagent.equivalents
        position = self.reagent.position
        
        info_html = f"""
        <div style="padding: 10px; background-color: {'#F0F7F4' if self.reagent.reagent_type == 'solid' else '#EFF7FF'}; 
                    border-radius: 5px; margin: 5px 0;">
            <h4 style="margin: 0 0 5px 0; color: {'#3F704D' if self.reagent.reagent_type == 'solid' else '#3A5D9F'};">
                {name} ({self.reagent.reagent_type.title()})
            </h4>
            <p style="margin: 2px 0;"><b>MW:</b> {mw} g/mol | <b>Eq:</b> {eq} | <b>Position:</b> {position}</p>
        """
        
        # Add type-specific information
        if self.reagent.reagent_type == "liquid" and self.reagent.density:
            info_html += f'<p style="margin: 2px 0;"><b>Density:</b> {self.reagent.density} g/mL</p>'
        
        # Add chemical identifiers if available
        if self.reagent.smiles:
            info_html += f'<p style="margin: 2px 0; font-size: 0.9em;"><b>SMILES:</b> {self.reagent.smiles}</p>'
        
        info_html += "</div>"
        
        self.info_widget = widgets.HTML(info_html)
        
        # Create action buttons
        self.edit_button = ButtonFactory.create_warning(f"Edit", "120px")
        self.delete_button = ButtonFactory.create_danger(f"Delete", "120px")
        
        # Set up button callbacks
        self.edit_button.on_click(self._handle_edit)
        self.delete_button.on_click(self._handle_delete)
        
        # Arrange components
        button_container = widgets.VBox([
            self.edit_button,
            self.delete_button
        ], layout=widgets.Layout(margin="0 0 0 10px"))
        
        self.widget = widgets.HBox([
            self.info_widget,
            button_container
        ], layout=widgets.Layout(
            margin="5px 0",
            align_items="center"
        ))
    
    def _handle_edit(self, button):
        """Handle edit button click."""
        if self.on_edit:
            self.on_edit(self.reagent)
    
    def _handle_delete(self, button):
        """Handle delete button click."""
        if self.on_delete:
            self.on_delete(self.reagent)
    
    def set_callbacks(self, on_edit: Callable, on_delete: Callable):
        """Set callbacks for edit and delete buttons."""
        self.on_edit = on_edit
        self.on_delete = on_delete


class DisplayTab:
    """
    Tab for displaying current reagents in the experiment.
    
    This class handles the display of all reagents with edit/delete functionality,
    delegating business logic to the services.
    """
    
    def __init__(self, experiment_service: ExperimentService, reagent_service: ReagentService):
        """
        Initialize display tab.
        
        Args:
            experiment_service: Service for experiment operations
            reagent_service: Service for reagent operations
        """
        self.experiment_service = experiment_service
        self.reagent_service = reagent_service
        self.on_edit_reagent = None  # Callback for editing reagent
        self.on_reagent_deleted = None  # Callback for reagent deletion
        
        # Create the tab UI
        self._create_tab()
    
    def _create_tab(self) -> widgets.Widget:
        """Create the display tab interface."""
        
        # Create header
        header = SectionHeader.create(
            "📋 Current Reagents",
            description="View and manage reagents in your experiment"
        )
        
        # Create refresh button
        self.refresh_button = ButtonFactory.create_info("🔄 Refresh")
        self.refresh_button.on_click(lambda b: self.refresh_display())
        
        # Create message area for feedback
        self.message_area = MessageArea()
        
        # Create reagents display area
        self.reagents_output = widgets.Output(
            layout=widgets.Layout(
                height='500px',
                border='1px solid #ddd',
                overflow_y='auto',
                padding='10px'
            )
        )
        
        # Create summary area
        self.summary_area = widgets.HTML("")
        
        # Create tab content
        self.widget = widgets.VBox([
            header,
            widgets.HBox([self.refresh_button], layout=widgets.Layout(margin="0 0 10px 0")),
            self.message_area.widget,
            self.summary_area,
            self.reagents_output
        ])
        
        # Initial display
        self.refresh_display()
        
        return self.widget
    
    def refresh_display(self):
        """Refresh the reagents display."""
        try:
            # Get current experiment
            experiment = self.experiment_service.get_current_experiment()
            
            # Update summary
            self._update_summary(experiment)
            
            # Display reagents
            self._display_reagents(experiment)
            
            self.message_area.clear()
            
        except Exception as e:
            self.message_area.show_error(f"Error refreshing display: {str(e)}")
    
    def _update_summary(self, experiment):
        """Update the experiment summary."""
        solid_count = len(experiment.solid_reagents)
        liquid_count = len(experiment.liquid_reagents)
        total_count = solid_count + liquid_count
        
        limiting_reagent = experiment.limiting_reagent
        limiting_text = limiting_reagent.name if limiting_reagent else "None (set eq=1.0 for limiting reagent)"
        
        summary_html = f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 10px 0; color: #1E40AF;">Experiment Summary</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                <div><b>Total Reagents:</b> {total_count}</div>
                <div><b>Solid Reagents:</b> {solid_count}</div>
                <div><b>Liquid Reagents:</b> {liquid_count}</div>
                <div><b>Limiting Reagent:</b> {limiting_text}</div>
            </div>
        </div>
        """
        
        self.summary_area.value = summary_html
    
    def _display_reagents(self, experiment):
        """Display all reagents in the experiment."""
        with self.reagents_output:
            clear_output(wait=True)
            
            # Display solid reagents
            if experiment.solid_reagents:
                print("🧱 SOLID REAGENTS")
                print("=" * 50)
                for i, reagent in enumerate(experiment.solid_reagents):
                    self._display_reagent_item(reagent, i)
                print()
            
            # Display liquid reagents
            if experiment.liquid_reagents:
                print("💧 LIQUID REAGENTS")
                print("=" * 50)
                for i, reagent in enumerate(experiment.liquid_reagents):
                    self._display_reagent_item(reagent, i)
                print()
            
            # Show message if no reagents
            if not experiment.solid_reagents and not experiment.liquid_reagents:
                print("No reagents added yet.")
                print("Use the solid or liquid reagent tabs to add reagents to your experiment.")
    
    def _display_reagent_item(self, reagent: ReagentModel, index: int):
        """
        Display a single reagent item.
        
        Args:
            reagent: ReagentModel to display
            index: Index in the list
        """
        # Create display item
        item = ReagentDisplayItem(reagent, index)
        item.set_callbacks(
            on_edit=self._handle_edit_reagent,
            on_delete=self._handle_delete_reagent
        )
        
        # Display the item
        display(item.widget)
    
    def _handle_edit_reagent(self, reagent: ReagentModel):
        """
        Handle edit reagent request.
        
        Args:
            reagent: ReagentModel to edit
        """
        try:
            if self.on_edit_reagent:
                self.on_edit_reagent(reagent)
                self.message_area.show_info(f"Switched to {reagent.reagent_type} reagents tab to edit {reagent.name}")
            else:
                self.message_area.show_warning("No edit handler configured")
                
        except Exception as e:
            self.message_area.show_error(f"Error starting edit: {str(e)}")
    
    def _handle_delete_reagent(self, reagent: ReagentModel):
        """
        Handle delete reagent request.
        
        Args:
            reagent: ReagentModel to delete
        """
        try:
            # Confirm deletion (in a real UI, this would be a proper dialog)
            print(f"⚠️ Are you sure you want to delete {reagent.name}?")
            
            # Perform deletion
            success, errors = self.reagent_service.delete_reagent(reagent)
            
            if success:
                self.message_area.show_success(f"Deleted {reagent.name}")
                self.refresh_display()
                
                # Notify callback
                if self.on_reagent_deleted:
                    self.on_reagent_deleted(reagent)
            else:
                error_msg = "; ".join(errors) if errors else "Unknown error"
                self.message_area.show_error(f"Failed to delete {reagent.name}: {error_msg}")
                
        except Exception as e:
            self.message_area.show_error(f"Error deleting reagent: {str(e)}")
    
    def set_edit_callback(self, callback: Callable):
        """
        Set callback for editing reagents.
        
        Args:
            callback: Function to call with (reagent) when edit is requested
        """
        self.on_edit_reagent = callback
    
    def set_deleted_callback(self, callback: Callable):
        """
        Set callback for reagent deletion.
        
        Args:
            callback: Function to call with (reagent) when reagent is deleted
        """
        self.on_reagent_deleted = callback
    
    def get_widget(self) -> widgets.Widget:
        """Get the tab widget."""
        return self.widget


# Factory function for backward compatibility
def create_display_tab(experiment_service: ExperimentService, reagent_service: ReagentService) -> DisplayTab:
    """
    Factory function to create a display tab.
    
    Args:
        experiment_service: Service for experiment operations
        reagent_service: Service for reagent operations
        
    Returns:
        DisplayTab instance
    """
    return DisplayTab(experiment_service, reagent_service)


__all__ = ['DisplayTab', 'ReagentDisplayItem', 'create_display_tab']