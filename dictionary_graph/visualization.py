"""Module for graph visualization."""

from .graph import DictionaryGraph
from config import (
    NODE_COLORS, NODE_SIZES
)

class GraphVisualizer:
    """Class to handle graph visualization."""
    
    def __init__(self):
        self.graph_handler = DictionaryGraph()
    
    def get_relevant_neighbors(self, graph, node, max_neighbors=5, directions=None):
        """Get relevant neighbors for a node."""
        if directions is None:
            directions = {'outgoing': True, 'incoming': True}
        
        if not graph or node not in graph:
            return []
            
        neighbors = []
        if directions['outgoing']:
            neighbors.extend(list(graph.successors(node)))
        if directions['incoming']:
            neighbors.extend(list(graph.predecessors(node)))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_neighbors = [n for n in neighbors if not (n in seen or seen.add(n))]
        return unique_neighbors[:max_neighbors]
    
    def create_visualization(self, word, max_nodes=50, depth=2, neighbor_limit=5,
                           progress_callback=None, directions=None):
        """Create graph data for visualization."""
        update_progress = lambda progress, message: progress_callback(
            {"progress": progress, "message": message}
        ) if progress_callback else None
        
        update_progress(5, "Loading graph data...")
        
        # Load only the required subgraph
        subgraph = self.graph_handler.load_subgraph(
            word,
            depth=depth,
            max_neighbors=neighbor_limit
        )
        
        if not subgraph:
            return None, "Word not found in graph"
        
        try:
            update_progress(30, "Processing graph data...")
            
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
                      node in subgraph.successors(word)) or
                      (directions.get('incoming', True) and
                       node in subgraph.predecessors(word))):
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
                    current_progress = 30 + (i / node_count * 35)
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
                    current_progress = 65 + (i / edge_count * 30)
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
            
        finally:
            # Clean up resources
            if subgraph:
                subgraph.clear()
            self.graph_handler.cleanup()

def main():
    """Test visualization creation."""
    visualizer = GraphVisualizer()
    graph_data, error = visualizer.create_visualization(
        "test",
        progress_callback=lambda x: print(f"{x['progress']}%: {x['message']}")
    )
    if error:
        print(f"Error: {error}")
    else:
        print("Visualization data created successfully")

if __name__ == '__main__':
    main()