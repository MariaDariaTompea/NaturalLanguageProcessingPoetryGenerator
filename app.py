from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import random
import re
import numpy as np
from collections import defaultdict, Counter
from textblob import TextBlob
import pronouncing
from datasets import load_dataset

# --- EXACT RESTORATION FROM GITHUB ---

# 1. Linguistic Utilities (from deneme.py)
class SentimentAnalyzer:
    @staticmethod
    def analyze(text):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            return max(-5, min(5, int(polarity * 5)))
        except: return 0

class LinguisticAnalyzer:
    @staticmethod
    def syllable_count(word):
        word = word.lower()
        count = 0
        vowels = 'aeiou'
        if not word: return 0
        if word[0] in vowels: count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith('e'): count -= 1
        return max(1, count)

    @staticmethod
    def line_syllables(line):
        return sum(LinguisticAnalyzer.syllable_count(w) for w in line.split())

    @staticmethod
    def end_sound(word):
        word = word.lower().rstrip('.,!?;:\'"')
        try:
            phones = pronouncing.phones_for_word(word)
            if phones: return phones[0].split()[-1]
        except: pass
        return word[-2:] if len(word) > 1 else word

def is_valid_line(line):
    if not line or not line.strip(): return False
    text = line.strip()
    words = text.split()
    if len(words) < 3 or len(words) > 20: return False
    if any(char.isdigit() for char in text): return False
    return True

# 2. CRPO Engine (Literal from deneme.py)
class PoemTemplate:
    TEMPLATES = {
        'couplet': {'stanzas': 1, 'lines_per_stanza': 2, 'constraints': ['rhyme_end'], 'sentiment_alternation': False},
        'quatrain': {'stanzas': 1, 'lines_per_stanza': 4, 'constraints': ['rhyme_abab'], 'sentiment_alternation': True},
        'free': {'stanzas': 2, 'lines_per_stanza': 3, 'constraints': [], 'sentiment_alternation': False}
    }
    @staticmethod
    def get_template(name='free'):
        return PoemTemplate.TEMPLATES.get(name, PoemTemplate.TEMPLATES['free'])

class PoemGenerator:
    @staticmethod
    def find_lines_with_phrase(clean_lines, noun_phrase, limit=50):
        if not noun_phrase: return []
        phrase_words = noun_phrase.lower().split()
        matching_lines = [line for line in clean_lines if any(word in line.lower() for word in phrase_words)]
        return random.sample(matching_lines, min(limit, len(matching_lines))) if matching_lines else []

    @staticmethod
    def select_lines_by_sentiment(clean_lines, line_metadata, num_lines, target_sentiment='positive', tolerance=1):
        candidates = [line for line in clean_lines if abs(line_metadata[line]['sentiment'] - (5 if target_sentiment == 'positive' else -5)) <= tolerance * 2]
        return random.sample(candidates, min(num_lines, len(candidates))) if candidates else random.sample(clean_lines, min(num_lines, len(clean_lines)))

    @staticmethod
    def generate_poem(clean_lines, line_metadata, template_name='free', num_stanzas=2, noun_phrase=None):
        template = PoemTemplate.get_template(template_name)
        target_sentiment = 'positive' # Default
        total_lines = num_stanzas * template['lines_per_stanza']
        
        if noun_phrase:
            phrase_lines = PoemGenerator.find_lines_with_phrase(clean_lines, noun_phrase, limit=total_lines)
            if phrase_lines:
                num_phrase = min(len(phrase_lines), max(1, total_lines // 2))
                poem_lines = random.sample(phrase_lines, num_phrase)
                remaining = total_lines - len(poem_lines)
                if remaining > 0:
                    poem_lines.extend(PoemGenerator.select_lines_by_sentiment(clean_lines, line_metadata, remaining, target_sentiment))
            else:
                poem_lines = PoemGenerator.select_lines_by_sentiment(clean_lines, line_metadata, total_lines, target_sentiment)
        else:
            poem_lines = PoemGenerator.select_lines_by_sentiment(clean_lines, line_metadata, total_lines, target_sentiment)
        
        random.shuffle(poem_lines)
        return poem_lines[:total_lines]

# 3. Markov Engine (Literal from markov_model.py)
class CMPPoet:
    def __init__(self, corpus_lines):
        self.vocab = sorted(list(set(" ".join(corpus_lines).split())))
        self.w2i = {w: i for i, w in enumerate(self.vocab)}
        self.i2w = {i: w for w, i in self.w2i.items()}
        self.n = len(self.vocab)
        self.M = np.zeros((self.n, self.n))
        self.prior = np.zeros(self.n)
        for line in corpus_lines:
            tokens = line.split()
            if not tokens: continue
            if tokens[0] in self.w2i: self.prior[self.w2i[tokens[0]]] += 1
            for i in range(len(tokens)-1):
                if tokens[i] in self.w2i and tokens[i+1] in self.w2i:
                    self.M[self.w2i[tokens[i]], self.w2i[tokens[i+1]]] += 1
        self.prior /= (self.prior.sum() + 1e-9)
        sums = self.M.sum(axis=1)
        self.M = np.divide(self.M, sums[:, None], where=sums[:, None]!=0)

    def generate_line(self, L, constraints):
        Z = [self.M.copy() for _ in range(L - 1)]
        Z_prior = self.prior.copy()
        for pos, allowed in constraints.items():
            if pos >= L: continue
            allowed_idx = [self.w2i[w] for w in allowed if w in self.w2i]
            if not allowed_idx: continue
            mask = np.ones(self.n, dtype=bool)
            mask[allowed_idx] = False
            if pos == 0: Z_prior[mask] = 0
            else: Z[pos-1][:, mask] = 0
        alphas = [np.zeros(self.n) for _ in range(L)]
        alphas[L-1] = np.ones(self.n)
        for i in range(L-2, -1, -1): alphas[i] = Z[i] @ alphas[i+1]
        p0 = Z_prior * (Z[0] @ alphas[1] if L > 1 else 1)
        if p0.sum() == 0: return "..."
        curr_idx = np.random.choice(self.n, p=p0/p0.sum())
        line = [self.i2w[curr_idx]]
        for i in range(L-1):
            prob_row = Z[i][curr_idx] * alphas[i+1]
            if prob_row.sum() == 0: break
            curr_idx = np.random.choice(self.n, p=prob_row/prob_row.sum())
            line.append(self.i2w[curr_idx])
        return " ".join(line)

# --- APP ---
app = Flask(__name__, static_folder='customs')
clean_lines = []
line_metadata = {}
markov_poet = None

def init_all():
    global clean_lines, line_metadata, markov_poet
    if clean_lines: return
    if os.path.exists("markov/corpus.txt"):
        with open("markov/corpus.txt", 'r', encoding='utf-8') as f:
            mc = [l.strip() for l in f.readlines() if is_valid_line(l)]
            markov_poet = CMPPoet(mc)
    ds = load_dataset("biglam/gutenberg-poetry-corpus", split="train")
    for row in ds:
        line = row.get("line", "").strip()
        if not is_valid_line(line): continue
        line = " ".join(line.split())
        clean_lines.append(line)
        line_metadata[line] = {'sentiment': SentimentAnalyzer.analyze(line), 'end_sound': LinguisticAnalyzer.end_sound(line.split()[-1])}
        if len(clean_lines) >= 10000: break

THEMATIC_WORDS = ["love", "night", "heart", "moon", "star", "sky", "soul", "dream", "fire", "light", "beauty", "rose", "kiss", "dear", "sweet", "dark", "glow", "deep", "blue", "gold", "white", "wind", "rain", "ocean", "sea", "plain", "wild", "soft", "pure", "true"]

@app.route('/')
def selection(): return render_template('selection.html')

@app.route('/customs/<path:filename>')
def custom_static(filename): return send_from_directory(app.static_folder, filename)

@app.route('/markov', methods=['GET', 'POST'])
def markov_page():
    init_all()
    result, mode, seed = None, None, request.form.get('seed')
    if request.method == 'POST':
        action = request.form.get('action')
        seeds = seed.lower().split() if seed else []
        def gen_s():
            l1 = markov_poet.generate_line(7, {0: seeds} if seeds else {})
            l2 = markov_poet.generate_line(7, {})
            return [l1.capitalize(), l2.capitalize()]
        if action == 'stanza': result, mode = gen_s(), 'stanza'
        else: result, mode = {"Stanza I": gen_s(), "Chorus": gen_s(), "Stanza II": gen_s()}, 'lyrics'
    return render_template('markov.html', result=result, mode=mode, popular_words=THEMATIC_WORDS, selected_seed=seed)

@app.route('/crpo', methods=['GET', 'POST'])
def crpo_page():
    init_all()
    result, mode, seed = None, None, request.form.get('seed')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'stanza':
            result = PoemGenerator.generate_poem(clean_lines, line_metadata, template_name='couplet', num_stanzas=1, noun_phrase=seed)
            mode = 'stanza'
        else:
            lines = PoemGenerator.generate_poem(clean_lines, line_metadata, template_name='free', num_stanzas=2, noun_phrase=seed)
            result = {"Verse 1": lines[:3], "Chorus": lines[3:]}
            mode = 'lyrics'
    return render_template('crpo.html', result=result, mode=mode, popular_words=THEMATIC_WORDS, selected_seed=seed)

if __name__ == '__main__': app.run(debug=True, port=8000)
