import re
import os
import numpy as np
from datasets import load_dataset
import re
import nltk
from nltk.corpus import cmudict

# Gerekli kaynakları indir
nltk.download('cmudict')
d = cmudict.dict()

def get_meter_profile(word):
    """
    Makaledeki 'Rhythmic Tags' mantığı: 'today' -> '01'[cite: 137].
    Kelimelerin vurgu yapısını döndürür.
    """
    word = word.lower()
    if word in d:
        # İlk telaffuz varyasyonunu al ve sadece rakamları (stres) çek
        return "".join([char for char in d[word][0] if char.isdigit()])
    return "0" * (len(word) // 3) # Bilinmeyen kelimeler için basit tahmin

def check_rhyme_manual(word1, word2):
    """
    Makaledeki 'Rhyme Constraints' mantığı: Son stressed sesliden sonrası aynı olmalı[cite: 132].
    """
    def get_rhyme_part(word):
        if word in d:
            # Fonetik dizideki son stressed sesliyi bul
            phonemes = d[word][0]
            for i in range(len(phonemes)-1, -1, -1):
                if any(char.isdigit() and char != '0' for char in phonemes[i]):
                    return phonemes[i:]
        return word[-2:] # Kelime sözlükte yoksa son 2 harfe bak

    return get_rhyme_part(word1.lower()) == get_rhyme_part(word2.lower())

def get_crpo_clean_corpus(limit=50000):
    # Data klasörünün varlığından emin olalım
    if not os.path.exists('data'):
        os.makedirs('data')

    dataset = load_dataset("biglam/gutenberg-poetry-corpus", split="train")
    
    # 1. Ham veriyi al (Raw Data)
    raw_lines = [line['line'] for line in dataset.select(range(limit))]
    full_text = "\n".join(raw_lines)

    # HAM VERİYİ KAYDET (Olduğu gibi)
    with open("data/raw_corpus_debug.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # 2. Temizlik İşlemleri (Process Data)
    # ISO-8859-1 dışı karakterleri at
    clean_text = re.sub(r'[^\x00-\x7f]', r'', full_text)
    # Gereksiz boşlukları/tabları temizle
    clean_text = re.sub(r'[ \t]+', ' ', clean_text)
    # Çoklu satır boşluklarını teke indir
    clean_text = re.sub(r'\n+', '\n', clean_text)
    # Küçük harfe çevir
    clean_text = clean_text.lower()
    
    # İŞLENMİŞ (PROCESSED) VERİYİ KAYDET
    with open("data/processed_corpus_debug.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

    print(f"--- Debug: Veriler data/ klasörüne kaydedildi. (Limit: {limit} satır) ---")
    
    return clean_text