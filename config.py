"""Configuration settings for the dictionary graph application."""

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
DICTIONARY_FILE = os.path.join(DATA_DIR, "dictionary.json")
PREPROCESSED_FILE = os.path.join(DATA_DIR, "preprocessed.joblib")
GRAPH_FILE = os.path.join(DATA_DIR, "dictionary_graph.gexf")

# NLP settings
SPACY_MODEL = "en_core_web_sm"
SPACY_DISABLED = ["parser", "ner"]

# Graph visualization settings
VIS_HEIGHT = "100%"
VIS_WIDTH = "100%"
VIS_BGCOLOR = "#ffffff"
VIS_FONT_COLOR = "black"

# Node colors
NODE_COLORS = {
    "default": "#97c2fc",  # Blue
    "target": "#ff4444",   # Red
    "neighbor": "#44ff44"  # Green
}

# Node sizes
NODE_SIZES = {
    "default": 25,
    "target": 35,
    "neighbor": 30
}