import os
import numpy as np
import tensorflow as tf
from .models.crpo_model import CRPOModel
from .utils.nlp_helpers import get_crpo_clean_corpus, prepare_data

class PoetryAPI:
    def __init__(self, weights_path='crpo_weights.weights.h5', limit=50000):
        corpus = get_crpo_clean_corpus(limit=limit) 
        chars = sorted(list(set(corpus)))
        self.char_to_int = {c: i for i, c in enumerate(chars)}
        self.int_to_char = {i: c for i, c in enumerate(chars)}
        self.vocab_size = len(chars)
        self.crpo_wrapper = CRPOModel(vocab_size=self.vocab_size, seq_length=40)
        self.crpo_model = self.crpo_wrapper.model
        if os.path.exists(weights_path):
            self.crpo_model.load_weights(weights_path)

    def sample_with_temperature(self, preds, temperature=0.4):
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds + 1e-7) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        return np.argmax(np.random.multinomial(1, preds, 1))

    def generate_crpo_poem(self, poetic_form, seed_word=""):
        """seed_word parametresi eklenerek TypeError hatası giderildi."""
        forms = {'quatrain': (4, 48), 'haiku': (3, 20), 'sonnet': (14, 48)}
        num_lines, target_len = forms.get(poetic_form, (4, 48))
        
        # Seçilen kelimeyi bağlama (context) yediriyoruz
        base_text = f"the beauty of {seed_word.lower()} " if seed_word else "the silent world "
        context = base_text.rjust(40)[-40:]
        
        poem = []
        for _ in range(num_lines):
            line = self._generate_line(context, target_len)
            poem.append(line)
            context = (context + line + "\n")[-40:]
        return poem

    def _generate_line(self, context, target_len):
        line = ""
        current_context = context
        for _ in range(int(target_len * 0.85)):
            char = self._predict(current_context, forbidden=['\n'])
            line += char
            current_context = (current_context + char)[-40:]
        for _ in range(15):
            char = self._predict(current_context)
            line += char
            if char in [' ', '.', '!', '?', '\n']: break
            current_context = (current_context + char)[-40:]
        return line.strip().capitalize()

    def _predict(self, context, forbidden=None):
        x = np.zeros((1, 40))
        for t, char in enumerate(context[-40:]):
            x[0, t] = self.char_to_int.get(char, 0)
        preds = self.crpo_model.predict(x, verbose=0)[0]
        if forbidden:
            for f_char in forbidden:
                if f_char in self.char_to_int: preds[self.char_to_int[f_char]] = 0
            if np.sum(preds) > 0: preds = preds / np.sum(preds)
        return self.int_to_char[self.sample_with_temperature(preds)]