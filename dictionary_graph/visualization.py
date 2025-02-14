"""Module for graph visualization."""

from .graph import DictionaryGraph
from config import (
    NODE_COLORS, NODE_SIZES
)

class GraphVisualizer:
    """Class to handle graph visualization."""
    
    def __init__(self):
        self.graph_handler = DictionaryGraph()
        self.graph_handler.load_graph()
    
    def get_relevant_neighbors(self, node, max_neighbors=5, directions=None):
        """Get relevant neighbors for a node."""
        if directions is None:
            directions = {'outgoing': True, 'incoming': True}
        
        if not self.graph_handler.graph or node not in self.graph_handler.graph:
            return []
            
        neighbors = []
        if directions['outgoing']:
            neighbors.extend(list(self.graph_handler.graph.successors(node)))
        if directions['incoming']:
            neighbors.extend(list(self.graph_handler.graph.predecessors(node)))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_neighbors = [n for n in neighbors if not (n in seen or seen.add(n))]
        return unique_neighbors[:max_neighbors]
    
    def create_visualization(self, word, max_nodes=50, depth=2, neighbor_limit=5,
                           progress_callback=None, directions=None):
        """Create graph data for visualization."""
        if not self.graph_handler.graph:
            return None, "Graph not loaded"
        
        if word not in self.graph_handler.graph:
            return None, "Word not found in graph"
        
        def update_progress(progress, message):
            """Update progress if callback is provided."""
            if progress_callback:
                progress_callback({"progress": progress, "message": message})
        
        update_progress(5, "Loading graph data...")
        
        # Collect nodes starting from the target word
        nodes_to_show = {word}
        current_layer = {word}
        current_depth = 1
        
        # Calculate progress steps
        total_steps = depth + 2  # depth + nodes + edges
        step_size = 60 / total_steps  # Reserve 40% for edge processing
        current_progress = 5
        
        while current_depth <= depth and len(nodes_to_show) < max_nodes:
            next_layer = set()
            for node in current_layer:
                if len(nodes_to_show) < max_nodes:
                    relevant_neighbors = self.get_relevant_neighbors(
                        node, neighbor_limit, directions
                    )
                    next_layer.update(relevant_neighbors)
                    nodes_to_show.update(
                        relevant_neighbors[:max(1, (max_nodes - len(nodes_to_show)))]
                    )
            current_layer = next_layer
            current_depth += 1
            current_progress += step_size
            update_progress(
                int(current_progress),
                f"Processing layer {current_depth} of {depth}..."
            )
        
        # Create subgraph
        subgraph = self.graph_handler.graph.subgraph(nodes_to_show)
        current_progress += step_size
        update_progress(int(current_progress), "Creating network data...")
        
        # Prepare visualization data
        nodes = []
        edges = []
        
        # Add nodes with custom properties
        node_count = len(subgraph.nodes())
        for i, node in enumerate(subgraph.nodes()):
            size = NODE_SIZES["default"]
            color = NODE_COLORS["default"]
            
            if node == word:
                size = NODE_SIZES["target"]
                color = NODE_COLORS["target"]
            elif ((directions.get('outgoing', True) and
                  node in self.graph_handler.graph.successors(word)) or
                  (directions.get('incoming', True) and
                   node in self.graph_handler.graph.predecessors(word))):
                size = NODE_SIZES["neighbor"]
                color = NODE_COLORS["neighbor"]
            
            nodes.append({
                "id": node,
                "label": node,
                "size": size,
                "color": color,
                "title": f"Word: {node}"
            })
            
            if i % max(1, node_count // 10) == 0:
                current_progress = 65 + (i / node_count * 20)
                update_progress(
                    int(current_progress),
                    f"Processing nodes ({i}/{node_count})..."
                )
        
        # Add edges
        edge_count = len(subgraph.edges())
        for i, edge in enumerate(subgraph.edges()):
            edges.append({
                "from": edge[0],
                "to": edge[1],
                "arrows": "to",
                "smooth": {"type": "curvedCW", "roundness": 0.2}
            })
            
            if i % max(1, edge_count // 10) == 0:
                current_progress = 85 + (i / edge_count * 10)
                update_progress(
                    int(current_progress),
                    f"Processing edges ({i}/{edge_count})..."
                )
        
        update_progress(95, "Finalizing data...")
        
        # Return the graph data
        graph_data = {
            "nodes": nodes,
            "edges": edges,
            "options": {
                "physics": {
                    "forceAtlas2Based": {
                        "gravitationalConstant": -50,
                        "centralGravity": 0.01,
                        "springLength": 100,
                        "springConstant": 0.08
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "solver": "forceAtlas2Based",
                    "timestep": 0.35
                },
                "interaction": {
                    "navigationButtons": True,
                    "keyboard": True
                }
            }
        }
        
        update_progress(100, "Visualization data ready!")
        return graph_data, None

def main():
    """Test visualization creation."""
    visualizer = GraphVisualizer()
    filename, error = visualizer.create_visualization(
        "test",
        progress_callback=lambda x: print(f"{x['progress']}%: {x['message']}")
    )
    if error:
        print(f"Error: {error}")
    else:
        print(f"Visualization saved as {filename}")

if __name__ == '__main__':
    main()