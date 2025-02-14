"""Module for preprocessing dictionary data using NLP."""

import json
import spacy
from multiprocessing import Pool, cpu_count, freeze_support
from tqdm import tqdm
import joblib
from config import DICTIONARY_FILE, PREPROCESSED_FILE, SPACY_MODEL, SPACY_DISABLED

def initialize_nlp():
    """Initialize spaCy NLP model."""
    print("Loading NLP model...")
    spacy.prefer_gpu()
    return spacy.load(SPACY_MODEL, disable=SPACY_DISABLED)

def preprocess_word(word_def):
    """Process a single word-definition pair."""
    word, definition = word_def
    doc = nlp(definition.lower())
    tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_stop]
    return word, tokens

def init_worker(nlp_model):
    """Initialize worker process with NLP model."""
    global nlp
    nlp = nlp_model

def preprocess_dictionary():
    """Preprocess the entire dictionary using multiprocessing."""
    # Load NLP model
    nlp_model = initialize_nlp()
    print("NLP model ready.\n")

    # Load dictionary data
    print("Loading dictionary...")
    try:
        with open(DICTIONARY_FILE) as f:
            data = json.load(f)
        print(f"Loaded {len(data)} entries.\n")
    except Exception as e:
        print(f"Error loading dictionary: {str(e)}")
        return None

    # Preprocessing with multiprocessing
    print("Preprocessing definitions...")
    with Pool(cpu_count(), initializer=init_worker, initargs=(nlp_model,)) as pool:
        results = list(tqdm(pool.imap(preprocess_word, data.items()),
                          total=len(data), desc="Processing", unit="words"))
    processed = dict(results)
    print("Preprocessing complete.\n")

    # Save processed data
    joblib.dump(processed, PREPROCESSED_FILE)
    print("Saved processed data.\n")
    
    return processed

if __name__ == '__main__':
    freeze_support()
    preprocess_dictionary()