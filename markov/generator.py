import random
import collections

class MarkovGenerator:
    def __init__(self, file_path, order=2):
        self.order = order
        self.model = collections.defaultdict(list)
        self.train(file_path)

    def train(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().split()
        for i in range(len(text) - self.order):
            state = tuple(text[i:i + self.order])
            next_word = text[i + self.order].strip('.,!?"()').lower()
            self.model[state].append(next_word)

    def get_rhyming_words(self, target_word):
        # Basit kafiye kısıtlaması (Unary Constraint)
        suffix = target_word[-2:]
        all_words = list(set([w for words in self.model.values() for w in words]))
        return [w for w in all_words if w.endswith(suffix) and w != target_word]

    def generate_verse(self, length=7, rhyme_with=None):
        attempts = 0
        while attempts < 30:
            state = random.choice(list(self.model.keys()))
            verse = list(state)
            for _ in range(length - self.order):
                next_options = self.model.get(state)
                if not next_options: break
                
                # Son kelimede kafiye kısıtlamasını kontrol et
                if _ == (length - self.order - 1) and rhyme_with:
                    rhymes = self.get_rhyming_words(rhyme_with)
                    valid = [w for w in next_options if w in rhymes]
                    if not valid: break
                    next_word = random.choice(valid)
                else:
                    next_word = random.choice(next_options)
                
                verse.append(next_word)
                state = tuple(verse[-self.order:])
            
            if len(verse) == length:
                return " ".join(verse).capitalize()
            attempts += 1
        return "Line could not be generated."

    def generate_stanza(self):
        # ABAB Kafiye Düzeni
        v1 = self.generate_verse()
        v2 = self.generate_verse()
        v3 = self.generate_verse(rhyme_with=v1.split()[-1])
        v4 = self.generate_verse(rhyme_with=v2.split()[-1])
        return [v1, v2, v3, v4]

    def generate_full_lyrics(self):
        # Verse 1 - Chorus - Verse 2 yapısında tam şarkı
        lyrics = {"Verse 1": self.generate_stanza(), 
                  "Chorus": self.generate_stanza(), 
                  "Verse 2": self.generate_stanza()}
        return lyrics