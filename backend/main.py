"""
Flask application entry point. 
Handles web routes for the user interface and coordinates with the PoetryAPI.
"""
from flask import Flask, render_template, request, jsonify
from .api import PoetryAPI
import pronouncing

app = Flask(__name__, template_folder='../templates', static_folder='../static')
api = PoetryAPI(limit=20000)

@app.route('/')
def index():
    # Renders the main landing page for model selection
    return render_template('selection.html')

@app.route('/api/word-insight/<word>')
def word_insight(word):
    # Provides rhyme suggestions for a given word to the frontend
    clean_word = word.lower().replace('.', '').replace(',', '')
    rhymes = pronouncing.rhymes(clean_word)
    return jsonify({
        "word": clean_word,
        "suggestions": rhymes[:5]
    })

@app.route('/crpo', methods=['GET', 'POST'])
def crpo_page():
    # Handles poetry generation requests using the CRPO model
    result, selected_seed, line_count = None, "", 6
    if request.method == 'POST':
        line_count = int(request.form.get('line_count', 6))
        selected_seed = request.form.get('seed_word', '')
        lines = api.generate_crpo_poem(line_count=line_count, seed_word=selected_seed)
        result = {f"CRPO {line_count}-Line Poem": lines}
    
    popular_words = ["Nature", "Spirit", "Dreams", "Silence", "Shadows", "Eternal"]
    return render_template('crpo.html', result=result, popular_words=popular_words, 
                           selected_seed=selected_seed, line_count=line_count)

@app.route('/markov', methods=['GET', 'POST'])
def markov_page():
    # Handles poetry generation requests using the Markov model based on button action
    result, selected_seed, line_count = None, "", 4
    
    if request.method == 'POST':
        action = request.form.get('action')
        selected_seed = request.form.get('seed', '')

        # Sets the number of lines and title based on the selected button
        if action == 'stanza':
            line_count = 2
            title = "Stanza Composition (Couplet)"
        else:
            line_count = 4
            title = "4-Line Composition"
        
        lines = api.generate_markov_poem(line_count=line_count, seed_word=selected_seed)
        result = {title: lines}
        
    popular_words = ["Night", "Garden", "Winter", "Forest", "Light", "Memory"]
    return render_template('markov.html', result=result, popular_words=popular_words,
                           selected_seed=selected_seed, line_count=line_count)

if __name__ == "__main__":
    app.run(debug=True)