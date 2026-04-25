from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backhand.models.markov_model import EnhancedMarkovPoet
from backhand.utils.nlp_helpers import load_corpus
import os

app = FastAPI(title="Symphony of Words - Strategic Brain API")

# Setup CORS - Allow your frontend to communicate with this python brain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all. You can restrict to ["http://localhost:8080"] later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Poet Brain at startup
poet_brain = None

@app.on_event("startup")
async def startup_event():
    global poet_brain
    print("Waking up the Strategic Brain...")
    
    corpus_path = os.path.join("data", "large_corpus.txt")
    if not os.path.exists(corpus_path):
        corpus_path = os.path.join("data", "corpus.txt")
        
    text = load_corpus(corpus_path)
    if text:
        poet_brain = EnhancedMarkovPoet(text, order=2)
        print("Poet Brain initialized with Graph-Relational memory.")
    else:
        print("Failed to load corpus. Strategic Brain is empty.")

@app.get("/status")
def get_status():
    return {"status": "online", "brain": "EnhancedMarkovPoet (Relational + Beam Search)"}

@app.get("/generate")
def generate(
    strategy: str = "forward", 
    theme: str = None, 
    length: int = 40, 
    rhyme_scheme: str = "AABBCC",
    rhythm: str = "0101010101"
):
    if not poet_brain:
        return {"error": "Brain not initialized"}
        
    print(f"Generating poem with strategy: {strategy} and theme: {theme}")
    
    if strategy == "rhyme":
        result = poet_brain.generate_rhymed_poem(rhyme_scheme=rhyme_scheme, theme_word=theme)
    elif strategy == "rhythm":
        result = poet_brain.generate_rhythmic_poem(rhythm_template=rhythm, lines_count=length // 6, theme_word=theme)
    else:
        # Default: Advanced Beam Search
        result = poet_brain.generate_poem(length=length, theme_word=theme)
        
    return {"poem": result, "strategy_used": strategy}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
