"""
Script for training the CRPO deep learning model.
It prepares the text data and saves the trained model weights.
"""
from .api import PoetryAPI
from .utils.nlp_helpers import get_crpo_clean_corpus, prepare_data
import tensorflow as tf
import os

def run_training():
    # Prepares the corpus, processes the data, and runs the training loop
    limit_val = 20000 
    print(f"Loading {limit_val} lines of poetry...")
    
    corpus = get_crpo_clean_corpus(limit=limit_val)
    X, y, char_to_int, vocab = prepare_data(corpus)
    y_cat = tf.keras.utils.to_categorical(y, num_classes=len(vocab))

    # Initializing API with the same limit to keep vocabulary consistent
    api = PoetryAPI(limit=limit_val) 
    
    print(f"Starting training with vocab size: {len(vocab)}")
    
    api.crpo_model.fit(
        X, y_cat, 
        epochs=5, 
        batch_size=256, 
        shuffle=True,
        validation_split=0.1
    )
    
    api.crpo_model.save_weights('crpo_weights.weights.h5')
    print("Training complete. Weights saved to crpo_weights.weights.h5")

if __name__ == "__main__":
    run_training()