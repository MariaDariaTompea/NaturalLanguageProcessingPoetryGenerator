from flask import Flask, render_template, request
from generator import MarkovGenerator
import os

app = Flask(__name__)
gen = MarkovGenerator("corpus.txt") if os.path.exists("corpus.txt") else None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    mode = None
    if request.method == "POST":
        action = request.form.get("action")
        if gen:
            if action == "stanza":
                result = gen.generate_stanza()
                mode = "stanza"
            elif action == "lyrics":
                result = gen.generate_full_lyrics()
                mode = "lyrics"
    return render_template("index.html", result=result, mode=mode)

if __name__ == "__main__":
    app.run(debug=True)