import random
import re
from utils.nlp_helpers import nlp, get_synonym, train_word2vec


# =====================================
# SIMPLE MARKOV MODEL
# =====================================

def preprocess_text(text):
    """
    Lowercase + tokenize
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens


def build_markov_chain(tokens, n=1):
    """
    n=1 -> unigram
    n=2 -> bigram
    """
    chain = {}

    for i in range(len(tokens) - n):
        state = tuple(tokens[i:i+n])
        next_word = tokens[i+n]

        if state not in chain:
            chain[state] = []

        chain[state].append(next_word)

    return chain


def generate_simple_poem(chain, n=1, length=30, words_per_line=5):
    """
    Basic Markov text generation
    """
    if not chain:
        return "Error: Chain is empty."

    current_state = random.choice(list(chain.keys()))
    poem_tokens = list(current_state)

    for _ in range(length - n):
        if current_state in chain:
            next_word = random.choice(chain[current_state])
            poem_tokens.append(next_word)

            current_state = tuple(poem_tokens[-n:])
        else:
            current_state = random.choice(list(chain.keys()))
            poem_tokens.extend(list(current_state))

    # Format
    lines = []
    current_line = []
    for word in poem_tokens:
        if not current_line and re.match(r'^[.,!?;:]+$', word):
            continue
            
        if not current_line:
            word = word.capitalize()
            
        if re.match(r'^[.,!?;:]+$', word) and current_line:
            current_line[-1] += word
            continue
            
        current_line.append(word)
        
        if len(current_line) >= words_per_line:
            lines.append(" ".join(current_line))
            current_line = []
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return "\n".join(lines).strip()


# =====================================
# ENHANCED MARKOV MODEL (NLP)
# =====================================

class EnhancedMarkovPoet:
    def __init__(self, corpus_text, order=2):
        self.order = order
        self.corpus_text = corpus_text

        self.tokens = []
        self.chain = {}
        self.pos_map = {}
        self.w2v_model = None

        self._analyze_corpus()
        self._train_embeddings()

    def _analyze_corpus(self):
        """
        SpaCy ile:
        - Lemmatization
        - POS tagging
        """
        print("Analyzing corpus with SpaCy...")

        doc = nlp(self.corpus_text)
        self.tokens = [t for t in doc if not t.is_space and not t.is_punct]

        for i in range(len(self.tokens) - self.order):
            state = tuple(t.lemma_ for t in self.tokens[i:i+self.order])
            next_token = self.tokens[i + self.order]

            if state not in self.chain:
                self.chain[state] = []

            self.chain[state].append((next_token.text, next_token.pos_))

            # POS map
            word_lower = next_token.text.lower()
            if word_lower not in self.pos_map:
                self.pos_map[word_lower] = set()

            self.pos_map[word_lower].add(next_token.pos_)

    def _train_embeddings(self):
        """
        Word2Vec eğitimi
        """
        print("Training Word2Vec...")
        self.w2v_model = train_word2vec(self.corpus_text)

    def generate_poem(self, length=40, words_per_line=6, theme_word=None):
        """
        Advanced poem generation:
        - POS control
        - Semantic similarity
        - Repetition penalty
        - WordNet variation
        """
        if not self.chain:
            return "Corpus too small."

        pos_sequence = ["NOUN", "VERB", "ADJ", "NOUN", "ADP", "DET", "NOUN"]

        current_lemmas = list(random.choice(list(self.chain.keys())))
        poem_words = list(current_lemmas)

        for i in range(length):
            state = tuple(current_lemmas)
            candidates = self.chain.get(state, [])

            if not candidates:
                current_lemmas = list(random.choice(list(self.chain.keys())))
                continue

            ideal_pos = pos_sequence[i % len(pos_sequence)]
            scored_candidates = []

            for word, pos in candidates:
                score = 1.0

                # POS bonus
                if pos == ideal_pos:
                    score += 2.0

                # Semantic similarity
                if theme_word and theme_word.lower() in self.w2v_model.wv:
                    w_lower = word.lower()

                    if w_lower in self.w2v_model.wv:
                        similarity = self.w2v_model.wv.similarity(
                            w_lower, theme_word.lower()
                        )
                        score += similarity * 3.0

                # repetition penalty
                if word.lower() in [pw.lower() for pw in poem_words[-3:]]:
                    score -= 5.0

                scored_candidates.append((word, score))

            # choose from best half
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_pool = scored_candidates[:max(1, len(scored_candidates)//2)]

            chosen_word = random.choice(best_pool)[0]
            poem_words.append(chosen_word)

            # update state (lemma)
            doc_word = nlp(chosen_word)
            current_lemmas = (current_lemmas + [doc_word[0].lemma_])[1:]

        # WordNet variation
        final_words = []
        for word in poem_words:
            if len(word) > 4 and random.random() < 0.1:
                final_words.append(get_synonym(word))
            else:
                final_words.append(word)

        # Formatting
        lines = []
        current_line = []
        for word in final_words:
            if not current_line and re.match(r'^[.,!?;:]+$', word):
                continue
                
            if not current_line:
                word = word.capitalize()
                
            if re.match(r'^[.,!?;:]+$', word) and current_line:
                current_line[-1] += word
                continue
                
            current_line.append(word)
            
            if len(current_line) >= words_per_line:
                lines.append(" ".join(current_line))
                current_line = []
                
        if current_line:
            lines.append(" ".join(current_line))
            
        return "\n".join(lines).strip()