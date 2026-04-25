import random
from utils.nlp_helpers import load_corpus
from models.markov_model import (
    preprocess_text,
    build_markov_chain,
    generate_simple_poem,
    EnhancedMarkovPoet
)

def main():
    corpus_path = "corpus.txt"

    print("Loading corpus...")
    text = load_corpus(corpus_path)

    if not text:
        return

    # =========================
    # SIMPLE MODEL
    # =========================
    tokens = preprocess_text(text)

    print("\n--- SIMPLE (UNIGRAM) ---")
    uni_chain = build_markov_chain(tokens, n=1)
    print(generate_simple_poem(uni_chain, n=1))

    print("\n--- SIMPLE (BIGRAM) ---")
    bi_chain = build_markov_chain(tokens, n=2)
    print(generate_simple_poem(bi_chain, n=2))

    # =========================
    # ENHANCED MODEL
    # =========================
    print("\n--- ENHANCED NLP MODEL ---")

    poet = EnhancedMarkovPoet(text, order=2)
    theme = random.choice(["love", "night", "science", "heart"])
    print(f"Theme: {theme}")

    print(poet.generate_poem(theme_word=theme))


if __name__ == "__main__":
    main()