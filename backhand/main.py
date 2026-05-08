import os
import sys
from flask import Flask, render_template, request, jsonify # render_template_string yerine render_template
from flask_cors import CORS

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.nlp_helpers import get_clean_corpus
from models.markov_model import CMPPoet
from api import PoetryAPI

app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')
CORS(app)

# Initialize the poetry API
poetry_api = None

def init_poetry_api():
    global poetry_api
    if poetry_api is None:
        poetry_api = PoetryAPI()
    return poetry_api

@app.route('/')
def index():
    # Templates klasöründeki selection.html'i ana sayfa yapalım
    # Çünkü senin görsel efektlerin bu dosyalarda.
    return render_template('selection.html')

@app.route('/markov', methods=['GET', 'POST'])
def markov_page():
    result = None
    selected_seed = None
    if request.method == 'POST':
        selected_seed = request.form.get('seed')
        api = init_poetry_api()
        poem_line = api.generate(length=6, theme_words=[selected_seed] if selected_seed else [])
        # HTML'in .items() beklediği yer için veriyi sözlük yapıyoruz:
        result = {"Generated Verse": [poem_line]} 
        
    return render_template('markov.html', 
                           popular_words=["spirit", "soul", "eternal", "night", "light"],
                           result=result,
                           selected_seed=selected_seed)

@app.route('/crpo', methods=['GET', 'POST'])
def crpo_page():
    result = None
    selected_seed = None
    if request.method == 'POST':
        selected_seed = request.form.get('seed')
        api = init_poetry_api()
        poem_line = api.generate(length=6, theme_words=[selected_seed] if selected_seed else [])
        # Aynı şekilde burada da sözlük yapıyoruz:
        result = {"Optimized Verse": [poem_line]}

    return render_template('crpo.html', 
                           popular_words=["nature", "sea", "dream", "memory"],
                           result=result,
                           selected_seed=selected_seed)


@app.route('/generate', methods=['POST'])
def generate_poetry():
    try:
        data = request.get_json()
        length = data.get('length', 6)
        theme_pos = data.get('theme_pos', 2)
        theme_words = data.get('theme_words', [])

        api = init_poetry_api()
        line = api.generate(length=length, theme_pos=theme_pos, theme_words=theme_words)

        return jsonify({'success': True, 'poetry': line})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Symphony of Words 3002 portunda baslatiliyor...")
    app.run(debug=True, port=3002)