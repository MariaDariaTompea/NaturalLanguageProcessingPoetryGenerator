"""
Markov Chain model for generating poetry with rhyme constraints.
This model uses backward generation to ensure lines end with the correct rhyme.
"""
import random
from collections import defaultdict
import pronouncing
from ..utils.nlp_helpers import check_rhyme_manual

class MarkovPoetryModel:
    def __init__(self, order=2):
        # Initializes the model with n-gram order and dictionaries
        self.order = order
        self.forward_model = defaultdict(list)
        self.backward_model = defaultdict(list)
        self.line_ends = []

    def train(self, corpus_text):
        # Processes the corpus to create backward transitions and collect rhyme words
        lines = corpus_text.split('\n')
        for line in lines:
            words = line.split()
            if len(words) < self.order: continue
            
            self.line_ends.append(words[-1])
            rev_words = words[::-1]
            for i in range(len(rev_words) - self.order):
                key = tuple(rev_words[i:i+self.order])
                next_word = rev_words[i+self.order]
                self.backward_model[key].append(next_word)

    def generate_line_backwards(self, rhyme_with=None, target_len=6):
        # Generates a poem line starting from the last word (rhyme) to the beginning
        if rhyme_with:
            options = [w for w in self.line_ends if check_rhyme_manual(w, rhyme_with)]
            if not options:
                options = pronouncing.rhymes(rhyme_with)
            current_word = random.choice(options) if options else random.choice(self.line_ends)
        else:
            current_word = random.choice(self.line_ends)

        result = [current_word]
        possible_seconds = [key[1] for key in self.backward_model.keys() if key[0] == current_word]
        if not possible_seconds: return current_word
        
        result.append(random.choice(possible_seconds))

        for i in range(target_len - 2):
            key = tuple(result[-2:])
            possible_next = self.backward_model.get(key, [])
            if not possible_next: break
            result.append(random.choice(possible_next))

        return " ".join(result[::-1])