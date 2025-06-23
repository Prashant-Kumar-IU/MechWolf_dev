"""
Modern UI Components - Tailwind-Inspired Styling System

This module provides a unified styling system for MechWolf DataEntry interfaces,
inspired by Tailwind CSS principles with consistent colors, spacing, and typography.
"""

import ipywidgets as widgets
from IPython.display import HTML
from typing import Dict, Any, List, Optional, Union, Callable


class TailwindColors:
    """Tailwind-inspired color palette for consistent theming"""
    
    # Primary colors (blues)
    BLUE_50 = "#eff6ff"
    BLUE_100 = "#dbeafe"
    BLUE_500 = "#3b82f6"
    BLUE_600 = "#2563eb"
    BLUE_700 = "#1d4ed8"
    
    # Secondary colors (greens)
    GREEN_50 = "#f0fdf4"
    GREEN_100 = "#dcfce7"
    GREEN_500 = "#22c55e"
    GREEN_600 = "#16a34a"
    GREEN_700 = "#15803d"
    
    # Accent colors
    PURPLE_50 = "#faf5ff"
    PURPLE_500 = "#a855f7"
    PURPLE_600 = "#9333ea"
    
    ORANGE_50 = "#fff7ed"
    ORANGE_500 = "#f97316"
    ORANGE_600 = "#ea580c"
    
    RED_50 = "#fef2f2"
    RED_500 = "#ef4444"
    RED_600 = "#dc2626"
    
    # Neutral colors
    GRAY_50 = "#f9fafb"
    GRAY_100 = "#f3f4f6"
    GRAY_200 = "#e5e7eb"
    GRAY_300 = "#d1d5db"
    GRAY_400 = "#9ca3af"
    GRAY_500 = "#6b7280"
    GRAY_600 = "#4b5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1f2937"
    GRAY_900 = "#111827"
    
    WHITE = "#ffffff"
    BLACK = "#000000"


class TailwindSpacing:
    """Spacing system following Tailwind conventions"""
    
    XS = "4px"    # 1
    SM = "8px"    # 2
    MD = "12px"   # 3
    BASE = "16px" # 4
    LG = "20px"   # 5
    XL = "24px"   # 6
    XXL = "32px"  # 8
    XXXL = "48px" # 12


class ModernUIComponents:
    """Modern UI components with Tailwind-inspired styling"""
    
    @staticmethod
    def create_section_header(
        title: str, 
        description: str = "", 
        variant: str = "primary",
        size: str = "large"
    ) -> widgets.HTML:
        """
        Create a modern section header with gradient background
        
        Args:
            title: Header title text
            description: Optional description text
            variant: Color scheme ('primary', 'secondary', 'accent', 'purple')
            size: Size variant ('small', 'medium', 'large')
        """
        
        # Define gradients for each variant
        gradients = {
            'primary': f"linear-gradient(135deg, {TailwindColors.BLUE_500} 0%, {TailwindColors.BLUE_700} 100%)",
            'secondary': f"linear-gradient(135deg, {TailwindColors.GREEN_500} 0%, {TailwindColors.GREEN_700} 100%)",
            'accent': f"linear-gradient(135deg, {TailwindColors.ORANGE_500} 0%, {TailwindColors.ORANGE_600} 100%)",
            'purple': f"linear-gradient(135deg, {TailwindColors.PURPLE_500} 0%, {TailwindColors.PURPLE_600} 100%)"
        }
        
        # Size configurations
        sizes = {
            'small': {'padding': TailwindSpacing.BASE, 'title_size': '18px', 'desc_size': '14px'},
            'medium': {'padding': TailwindSpacing.LG, 'title_size': '20px', 'desc_size': '15px'},
            'large': {'padding': TailwindSpacing.XL, 'title_size': '24px', 'desc_size': '16px'}
        }
        
        gradient = gradients.get(variant, gradients['primary'])
        size_config = sizes.get(size, sizes['large'])
        
        html_content = f"""
        <div style='
            background: {gradient}; 
            padding: {size_config["padding"]}; 
            border-radius: 12px; 
            margin-bottom: {TailwindSpacing.LG};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
        '>
            <h2 style='
                color: {TailwindColors.WHITE}; 
                margin: 0; 
                text-align: center; 
                font-weight: 600;
                font-size: {size_config["title_size"]};
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            '>
                {title}
            </h2>
        """
        
        if description:
            html_content += f"""
            <p style='
                color: rgba(255, 255, 255, 0.9); 
                margin: {TailwindSpacing.SM} 0 0 0; 
                text-align: center;
                font-size: {size_config["desc_size"]};
                font-weight: 400;
            '>
                {description}
            </p>
            """
        
        html_content += "</div>"
        
        return widgets.HTML(html_content)
    
    @staticmethod
    def create_info_box(
        content: str, 
        variant: str = "info",
        dismissible: bool = False
    ) -> widgets.HTML:
        """
        Create a modern info box with consistent styling
        
        Args:
            content: HTML content for the box
            variant: Style variant ('info', 'success', 'warning', 'error')
            dismissible: Whether to show a close button
        """
        
        variants = {
            'info': {
                'bg': TailwindColors.BLUE_50,
                'border': TailwindColors.BLUE_500,
                'icon': '💡',
                'text_color': TailwindColors.BLUE_700
            },
            'success': {
                'bg': TailwindColors.GREEN_50,
                'border': TailwindColors.GREEN_500,
                'icon': '✅',
                'text_color': TailwindColors.GREEN_700
            },
            'warning': {
                'bg': TailwindColors.ORANGE_50,
                'border': TailwindColors.ORANGE_500,
                'icon': '⚠️',
                'text_color': TailwindColors.ORANGE_600
            },
            'error': {
                'bg': TailwindColors.RED_50,
                'border': TailwindColors.RED_500,
                'icon': '❌',
                'text_color': TailwindColors.RED_600
            }
        }
        
        style_config = variants.get(variant, variants['info'])
        
        html_content = f"""
        <div style='
            background: {style_config["bg"]}; 
            border-left: 4px solid {style_config["border"]}; 
            padding: {TailwindSpacing.BASE}; 
            border-radius: 8px; 
            margin: {TailwindSpacing.SM} 0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        '>
            <div style='
                display: flex; 
                align-items: flex-start; 
                gap: {TailwindSpacing.SM};
            '>
                <span style='font-size: 18px; line-height: 1;'>{style_config["icon"]}</span>
                <div style='
                    flex: 1;
                    color: {style_config["text_color"]};
                    line-height: 1.5;
                '>
                    {content}
                </div>
        """
        
        if dismissible:
            html_content += f"""
                <button style='
                    background: none;
                    border: none;
                    color: {style_config["text_color"]};
                    cursor: pointer;
                    font-size: 16px;
                    padding: 0;
                    margin-left: {TailwindSpacing.SM};
                '>×</button>
            """
        
        html_content += """
            </div>
        </div>
        """
        
        return widgets.HTML(html_content)
    
    @staticmethod
    def create_card(
        content: Union[str, widgets.Widget, List[widgets.Widget]],
        title: str = "",
        variant: str = "default",
        padding: str = "medium"
    ) -> widgets.VBox:
        """
        Create a modern card container
        
        Args:
            content: Card content (HTML string or widgets)
            title: Optional card title
            variant: Style variant ('default', 'elevated', 'outlined')
            padding: Padding size ('small', 'medium', 'large')
        """
        
        padding_sizes = {
            'small': TailwindSpacing.SM,
            'medium': TailwindSpacing.BASE,
            'large': TailwindSpacing.XL
        }
        
        card_padding = padding_sizes.get(padding, padding_sizes['medium'])
        
        # Card styles by variant
        if variant == "elevated":
            card_style = f"""
                background: {TailwindColors.WHITE};
                border-radius: 12px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                border: 1px solid {TailwindColors.GRAY_200};
                padding: {card_padding};
                margin: {TailwindSpacing.SM} 0;
            """
        elif variant == "outlined":
            card_style = f"""
                background: {TailwindColors.WHITE};
                border-radius: 8px;
                border: 2px solid {TailwindColors.GRAY_300};
                padding: {card_padding};
                margin: {TailwindSpacing.SM} 0;
            """
        else:  # default
            card_style = f"""
                background: {TailwindColors.WHITE};
                border-radius: 8px;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                border: 1px solid {TailwindColors.GRAY_200};
                padding: {card_padding};
                margin: {TailwindSpacing.SM} 0;
            """
        
        children = []
        
        # Add title if provided
        if title:
            title_widget = widgets.HTML(f"""
            <h3 style='
                margin: 0 0 {TailwindSpacing.MD} 0;
                color: {TailwindColors.GRAY_800};
                font-size: 18px;
                font-weight: 600;
            '>{title}</h3>
            """)
            children.append(title_widget)
        
        # Add content
        if isinstance(content, str):
            content_widget = widgets.HTML(content)
            children.append(content_widget)
        elif isinstance(content, widgets.Widget):
            children.append(content)
        elif isinstance(content, list):
            children.extend(content)
        
        return widgets.VBox(
            children,
            layout=widgets.Layout(
                **{k.replace('-', '_'): v for k, v in 
                   dict(item.split(': ') for item in card_style.strip().split(';\n') if item.strip()).items()}
            )
        )
    
    @staticmethod
    def create_button(
        description: str,
        on_click: Optional[Callable] = None,
        variant: str = "primary",
        size: str = "medium",
        disabled: bool = False,
        icon: str = ""
    ) -> widgets.Button:
        """
        Create a modern styled button
        
        Args:
            description: Button text
            on_click: Click handler function
            variant: Style variant ('primary', 'secondary', 'success', 'warning', 'danger')
            size: Size variant ('small', 'medium', 'large')
            disabled: Whether button is disabled
            icon: Optional icon/emoji to prepend
        """
        
        # Button variants
        variants = {
            'primary': {
                'bg': TailwindColors.BLUE_600,
                'hover_bg': TailwindColors.BLUE_700,
                'text': TailwindColors.WHITE
            },
            'secondary': {
                'bg': TailwindColors.GRAY_600,
                'hover_bg': TailwindColors.GRAY_700,
                'text': TailwindColors.WHITE
            },
            'success': {
                'bg': TailwindColors.GREEN_600,
                'hover_bg': TailwindColors.GREEN_700,
                'text': TailwindColors.WHITE
            },
            'warning': {
                'bg': TailwindColors.ORANGE_600,
                'hover_bg': TailwindColors.ORANGE_600,
                'text': TailwindColors.WHITE
            },
            'danger': {
                'bg': TailwindColors.RED_600,
                'hover_bg': TailwindColors.RED_700,
                'text': TailwindColors.WHITE
            }
        }
        
        # Size configurations
        sizes = {
            'small': {'padding': f"{TailwindSpacing.XS} {TailwindSpacing.SM}", 'font_size': '14px'},
            'medium': {'padding': f"{TailwindSpacing.SM} {TailwindSpacing.BASE}", 'font_size': '16px'},
            'large': {'padding': f"{TailwindSpacing.MD} {TailwindSpacing.LG}", 'font_size': '18px'}
        }
        
        style_config = variants.get(variant, variants['primary'])
        size_config = sizes.get(size, sizes['medium'])
        
        # Prepare button text
        button_text = f"{icon} {description}".strip() if icon else description
        
        button = widgets.Button(
            description=button_text,
            disabled=disabled,
            layout=widgets.Layout(
                width='auto',
                height='auto'
            ),
            style={
                'button_color': style_config['bg'],
                'font_weight': '500'
            }
        )
        
        if on_click:
            button.on_click(on_click)
        
        return button
    
    @staticmethod
    def create_progress_bar(
        value: int,
        max_value: int = 100,
        description: str = "",
        variant: str = "primary",
        show_percentage: bool = True
    ) -> widgets.VBox:
        """
        Create a modern progress bar
        
        Args:
            value: Current progress value
            max_value: Maximum value
            description: Optional description text
            variant: Color variant ('primary', 'success', 'warning', 'danger')
            show_percentage: Whether to show percentage text
        """
        
        variants = {
            'primary': TailwindColors.BLUE_600,
            'success': TailwindColors.GREEN_600,
            'warning': TailwindColors.ORANGE_600,
            'danger': TailwindColors.RED_600
        }
        
        color = variants.get(variant, variants['primary'])
        percentage = min(100, (value / max_value) * 100)
        
        children = []
        
        if description:
            desc_widget = widgets.HTML(f"""
            <div style='
                margin-bottom: {TailwindSpacing.XS};
                color: {TailwindColors.GRAY_700};
                font-size: 14px;
                font-weight: 500;
            '>{description}</div>
            """)
            children.append(desc_widget)
        
        progress_html = f"""
        <div style='
            width: 100%;
            background-color: {TailwindColors.GRAY_200};
            border-radius: 9999px;
            height: 8px;
            overflow: hidden;
        '>
            <div style='
                width: {percentage}%;
                height: 100%;
                background-color: {color};
                border-radius: 9999px;
                transition: width 0.3s ease;
            '></div>
        </div>
        """
        
        if show_percentage:
            progress_html += f"""
            <div style='
                text-align: right;
                margin-top: {TailwindSpacing.XS};
                color: {TailwindColors.GRAY_600};
                font-size: 12px;
                font-weight: 500;
            '>{percentage:.1f}%</div>
            """
        
        progress_widget = widgets.HTML(progress_html)
        children.append(progress_widget)
        
        return widgets.VBox(children)
    
    @staticmethod
    def create_form_field(
        widget: widgets.Widget,
        label: str = "",
        help_text: str = "",
        required: bool = False,
        error_message: str = ""
    ) -> widgets.VBox:
        """
        Create a modern form field with label and help text
        
        Args:
            widget: The input widget
            label: Field label
            help_text: Optional help text
            required: Whether field is required
            error_message: Error message to display
        """
        
        children = []
        
        # Label
        if label:
            required_indicator = " *" if required else ""
            label_html = f"""
            <label style='
                display: block;
                margin-bottom: {TailwindSpacing.XS};
                color: {TailwindColors.GRAY_700};
                font-size: 14px;
                font-weight: 500;
            '>
                {label}{required_indicator}
            </label>
            """
            children.append(widgets.HTML(label_html))
        
        # Widget with error styling if needed
        if error_message:
            widget.layout.border = f"2px solid {TailwindColors.RED_500}"
        
        children.append(widget)
        
        # Help text or error message
        if error_message:
            help_html = f"""
            <div style='
                margin-top: {TailwindSpacing.XS};
                color: {TailwindColors.RED_600};
                font-size: 12px;
            '>{error_message}</div>
            """
            children.append(widgets.HTML(help_html))
        elif help_text:
            help_html = f"""
            <div style='
                margin-top: {TailwindSpacing.XS};
                color: {TailwindColors.GRAY_500};
                font-size: 12px;
            '>{help_text}</div>
            """
            children.append(widgets.HTML(help_html))
        
        return widgets.VBox(children)


# Convenience functions for backward compatibility and ease of use
def create_header(title: str, description: str = "", color: str = "blue") -> widgets.HTML:
    """Convenience function for creating headers"""
    return ModernUIComponents.create_section_header(title, description, color)

def create_info(content: str, type: str = "info") -> widgets.HTML:
    """Convenience function for creating info boxes"""
    return ModernUIComponents.create_info_box(content, type)

def create_card(content, title: str = "") -> widgets.VBox:
    """Convenience function for creating cards"""
    return ModernUIComponents.create_card(content, title)

def create_button(text: str, variant: str = "primary", on_click=None) -> widgets.Button:
    """Convenience function for creating buttons"""
    return ModernUIComponents.create_button(text, on_click, variant)