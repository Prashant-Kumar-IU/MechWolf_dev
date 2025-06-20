"""
Apparatus Visualizer - Creates visual diagrams of apparatus networks

This module provides visualization capabilities for apparatus connections
using matplotlib and networkx for network diagrams.
"""
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from IPython.display import display, HTML
import ipywidgets as widgets


class ApparatusVisualizer:
    """Creates visual representations of apparatus networks"""
    
    def __init__(self):
        # Color scheme for different component types
        self.component_colors = {
            'Vessel': '#9c27b0',           # Purple
            'Pump': '#4caf50',             # Green  
            'Valve': '#ff9800',            # Orange
            'Mixer': '#2196f3',            # Blue
            'TMixer': '#2196f3',           # Blue
            'CrossMixer': '#2196f3',       # Blue
            'YMixer': '#2196f3',           # Blue
            'Sensor': '#607d8b',           # Blue Grey
            'TempControl': '#f44336',      # Red
            'Tube': '#795548',             # Brown
        }
        
        # Shape mapping for components
        self.component_shapes = {
            'Vessel': 'o',      # Circle
            'Pump': 's',        # Square
            'Valve': 'D',       # Diamond
            'Mixer': '^',       # Triangle
            'TMixer': '^',      # Triangle
            'CrossMixer': 'P',  # Plus
            'YMixer': 'v',      # Triangle down
            'Sensor': 'h',      # Hexagon
            'TempControl': '*', # Star
        }
        
        # Size mapping for components
        self.component_sizes = {
            'Vessel': 800,
            'Pump': 600,
            'Valve': 600,
            'Mixer': 500,
            'TMixer': 500,
            'CrossMixer': 500,
            'YMixer': 500,
            'Sensor': 400,
            'TempControl': 500,
        }
    
    def create_network_diagram(self, components: Dict[str, Dict[str, Any]], 
                             connections: List[Dict[str, Any]], 
                             figsize: Tuple[int, int] = (12, 8),
                             title: str = "Apparatus Network Diagram") -> None:
        """
        Create a network diagram of the apparatus
        
        Args:
            components: Dictionary of component configurations
            connections: List of connection configurations
            figsize: Figure size (width, height)
            title: Diagram title
        """
        if not connections:
            self._show_no_connections_message()
            return
        
        # Create NetworkX graph
        G = self._build_networkx_graph(components, connections)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate layout
        pos = self._generate_layout(G, components)
        
        # Draw components (nodes)
        self._draw_components(G, pos, ax, components)
        
        # Draw connections (edges)
        self._draw_connections(G, pos, ax, connections)
        
        # Add labels
        self._add_labels(G, pos, ax)
        
        # Customize plot
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # Add legend
        self._add_legend(ax, components)
        
        # Add connection summary
        self._add_connection_summary(ax, connections)
        
        plt.tight_layout()
        plt.show()
    
    def create_interactive_diagram(self, components: Dict[str, Dict[str, Any]], 
                                 connections: List[Dict[str, Any]]) -> widgets.Widget:
        """Create an interactive diagram widget"""
        
        if not connections:
            return widgets.HTML("<p>No connections to visualize</p>")
        
        # Create static diagram first
        self.create_network_diagram(components, connections)
        
        # Create interactive controls
        controls = self._create_interactive_controls(components, connections)
        
        return controls
    
    def create_flow_diagram(self, components: Dict[str, Dict[str, Any]], 
                          connections: List[Dict[str, Any]]) -> None:
        """Create a flow-oriented diagram showing process flow"""
        
        if not connections:
            self._show_no_connections_message()
            return
        
        # Analyze flow paths
        flow_paths = self._analyze_flow_paths(components, connections)
        
        # Create flow diagram
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Draw flow paths
        self._draw_flow_paths(ax, flow_paths, components)
        
        ax.set_title("Process Flow Diagram", fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    def _build_networkx_graph(self, components: Dict[str, Dict[str, Any]], 
                            connections: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build NetworkX directed graph from connections"""
        G = nx.DiGraph()
        
        # Add nodes (components) with attributes
        for comp_id, comp_data in components.items():
            comp_name = comp_data.get('name', comp_id)
            G.add_node(comp_name, **comp_data)
        
        # Add edges (connections) with tube information
        for conn in connections:
            from_comp = conn['from']
            to_comp = conn['to']
            tube = conn['tube']
            
            G.add_edge(from_comp, to_comp, tube=tube, **conn)
        
        return G
    
    def _generate_layout(self, G: nx.DiGraph, components: Dict[str, Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
        """Generate optimal layout for the network"""
        
        # Try different layout algorithms based on network characteristics
        num_nodes = len(G.nodes())
        
        if num_nodes <= 5:
            # Small networks: use circular layout
            pos = nx.circular_layout(G, scale=2)
        elif num_nodes <= 10:
            # Medium networks: use spring layout with more iterations
            pos = nx.spring_layout(G, k=3, iterations=100, scale=2)
        else:
            # Large networks: use hierarchical layout
            pos = self._hierarchical_layout(G, components)
        
        return pos
    
    def _hierarchical_layout(self, G: nx.DiGraph, components: Dict[str, Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical layout based on component roles"""
        
        # Categorize components by role
        sources = []  # Vessels with no inputs
        sinks = []    # Vessels with no outputs  
        active = []   # Pumps, valves, sensors
        mixers = []   # Mixers
        
        for node in G.nodes():
            comp_data = G.nodes[node]
            comp_type = comp_data.get('type', '')
            
            # Count inputs and outputs
            inputs = len(list(G.predecessors(node)))
            outputs = len(list(G.successors(node)))
            
            if comp_type == 'Vessel':
                if inputs == 0:
                    sources.append(node)
                elif outputs == 0:
                    sinks.append(node)
                else:
                    active.append(node)  # Intermediate vessel
            elif 'Mixer' in comp_type:
                mixers.append(node)
            else:
                active.append(node)
        
        # Create hierarchical positions
        pos = {}
        
        # Layer 1: Sources (left side)
        for i, node in enumerate(sources):
            pos[node] = (0, i - len(sources)/2)
        
        # Layer 2: Active components (middle-left)
        for i, node in enumerate(active):
            pos[node] = (2, i - len(active)/2)
        
        # Layer 3: Mixers (middle-right)
        for i, node in enumerate(mixers):
            pos[node] = (4, i - len(mixers)/2)
        
        # Layer 4: Sinks (right side)
        for i, node in enumerate(sinks):
            pos[node] = (6, i - len(sinks)/2)
        
        # Fine-tune positions to avoid overlaps
        pos = self._adjust_positions(pos)
        
        return pos
    
    def _adjust_positions(self, pos: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Adjust positions to avoid overlaps"""
        
        # Add small random offsets to avoid exact overlaps
        adjusted_pos = {}
        for node, (x, y) in pos.items():
            # Add small random offset
            offset_x = np.random.uniform(-0.1, 0.1)
            offset_y = np.random.uniform(-0.1, 0.1)
            adjusted_pos[node] = (x + offset_x, y + offset_y)
        
        return adjusted_pos
    
    def _draw_components(self, G: nx.DiGraph, pos: Dict[str, Tuple[float, float]], 
                        ax, components: Dict[str, Dict[str, Any]]) -> None:
        """Draw component nodes"""
        
        # Group nodes by type for consistent drawing
        nodes_by_type = {}
        for node in G.nodes():
            comp_data = G.nodes[node]
            comp_type = comp_data.get('type', 'Unknown')
            
            if comp_type not in nodes_by_type:
                nodes_by_type[comp_type] = []
            nodes_by_type[comp_type].append(node)
        
        # Draw each component type
        for comp_type, nodes in nodes_by_type.items():
            node_color = self.component_colors.get(comp_type, '#cccccc')
            node_shape = self.component_shapes.get(comp_type, 'o')
            node_size = self.component_sizes.get(comp_type, 500)
            
            # Get positions for these nodes
            node_positions = {node: pos[node] for node in nodes if node in pos}
            
            if node_positions:
                nx.draw_networkx_nodes(
                    G, node_positions, 
                    nodelist=nodes,
                    node_color=node_color,
                    node_shape=node_shape,
                    node_size=node_size,
                    alpha=0.8,
                    ax=ax
                )
    
    def _draw_connections(self, G: nx.DiGraph, pos: Dict[str, Tuple[float, float]], 
                         ax, connections: List[Dict[str, Any]]) -> None:
        """Draw connection edges"""
        
        # Draw edges with different styles based on tube type
        edge_colors = []
        edge_styles = []
        edge_widths = []
        
        for edge in G.edges():
            edge_data = G.edges[edge]
            tube = edge_data.get('tube', '')
            
            # Get tube data to determine style
            tube_info = self._get_tube_info(tube, connections)
            
            if 'fat' in tube.lower():
                edge_colors.append('#4CAF50')  # Green for fat tubes
                edge_widths.append(3)
                edge_styles.append('-')
            elif 'thin' in tube.lower():
                edge_colors.append('#2196F3')  # Blue for thin tubes
                edge_widths.append(2)
                edge_styles.append('-')
            else:
                edge_colors.append('#666666')  # Gray for custom tubes
                edge_widths.append(2)
                edge_styles.append('-')
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            edge_color=edge_colors,
            width=edge_widths,
            alpha=0.7,
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            ax=ax
        )
    
    def _add_labels(self, G: nx.DiGraph, pos: Dict[str, Tuple[float, float]], ax) -> None:
        """Add component labels"""
        
        # Create labels with component names
        labels = {node: node for node in G.nodes()}
        
        nx.draw_networkx_labels(
            G, pos, labels,
            font_size=10,
            font_weight='bold',
            font_color='white',
            ax=ax
        )
    
    def _add_legend(self, ax, components: Dict[str, Dict[str, Any]]) -> None:
        """Add legend showing component types"""
        
        # Get unique component types
        unique_types = set()
        for comp_data in components.values():
            unique_types.add(comp_data.get('type', 'Unknown'))
        
        # Create legend elements
        legend_elements = []
        for comp_type in sorted(unique_types):
            color = self.component_colors.get(comp_type, '#cccccc')
            marker = self.component_shapes.get(comp_type, 'o')
            
            legend_elements.append(
                plt.Line2D([0], [0], marker=marker, color='w', 
                          markerfacecolor=color, markersize=10, label=comp_type)
            )
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    def _add_connection_summary(self, ax, connections: List[Dict[str, Any]]) -> None:
        """Add connection summary text"""
        
        summary_text = f"Total Connections: {len(connections)}"
        
        # Count tube types
        tube_counts = {}
        for conn in connections:
            tube = conn.get('tube', 'Unknown')
            tube_type = self._classify_tube_type(tube)
            tube_counts[tube_type] = tube_counts.get(tube_type, 0) + 1
        
        if tube_counts:
            summary_text += "\nTube Types:"
            for tube_type, count in tube_counts.items():
                summary_text += f"\n  {tube_type}: {count}"
        
        # Add text box
        ax.text(1.02, 0.5, summary_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    def _get_tube_info(self, tube_name: str, connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get tube information from connections"""
        for conn in connections:
            if conn.get('tube') == tube_name:
                return conn
        return {}
    
    def _classify_tube_type(self, tube_name: str) -> str:
        """Classify tube type from name"""
        tube_lower = tube_name.lower()
        
        if 'fat' in tube_lower:
            return 'Fat Tube'
        elif 'thinner' in tube_lower:
            return 'Thinner Tube'
        elif 'thin' in tube_lower:
            return 'Thin Tube'
        else:
            return 'Custom Tube'
    
    def _analyze_flow_paths(self, components: Dict[str, Dict[str, Any]], 
                          connections: List[Dict[str, Any]]) -> List[List[str]]:
        """Analyze flow paths through the apparatus"""
        
        # Build graph
        G = self._build_networkx_graph(components, connections)
        
        # Find source nodes (no predecessors)
        sources = [node for node in G.nodes() if G.in_degree(node) == 0]
        
        # Find sink nodes (no successors)
        sinks = [node for node in G.nodes() if G.out_degree(node) == 0]
        
        # Find all paths from sources to sinks
        paths = []
        for source in sources:
            for sink in sinks:
                try:
                    all_paths = list(nx.all_simple_paths(G, source, sink))
                    paths.extend(all_paths)
                except nx.NetworkXNoPath:
                    continue
        
        return paths
    
    def _draw_flow_paths(self, ax, flow_paths: List[List[str]], 
                        components: Dict[str, Dict[str, Any]]) -> None:
        """Draw flow paths diagram"""
        
        if not flow_paths:
            ax.text(0.5, 0.5, "No complete flow paths found", 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            return
        
        # Create a simplified layout for flow paths
        y_spacing = 1.0 / (len(flow_paths) + 1)
        
        for i, path in enumerate(flow_paths):
            y_pos = 1.0 - (i + 1) * y_spacing
            x_spacing = 1.0 / (len(path) + 1)
            
            # Draw path components
            for j, component in enumerate(path):
                x_pos = (j + 1) * x_spacing
                
                # Get component data
                comp_data = self._get_component_data_by_name(component, components)
                comp_type = comp_data.get('type', 'Unknown') if comp_data else 'Unknown'
                
                # Draw component
                color = self.component_colors.get(comp_type, '#cccccc')
                ax.scatter(x_pos, y_pos, s=300, c=color, alpha=0.8)
                ax.text(x_pos, y_pos, component, ha='center', va='center', 
                       fontsize=8, fontweight='bold', color='white')
                
                # Draw arrow to next component
                if j < len(path) - 1:
                    next_x = (j + 2) * x_spacing
                    ax.annotate('', xy=(next_x - 0.05, y_pos), xytext=(x_pos + 0.05, y_pos),
                               arrowprops=dict(arrowstyle='->', lw=2, color='black'))
            
            # Label path
            ax.text(0.02, y_pos, f"Path {i+1}:", ha='left', va='center', 
                   fontweight='bold', fontsize=10)
    
    def _get_component_data_by_name(self, name: str, components: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get component data by name"""
        for comp_data in components.values():
            if comp_data.get('name') == name:
                return comp_data
        return None
    
    def _show_no_connections_message(self) -> None:
        """Show message when no connections are available"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No connections to visualize\nAdd connections in the Apparatus Builder", 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=16, bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray"))
        ax.axis('off')
        ax.set_title("Apparatus Visualization", fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def _create_interactive_controls(self, components: Dict[str, Dict[str, Any]], 
                                   connections: List[Dict[str, Any]]) -> widgets.Widget:
        """Create interactive controls for diagram exploration"""
        
        # Layout selector
        layout_selector = widgets.Dropdown(
            options=[
                ('Network Layout', 'network'),
                ('Flow Diagram', 'flow'),
                ('Hierarchical Layout', 'hierarchical')
            ],
            value='network',
            description='Layout:'
        )
        
        # Component filter
        comp_types = list(set(comp['type'] for comp in components.values()))
        component_filter = widgets.SelectMultiple(
            options=comp_types,
            value=comp_types,
            description='Show Types:'
        )
        
        # Update button
        update_btn = widgets.Button(
            description='Update Diagram',
            button_style='primary'
        )
        
        def update_diagram(b):
            if layout_selector.value == 'network':
                self.create_network_diagram(components, connections)
            elif layout_selector.value == 'flow':
                self.create_flow_diagram(components, connections)
        
        update_btn.on_click(update_diagram)
        
        # Create control panel
        controls = widgets.VBox([
            widgets.HTML("<h4>Visualization Controls</h4>"),
            layout_selector,
            component_filter,
            update_btn
        ])
        
        return controls