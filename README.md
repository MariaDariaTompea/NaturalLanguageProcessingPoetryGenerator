# Natural Language Poetry Generator

A web-based poetry generator that combines two creative generation engines:

- **CRPO**: a character-level neural poetry model using bidirectional LSTMs and attention.
- **Markov**: a backward Markov chain model that generates rhymed lines by constructing lines from their endings.

The app provides a simple Flask front end where users can choose a seed word and generate poems in different styles.

## Features

- Generate poems with the **CRPO model** using character-level language modeling and temperature sampling.
- Generate poems with the **Markov model** using rhyme-aware backward generation.
- Select poem length and seed words through the browser UI.
- Get rhyme suggestions for words via a built-in `/api/word-insight/<word>` endpoint.

## Project Structure

- `backend/`
  - `main.py` — Flask application entry point and route handlers.
  - `api.py` — PoetryAPI wrapper that initializes both generation engines.
  - `models/crpo_model.py` — Character-based LSTM + attention model.
  - `models/markov_model.py` — Backward Markov chain model with rhyme support.
  - `utils/nlp_helpers.py` — Corpus loading and preprocessing utilities.
- `templates/` — Jinja2 templates for selection, CRPO, and Markov pages.
- `static/` — Front-end assets including CSS, JavaScript, and images.
- `data/` — Corpus files used for training and generation.
- `crpo_weights.weights.h5` — Optional pre-trained weights for the CRPO model.
- `requirements.txt` — Python dependencies.

## Requirements

Install dependencies from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

The app depends on:

- `flask`
- `tensorflow`
- `keras`
- `numpy`
- `pronouncing`
- `regex`
- `datasets`
- `huggingface-hub`

## Running the App

From the project root, run:

```powershell
python backend/main.py
```

Then open the browser at:

```text
http://127.0.0.1:5000
```

If `crpo_weights.weights.h5` is present, the CRPO model loads the weights automatically. Otherwise, the CRPO model starts untrained and may produce lower-quality output.

## How to Use

1. Open the selection page at `/`.
2. Choose the CRPO or Markov generation page.
3. Enter a seed word and select the poem style or length.
4. Submit the form to generate a poem.

## Model Details

- `CRPOModel` creates a character-level embedding, two bidirectional LSTM layers, an attention mechanism, and a softmax output over the character vocabulary.
- `MarkovPoetryModel` trains on the corpus text, stores reversed n-gram transitions, and generates lines from rhyme words backward to the start.

## Notes

- The `data/raw_corpus_debug.txt` and `data/processed_corpus_debug.txt` files contain the source text used for training and generation.
- The application uses simple line filtering to improve output quality by removing invalid endings and very short lines.
- The rhyme suggestion endpoint can be extended for more advanced rhyme or thesaurus support.

## License

This repository is provided as-is for experimentation and learning with poetry generation.
