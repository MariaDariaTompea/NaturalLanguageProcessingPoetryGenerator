import random
import os
import spacy
import nltk
from nltk.corpus import wordnet
from gensim.models import Word2Vec

# SpaCy yüklemesi
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class EnhancedFacePoet:
    def __init__(self, corpus_text, order=2):
        self.order = order
        self.corpus_text = corpus_text
        self.tokens = []
        self.chain = {}
        self.w2v_model = None
        self._analyze_corpus()
        self._train_embeddings()

    def _analyze_corpus(self):
        doc = nlp(self.corpus_text)
        self.tokens = [t for t in doc if not t.is_space and not t.is_punct]
        for i in range(len(self.tokens) - self.order):
            state = tuple(t.lemma_ for t in self.tokens[i : i + self.order])
            next_token = self.tokens[i + self.order]
            if state not in self.chain:
                self.chain[state] = []
            self.chain[state].append((next_token.text, next_token.pos_))

    def _train_embeddings(self):
        sentences = [line.lower().split() for line in self.corpus_text.split('\n') if line.strip()]
        self.w2v_model = Word2Vec(sentences, vector_size=50, window=5, min_count=1, workers=4)

    def get_synonym(self, word):
        syns = wordnet.synsets(word)
        if not syns: return word
        synonyms = set()
        for syn in syns:
            for l in syn.lemmas():
                if l.name() != word:
                    synonyms.add(l.name().replace('_', ' '))
        return random.choice(list(synonyms)) if synonyms else word

    def generate(self, length=40, words_per_line=6):
        if not self.chain: return "Corpus too small."
        pos_sequence = ["NOUN", "VERB", "ADJ", "NOUN", "ADP", "DET", "NOUN"]
        current_lemmas = random.choice(list(self.chain.keys()))
        poem_words = list(current_lemmas)

        for i in range(length):
            state = tuple(current_lemmas)
            candidates = self.chain.get(state, [])
            if not candidates:
                new_state = random.choice(list(self.chain.keys()))
                current_lemmas = list(new_state)
                continue

            ideal_pos = pos_sequence[i % len(pos_sequence)]
            scored = []
            for word, pos in candidates:
                score = 1.0
                if pos == ideal_pos: score += 2.0
                if word.lower() in [pw.lower() for pw in poem_words[-3:]]: score -= 5.0
                scored.append((word, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            choice_word = random.choice(scored[:max(1, len(scored)//2)])[0]
            poem_words.append(choice_word)
            doc_word = nlp(choice_word)
            current_lemmas = (list(current_lemmas) + [doc_word[0].lemma_])[1:]

        # WordNet Değişimi & Biçimlendirme
        final = []
        for word in poem_words:
            final.append(self.get_synonym(word) if len(word) > 4 and random.random() < 0.1 else word)

        import re
        lines = []
        current_line = []
        for word in final:
            if not current_line and re.match(r'^[.,!?;:]+$', word):
                continue
                
            if not current_line:
                word = word.capitalize()
                
            if re.match(r'^[.,!?;:]+$', word) and current_line:
                current_line[-1] += word
                continue
                
            current_line.append(word)
            
            if len(current_line) >= words_per_line:
                lines.append(" ".join(current_line))
                current_line = []
                
        if current_line:
            lines.append(" ".join(current_line))
            
        return "\n".join(lines).strip()