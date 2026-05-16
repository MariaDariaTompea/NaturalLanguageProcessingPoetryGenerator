import os
import re
import random
import numpy as np
import tensorflow as tf
import pronouncing  # pip install pronouncing
from .models.crpo_model import CRPOModel
from .utils.nlp_helpers import get_crpo_clean_corpus

class PoetryAPI:
    def __init__(self, weights_path='crpo_weights.weights.h5', limit=20000):
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

    def _clean_line(self, line):
        if not line: return None
        
        # 1. Yan yana gelen noktalamaları temizle (,,. -> .)
        line = re.sub(r'[.,!?;:]{2,}', '.', line)
        
        # 2. Gereksiz boşlukları al ve kenarları temizle
        line = line.strip().strip(',').strip()
        
        words = line.split()
        if len(words) < 3: return None # Çok kısa/anlamsız satırları reddet

        # 3. Anlamsız/Yarım kelime kontrolü (gr, th gibi 1-2 harflik saçma bitişleri temizle)
        # İstisna: İngilizcedeki anlamlı kısa kelimeler
        allowed_shorts = ['me', 'be', 'is', 'he', 'we', 'to', 'in', 'it', 'my', 'so', 'as']
        if len(words[-1]) < 3 and words[-1].lower() not in allowed_shorts:
            words.pop()
            line = " ".join(words)

        # 4. Satır sonu bağlaç kontrolü
        invalid_ends = ['the', 'and', 'a', 'of', 'with', 'to', 'in', 'is', 'at', 'by', 'for']
        if words and words[-1].lower() in invalid_ends:
            return None 

        return line if len(line) > 10 else None

    def generate_crpo_poem(self, line_count, seed_word=""):
        # Dinamik Kafiye Şeması Oluşturma (A, B, A, B... şeklinde döngü)
        # Örn: line_count=6 ise scheme=['A', 'B', 'A', 'B', 'A', 'B'] olur
        scheme = []
        for i in range(line_count):
            scheme.append('A' if i % 2 == 0 else 'B')
        
        # Satır uzunluğunu slider modunda standart (45) tutuyoruz
        target_len = 45 
        
        poem = []
        rhyme_storage = {} 
        line_idx = 0

        # Güvenlik önlemi: Sonsuz döngüye girmemesi için deneme sınırı
        max_attempts = line_count * 5 
        attempts = 0

        while len(poem) < line_count and attempts < max_attempts:
            attempts += 1
            current_scheme = scheme[line_idx]
            target_rhyme_word = rhyme_storage.get(current_scheme)
            
            # Satır üretimi
            line = self._generate_line(target_len, rhyme_with=target_rhyme_word)
            
            # SEED WORD: Sadece ilk satıra rastgele yerleştir
            if line_idx == 0 and seed_word:
                words = line.split()
                if seed_word.lower() not in line.lower():
                    insert_pos = random.randint(0, len(words))
                    words.insert(insert_pos, seed_word)
                    line = " ".join(words)

            cleaned = self._clean_line(line)
            if cleaned:
                # Kafiye için son kelimeyi kaydet
                last_word = cleaned.split()[-1].strip(".,!?;").lower()
                if current_scheme not in rhyme_storage:
                    rhyme_storage[current_scheme] = last_word
                
                poem.append(cleaned.capitalize())
                line_idx += 1
                
        return poem

    def _generate_line(self, target_len, rhyme_with=None):
        # Her satır için temiz bir context başlatarak modelin takılmasını önlüyoruz
        context = "the silent world of nature and spirits ".rjust(40)[-40:]
        line = ""
        
        # 1. Normal Üretim (Hedef uzunluğun %70'ine kadar)
        for _ in range(int(target_len * 0.7)):
            char = self._predict(context, forbidden=['\n', '\r'])
            line += char
            context = (context + char)[-40:]

        # 2. Kafiye Enjeksiyonu
        if rhyme_with:
            rhymes = pronouncing.rhymes(rhyme_with)
            # Anlamsız (gr. gibi) kısa harfleri filtrele, sadece gerçek kelimeleri al
            valid_rhymes = [r for r in rhymes if len(r) > 2 and r.isalpha()]
            
            if valid_rhymes:
                rhyme_word = random.choice(valid_rhymes[:15]) # En iyi 15 seçenekten biri
                # Yarım kalan son kelimeyi temizle ve kafiyeli kelimeyi bağla
                if ' ' in line:
                    line = line.rsplit(' ', 1)[0]
                return line + " " + rhyme_word + "."

        # 3. Kafiye yoksa veya bulunamadıysa cümleyi doğal bitir
        for _ in range(25):
            char = self._predict(context)
            line += char
            if char in [' ', '.', '!', '?']: break
            context = (context + char)[-40:]
            
        return line

    def _predict(self, context, forbidden=None):
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