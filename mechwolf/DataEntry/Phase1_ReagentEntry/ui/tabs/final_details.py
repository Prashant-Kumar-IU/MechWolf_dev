"""
Final details tab implementation.

This module handles the experiment final details interface including mass scale,
concentration, solvent, and stoichiometry calculations, extracted from the
original monolithic UI file for better maintainability.
"""

import ipywidgets as widgets
from typing import Dict, Any, Callable, Optional
from ..components.base import SectionHeader, ButtonFactory, MessageArea, FormContainer
from ...core.services import ExperimentService


class FinalDetailsTab:
    """
    Tab for experiment final details and stoichiometry calculations.
    
    This class handles experiment parameters, calculations, and final processing,
    delegating business logic to the ExperimentService.
    """
    
    def __init__(self, experiment_service: ExperimentService):
        """
        Initialize final details tab.
        
        Args:
            experiment_service: Service for experiment operations
        """
        self.experiment_service = experiment_service
        self.on_experiment_completed = None  # Callback for completion
        
        # Create the tab UI
        self._create_tab()
        
        # Load current data
        self._load_current_data()
    
    def _create_tab(self) -> widgets.Widget:
        """Create the final details tab interface."""
        
        # Create header
        header = SectionHeader.create(
            "⚗️ Final Details",
            description="Set experiment parameters and process data"
        )
        
        # Create message area
        self.message_area = MessageArea()
        
        # Create limiting reagent display
        self.limiting_reagent_display = widgets.HTML("")
        
        # Create form fields
        self._create_form_fields()
        
        # Create volume calculation display
        self.volume_display = widgets.HTML(
            "<p><b>Volume needed:</b> Enter values above to calculate</p>"
        )
        
        # Set up volume calculation observers
        self.mass_scale_input.observe(self._update_volume, names='value')
        self.concentration_input.observe(self._update_volume, names='value')
        
        # Create buttons
        self.process_button = ButtonFactory.create_success("💾 Process Data")
        self.process_button.on_click(self._handle_process_data)
        
        self.stoichiometry_button = ButtonFactory.create_info("📊 Create Stoichiometry Table")
        self.stoichiometry_button.on_click(self._handle_stoichiometry)
        
        button_row = widgets.HBox([
            self.process_button,
            self.stoichiometry_button
        ], layout=widgets.Layout(gap="10px"))
        
        # Create form content
        form_fields = [
            widgets.HTML("<h4>Experiment Parameters</h4>"),
            self.message_area.widget,
            self.limiting_reagent_display,
            self._create_form_field(self.mass_scale_input, "Mass of limiting reagent in mg"),
            self._create_form_field(self.concentration_input, "Final concentration in mM"),
            self.volume_display,
            self._create_form_field(self.solvent_input, "Solvent(s) used"),
            button_row
        ]
        
        # Create form container
        form_container = FormContainer.create(form_fields, "solid")
        
        # Create stoichiometry display area
        self.stoichiometry_area = widgets.Output(
            layout=widgets.Layout(
                border='1px solid #ddd',
                padding='10px',
                margin='10px 0'
            )
        )
        
        # Create tab content
        self.widget = widgets.VBox([
            header,
            form_container,
            self.stoichiometry_area
        ])
        
        # Initial updates
        self._refresh_limiting_reagent_display()
        
        return self.widget
    
    def _create_form_fields(self):
        """Create the form input fields."""
        self.mass_scale_input = widgets.FloatText(
            description="Mass scale (mg):",
            layout=widgets.Layout(width="80%")
        )
        
        self.concentration_input = widgets.FloatText(
            description="Concentration (mM):",
            layout=widgets.Layout(width="80%")
        )
        
        self.solvent_input = widgets.Text(
            description="Solvents:",
            layout=widgets.Layout(width="80%")
        )
    
    def _create_form_field(self, widget: widgets.Widget, tooltip: str) -> widgets.VBox:
        """Create a form field with tooltip."""
        tooltip_html = widgets.HTML(
            f"<span style='font-size: 0.8em; color: #666;'>{tooltip}</span>"
        )
        return widgets.VBox([widget, tooltip_html])
    
    def _load_current_data(self):
        """Load current experiment data into form fields."""
        try:
            experiment = self.experiment_service.get_current_experiment()
            
            if experiment.mass_scale:
                self.mass_scale_input.value = experiment.mass_scale
            if experiment.concentration:
                self.concentration_input.value = experiment.concentration
            if experiment.solvent:
                self.solvent_input.value = experiment.solvent
                
        except Exception as e:
            self.message_area.show_error(f"Error loading data: {str(e)}")
    
    def _refresh_limiting_reagent_display(self):
        """Refresh the limiting reagent display."""
        try:
            experiment = self.experiment_service.get_current_experiment()
            
            if experiment.limiting_reagent:
                reagent_html = f"""
                <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 5px; padding: 10px; margin: 10px 0;">
                    <b>Limiting Reagent:</b> {experiment.limiting_reagent.name} 
                    (MW: {experiment.limiting_reagent.molecular_weight} g/mol)
                </div>
                """
            else:
                reagent_html = """
                <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 5px; padding: 10px; margin: 10px 0;">
                    <b>Limiting Reagent:</b> <span style="color: red;">None selected</span><br>
                    <small>Set one reagent to eq=1.0 to define the limiting reagent</small>
                </div>
                """
            
            self.limiting_reagent_display.value = reagent_html
            
        except Exception as e:
            self.limiting_reagent_display.value = f"<p style='color: red;'>Error: {str(e)}</p>"
    
    def _update_volume(self, change=None):
        """Update volume calculation display."""
        try:
            mass_scale = self.mass_scale_input.value
            concentration = self.concentration_input.value
            
            if mass_scale <= 0 or concentration <= 0:
                self.volume_display.value = "<p><b>Volume needed:</b> Please enter valid mass scale and concentration values</p>"
                return
            
            experiment = self.experiment_service.get_current_experiment()
            limiting_reagent = experiment.limiting_reagent
            
            if not limiting_reagent:
                self.volume_display.value = "<p><b>Volume needed:</b> No limiting reagent defined</p>"
                return
            
            # Calculate volume
            limiting_mw = limiting_reagent.molecular_weight
            moles_limiting = mass_scale / limiting_mw  # mg to mmol (since MW is in g/mol)
            volume_ml = moles_limiting / concentration  # mmol / mM = mL
            
            self.volume_display.value = f"<p><b>Volume needed:</b> {volume_ml:.4f} mL</p>"
            
        except Exception as e:
            self.volume_display.value = f"<p><b>Volume needed:</b> Error: {str(e)}</p>"
    
    def _handle_process_data(self, button):
        """Handle process data button click."""
        try:
            # Get form values
            mass_scale = self.mass_scale_input.value
            concentration = self.concentration_input.value
            solvent = self.solvent_input.value
            
            # Validate experiment completeness
            is_complete, issues = self.experiment_service.validate_experiment_completeness()
            
            if not is_complete:
                self.message_area.show_errors(issues)
                return
            
            # Save final details
            success, errors = self.experiment_service.update_final_details(
                mass_scale, concentration, solvent
            )
            
            if success:
                self.message_area.show_success(
                    "Final details saved successfully! Your experiment data has been processed."
                )
                
                # Notify completion callback
                if self.on_experiment_completed:
                    self.on_experiment_completed()
                    
            else:
                self.message_area.show_errors(errors)
                
        except Exception as e:
            self.message_area.show_error(f"Error processing data: {str(e)}")
    
    def _handle_stoichiometry(self, button):
        """Handle stoichiometry table creation."""
        try:
            # Calculate stoichiometry
            stoich_data, errors = self.experiment_service.calculate_stoichiometry()
            
            if errors:
                self.message_area.show_errors(errors)
                return
            
            # Generate and display stoichiometry table
            self._display_stoichiometry_table(stoich_data)
            
        except Exception as e:
            self.message_area.show_error(f"Error creating stoichiometry table: {str(e)}")
    
    def _display_stoichiometry_table(self, stoich_data: Dict[str, Any]):
        """Display the stoichiometry table."""
        with self.stoichiometry_area:
            from IPython.display import clear_output, HTML, display
            clear_output(wait=True)
            
            # Generate table HTML
            html = self._generate_stoichiometry_html(stoich_data)
            display(HTML(html))
    
    def _generate_stoichiometry_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for stoichiometry table."""
        html = f"""
        <div style="max-width: 1200px; margin: 20px auto; font-family: Arial, sans-serif;">
            <h2 style="color: #2563eb; text-align: center; margin-bottom: 30px;">
                📊 Stoichiometry Table
            </h2>
            
            <!-- Experiment Summary -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                <h3 style="color: #1e40af; margin-top: 0;">Experiment Parameters</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div><strong>Limiting Reagent:</strong> {data['limiting_reagent']}</div>
                    <div><strong>Mass Scale:</strong> {data['mass_scale_mg']} mg</div>
                    <div><strong>Concentration:</strong> {data['concentration_mM']} mM</div>
                    <div><strong>Solvent:</strong> {data.get('solvent', 'Not specified')}</div>
                    <div><strong>Limiting Reagent Amount:</strong> {data['limiting_moles_mmol']:.3f} mmol</div>
                </div>
            </div>
            
            <!-- Reagents Table -->
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white;">
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Reagent</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">MW (g/mol)</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Equivalents</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Amount (mmol)</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Mass (mg)</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Density (g/mL)</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Volume (μL)</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Position</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add reagent rows
        for i, reagent in enumerate(data['reagents']):
            row_style = "background: #f8fafc;" if i % 2 == 0 else "background: white;"
            
            # Format volume display
            if reagent['type'] == 'liquid' and 'volume_ul' in reagent:
                volume_display = f"{reagent['volume_ul']:.1f}"
                mass_display = f"{reagent['mass_mg']:.1f}"
            else:
                volume_display = "—"
                mass_display = f"{reagent['mass_mg']:.1f}"
            
            # Format density display
            if reagent['type'] == 'liquid' and 'density' in reagent:
                density_display = f"{reagent['density']:.2f}"
            else:
                density_display = "—"
            
            html += f"""
                    <tr style="{row_style}">
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; word-wrap: break-word; max-width: 200px; white-space: normal; line-height: 1.4;">
                            <strong>{reagent['name']}</strong>
                        </td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent['molecular_weight']:.1f}</td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent['equivalents']:.2f}</td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent['moles_mmol']:.3f}</td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{mass_display}</td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{density_display}</td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{volume_display}</td>
                        <td style="padding: 18px 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{reagent['position']}</td>
                    </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- Notes -->
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 20px; margin-top: 20px;">
                <h4 style="color: #1e40af; margin-top: 0;">Notes</h4>
                <ul style="margin: 0; padding-left: 20px; color: #374151;">
                    <li>Calculations based on limiting reagent and mass scale</li>
                    <li>Volume calculations for liquid reagents only</li>
                    <li>Uses densities from reagent properties</li>
                    <li>All volumes in microliters (μL) for precision</li>
                </ul>
            </div>
        </div>
        """
        
        return html
    
    def refresh_display(self):
        """Refresh the display with current data."""
        self._refresh_limiting_reagent_display()
        self._load_current_data()
        self._update_volume()
    
    def set_completion_callback(self, callback: Callable):
        """
        Set callback for experiment completion.
        
        Args:
            callback: Function to call when experiment is completed
        """
        self.on_experiment_completed = callback
    
    def get_widget(self) -> widgets.Widget:
        """Get the tab widget."""
        return self.widget


# Factory function for backward compatibility
def create_final_details_tab(experiment_service: ExperimentService) -> FinalDetailsTab:
    """
    Factory function to create a final details tab.
    
    Args:
        experiment_service: Service for experiment operations
        
    Returns:
        FinalDetailsTab instance
    """
    return FinalDetailsTab(experiment_service)


__all__ = ['FinalDetailsTab', 'create_final_details_tab']