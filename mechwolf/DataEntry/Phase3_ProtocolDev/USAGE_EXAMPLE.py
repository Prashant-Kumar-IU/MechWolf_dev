"""
Phase 3 Simple Protocol Builder - Usage Example

This example demonstrates how to use the new Simple Protocol Builder
to create MechWolf protocols with clean, readable code generation.
"""

# Step 1: Import the experimental metadata system
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager

# Step 2: Load or create an experiment with apparatus from Phase 2
experiment = ExperimentalMetadataManager("my_flow_experiment.json")

# If you don't have an experiment file yet, you can create one:
# experiment = ExperimentalMetadataManager(
#     filename="my_flow_experiment.json",
#     experiment_name="Flow Synthesis Example"
# )

# Step 3: Launch the Simple Protocol Builder
from mechwolf.DataEntry.Phase3_ProtocolDev import launch_simple_builder

protocol_builder = launch_simple_builder(experiment)

# The GUI will open with 4 tabs:
# 1. ⏱️ Time Variables - Define reusable time variables
# 2. ➕ Add Procedures - Add protocol steps
# 3. 📋 View Procedures - Review current procedures  
# 4. 💻 Generated Code - See the MechWolf code

print("""
🧪 SIMPLE PROTOCOL BUILDER USAGE:

1. TIME VARIABLES TAB:
   - Add common time variables like PPh3=2min, H2O=1min, switch=45s
   - Use preset buttons for quick setup
   - The 'current' variable tracks protocol time

2. ADD PROCEDURES TAB:
   - Select component (pump, valve) from your apparatus
   - Choose action (run, switch, etc.)
   - Set timing using variables: current, PPh3 + H2O, etc.
   - Add parameters like flow rate
   - Check "increment current time" to automatically advance timing

3. VIEW PROCEDURES TAB:
   - Review all your protocol steps
   - Delete unwanted steps
   - See the logical flow of your protocol

4. GENERATED CODE TAB:
   - Copy the clean MechWolf protocol code
   - Code includes proper timedelta variables
   - Ready to paste into your notebook

EXAMPLE WORKFLOW:
1. Define time variables: PPh3 = 2min, H2O = 1min, switch = 45s
2. Add procedure: pump_1 run at current for PPh3 + H2O at 0.5 mL/min
3. Add procedure: pump_2 run at current for H2O at 1 mL/min  
4. Generate code and copy to notebook

The generated code will look like:
```python
import mechwolf as mw
from datetime import timedelta

switch = timedelta(seconds = 45)
current = timedelta(minutes = 0)
PPh3 = timedelta(minutes = 2)
H2O = timedelta(minutes = 1) 

P = mw.Protocol(A)

P.add(pump_1, start = current,
              duration = PPh3 + H2O, rate = "0.5 mL/min")
current += PPh3

P.add(pump_2, start = current, 
              duration = H2O, rate = "1 mL/min")
current += H2O + switch

print(f'TOTAL TIME: {current}')
# P.execute(confirm = True)
```
""")

# Step 4: After building your protocol, get the generated code
def get_protocol_code():
    """Get the generated protocol code"""
    return protocol_builder.get_generated_code()

# Step 5: Get the apparatus for executing the protocol
def get_apparatus():
    """Get the apparatus object for protocol execution"""
    return protocol_builder.get_apparatus()

# Step 6: Example of using the generated code in a notebook
def example_notebook_usage():
    """
    Example of how to use the generated code in a Jupyter notebook
    """
    code_example = '''
# Cell 1: Load the apparatus
from mechwolf.DataEntry.shared_components.apparatus_factory import ApparatusFactory
A = ApparatusFactory.create_apparatus_from_experiment(experiment)

# Cell 2: Paste the generated protocol code here
import mechwolf as mw
from datetime import timedelta

switch = timedelta(seconds = 45)
current = timedelta(minutes = 0)
PPh3 = timedelta(minutes = 2)
H2O = timedelta(minutes = 1) 

P = mw.Protocol(A)

P.add(pump_1, start = current,
              duration = PPh3 + H2O, rate = "0.5 mL/min")
current += PPh3

P.add(pump_2, start = current, 
              duration = H2O, rate = "1 mL/min")
current += H2O + switch

print(f'TOTAL TIME: {current}')

# Cell 3: Execute the protocol
# For testing with dry run (1000x speed):
# experiment = P.execute(dry_run=1000)

# For real execution:
# experiment = P.execute(confirm=True)
    '''
    
    print("📓 JUPYTER NOTEBOOK USAGE EXAMPLE:")
    print("=" * 50)
    print(code_example)

if __name__ == "__main__":
    print("Simple Protocol Builder loaded successfully!")
    print("Use the GUI tabs to build your protocol step by step.")
    print("\nCall example_notebook_usage() to see how to use the generated code.")