from flask import Flask, render_template, request
from generator import MarkovGenerator
import os

app = Flask(__name__)

# Initialize generator with the local corpus
# Using order=3 for better coherence
corpus_path = os.path.join(os.path.dirname(__file__), "corpus.txt")
gen = MarkovGenerator(corpus_path, order=3) if os.path.exists(corpus_path) else None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    mode = None
    seed = None
    popular_words = []
    
    if gen:
        popular_words = [w for w, c in gen.get_popular_words(20)]
    
    if request.method == "POST":
        action = request.form.get("action")
        seed = request.form.get("seed")
        
        if gen:
            if action == "stanza":
                result = gen.generate_stanza(seed_word=seed)
                mode = "stanza"
            elif action == "lyrics":
                result = gen.generate_full_lyrics(seed_word=seed)
                mode = "lyrics"
                
    return render_template("index.html", 
                           result=result, 
                           mode=mode, 
                           popular_words=popular_words,
                           selected_seed=seed)

if __name__ == "__main__":
    app.run(debug=True, port=5000) # Reverted to port 5000 as per original GitHub setting