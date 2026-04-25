import random
import re
import pronouncing
from backhand.utils.nlp_helpers import nlp, get_synonym, train_word2vec


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
        self.chains_by_order = {}  # Variable-Order Markov Chain (VOMC)
        self.pos_map = {}
        self.w2v_model = None
        self.corpus_vocab = set()
        self.word_graph = {}  # Relational Graph (Word -> Word -> Weight)
        self.thematic_reservoir = []  # Long-range coherence memory
        self.lemma_cache = {}  # Fast lemma lookup (avoids calling nlp() per word)

        self._analyze_corpus()
        self._train_embeddings()
        self._build_relational_graph()

        # Era Stickiness: Mark Archaic/Historical language
        self.ARCHAIC_MARKERS = {
            'thou', 'thee', 'thy', 'thine', 'hath', 'doth', 'hast', 'ye', 'shalt', 'art',
            'noght', 'togedre', 'moe', 'fairest', 'dost', 'wast', 'wert', 'ay', 'nay',
            'spede', 'tresoun', 'togedre', 'amonte', 'noght'
        }

    def _is_archaic(self, word):
        w = word.lower()
        if w in self.ARCHAIC_MARKERS: return True
        # Common historical endings
        if len(w) > 4:
            if w.endswith('eth') or w.endswith('est'): return True
        return False

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
            # Cache lemma for fast lookup later
            self.lemma_cache[word_lower] = next_token.lemma_

        # --- Variable-Order Markov Chains (VOMC) ---
        print("Building Variable-Order Chains (1-gram, 2-gram, 3-gram)...")
        for n in range(1, 4):  # Build chains of order 1, 2, 3
            vomc = {}
            for i in range(len(self.tokens) - n):
                state = tuple(t.lemma_ for t in self.tokens[i:i+n])
                next_tok = self.tokens[i + n]
                if state not in vomc:
                    vomc[state] = []
                vomc[state].append((next_tok.text, next_tok.pos_))
            self.chains_by_order[n] = vomc

    def _build_relational_graph(self):
        """
        Builds a Relational Word Graph where edge weights are conditioned on 
        Semantic Similarity (GMNN-inspired Feature-dependent adjacency).
        """
        print("Building Semantic Relational Word Graph...")
        doc = nlp(self.corpus_text)
        
        for sentence in doc.sents:
            sent_words = [t.text.lower() for t in sentence if not t.is_punct and not t.is_space]
            for i, w1 in enumerate(sent_words):
                if w1 not in self.word_graph:
                    self.word_graph[w1] = {}
                for w2 in sent_words[i+1:]:
                    # GMNN: The weight isn't just +1, it's (1 + similarity)
                    sim_bonus = 0.0
                    if self.w2v_model and w1 in self.w2v_model.wv and w2 in self.w2v_model.wv:
                        sim_bonus = self.w2v_model.wv.similarity(w1, w2)
                    
                    weight_increment = 1.0 + sim_bonus
                    
                    if w2 not in self.word_graph[w1]:
                        self.word_graph[w1][w2] = 0
                    self.word_graph[w1][w2] += weight_increment
                    
                    # Undirected
                    if w2 not in self.word_graph:
                        self.word_graph[w2] = {}
                    if w1 not in self.word_graph[w2]:
                        self.word_graph[w2][w1] = 0
                    self.word_graph[w2][w1] += weight_increment

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

    def get_graph_relational_score(self, word, history_lowers):
        """
        Calculates how strongly a word is connected to the previous words in the poem 
        using the Global Word Graph. Optimized to accept pre-lowercased history.
        """
        if not history_lowers:
            return 0.0
            
        w_lower = word.lower()
        if w_lower not in self.word_graph:
            return 0.0
            
        total_weight = 0
        connections = self.word_graph[w_lower]
        
        for hist_lower in history_lowers:
            if hist_lower in connections:
                total_weight += connections[hist_lower]
                
        return total_weight / len(history_lowers)

    def _get_candidates_vomc(self, lemmas):
        """
        Variable-Order Markov Chain lookup.
        Tries order 3 first, falls back to 2, then 1.
        Returns (candidates, order_used).
        """
        for n in [3, 2, 1]:
            if n > len(lemmas):
                continue
            state = tuple(lemmas[-n:])
            chain = self.chains_by_order.get(n, {})
            candidates = chain.get(state, [])
            if candidates:
                return candidates, n
        return [], 0

    def _fast_lemma(self, word):
        """Fast lemma lookup using pre-built cache. Falls back to lowercase."""
        return self.lemma_cache.get(word.lower(), word.lower())

    def beam_search_generate(self, length=40, beam_width=3, theme_word=None):
        """
        Generates a poem using Beam Search with:
        - Variable-Order Markov Chain (VOMC) for adaptive context
        - Graph Relational scoring for global coherence
        - Thematic Reservoir for long-range memory
        """
        if not self.chain:
            return []

        # Reset thematic reservoir for this generation
        self.thematic_reservoir = []

        # Initial candidates: Top states from the Markov chain
        initial_states = random.sample(list(self.chain.keys()), min(beam_width, len(self.chain)))
        
        # Beam structure: (total_score, [words], current_lemmas)
        beam = []
        for state in initial_states:
            beam.append((0.0, list(state), list(state)))

        pos_sequence = ["NOUN", "VERB", "ADJ", "NOUN", "ADP", "DET", "NOUN"]

        for i in range(length):
            new_beam = []
            
            for score, words, lemmas in beam:
                # VOMC: Try trigram -> bigram -> unigram adaptively
                candidates, order_used = self._get_candidates_vomc(lemmas)
                
                if not candidates:
                    # Dead end: random jump with heavy penalty
                    jump_state = random.choice(list(self.chain.keys()))
                    new_beam.append((score - 10.0, words, list(jump_state)))
                    continue

                # Pre-calculate lowercased history for graph efficiency
                history_lowers = [w.lower() for w in words[-5:]]
                res_lowers = [w.lower() for w in self.thematic_reservoir[-10:]]

                # Bonus for higher-order matches (more context = more stable)
                order_bonus = order_used * 0.5

                ideal_pos = pos_sequence[i % len(pos_sequence)]
                
                # Pre-score all candidates, then only expand the top 2
                pre_scored = []
                for word, pos in candidates:
                    word_score = 1.0 + order_bonus
                    
                    if pos == ideal_pos:
                        word_score += 2.0
                    
                    if theme_word and theme_word.lower() in self.w2v_model.wv:
                        w_lower = word.lower()
                        if w_lower in self.w2v_model.wv:
                            word_score += self.w2v_model.wv.similarity(w_lower, theme_word.lower()) * 3.0
                    
                    graph_affinity = self.get_graph_relational_score(word, history_lowers)
                    word_score += graph_affinity * 2.0

                    if self.thematic_reservoir:
                        reservoir_affinity = self.get_graph_relational_score(word, res_lowers)
                        word_score += reservoir_affinity * 1.5
                    
                    if word.lower() in [w.lower() for w in words[-3:]]:
                        word_score -= 5.0

                    # Era Consistency Scoring (Style Stickiness)
                    # Look at the previous 8 words to see if we've committed to a style
                    is_archaic_history = any(self._is_archaic(w) for w in words[-8:])
                    is_archaic_cand = self._is_archaic(word)
                    
                    if is_archaic_history:
                        if is_archaic_cand: word_score += 10.0 # Reinforce Era consistency
                        else: word_score -= 15.0 # Penalize jumping to modern mid-stanza
                    else:
                        if is_archaic_cand: word_score -= 15.0 # Keep it modern by default
                        else: word_score += 5.0
                    
                    pre_scored.append((word, word_score))
                
                # Only expand the top 2 candidates (prevents exponential blowup)
                pre_scored.sort(key=lambda x: x[1], reverse=True)
                top_candidates = pre_scored[:2]
                
                for word, word_score in top_candidates:
                    new_score = score + word_score
                    new_words = words + [word]
                    
                    new_lemma = self._fast_lemma(word)
                    new_lemmas = (lemmas + [new_lemma])[1:]
                    
                    new_beam.append((new_score, new_words, new_lemmas))
            
            # Prune beam to keep only top paths
            new_beam.sort(key=lambda x: x[0], reverse=True)
            beam = new_beam[:beam_width]

            # Feed the thematic reservoir with the best beam's latest word
            if beam and len(beam[0][1]) > 0:
                latest_word = beam[0][1][-1]
                if not re.match(r'^[.,!?;:]+$', latest_word):
                    self.thematic_reservoir.append(latest_word)

        # Return best path words
        return beam[0][1] if beam else []

    def refine_poem_relational(self, poem_words, passes=1):
        """
        Refines a poem using an Iterative M-Step (GMNN Refinement).
        Tries to swap words for neighbors with higher global relational energy.
        """
        refined = list(poem_words)
        
        for p in range(passes):
            for i in range(len(refined)):
                current_word = refined[i]
                if re.match(r'^[.,!?;:]+$', current_word): continue
                
                # Context words (neighbors in the poem)
                context = refined[max(0, i-5):i] + refined[i+1:i+6]
                current_score = self.get_graph_relational_score(current_word, [w.lower() for w in context])
                
                # Look for better relational candidates with same POS
                current_pos = list(self.pos_map.get(current_word.lower(), ["NOUN"]))[0]
                candidates, _ = self._get_candidates_vomc(self._fast_lemma(refined[max(0, i-1)])) # fallback candidates
                
                best_w = current_word
                best_s = current_score
                
                for cand_w, cand_p in candidates[:10]:
                    if cand_p == current_pos:
                        cand_s = self.get_graph_relational_score(cand_w, [w.lower() for w in context])
                        if cand_s > best_s:
                            best_s = cand_s
                            best_w = cand_w
                
                refined[i] = best_w
                
        return refined

    def generate_poem(self, length=40, theme_word=None, strategy="constrained"):
        """
        Main entry point for Constrained Markov Process generation.
        """
        if strategy == "constrained":
            return self.generate_constrained_poem(length=length, theme_word=theme_word)
        else:
            words = self.beam_search_generate(length=length, theme_word=theme_word)
            return format_poem(words)

    def generate_constrained_poem(self, length=40, theme_word=None, rhyme_scheme="AABB"):
        """
        Generates a poem where each line is solved as a constraint satisfaction problem.
        """
        stanza_count = (length // 24) + 1
        full_poem_words = []
        
        # We solve the poem in quatrains (4 lines)
        for _ in range(stanza_count):
            quatrain_lines = self.generate_quatrain_cmp(rhyme_scheme, theme_word)
            for line in quatrain_lines:
                full_poem_words.extend(line.split())
            if len(full_poem_words) >= length: break
            
        return format_poem(full_poem_words)

    def generate_quatrain_cmp(self, scheme, theme_word):
        """
        CMP Quatrain Solver: Uses backtracking/search to find lines that rhyme.
        """
        lines = [None] * 4
        rhymes_needed = {} 
        
        for i, char in enumerate(scheme):
            target_rhyme = rhymes_needed.get(char)
            line = self.solve_line_constraints(target_rhyme, theme_word)
            
            if char not in rhymes_needed:
                rhymes_needed[char] = self._get_rhyme_part(line.split()[-1])
            
            lines[i] = line
            
        return lines

    def solve_line_constraints(self, target_rhyme, theme_word, max_attempts=5):
        """
        The core CMP Solver: Generates a line that satisfies the rhyme constraint.
        """
        for _ in range(max_attempts):
            # Beam search with constraint filtering
            line_tokens = self.beam_search_generate_constrained(target_rhyme, theme_word)
            if line_tokens:
                return " ".join(line_tokens)
        
        # Fallback
        return " ".join(self.beam_search_generate(length=6, theme_word=theme_word)[:6])

    def beam_search_generate_constrained(self, target_rhyme, theme_word, beam_width=3, max_tokens=7):
        """
        Beam Search specialized for CMP: Penalizes paths that don't reach a rhyme.
        """
        import pronouncing
        states = list(self.chain.keys())
        seed = random.choice(states)
        beam = [(0.0, list(seed), list(seed))]

        for i in range(max_tokens - self.order):
            new_beam = []
            for score, words, lemmas in beam:
                # Use standard VOMC candidates
                candidates, _ = self._get_candidates_vomc(lemmas[-1])
                
                is_final_word = (i == max_tokens - self.order - 1)
                
                for word, pos in candidates[:10]:
                    word_score = 5.0
                    
                    # Constraint Verification
                    if target_rhyme and is_final_word:
                        if self._get_rhyme_part(word) == target_rhyme:
                            word_score += 100.0 # Match!
                        else:
                            word_score -= 80.0 # Violation
                    
                    new_words = words + [word]
                    new_lemmas = (lemmas + [self._fast_lemma(word)])[1:]
                    new_beam.append((score + word_score, new_words, new_lemmas))
            
            new_beam.sort(key=lambda x: x[0], reverse=True)
            beam = new_beam[:beam_width]

        return beam[0][1]

    def _get_rhyme_part(self, word):
        import pronouncing
        phones = pronouncing.phones_for_word(word)
        if not phones: return None
        return pronouncing.rhyming_part(phones[0])

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
            target_lemma = self._fast_lemma(target_word)

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

                    # Score candidates based on semantic bias and Graph Relational coherence
                    scored_candidates = []
                    for word, pos in candidates:
                        score = 1.0
                        if theme_word and theme_word.lower() in self.w2v_model.wv:
                            w_lower = word.lower()
                            if w_lower in self.w2v_model.wv:
                                score += self.w2v_model.wv.similarity(w_lower, theme_word.lower()) * 3.0
                        
                        # Graph Relational bias
                        graph_affinity = self.get_graph_relational_score(word, line_words)
                        score += graph_affinity * 2.5 # Slightly higher weight for rhymed coherence
                        
                        scored_candidates.append((word, score))
                        
                    scored_candidates.sort(key=lambda x: x[1], reverse=True)
                    best_pool = scored_candidates[:max(1, len(scored_candidates)//2)]
                    chosen_word = random.choice(best_pool)[0]

                    line_words.insert(0, chosen_word)

                    current_rev_state = (self._fast_lemma(chosen_word),) + current_rev_state[:-1]
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

                # Score candidates based on semantic bias and Graph Coherence
                scored_candidates = []
                for word, pos in candidates:
                    score = 1.0
                    
                    stress = self.get_word_stress(word)
                    if stress == "" or not current_target.startswith(stress):
                        continue

                    # Semantic bias
                    if theme_word and theme_word.lower() in self.w2v_model.wv:
                        w_lower = word.lower()
                        if w_lower in self.w2v_model.wv:
                            score += self.w2v_model.wv.similarity(w_lower, theme_word.lower()) * 3.0
                    
                    # Graph Relational bias
                    graph_affinity = self.get_graph_relational_score(word, line_words)
                    score += graph_affinity * 2.0
                    
                    scored_candidates.append((word, score, stress))
                    
                if scored_candidates:
                    scored_candidates.sort(key=lambda x: x[1], reverse=True)
                    best_pool = scored_candidates[:max(1, len(scored_candidates)//2)]
                    chosen_word, _, chosen_stress = random.choice(best_pool)
                    
                    line_words.append(chosen_word)
                    current_target = current_target[len(chosen_stress):]
                    current_lemmas = (current_lemmas + [self._fast_lemma(chosen_word)])[1:]
                else:
                    # Semantic Fallback with Graph checking
                    fallback_pool = []
                    for v in self.corpus_vocab:
                        stress = self.get_word_stress(v)
                        if stress and current_target.startswith(stress):
                            g_score = self.get_graph_relational_score(v, line_words)
                            fallback_pool.append((v, stress, g_score))
                            
                    if fallback_pool:
                        fallback_pool.sort(key=lambda x: x[2], reverse=True)
                        chosen_word, chosen_stress, _ = fallback_pool[0]
                        line_words.append(chosen_word)
                        current_target = current_target[len(chosen_stress):]
                        current_lemmas = (current_lemmas + [self._fast_lemma(chosen_word)])[1:]
                    else:
                        break

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