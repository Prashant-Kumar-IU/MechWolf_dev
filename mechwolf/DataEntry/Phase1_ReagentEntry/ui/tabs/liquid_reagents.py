"""
Liquid reagents tab implementation.

This module handles the liquid reagent entry interface, extracted from the
original monolithic UI file for better maintainability and separation of concerns.
"""

import ipywidgets as widgets
from typing import Dict, Any, Optional, Callable
from ..components.forms import ReagentForm
from ..components.base import SectionHeader, MessageArea
from ...core.services import ReagentService
from ...core.models import ReagentModel


class LiquidReagentsTab:
    """
    Tab for liquid reagent entry and management.
    
    This class handles all UI logic specific to liquid reagents,
    delegating business logic to the ReagentService.
    """
    
    def __init__(self, reagent_service: ReagentService):
        """
        Initialize liquid reagents tab.
        
        Args:
            reagent_service: Service for reagent operations
        """
        self.reagent_service = reagent_service
        self.on_reagent_saved = None  # Callback for when reagent is saved
        
        # Create the tab UI
        self._create_tab()
    
    def _create_tab(self) -> widgets.Widget:
        """Create the liquid reagents tab interface."""
        
        # Create header
        header = SectionHeader.create(
            "💧 Liquid Reagents",
            description="Add liquid reagents (solutions, solvents, etc.)"
        )
        
        # Create density warning area
        self.density_warning = MessageArea()
        
        # Create reagent form
        self.reagent_form = ReagentForm(
            reagent_type="liquid",
            on_save=self._handle_save_reagent
        )
        
        # Create tab content
        self.widget = widgets.VBox([
            header,
            widgets.HTML("<p>Add liquid reagents to your experiment. These are typically solutions, solvents, or other liquid compounds.</p>"),
            widgets.HTML("<p><strong>Note:</strong> Density values are required for liquid reagents to calculate volumes correctly.</p>"),
            self.density_warning.widget,
            self.reagent_form.widget
        ])
        
        return self.widget
    
    def _handle_save_reagent(self, form_data: Dict[str, Any], editing_reagent: Optional[ReagentModel]) -> bool:
        """
        Handle saving a reagent from the form.
        
        Args:
            form_data: Form data dictionary
            editing_reagent: ReagentModel being edited (None for new reagent)
            
        Returns:
            True if saved successfully
        """
        try:
            # Check density for liquid reagents
            density = form_data.get('density', 0)
            if not density or density <= 0:
                self.density_warning.show_warning(
                    "Density is required for liquid reagents and must be greater than 0. "
                    "Please update this value for accurate volume calculations."
                )
                return False
            else:
                self.density_warning.clear()
            
            if editing_reagent:
                # Update existing reagent
                new_reagent, errors = self.reagent_service.create_reagent_from_form_data(
                    form_data, "liquid"
                )
                
                if errors:
                    return False
                
                success, save_errors = self.reagent_service.update_reagent(
                    editing_reagent, new_reagent
                )
                
                if success and self.on_reagent_saved:
                    self.on_reagent_saved("updated", new_reagent)
                
                return success
            else:
                # Create new reagent
                reagent, errors = self.reagent_service.create_reagent_from_form_data(
                    form_data, "liquid"
                )
                
                if errors:
                    return False
                
                success, save_errors = self.reagent_service.save_reagent(reagent)
                
                if success and self.on_reagent_saved:
                    self.on_reagent_saved("added", reagent)
                
                return success
                
        except Exception as e:
            print(f"Error in liquid reagents tab: {e}")
            return False
    
    def populate_from_pubchem(self, compound_data: Dict[str, Any]):
        """
        Populate form with PubChem compound data.
        
        Args:
            compound_data: Dictionary with compound information
        """
        # Add density warning for PubChem imports
        if not compound_data.get('density'):
            self.density_warning.show_warning(
                "PubChem data imported successfully, but density value needs to be updated. "
                "Please enter the correct density for accurate volume calculations."
            )
        
        self.reagent_form.populate_from_pubchem(compound_data)
    
    def start_editing_reagent(self, reagent: ReagentModel):
        """
        Start editing an existing reagent.
        
        Args:
            reagent: ReagentModel to edit
        """
        if reagent.reagent_type != "liquid":
            raise ValueError("Cannot edit non-liquid reagent in liquid reagents tab")
        
        # Show density warning if density is missing or seems incorrect
        if not reagent.density or reagent.density <= 0:
            self.density_warning.show_warning(
                f"Density for {reagent.name} needs to be updated. "
                "Please enter the correct density for accurate volume calculations."
            )
        else:
            self.density_warning.clear()
        
        self.reagent_form.start_editing(reagent)
    
    def stop_editing(self):
        """Stop editing mode and return to add mode."""
        self.reagent_form.stop_editing()
        self.density_warning.clear()
    
    def clear_form(self):
        """Clear the reagent form."""
        self.reagent_form.clear_form()
        self.density_warning.clear()
    
    def set_reagent_saved_callback(self, callback: Callable):
        """
        Set callback for when reagent is saved.
        
        Args:
            callback: Function to call with (action, reagent) when reagent is saved
                     action is "added" or "updated"
        """
        self.on_reagent_saved = callback
    
    def get_widget(self) -> widgets.Widget:
        """Get the tab widget."""
        return self.widget


# Factory function for backward compatibility
def create_liquid_reagents_tab(reagent_service: ReagentService) -> LiquidReagentsTab:
    """
    Factory function to create a liquid reagents tab.
    
    Args:
        reagent_service: Service for reagent operations
        
    Returns:
        LiquidReagentsTab instance
    """
    return LiquidReagentsTab(reagent_service)


__all__ = ['LiquidReagentsTab', 'create_liquid_reagents_tab']