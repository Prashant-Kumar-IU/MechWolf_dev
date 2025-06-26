"""
PubChem search tab implementation.

This module handles the compound search interface, extracted from the
original monolithic UI file for better maintainability and separation of concerns.
"""

import ipywidgets as widgets
from typing import Dict, Any, List, Callable, Optional
from IPython.display import display, clear_output
from ..components.forms import SearchForm
from ..components.base import SearchResult, SectionHeader, StatusIndicator
from ...core.services import ReagentService


class SearchTab:
    """
    Tab for PubChem compound search and import.
    
    This class handles compound search UI and import functionality,
    delegating business logic to the ReagentService.
    """
    
    def __init__(self, reagent_service: ReagentService):
        """
        Initialize search tab.
        
        Args:
            reagent_service: Service for reagent operations
        """
        self.reagent_service = reagent_service
        self.search_results = []
        self.on_import_compound = None  # Callback for compound import
        
        # Create the tab UI
        self._create_tab()
    
    def _create_tab(self) -> widgets.Widget:
        """Create the search tab interface."""
        
        # Create header
        header = SectionHeader.create(
            "🔍 PubChem Search",
            description="Search for compounds and import them directly into your reagent forms"
        )
        
        # Create search form
        self.search_form = SearchForm(on_search=self._handle_search)
        
        # Create results area
        self.results_output = widgets.Output(
            layout=widgets.Layout(
                height='500px',
                border='1px solid #ddd',
                overflow_y='auto',
                padding='10px'
            )
        )
        
        # Create status indicator
        self.status = StatusIndicator()
        
        # Create tab content
        self.widget = widgets.VBox([
            header,
            self.search_form.widget,
            self.status.widget,
            widgets.HTML("<h5>Search Results:</h5>"),
            self.results_output
        ])
        
        return self.widget
    
    def _handle_search(self, query: str, search_type: str):
        """
        Handle search request.
        
        Args:
            query: Search query
            search_type: Type of search ('name', 'smiles', 'inchi', 'cas')
        """
        try:
            self.status.show_loading(f"Searching PubChem for '{query}' ({search_type})...")
            
            # Perform search using service
            results, errors = self.reagent_service.search_pubchem(query, search_type)
            
            if errors:
                self.status.show_error("Search failed")
                self.search_form.show_search_status(
                    f"Search error: {'; '.join(errors)}", "error"
                )
                self._clear_results()
                return
            
            # Store results and display them
            self.search_results = results
            self._display_results()
            
            # Update status
            self.status.show_success(f"Found {len(results)} results")
            self.search_form.show_search_status(
                f"Found {len(results)} compounds", "success"
            )
            
        except Exception as e:
            self.status.show_error("Search error")
            self.search_form.show_search_status(f"Search error: {str(e)}", "error")
            self._clear_results()
    
    def _display_results(self):
        """Display search results with import options."""
        with self.results_output:
            clear_output(wait=True)
            
            if not self.search_results:
                print("No compounds found")
                return
            
            for i, compound in enumerate(self.search_results):
                self._display_single_result(compound, i)
    
    def _display_single_result(self, compound: Dict[str, Any], index: int):
        """
        Display a single search result.
        
        Args:
            compound: Compound data dictionary
            index: Result index
        """
        # Create search result component
        result = SearchResult(compound)
        
        # Set up import callbacks
        result.set_import_callbacks(
            on_solid=lambda comp: self._handle_import(comp, "solid"),
            on_liquid=lambda comp: self._handle_import(comp, "liquid")
        )
        
        # Display the result
        display(result.container)
    
    def _handle_import(self, compound_data: Dict[str, Any], reagent_type: str):
        """
        Handle compound import request.
        
        Args:
            compound_data: Compound data to import
            reagent_type: "solid" or "liquid"
        """
        try:
            if self.on_import_compound:
                success = self.on_import_compound(compound_data, reagent_type)
                
                if success:
                    compound_name = compound_data.get('name', 'Unknown')
                    self.search_form.show_search_status(
                        f"✅ Imported {compound_name} as {reagent_type} reagent", 
                        "success"
                    )
                else:
                    self.search_form.show_search_status(
                        "Failed to import compound", "error"
                    )
            else:
                self.search_form.show_search_status(
                    "No import handler configured", "warning"
                )
                
        except Exception as e:
            self.search_form.show_search_status(
                f"Import error: {str(e)}", "error"
            )
    
    def _clear_results(self):
        """Clear the search results display."""
        with self.results_output:
            clear_output(wait=True)
            print("No results to display")
        
        self.search_results = []
    
    def set_import_callback(self, callback: Callable):
        """
        Set callback for compound import.
        
        Args:
            callback: Function to call with (compound_data, reagent_type)
                     Should return True if import successful
        """
        self.on_import_compound = callback
    
    def get_widget(self) -> widgets.Widget:
        """Get the tab widget."""
        return self.widget
    
    def clear_search(self):
        """Clear search results and status."""
        self._clear_results()
        self.status.clear()
        self.search_form.show_search_status("Ready to search", "info")


# Factory function for backward compatibility
def create_search_tab(reagent_service: ReagentService) -> SearchTab:
    """
    Factory function to create a search tab.
    
    Args:
        reagent_service: Service for reagent operations
        
    Returns:
        SearchTab instance
    """
    return SearchTab(reagent_service)


__all__ = ['SearchTab', 'create_search_tab']