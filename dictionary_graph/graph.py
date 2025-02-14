"""Module for graph construction and operations."""

import networkx as nx
from tqdm import tqdm
import joblib
from config import PREPROCESSED_FILE, GRAPH_FILE
import gc

class DictionaryGraph:
    """Class to handle dictionary graph operations."""
    
    def __init__(self):
        self.graph = None
        self.processed_data = None
    
    def load_processed_data(self):
        """Load preprocessed dictionary data."""
        try:
            self.processed_data = joblib.load(PREPROCESSED_FILE)
            print(f"Loaded {len(self.processed_data)} processed entries.")
            return True
        except Exception as e:
            print(f"Error loading processed data: {str(e)}")
            return False
    
    def build_graph(self):
        """Construct the graph from processed data."""
        if not self.processed_data:
            if not self.load_processed_data():
                return False
        
        print("Constructing graph...")
        self.graph = nx.DiGraph()
        word_set = set(self.processed_data.keys())
        edge_count = 0
        
        # Add nodes first
        self.graph.add_nodes_from(word_set)
        
        # Add edges based on token matches
        for word, tokens in tqdm(self.processed_data.items(), desc="Building graph"):
            # Find valid connections
            connections = [token for token in tokens if token in word_set]
            
            # Add edges
            for target in connections:
                if word != target:  # Avoid self-references
                    self.graph.add_edge(word, target)
                    edge_count += 1
        
        print(f"\nGraph constructed with {edge_count} relationships.")
        return True
    
    def save_graph(self):
        """Save the graph to a file."""
        if not self.graph:
            print("No graph to save.")
            return False
            
        try:
            nx.write_gexf(self.graph, GRAPH_FILE)
            print("Graph saved successfully.")
            return True
        except Exception as e:
            print(f"Error saving graph: {str(e)}")
            return False
    
    def load_subgraph(self, word, depth=2, max_neighbors=5):
        """Load a subgraph centered around a specific word."""
        try:
            # Load the full graph first
            full_graph = nx.read_gexf(GRAPH_FILE, node_type=str)
            
            if word not in full_graph:
                return None
            
            # Initialize subgraph with the target word
            nodes_to_include = {word}
            current_layer = {word}
            
            # Expand the subgraph up to the specified depth
            for _ in range(depth):
                next_layer = set()
                for node in current_layer:
                    # Get successors (outgoing edges)
                    successors = list(full_graph.successors(node))[:max_neighbors]
                    next_layer.update(successors)
                    nodes_to_include.update(successors)
                    
                    # Get predecessors (incoming edges)
                    predecessors = list(full_graph.predecessors(node))[:max_neighbors]
                    next_layer.update(predecessors)
                    nodes_to_include.update(predecessors)
                
                current_layer = next_layer
            
            # Create the subgraph with the collected nodes
            subgraph = full_graph.subgraph(nodes_to_include).copy()
            
            # Clean up the full graph to free memory
            full_graph.clear()
            del full_graph
            gc.collect()
            
            return subgraph
            
        except Exception as e:
            print(f"Error loading subgraph: {str(e)}")
            return None
    
    def get_graph_stats(self):
        """Get basic statistics about the graph."""
        try:
            graph = nx.read_gexf(GRAPH_FILE)
            stats = {
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "avg_degree": sum(dict(graph.degree()).values()) / graph.number_of_nodes()
            }
            graph.clear()
            del graph
            gc.collect()
            return stats
        except Exception:
            return None
    
    def get_word_connections(self, word, limit=10):
        """Get connections for a specific word."""
        try:
            graph = nx.read_gexf(GRAPH_FILE)
            if word not in graph:
                return None
            
            connections = {
                "outgoing": list(graph.successors(word))[:limit],
                "incoming": list(graph.predecessors(word))[:limit]
            }
            graph.clear()
            del graph
            gc.collect()
            return connections
        except Exception:
            return None

    def cleanup(self):
        """Clean up resources and free memory."""
        if self.graph:
            self.graph.clear()
            self.graph = None
        if self.processed_data:
            self.processed_data = None
        gc.collect()

def main():
    """Main function to build and save the graph."""
    graph_handler = DictionaryGraph()
    if graph_handler.build_graph():
        graph_handler.save_graph()
        stats = graph_handler.get_graph_stats()
        print("\n=== Graph Statistics ===")
        print(f"Nodes: {stats['nodes']}")
        print(f"Edges: {stats['edges']}")
        print(f"Average Degree: {stats['avg_degree']:.2f}")
        graph_handler.cleanup()

if __name__ == '__main__':
    main()