import os
import random
import spacy
import nltk
from nltk.corpus import wordnet
from gensim.models import Word2Vec

# SpaCy model yükleme
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    nlp.max_length = 5000000
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    nlp.max_length = 5000000


def load_corpus(file_path):
    """Reads the corpus from a text file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_synonym(word):
    """WordNet üzerinden synonym seçer"""
    syns = wordnet.synsets(word)
    if not syns:
        return word

    synonyms = set()
    for syn in syns:
        for l in syn.lemmas():
            if l.name() != word:
                synonyms.add(l.name().replace('_', ' '))

    return random.choice(list(synonyms)) if synonyms else word


def train_word2vec(corpus_text):
    """Word2Vec model eğitir"""
    sentences = [line.lower().split() for line in corpus_text.split('\n') if line.strip()]
    return Word2Vec(sentences, vector_size=50, window=5, min_count=1, workers=4)