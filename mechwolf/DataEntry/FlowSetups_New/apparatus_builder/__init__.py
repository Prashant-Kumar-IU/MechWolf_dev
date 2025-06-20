"""
Apparatus Builder - Phase 2 of FlowSetups workflow

This module provides connection building and validation interfaces
for creating apparatus topologies.
"""

from .connection_gui import ConnectionGUI
from .connection_validator import ConnectionValidator

__all__ = ['ConnectionGUI', 'ConnectionValidator']