import re
import os
import numpy as np
from datasets import load_dataset

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