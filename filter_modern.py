import os

ARCHAIC_MARKERS = {
    'thou', 'thee', 'thy', 'thine', 'hath', 'doth', 'hast', 'ye', 'shalt', 'art',
    'noght', 'togedre', 'moe', 'fairest', 'dost', 'wast', 'wert', 'ay', 'nay',
    'spede', 'tresoun', 'togedre', 'amonte', 'noght', 'spake', 'quoth', 'unto', 'oft'
}

def is_archaic(line):
    words = line.lower().split()
    for w in words:
        # Check specific markers
        if w in ARCHAIC_MARKERS:
            return True
        # Check historical endings (-eth, -est) on words longer than 4 chars
        if len(w) > 4:
            if w.endswith('eth') or w.endswith('est'):
                return True
    return False

def filter_corpus():
    input_path = os.path.join("data", "gutenberg_sample.txt")
    output_path = os.path.join("data", "gutenberg_modern.txt")
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print("Filtering Gutenberg Corpus for Modern English...")
    modern_lines = []
    total_checked = 0
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            total_checked += 1
            if not is_archaic(line):
                modern_lines.append(line)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(modern_lines)
        
    print(f"Filtered {total_checked} lines.")
    print(f"Saved {len(modern_lines)} Modern lines to {output_path}.")
    print(f"Removed {total_checked - len(modern_lines)} archaic lines.")

if __name__ == "__main__":
    filter_corpus()
