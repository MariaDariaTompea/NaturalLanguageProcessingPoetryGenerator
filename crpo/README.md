# Full-FACE Poetry Generator with Gutenberg Corpus (CRPO)

This is an integrated poetry generation system that combines:
- **Full-FACE** (Colton et al. 2012) architecture for computational poetry
- **CRPO** (Gutenberg Poetry Corpus) as the source material
- **Flask** web interface for interactive generation

## Features

### 1. **Mood Detection**
- Analyzes the sentiment of the entire Gutenberg corpus
- Determines whether the corpus mood is positive, negative, or neutral
- Influences poem generation parameters

### 2. **Sentiment Analysis**
- Each line is tagged with sentiment (-5 to +5 scale)
- Poems are generated with matching sentiment
- Ensures emotional coherence in generated work

### 3. **Template-Based Generation**
Supports three poem templates:
- **Free Form**: Unrestricted stanzas (default)
- **Couplet**: 2-line stanzas with rhyme constraints
- **Quatrain**: 4-line stanzas with ABAB rhyme scheme

### 4. **Linguistic Analysis**
- Syllable counting for rhythm analysis
- End-sound detection for potential rhyming
- Line length consistency metrics

### 5. **Aesthetic Scoring**
Each generated poem is evaluated on:
- **Lyricism**: Syllable consistency and flow
- **Sentiment Coherence**: How well the poem matches mood
- **Variety**: Avoids repetition and maintains freshness
- **Overall Aesthetic**: Combined score (0-10)

### 6. **Commentary Generation**
Automatic contextualization of each poem:
- Explains the mood and template used
- Highlights notable aesthetic properties
- Adds interpretive framing in the Full-FACE tradition

## Installation

```bash
# Navigate to the project directory
cd c:\Users\ilayd\Desktop\crpo

# Install dependencies
pip install -r requirements.txt
```

### First Run
Note: The first execution will download the Gutenberg Poetry Corpus (~250MB) and preprocess it. This takes 2-5 minutes.

## Running the Application

```bash
python deneme.py
```

Then open in your browser:
```
http://127.0.0.1:5000/
```

## API Endpoints

### Generate Poem
```
GET /api/generate?template=free&stanzas=2
```

**Parameters:**
- `template`: `free`, `couplet`, or `quatrain` (default: `free`)
- `stanzas`: Number of stanzas, 1-5 (default: `2`)

**Response:**
```json
{
  "poem": ["line 1", "line 2", ...],
  "metadata": {
    "template": "free",
    "mood": "positive",
    "sentiment": "positive",
    "stanzas": 2
  },
  "aesthetic_score": 7.3,
  "aesthetics": {
    "lyricism": 7.5,
    "sentiment_coherence": 8.2,
    "variety": 6.2
  },
  "commentary": "This poem emerges from a positive day..."
}
```

### Get Corpus Mood
```
GET /api/mood
```

**Response:**
```json
{
  "mood": "positive"
}
```

## Architecture

### Core Components

1. **SentimentAnalyzer**
   - Uses TextBlob for NLP sentiment detection
   - Scales to -5 to +5 range matching Full-FACE

2. **LinguisticAnalyzer**
   - Syllable counting (phonetic estimation)
   - End-sound extraction for rhyming
   - Line property extraction

3. **PoemTemplate**
   - Defines structural constraints
   - Maps templates to generation rules
   - Configurable rhyme and meter patterns

4. **PoemGenerator**
   - Selects lines by sentiment matching
   - Assembles poems according to templates
   - Enforces constraint satisfaction

5. **CommentaryGenerator**
   - Template-based commentary production
   - Highlights aesthetic achievements
   - Provides creative framing

## Corpus Properties

- **Size**: 3+ million individual poem lines
- **Source**: Project Gutenberg English poetry collection
- **Quality Filter**: Lines with 3-20 words, no digits, ASCII-safe
- **Sentiment Range**: -5 (very negative) to +5 (very positive)

## Web Interface

The Flask app provides:
- Real-time poem generation
- Interactive template selection
- Visual aesthetic scoring
- Mood indicator
- Automatic commentary display
- Responsive design

## How Full-FACE is Integrated

The system implements the four generative acts of Full-FACE:

1. **Examples**: Individual poems and lines generated from the corpus
2. **Concepts**: Poem templates and structural rules
3. **Aesthetics**: Multi-metric evaluation (lyricism, sentiment, variety)
4. **Framing**: Generated commentaries providing context

## Performance Notes

- **First request**: 2-5 minutes (corpus load + preprocessing)
- **Subsequent requests**: < 1 second
- **Corpus preprocessing**: Runs on first `build_corpus_model()` call
- **Model size**: ~300-500MB in memory (for 100k+ lines)

## Customization

### Add New Template
Edit `PoemTemplate.TEMPLATES` in `deneme.py`:
```python
'custom': {
    'stanzas': 3,
    'lines_per_stanza': 2,
    'constraints': ['your_constraints'],
    'sentiment_alternation': True
}
```

### Adjust Corpus Size
Change `max_lines` parameter in `build_corpus_model()`:
```python
build_corpus_model(max_lines=50000)  # Faster loading
```

### Modify Aesthetic Weights
Edit `calculate_aesthetic()` to change how scores are computed.

## References

- Colton, S., Goodwin, J., & Veale, T. (2012). *Full-FACE Poetry Generation*. ICCC 2012.
- Project Gutenberg: https://www.gutenberg.org/
- Gutenberg Poetry Corpus: https://huggingface.co/datasets/biglam/gutenberg-poetry-corpus

## Future Enhancements

- [ ] Real-time news article integration (like original Full-FACE)
- [ ] Advanced rhyme scheme enforcement
- [ ] Meter/stress pattern constraints
- [ ] Neural language model improvements
- [ ] Simile database enrichment
- [ ] Multi-language support
- [ ] Poetry publication pipeline

## License

This project integrates open-source components:
- Flask: BSD
- Datasets: Apache 2.0
- TextBlob: MIT
- Pronouncing: MIT
