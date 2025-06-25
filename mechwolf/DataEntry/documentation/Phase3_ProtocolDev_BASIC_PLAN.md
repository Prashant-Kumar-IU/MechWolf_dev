# Phase3_ProtocolDev - Basic Implementation Plan

## 🎯 **Start Small Philosophy**

**Goal**: Create the simplest possible protocol GUI that actually works with Harvard pumps only. Focus on core functionality first, add features later.

**Core Principle**: Make it work, then make it better.

## 📋 **MVP Requirements (Week 1-2)**

### Essential Features Only:
1. **Add pump procedures** with basic parameters (start_time, duration, flow_rate)
2. **View procedures** in a simple table
3. **Basic validation** (no negative values, overlap detection)
4. **Generate MechWolf Protocol** that actually works
5. **Save/load** to experimental metadata

### What We're NOT Building Initially:
- ❌ Timeline visualization (add later)
- ❌ Drag-and-drop interface (add later)  
- ❌ Multi-component support (Harvard pumps only)
- ❌ Real-time monitoring (add later)
- ❌ Complex validation (basic only)

## 📁 **Minimal File Structure**

Start with just 3 files:

```
Phase3_ProtocolDev/
├── __init__.py                 # Simple entry point
├── basic_protocol_gui.py       # Single-file GUI implementation  
└── harvard_pump_handler.py     # Harvard pump specific logic
```

**That's it.** No complex architecture, no multiple modules. Get it working first.

## 🔧 **Core Data Models (Keep Simple)**

### Procedure Data Structure:
```python
{
    "pump_id": "pump_1",           # From apparatus
    "start_time": 0.0,             # Seconds
    "duration": 300.0,             # Seconds  
    "flow_rate": 2.5,              # mL/min
    "direction": "infuse"          # infuse/withdraw
}
```

### Basic Validation Rules:
```python
def validate_procedure(procedure):
    errors = []
    if procedure["start_time"] < 0:
        errors.append("Start time must be ≥ 0")
    if procedure["duration"] <= 0:
        errors.append("Duration must be > 0")
    if procedure["flow_rate"] <= 0:
        errors.append("Flow rate must be > 0")
    return errors
```

## 🎨 **Simple GUI Design**

### Tab Structure:
1. **📝 Add Procedures Tab**: Simple form to add pump procedures
2. **📋 View Procedures Tab**: Table showing all added procedures  
3. **⚙️ Generate Protocol Tab**: Create MechWolf Protocol object

### Add Procedures Form:
```python
# Basic input widgets
pump_dropdown = Dropdown(options=harvard_pumps)
start_time_input = FloatText(description="Start (s):")
duration_input = FloatText(description="Duration (s):")
flow_rate_input = FloatText(description="Rate (mL/min):")
direction_dropdown = Dropdown(options=["infuse", "withdraw"])
add_button = Button(description="Add Procedure")
```

### Procedures Table:
```python
# Simple HTML table showing:
# | Pump | Start (s) | Duration (s) | Rate (mL/min) | Direction | Actions |
# | pump_1 | 0 | 300 | 2.5 | infuse | Edit | Delete |
```

## 💾 **Integration Points**

### Load Apparatus from Phase 2:
```python
def load_harvard_pumps(experiment_manager):
    """Get Harvard pumps from apparatus configuration."""
    apparatus_data = experiment_manager.apparatus.get_apparatus_config()
    harvard_pumps = []
    
    for comp_id, comp_data in apparatus_data["components"]["active"].items():
        if comp_data["component_type"] == "HarvardSyringePump":
            harvard_pumps.append(comp_id)
    
    return harvard_pumps
```

### Save to Experimental Metadata:
```python
def save_procedures(experiment_manager, procedures):
    """Save procedures to experimental metadata."""
    # Clear existing procedures
    experiment_manager.protocol.procedures = []
    
    # Add new procedures
    for proc in procedures:
        experiment_manager.protocol.add_procedure({
            "component_id": proc["pump_id"],
            "start_time": proc["start_time"], 
            "duration": proc["duration"],
            "parameters": {
                "rate": f'{proc["flow_rate"]} mL/min',
                "direction": proc["direction"]
            }
        })
    
    experiment_manager.save()
```

### Generate MechWolf Protocol:
```python
def create_mechwolf_protocol(apparatus, procedures):
    """Create executable MechWolf Protocol."""
    import mechwolf as mw
    
    protocol = mw.Protocol(apparatus)
    
    for proc in procedures:
        pump = apparatus[proc["pump_id"]]  # Get pump by ID
        protocol.add(
            pump,
            start=f'{proc["start_time"]}s',
            duration=f'{proc["duration"]}s',
            rate=f'{proc["flow_rate"]} mL/min',
            # Note: Harvard pumps might not support direction parameter
            # Check MechWolf documentation for correct parameter names
        )
    
    return protocol
```

## ✅ **Week 1 Implementation Checklist**

### Day 1-2: Setup & Basic Structure
- [ ] Create `Phase3_ProtocolDev/` directory
- [ ] Create `__init__.py` with simple entry point
- [ ] Create `basic_protocol_gui.py` skeleton
- [ ] Create `harvard_pump_handler.py` skeleton
- [ ] Test imports work in Jupyter

### Day 3-4: Core GUI 
- [ ] Implement Add Procedures tab with basic form
- [ ] Implement View Procedures tab with HTML table
- [ ] Add basic form validation
- [ ] Test adding/viewing procedures

### Day 5-7: Integration & Protocol Generation
- [ ] Load Harvard pumps from experimental metadata
- [ ] Save procedures to experimental metadata
- [ ] Generate basic MechWolf Protocol object
- [ ] Test complete workflow in Jupyter

## ✅ **Week 2 Enhancement Checklist**

### Enhanced Validation
- [ ] Check for time overlaps on same pump
- [ ] Validate pump exists in apparatus
- [ ] Add parameter range validation
- [ ] Better error messages

### Edit/Delete Functionality  
- [ ] Edit existing procedures
- [ ] Delete procedures
- [ ] Confirm deletion dialogs
- [ ] Refresh table after changes

### Protocol Preview
- [ ] Show text summary of protocol
- [ ] Display total runtime
- [ ] Show procedure count per pump
- [ ] Basic timeline text view

## 📖 **Basic Usage Example**

```python
# Cell 1: Load experiment from Phase 2
from mechwolf.DataEntry.experimental_metadata import ExperimentalMetadataManager
experiment = ExperimentalMetadataManager("my_experiment.json")

# Cell 2: Launch basic protocol GUI
from mechwolf.DataEntry import Phase3_ProtocolDev
protocol_gui = Phase3_ProtocolDev.launch_basic_gui(experiment)

# Cell 3: Build protocol using GUI
# User adds procedures:
# - pump_1: start=0s, duration=300s, rate=2.5 mL/min, direction=infuse
# - pump_1: start=400s, duration=600s, rate=1.0 mL/min, direction=infuse

# Cell 4: Generate MechWolf protocol
import mechwolf as mw

# Get apparatus from Phase 2 data  
apparatus = protocol_gui.get_apparatus()

# Get protocol from GUI procedures
protocol = protocol_gui.get_protocol()

# Cell 5: Validate and preview
print("Protocol Summary:")
print(f"Total procedures: {len(protocol.procedures)}")
print(f"Total runtime: {protocol_gui.get_total_runtime()}s")

# Cell 6: Execute protocol
experiment = protocol.execute(dry_run=1000)  # 1000x speed for testing
```

## 🔍 **Overlap Detection Logic**

```python
def check_overlaps(procedures, new_procedure):
    """Check if new procedure overlaps with existing ones on same pump."""
    overlaps = []
    
    new_start = new_procedure["start_time"]
    new_end = new_start + new_procedure["duration"]
    new_pump = new_procedure["pump_id"]
    
    for proc in procedures:
        if proc["pump_id"] == new_pump:
            proc_start = proc["start_time"]
            proc_end = proc_start + proc["duration"]
            
            # Check for overlap
            if not (new_end <= proc_start or new_start >= proc_end):
                overlaps.append(f"Overlaps with procedure at {proc_start}s")
    
    return overlaps
```

## 🚀 **Future Enhancement Path (After MVP)**

### Phase 3.1: Visual Timeline (Week 3-4)
- Replace table with interactive timeline widget
- Drag-and-drop procedure positioning
- Visual overlap indicators
- Zoom and pan functionality

### Phase 3.2: Multi-Component Support (Week 5-6)  
- Add valve procedures
- Add sensor procedures
- Component-specific parameter forms
- Enhanced validation for multi-component protocols

### Phase 3.3: Advanced Features (Week 7+)
- Real-time execution monitoring
- Protocol templates library
- Import/export protocols
- Optimization suggestions

## 💡 **Key Design Decisions**

### Start with Forms, Not Timeline
- Forms are easier to implement and debug
- Users can still build complex protocols
- Timeline can be added later without breaking existing code

### Harvard Pumps Only Initially
- Reduces complexity significantly
- Most common use case for flow chemistry
- Easy to extend to other components later

### Simple Data Structures
- Use basic dictionaries, not complex classes
- Easy to serialize/deserialize
- Simple to debug and modify

### Direct MechWolf Integration
- Generate standard `mw.Protocol` objects
- Use existing MechWolf validation
- Leverage existing execution engine

## ⚠️ **Potential Gotchas**

### Harvard Pump Parameters
- Check MechWolf documentation for exact parameter names
- Some pumps might not support all parameters (direction, etc.)
- Syringe volume limits flow rate ranges

### Time Units Consistency  
- Keep everything in seconds internally
- Convert to/from user-friendly units in GUI
- Be consistent with MechWolf time format

### Apparatus Loading
- Ensure apparatus from Phase 2 actually contains Harvard pumps
- Handle case where no Harvard pumps are configured
- Validate pump IDs exist before adding procedures

## 🎯 **Success Criteria for MVP**

After Week 2, we should have:
- [ ] **Working GUI** that runs in Jupyter without errors
- [ ] **Can add Harvard pump procedures** with basic parameters
- [ ] **Basic validation** prevents invalid inputs
- [ ] **Generates working mw.Protocol** object that can be executed
- [ ] **Saves/loads procedures** to/from experimental metadata
- [ ] **Ready for timeline enhancement** (clean, modular code)

This basic plan focuses on getting core functionality working quickly, then building on that foundation. The key is to have something useful after just 1-2 weeks that can be enhanced incrementally.
