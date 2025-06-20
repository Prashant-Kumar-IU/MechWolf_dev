"""
Flow Setup Main Orchestrator - Coordinates the complete apparatus building workflow

This module provides the main orchestrator class that coordinates between
component configuration, apparatus building, and data management.
"""
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..component_configurator.component_selector import ComponentSelector
from ..apparatus_builder.connection_gui import ConnectionGUI
from ..data_manager.json_handler import JSONHandler
from .tailwind_components import TailwindComponents


class FlowSetupMain:
    """Main orchestrator for the Flow Setup system"""
    
    def __init__(self, json_file: str = "apparatus_config.json"):
        self.json_file = json_file
        self.data_manager = JSONHandler(json_file)
        self.tailwind = TailwindComponents()
        
        # Initialize subsystems
        self.component_selector = ComponentSelector(self.data_manager)
        self.connection_gui = ConnectionGUI(self.data_manager)
        
        # Current state
        self.current_view = "welcome"
        self.configured_components: Dict[str, Dict[str, Any]] = {}
        
        # UI elements
        self.main_container = None
        self.navigation_bar = None
        
    def start(self):
        """Start the Flow Setup application"""
        self.create_main_interface()
    
    def create_main_interface(self):
        """Create the main application interface"""
        
        # Create navigation bar
        self.navigation_bar = self._create_navigation_bar()
        
        # Create main content area
        self.main_content = widgets.VBox([], layout=widgets.Layout(
            width='100%',
            min_height='600px'
        ))
        
        # Main container
        self.main_container = widgets.VBox([
            self.navigation_bar,
            self.main_content
        ])
        
        display(self.main_container)
        
        # Show welcome screen
        self.show_welcome()
    
    def _create_navigation_bar(self) -> widgets.Widget:
        """Create the navigation bar"""
        
        # Application title
        title = widgets.HTML(
            value=self.tailwind.create_title("🔧 MechWolf FlowSetups", "Modern Apparatus Builder"),
            layout=widgets.Layout(flex='1')
        )
        
        # Navigation buttons
        nav_buttons = []
        
        nav_config = [
            ("🏠 Home", "welcome", "primary"),
            ("⚙️ Components", "components", "info"),
            ("🔗 Connections", "connections", "success"),
            ("💾 Data", "data", "warning"),
            ("📊 Summary", "summary", "")
        ]
        
        for label, view, style in nav_config:
            btn = widgets.Button(
                description=label,
                button_style=style,
                layout=widgets.Layout(width='120px', margin='0 5px')
            )
            btn.on_click(lambda b, v=view: self.switch_view(v))
            nav_buttons.append(btn)
        
        # File info display
        file_info = self._create_file_info_display()
        
        # Navigation layout
        nav_bar = widgets.HBox([
            title,
            widgets.HBox(nav_buttons),
            file_info
        ], layout=widgets.Layout(
            width='100%',
            padding='10px 20px',
            border='1px solid #ddd',
            background_color='#f8f9fa'
        ))
        
        return nav_bar
    
    def _create_file_info_display(self) -> widgets.Widget:
        """Create file information display"""
        info = self.data_manager.get_file_info()
        
        status_color = "#28a745" if info['is_valid'] else "#dc3545"
        status_text = "✅ Valid" if info['is_valid'] else "❌ Invalid"
        
        file_info_html = f"""
            <div style='text-align: right; font-size: 12px; color: #666;'>
                <div><strong>Config:</strong> {Path(info['file_path']).name}</div>
                <div style='color: {status_color};'>{status_text}</div>
            </div>
        """
        
        return widgets.HTML(file_info_html)
    
    def switch_view(self, view: str):
        """Switch to a different view"""
        self.current_view = view
        
        if view == "welcome":
            self.show_welcome()
        elif view == "components":
            self.show_components()
        elif view == "connections":
            self.show_connections()
        elif view == "data":
            self.show_data_management()
        elif view == "summary":
            self.show_summary()
    
    def show_welcome(self):
        """Show the welcome screen"""
        clear_output()
        
        welcome_content = self.tailwind.create_welcome_screen(
            title="Welcome to MechWolf FlowSetups",
            subtitle="Build your flow chemistry apparatus step by step",
            steps=[
                {
                    "number": "1",
                    "title": "Configure Components",
                    "description": "Add and configure pumps, valves, vessels, and other components",
                    "icon": "⚙️"
                },
                {
                    "number": "2", 
                    "title": "Build Connections",
                    "description": "Connect components together to form your apparatus",
                    "icon": "🔗"
                },
                {
                    "number": "3",
                    "title": "Validate & Export",
                    "description": "Validate your setup and export the configuration",
                    "icon": "✅"
                }
            ]
        )
        
        # Quick start buttons
        start_buttons = widgets.HBox([
            self._create_action_button("Start with Components", "components", "primary"),
            self._create_action_button("Load Existing Config", "load_config", "info"),
            self._create_action_button("View Documentation", "docs", "")
        ], layout=widgets.Layout(justify_content='center', margin='20px 0'))
        
        # System status
        status_info = self._create_system_status()
        
        self.main_content.children = [
            welcome_content,
            start_buttons,
            status_info
        ]
        
        display(self.main_container)
    
    def show_components(self):
        """Show the component configuration interface"""
        clear_output()
        
        # Update configured components from selector
        self.configured_components = self.component_selector.get_configured_components()
        
        # Create component selector interface
        self.component_selector.create_main_interface()
        
        # Replace main content with component selector
        # (The component selector displays itself, so we don't need to modify main_content)
    
    def show_connections(self):
        """Show the connection building interface"""
        clear_output()
        
        # Get latest components
        self.configured_components = self.component_selector.get_configured_components()
        
        if not self.configured_components:
            # Show message about needing components first
            no_components_msg = self.tailwind.create_info_card(
                title="No Components Configured",
                message="Please configure some components first before building connections.",
                type="warning"
            )
            
            back_btn = self._create_action_button("Configure Components", "components", "primary")
            
            self.main_content.children = [no_components_msg, back_btn]
            display(self.main_container)
            return
        
        # Initialize connection GUI with components
        self.connection_gui.initialize(self.configured_components)
        
        # (The connection GUI displays itself)
    
    def show_data_management(self):
        """Show data management interface"""
        clear_output()
        
        # File information
        file_info = self.data_manager.get_file_info()
        
        # Create data management interface
        data_content = self._create_data_management_interface(file_info)
        
        self.main_content.children = [data_content]
        display(self.main_container)
    
    def show_summary(self):
        """Show apparatus summary"""
        clear_output()
        
        # Load current configuration
        config = self.data_manager.load_config()
        
        if not config:
            no_config_msg = self.tailwind.create_info_card(
                title="No Configuration Available",
                message="No apparatus configuration found. Please build your apparatus first.",
                type="info"
            )
            
            start_btn = self._create_action_button("Start Building", "components", "primary")
            
            self.main_content.children = [no_config_msg, start_btn]
            display(self.main_container)
            return
        
        # Create summary interface
        summary_content = self._create_summary_interface(config)
        
        self.main_content.children = [summary_content]
        display(self.main_container)
    
    def _create_action_button(self, text: str, action: str, style: str) -> widgets.Button:
        """Create an action button"""
        btn = widgets.Button(
            description=text,
            button_style=style,
            layout=widgets.Layout(width='200px', margin='10px')
        )
        
        def handle_click(b):
            if action == "load_config":
                self._load_config_dialog()
            elif action == "docs":
                self._show_documentation()
            else:
                self.switch_view(action)
        
        btn.on_click(handle_click)
        return btn
    
    def _create_system_status(self) -> widgets.Widget:
        """Create system status display"""
        
        # Check system status
        file_info = self.data_manager.get_file_info()
        component_count = len(self.configured_components)
        
        status_items = [
            f"📁 Config File: {Path(file_info['file_path']).name}",
            f"✅ File Status: {'Valid' if file_info['is_valid'] else 'Invalid'}",
            f"⚙️ Components: {component_count}",
            f"💾 Backups: {file_info['backup_count']}"
        ]
        
        status_html = "<div style='background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;'>"
        status_html += "<h4>System Status</h4>"
        for item in status_items:
            status_html += f"<div style='margin: 5px 0;'>{item}</div>"
        status_html += "</div>"
        
        return widgets.HTML(status_html)
    
    def _create_data_management_interface(self, file_info: Dict[str, Any]) -> widgets.Widget:
        """Create data management interface"""
        
        # File status card
        status_card = self.tailwind.create_info_card(
            title="Configuration File Status",
            message=f"File: {Path(file_info['file_path']).name}\n" +
                   f"Status: {'Valid' if file_info['is_valid'] else 'Invalid'}\n" +
                   f"Size: {file_info['size']} bytes\n" +
                   f"Backups: {file_info['backup_count']}",
            type="info" if file_info['is_valid'] else "warning"
        )
        
        # Action buttons
        action_buttons = widgets.VBox([
            widgets.HTML("<h4>Data Management Actions</h4>"),
            self._create_data_action_button("💾 Save Current Config", "save"),
            self._create_data_action_button("📂 Load Config File", "load"),
            self._create_data_action_button("📤 Export Configuration", "export"),
            self._create_data_action_button("🔄 Create Backup", "backup"),
            self._create_data_action_button("🧹 Cleanup Old Backups", "cleanup"),
            self._create_data_action_button("✅ Validate Configuration", "validate")
        ])
        
        # Validation results
        self.validation_output = widgets.Output()
        
        return widgets.VBox([
            status_card,
            action_buttons,
            self.validation_output
        ])
    
    def _create_data_action_button(self, text: str, action: str) -> widgets.Button:
        """Create data management action button"""
        btn = widgets.Button(
            description=text,
            layout=widgets.Layout(width='250px', margin='5px 0')
        )
        
        def handle_action(b):
            with self.validation_output:
                clear_output()
                
                if action == "save":
                    self._save_current_config()
                elif action == "load":
                    self._load_config_file()
                elif action == "export":
                    self._export_config()
                elif action == "backup":
                    self._create_backup()
                elif action == "cleanup":
                    self._cleanup_backups()
                elif action == "validate":
                    self._validate_config()
        
        btn.on_click(handle_action)
        return btn
    
    def _create_summary_interface(self, config: Dict[str, Any]) -> widgets.Widget:
        """Create apparatus summary interface"""
        
        apparatus_config = config.get("apparatus_config", {})
        components = apparatus_config.get("components", {})
        connections = apparatus_config.get("connections", [])
        
        # Summary statistics
        active_count = len(components.get("active", []))
        passive_count = len(components.get("passive", []))
        connection_count = len(connections)
        
        stats_html = f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='margin: 0; font-family: "Segoe UI", sans-serif;'>
                    📊 Apparatus Summary
                </h2>
                <div style='margin-top: 15px; display: flex; gap: 30px;'>
                    <div><strong>Active Components:</strong> {active_count}</div>
                    <div><strong>Passive Components:</strong> {passive_count}</div>
                    <div><strong>Connections:</strong> {connection_count}</div>
                </div>
            </div>
        """
        
        stats_widget = widgets.HTML(stats_html)
        
        # Component details
        component_details = self._create_component_summary(components)
        
        # Connection details
        connection_details = self._create_connection_summary(connections)
        
        # Action buttons
        summary_actions = widgets.HBox([
            self._create_action_button("🎨 Visualize Apparatus", "visualize", "info"),
            self._create_action_button("📝 Generate Code", "generate_code", "success"),
            self._create_action_button("💾 Export Configuration", "export", "warning")
        ], layout=widgets.Layout(justify_content='center', margin='20px 0'))
        
        return widgets.VBox([
            stats_widget,
            component_details,
            connection_details,
            summary_actions
        ])
    
    def _create_component_summary(self, components: Dict[str, Any]) -> widgets.Widget:
        """Create component summary display"""
        
        summary_html = "<div style='background: white; padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0;'>"
        summary_html += "<h4>📦 Components</h4>"
        
        for category in ["active", "passive"]:
            comp_list = components.get(category, [])
            if comp_list:
                category_title = "Active Components" if category == "active" else "Passive Components"
                summary_html += f"<h5>{category_title}</h5><ul>"
                
                for comp in comp_list:
                    comp_name = comp.get("name", "Unknown")
                    comp_type = comp.get("type", "Unknown")
                    summary_html += f"<li><strong>{comp_name}</strong> ({comp_type})</li>"
                
                summary_html += "</ul>"
        
        summary_html += "</div>"
        
        return widgets.HTML(summary_html)
    
    def _create_connection_summary(self, connections: List[Dict[str, Any]]) -> widgets.Widget:
        """Create connection summary display"""
        
        summary_html = "<div style='background: white; padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0;'>"
        summary_html += "<h4>🔗 Connections</h4>"
        
        if connections:
            summary_html += "<ul>"
            for conn in connections:
                from_comp = conn.get("from", "Unknown")
                to_comp = conn.get("to", "Unknown")
                tube = conn.get("tube", "Unknown")
                summary_html += f"<li>{from_comp} → {to_comp} <em>(via {tube})</em></li>"
            summary_html += "</ul>"
        else:
            summary_html += "<p style='color: #666;'>No connections defined.</p>"
        
        summary_html += "</div>"
        
        return widgets.HTML(summary_html)
    
    # Data management action handlers
    def _save_current_config(self):
        """Save current configuration"""
        # Get latest components and connections
        components = self.component_selector.get_configured_components()
        connections = self.connection_gui.get_connections()
        
        # Organize data
        organized_components = {"active": [], "passive": []}
        for comp_data in components.values():
            category = comp_data.get("category", "passive")
            if category in ["active_contrib", "active_stdlib"]:
                organized_components["active"].append(comp_data)
            else:
                organized_components["passive"].append(comp_data)
        
        config = {
            "apparatus_config": {
                "name": "Generated Apparatus",
                "description": "Created with MechWolf FlowSetups",
                "components": organized_components,
                "connections": connections
            }
        }
        
        success = self.data_manager.save_config(config)
        if success:
            print("✅ Configuration saved successfully!")
        else:
            print("❌ Failed to save configuration")
    
    def _load_config_file(self):
        """Load configuration file"""
        config = self.data_manager.load_config()
        if config:
            print("✅ Configuration loaded successfully!")
            # Update subsystems with loaded data
            self._update_subsystems_from_config(config)
        else:
            print("❌ Failed to load configuration")
    
    def _export_config(self):
        """Export configuration"""
        success = self.data_manager.export_config("json")
        if success:
            print("✅ Configuration exported successfully!")
        else:
            print("❌ Failed to export configuration")
    
    def _create_backup(self):
        """Create backup"""
        # This would be handled by the data manager during save
        print("✅ Backup will be created automatically on next save")
    
    def _cleanup_backups(self):
        """Cleanup old backups"""
        deleted = self.data_manager.cleanup_old_backups(keep_count=5)
        print(f"🧹 Cleaned up {deleted} old backup files")
    
    def _validate_config(self):
        """Validate current configuration"""
        errors = self.data_manager.validate_file()
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"  • {error}")
        else:
            print("✅ Configuration is valid!")
    
    def _update_subsystems_from_config(self, config: Dict[str, Any]):
        """Update subsystems with loaded configuration"""
        # This would update the component selector and connection GUI
        # with the loaded configuration data
        pass
    
    def _load_config_dialog(self):
        """Show load configuration dialog"""
        print("📂 Load config dialog would be shown here")
    
    def _show_documentation(self):
        """Show documentation"""
        print("📚 Documentation would be shown here")
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current apparatus configuration"""
        components = self.component_selector.get_configured_components()
        connections = self.connection_gui.get_connections()
        
        # Organize components by category
        organized_components = {"active": [], "passive": []}
        for comp_data in components.values():
            category = comp_data.get("category", "passive")
            if category in ["active_contrib", "active_stdlib"]:
                organized_components["active"].append(comp_data)
            else:
                organized_components["passive"].append(comp_data)
        
        return {
            "apparatus_config": {
                "name": "Current Apparatus",
                "description": "Work in progress",
                "components": organized_components,
                "connections": connections
            }
        }