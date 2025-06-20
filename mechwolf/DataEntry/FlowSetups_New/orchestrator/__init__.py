"""
Orchestrator - Phase 4 of FlowSetups workflow

This module provides the main application orchestration and modern UI
components for the complete FlowSetups workflow.
"""

from .flow_setup_main import FlowSetupMain
from .tailwind_components import TailwindComponents

__all__ = ['FlowSetupMain', 'TailwindComponents']