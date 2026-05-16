from flask import Flask, render_template, request
from .api import PoetryAPI

app = Flask(__name__, template_folder='../templates', static_folder='../static')
api = PoetryAPI(limit=20000)

@app.route('/')
def index():
    return render_template('selection.html')

@app.route('/markov', methods=['GET', 'POST'])
def markov_page():
    result = None
    selected_seed = ""
    if request.method == 'POST':
        action = request.form.get('action')
        selected_seed = request.form.get('seed', '')
        
        # Makaleye göre dize sayısı (couplet için 2, full poem için 4-8)
        line_count = 2 if action == 'stanza' else 4
        
        # API'deki yeni markov fonksiyonunu çağırıyoruz
        lines = api.generate_markov_poem(line_count=line_count, seed_word=selected_seed)
        result = {f"Markov {line_count}-Line Composition": lines}
    
    popular_words = ["Music", "Nature", "Today", "Paradise", "Love"] # Makaledeki örnek temalar
    return render_template('markov.html', result=result, popular_words=popular_words, selected_seed=selected_seed)

@app.route('/crpo', methods=['GET', 'POST'])
def crpo_page():
    result = None
    selected_seed = ""
    line_count = 4  # <-- Varsayılan değeri buraya ekledik (Hatanın çözümü bu)
    
    if request.method == 'POST':
        # Formdan gelen değeri al, gelmezse varsayılan 4 olsun
        line_count = int(request.form.get('line_count', 4))
        selected_seed = request.form.get('seed_word', '')
        
        lines = api.generate_crpo_poem(line_count=line_count, seed_word=selected_seed)
        result = {f"Custom {line_count}-Line Poem": lines}
    
    popular_words = ["Nature", "Spirit", "Dreams", "Silence", "Shadows", "Eternal"]
    
    return render_template('crpo.html', 
                           result=result, 
                           popular_words=popular_words, 
                           selected_seed=selected_seed, 
                           line_count=line_count) # Artık her zaman bir değere sahip


if __name__ == '__main__':
    app.run(debug=True, port=3002)