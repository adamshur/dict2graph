"""Main entry point for the dictionary graph application."""

import argparse
from dictionary_graph.preprocessing import preprocess_dictionary
from dictionary_graph.graph import DictionaryGraph
from dictionary_graph.web.app import main as run_web_server

def main():
    """Parse arguments and run the appropriate function."""
    parser = argparse.ArgumentParser(
        description='Dictionary Graph Application',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        'action',
        choices=['process', 'build', 'serve'],
        help='''
        Action to perform:
        - process: Preprocess the dictionary data using NLP
        - build: Build the graph from preprocessed data
        - serve: Run the web visualization server
        '''
    )
    
    args = parser.parse_args()
    
    if args.action == 'process':
        preprocess_dictionary()
    elif args.action == 'build':
        graph_handler = DictionaryGraph()
        if graph_handler.build_graph():
            graph_handler.save_graph()
            stats = graph_handler.get_graph_stats()
            if stats:
                print("\n=== Graph Statistics ===")
                print(f"Nodes: {stats['nodes']}")
                print(f"Edges: {stats['edges']}")
                print(f"Average Degree: {stats['avg_degree']:.2f}")
    else:  # serve
        run_web_server()

if __name__ == '__main__':
    main()