"""
Time Variable Manager for Phase 3 Protocol Development

Handles time variable definitions and calculations for generating clean,
readable MechWolf protocol code with timedelta variables.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import timedelta


class TimeVariableManager:
    """Manages time variables for protocol code generation"""
    
    def __init__(self):
        """Initialize time variable manager"""
        self.variables = {}  # {name: timedelta_object}
        self.variable_order = []  # Ordered list of variable names
        self.current_time_var = "current"  # Name of current time tracking variable
        
        # Default variables that are commonly used
        self.default_variables = {
            "current": timedelta(seconds=0),
            "switch": timedelta(seconds=45)
        }
        
        self.variables.update(self.default_variables)
        self.variable_order = ["current", "switch"]
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create time variable management widgets"""
        
        # Variable definition section
        self.var_name_input = widgets.Text(
            placeholder="e.g., PPh3, H2O, reaction_time",
            description="Variable:",
            layout=widgets.Layout(width='200px')
        )
        
        self.var_value_input = widgets.Text(
            placeholder="e.g., 2min, 30s, 1.5h",
            description="Duration:",
            layout=widgets.Layout(width='150px')
        )
        
        self.add_var_button = widgets.Button(
            description="Add Variable",
            button_style='success',
            layout=widgets.Layout(width='120px')
        )
        self.add_var_button.on_click(self._add_variable)
        
        # Variable list display
        self.variables_display = widgets.Output(
            layout=widgets.Layout(
                height='200px',
                border='1px solid #ccc',
                padding='10px'
            )
        )
        
        # Preset buttons for common variables
        self.preset_buttons = widgets.HBox([
            self._create_preset_button("PPh3", "2min"),
            self._create_preset_button("H2O", "1min"),
            self._create_preset_button("flush", "15min"),
            self._create_preset_button("reaction", "30min")
        ])
        
        # Current time tracking
        self.current_time_input = widgets.Text(
            value="current",
            description="Current time var:",
            layout=widgets.Layout(width='200px')
        )
        self.current_time_input.observe(self._on_current_time_change, names='value')
        
        self._refresh_display()
    
    def _create_preset_button(self, name: str, duration: str) -> widgets.Button:
        """Create a preset variable button"""
        button = widgets.Button(
            description=f"{name} ({duration})",
            button_style='info',
            layout=widgets.Layout(width='120px')
        )
        
        def on_click(b):
            self.add_time_variable(name, duration)
            self._refresh_display()
        
        button.on_click(on_click)
        return button
    
    def _add_variable(self, button):
        """Add a new time variable"""
        name = self.var_name_input.value.strip()
        duration = self.var_value_input.value.strip()
        
        if not name or not duration:
            print("❌ Please enter both variable name and duration")
            return
        
        try:
            self.add_time_variable(name, duration)
            self.var_name_input.value = ""
            self.var_value_input.value = ""
            self._refresh_display()
            print(f"✅ Added variable: {name} = {duration}")
        except Exception as e:
            print(f"❌ Error adding variable: {e}")
    
    def _on_current_time_change(self, change):
        """Handle current time variable name change"""
        new_name = change['new'].strip()
        if new_name and new_name != self.current_time_var:
            self.current_time_var = new_name
            # Ensure current time variable exists
            if new_name not in self.variables:
                self.variables[new_name] = timedelta(seconds=0)
                if new_name not in self.variable_order:
                    self.variable_order.insert(0, new_name)
            self._refresh_display()
    
    def add_time_variable(self, name: str, duration_str: str) -> bool:
        """
        Add a time variable
        
        Args:
            name: Variable name (e.g., 'PPh3', 'H2O')
            duration_str: Duration string (e.g., '2min', '30s', '1.5h')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                raise ValueError(f"Invalid variable name '{name}'. Use letters, numbers, and underscores only.")
            
            # Parse duration
            duration = self._parse_duration_string(duration_str)
            
            # Add to variables
            self.variables[name] = duration
            
            # Add to order if new
            if name not in self.variable_order:
                # Insert non-special variables after 'current' and 'switch'
                if name in ['current', 'switch']:
                    if name not in self.variable_order:
                        self.variable_order.insert(len([v for v in self.variable_order if v in ['current', 'switch']]), name)
                else:
                    self.variable_order.append(name)
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to add variable '{name}': {e}")
    
    def remove_time_variable(self, name: str) -> bool:
        """Remove a time variable"""
        if name in ['current', 'switch']:
            print(f"⚠️ Cannot remove built-in variable '{name}'")
            return False
        
        if name in self.variables:
            del self.variables[name]
            if name in self.variable_order:
                self.variable_order.remove(name)
            return True
        
        return False
    
    def get_variable_definitions_code(self) -> List[str]:
        """
        Generate code lines for variable definitions
        
        Returns:
            List of code lines defining variables
        """
        lines = []
        
        for var_name in self.variable_order:
            if var_name in self.variables:
                duration = self.variables[var_name]
                
                if duration.total_seconds() == 0 and var_name == "current":
                    lines.append(f"{var_name} = timedelta(minutes = 0)")
                elif duration.total_seconds() % 60 == 0:
                    # Use minutes if it's a whole number of minutes
                    minutes = int(duration.total_seconds() / 60)
                    if minutes == 0:
                        lines.append(f"{var_name} = timedelta(seconds = 0)")
                    else:
                        lines.append(f"{var_name} = timedelta(minutes = {minutes})")
                elif duration.total_seconds() % 3600 == 0:
                    # Use hours if it's a whole number of hours
                    hours = int(duration.total_seconds() / 3600)
                    lines.append(f"{var_name} = timedelta(hours = {hours})")
                else:
                    # Use seconds for fractional values
                    seconds = int(duration.total_seconds())
                    lines.append(f"{var_name} = timedelta(seconds = {seconds})")
        
        return lines
    
    def get_current_time_expression(self) -> str:
        """Get the current time variable expression"""
        return self.current_time_var
    
    def generate_time_increment_code(self, duration_expr: str) -> str:
        """
        Generate code for incrementing current time
        
        Args:
            duration_expr: Duration expression (e.g., 'PPh3', 'H2O + switch')
            
        Returns:
            Code line for incrementing current time
        """
        return f"{self.current_time_var} += {duration_expr}"
    
    def _parse_duration_string(self, duration_str: str) -> timedelta:
        """Parse duration string to timedelta object"""
        duration_str = duration_str.strip().lower()
        
        # Handle common patterns
        patterns = [
            (r'^(\d+\.?\d*)\s*s(ec)?$', 'seconds'),
            (r'^(\d+\.?\d*)\s*min(ute)?s?$', 'minutes'),
            (r'^(\d+\.?\d*)\s*h(our)?s?$', 'hours'),
            (r'^(\d+\.?\d*)\s*ms$', 'milliseconds'),
        ]
        
        for pattern, unit in patterns:
            match = re.match(pattern, duration_str)
            if match:
                value = float(match.group(1))
                
                if unit == 'seconds':
                    return timedelta(seconds=value)
                elif unit == 'minutes':
                    return timedelta(minutes=value)
                elif unit == 'hours':
                    return timedelta(hours=value)
                elif unit == 'milliseconds':
                    return timedelta(milliseconds=value)
        
        raise ValueError(f"Invalid duration format: '{duration_str}'. Use formats like '30s', '2min', '1.5h'")
    
    def _refresh_display(self):
        """Refresh the variables display"""
        with self.variables_display:
            clear_output(wait=True)
            
            if not self.variables:
                print("No time variables defined.")
                return
            
            print("⏱️ DEFINED TIME VARIABLES")
            print("=" * 40)
            
            for var_name in self.variable_order:
                if var_name in self.variables:
                    duration = self.variables[var_name]
                    seconds = duration.total_seconds()
                    
                    # Format duration nicely
                    if seconds == 0:
                        duration_str = "0s"
                    elif seconds % 3600 == 0:
                        duration_str = f"{int(seconds/3600)}h"
                    elif seconds % 60 == 0:
                        duration_str = f"{int(seconds/60)}min"
                    else:
                        duration_str = f"{int(seconds)}s"
                    
                    # Mark special variables
                    marker = ""
                    if var_name == self.current_time_var:
                        marker = " (current time)"
                    elif var_name == "switch":
                        marker = " (switch time)"
                    
                    print(f"  {var_name} = {duration_str}{marker}")
            
            print("\n💡 Use these variables in your procedure timing")
    
    def create_interface(self) -> widgets.Widget:
        """Create the time variable management interface"""
        
        # Header
        header = widgets.HTML("""
        <div style='background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0; color: #2e7d32;'>⏱️ Time Variable Manager</h4>
            <p style='margin-bottom: 0;'>
                Define reusable time variables for clean protocol code generation.
            </p>
        </div>
        """)
        
        # Variable creation section
        creation_section = widgets.VBox([
            widgets.HTML("<h5>Add New Variable:</h5>"),
            widgets.HBox([self.var_name_input, self.var_value_input, self.add_var_button]),
            widgets.HTML("<h6>Quick Presets:</h6>"),
            self.preset_buttons
        ])
        
        # Current time tracking
        current_time_section = widgets.VBox([
            widgets.HTML("<h5>Current Time Tracking:</h5>"),
            self.current_time_input,
            widgets.HTML("<small>Variable name used for tracking current protocol time</small>")
        ])
        
        # Variables display
        display_section = widgets.VBox([
            widgets.HTML("<h5>Defined Variables:</h5>"),
            self.variables_display
        ])
        
        return widgets.VBox([
            header,
            creation_section,
            current_time_section,
            display_section
        ])
    
    def validate_expression(self, expression: str) -> Tuple[bool, str]:
        """
        Validate a time expression using defined variables
        
        Args:
            expression: Time expression to validate (e.g., 'PPh3 + H2O')
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Check if all variable names in expression are defined
            # Simple regex to find variable names (alphanumeric + underscore)
            var_names = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression)
            
            undefined_vars = []
            for var_name in var_names:
                if var_name not in self.variables and var_name not in ['timedelta']:
                    undefined_vars.append(var_name)
            
            if undefined_vars:
                return False, f"Undefined variables: {', '.join(undefined_vars)}"
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def get_variables_dict(self) -> Dict[str, timedelta]:
        """Get copy of variables dictionary"""
        return self.variables.copy()
    
    def set_variables_from_dict(self, variables_dict: Dict[str, Any]):
        """Set variables from dictionary (for loading saved state)"""
        self.variables = {}
        self.variable_order = []
        
        # Convert string durations to timedelta objects if needed
        for name, value in variables_dict.items():
            if isinstance(value, str):
                try:
                    duration = self._parse_duration_string(value)
                    self.variables[name] = duration
                except:
                    # Skip invalid entries
                    continue
            elif isinstance(value, timedelta):
                self.variables[name] = value
            elif isinstance(value, (int, float)):
                # Assume seconds
                self.variables[name] = timedelta(seconds=value)
        
        # Rebuild variable order
        special_vars = ['current', 'switch']
        self.variable_order = [v for v in special_vars if v in self.variables]
        self.variable_order.extend([v for v in self.variables if v not in special_vars])
        
        self._refresh_display()