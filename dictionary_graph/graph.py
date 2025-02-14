"""Module for graph construction and operations."""

import networkx as nx
from tqdm import tqdm
import joblib
from config import PREPROCESSED_FILE, GRAPH_FILE

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
    
    def load_graph(self):
        """Load the graph from file."""
        try:
            self.graph = nx.read_gexf(GRAPH_FILE)
            print(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
            return True
        except Exception as e:
            print(f"Error loading graph: {str(e)}")
            return False
    
    def get_graph_stats(self):
        """Get basic statistics about the graph."""
        if not self.graph:
            return None
            
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "avg_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
        }
    
    def get_word_connections(self, word, limit=10):
        """Get connections for a specific word."""
        if not self.graph or word not in self.graph:
            return None
            
        return {
            "outgoing": list(self.graph.successors(word))[:limit],
            "incoming": list(self.graph.predecessors(word))[:limit]
        }

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

if __name__ == '__main__':
    main()