"""
PoetryAPI class that manages both Markov and CRPO models.
It handles data loading, model initialization, and poem generation logic.
"""
import os
import re
import random
import numpy as np
import tensorflow as tf
import pronouncing
from .models.crpo_model import CRPOModel
from .utils.nlp_helpers import get_crpo_clean_corpus
from .models.markov_model import MarkovPoetryModel

class PoetryAPI:
    def __init__(self, weights_path='crpo_weights.weights.h5', limit=20000):
        # Prepares the corpus and initializes both generation engines
        self.corpus = get_crpo_clean_corpus(limit=limit) 
        self.markov_engine = MarkovPoetryModel(order=2) 
        self.markov_engine.train(self.corpus) 
        
        chars = sorted(list(set(self.corpus)))
        self.char_to_int = {c: i for i, c in enumerate(chars)}
        self.int_to_char = {i: c for i, c in enumerate(chars)}
        self.vocab_size = len(chars)
        self.crpo_wrapper = CRPOModel(vocab_size=self.vocab_size, seq_length=40)
        self.crpo_model = self.crpo_wrapper.model
        if os.path.exists(weights_path):
            self.crpo_model.load_weights(weights_path)

    def sample_with_temperature(self, preds, temperature=0.4):
        # Adds randomness to character selection based on a temperature value
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds + 1e-7) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        return np.argmax(np.random.multinomial(1, preds, 1))

    def _clean_line(self, line):
        # Removes unwanted characters and fixes formatting of the generated lines
        if not line: return None
        line = re.sub(r'[()\[\]{}\"\'`]', '', line)
        line = re.sub(r'([.,!?;:])(?=[^\s])', r'\1 ', line)
        line = re.sub(r'[.,!?;:]{2,}', '.', line)
        line = re.sub(r'\s+', ' ', line).strip()
        line = line.strip(',').strip()
        words = line.split()
        if len(words) < 3: return None

        allowed_shorts = ['me', 'be', 'is', 'he', 'we', 'to', 'in', 'it', 'my', 'so', 'as']
        if len(words[-1]) < 3 and words[-1].lower() not in allowed_shorts:
            words.pop()
            line = " ".join(words)

        invalid_ends = ['the', 'and', 'a', 'of', 'with', 'to', 'in', 'is', 'at', 'by', 'for']
        if words and words[-1].lower() in invalid_ends:
            return None 

        return line if len(line) > 10 else None

    def generate_crpo_poem(self, line_count, seed_word=""):
        # Creates a poem using the CRPO model with rhyming patterns
        scheme = ['A' if i % 2 == 0 else 'B' for i in range(line_count)]
        target_len = 45 
        poem = []
        rhyme_storage = {} 
        line_idx = 0
        max_attempts = line_count * 5 
        attempts = 0

        while len(poem) < line_count and attempts < max_attempts:
            attempts += 1
            current_scheme = scheme[line_idx]
            target_rhyme_word = rhyme_storage.get(current_scheme)
            line = self._generate_line(target_len, rhyme_with=target_rhyme_word)
            
            if line_idx == 0 and seed_word:
                words = line.split()
                if seed_word.lower() not in line.lower():
                    insert_pos = random.randint(0, len(words))
                    words.insert(insert_pos, seed_word)
                    line = " ".join(words)

            cleaned = self._clean_line(line)
            if cleaned:
                last_word = cleaned.split()[-1].strip(".,!?;").lower()
                if current_scheme not in rhyme_storage:
                    rhyme_storage[current_scheme] = last_word
                poem.append(cleaned.capitalize())
                line_idx += 1
        return poem

    def _generate_line(self, target_len, rhyme_with=None):
        # Internal function to build a single line character by character
        context = "the silent world of nature and spirits ".rjust(40)[-40:]
        line = ""
        for _ in range(int(target_len * 0.7)):
            char = self._predict(context, forbidden=['\n', '\r', '"', "'", '`'])
            line += char
            context = (context + char)[-40:]

        if rhyme_with:
            rhymes = pronouncing.rhymes(rhyme_with)
            valid_rhymes = [r for r in rhymes if len(r) > 2 and r.isalpha()]
            if valid_rhymes:
                rhyme_word = random.choice(valid_rhymes[:15])
                if ' ' in line:
                    line = line.rsplit(' ', 1)[0]
                return line + " " + rhyme_word + "."

        for _ in range(25):
            char = self._predict(context, forbidden=['"', "'", '`'])
            line += char
            if char in [' ', '.', '!', '?']: break
            context = (context + char)[-40:]
        return line

    def generate_markov_poem(self, line_count, seed_word=""):
        # Creates a poem with A-A or A-A-B-A schemes using the Markov engine
        poem = []
        rhyme_storage = {}
        
        # Eğer line_count 4 ise A-A-B-A, değilse (2 ise) A-A şeması uygula
        if line_count == 4:
            scheme = ['A', 'A', 'B', 'A']
        else:
            scheme = ['A', 'A']
            
        line_idx = 0
        max_attempts = line_count * 5
        attempts = 0

        # len(poem) < line_count kontrolü burada kritik, 
        # line_count kaç gelirse o kadar satırda durur.
        while len(poem) < line_count and attempts < max_attempts:
            attempts += 1
            # Şema indexini döngüsel olarak al (A, A, B, A, A, A...)
            current_scheme = scheme[line_idx % len(scheme)]
            target_rhyme = rhyme_storage.get(current_scheme)
            
            line = self.markov_engine.generate_line_backwards(
                rhyme_with=target_rhyme, 
                target_len=random.randint(5, 8)
            )
            
            cleaned = self._clean_line(line)
            if cleaned:
                last_word = cleaned.split()[-1].strip(".,!?;").lower()
                if current_scheme not in rhyme_storage:
                    rhyme_storage[current_scheme] = last_word
                    
                poem.append(cleaned.capitalize())
                line_idx += 1
                
        return poem

    def _predict(self, context, forbidden=None):
        # Uses the CRPO neural network to predict the next character
        if forbidden is None:
            forbidden = []
        
        forbidden.extend(['(', ')', '[', ']', '{', '}', '"', "'", '`'])
        
        if context[-1] in ".,!?;:":
            forbidden.extend([".", ",", "!", "?", ";", ":"])

        x = np.zeros((1, 40))
        for t, char in enumerate(context[-40:]):
            x[0, t] = self.char_to_int.get(char, 0)
        
        preds = self.crpo_model.predict(x, verbose=0)[0]
        
        if forbidden:
            for f_char in forbidden:
                if f_char in self.char_to_int:
                    preds[self.char_to_int[f_char]] = 0
            if np.sum(preds) > 0:
                preds = preds / np.sum(preds)
        
        return self.int_to_char[self.sample_with_temperature(preds)]