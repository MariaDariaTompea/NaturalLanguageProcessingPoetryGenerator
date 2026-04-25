from datasets import load_dataset
import re

def get_clean_corpus(limit=10000):
    """Fetches and cleans the Gutenberg Poetry Corpus"""
    dataset = load_dataset("allisonparrish/gutenberg-poetry-corpus", split="train")
    lines = [line['s'].lower() for line in dataset.select(range(limit))]
    # Basic cleaning to remove non-alphabetic noise
    return [re.sub(r'[^a-z\s]', '', line).strip() for line in lines if line.strip()]

def get_semantic_neighbors(word, vocab, top_n=10):
    """Placeholder for semantic constraint generation"""
    # In a full implementation, use WordNet or Wikipedia Link-Based Measure
    return [w for w in vocab if w.startswith(word[0])][:top_n]