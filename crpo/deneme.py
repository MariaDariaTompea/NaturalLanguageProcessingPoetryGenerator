from flask import Flask, render_template, request, jsonify
from datasets import load_dataset
import random
import re
from collections import defaultdict, Counter
from datetime import datetime
from textblob import TextBlob
import pronouncing

app = Flask(__name__)

# Global models and data
clean_lines = []
line_metadata = {}  # store sentiment, syllables, rhyme info
sentiment_scores = {}
ngram_model = None


class SentimentAnalyzer:
    """Simple sentiment analysis using TextBlob."""
    
    @staticmethod
    def analyze(text):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            return max(-5, min(5, int(polarity * 5)))  # Scale to -5 to 5
        except:
            return 0


class LinguisticAnalyzer:
    """Extract linguistic properties of lines."""
    
    @staticmethod
    def syllable_count(word):
        """Rough syllable estimation."""
        word = word.lower()
        count = 0
        vowels = 'aeiou'
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            count += 1
        return max(1, count)
    
    @staticmethod
    def line_syllables(line):
        """Count total syllables in a line."""
        return sum(LinguisticAnalyzer.syllable_count(w) for w in line.split())
    
    @staticmethod
    def end_sound(word):
        """Get the final phoneme for rhyming."""
        word = word.lower().rstrip('.,!?;:\'"')
        try:
            phones = pronouncing.phones_for_word(word)
            if phones:
                return phones[0].split()[-1]
        except:
            pass
        return word[-2:] if len(word) > 1 else word


def is_valid_line(line):
    """Filter for quality lines."""
    if not line or not line.strip():
        return False
    text = line.strip()
    words = text.split()
    if len(words) < 3 or len(words) > 20:
        return False
    if any(char.isdigit() for char in text):
        return False
    if re.search(r"[^A-Za-z0-9 ,.;:'\"!?()\-]", text):
        return False
    if text.count("'") > 3:
        return False
    return True


def build_corpus_model(max_lines=100000):
    """Load Gutenberg poetry corpus with linguistic metadata."""
    global clean_lines, line_metadata, sentiment_scores, ngram_model
    
    dataset = load_dataset("biglam/gutenberg-poetry-corpus", split="train")
    clean_lines = []
    line_metadata = {}
    sentiment_scores = []
    ngram = defaultdict(Counter)
    
    loaded = 0
    for row in dataset:
        line = row.get("line", "")
        if not is_valid_line(line):
            continue
        
        line = " ".join(line.strip().split())
        clean_lines.append(line)
        
        # Analyze line properties
        sentiment = SentimentAnalyzer.analyze(line)
        syllables = LinguisticAnalyzer.line_syllables(line)
        end_word = line.split()[-1] if line.split() else ""
        end_sound = LinguisticAnalyzer.end_sound(end_word)
        
        line_metadata[line] = {
            'sentiment': sentiment,
            'syllables': syllables,
            'end_sound': end_sound,
            'length': len(line.split())
        }
        sentiment_scores.append(sentiment)
        
        # Build n-gram model for fallback
        words = ["<s>"] + line.split() + ["</s>"]
        for i in range(len(words) - 2):
            key = (words[i], words[i + 1])
            ngram[key][words[i + 2]] += 1
        
        loaded += 1
        if loaded >= max_lines:
            break
    
    ngram_model = {key: dict(counter) for key, counter in ngram.items()}
    return len(clean_lines)


class PoemTemplate:
    """Define poem structure with constraints."""
    
    TEMPLATES = {
        'couplet': {
            'stanzas': 2,
            'lines_per_stanza': 2,
            'constraints': ['rhyme_end'],
            'sentiment_alternation': False
        },
        'quatrain': {
            'stanzas': 1,
            'lines_per_stanza': 4,
            'constraints': ['rhyme_abab'],
            'sentiment_alternation': True
        },
        'free': {
            'stanzas': 2,
            'lines_per_stanza': 3,
            'constraints': [],
            'sentiment_alternation': False
        }
    }
    
    @staticmethod
    def get_template(template_name='free'):
        return PoemTemplate.TEMPLATES.get(template_name, PoemTemplate.TEMPLATES['free'])


class PoemGenerator:
    """Generate poems using Full-FACE approach."""
    
    @staticmethod
    def get_mood():
        """Determine mood from average sentiment of corpus."""
        if not sentiment_scores:
            return "neutral"
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        return "positive" if avg_sentiment > 0 else "negative" if avg_sentiment < 0 else "neutral"
    
    @staticmethod
    def find_lines_with_phrase(noun_phrase, limit=50):
        """Find lines containing the noun phrase or similar words."""
        if not noun_phrase or len(noun_phrase.strip()) == 0:
            return []
        
        phrase_words = noun_phrase.lower().split()
        matching_lines = []
        
        for line in clean_lines:
            line_lower = line.lower()
            # Check if any word from phrase is in the line
            if any(word in line_lower for word in phrase_words):
                matching_lines.append(line)
        
        # If we found matches, return up to limit
        if matching_lines:
            return random.sample(matching_lines, min(limit, len(matching_lines)))
        
        return []
    
    @staticmethod
    def select_lines_by_sentiment(num_lines, target_sentiment='positive', tolerance=1):
        """Select lines matching a sentiment target."""
        candidates = [
            line for line in clean_lines
            if abs(line_metadata[line]['sentiment'] - (5 if target_sentiment == 'positive' else -5)) <= tolerance * 2
        ]
        return random.sample(candidates, min(num_lines, len(candidates))) if candidates else random.sample(clean_lines, min(num_lines, len(clean_lines)))
    
    @staticmethod
    def generate_poem(template_name='free', num_stanzas=2, noun_phrase=None):
        """Generate poem using template constraints, optionally incorporating noun phrase."""
        if not clean_lines:
            return [], {}
        
        template = PoemTemplate.get_template(template_name)
        mood = PoemGenerator.get_mood()
        target_sentiment = 'positive' if mood == 'positive' else 'negative'
        
        poem_lines = []
        metadata = {
            'template': template_name,
            'mood': mood,
            'sentiment': target_sentiment,
            'stanzas': num_stanzas,
            'lines_per_stanza': template['lines_per_stanza'],
            'noun_phrase': noun_phrase
        }
        
        total_lines_needed = num_stanzas * template['lines_per_stanza']
        
        # If noun phrase provided, try to include lines containing it
        if noun_phrase and len(noun_phrase.strip()) > 0:
            phrase_lines = PoemGenerator.find_lines_with_phrase(noun_phrase, limit=total_lines_needed)
            
            if phrase_lines:
                # Use some phrase-related lines and fill rest with sentiment-matched lines
                num_phrase_lines = min(len(phrase_lines), max(1, total_lines_needed // 2))
                poem_lines.extend(random.sample(phrase_lines, num_phrase_lines))
                
                # Fill remaining with sentiment-matched lines
                remaining = total_lines_needed - len(poem_lines)
                if remaining > 0:
                    additional_lines = PoemGenerator.select_lines_by_sentiment(remaining, target_sentiment)
                    poem_lines.extend(additional_lines[:remaining])
            else:
                # If no phrase lines found, generate normally
                poem_lines = PoemGenerator.select_lines_by_sentiment(total_lines_needed, target_sentiment)
        else:
            # Generate without phrase
            poem_lines = PoemGenerator.select_lines_by_sentiment(total_lines_needed, target_sentiment)
        
        # Shuffle to avoid obvious pattern
        random.shuffle(poem_lines)
        poem_lines = poem_lines[:total_lines_needed]
        
        return poem_lines, metadata
    
    @staticmethod
    def calculate_aesthetic(poem_lines, metadata):
        """Calculate aesthetic score based on multiple measures."""
        if not poem_lines:
            return 0, {}
        
        aesthetics = {}
        
        # Lyricism: how well lines flow (syllable consistency)
        syllable_counts = [line_metadata[line]['syllables'] for line in poem_lines]
        avg_syllables = sum(syllable_counts) / len(syllable_counts)
        std_dev = (sum((s - avg_syllables) ** 2 for s in syllable_counts) / len(syllable_counts)) ** 0.5
        aesthetics['lyricism'] = max(0, 10 - std_dev)
        
        # Sentiment coherence: lines match mood
        sentiment_vals = [line_metadata[line]['sentiment'] for line in poem_lines]
        sentiment_avg = sum(sentiment_vals) / len(sentiment_vals)
        coherence = 1 - (abs(sentiment_avg - (5 if metadata['sentiment'] == 'positive' else -5)) / 10)
        aesthetics['sentiment_coherence'] = max(0, coherence * 10)
        
        # Variety: avoid repetition
        unique_lines = len(set(poem_lines))
        aesthetics['variety'] = (unique_lines / len(poem_lines)) * 10
        
        # Thematic coherence: if noun phrase, check how many lines contain it
        if metadata.get('noun_phrase') and len(metadata['noun_phrase'].strip()) > 0:
            phrase_words = metadata['noun_phrase'].lower().split()
            matching_count = sum(1 for line in poem_lines if any(word in line.lower() for word in phrase_words))
            aesthetics['thematic_coherence'] = (matching_count / len(poem_lines)) * 10
        else:
            aesthetics['thematic_coherence'] = 5.0  # Neutral score when no phrase
        
        overall = sum(aesthetics.values()) / len(aesthetics)
        return overall, aesthetics


class CommentaryGenerator:
    """Generate contextual commentary for poems."""
    
    TEMPLATES = [
        "This poem emerges from a {mood} day, weaving {num_lines} lines into a reflective {template}.",
        "Crafted in a {mood} moment, this {template} explores lyrical beauty across {num_lines} carefully selected verses.",
        "A {mood} meditation presented as a {template}, this poem balances semantic richness with poetic form.",
    ]
    
    THEMATIC_TEMPLATES = [
        "Centered around the theme '{phrase}', this {mood} {template} weaves {num_lines} lines of poetic exploration.",
        "Exploring '{phrase}' through a {mood} lens, this {template} combines {num_lines} lines of linguistic artistry.",
        "The {mood} essence of '{phrase}' is captured in this {template}, expressed across {num_lines} carefully chosen verses.",
    ]
    
    @staticmethod
    def generate(poem_lines, metadata, aesthetics):
        """Generate commentary about the poem."""
        # Choose template based on whether noun phrase was used
        if metadata.get('noun_phrase') and len(metadata['noun_phrase'].strip()) > 0:
            templates = CommentaryGenerator.THEMATIC_TEMPLATES
            template = random.choice(templates)
            commentary = template.format(
                phrase=metadata['noun_phrase'],
                mood=metadata['mood'],
                num_lines=len(poem_lines),
                template=metadata['template']
            )
        else:
            templates = CommentaryGenerator.TEMPLATES
            template = random.choice(templates)
            commentary = template.format(
                mood=metadata['mood'],
                num_lines=len(poem_lines),
                template=metadata['template']
            )
        
        aesthetic_notes = []
        if aesthetics.get('lyricism', 0) > 7:
            aesthetic_notes.append("its consistent rhythm")
        if aesthetics.get('sentiment_coherence', 0) > 7:
            aesthetic_notes.append("emotional coherence")
        if aesthetics.get('variety', 0) > 7:
            aesthetic_notes.append("linguistic variety")
        if aesthetics.get('thematic_coherence', 0) > 6 and metadata.get('noun_phrase'):
            aesthetic_notes.append("thematic unity")
        
        if aesthetic_notes:
            commentary += f" Notable for {' and '.join(aesthetic_notes)}."
        
        return commentary


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["GET"])
def generate():
    """API endpoint for poem generation."""
    if not clean_lines:
        build_corpus_model()
    
    template_type = request.args.get("template", default="free")
    num_stanzas = request.args.get("stanzas", default=2, type=int)
    noun_phrase = request.args.get("noun_phrase", default=None)
    
    poem_lines, metadata = PoemGenerator.generate_poem(template_type, num_stanzas, noun_phrase)
    aesthetic_score, aesthetics = PoemGenerator.calculate_aesthetic(poem_lines, metadata)
    commentary = CommentaryGenerator.generate(poem_lines, metadata, aesthetics)
    
    return jsonify({
        'poem': poem_lines,
        'metadata': metadata,
        'aesthetic_score': aesthetic_score,
        'aesthetics': aesthetics,
        'commentary': commentary
    })


@app.route("/api/mood")
def get_mood():
    """Get current corpus mood."""
    if not clean_lines:
        build_corpus_model()
    return jsonify({'mood': PoemGenerator.get_mood()})


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON for uncaught exceptions."""
    response = jsonify({'error': str(e)})
    response.status_code = 500
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
