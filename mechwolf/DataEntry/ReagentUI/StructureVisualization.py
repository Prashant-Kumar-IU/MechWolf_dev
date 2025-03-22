"""Structure visualization utilities for chemical structures."""
import io
from typing import Optional, Tuple
from mechwolf.DataEntry.ReagentUI.utils import is_rdkit_available, safe_mol_from_smiles
import ipywidgets as widgets

class StructureVisualizer:
    """Visualizes chemical structures using RDKit."""
    
    @staticmethod
    def get_structure_image(smiles: str, size: Tuple[int, int] = (150, 150)) -> Optional[widgets.Image]:
        """
        Create an image widget from SMILES.
        
        Parameters:
        -----------
        smiles : str
            SMILES string
        size : tuple
            Image size as (width, height)
            
        Returns:
        --------
        ipywidgets.Image or None
            Image widget if successful, None otherwise
        """
        if not is_rdkit_available() or not smiles:
            return None
            
        try:
            from rdkit.Chem import Draw
            
            mol = safe_mol_from_smiles(smiles)
            if not mol:
                return None
                
            img = Draw.MolToImage(mol, size=size)
            
            # Convert PIL image to widget
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return widgets.Image(
                value=buffer.getvalue(),
                format='png',
                width=size[0],
                height=size[1]
            )
        except Exception:
            return None
    
    @staticmethod
    def get_structure_output(smiles: str, size: Tuple[int, int] = (180, 180)) -> widgets.Output:
        """
        Create an output widget with a structure visualization.
        
        Parameters:
        -----------
        smiles : str
            SMILES string
        size : tuple
            Image size as (width, height)
            
        Returns:
        --------
        ipywidgets.Output
            Output widget containing the structure image
        """
        from IPython.display import display
        
        output = widgets.Output(
            layout=widgets.Layout(
                height=f"{size[1]}px",
                width=f"{size[0]}px",
                margin="10px auto",
                border="1px solid #ddd"
            )
        )
        
        with output:
            if not is_rdkit_available():
                print("RDKit not available")
            elif not smiles:
                pass  # Empty output
            else:
                try:
                    from rdkit.Chem import Draw
                    
                    mol = safe_mol_from_smiles(smiles)
                    if mol:
                        img = Draw.MolToImage(mol, size=size)
                        display(img)
                    else:
                        print("Could not render structure.\nCheck SMILES format.")
                except Exception:
                    print("Could not render structure.\nCheck SMILES format.")
                    
        return output
