"""
Application settings and configuration.

Contains default settings and configuration options.
"""

from .path_utils import get_contrib_path, get_default_serial_port


DEFAULT_SETTINGS = {
    'contrib_path': get_contrib_path(),  # Dynamic path resolution
    'default_tube_type': 'fat_tube',
    'default_tube_length': '1 ft',
    'default_serial_port': get_default_serial_port(),  # Cross-platform serial port
    'ui_theme': 'default'
}