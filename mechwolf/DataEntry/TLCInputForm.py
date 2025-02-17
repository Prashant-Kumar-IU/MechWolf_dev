import ipywidgets as widgets
from IPython.display import display, clear_output

class TLCInputForm:
    def __init__(self):
        self.create_widgets()
    
    def create_widgets(self):
        self.num_spots_input = widgets.IntText(description="Number of spots:", layout=widgets.Layout(width='400px'))
        self.num_spots_button = widgets.Button(description="Submit")
        self.num_spots_button.on_click(self.create_sample_inputs)
        
        self.output = widgets.Output()
        
        display(widgets.VBox([
            self.num_spots_input,
            self.num_spots_button,
            self.output
        ]))
    
    def create_sample_inputs(self, b):
        with self.output:
            self.output.clear_output()
            try:
                num_spots = self.num_spots_input.value
                if num_spots <= 0:
                    raise ValueError("Number of spots must be greater than zero.")
                
                self.sample_inputs = []
                for i in range(1, num_spots + 1):
                    sample_input = widgets.VBox([
                        widgets.Label(f"Distance moved by sample {i} (cm):"),
                        widgets.FloatText(layout=widgets.Layout(width='400px'))
                    ])
                    self.sample_inputs.append(sample_input)
                
                self.solvent_distance_input = widgets.VBox([
                    widgets.Label("Distance moved by solvent (cm):"),
                    widgets.FloatText(layout=widgets.Layout(width='400px'))
                ])
                
                self.calculate_button = widgets.Button(description="Calculate RF values")
                self.calculate_button.on_click(self.calculate_rf_values)
                
                display(widgets.VBox(self.sample_inputs + [self.solvent_distance_input, self.calculate_button, self.output]))
            except Exception as e:
                print(f"Error: {e}")
    
    def calculate_rf_values(self, b):
        with self.output:
            self.output.clear_output()
            try:
                solvent_distance = self.solvent_distance_input.children[1].value
                if solvent_distance == 0:
                    raise ZeroDivisionError("Solvent distance cannot be zero.")
                
                rf_values = []
                for sample_input in self.sample_inputs:
                    sample_distance = sample_input.children[1].value
                    rf_value = round(sample_distance / solvent_distance, 4)
                    rf_values.append(rf_value)
                
                for i, rf_value in enumerate(rf_values, start=1):
                    print(f"RF value for sample {i}: {rf_value}")
            except ZeroDivisionError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    TLCInputForm()
