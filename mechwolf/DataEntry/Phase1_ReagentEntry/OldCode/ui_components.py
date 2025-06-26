"""UI components for reagent entry forms."""
import ipywidgets as widgets
from typing import Dict, Any, Callable, Optional

# Try relative import first, fall back to absolute import
try:
    from .structure_visualization import StructureVisualization
except ImportError:
    try:
        from mechwolf.DataEntry.Phase1_ReagentEntry.structure_visualization import StructureVisualization
    except ImportError:
        # Fallback implementation
        class StructureVisualization:
            @staticmethod
            def get_structure_image(smiles, size=(150, 150)):
                return None

class UIComponents:
    """Factory for creating UI components."""
    
    @staticmethod
    def create_reagent_item(reagent: Dict[str, Any], is_solid: bool, 
                            on_edit: Callable, on_delete: Callable, 
                            index: int = 0) -> widgets.Widget:
        """
        Create a widget to display a reagent with edit/delete buttons.
        
        Parameters:
        -----------
        reagent : dict
            Reagent data
        is_solid : bool
            Whether the reagent is a solid
        on_edit : callable
            Callback for edit button
        on_delete : callable
            Callback for delete button
        index : int
            Index of the reagent in the list
            
        Returns:
        --------
        ipywidgets.Widget
            Widget displaying the reagent
        """
        bg_color = "#F0F7F4" if is_solid else "#EFF7FF"  # Light green for solids, light blue for liquids
        
        # Create structure visualization if possible
        smiles = reagent.get("SMILES", "") or reagent.get("smiles", "")
        structure_widget = None
        if smiles:
            structure_widget = StructureVisualization.get_structure_image(
                smiles, size=(120, 120)
            )
        
        # Get reagent properties with fallback names
        name = reagent.get("name", "Unknown")
        eq = reagent.get("eq", reagent.get("equivalents", "N/A"))
        mw = reagent.get("molecular_weight", reagent.get("molecular weight (in g/mol)", 0))
        position = reagent.get("position", reagent.get("syringe", "N/A"))
        
        # Type-specific information
        type_info = ""
        if is_solid:
            mass = reagent.get("mass", "N/A")
            type_info = f"<p style='margin: 2px 0;'><b>Mass:</b> {mass} mg</p>"
        else:
            volume = reagent.get("volume", "N/A")
            density = reagent.get("density", reagent.get("density (in g/mL)", 1.0))
            type_info = f"""
                <p style='margin: 2px 0;'><b>Volume:</b> {volume} mL</p>
                <p style='margin: 2px 0;'><b>Density:</b> {density} g/mL</p>
            """
        
        # Style for reagent item
        item_style = f"""
        <div style="padding: 8px; background-color: {bg_color}; border-radius: 4px; margin-bottom: 4px;">
            <h4 style="margin: 0 0 5px 0;">{name}</h4>
            <div style="display: flex; flex-direction: row;">
                <div style="flex: 1;">
                    <p style="margin: 2px 0;"><b>Eq:</b> {eq}</p>
                    <p style="margin: 2px 0;"><b>MW:</b> {mw} g/mol</p>
                </div>
                <div style="flex: 1;">
                    <p style="margin: 2px 0;"><b>Position:</b> {position}</p>
                    {type_info}
                </div>
            </div>
        </div>
        """
        
        # HTML widget for the reagent details
        html_widget = widgets.HTML(item_style)
        
        # Create buttons
        edit_button = widgets.Button(
            description="Edit",
            button_style="info",
            layout=widgets.Layout(width="60px"),
            style={"button_color": "#1E3A8A"}
        )
        
        delete_button = widgets.Button(
            description="Delete",
            button_style="danger",
            layout=widgets.Layout(width="70px"),
            style={"button_color": "#D72638"}
        )
        
        # Setup callbacks - pass index for identification
        edit_button.on_click(lambda b: on_edit(index, reagent))
        delete_button.on_click(lambda b: on_delete(index, reagent))
        
        # Container for buttons
        button_container = widgets.VBox(
            [edit_button, delete_button],
            layout=widgets.Layout(margin="0 0 0 10px", align_items="flex-start")
        )
        
        # Return an HBox containing the structure, HTML and buttons
        if structure_widget:
            return widgets.HBox(
                [structure_widget, html_widget, button_container],
                layout=widgets.Layout(
                    margin="2px 0",
                    align_items="center",
                    border=f"1px solid {'#90BE6D' if is_solid else '#577590'}",
                    border_radius="5px",
                    padding="5px"
                )
            )
        else:
            return widgets.HBox(
                [html_widget, button_container],
                layout=widgets.Layout(
                    margin="2px 0",
                    align_items="center",
                    border=f"1px solid {'#90BE6D' if is_solid else '#577590'}",
                    border_radius="5px",
                    padding="5px"
                )
            )
    
    @staticmethod
    def create_search_result_widget(compound: Dict[str, Any], 
                                   on_import_solid: Callable, 
                                   on_import_liquid: Callable) -> widgets.Widget:
        """
        Create a widget to display a search result with import buttons.
        
        Parameters:
        -----------
        compound : dict
            Compound data
        on_import_solid : callable
            Callback for import as solid button
        on_import_liquid : callable
            Callback for import as liquid button
            
        Returns:
        --------
        ipywidgets.Widget
            Widget displaying the search result
        """
        # Generate structure image
        smiles = compound.get('smiles', '')
        structure_img = None
        if smiles:
            structure_img = StructureVisualization.get_structure_image(
                smiles, size=(150, 150)
            )
        
        # Create info widget
        info_html = f"""
        <div style="padding-left: 10px;">
            <h4>{compound.get('name', 'Unknown')}</h4>
            <p><b>Formula:</b> {compound.get('formula', 'N/A')}</p>
            <p><b>Molecular Weight:</b> {compound.get('molecular_weight', 'N/A')} g/mol</p>
            <p><b>InChI Key:</b> {compound.get('inchikey', 'N/A')}</p>
            <p><b>SMILES:</b> {smiles}</p>
        </div>
        """
        
        info_widget = widgets.HTML(info_html)
        
        # Create import buttons
        import_solid_button = widgets.Button(
            description="Import as Solid",
            button_style="success",
            style={"button_color": "#3F704D"}
        )
        
        import_liquid_button = widgets.Button(
            description="Import as Liquid",
            button_style="info",
            style={"button_color": "#3A5D9F"}
        )
        
        # Set up callbacks
        import_solid_button.on_click(lambda b: on_import_solid(compound))
        import_liquid_button.on_click(lambda b: on_import_liquid(compound))
        
        # Arrange buttons
        buttons = widgets.VBox([
            import_solid_button,
            import_liquid_button
        ])
        
        # Create result container with structure + info + buttons
        if structure_img:
            result = widgets.HBox([
                structure_img,
                info_widget,
                buttons
            ])
        else:
            result = widgets.HBox([
                info_widget,
                buttons
            ])
        
        return widgets.VBox([
            result,
            widgets.HTML("<hr style='margin: 10px 0;'>")
        ], layout=widgets.Layout(margin="5px 0"))
    
    @staticmethod
    def create_form_field(widget: widgets.Widget, 
                         tooltip_text: str, 
                         error_style: bool = False) -> widgets.VBox:
        """
        Create a form field with tooltip.
        
        Parameters:
        -----------
        widget : widgets.Widget
            Input widget
        tooltip_text : str
            Text for tooltip
        error_style : bool
            Whether to style the tooltip as an error
            
        Returns:
        --------
        widgets.VBox
            Container with widget and tooltip
        """
        tooltip_color = "red" if error_style else "#666"
        tooltip_weight = "bold" if error_style else "normal"
        
        tooltip = widgets.HTML(
            f"<span style='font-size: 0.8em; color: {tooltip_color}; font-weight: {tooltip_weight};'>{tooltip_text}</span>"
        )
        
        if error_style:
            widget.style.description_width = 'initial'
            widget.layout.border = "2px solid red"
        else:
            widget.layout.border = ""
            
        return widgets.VBox([widget, tooltip])
    
    @staticmethod 
    def create_section_header(title: str, icon: str = "") -> widgets.HTML:
        """
        Create a styled section header.
        
        Parameters:
        -----------
        title : str
            Section title
        icon : str
            Optional emoji icon
            
        Returns:
        --------
        widgets.HTML
            Styled header widget
        """
        return widgets.HTML(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 8px; margin: 10px 0;'>
            <h3 style='color: white; margin: 0; text-align: center;'>
                {icon} {title}
            </h3>
        </div>
        """)