import random
from collections import defaultdict
from ..utils.nlp_helpers import get_meter_profile, check_rhyme_manual

class MarkovPoetryModel:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(list)
        self.start_words = []

    def train(self, corpus_text):
        """
        Makalede Dylan korpusunda yapıldığı gibi n-gram RF (Relative Frequency) çıkarır[cite: 61, 185].
        """
        lines = corpus_text.split('\n')
        for line in lines:
            words = line.split()
            if len(words) < self.order: continue
            
            self.start_words.append(tuple(words[:self.order]))
            for i in range(len(words) - self.order):
                key = tuple(words[i:i+self.order])
                next_word = words[i+self.order]
                self.model[key].append(next_word)

    def generate_line(self, rhyme_with=None, seed=None, target_len=7):
        # Makaledeki gibi 2. dereceden başlangıç [cite: 185]
        current = random.choice(self.start_words)
        result = list(current)
        
        # Eğer seed word varsa ve dizede yoksa dizeye dahil et [cite: 193]
        if seed and seed.lower() not in [w.lower() for w in result]:
            result.insert(random.randint(0, len(result)), seed)

        for i in range(target_len - len(result)):
            key = tuple(result[-2:])
            possible_next = self.model.get(key, [])
            if not possible_next: break
            
            # Kafiye kısıtı (Unary Constraint) [cite: 121, 127]
            if i == (target_len - len(result) - 1) and rhyme_with:
                valid_rhymes = [w for w in possible_next if check_rhyme_manual(w, rhyme_with)]
                next_word = random.choice(valid_rhymes) if valid_rhymes else random.choice(possible_next)
            else:
                next_word = random.choice(possible_next)
                
            result.append(next_word)
            
        return " ".join(result)