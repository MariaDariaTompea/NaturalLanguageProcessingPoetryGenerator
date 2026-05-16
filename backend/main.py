from flask import Flask, render_template, request
from .api import PoetryAPI

app = Flask(__name__, template_folder='../templates', static_folder='../static')
api = PoetryAPI(limit=20000)

@app.route('/')
def index():
    return render_template('selection.html')

@app.route('/crpo', methods=['GET', 'POST'])
def crpo_page():
    result = None
    selected_seed = ""
    if request.method == 'POST':
        form = request.form.get('poetic_form', 'quatrain')
        selected_seed = request.form.get('seed_word', '')
        # Makale: Kullanıcı form seçer -> Taslak oluşturulur [cite: 42, 47]
        lines = api.generate_crpo_poem(form, seed_word=selected_seed)
        result = {f"CRPO {form.capitalize()}": lines}
        
    # Öneri kelimeleri listesi
    popular_words = ["Nature", "Spirit", "Dreams", "Silence", "Shadows", "Eternal"]
    return render_template('crpo.html', result=result, popular_words=popular_words, selected_seed=selected_seed)

if __name__ == '__main__':
    app.run(debug=True, port=3002)