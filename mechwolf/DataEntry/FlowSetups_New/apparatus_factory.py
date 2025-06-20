"""
Apparatus Factory - Factory pattern for creating configured MechWolf apparatus

This module provides a factory interface similar to the old FlowSetups system,
allowing users to create fully configured apparatus with a simple factory call.

Usage:
    from mechwolf.DataEntry.FlowSetups_New import ApparatusFactory
    A = ApparatusFactory.create_apparatus_from_config('my_config.json')
    A = ApparatusFactory.create_apparatus_from_components(components, connections)
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import mechwolf as mw

from .data_manager.json_handler import JSONHandler
from .data_manager.schema_validator import SchemaValidator


class ApparatusFactory:
    """Factory for creating MechWolf apparatus from configurations"""
    
    @classmethod
    def create_apparatus_from_config(cls, config_file: str, 
                                   apparatus_name: Optional[str] = None) -> mw.Apparatus:
        """
        Create a MechWolf Apparatus from a JSON configuration file
        
        Args:
            config_file: Path to JSON configuration file
            apparatus_name: Optional name for the apparatus (overrides config)
            
        Returns:
            Fully configured MechWolf Apparatus ready for use
            
        Example:
            A = ApparatusFactory.create_apparatus_from_config('birch_reduction.json')
            P = mw.Protocol(A)
            # Continue with protocol definition...
        """
        # Load and validate configuration
        data_manager = JSONHandler(config_file)
        config = data_manager.load_config()
        
        if not config:
            raise ValueError(f"Failed to load configuration from {config_file}")
        
        # Extract apparatus configuration
        apparatus_config = config.get("apparatus_config", {})
        if not apparatus_config:
            raise ValueError("No apparatus_config found in configuration file")
        
        # Create apparatus
        name = apparatus_name or apparatus_config.get("name", "Generated_Apparatus")
        return cls._build_apparatus_from_config(apparatus_config, name)
    
    @classmethod
    def create_apparatus_from_components(cls, components: Dict[str, Any], 
                                       connections: List[Dict[str, Any]],
                                       apparatus_name: str = "Generated_Apparatus") -> mw.Apparatus:
        """
        Create a MechWolf Apparatus from component and connection dictionaries
        
        Args:
            components: Dictionary with 'active' and 'passive' component lists
            connections: List of connection dictionaries
            apparatus_name: Name for the apparatus
            
        Returns:
            Fully configured MechWolf Apparatus
            
        Example:
            components = {
                "active": [pump_config, valve_config],
                "passive": [vessel_config, tube_config]
            }
            connections = [{"from": "vessel1", "to": "pump1", "tube": "tube1"}]
            A = ApparatusFactory.create_apparatus_from_components(components, connections)
        """
        apparatus_config = {
            "name": apparatus_name,
            "components": components,
            "connections": connections
        }
        
        return cls._build_apparatus_from_config(apparatus_config, apparatus_name)
    
    @classmethod
    def create_apparatus_from_flow_setup(cls, flow_setup_main, 
                                        apparatus_name: str = "FlowSetup_Apparatus") -> mw.Apparatus:
        """
        Create apparatus from a FlowSetupMain instance
        
        Args:
            flow_setup_main: FlowSetupMain instance with configured components
            apparatus_name: Name for the apparatus
            
        Returns:
            Fully configured MechWolf Apparatus
        """
        current_config = flow_setup_main.get_current_config()
        apparatus_config = current_config.get("apparatus_config", {})
        
        return cls._build_apparatus_from_config(apparatus_config, apparatus_name)
    
    @classmethod
    def _build_apparatus_from_config(cls, apparatus_config: Dict[str, Any], 
                                   apparatus_name: str) -> mw.Apparatus:
        """Build apparatus from configuration dictionary"""
        
        # Create apparatus
        A = mw.Apparatus(apparatus_name)
        
        # Create component instances
        component_instances = {}
        components = apparatus_config.get("components", {})
        
        # Process passive components first (vessels, tubes, mixers)
        passive_components = components.get("passive", [])
        for comp_config in passive_components:
            instance = cls._create_component_instance(comp_config)
            if instance:
                component_instances[comp_config["name"]] = instance
        
        # Process active components (pumps, valves, sensors)
        active_components = components.get("active", [])
        for comp_config in active_components:
            instance = cls._create_component_instance(comp_config)
            if instance:
                component_instances[comp_config["name"]] = instance
        
        # Add connections
        connections = apparatus_config.get("connections", [])
        for conn in connections:
            from_name = conn.get("from")
            to_name = conn.get("to")
            tube_name = conn.get("tube")
            
            from_comp = component_instances.get(from_name)
            to_comp = component_instances.get(to_name)
            tube_comp = component_instances.get(tube_name)
            
            if from_comp and to_comp and tube_comp:
                A.add(from_comp, to_comp, tube_comp)
            elif from_comp and to_comp:
                # Direct connection without tube
                A.add(from_comp, to_comp)
            else:
                print(f"⚠️  Warning: Could not create connection {from_name} → {to_name}")
                missing = []
                if not from_comp:
                    missing.append(f"from_component '{from_name}'")
                if not to_comp:
                    missing.append(f"to_component '{to_name}'")
                if tube_name and not tube_comp:
                    missing.append(f"tube '{tube_name}'")
                print(f"    Missing: {', '.join(missing)}")
        
        return A
    
    @classmethod
    def _create_component_instance(cls, comp_config: Dict[str, Any]):
        """Create a component instance from configuration"""
        comp_type = comp_config.get("type")
        comp_name = comp_config.get("name")
        
        if not comp_type or not comp_name:
            print(f"⚠️  Warning: Invalid component config - missing type or name: {comp_config}")
            return None
        
        try:
            if comp_type == "Vessel":
                description = comp_config.get("description", comp_name)
                return mw.Vessel(description, name=comp_name)
            
            elif comp_type == "Tube":
                return mw.Tube(
                    length=comp_config.get("length", "1 ft"),
                    ID=comp_config.get("ID", "1/16 in"),
                    OD=comp_config.get("OD", "1/8 in"),
                    material=comp_config.get("material", "PFA"),
                    name=comp_name
                )
            
            elif comp_type in ["TMixer", "CrossMixer", "YMixer"]:
                # Get the class from mechwolf
                mixer_class = getattr(mw, comp_type, None)
                if mixer_class:
                    return mixer_class(name=comp_name)
                else:
                    print(f"⚠️  Warning: Unknown mixer type: {comp_type}")
                    return None
            
            elif comp_type == "HarvardSyringePump":
                return mw.HarvardSyringePump(
                    syringe_volume=comp_config.get("syringe_volume", "10 mL"),
                    syringe_diameter=comp_config.get("syringe_diameter", "10 mm"),
                    serial_port=comp_config.get("serial_port", "/dev/ttyUSB0"),
                    name=comp_name
                )
            
            elif comp_type == "ViciValve":
                serial_port = comp_config.get("serial_port", "/dev/ttyUSB1")
                mapping = comp_config.get("mapping", {})
                
                if mapping:
                    return mw.ViciValve(
                        serial_port=serial_port,
                        mapping=mapping,
                        name=comp_name
                    )
                else:
                    return mw.ViciValve(
                        serial_port=serial_port,
                        name=comp_name
                    )
            
            elif comp_type == "VarianPump":
                return mw.VarianPump(
                    serial_port=comp_config.get("serial_port", "/dev/ttyUSB2"),
                    max_rate=comp_config.get("max_rate", "10 mL/min"),
                    name=comp_name
                )
            
            elif comp_type == "FreeStepPump":
                return mw.FreeStepPump(
                    MCU_ID=comp_config.get("MCU_ID", "A"),
                    motor_ID=comp_config.get("motor_ID", 1),
                    syringe_volume=comp_config.get("syringe_volume", "10 mL"),
                    syringe_diameter=comp_config.get("syringe_diameter", "10 mm"),
                    name=comp_name
                )
            
            else:
                # Generic component creation
                try:
                    comp_class = getattr(mw, comp_type, None)
                    if comp_class:
                        return comp_class(name=comp_name)
                    else:
                        print(f"⚠️  Warning: Unknown component type: {comp_type}")
                        return None
                except Exception as e:
                    print(f"⚠️  Warning: Failed to create {comp_type}: {e}")
                    return None
        
        except Exception as e:
            print(f"❌ Error creating {comp_type} '{comp_name}': {e}")
            return None
    
    @classmethod
    def create_setup_like_old_factory(cls, setup_name: str, config_file: str, 
                                    pumps: Optional[list] = None) -> mw.Apparatus:
        """
        Create apparatus with interface similar to old FlowSetupFactory
        
        This method provides compatibility with the old factory pattern:
        A = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump_1, pump_2])
        
        Now use:
        A = ApparatusFactory.create_setup_like_old_factory('birch_reduction', 'config.json')
        
        Args:
            setup_name: Name for the apparatus (used as apparatus name)
            config_file: JSON configuration file path
            pumps: Optional list of pumps (for compatibility - not used in new system)
            
        Returns:
            Fully configured MechWolf Apparatus
        """
        if pumps:
            print("ℹ️  Note: The new FlowSetups system uses component definitions from JSON.")
            print("   The pumps parameter is ignored. Components are defined in the config file.")
        
        return cls.create_apparatus_from_config(config_file, apparatus_name=setup_name)
    
    @classmethod
    def list_available_configs(cls, config_directory: str = ".") -> List[str]:
        """
        List available JSON configuration files in a directory
        
        Args:
            config_directory: Directory to search for config files
            
        Returns:
            List of JSON configuration file names
        """
        config_path = Path(config_directory)
        json_files = list(config_path.glob("*.json"))
        
        # Filter for valid apparatus configurations
        valid_configs = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "apparatus_config" in data:
                        valid_configs.append(json_file.name)
            except Exception:
                # Skip invalid JSON files
                continue
        
        return sorted(valid_configs)
    
    @classmethod
    def validate_config(cls, config_file: str) -> bool:
        """
        Validate a configuration file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validator = SchemaValidator()
            data_manager = JSONHandler(config_file)
            
            # Try to load configuration
            config = data_manager.load_config()
            if not config:
                return False
            
            # Validate schema
            errors = validator.validate_config(config)
            return len(errors) == 0
        
        except Exception:
            return False
    
    @classmethod
    def print_config_summary(cls, config_file: str) -> None:
        """
        Print a summary of a configuration file
        
        Args:
            config_file: Path to configuration file
        """
        try:
            data_manager = JSONHandler(config_file)
            config = data_manager.load_config()
            
            if not config:
                print(f"❌ Could not load configuration from {config_file}")
                return
            
            apparatus_config = config.get("apparatus_config", {})
            components = apparatus_config.get("components", {})
            connections = apparatus_config.get("connections", [])
            
            name = apparatus_config.get("name", "Unknown")
            description = apparatus_config.get("description", "No description")
            
            active_count = len(components.get("active", []))
            passive_count = len(components.get("passive", []))
            connection_count = len(connections)
            
            print(f"📊 Configuration Summary: {Path(config_file).name}")
            print("=" * 50)
            print(f"Name: {name}")
            print(f"Description: {description}")
            print(f"Active Components: {active_count}")
            print(f"Passive Components: {passive_count}")
            print(f"Connections: {connection_count}")
            
            if active_count > 0:
                print("\nActive Components:")
                for comp in components.get("active", []):
                    print(f"  • {comp.get('name', 'Unknown')} ({comp.get('type', 'Unknown')})")
            
            if passive_count > 0:
                print("\nPassive Components:")
                for comp in components.get("passive", []):
                    print(f"  • {comp.get('name', 'Unknown')} ({comp.get('type', 'Unknown')})")
            
            if connection_count > 0:
                print("\nConnections:")
                for conn in connections:
                    from_comp = conn.get("from", "Unknown")
                    to_comp = conn.get("to", "Unknown")
                    tube = conn.get("tube", "direct")
                    print(f"  • {from_comp} → {to_comp} (via {tube})")
        
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")


# Convenience functions for backward compatibility
def create_apparatus_from_config(config_file: str, apparatus_name: Optional[str] = None) -> mw.Apparatus:
    """Convenience function - create apparatus from config file"""
    return ApparatusFactory.create_apparatus_from_config(config_file, apparatus_name)


def create_setup(setup_name: str, config_file: str, pumps: Optional[list] = None) -> mw.Apparatus:
    """
    Backward compatibility function that mimics the old FlowSetupFactory.create_setup()
    
    Old usage:
        from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
        A = FlowSetupFactory.create_setup('two_syringes_1r_1m', [pump_1, pump_2])
    
    New usage:
        from mechwolf.DataEntry.FlowSetups_New import create_setup
        A = create_setup('birch_reduction', 'birch_reduction.json')
    """
    return ApparatusFactory.create_setup_like_old_factory(setup_name, config_file, pumps)