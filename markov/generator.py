import random
import collections
import re

class MarkovGenerator:
    def __init__(self, file_path, order=3):
        self.order = order
        self.vocab = collections.Counter()
        self.forward_model = collections.defaultdict(lambda: collections.defaultdict(int))
        self.backward_model = collections.defaultdict(lambda: collections.defaultdict(int))
        self.start_states = []
        self.end_states = []
        
        if file_path:
            self.train(file_path)

    def train(self, file_path):
        """Builds both forward and backward graphs for bidirectional generation with filtering"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except FileNotFoundError:
            return

        # Filtering logic: identify 'love' themed poetic lines
        love_keywords = {"love", "heart", "soul", "kiss", "darling", "sweet", "rose", "night", "moon", "dear", "beauty", "light"}
        
        lines = raw_text.split('\n')
        filtered_text = []
        
        for line in lines:
            clean_line = re.sub(r'[^a-zA-Z\s]', '', line).lower().strip()
            if not clean_line: continue
            
            tokens = clean_line.split()
            if any(word in tokens for word in love_keywords):
                filtered_text.append(tokens)
        
        # Build model from filtered lines
        for tokens in filtered_text:
            if len(tokens) < self.order: continue
            
            self.start_states.append(tuple(tokens[:self.order-1]))
            self.end_states.append(tuple(tokens[-(self.order-1):]))
            
            for t in tokens:
                self.vocab[t] += 1
                
            for i in range(len(tokens) - (self.order - 1)):
                state = tuple(tokens[i : i + self.order - 1])
                next_word = tokens[i + self.order - 1]
                self.forward_model[state][next_word] += 1
                
            rev_tokens = tokens[::-1]
            for i in range(len(rev_tokens) - (self.order - 1)):
                state = tuple(rev_tokens[i : i + self.order - 1])
                next_word = rev_tokens[i + self.order - 1]
                self.backward_model[state][next_word] += 1

    def get_popular_words(self, top_n=25):
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "is", "was", "of", "my", "you", "i"}
        filtered = {w: c for w, c in self.vocab.items() if w not in stop_words and len(w) > 2}
        return sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_rhyming_words(self, target_word):
        suffix = target_word[-2:].lower()
        all_words = [w for w in self.vocab.keys() if len(w) > 3]
        return [w for w in all_words if w.endswith(suffix) and w != target_word.lower()]

    def generate_line(self, length=7, seed_word=None, reverse=False):
        """Generates a line. seed_word can be a single word or multiple space-separated words"""
        model = self.backward_model if reverse else self.forward_model
        
        # Extract all valid seeds
        seeds = []
        if seed_word:
            potential_seeds = seed_word.lower().split() if isinstance(seed_word, str) else seed_word
            seeds = [s for s in potential_seeds if s in self.vocab]
        
        current_state = None
        if seeds:
            # Shuffle seeds to pick a random one that has a valid state
            random.shuffle(seeds)
            for seed in seeds:
                possible_starts = [s for s in model.keys() if seed in s]
                if possible_starts:
                    current_state = random.choice(possible_starts)
                    break
        
        if not current_state:
            current_state = random.choice(self.end_states if reverse else self.start_states)
            
        line = list(current_state)
        
        for _ in range(length - (self.order - 1)):
            candidates = model.get(current_state)
            if not candidates: break
                
            words = list(candidates.keys())
            weights = list(candidates.values())
            next_word = random.choices(words, weights=weights)[0]
            
            line.append(next_word)
            current_state = tuple(line[-(self.order-1):])
            
        result = " ".join(line[::-1]) if reverse else " ".join(line)
        return result.capitalize()

    def generate_stanza(self, seed_word=None):
        v1 = self.generate_line(seed_word=seed_word)
        last_word = v1.split()[-1]
        
        rhymes = self.get_rhyming_words(last_word)
        rhyme_word = random.choice(rhymes) if rhymes else None
        
        v2 = self.generate_line(seed_word=rhyme_word, reverse=True)
        return [v1, v2]

    def generate_full_lyrics(self, seed_word=None):
        lyrics = {
            "Verse 1": self.generate_stanza(seed_word),
            "Chorus": self.generate_stanza(seed_word),
            "Verse 2": self.generate_stanza(seed_word)
        }
        return lyrics