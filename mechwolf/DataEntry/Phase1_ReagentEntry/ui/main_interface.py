"""
Main interface coordinator for Phase 1 Reagent Entry.

This module provides the main UI coordinator that brings together all tabs
and manages their interactions, replacing the original monolithic UI class.
"""

import ipywidgets as widgets
from typing import Dict, Any, Optional
from IPython.display import display
from .tabs.solid_reagents import SolidReagentsTab
from .tabs.liquid_reagents import LiquidReagentsTab
from .tabs.search import SearchTab
from .tabs.display import DisplayTab
from .tabs.final_details import FinalDetailsTab
from .components.base import SectionHeader
from ..core.services import ReagentService, ExperimentService
from ..core.data_adapter import ReagentDataAdapter


class ReagentEntryInterface:
    """
    Main interface coordinator for reagent entry.
    
    This class orchestrates the interaction between different tabs and manages
    the overall UI state, replacing the original 1,427-line monolithic class.
    """
    
    def __init__(self, experiment_manager):
        """
        Initialize the main interface.
        
        Args:
            experiment_manager: ExperimentalMetadataManager instance
        """
        self.experiment_manager = experiment_manager
        
        # Create services
        self.data_adapter = ReagentDataAdapter(experiment_manager)
        self.reagent_service = ReagentService(self.data_adapter)
        self.experiment_service = ExperimentService(self.data_adapter)
        
        # Create tabs
        self._create_tabs()
        
        # Create main interface
        self._create_interface()
        
        # Set up inter-tab communication
        self._setup_tab_communication()
    
    def _create_tabs(self):
        """Create all tab instances."""
        self.solid_tab = SolidReagentsTab(self.reagent_service)
        self.liquid_tab = LiquidReagentsTab(self.reagent_service)
        self.search_tab = SearchTab(self.reagent_service)
        self.display_tab = DisplayTab(self.experiment_service, self.reagent_service)
        self.final_tab = FinalDetailsTab(self.experiment_service)
    
    def _create_interface(self):
        """Create the main tabbed interface."""
        # Create header
        header = widgets.HTML("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🧪 ReagentUI - Phase 1: Reagent Entry</h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0;'>
                Modular interface with modern experimental metadata backend
            </p>
        </div>
        """)
        
        # Create tab widget
        self.tab_widget = widgets.Tab()
        self.tab_widget.children = [
            self.solid_tab.get_widget(),
            self.liquid_tab.get_widget(),
            self.search_tab.get_widget(),
            self.display_tab.get_widget(),
            self.final_tab.get_widget()
        ]
        
        # Set tab titles with icons
        self.tab_widget.set_title(0, "🧱 Solid Reagents")
        self.tab_widget.set_title(1, "💧 Liquid Reagents")
        self.tab_widget.set_title(2, "🔍 PubChem Search")
        self.tab_widget.set_title(3, "📋 Current Reagents")
        self.tab_widget.set_title(4, "⚗️ Final Details")
        
        # Create main widget
        self.main_widget = widgets.VBox([
            header,
            self.tab_widget
        ])
    
    def _setup_tab_communication(self):
        """Set up communication between tabs."""
        
        # Search tab -> Reagent tabs (import compounds)
        self.search_tab.set_import_callback(self._handle_compound_import)
        
        # Display tab -> Reagent tabs (edit reagents)
        self.display_tab.set_edit_callback(self._handle_edit_reagent)
        
        # All reagent operations -> Display tab (refresh)
        self.solid_tab.set_reagent_saved_callback(self._handle_reagent_saved)
        self.liquid_tab.set_reagent_saved_callback(self._handle_reagent_saved)
        self.display_tab.set_deleted_callback(self._handle_reagent_deleted)
        
        # Final tab completion
        self.final_tab.set_completion_callback(self._handle_experiment_completed)
    
    def _handle_compound_import(self, compound_data: Dict[str, Any], reagent_type: str) -> bool:
        """
        Handle compound import from search tab.
        
        Args:
            compound_data: Compound data from PubChem
            reagent_type: "solid" or "liquid"
            
        Returns:
            True if import successful
        """
        try:
            # Switch to appropriate tab
            if reagent_type == "solid":
                self.tab_widget.selected_index = 0
                self.solid_tab.populate_from_pubchem(compound_data)
            elif reagent_type == "liquid":
                self.tab_widget.selected_index = 1
                self.liquid_tab.populate_from_pubchem(compound_data)
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"Error importing compound: {e}")
            return False
    
    def _handle_edit_reagent(self, reagent):
        """
        Handle edit reagent request from display tab.
        
        Args:
            reagent: ReagentModel to edit
        """
        try:
            # Switch to appropriate tab and start editing
            if reagent.reagent_type == "solid":
                self.tab_widget.selected_index = 0
                self.solid_tab.start_editing_reagent(reagent)
            elif reagent.reagent_type == "liquid":
                self.tab_widget.selected_index = 1
                self.liquid_tab.start_editing_reagent(reagent)
            
        except Exception as e:
            print(f"Error starting edit: {e}")
    
    def _handle_reagent_saved(self, action: str, reagent):
        """
        Handle reagent saved notification.
        
        Args:
            action: "added" or "updated"
            reagent: ReagentModel that was saved
        """
        # Refresh display tab
        self.display_tab.refresh_display()
        
        # Refresh final details tab (for limiting reagent changes)
        self.final_tab.refresh_display()
        
        print(f"✅ Reagent {action}: {reagent.name}")
    
    def _handle_reagent_deleted(self, reagent):
        """
        Handle reagent deleted notification.
        
        Args:
            reagent: ReagentModel that was deleted
        """
        # Refresh final details tab (for limiting reagent changes)
        self.final_tab.refresh_display()
        
        print(f"🗑️ Reagent deleted: {reagent.name}")
    
    def _handle_experiment_completed(self):
        """Handle experiment completion."""
        print("🎉 Experiment processing completed successfully!")
        print("You can now proceed to Phase 2: Apparatus Builder")
    
    def display(self):
        """Display the main interface."""
        display(self.main_widget)
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get current reagent data in old format for backward compatibility.
        
        Returns:
            Dictionary with current reagent data
        """
        return self.data_adapter.load_data()


# Backward compatibility alias
ReagentUI = ReagentEntryInterface


def launch_gui(experiment_manager):
    """
    Launch the ReagentUI interface for an experiment.
    
    Args:
        experiment_manager: ExperimentalMetadataManager instance
        
    Returns:
        ReagentEntryInterface instance
    """
    gui = ReagentEntryInterface(experiment_manager)
    gui.display()
    return gui


__all__ = ['ReagentEntryInterface', 'ReagentUI', 'launch_gui']