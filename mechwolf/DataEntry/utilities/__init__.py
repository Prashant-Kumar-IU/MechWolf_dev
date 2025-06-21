"""
MechWolf DataEntry Utilities

Essential utility functions for the MechWolf DataEntry system.

Available utilities:
    GetNotebookName: Jupyter notebook naming utilities
    SerialPortViewer: Hardware discovery and serial port management
    TLCInputForm: Analysis data input forms
    Calibration tools: Instrument calibration utilities
"""

# Import main utility functions for easy access
try:
    from .GetNotebookName import get_notebook_json_name
except ImportError:
    # Fallback function if GetNotebookName is not available
    def get_notebook_json_name():
        """Fallback function for notebook naming"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"experiment_{timestamp}.json"

try:
    from .SerialPortViewer import SerialPortViewer
except ImportError:
    class SerialPortViewer:
        """Fallback SerialPortViewer class"""
        def __init__(self):
            print("Warning: SerialPortViewer dependencies not available")
        
        def run(self):
            print("SerialPortViewer not available - install required dependencies")

try:
    from .TLCInputForm import TLCInputForm
except ImportError:
    class TLCInputForm:
        """Fallback TLCInputForm class"""
        def __init__(self, experiment_manager):
            self.experiment = experiment_manager
            print("Warning: TLCInputForm dependencies not available")
        
        def run(self):
            print("TLCInputForm not available - install required dependencies")

__all__ = [
    'get_notebook_json_name',
    'SerialPortViewer', 
    'TLCInputForm'
]