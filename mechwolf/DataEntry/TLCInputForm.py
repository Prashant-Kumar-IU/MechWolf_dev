import ipywidgets as widgets
from IPython.display import display, clear_output

class TLCInputForm:
    def __init__(self):
        self.main_output = widgets.Output()
        with self.main_output:
            self.create_initial_widgets()
    
    def create_initial_widgets(self):
        # Initial form for number of spots
        spots_box = widgets.VBox([
            widgets.Label('Number of spots:'),
            widgets.IntText(min=1, layout=widgets.Layout(width='200px')),
            widgets.Button(description='Create Form')
        ])
        
        spots_box.children[2].on_click(self.on_create_form)
        self.spots_box = spots_box
        display(spots_box)
        
    def on_create_form(self, b):
        try:
            num_spots = self.spots_box.children[1].value
            if num_spots <= 0:
                raise ValueError("Please enter a positive number")
                
            clear_output()
            
            # Create headers with bigger font and bold styling
            headers = widgets.HBox([
                widgets.HTML(
                    value='<h2 style="font-size: 16px; margin: 0;">Identity of spot</h2>',
                    layout=widgets.Layout(width='200px')
                ),
                widgets.HTML(
                    value='<h2 style="font-size: 16px; margin: 0;">Distance from baseline (cm)</h2>',
                    layout=widgets.Layout(width='200px')
                )
            ], layout=widgets.Layout(justify_content='space-between', width='500px', margin='5px 0'))
            
            # Create input boxes for samples
            inputs = []
            for i in range(num_spots):
                sample_name = widgets.Text(
                    placeholder=f'Spot {i+1}',
                    layout=widgets.Layout(width='200px')
                )
                sample_distance = widgets.FloatText(
                    layout=widgets.Layout(width='200px')
                )
                inputs.append(widgets.HBox([
                    sample_name,
                    sample_distance
                ], layout=widgets.Layout(justify_content='space-between', width='500px')))
            
            # Add solvent distance input with matching header style and spacing
            solvent_distance = widgets.VBox([
                widgets.HTML(
                    value='<h2 style="font-size: 16px; margin: 5;">Distance travelled by solvent front (cm)</h2>',
                    layout=widgets.Layout(width='200px')
                ),
                widgets.FloatText(layout=widgets.Layout(width='200px'))
            ], layout=widgets.Layout(margin='0px 0 20px 0'))  # Add top margin for spacing

            calc_button = widgets.Button(
                description='Calculate Rf Values',
                button_style='success',
                style={'button_color': '#007F5F', 'font_color': 'black'}
            )
            
            result_output = widgets.Output()
            
            def on_calculate(b):
                with result_output:
                    clear_output()
                    try:
                        solvent_dist = solvent_distance.children[1].value
                        if solvent_dist == 0:
                            raise ValueError("Solvent distance cannot be zero")
                            
                        for i in range(num_spots):
                            sample_name = inputs[i].children[0].value or f"Spot {i+1}"
                            sample_dist = inputs[i].children[1].value
                            rf = round(sample_dist / solvent_dist, 4)
                            print(f"RF value for {sample_name}: {rf}")
                    except Exception as e:
                        print(f"Error: {e}")
            
            calc_button.on_click(on_calculate)
            
            display(widgets.VBox([
                headers,
                widgets.VBox(inputs),
                solvent_distance,
                calc_button,
                result_output
            ]))
            
        except Exception as e:
            print(f"Error: {e}")

def create_tlc_form():
    return TLCInputForm()

if __name__ == "__main__":
    create_tlc_form()