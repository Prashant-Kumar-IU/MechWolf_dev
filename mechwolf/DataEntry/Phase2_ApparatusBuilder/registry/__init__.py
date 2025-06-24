"""
Component registry and discovery system.

Handles dynamic component discovery and registration.
"""

from .component_registry import ComponentRegistry
from .component_discovery import discover_components

__all__ = ['ComponentRegistry', 'discover_components']