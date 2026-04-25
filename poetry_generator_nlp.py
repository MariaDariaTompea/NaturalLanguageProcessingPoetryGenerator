import random
import os
import spacy
import nltk
from nltk.corpus import wordnet
from gensim.models import Word2Vec
import re

# Initialize NLP tools
# Using 'en_core_web_sm' for speed and availability
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If not found, try common download
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def load_corpus(file_path):
    """Reads the corpus from a text file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

class EnhancedMarkovPoet:
    def __init__(self, corpus_text, order=2):
        self.order = order
        self.corpus_text = corpus_text
        self.tokens = [] # List of Spacy tokens (includes lemmatized and POS)
        self.chain = {}   # (tuple of n lemmas) -> list of surface words
        self.pos_map = {} # word -> set of its seen POS tags
        self.w2v_model = None
        
        self._analyze_corpus()
        self._train_embeddings()

    def _analyze_corpus(self):
        """Processes corpus with Spacy to extract lemmas and POS tags."""
        print("Analyzing corpus with SpaCy (Lemmatization & POS tagging)...")
        # Process in chunks to avoid memory issues for very large corpora
        doc = nlp(self.corpus_text)
        self.tokens = [t for t in doc if not t.is_space and not t.is_punct]
        
        # Build the n-gram chain based on lemmas for flexibility
        # but storing original text for poetic surface forms
        for i in range(len(self.tokens) - self.order):
            # State is a tuple of n lemmas
            state = tuple(t.lemma_ for t in self.tokens[i : i + self.order])
            next_token = self.tokens[i + self.order]
            
            if state not in self.chain:
                self.chain[state] = []
            
            # Store the tuple (surface_text, pos_tag)
            self.chain[state].append((next_token.text, next_token.pos_))
            
            # Map word to its tags
            w = next_token.text.lower()
            if w not in self.pos_map:
                self.pos_map[w] = set()
            self.pos_map[w].add(next_token.pos_)

    def _train_embeddings(self):
        """Trains a local Word2Vec model on the corpus for semantic similarity."""
        print("Training local Word2Vec embeddings...")
        sentences = [line.lower().split() for line in self.corpus_text.split('\n') if line.strip()]
        self.w2v_model = Word2Vec(sentences, vector_size=50, window=5, min_count=1, workers=4)

    def get_synonym(self, word):
        """Randomly replaces a word with a synonym from WordNet."""
        syns = wordnet.synsets(word)
        if not syns:
            return word
        
        synonyms = set()
        for syn in syns:
            for l in syn.lemmas():
                if l.name() != word:
                    synonyms.add(l.name().replace('_', ' '))
        
        return random.choice(list(synonyms)) if synonyms else word

    def generate_poem(self, length=40, words_per_line=6, theme_word=None):
        """
        Generates a poem using:
        - Bigram/Trigram models
        - POS sequence constraints
        - Semantic similarity scoring
        - Repetition filtering
        """
        if not self.chain:
            return "Corpus too small."

        # Grammatical sequence we want to emulate (simplified)
        pos_sequence = ["NOUN", "VERB", "ADJ", "NOUN", "ADP", "DET", "NOUN"]
        
        # Start with a random key
        current_lemmas = random.choice(list(self.chain.keys()))
        poem_words = []
        for l in current_lemmas:
            # Pick a surface form for the initial lemmas (fallback search)
            poem_words.append(l) # Using lemma as fallback for start

        for i in range(length):
            state = tuple(current_lemmas)
            candidates = self.chain.get(state, [])
            
            if not candidates:
                # Dead end, reset to a random state
                new_state = random.choice(list(self.chain.keys()))
                current_lemmas = list(new_state)
                continue

            # Filtering and Scoring
            ideal_pos = pos_sequence[i % len(pos_sequence)]
            scored_candidates = []
            
            for word, pos in candidates:
                # 1. POS Scoring
                score = 1.0
                if pos == ideal_pos:
                    score += 2.0
                
                # 2. Semantic Similarity to theme (if provided)
                if theme_word and theme_word.lower() in self.w2v_model.wv:
                    w_lower = word.lower()
                    if w_lower in self.w2v_model.wv:
                        similarity = self.w2v_model.wv.similarity(w_lower, theme_word.lower())
                        score += (similarity * 3.0)
                
                # 3. Repeat filtering
                if word.lower() in [pw.lower() for pw in poem_words[-3:]]:
                    score -= 5.0 # Penalize recent repetition
                
                scored_candidates.append((word, score))
            
            # Weighted random selection OR pick best
            # Let's pick from the top 3 best to balance randomness and logic
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_pool = scored_candidates[:max(1, len(scored_candidates)//2)]
            choice_word = random.choice(best_pool)[0]
            
            poem_words.append(choice_word)
            
            # Advancing state (using tokens from corpus for next lemmas)
            # Find the lemma of our choice_word to update the state
            # This is a simplification: we'll just track the last n tokens
            doc_word = nlp(choice_word)
            current_lemmas = (list(current_lemmas) + [doc_word[0].lemma_])[1:]

        # Post-processing: WordNet richness (occasional replacement)
        final_poem = []
        for word in poem_words:
            if len(word) > 4 and random.random() < 0.1: # 10% chance to swap
                final_poem.append(self.get_synonym(word))
            else:
                final_poem.append(word)

        # Formatting
        lines = []
        current_line = []
        capitalize_next = False
        
        for word in final_poem:
            if not current_line and re.match(r'^[.,!?;:]+$', word):
                continue
                
            if not current_line or capitalize_next:
                word = word.capitalize()
                capitalize_next = False
                
            if re.match(r'^[.,!?;:]+$', word) and current_line:
                current_line[-1] += word
                if re.search(r'[.!?;]$', word):
                    capitalize_next = True
                continue
                
            current_line.append(word)
            
            if len(current_line) >= words_per_line:
                lines.append(" ".join(current_line))
                current_line = []
                
        if current_line:
            lines.append(" ".join(current_line))
            
        return "\n".join(lines).strip()

def main():
    corpus_path = "large_corpus.txt"
    if not os.path.exists(corpus_path):
        corpus_path = "corpus.txt" # fallback
        
    print(f"Loading corpus: {corpus_path}")
    raw_text = load_corpus(corpus_path)
    
    # We'll use a subset if it's too massive, but 2000 lines should be fine.
    poet = EnhancedMarkovPoet(raw_text, order=2) # Using Bigram (state of 2)
    
    print("\n--- Generating NLP-Enhanced Poem (Bigram + POS + Semantic + WordNet) ---")
    # Setting a theme word for semantic guidance
    theme = random.choice(["star", "love", "night", "atoms", "heart", "science"])
    print(f"Guided by theme: '{theme}'")
    
    poem = poet.generate_poem(length=36, words_per_line=6, theme_word=theme)
    print("\nResult:\n")
    print(poem)

if __name__ == "__main__":
    main()
