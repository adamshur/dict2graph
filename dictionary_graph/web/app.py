"""Flask web application for dictionary graph visualization."""

from flask import Flask, render_template, jsonify, request, Response
import json
from queue import Queue
import logging
import gc
from ..visualization import GraphVisualizer

# Initialize Flask app with correct template and static paths
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Progress tracking
progress_queues = {}

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/progress/<word>')
def progress(word):
    """Stream visualization progress updates."""
    if not word.isalnum():
        return jsonify({'error': 'Invalid word format'}), 400
        
    def generate():
        q = Queue()
        progress_queues[word] = q
        try:
            while True:
                progress = q.get()
                yield f"data: {json.dumps(progress)}\n\n"
                if progress['progress'] == 100:
                    break
        finally:
            if word in progress_queues:
                del progress_queues[word]
            gc.collect()
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/visualize', methods=['POST'])
def visualize():
    """Create and return visualization data for the requested word."""
    visualizer = None
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid JSON format'}), 400

        # Validate and sanitize input
        word = str(data.get('word', '')).lower().strip()
        if not word or not word.isalnum():
            return jsonify({'error': 'Invalid word provided'}), 400

        # Get visualization parameters with reasonable defaults
        max_nodes = min(int(data.get('max_nodes', 50)), 100)  # Limit max nodes
        depth = min(int(data.get('depth', 2)), 3)  # Limit depth
        neighbor_limit = min(int(data.get('neighbor_limit', 5)), 10)  # Limit neighbors

        # Create a progress queue for this visualization
        progress_queue = Queue()
        progress_queues[word] = progress_queue

        # Initialize visualizer for this request only
        visualizer = GraphVisualizer()

        try:
            # Create visualization with progress tracking
            directions = data.get('directions', {'outgoing': True, 'incoming': True})
            graph_data, error = visualizer.create_visualization(
                word,
                max_nodes=max_nodes,
                depth=depth,
                neighbor_limit=neighbor_limit,
                progress_callback=lambda x: progress_queue.put(x),
                directions=directions
            )

            if error:
                logger.error(f"Visualization error for word '{word}': {error}")
                return jsonify({'error': error}), 400

            return jsonify({'graph_data': graph_data})

        finally:
            # Clean up progress queue
            if word in progress_queues:
                del progress_queues[word]

    except Exception as e:
        logger.exception(f"Unexpected error in visualization endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
    finally:
        # Ensure cleanup of visualizer resources
        if visualizer:
            del visualizer
        gc.collect()

def main():
    """Run the Flask application."""
    app.run(debug=True, host='127.0.0.1')

if __name__ == '__main__':
    main()