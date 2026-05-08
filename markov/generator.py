import random
import collections
import re
import pronouncing

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
        love_keywords = {"love", "heart", "soul", "kiss", "darling", "sweet", "rose", "night", "moon", "dear", "beauty", "light", "dream", "star", "fire", "ice", "sea"}
        
        lines = raw_text.split('\n')
        filtered_text = []
        
        for line in lines:
            clean_line = re.sub(r'[^a-zA-Z\s]', '', line).lower().strip()
            if not clean_line: continue
            
            tokens = clean_line.split()
            if len(tokens) >= 3 and (any(word in tokens for word in love_keywords) or len(tokens) < 10):
                filtered_text.append(tokens)
        
        # Build model from filtered lines
        for tokens in filtered_text:
            if len(tokens) < self.order: continue
            
            self.start_states.append(tuple(tokens[:self.order-1]))
            self.end_states.append(tuple(tokens[::-1][:self.order-1]))
            
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
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "is", "was", "of", "my", "you", "i", "it", "that", "this"}
        filtered = {w: c for w, c in self.vocab.items() if w not in stop_words and len(w) > 2}
        return sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_rhyming_words(self, target_word):
        target_word = target_word.lower()
        rhymes = pronouncing.rhymes(target_word)
        valid_rhymes = [w for w in rhymes if w in self.vocab]
        if not valid_rhymes:
            suffix = target_word[-2:]
            valid_rhymes = [w for w in self.vocab.keys() if w.endswith(suffix) and len(w) > 3 and w != target_word]
        return valid_rhymes

    def generate_line(self, length=7, seed_word=None, reverse=False):
        model = self.backward_model if reverse else self.forward_model
        
        seeds = []
        if seed_word:
            seeds = [s.strip().lower() for s in seed_word.split() if s.strip().lower() in self.vocab]
            
        current_state = None
        if seeds:
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
        used = set()
        v1 = self.generate_line(seed_word=seed_word)
        used.add(v1)
        
        last_word = v1.split()[-1]
        rhymes = self.get_rhyming_words(last_word)
        
        v2 = "Line could not be generated."
        for _ in range(10):
            rhyme_word = random.choice(rhymes) if rhymes else None
            cand = self.generate_line(seed_word=rhyme_word, reverse=True)
            if cand not in used:
                v2 = cand
                break
        return [v1, v2]

    def generate_full_lyrics(self, seed_word=None):
        sections = ["Verse 1", "Chorus", "Verse 2"]
        lyrics = {}
        overall_used = set()
        for section in sections:
            lines = []
            s = self.generate_stanza(seed_word)
            for line in s:
                if line in overall_used:
                    line = self.generate_line()
                lines.append(line)
                overall_used.add(line)
            lyrics[section] = lines
        return lyrics