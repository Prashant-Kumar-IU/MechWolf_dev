"""
User interface components for Phase 1 Reagent Entry.

This module contains all UI-related code including tabs, forms, and components,
separated from business logic for better maintainability and testability.
"""

from .main_interface import ReagentEntryInterface, ReagentUI, launch_gui

# Import tab creators for advanced usage
from .tabs.solid_reagents import create_solid_reagents_tab
from .tabs.liquid_reagents import create_liquid_reagents_tab
from .tabs.search import create_search_tab
from .tabs.display import create_display_tab
from .tabs.final_details import create_final_details_tab

# Import component factories
from .components.base import ButtonFactory, SectionHeader, MessageArea
from .components.forms import ReagentForm, SearchForm

__all__ = [
    # Main interfaces
    'ReagentEntryInterface',
    'ReagentUI',
    'launch_gui',
    
    # Tab creators
    'create_solid_reagents_tab',
    'create_liquid_reagents_tab', 
    'create_search_tab',
    'create_display_tab',
    'create_final_details_tab',
    
    # Component classes
    'ReagentForm',
    'SearchForm',
    'ButtonFactory',
    'SectionHeader', 
    'MessageArea'
]