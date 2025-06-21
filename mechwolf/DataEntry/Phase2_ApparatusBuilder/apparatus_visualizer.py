"""
Apparatus Visualizer

Creates visual representations of apparatus configurations including
network diagrams and flow path visualizations.
"""

import ipywidgets as widgets
from IPython.display import HTML, display
from typing import Dict, Any, List, Optional, Tuple
import json

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import networkx as nx
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ApparatusVisualizer:
    """Visual representation generator for apparatus configurations"""
    
    def __init__(self):
        """Initialize visualizer"""
        
        # Component symbols and colors
        self.component_symbols = {
            'Vessel': '◯',
            'HarvardSyringePump': '⚡',
            'VarianPump': '⚡',
            'FreeStepPump': '⚡',
            'TMixer': '⊤',
            'CrossMixer': '✚',
            'YMixer': 'Ψ',
            'Tube': '─',
            'Reactor': '⬢',
            'Sensor': '◈'
        }
        
        self.component_colors = {
            'Vessel': '#4CAF50',
            'HarvardSyringePump': '#2196F3',
            'VarianPump': '#2196F3', 
            'FreeStepPump': '#2196F3',
            'TMixer': '#FF9800',
            'CrossMixer': '#FF9800',
            'YMixer': '#FF9800',
            'Tube': '#9E9E9E',
            'Reactor': '#9C27B0',
            'Sensor': '#F44336'
        }
        
    def create_network_diagram(self, apparatus_data: Dict[str, Any]) -> Optional[widgets.Widget]:
        """
        Create network diagram of apparatus
        
        Args:
            apparatus_data: Apparatus configuration data
            
        Returns:
            Widget containing visualization or None if not possible
        """
        try:
            if MATPLOTLIB_AVAILABLE:
                return self._create_matplotlib_diagram(apparatus_data)
            else:
                return self._create_html_diagram(apparatus_data)
                
        except Exception as e:
            print(f"Error creating network diagram: {e}")
            return None
    
    def _create_matplotlib_diagram(self, apparatus_data: Dict[str, Any]) -> widgets.Widget:
        """Create diagram using matplotlib"""
        
        output = widgets.Output()
        
        with output:
            components = apparatus_data.get('components', {})
            connections = apparatus_data.get('connections', [])
            
            # Get all components
            all_components = (components.get('active', []) + 
                            components.get('passive', []))
            
            if not all_components:
                print("No components to visualize")
                return output
            
            # Create network graph
            G = nx.DiGraph()
            
            # Add nodes
            for component in all_components:
                name = component.get('name', 'Unknown')
                comp_type = component.get('type', 'Unknown')
                G.add_node(name, type=comp_type)
            
            # Add edges
            for connection in connections:
                from_comp = connection.get('from')
                to_comp = connection.get('to')
                tube = connection.get('tube')
                
                if tube:
                    # Add tube as intermediate node
                    G.add_edge(from_comp, tube)
                    G.add_edge(tube, to_comp)
                else:
                    G.add_edge(from_comp, to_comp)
            
            # Create layout
            try:
                pos = nx.spring_layout(G, k=3, iterations=50)
            except:
                pos = nx.random_layout(G)
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            ax.set_title("Apparatus Network Diagram", fontsize=16, fontweight='bold')
            
            # Draw nodes
            for node, (x, y) in pos.items():
                node_data = G.nodes[node]
                node_type = node_data.get('type', 'Unknown')
                
                color = self.component_colors.get(node_type, '#CCCCCC')
                symbol = self.component_symbols.get(node_type, '?')
                
                # Draw node circle
                circle = patches.Circle((x, y), 0.1, color=color, alpha=0.7)
                ax.add_patch(circle)
                
                # Add symbol
                ax.text(x, y, symbol, ha='center', va='center', 
                       fontsize=14, fontweight='bold', color='white')
                
                # Add label below
                ax.text(x, y-0.15, node, ha='center', va='top', 
                       fontsize=8, fontweight='bold')
            
            # Draw edges
            for edge in G.edges():
                start_pos = pos[edge[0]]
                end_pos = pos[edge[1]]
                
                ax.annotate('', xy=end_pos, xytext=start_pos,
                           arrowprops=dict(arrowstyle='->', lw=2, color='#666666'))
            
            # Create legend
            legend_elements = []
            unique_types = set(G.nodes[node].get('type', 'Unknown') for node in G.nodes())
            
            for comp_type in unique_types:
                color = self.component_colors.get(comp_type, '#CCCCCC')
                symbol = self.component_symbols.get(comp_type, '?')
                legend_elements.append(
                    patches.Patch(color=color, label=f'{symbol} {comp_type}')
                )
            
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
            
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_aspect('equal')
            ax.axis('off')
            
            plt.tight_layout()
            plt.show()
        
        return output
    
    def _create_html_diagram(self, apparatus_data: Dict[str, Any]) -> widgets.Widget:
        """Create diagram using HTML/CSS (fallback)"""
        
        components = apparatus_data.get('components', {})
        connections = apparatus_data.get('connections', [])
        
        # Get all components
        all_components = (components.get('active', []) + 
                        components.get('passive', []))
        
        if not all_components:
            return widgets.HTML("<p>No components to visualize</p>")
        
        # Build HTML representation
        html_content = """
        <div style='border: 1px solid #ccc; padding: 20px; border-radius: 8px; background: #f9f9f9;'>
            <h3 style='text-align: center; margin-top: 0;'>Apparatus Network Diagram</h3>
        """
        
        # Component grid layout
        html_content += """
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                    gap: 15px; margin: 20px 0;'>
        """
        
        for component in all_components:
            name = component.get('name', 'Unknown')
            comp_type = component.get('type', 'Unknown')
            color = self.component_colors.get(comp_type, '#CCCCCC')
            symbol = self.component_symbols.get(comp_type, '?')
            
            html_content += f"""
            <div style='background: {color}; padding: 15px; border-radius: 8px; 
                        text-align: center; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <div style='font-size: 24px; margin-bottom: 5px;'>{symbol}</div>
                <div style='font-weight: bold; font-size: 12px;'>{name}</div>
                <div style='font-size: 10px; opacity: 0.8;'>{comp_type}</div>
            </div>
            """
        
        html_content += "</div>"
        
        # Connection list
        if connections:
            html_content += "<h4>Flow Connections:</h4>"
            html_content += "<div style='background: white; padding: 15px; border-radius: 5px;'>"
            
            for i, connection in enumerate(connections):
                from_comp = connection.get('from', 'Unknown')
                to_comp = connection.get('to', 'Unknown')
                tube = connection.get('tube')
                
                if tube:
                    connection_text = f"{from_comp} → {tube} → {to_comp}"
                else:
                    connection_text = f"{from_comp} → {to_comp}"
                
                html_content += f"""
                <div style='margin: 5px 0; padding: 8px; background: #e3f2fd; 
                           border-radius: 4px; border-left: 4px solid #2196f3;'>
                    {i+1}. {connection_text}
                </div>
                """
            
            html_content += "</div>"
        
        # Legend
        html_content += "<h4>Component Legend:</h4>"
        html_content += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
        
        unique_types = set(comp.get('type', 'Unknown') for comp in all_components)
        for comp_type in unique_types:
            color = self.component_colors.get(comp_type, '#CCCCCC')
            symbol = self.component_symbols.get(comp_type, '?')
            
            html_content += f"""
            <div style='display: flex; align-items: center; gap: 5px; 
                        background: white; padding: 5px 10px; border-radius: 4px; 
                        border: 1px solid #ddd;'>
                <span style='color: {color}; font-size: 16px; font-weight: bold;'>{symbol}</span>
                <span style='font-size: 12px;'>{comp_type}</span>
            </div>
            """
        
        html_content += "</div></div>"
        
        return widgets.HTML(html_content)
    
    def create_flow_path_analysis(self, apparatus_data: Dict[str, Any]) -> widgets.Widget:
        """Create flow path analysis visualization"""
        
        components = apparatus_data.get('components', {})
        connections = apparatus_data.get('connections', [])
        
        # Build connection graph
        graph = {}
        reverse_graph = {}
        
        for connection in connections:
            from_comp = connection.get('from')
            to_comp = connection.get('to')
            tube = connection.get('tube')
            
            # Build forward graph
            if from_comp not in graph:
                graph[from_comp] = []
            
            if tube:
                graph[from_comp].append(tube)
                if tube not in graph:
                    graph[tube] = []
                graph[tube].append(to_comp)
            else:
                graph[from_comp].append(to_comp)
            
            # Build reverse graph for finding sources
            final_dest = tube if tube else to_comp
            if final_dest not in reverse_graph:
                reverse_graph[final_dest] = []
            reverse_graph[final_dest].append(from_comp)
        
        # Find sources and sinks
        all_components = (components.get('active', []) + 
                        components.get('passive', []))
        all_names = [comp.get('name') for comp in all_components]
        
        sources = [name for name in all_names if name not in reverse_graph]
        sinks = [name for name in all_names if name not in graph]
        
        # Generate HTML analysis
        html_content = """
        <div style='border: 1px solid #ccc; padding: 20px; border-radius: 8px; background: #f9f9f9;'>
            <h3 style='margin-top: 0;'>Flow Path Analysis</h3>
        """
        
        # Sources section
        html_content += "<h4>🔵 Source Components (No Inputs):</h4>"
        if sources:
            for source in sources:
                html_content += f"<div style='background: #e8f5e8; padding: 8px; margin: 4px 0; border-radius: 4px;'>• {source}</div>"
        else:
            html_content += "<div style='color: #ff9800;'>⚠️ No sources found - may indicate cycles</div>"
        
        # Sinks section
        html_content += "<h4>🔴 Sink Components (No Outputs):</h4>"
        if sinks:
            for sink in sinks:
                html_content += f"<div style='background: #fff3e0; padding: 8px; margin: 4px 0; border-radius: 4px;'>• {sink}</div>"
        else:
            html_content += "<div style='color: #ff9800;'>⚠️ No sinks found - products may not be collected</div>"
        
        # Flow paths section
        html_content += "<h4>🔄 Flow Paths:</h4>"
        
        for source in sources:
            paths = self._find_all_paths(graph, source, sinks)
            
            if paths:
                html_content += f"<div style='margin: 10px 0;'><strong>From {source}:</strong></div>"
                for path in paths[:5]:  # Limit to 5 paths
                    path_str = " → ".join(path)
                    html_content += f"<div style='background: #e3f2fd; padding: 8px; margin: 4px 0; border-radius: 4px; margin-left: 20px;'>{path_str}</div>"
                
                if len(paths) > 5:
                    html_content += f"<div style='margin-left: 20px; color: #666;'>... and {len(paths) - 5} more paths</div>"
        
        html_content += "</div>"
        
        return widgets.HTML(html_content)
    
    def _find_all_paths(self, graph: Dict[str, List[str]], start: str, 
                       targets: List[str], path: List[str] = None, 
                       visited: set = None, max_depth: int = 10) -> List[List[str]]:
        """Find all paths from start to any target"""
        
        if path is None:
            path = []
        if visited is None:
            visited = set()
        
        path = path + [start]
        visited = visited | {start}
        
        # Check if we've reached a target
        if start in targets:
            return [path]
        
        # Prevent infinite loops
        if len(path) > max_depth:
            return []
        
        paths = []
        
        # Explore neighbors
        for neighbor in graph.get(start, []):
            if neighbor not in visited:
                new_paths = self._find_all_paths(graph, neighbor, targets, path, visited, max_depth)
                paths.extend(new_paths)
        
        return paths
    
    def create_summary_widget(self, apparatus_data: Dict[str, Any]) -> widgets.Widget:
        """Create apparatus summary widget"""
        
        components = apparatus_data.get('components', {})
        connections = apparatus_data.get('connections', [])
        
        active_components = components.get('active', [])
        passive_components = components.get('passive', [])
        
        # Count component types
        component_counts = {}
        for component in active_components + passive_components:
            comp_type = component.get('type', 'Unknown')
            component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
        
        # Generate summary HTML
        html_content = """
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; 
                    background: #f5f5f5; border-radius: 8px;'>
        """
        
        # Left column: Component summary
        html_content += """
        <div style='background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h4 style='margin-top: 0; color: #1976d2;'>📊 Component Summary</h4>
        """
        
        html_content += f"<div><strong>Total Components:</strong> {len(active_components) + len(passive_components)}</div>"
        html_content += f"<div><strong>Active Components:</strong> {len(active_components)}</div>"
        html_content += f"<div><strong>Passive Components:</strong> {len(passive_components)}</div>"
        html_content += "<hr>"
        
        for comp_type, count in sorted(component_counts.items()):
            symbol = self.component_symbols.get(comp_type, '?')
            color = self.component_colors.get(comp_type, '#666')
            html_content += f"""
            <div style='display: flex; align-items: center; margin: 5px 0;'>
                <span style='color: {color}; font-size: 16px; margin-right: 8px;'>{symbol}</span>
                <span>{comp_type}: {count}</span>
            </div>
            """
        
        html_content += "</div>"
        
        # Right column: Connection summary
        html_content += """
        <div style='background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h4 style='margin-top: 0; color: #1976d2;'>🔗 Connection Summary</h4>
        """
        
        html_content += f"<div><strong>Total Connections:</strong> {len(connections)}</div>"
        
        # Connection types
        direct_connections = sum(1 for conn in connections if not conn.get('tube'))
        tube_connections = sum(1 for conn in connections if conn.get('tube'))
        
        html_content += f"<div><strong>Direct Connections:</strong> {direct_connections}</div>"
        html_content += f"<div><strong>Via Tube:</strong> {tube_connections}</div>"
        html_content += "<hr>"
        
        # Most connected components
        connection_counts = {}
        for connection in connections:
            from_comp = connection.get('from')
            to_comp = connection.get('to')
            
            connection_counts[from_comp] = connection_counts.get(from_comp, 0) + 1
            connection_counts[to_comp] = connection_counts.get(to_comp, 0) + 1
        
        if connection_counts:
            html_content += "<div><strong>Most Connected:</strong></div>"
            sorted_counts = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)
            for comp_name, count in sorted_counts[:3]:
                html_content += f"<div style='margin-left: 15px;'>• {comp_name} ({count} connections)</div>"
        
        html_content += "</div></div>"
        
        return widgets.HTML(html_content)
    
    def export_diagram(self, apparatus_data: Dict[str, Any], format: str = 'json') -> str:
        """Export diagram data in specified format"""
        
        if format == 'json':
            return json.dumps(apparatus_data, indent=2)
        
        elif format == 'dot':
            # Export as Graphviz DOT format
            components = apparatus_data.get('components', {})
            connections = apparatus_data.get('connections', [])
            
            all_components = (components.get('active', []) + 
                            components.get('passive', []))
            
            dot_content = ["digraph apparatus {"]
            dot_content.append("  rankdir=LR;")
            dot_content.append("  node [shape=box];")
            
            # Add nodes
            for component in all_components:
                name = component.get('name', 'Unknown')
                comp_type = component.get('type', 'Unknown')
                dot_content.append(f'  "{name}" [label="{name}\\n({comp_type})"];')
            
            # Add edges
            for connection in connections:
                from_comp = connection.get('from')
                to_comp = connection.get('to')
                tube = connection.get('tube')
                
                if tube:
                    dot_content.append(f'  "{from_comp}" -> "{tube}";')
                    dot_content.append(f'  "{tube}" -> "{to_comp}";')
                else:
                    dot_content.append(f'  "{from_comp}" -> "{to_comp}";')
            
            dot_content.append("}")
            return "\n".join(dot_content)
        
        else:
            return f"# Export format '{format}' not supported"