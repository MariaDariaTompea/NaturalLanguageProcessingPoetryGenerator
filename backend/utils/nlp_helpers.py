import re
import numpy as np
from datasets import load_dataset

def get_crpo_clean_corpus(limit=50000):
    dataset = load_dataset("biglam/gutenberg-poetry-corpus", split="train")
    
    # 1. Ham satırları al
    raw_lines = [line['line'] for line in dataset.select(range(limit))]
    
    # 2. Satırları birleştirirken her satırın sonuna gerçek bir yeni satır karakteri koy
    # Bu, modelin dizenin nerede bittiğini öğrenmesi için hayatidir.
    full_text = "\n".join(raw_lines)
    
    # 3. ISO-8859-1 temizliği (Senin mevcut kodun)
    clean_text = re.sub(r'[^\x00-\x7f]', r'', full_text)
    
    # 4. KRİTİK: Gereksiz boşlukları temizle ama tek boşluğu ve yeni satırı koru
    # Modelin 'kelime' kavramını anlaması için boşluklar çok önemli.
    clean_text = re.sub(r'[ \t]+', ' ', clean_text) # Sekmeleri boşluğa çevir
    
    # 5. Küçük harfe çevir (Makale, karakter kümesini daraltmak için bunu önerir)
    clean_text = clean_text.lower()
    
    return clean_text

def prepare_data(text, seq_length=40):
    chars = sorted(list(set(text)))
    char_to_int = {c: i for i, c in enumerate(chars)}
    
    X, y = [], []
    for i in range(0, len(text) - seq_length):
        sequence = text[i:i + seq_length]
        label = text[i + seq_length]
        X.append([char_to_int[char] for char in sequence])
        # Softmax tahmini için hedef karakterin indeksini al [cite: 144]
        y.append(char_to_int[label])
        
    return np.array(X), np.array(y), char_to_int, chars