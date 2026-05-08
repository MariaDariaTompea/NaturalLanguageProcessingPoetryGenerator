import kagglehub
import pandas as pd
import os

def prepare_data():
    print("Veri seti indiriliyor...")
    path = kagglehub.dataset_download("cloudy17/bob-dylan-songs")
    
    # Klasördeki tüm dosyaları listele ve ilk csv dosyasını bul
    files = [f for f in os.listdir(path) if f.endswith('.csv')]
    
    if not files:
        print("Hata: İndirilen klasörde CSV dosyası bulunamadı!")
        return

    csv_path = os.path.join(path, files[0])
    print(f"Dosya bulundu: {csv_path}")
    
    # Veriyi oku
    df = pd.read_csv(csv_path)
    
    # Kaggle görselindeki sütun isimlerine göre 'lyrics' kısmını al
    if 'lyrics' in df.columns:
        lyrics = df['lyrics'].dropna().astype(str).tolist()
        with open("corpus.txt", "w", encoding="utf-8") as f:
            for line in lyrics:
                f.write(line + "\n")
        print("Başarılı: corpus.txt oluşturuldu.")
    else:
        print(f"Hata: 'lyrics' sütunu bulunamadı. Mevcut sütunlar: {df.columns.tolist()}")

if __name__ == "__main__":
    prepare_data()