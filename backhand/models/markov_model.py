import random
import re
import pronouncing
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


# =====================================
# ENHANCED MARKOV MODEL (NLP)
# =====================================

class EnhancedMarkovPoet:
    def __init__(self, corpus_text, order=2):
        self.order = order
        self.corpus_text = corpus_text

        self.tokens = []
        self.chain = {}
        self.rev_chain = {}
        self.pos_map = {}
        self.w2v_model = None
        self.corpus_vocab = set()

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

            # Reverse Chain logic
            rev_state = tuple(t.lemma_ for t in self.tokens[i+1:i+self.order+1])
            prev_token = self.tokens[i]

            if rev_state not in self.rev_chain:
                self.rev_chain[rev_state] = []
            
            self.rev_chain[rev_state].append((prev_token.text, prev_token.pos_))

            # POS map
            word_lower = next_token.text.lower()
            self.corpus_vocab.add(word_lower)
            if word_lower not in self.pos_map:
                self.pos_map[word_lower] = set()

            self.pos_map[word_lower].add(next_token.pos_)

    def _train_embeddings(self):
        """
        Word2Vec eğitimi
        """
        print("Training Word2Vec...")
        self.w2v_model = train_word2vec(self.corpus_text)

    def get_corpus_rhyme(self, word):
        """
        Returns a word from the corpus vocabulary that rhymes with `word`.
        Uses the `pronouncing` dictionary. Returns None if no rhyme is found.
        """
        rhymes = pronouncing.rhymes(word)
        valid_rhymes = [r for r in rhymes if r in self.corpus_vocab and r != word]
        if valid_rhymes:
            return random.choice(valid_rhymes)
        return None

    def get_word_stress(self, word):
        """
        Returns the stress sequence of a word using pronouncing.
        E.g., "today" -> "01". Returns "" if the word is not in the dictionary.
        """
        if re.match(r'^[.,!?;:]+$', word):
            return ""
        
        phones = pronouncing.phones_for_word(word.lower())
        if phones:
            stresses = pronouncing.stresses(phones[0])
            return stresses.replace('2', '1')
        return ""

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
        capitalize_next = False
        
        for word in final_words:
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

    def generate_rhymed_poem(self, rhyme_scheme="AABBCC", words_per_line=6, theme_word=None):
        """
        Generates a poem enforcing a strict rhyme scheme using Backward Markov Generation.
        """
        if not self.rev_chain:
            return "Corpus too small or not analyzed."

        lines = []
        rhyme_anchors = {}

        for rh_char in rhyme_scheme:
            target_word = None

            # Determine anchor word for this line
            if rh_char not in rhyme_anchors:
                # Find a random word from the corpus that has at least one valid rhyme in the corpus
                for _ in range(50):
                    candidate = random.choice(list(self.corpus_vocab))
                    if self.get_corpus_rhyme(candidate):
                        target_word = candidate
                        break
                if not target_word:
                    target_word = random.choice(list(self.corpus_vocab))
                rhyme_anchors[rh_char] = target_word
            else:
                target_word = self.get_corpus_rhyme(rhyme_anchors[rh_char])
                if not target_word:
                    target_word = rhyme_anchors[rh_char]

            # Generate line backwards from target_word
            doc_target = nlp(target_word)
            target_lemma = doc_target[0].lemma_

            possible_rev_states = [s for s in self.rev_chain.keys() if s[-1] == target_lemma]
            line_words = [target_word]
            
            if possible_rev_states:
                current_rev_state = random.choice(possible_rev_states)
                
                # Insert the remaining words from the state
                for w in reversed(current_rev_state[:-1]):
                    line_words.insert(0, w)

                # Generate the rest of the line backwards
                for i in range(words_per_line - len(current_rev_state)):
                    candidates = self.rev_chain.get(current_rev_state, [])
                    if not candidates:
                        current_rev_state = random.choice(list(self.rev_chain.keys()))
                        continue

                    # Score candidates based on semantic bias if needed
                    scored_candidates = []
                    for word, pos in candidates:
                        score = 1.0
                        if theme_word and theme_word.lower() in self.w2v_model.wv:
                            w_lower = word.lower()
                            if w_lower in self.w2v_model.wv:
                                score += self.w2v_model.wv.similarity(w_lower, theme_word.lower()) * 3.0
                        scored_candidates.append((word, score))
                        
                    scored_candidates.sort(key=lambda x: x[1], reverse=True)
                    best_pool = scored_candidates[:max(1, len(scored_candidates)//2)]
                    chosen_word = random.choice(best_pool)[0]

                    line_words.insert(0, chosen_word)

                    doc_word = nlp(chosen_word)
                    current_rev_state = (doc_word[0].lemma_,) + current_rev_state[:-1]
            else:
                for i in range(words_per_line - 1):
                    line_words.insert(0, random.choice(list(self.corpus_vocab)))

            # Punctuation/Capitalization Format
            formatted_line = []
            capitalize_next = False
            for w in line_words:
                if not formatted_line and re.match(r'^[.,!?;:]+$', w):
                    continue
                if not formatted_line or capitalize_next:
                    w = w.capitalize()
                    capitalize_next = False
                
                if re.match(r'^[.,!?;:]+$', w) and formatted_line:
                    formatted_line[-1] += w
                    if re.search(r'[.!?;]$', w):
                        capitalize_next = True
                    continue
                
                formatted_line.append(w)
            
            lines.append(" ".join(formatted_line))

        return "\n".join(lines).strip()

    def generate_rhythmic_poem(self, rhythm_template="0101010101", lines_count=4, theme_word=None):
        """
        Generates a poem enforcing a strict syllabic rhythm template.
        """
        if not self.chain:
            return "Corpus too small or not analyzed."

        poem_lines = []

        for _ in range(lines_count):
            current_target = rhythm_template
            current_lemmas = list(random.choice(list(self.chain.keys())))
            
            line_words = []
            
            while current_target:
                state = tuple(current_lemmas)
                candidates = self.chain.get(state, [])

                valid_candidates = []
                for word, pos in candidates:
                    stress = self.get_word_stress(word)
                    if stress == "":
                        continue
                        
                    if current_target.startswith(stress):
                        valid_candidates.append((word, stress))
                
                if valid_candidates:
                    chosen_word, chosen_stress = random.choice(valid_candidates)
                    
                    line_words.append(chosen_word)
                    current_target = current_target[len(chosen_stress):]
                    doc_word = nlp(chosen_word)
                    current_lemmas = (current_lemmas + [doc_word[0].lemma_])[1:]
                else:
                    # Semantic Fallback
                    fallback_pool = []
                    for v in self.corpus_vocab:
                        stress = self.get_word_stress(v)
                        if stress and current_target.startswith(stress):
                            fallback_pool.append((v, stress))
                            
                    if fallback_pool:
                        chosen_word, chosen_stress = random.choice(fallback_pool)
                        line_words.append(chosen_word)
                        current_target = current_target[len(chosen_stress):]
                        doc_word = nlp(chosen_word)
                        current_lemmas = (current_lemmas + [doc_word[0].lemma_])[1:]
                    else:
                        break # Unrecoverable dead end

            formatted_line = []
            capitalize_next = False
            for w in line_words:
                if not formatted_line and re.match(r'^[.,!?;:]+$', w):
                    continue
                if not formatted_line or capitalize_next:
                    w = w.capitalize()
                    capitalize_next = False
                
                if re.match(r'^[.,!?;:]+$', w) and formatted_line:
                    formatted_line[-1] += w
                    if re.search(r'[.!?;]$', w):
                        capitalize_next = True
                    continue
                
                formatted_line.append(w)
            
            poem_lines.append(" ".join(formatted_line))

        return "\n".join(poem_lines).strip()