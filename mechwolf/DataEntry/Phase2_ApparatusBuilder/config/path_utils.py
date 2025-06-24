"""
Path utilities for cross-platform compatibility.

Provides dynamic path resolution to avoid hardcoded paths.
"""

import os
import platform
from pathlib import Path


def get_contrib_path():
    """Get the contrib components path dynamically."""
    try:
        # Try to find mechwolf package root
        current_file = Path(__file__)
        
        # Navigate up to find mechwolf root
        # Current: mechwolf/DataEntry/Phase2_ApparatusBuilder/config/path_utils.py
        # Target:  mechwolf/components/contrib
        mechwolf_root = current_file.parent.parent.parent.parent
        contrib_path = mechwolf_root / 'components' / 'contrib'
        
        if contrib_path.exists():
            return str(contrib_path)
        else:
            # Fallback to relative path
            return str(Path(__file__).parent.parent.parent.parent / 'components' / 'contrib')
            
    except Exception:
        # Last resort fallback
        return os.path.join(os.path.dirname(__file__), '../../../../components/contrib')


def get_default_serial_port():
    """Get default serial port based on platform."""
    system = platform.system()
    
    if system == 'Windows':
        return 'COM1'
    elif system == 'Darwin':  # macOS
        return '/dev/tty.usbserial'
    else:  # Linux and others
        return '/dev/ttyUSB0'


def get_mechwolf_root():
    """Get the root directory of the mechwolf package."""
    try:
        current_file = Path(__file__)
        # Navigate up to mechwolf root
        return current_file.parent.parent.parent.parent
    except Exception:
        return Path(__file__).parent.parent.parent.parent