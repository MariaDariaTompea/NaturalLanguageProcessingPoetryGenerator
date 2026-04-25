##### gpt says to put this file to models/markow (and some of it in models/utils/nlp_helpers)
##### i didnt delete this one but tried put this in that file without lefting out anything

import random
import re
import os

def load_corpus(file_path):
    """
    Reads the corpus from a text file.
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return ""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def preprocess_text(text):
    """
    Cleans and tokenizes the text.
    - Lowers case
    - Removes punctuation (optional, keeping it simple as per instructions)
    - Splits into words (tokenization)
    """
    # Lowercase
    text = text.lower()
    
    # Remove unwanted characters/punctuation (optional but improves matching)
    # Keeping it simple: split by whitespace
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def build_markov_chain(tokens, n=1):
    """
    Builds a Markov Chain model.
    n=1: Single word (monogram)
    n=2: Bigram (pair of words)
    """
    chain = {}
    
    for i in range(len(tokens) - n):
        # The key is the current word (or tuple for bigrams)
        state = tuple(tokens[i:i+n])
        next_word = tokens[i+n]
        
        if state not in chain:
            chain[state] = []
        chain[state].append(next_word)
        
    return chain

def generate_poem(chain, n=1, length=30, words_per_line=5):
    """
    Generates a poem using the Markov Chain.
    """
    if not chain:
        return "Error: Chain is empty. Check your corpus."
    
    # Start with a random key
    current_state = random.choice(list(chain.keys()))
    poem_tokens = list(current_state)
    
    for _ in range(length - n):
        if current_state in chain:
            next_word = random.choice(chain[current_state])
            poem_tokens.append(next_word)
            
            # Update the current state
            current_state = tuple(poem_tokens[-n:])
        else:
            # If we hit a dead end, pick a new random word
            current_state = random.choice(list(chain.keys()))
            poem_tokens.extend(list(current_state))
    
    # Formatting
    lines = []
    current_line = []
    capitalize_next = False
    
    for word in poem_tokens:
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
    corpus_path = "corpus.txt"
    print(f"--- Simple Poetry Generator ---")
    print(f"Loading corpus from: {corpus_path}")
    
    raw_text = load_corpus(corpus_path)
    if not raw_text:
        return
        
    tokens = preprocess_text(raw_text)
    print(f"Token count: {len(tokens)}")
    
    # User choice for simple or bigram model
    # For now, let's show simple first, then bigram
    
    print("\n--- Generating Simple Poem (Unigram) ---")
    unigram_chain = build_markov_chain(tokens, n=1)
    poem_unigram = generate_poem(unigram_chain, n=1, length=30, words_per_line=6)
    print(poem_unigram)
    
    print("\n--- Generating Advanced Poem (Bigram) ---")
    bigram_chain = build_markov_chain(tokens, n=2)
    poem_bigram = generate_poem(bigram_chain, n=2, length=30, words_per_line=6)
    print(poem_bigram)

if __name__ == "__main__":
    main()
