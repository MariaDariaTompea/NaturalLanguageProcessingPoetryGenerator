from utils.nlp_helpers import get_clean_corpus
from models.markov_model import CMPPoet

def main():
    print("Initializing Symphony of Words (CMP Model)...")
    corpus = get_clean_corpus(limit=20000)
    poet = CMPPoet(corpus)

    # Constraints: Word at index 2 must be related to 'sea'
    # Word at index 5 must be 'light'
    my_constraints = {
        2: ["sea", "ocean", "waves", "deep"],
        5: ["light", "bright", "white"]
    }

    print("\n--- Generated Verses ---")
    for _ in range(4):
        print(poet.generate_line(L=6, constraints=my_constraints))

if __name__ == "__main__":
    main()