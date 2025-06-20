"""
Structure Visualization

Enhanced structure visualization that works with the existing ReagentUI 
StructureVisualization or provides fallback functionality.
"""

from typing import Optional, Dict, Any
import warnings

try:
    from ..ReagentUI.StructureVisualization import StructureVisualization as BaseStructureViz
    STRUCTURE_VIZ_AVAILABLE = True
except ImportError:
    BaseStructureViz = None
    STRUCTURE_VIZ_AVAILABLE = False

try:
    import ipywidgets as widgets
    from IPython.display import display, HTML, Image
    DISPLAY_AVAILABLE = True
except ImportError:
    widgets = None
    DISPLAY_AVAILABLE = False


class StructureVisualization:
    """Enhanced structure visualization for reagents"""
    
    def __init__(self):
        """Initialize structure visualization"""
        if STRUCTURE_VIZ_AVAILABLE:
            self.base_viz = BaseStructureViz()
        else:
            self.base_viz = None
            if DISPLAY_AVAILABLE:
                warnings.warn("Base structure visualization not available - using fallback")
    
    def display_structure(self, inchi: Optional[str] = None, 
                         compound_id: Optional[str] = None,
                         name: Optional[str] = None) -> bool:
        """
        Display molecular structure
        
        Args:
            inchi: InChI string
            compound_id: PubChem compound ID
            name: Compound name
            
        Returns:
            True if structure was displayed, False otherwise
        """
        if not DISPLAY_AVAILABLE:
            return False
            
        # Try base visualization first
        if self.base_viz:
            try:
                if inchi:
                    return self.base_viz.display_from_inchi(inchi)
                elif compound_id:
                    return self.base_viz.display_from_pubchem_id(compound_id)
                elif name:
                    return self.base_viz.display_from_name(name)
            except Exception as e:
                print(f"Warning: Base structure visualization failed: {e}")
        
        # Fallback to PubChem image
        return self._display_pubchem_fallback(compound_id, name)
    
    def _display_pubchem_fallback(self, compound_id: Optional[str] = None,
                                name: Optional[str] = None) -> bool:
        """
        Fallback structure display using PubChem images
        
        Args:
            compound_id: PubChem compound ID
            name: Compound name
            
        Returns:
            True if image was displayed, False otherwise
        """
        if not DISPLAY_AVAILABLE:
            return False
            
        image_url = None
        
        if compound_id:
            image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{compound_id}/PNG"
        elif name:
            # Note: This would require an additional API call to get CID from name
            # For now, we'll just show a placeholder
            pass
        
        if image_url:
            try:
                html_content = f"""
                <div style='text-align: center; padding: 10px;'>
                    <img src='{image_url}' alt='Molecular structure' 
                         style='max-width: 300px; max-height: 300px; border: 1px solid #ccc;'
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div style='display: none; color: #666; font-style: italic;'>
                        Structure image not available
                    </div>
                </div>
                """
                display(HTML(html_content))
                return True
            except Exception as e:
                print(f"Warning: Failed to display structure image: {e}")
        
        return False
    
    def create_structure_widget(self, inchi: Optional[str] = None,
                              compound_id: Optional[str] = None,
                              name: Optional[str] = None) -> Optional[widgets.Widget]:
        """
        Create widget for interactive structure display
        
        Args:
            inchi: InChI string
            compound_id: PubChem compound ID
            name: Compound name
            
        Returns:
            Widget for structure display or None if not available
        """
        if not DISPLAY_AVAILABLE:
            return None
            
        # Try base visualization widget first
        if self.base_viz and hasattr(self.base_viz, 'create_widget'):
            try:
                return self.base_viz.create_widget(inchi=inchi, compound_id=compound_id, name=name)
            except Exception as e:
                print(f"Warning: Base structure widget creation failed: {e}")
        
        # Fallback widget
        return self._create_fallback_widget(compound_id, name)
    
    def _create_fallback_widget(self, compound_id: Optional[str] = None,
                               name: Optional[str] = None) -> Optional[widgets.Widget]:
        """
        Create fallback widget for structure display
        
        Args:
            compound_id: PubChem compound ID
            name: Compound name
            
        Returns:
            Widget for structure display
        """
        if not widgets:
            return None
            
        output = widgets.Output()
        
        def show_structure():
            with output:
                output.clear_output(wait=True)
                success = self._display_pubchem_fallback(compound_id, name)
                if not success:
                    print("Structure not available")
        
        # Create button to show structure
        button = widgets.Button(
            description="🧪 Show Structure",
            button_style='info',
            layout=widgets.Layout(width='150px')
        )
        button.on_click(lambda x: show_structure())
        
        # Show structure immediately if possible
        show_structure()
        
        return widgets.VBox([button, output])
    
    def export_structure(self, inchi: str, format: str = 'png') -> Optional[bytes]:
        """
        Export structure to specified format
        
        Args:
            inchi: InChI string
            format: Export format ('png', 'svg', 'mol')
            
        Returns:
            Structure data as bytes or None if export failed
        """
        if self.base_viz and hasattr(self.base_viz, 'export_structure'):
            try:
                return self.base_viz.export_structure(inchi, format)
            except Exception as e:
                print(f"Warning: Structure export failed: {e}")
        
        return None
    
    def is_available(self) -> bool:
        """Check if structure visualization is available"""
        return DISPLAY_AVAILABLE and (self.base_viz is not None or True)  # Fallback always available
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        if self.base_viz and hasattr(self.base_viz, 'get_supported_formats'):
            try:
                return self.base_viz.get_supported_formats()
            except Exception:
                pass
        
        return ['png']  # Fallback only supports PNG via PubChem