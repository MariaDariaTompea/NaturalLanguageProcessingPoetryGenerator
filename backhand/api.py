from .models.markov_model import CMPPoet
from .utils.nlp_helpers import get_clean_corpus

class PoetryAPI:
    def __init__(self):
        corpus = get_clean_corpus()
        self.poet = CMPPoet(corpus)

    def generate(self, length=6, theme_pos=2, theme_words=None):
        constraints = {theme_pos: theme_words if theme_words else []}
        return self.poet.generate_line(length, constraints)