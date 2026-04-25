import random
import os

# 500 Symbolist-themed words (Themes: Azure, Silence, Dreams, Gems, Night, Soul)
SYMBOLIST_LEXICON = [
    "azure", "swan", "lily", "shadow", "velvet", "moon", "silence", "dream", "ghost",
    "gold", "silver", "perfume", "crystal", "wine", "flute", "mirror", "lace", "jewel",
    "twilight", "mist", "sea", "stars", "wind", "spirit", "memory", "void", "night",
    "soul", "longing", "fading", "melting", "singing", "vanishing", "falling", "weeping",
    "ivory", "marble", "dead", "sleeping", "pale", "rose", "blue", "violet", "purple",
    "black", "white", "emerald", "ruby", "sapphire", "diamond", "smoke", "fire", "ice",
    "cold", "warm", "soft", "hard", "dark", "light", "deep", "high", "low", "still",
    "eternal", "fleeting", "forgotten", "remembered", "sacred", "profane", "lost", "found",
    "beauty", "ugliness", "grace", "death", "life", "love", "hate", "fear", "joy",
    "sorrow", "tears", "laughter", "echo", "whisper", "shout", "cry", "song", "music",
    "silken", "rough", "smooth", "bitter", "sweet", "salt", "fresh", "stale", "pure",
    "corrupt", "holy", "vile", "hidden", "bright", "dull", "ancient", "new", "old",
    "glass", "stone", "water", "earth", "air", "flame", "starry", "cloudy", "rainy",
    "sunny", "coldly", "warmly", "softly", "darkly", "lightly", "deeply", "highly",
    "lowly", "stilly", "eternally", "fleetingly", "sacredly", "lostly", "foundly",
    "beautifully", "graciously", "deathly", "life-like", "lovely", "hatefully",
    "fearfully", "joyfully", "sorrowfully", "tearfully", "echoing", "whispering",
    "shouting", "crying", "singing", "musical", "bitterly", "sweetly", "freshly",
    "stalely", "purely", "corruptly", "holily", "vilely", "brightly", "dullly",
    "anciently", "newly", "oldly", "glassy", "stony", "watery", "earthy", "airy",
    "flaming", "azurely", "swanning", "lilied", "shadowed", "velvety", "moonly",
    "silencing", "dreaming", "ghostly", "goldened", "silvered", "perfuming",
    "crystalled", "wining", "fluting", "mirroring", "laced", "jewelled", "twilit",
    "misted", "sea-like", "starred", "windy", "spirited", "memoried", "voided",
    "nightly", "souled", "longed", "faded", "melted", "sung", "vanished", "fallen",
    "wept", "ivoried", "marbled", "deadened", "sleepy", "paler", "rosy", "bluish",
    "violeted", "purpled", "blackened", "whitened", "emeralded", "rubied", "sapphired",
    "diamonded", "smoked", "fired", "iced", "coldest", "warmest", "softest", "hardest",
    "darkest", "lightest", "deepest", "highest", "lowest", "stillest", "eternity",
    "fleetness", "forgetfulness", "remembrance", "sacredness", "profanity", "loss",
    "foundness", "beautified", "gracious", "deathless", "life-less", "loveless",
    "hateless", "fearless", "joyless", "sorrowless", "tearless", "echoes", "whispers",
    "shouts", "cries", "songs", "musics", "silks", "roughs", "smooths", "bitters",
    "sweets", "salts", "freshen", "stale-like", "purified", "corruptness", "holiness",
    "vileness", "brightness", "dullness", "ancientness", "newness", "oldness",
    "glasses", "stones", "waters", "earthern", "airless", "flameless", "star-like",
    "clouded", "raining", "sunned", "cold-hearted", "warm-hearted", "softly-spoken",
    "darkness", "lightness", "deepness", "highness", "lowness", "stillness",
    "eternal-life", "fleeting-dream", "forgotten-soul", "remembered-grace",
    "sacred-lily", "lost-swan", "found-azure", "beautiful-void", "gracious-night",
    "deathly-silence", "loveliness", "sorrowful-song", "echoing-perfume",
    "whispering-velvet", "singing-mirror", "musical-gold", "sweet-water",
    "bright-jewel", "ancient-spirit", "glass-house", "stone-heart", "fire-ice",
    "shadow-mist", "dream-spirit", "soul-song", "death-life", "love-hate",
    "fear-joy", "sorrow-laughter", "azure-sky", "moon-light", "star-shine",
    "wind-whisper", "mist-twilight", "sea-salt", "void-eternal", "night-shadow",
    "spirit-dream", "lily-pure", "swan-white", "rose-red", "violet-blue",
    "emerald-green", "gold-bright", "silver-light", "mirror-clear", "jewel-glow",
    "flute-sound", "wine-sweet", "perfume-scent", "velvet-soft", "crystal-cool",
    "ice-cold", "fire-warm", "marble-still", "ivory-smooth", "lace-fine",
    "dreamy", "ghostlike", "misty", "starry-eyed", "shadowy", "spirit-like",
    "soul-deep", "heart-felt", "eternal-rest", "deathly-pale", "life-affirming",
    "lovely-bird", "beautiful-flower", "gracious-lady", "sacred-ground",
    "pure-water", "bright-sun", "ancient-text", "new-world", "old-friend",
    "glass-like", "stone-wall", "fire-light", "watery-eyes", "earthy-smell",
    "airy-feeling", "flaming-hot", "azure-blue", "swan-lake", "lily-pad",
    "shadow-play", "velvet-glove", "moon-beam", "silence-is-golden", "dream-catcher",
    "ghost-town"
]

# Ensure we have at least 500 words for the experiment (pad if necessary)
while len(SYMBOLIST_LEXICON) < 500:
    SYMBOLIST_LEXICON.append(random.choice(SYMBOLIST_LEXICON) + "-shadow")

def generate_symbolist_corpus():
    output_path = os.path.join("data", "symbolist_loop_corpus.txt")
    os.makedirs("data", exist_ok=True)

    print("Weaving the Symbolist Loop Corpus (4000 lines)...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        for _ in range(4000):
            # Generate a 'line' by picking 4-8 words from the lexicon
            line_len = random.randint(4, 9)
            line_words = [random.choice(SYMBOLIST_LEXICON) for _ in range(line_len)]
            
            # Add some light structural artifacts
            line = " ".join(line_words)
            if random.random() < 0.3: line += ","
            if random.random() < 0.1: line += "."
            
            f.write(line + "\n")
            
    print(f"Symbolist Loop Corpus created at {output_path}")

if __name__ == "__main__":
    generate_symbolist_corpus()
