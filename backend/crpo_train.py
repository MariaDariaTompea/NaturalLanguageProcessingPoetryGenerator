from .api import PoetryAPI
from .utils.nlp_helpers import get_crpo_clean_corpus, prepare_data
import tensorflow as tf
import os

def run_training():
    limit_val = 20000 # Hız için 20 bin demiştik
    print(f"Loading {limit_val} lines of poetry...")
    
    corpus = get_crpo_clean_corpus(limit=limit_val)
    X, y, char_to_int, vocab = prepare_data(corpus)
    y_cat = tf.keras.utils.to_categorical(y, num_classes=len(vocab))

    # KRİTİK: api'ye de aynı limiti gönderiyoruz ki alfabe (vocab) aynı olsun
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

if __name__ == "__main__":
    run_training()