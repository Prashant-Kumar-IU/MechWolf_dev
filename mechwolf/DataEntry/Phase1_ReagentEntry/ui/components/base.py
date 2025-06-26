"""
Base UI components for reagent entry forms.

This module contains reusable base components that can be used across
different tabs and interfaces, extracted from the original monolithic UI.
"""

import ipywidgets as widgets
from typing import Dict, Any, Callable, Optional, List
from ...utils.imports import get_structure_visualization

# Get structure visualization through centralized import
StructureVisualization = get_structure_visualization()


class BaseFormField:
    """Base class for form fields with validation and tooltips."""
    
    @staticmethod
    def create_field(widget: widgets.Widget, tooltip_text: str, 
                    error_style: bool = False) -> widgets.VBox:
        """
        Create a form field with tooltip and error styling.
        
        Args:
            widget: Input widget
            tooltip_text: Tooltip/help text
            error_style: Whether to style as error
            
        Returns:
            VBox containing widget and tooltip
        """
        tooltip_color = "red" if error_style else "#666"
        tooltip_weight = "bold" if error_style else "normal"
        
        tooltip = widgets.HTML(
            f"<span style='font-size: 0.8em; color: {tooltip_color}; "
            f"font-weight: {tooltip_weight};'>{tooltip_text}</span>"
        )
        
        if error_style:
            widget.layout.border = "2px solid red"
        else:
            widget.layout.border = ""
            
        return widgets.VBox([widget, tooltip])


class MessageArea:
    """Reusable message display component."""
    
    def __init__(self):
        self.widget = widgets.HTML("")
    
    def show_success(self, message: str):
        """Display a success message."""
        self.widget.value = f"""
        <div style='color: green; padding: 10px; background-color: #EEFFEE; 
                    border-radius: 5px; margin: 10px 0; border: 1px solid #90BE6D;'>
            <b>✅ {message}</b>
        </div>
        """
    
    def show_error(self, message: str):
        """Display an error message."""
        self.widget.value = f"""
        <div style='color: red; padding: 10px; background-color: #FFEEEE; 
                    border-radius: 5px; margin: 10px 0; border: 1px solid #FFD2D2;'>
            <b>❌ {message}</b>
        </div>
        """
    
    def show_warning(self, message: str):
        """Display a warning message."""
        self.widget.value = f"""
        <div style='color: #B45309; padding: 10px; background-color: #FEF3C7; 
                    border-radius: 5px; margin: 10px 0; border: 1px solid #F59E0B;'>
            <b>⚠️ {message}</b>
        </div>
        """
    
    def show_info(self, message: str):
        """Display an info message."""
        self.widget.value = f"""
        <div style='color: #1E40AF; padding: 10px; background-color: #EFF6FF; 
                    border-radius: 5px; margin: 10px 0; border: 1px solid #3B82F6;'>
            <b>ℹ️ {message}</b>
        </div>
        """
    
    def show_errors(self, errors: List[str]):
        """Display multiple error messages."""
        if not errors:
            self.clear()
            return
        
        error_html = """
        <div style='color: red; padding: 10px; background-color: #FFEEEE; 
                    border-radius: 5px; margin: 10px 0; border: 1px solid #FFD2D2;'>
            <b>Please correct the following errors:</b>
            <ul style='margin: 5px 0 0 20px;'>
        """
        for error in errors:
            error_html += f"<li>{error}</li>"
        error_html += "</ul></div>"
        
        self.widget.value = error_html
    
    def clear(self):
        """Clear the message area."""
        self.widget.value = ""


class StructurePreview:
    """Component for displaying chemical structure previews."""
    
    def __init__(self, size: tuple = (200, 200)):
        """
        Initialize structure preview component.
        
        Args:
            size: (width, height) tuple for structure image
        """
        self.size = size
        self.widget = widgets.Output(
            layout=widgets.Layout(
                width=f"{size[0]}px", 
                height=f"{size[1]}px",
                border="1px solid #ddd",
                margin="10px 0"
            )
        )
    
    def update(self, smiles: str):
        """
        Update the structure display with new SMILES.
        
        Args:
            smiles: SMILES string to display
        """
        self.widget.clear_output()
        with self.widget:
            if smiles and smiles.strip():
                vis = StructureVisualization.get_structure_image(smiles, size=self.size)
                if vis:
                    from IPython.display import display
                    display(vis)
                else:
                    print("Could not render structure.\nCheck SMILES format.")
            else:
                print("No SMILES provided")


class StatusIndicator:
    """Component for showing loading/status indicators."""
    
    def __init__(self):
        self.widget = widgets.HTML("")
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading indicator."""
        self.widget.value = f"""
        <div style='color: #3B82F6; padding: 8px; text-align: center;'>
            <span style='font-size: 1.2em;'>⏳</span> {message}
        </div>
        """
    
    def show_success(self, message: str = "Complete"):
        """Show success indicator."""
        self.widget.value = f"""
        <div style='color: #10B981; padding: 8px; text-align: center;'>
            <span style='font-size: 1.2em;'>✅</span> {message}
        </div>
        """
    
    def show_error(self, message: str = "Error"):
        """Show error indicator."""
        self.widget.value = f"""
        <div style='color: #EF4444; padding: 8px; text-align: center;'>
            <span style='font-size: 1.2em;'>❌</span> {message}
        </div>
        """
    
    def clear(self):
        """Clear the indicator."""
        self.widget.value = ""


class SectionHeader:
    """Component for creating styled section headers."""
    
    @staticmethod
    def create(title: str, icon: str = "", description: str = "") -> widgets.HTML:
        """
        Create a styled section header.
        
        Args:
            title: Section title
            icon: Optional emoji icon
            description: Optional description text
            
        Returns:
            HTML widget with styled header
        """
        desc_html = f"<p style='color: #f0f0f0; margin: 5px 0 0 0;'>{description}</p>" if description else ""
        
        return widgets.HTML(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='color: white; margin: 0; text-align: center;'>
                {icon} {title}
            </h3>
            {desc_html}
        </div>
        """)


class ButtonFactory:
    """Factory for creating styled buttons with consistent styling."""
    
    @staticmethod
    def create_primary(description: str, width: str = "auto") -> widgets.Button:
        """Create a primary action button."""
        return widgets.Button(
            description=description,
            button_style="primary",
            layout=widgets.Layout(width=width)
        )
    
    @staticmethod
    def create_success(description: str, width: str = "auto") -> widgets.Button:
        """Create a success/save button."""
        return widgets.Button(
            description=description,
            button_style="success",
            layout=widgets.Layout(width=width)
        )
    
    @staticmethod
    def create_warning(description: str, width: str = "auto") -> widgets.Button:
        """Create a warning/edit button."""
        return widgets.Button(
            description=description,
            button_style="warning",
            layout=widgets.Layout(width=width)
        )
    
    @staticmethod
    def create_danger(description: str, width: str = "auto") -> widgets.Button:
        """Create a danger/delete button."""
        return widgets.Button(
            description=description,
            button_style="danger",
            layout=widgets.Layout(width=width)
        )
    
    @staticmethod
    def create_info(description: str, width: str = "auto") -> widgets.Button:
        """Create an info button."""
        return widgets.Button(
            description=description,
            button_style="info",
            layout=widgets.Layout(width=width)
        )


class FormContainer:
    """Container for forms with consistent styling."""
    
    @staticmethod
    def create(children: List[widgets.Widget], reagent_type: str = "solid") -> widgets.VBox:
        """
        Create a styled form container.
        
        Args:
            children: List of widgets to include in form
            reagent_type: "solid" or "liquid" for color coding
            
        Returns:
            VBox with styled container
        """
        bg_color = "#F0F7F4" if reagent_type == "solid" else "#EFF7FF"
        border_color = "#90BE6D" if reagent_type == "solid" else "#577590"
        
        return widgets.VBox(
            children,
            layout=widgets.Layout(
                border=f"1px solid {border_color}",
                padding="15px",
                margin="10px 0",
                background_color=bg_color,
                border_radius="5px"
            )
        )


class SearchResult:
    """Component for displaying search results with import buttons."""
    
    def __init__(self, compound_data: Dict[str, Any]):
        """
        Initialize search result component.
        
        Args:
            compound_data: Dictionary with compound information
        """
        self.compound_data = compound_data
        self.on_import_solid = None
        self.on_import_liquid = None
        
        # Create structure preview
        smiles = compound_data.get('smiles', '')
        self.structure = StructurePreview(size=(150, 150))
        if smiles:
            self.structure.update(smiles)
        
        # Create info display
        self.info = self._create_info_display()
        
        # Create import buttons
        self.buttons = self._create_buttons()
        
        # Arrange components
        components = [self.info, self.buttons]
        if smiles:  # Only add structure if we have SMILES
            self.widget = widgets.HBox([self.structure.widget] + components)
        else:
            self.widget = widgets.HBox(components)
        
        # Add container styling
        self.container = widgets.VBox([
            self.widget,
            widgets.HTML("<hr style='margin: 10px 0;'>")
        ], layout=widgets.Layout(
            border="1px solid #ddd",
            margin="5px 0",
            padding="10px",
            border_radius="5px"
        ))
    
    def _create_info_display(self) -> widgets.HTML:
        """Create the compound information display."""
        info_html = f"""
        <div style="padding: 10px;">
            <h4>{self.compound_data.get('name', 'Unknown')}</h4>
            <p><b>Formula:</b> {self.compound_data.get('formula', 'N/A')}</p>
            <p><b>Molecular Weight:</b> {self.compound_data.get('molecular_weight', 'N/A')} g/mol</p>
            <p><b>InChI Key:</b> {self.compound_data.get('inchikey', 'N/A')}</p>
            <p><b>SMILES:</b> {self.compound_data.get('smiles', 'N/A')}</p>
        </div>
        """
        return widgets.HTML(info_html)
    
    def _create_buttons(self) -> widgets.VBox:
        """Create the import buttons."""
        import_solid_btn = ButtonFactory.create_success("Import as Solid")
        import_solid_btn.style.button_color = "#3F704D"
        
        import_liquid_btn = ButtonFactory.create_info("Import as Liquid")
        import_liquid_btn.style.button_color = "#3A5D9F"
        
        # Set up callbacks
        import_solid_btn.on_click(lambda b: self._handle_import("solid"))
        import_liquid_btn.on_click(lambda b: self._handle_import("liquid"))
        
        return widgets.VBox([import_solid_btn, import_liquid_btn])
    
    def _handle_import(self, reagent_type: str):
        """Handle import button clicks."""
        if reagent_type == "solid" and self.on_import_solid:
            self.on_import_solid(self.compound_data)
        elif reagent_type == "liquid" and self.on_import_liquid:
            self.on_import_liquid(self.compound_data)
    
    def set_import_callbacks(self, on_solid: Callable, on_liquid: Callable):
        """Set callbacks for import buttons."""
        self.on_import_solid = on_solid
        self.on_import_liquid = on_liquid


__all__ = [
    'BaseFormField',
    'MessageArea',
    'StructurePreview',
    'StatusIndicator', 
    'SectionHeader',
    'ButtonFactory',
    'FormContainer',
    'SearchResult'
]