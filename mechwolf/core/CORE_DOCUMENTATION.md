# MechWolf Core Documentation

## Overview

The MechWolf core module provides the fundamental orchestration layer for flow chemistry automation. It manages apparatus networks, protocol definitions, experiment execution, and real-time monitoring. This module serves as the bridge between physical components and high-level experimental workflows.

## Architecture

### Core Classes Hierarchy

```
Apparatus (physical setup)
    ↓
Protocol (procedural instructions)
    ↓
Experiment (execution context)
    ↓
ExecutionEngine (real-time control)
```

## Core Files

### apparatus.py - Physical System Management

#### Apparatus Class
**Purpose**: Represents a unique network of connected components in a flow chemistry setup.

**Key Features**:
- Component network management with graph-based validation
- Connection modeling using named tuples
- Visual diagram generation with Graphviz
- Automatic network validation and connectivity checking

**Core Attributes**:
- `components`: Set of all components in the apparatus
- `network`: List of Connection namedtuples (from_component, to_component, tube)
- `name`: Apparatus identifier (auto-generated or user-defined)
- `description`: Human-readable apparatus description

**Key Methods**:

#### add(from_component, to_component, tube)
- **Purpose**: Establishes connections between components
- **Features**: 
  - Supports single components or iterables
  - Cartesian product connections for multiple components
  - Duplicate connection detection and warnings
  - Component name uniqueness validation

#### visualize(title, label_tubes, describe_vessels, **kwargs)
- **Purpose**: Generates apparatus network diagrams
- **Output**: Graphviz-based visual representation
- **Customization**: Node shapes, edge labels, graph layout options
- **Formats**: PDF, PNG output with customizable styling

#### _validate()
- **Purpose**: Ensures apparatus integrity
- **Checks**: 
  - Network connectivity (using NetworkX)
  - Valve mapping completeness
  - Component relationships

#### Component Access Patterns
```python
# Access by type
pumps = apparatus[Pump]
valves = apparatus[Valve]

# Access by name
pump1 = apparatus["pump_1"]

# Check membership
if component in apparatus:
    component_ref = apparatus[component]
```

**Connection Management**:
- Named tuple structure: `Connection(from_component, to_component, tube)`
- Automatic component registration upon connection
- Bidirectional graph validation for connectivity

---

### protocol.py - Experimental Procedure Definition

#### Protocol Class
**Purpose**: Defines a sequence of timed procedures for apparatus components.

**Core Concepts**:
- **Procedure**: Atomic operation on a single component with timing and parameters
- **Compilation**: Conversion of high-level procedures into device-specific instructions
- **Validation**: Parameter checking and conflict detection

**Key Attributes**:
- `apparatus`: Reference to the physical setup
- `procedures`: List of procedure dictionaries
- `name`: Protocol identifier
- `description`: Protocol documentation

**Procedure Structure**:
```python
{
    "start": float,           # Start time in seconds
    "stop": float,            # Stop time in seconds  
    "component": ActiveComponent,  # Target component
    "params": dict            # Component-specific parameters
}
```

#### add(component, start, stop, duration, **kwargs)
- **Purpose**: Adds timed procedures to the protocol
- **Timing Options**:
  - `start`: Absolute start time or timedelta
  - `stop`: Absolute stop time or timedelta
  - `duration`: Procedure duration (alternative to stop)
- **Parameter Validation**:
  - Dimensional analysis for Pint quantities
  - Type checking against component attributes
  - Valve mapping resolution

**Component-Specific Logic**:

**Pumps**:
```python
P.add(pump, start="0s", duration="5min", rate="2.5 mL/min")
```

**Valves**:
```python
P.add(valve, start="1min", duration="10min", setting="position_A")
# Automatic mapping resolution: component name → port number
```

**Sensors**:
```python
P.add(sensor, start="0s", duration="30min", rate="10 Hz")
```

**Temperature Controllers**:
```python
P.add(temp_control, start="0s", duration="60min", temp="25 degC", active=True)
```

#### _compile(dry_run=True)
- **Purpose**: Converts procedures into executable device instructions
- **Process**:
  1. Groups procedures by component
  2. Sorts by start time
  3. Infers missing stop times
  4. Detects overlapping procedures
  5. Inserts base state returns
- **Output**: Dictionary mapping components to instruction lists

**Timing Resolution**:
- Automatic inference of missing stop times
- Next procedure start time becomes current stop time
- Protocol end time inference from longest procedure
- Overlap detection with floating-point tolerance

**State Management**:
- Components return to `_base_state` between procedures
- Continuous procedures skip base state returns
- State transitions at precise timing boundaries

#### Visualization and Export

**visualize(legend, width, renderer)**
- **Purpose**: Interactive Gantt chart of protocol timeline
- **Technology**: Altair/Vega-Lite for interactive visualization
- **Features**:
  - Component-wise procedure bars
  - Tooltip details for parameters
  - Time axis with h:m:s formatting
  - Color coding by parameter sets

**Export Formats**:
- `json()`: Structured procedure data
- `yaml()`: Human-readable procedure format
- `to_dict()`: Component-keyed compiled instructions
- `to_list()`: Flat list of all procedures

---

### experiment.py - Execution Context Management

#### Experiment Class
**Purpose**: Manages real-time protocol execution with data collection and monitoring.

**Key Features**:
- Real-time sensor data streaming
- Interactive execution controls (pause/resume/cancel)
- Comprehensive logging and data persistence
- Live visualization updates

**Core Attributes**:
- `protocol`: Source protocol definition
- `apparatus`: Physical system reference
- `experiment_id`: Unique experiment identifier
- `data`: Collected sensor data by device
- `start_time`/`end_time`: Execution timestamps
- `executed_procedures`: Log of completed procedures

**Data Collection**:
- `Datapoint` namedtuple: `(data, timestamp, experiment_elapsed_time)`
- Device-keyed data storage: `{sensor_name: [Datapoint, ...]}`
- Real-time streaming with async generators
- Automatic unit tracking per sensor

**Execution States**:
- `_is_executing`: Currently running
- `_paused`: Temporarily suspended
- `cancelled`: User-terminated
- `was_executed`: Completed successfully

**Interactive Controls**:
- Live pause/resume functionality
- Emergency cancellation
- Real-time parameter monitoring
- Execution progress tracking

---

### execute.py - Real-Time Execution Engine

#### main(experiment, dry_run, strict)
**Purpose**: Core async execution engine for protocol procedures.

**Execution Flow**:
1. **Pre-flight Validation**: Component status and protocol integrity
2. **Context Management**: Serial port initialization and resource allocation
3. **Task Orchestration**: Async procedure scheduling and monitoring
4. **Real-time Control**: Sensor monitoring and user interaction handling

**Async Task Types**:

**Procedure Execution**:
```python
wait_and_execute_procedure(procedure, component, experiment, dry_run, strict)
```
- Waits for precise start time
- Updates component state via `_update()`
- Logs execution events
- Error handling based on strict mode

**Sensor Monitoring**:
```python
_monitor(sensor, experiment, dry_run, strict)
```
- Continuous data collection
- Rate-controlled sampling
- Real-time data streaming
- Automatic data persistence

**User Controls**:
```python
check_if_cancelled(experiment)
pause_handler(experiment, end_time, components) 
end_loop(experiment)
```

**Context Management**:
- `ExitStack` for automatic resource cleanup
- Component context managers for hardware initialization
- Graceful shutdown on errors or cancellation

**Timing Precision**:
- Millisecond-level procedure timing
- Dry run speed scaling (1x, 2x, 10x, etc.)
- Pause/resume with time tracking
- Async sleep for non-blocking delays

**Error Handling**:
- `strict=True`: Stop on first error
- `strict=False`: Log errors and continue
- Comprehensive error logging and tracebacks
- Component validation before execution

---

## Integration Patterns

### Component Lifecycle

```python
# 1. Apparatus Definition
A = mw.Apparatus("FlowSetup")
A.add(pump, vessel, tube)

# 2. Protocol Creation  
P = mw.Protocol(A)
P.add(pump, start="0s", duration="10min", rate="5 mL/min")

# 3. Execution
experiment = P.execute(dry_run=False)
```

### Real-Time Data Access

```python
# Access sensor data during execution
for sensor_name, datapoints in experiment.data.items():
    latest_value = datapoints[-1].data
    timestamp = datapoints[-1].timestamp
```

### Visualization Integration

```python
# Apparatus network diagram
A.visualize(graph_attr={"splines": "ortho"})

# Protocol timeline
P.visualize(width=800, legend=True)

# Live experiment monitoring (automatic in Jupyter)
experiment  # Shows real-time plots
```

## Advanced Features

### Valve Logic Resolution
- Automatic mapping from component references to port numbers
- Support for component names in valve settings
- Bidirectional mapping validation

### Unit System Integration
- Pint quantities for all dimensional parameters
- Automatic unit conversion and validation
- Dimensional analysis for parameter checking

### Async Architecture Benefits
- Non-blocking sensor monitoring
- Concurrent component control
- Real-time user interaction
- Scalable to many components

### Data Persistence
- JSONL format for streaming data
- Compressed log files for long experiments
- Automatic backup and recovery
- Integration with external analysis tools

## Error Handling Patterns

### Component Validation
- Pre-execution component state validation
- Runtime parameter checking
- Hardware connection verification

### Timing Conflicts
- Overlapping procedure detection
- Automatic stop time inference
- Resource conflict warnings

### Execution Robustness
- Graceful degradation on component failures
- Partial execution recovery
- Comprehensive error logging

## Performance Considerations

### Memory Management
- Streaming data collection for long experiments
- Periodic data flushing to disk
- Memory-efficient sensor monitoring

### Timing Precision
- Sub-second procedure timing accuracy
- Minimal execution overhead
- Optimized async task scheduling

### Scalability
- Support for dozens of concurrent components
- Efficient NetworkX graph operations
- Lazy evaluation of protocol compilation

This core system provides a robust foundation for complex flow chemistry automation while maintaining flexibility for diverse experimental requirements.