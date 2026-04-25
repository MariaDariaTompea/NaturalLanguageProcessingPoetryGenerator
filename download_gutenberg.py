from datasets import load_dataset
import os

def download_sample():
    print("Loading Gutenberg Poetry Corpus from HuggingFace...")
    # This dataset only has a 'train' split usually
    dataset = load_dataset("biglam/gutenberg-poetry-corpus", split="train", streaming=True)
    
    output_path = os.path.join("data", "gutenberg_sample.txt")
    os.makedirs("data", exist_ok=True)
    
    count = 0
    limit = 100000
    
    print(f"Extracting up to {limit} lines...")
    with open(output_path, "w", encoding="utf-8") as f:
        for item in dataset:
            line = item['line'].strip()
            if line:
                f.write(line + "\n")
                count += 1
            if count >= limit:
                break
    
    print(f"Download complete! Saved {count} lines to {output_path}")

if __name__ == "__main__":
    download_sample()
