"""
Export Manager - Simple JSON file export functionality

This module provides basic export functionality focused on JSON output
for apparatus configurations.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ExportManager:
    """Simple export manager for JSON configurations"""
    
    def __init__(self):
        pass
    
    def export_config(self, config: Dict[str, Any], export_format: str, 
                     output_file: Optional[str] = None) -> bool:
        """
        Export configuration to JSON format
        
        Args:
            config: Configuration dictionary to export
            export_format: Format to export to (only 'json' supported)
            output_file: Output file path, or None for default naming
        
        Returns:
            True if export successful, False otherwise
        """
        if export_format.lower() != 'json':
            print(f"❌ Only JSON export is supported, got: {export_format}")
            return False
        
        try:
            # Generate output filename if not provided
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"mechwolf_apparatus_export_{timestamp}.json"
            
            output_path = Path(output_file)
            
            # Create export-ready configuration
            export_config = self._prepare_export_config(config)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_config, f, indent=4, ensure_ascii=False, sort_keys=True)
            
            print(f"✅ Configuration exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting configuration: {e}")
            return False
    
    def _prepare_export_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare configuration for export"""
        export_config = config.copy()
        
        # Add export metadata
        export_config["export_info"] = {
            "exported_at": datetime.now().isoformat(),
            "exported_by": "MechWolf FlowSetups",
            "export_version": "2.0.0"
        }
        
        # Ensure proper structure
        if "version" not in export_config:
            export_config["version"] = "2.0.0"
        
        # Clean up any temporary fields
        if "metadata" in export_config:
            # Remove file-specific metadata that doesn't apply to exports
            metadata = export_config["metadata"].copy()
            metadata.pop("file_size", None)
            export_config["metadata"] = metadata
        
        return export_config
    
    def create_python_code_export(self, config: Dict[str, Any], 
                                 output_file: Optional[str] = None) -> bool:
        """
        Export configuration as Python code
        
        Args:
            config: Configuration dictionary
            output_file: Output file path for Python code
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"mechwolf_apparatus_code_{timestamp}.py"
            
            python_code = self._generate_python_code(config)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            print(f"✅ Python code exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting Python code: {e}")
            return False
    
    def _generate_python_code(self, config: Dict[str, Any]) -> str:
        """Generate Python code from configuration"""
        
        apparatus_config = config.get("apparatus_config", {})
        components = apparatus_config.get("components", {})
        connections = apparatus_config.get("connections", [])
        
        code_lines = [
            "# Generated MechWolf Apparatus Code",
            f"# Generated on: {datetime.now().isoformat()}",
            "# This code recreates the apparatus configuration",
            "",
            "import mechwolf as mw",
            "",
        ]
        
        # Generate component definitions
        code_lines.extend(self._generate_component_code(components))
        
        # Generate apparatus definition
        apparatus_name = apparatus_config.get("name", "Generated_Apparatus")
        code_lines.extend([
            "",
            "# Build Apparatus",
            f'A = mw.Apparatus("{apparatus_name}")',
        ])
        
        # Generate connections
        if connections:
            code_lines.append("")
            code_lines.append("# Add Connections")
            for conn in connections:
                from_comp = conn.get("from", "")
                to_comp = conn.get("to", "")
                tube = conn.get("tube", "")
                code_lines.append(f"A.add({from_comp}, {to_comp}, {tube})")
        
        # Add visualization calls
        code_lines.extend([
            "",
            "# Visualize the apparatus",
            "A.visualize()",
            "# A.describe()  # Uncomment for detailed description",
            "",
            "# Create protocol (example)",
            "# P = mw.Protocol(A)",
            "# P.add(pump_name, start='0s', duration='10min', rate='5 mL/min')",
            "# experiment = P.execute()",
        ])
        
        return "\n".join(code_lines)
    
    def _generate_component_code(self, components: Dict[str, Any]) -> list:
        """Generate Python code for component definitions"""
        code_lines = []
        
        # Process passive components first
        passive_components = components.get("passive", [])
        if passive_components:
            code_lines.append("# Define Passive Components")
            
            for comp in passive_components:
                comp_code = self._generate_single_component_code(comp)
                if comp_code:
                    code_lines.extend(comp_code)
        
        # Process active components
        active_components = components.get("active", [])
        if active_components:
            if passive_components:
                code_lines.append("")
            code_lines.append("# Define Active Components")
            
            for comp in active_components:
                comp_code = self._generate_single_component_code(comp)
                if comp_code:
                    code_lines.extend(comp_code)
        
        return code_lines
    
    def _generate_single_component_code(self, component: Dict[str, Any]) -> list:
        """Generate code for a single component"""
        comp_type = component.get("type", "")
        comp_name = component.get("name", "")
        
        if not comp_name or not comp_type:
            return []
        
        code_lines = []
        
        if comp_type == "Vessel":
            description = component.get("description", "")
            if description:
                code_lines.append(f'{comp_name} = mw.Vessel("{description}", name="{comp_name}")')
            else:
                code_lines.append(f'{comp_name} = mw.Vessel("{comp_name}")')
        
        elif comp_type == "Tube":
            length = component.get("length", "")
            id_val = component.get("ID", "")
            od_val = component.get("OD", "")
            material = component.get("material", "PFA")
            
            code_lines.append(f'{comp_name} = mw.Tube(')
            code_lines.append(f'    length="{length}",')
            code_lines.append(f'    ID="{id_val}",')
            code_lines.append(f'    OD="{od_val}",')
            code_lines.append(f'    material="{material}"')
            code_lines.append(')')
        
        elif "Mixer" in comp_type:
            code_lines.append(f'{comp_name} = mw.{comp_type}(name="{comp_name}")')
        
        elif comp_type == "HarvardSyringePump":
            serial_port = component.get("serial_port", "")
            syringe_volume = component.get("syringe_volume", "")
            syringe_diameter = component.get("syringe_diameter", "")
            
            code_lines.append(f'{comp_name} = mw.HarvardSyringePump(')
            code_lines.append(f'    syringe_volume="{syringe_volume}",')
            code_lines.append(f'    syringe_diameter="{syringe_diameter}",')
            code_lines.append(f'    serial_port="{serial_port}",')
            code_lines.append(f'    name="{comp_name}"')
            code_lines.append(')')
        
        elif comp_type == "ViciValve":
            serial_port = component.get("serial_port", "")
            mapping = component.get("mapping", {})
            
            if mapping:
                # Create mapping variable
                mapping_var = f"{comp_name}_mapping"
                mapping_items = [f'{vessel}: {port}' for vessel, port in mapping.items()]
                mapping_str = '{' + ', '.join(mapping_items) + '}'
                
                code_lines.append(f'{mapping_var} = {mapping_str}')
                code_lines.append(f'{comp_name} = mw.ViciValve(')
                code_lines.append(f'    serial_port="{serial_port}",')
                code_lines.append(f'    mapping={mapping_var},')
                code_lines.append(f'    name="{comp_name}"')
                code_lines.append(')')
        
        elif comp_type == "VarianPump":
            serial_port = component.get("serial_port", "")
            max_rate = component.get("max_rate", "")
            
            code_lines.append(f'{comp_name} = mw.VarianPump(')
            code_lines.append(f'    serial_port="{serial_port}",')
            code_lines.append(f'    max_rate="{max_rate}",')
            code_lines.append(f'    name="{comp_name}"')
            code_lines.append(')')
        
        else:
            # Generic component
            code_lines.append(f'{comp_name} = mw.{comp_type}(name="{comp_name}")')
        
        return code_lines