"""
Tailwind Components - Modern UI components styled with Tailwind-inspired CSS

This module provides modern, styled UI components for the Flow Setup interface
using Tailwind CSS-inspired styling within ipywidgets HTML components.
"""
import ipywidgets as widgets
from typing import Dict, List, Any, Optional


class TailwindComponents:
    """Creates modern UI components with Tailwind CSS-inspired styling"""
    
    def __init__(self):
        # Color palette inspired by Tailwind CSS
        self.colors = {
            'primary': '#3b82f6',    # blue-500
            'success': '#10b981',    # emerald-500
            'warning': '#f59e0b',    # amber-500
            'danger': '#ef4444',     # red-500
            'info': '#06b6d4',       # cyan-500
            'light': '#f8fafc',      # slate-50
            'dark': '#0f172a',       # slate-900
            'gray': {
                '50': '#f8fafc',
                '100': '#f1f5f9',
                '200': '#e2e8f0',
                '300': '#cbd5e1',
                '400': '#94a3b8',
                '500': '#64748b',
                '600': '#475569',
                '700': '#334155',
                '800': '#1e293b',
                '900': '#0f172a'
            }
        }
        
        # Common CSS classes
        self.css_classes = {
            'card': """
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
                margin: 16px 0;
            """,
            'button_primary': """
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            """,
            'button_secondary': """
                background: white;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            """,
            'header_gradient': """
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 24px;
                border-radius: 12px;
                margin-bottom: 24px;
            """,
            'input_field': """
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 12px 16px;
                background: white;
                transition: border-color 0.3s ease;
                font-size: 14px;
            """,
            'alert_success': """
                background: #d1fae5;
                border: 1px solid #a7f3d0;
                border-radius: 8px;
                padding: 16px;
                color: #065f46;
                margin: 16px 0;
            """,
            'alert_warning': """
                background: #fef3c7;
                border: 1px solid #fde68a;
                border-radius: 8px;
                padding: 16px;
                color: #92400e;
                margin: 16px 0;
            """,
            'alert_danger': """
                background: #fecaca;
                border: 1px solid #fca5a5;
                border-radius: 8px;
                padding: 16px;
                color: #991b1b;
                margin: 16px 0;
            """,
            'alert_info': """
                background: #dbeafe;
                border: 1px solid #93c5fd;
                border-radius: 8px;
                padding: 16px;
                color: #1e40af;
                margin: 16px 0;
            """
        }
    
    def create_title(self, title: str, subtitle: Optional[str] = None) -> str:
        """Create a styled title with optional subtitle"""
        
        html = f"""
            <div style='{self.css_classes["header_gradient"]}'>
                <h1 style='margin: 0; font-size: 28px; font-weight: 700; font-family: "Segoe UI", sans-serif;'>
                    {title}
                </h1>
        """
        
        if subtitle:
            html += f"""
                <p style='margin: 8px 0 0 0; font-size: 16px; opacity: 0.9; font-weight: 400;'>
                    {subtitle}
                </p>
            """
        
        html += "</div>"
        return html
    
    def create_card(self, title: str, content: str, icon: Optional[str] = None) -> str:
        """Create a styled card component"""
        
        icon_html = f"<span style='font-size: 24px; margin-right: 12px;'>{icon}</span>" if icon else ""
        
        return f"""
            <div style='{self.css_classes["card"]}'>
                <h3 style='margin: 0 0 16px 0; font-size: 20px; font-weight: 600; display: flex; align-items: center;'>
                    {icon_html}{title}
                </h3>
                <div style='color: #374151; line-height: 1.6;'>
                    {content}
                </div>
            </div>
        """
    
    def create_info_card(self, title: str, message: str, type: str = "info") -> widgets.HTML:
        """Create an information card widget"""
        
        alert_class = f"alert_{type}"
        style = self.css_classes.get(alert_class, self.css_classes["alert_info"])
        
        # Icons for different types
        icons = {
            'success': '✅',
            'warning': '⚠️',
            'danger': '❌',
            'info': 'ℹ️'
        }
        
        icon = icons.get(type, 'ℹ️')
        
        html = f"""
            <div style='{style}'>
                <h4 style='margin: 0 0 8px 0; font-weight: 600; display: flex; align-items: center;'>
                    <span style='margin-right: 8px; font-size: 18px;'>{icon}</span>
                    {title}
                </h4>
                <div style='white-space: pre-line;'>{message}</div>
            </div>
        """
        
        return widgets.HTML(html)
    
    def create_welcome_screen(self, title: str, subtitle: str, steps: List[Dict[str, str]]) -> widgets.HTML:
        """Create a welcome screen with steps"""
        
        html = f"""
            <div style='text-align: center; padding: 40px 20px;'>
                <h1 style='font-size: 36px; font-weight: 700; color: #1f2937; margin: 0 0 16px 0; font-family: "Segoe UI", sans-serif;'>
                    {title}
                </h1>
                <p style='font-size: 18px; color: #6b7280; margin: 0 0 48px 0; max-width: 600px; margin-left: auto; margin-right: auto;'>
                    {subtitle}
                </p>
                
                <div style='display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; max-width: 1000px; margin: 0 auto;'>
        """
        
        for step in steps:
            html += f"""
                <div style='flex: 1; min-width: 280px; max-width: 320px; text-align: center;'>
                    <div style='{self.css_classes["card"]} text-align: center; height: 100%;'>
                        <div style='font-size: 48px; margin-bottom: 16px;'>{step['icon']}</div>
                        <div style='background: {self.colors["primary"]}; color: white; width: 32px; height: 32px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-bottom: 16px;'>
                            {step['number']}
                        </div>
                        <h3 style='font-size: 20px; font-weight: 600; margin: 0 0 12px 0; color: #1f2937;'>
                            {step['title']}
                        </h3>
                        <p style='color: #6b7280; line-height: 1.6; margin: 0;'>
                            {step['description']}
                        </p>
                    </div>
                </div>
            """
        
        html += """
                </div>
            </div>
        """
        
        return widgets.HTML(html)
    
    def create_stats_grid(self, stats: List[Dict[str, str]]) -> widgets.HTML:
        """Create a statistics grid"""
        
        html = """
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 24px 0;'>
        """
        
        for stat in stats:
            html += f"""
                <div style='{self.css_classes["card"]} text-align: center;'>
                    <div style='font-size: 32px; font-weight: 700; color: {self.colors["primary"]}; margin-bottom: 8px;'>
                        {stat['value']}
                    </div>
                    <div style='color: {self.colors["gray"]["600"]}; font-weight: 500;'>
                        {stat['label']}
                    </div>
                </div>
            """
        
        html += "</div>"
        return widgets.HTML(html)
    
    def create_progress_bar(self, progress: float, label: str = "") -> widgets.HTML:
        """Create a progress bar"""
        
        percentage = min(max(progress * 100, 0), 100)
        
        html = f"""
            <div style='margin: 16px 0;'>
                {f'<div style="margin-bottom: 8px; font-weight: 500; color: {self.colors["gray"]["700"]};">{label}</div>' if label else ''}
                <div style='background: {self.colors["gray"]["200"]}; border-radius: 9999px; height: 8px; overflow: hidden;'>
                    <div style='background: linear-gradient(90deg, {self.colors["primary"]} 0%, {self.colors["success"]} 100%); height: 100%; border-radius: 9999px; transition: width 0.3s ease; width: {percentage}%;'></div>
                </div>
                <div style='text-align: right; margin-top: 4px; font-size: 12px; color: {self.colors["gray"]["500"]};'>
                    {percentage:.1f}%
                </div>
            </div>
        """
        
        return widgets.HTML(html)
    
    def create_feature_grid(self, features: List[Dict[str, str]]) -> widgets.HTML:
        """Create a feature grid layout"""
        
        html = """
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin: 32px 0;'>
        """
        
        for feature in features:
            html += f"""
                <div style='{self.css_classes["card"]} border-left: 4px solid {self.colors["primary"]};'>
                    <div style='display: flex; align-items: center; margin-bottom: 12px;'>
                        <span style='font-size: 24px; margin-right: 12px;'>{feature.get('icon', '🔧')}</span>
                        <h3 style='margin: 0; font-size: 18px; font-weight: 600; color: #1f2937;'>
                            {feature['title']}
                        </h3>
                    </div>
                    <p style='color: #6b7280; line-height: 1.6; margin: 0;'>
                        {feature['description']}
                    </p>
                </div>
            """
        
        html += "</div>"
        return widgets.HTML(html)
    
    def create_timeline(self, steps: List[Dict[str, str]]) -> widgets.HTML:
        """Create a timeline component"""
        
        html = """
            <div style='position: relative; padding: 20px 0;'>
        """
        
        for i, step in enumerate(steps):
            is_last = i == len(steps) - 1
            
            html += f"""
                <div style='display: flex; align-items: center; margin-bottom: {0 if is_last else 32}px;'>
                    <div style='flex-shrink: 0; width: 40px; height: 40px; background: {self.colors["primary"]}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; position: relative; z-index: 2;'>
                        {i + 1}
                    </div>
                    <div style='flex: 1; margin-left: 20px;'>
                        <h4 style='margin: 0 0 4px 0; font-weight: 600; color: #1f2937;'>
                            {step['title']}
                        </h4>
                        <p style='margin: 0; color: #6b7280; line-height: 1.5;'>
                            {step['description']}
                        </p>
                    </div>
                </div>
            """
            
            if not is_last:
                html += f"""
                    <div style='width: 2px; height: 24px; background: {self.colors["gray"]["300"]}; margin-left: 19px; margin-bottom: 8px;'></div>
                """
        
        html += "</div>"
        return widgets.HTML(html)
    
    def create_button_group(self, buttons: List[Dict[str, str]]) -> widgets.HBox:
        """Create a group of styled buttons"""
        
        button_widgets = []
        
        for btn_config in buttons:
            btn = widgets.Button(
                description=btn_config['text'],
                button_style=btn_config.get('style', ''),
                layout=widgets.Layout(
                    width=btn_config.get('width', '120px'),
                    margin='5px'
                )
            )
            
            if 'callback' in btn_config:
                btn.on_click(btn_config['callback'])
            
            button_widgets.append(btn)
        
        return widgets.HBox(
            button_widgets,
            layout=widgets.Layout(justify_content='center')
        )
    
    def create_status_badge(self, text: str, status: str = "info") -> str:
        """Create a status badge"""
        
        colors = {
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4'
        }
        
        bg_colors = {
            'success': '#d1fae5',
            'warning': '#fef3c7',
            'danger': '#fecaca',
            'info': '#dbeafe'
        }
        
        color = colors.get(status, colors['info'])
        bg_color = bg_colors.get(status, bg_colors['info'])
        
        return f"""
            <span style='
                background: {bg_color};
                color: {color};
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 600;
                display: inline-block;
            '>
                {text}
            </span>
        """
    
    def create_divider(self, text: Optional[str] = None) -> widgets.HTML:
        """Create a section divider"""
        
        if text:
            html = f"""
                <div style='display: flex; align-items: center; margin: 32px 0;'>
                    <div style='flex: 1; height: 1px; background: {self.colors["gray"]["300"]};'></div>
                    <div style='padding: 0 16px; color: {self.colors["gray"]["500"]}; font-weight: 500;'>
                        {text}
                    </div>
                    <div style='flex: 1; height: 1px; background: {self.colors["gray"]["300"]};'></div>
                </div>
            """
        else:
            html = f"""
                <div style='height: 1px; background: {self.colors["gray"]["300"]}; margin: 24px 0;'></div>
            """
        
        return widgets.HTML(html)