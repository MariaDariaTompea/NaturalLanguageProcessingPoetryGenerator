"""
Helper functions for Natural Language Processing tasks.
Includes tools for rhythm analysis, rhyme checking, and corpus preprocessing.
"""
import re
import os
import nltk
import numpy as np
from datasets import load_dataset
from nltk.corpus import cmudict

# Download and load the CMU Pronouncing Dictionary
nltk.download('cmudict')
d = cmudict.dict()

def get_meter_profile(word):
    # Returns the stress pattern of a word (e.g., 'today' -> '01')
    word = word.lower()
    if word in d:
        # Extract numeric stress markers from the first phonetic variation
        return "".join([char for char in d[word][0] if char.isdigit()])
    return "0" * (len(word) // 3)

def check_rhyme_manual(word1, word2):
    # Checks if two words rhyme by comparing their phonetic endings
    def get_rhyme_part(word):
        if word in d:
            # Find the part of the word from the last stressed vowel to the end
            phonemes = d[word][0]
            for i in range(len(phonemes)-1, -1, -1):
                if any(char.isdigit() and char != '0' for char in phonemes[i]):
                    return phonemes[i:]
        return word[-2:]

    return get_rhyme_part(word1.lower()) == get_rhyme_part(word2.lower())

def get_crpo_clean_corpus(limit=50000):
    # Downloads the Gutenberg poetry dataset and cleans it for training
    if not os.path.exists('data'):
        os.makedirs('data')

    dataset = load_dataset("biglam/gutenberg-poetry-corpus", split="train")
    
    # Extract raw text from the dataset
    raw_lines = [line['line'] for line in dataset.select(range(limit))]
    full_text = "\n".join(raw_lines)

    # Save the raw data for debugging purposes
    with open("data/raw_corpus_debug.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # Data Cleaning: Remove non-ASCII characters and normalize whitespaces
    clean_text = re.sub(r'[^\x00-\x7f]', r'', full_text)
    clean_text = re.sub(r'[ \t]+', ' ', clean_text)
    clean_text = re.sub(r'\n+', '\n', clean_text)
    clean_text = clean_text.lower()
    
    # Save the processed text for model training
    with open("data/processed_corpus_debug.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

    print(f"--- Debug: Data saved to data/ folder (Limit: {limit} lines) ---")
    
    return clean_text

def prepare_data(corpus, seq_length=40):
    # Prepares sequences for character-level training (needed for crpo_train.py)
    chars = sorted(list(set(corpus)))
    char_to_int = {c: i for i, c in enumerate(chars)}
    
    X = []
    y = []
    for i in range(0, len(corpus) - seq_length, 1):
        seq_in = corpus[i:i + seq_length]
        seq_out = corpus[i + seq_length]
        X.append([char_to_int[char] for char in seq_in])
        y.append(char_to_int[seq_out])
        
    X = np.reshape(X, (len(X), seq_length))
    return X, y, char_to_int, chars