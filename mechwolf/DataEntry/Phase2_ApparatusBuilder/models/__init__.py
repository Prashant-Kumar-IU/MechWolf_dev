"""
Data models for Phase2_ApparatusBuilder.

Contains the core data structures used throughout the apparatus builder.
"""

from .component import ApparatusComponent
from .connection import ApparatusConnection

__all__ = ['ApparatusComponent', 'ApparatusConnection']