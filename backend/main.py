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
        # Select yerine slider'dan gelen line_count'u alıyoruz
        line_count = int(request.form.get('line_count', 4))
        selected_seed = request.form.get('seed_word', '')
        
        # API fonksiyonunu yeni parametreyle çağırıyoruz
        lines = api.generate_crpo_poem(line_count=line_count, seed_word=selected_seed)
        result = {f"Custom {line_count}-Line Poem": lines}
    
    popular_words = ["Nature", "Spirit", "Dreams", "Silence", "Shadows", "Eternal"]
    return render_template('crpo.html', result=result, popular_words=popular_words, selected_seed=selected_seed)
if __name__ == '__main__':
    app.run(debug=True, port=3002)