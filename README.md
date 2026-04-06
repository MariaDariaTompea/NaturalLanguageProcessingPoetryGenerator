## How it Works: The Markov Chain Algorithm

Unlike modern AI (like ChatGPT or Gemini) which use deep learning and millions of parameters, this project uses a purely **statistical method** called a **Markov Chain**.

### 1. No "Intelligence" Involved
The program does not understand what a poem is, nor does it understand human emotions. It simply looks at the training data and counts how often words appear next to each other.

### 2. The Chain Mechanism
The "Chain" is a dictionary of **States** and **Transitions**:
*   **State**: The current word (or pair of words).
*   **Transition**: A list of every word that has ever followed that state in your corpus.

**Example (Bigram Logic):**
If your training corpus has the phrase: *"The stars are bright"*, the model learns:
- **"The"** is followed by **"stars"**.
- **"stars"** is followed by **"are"**.
- **"are"** is followed by **"bright"**.

### 3. Generating the Poem
To "compose" a poem, the program:
1.  **Picks a Random Start**: It selects any word from the corpus to begin.
2.  **Consults the Map**: It looks up the current word in its dictionary to see what words usually follow it.
3.  **Rolls the Dice**: If the word *"stars"* is followed by *"are"* 10 times and *"shine"* 5 times, there is a higher mathematical probability it will pick *"are"*.
4.  **Repeats**: It moves to the new word and repeats the process until the poem is finished.

### 4. Why Trigrams (Order 3) are Better
- **Unigrams** (1 word) have no memory. They pick words at random based on frequency.
- **Bigrams** (2 words) remember 1 word back. This creates basic sentences.
- **Trigrams** (3 words) remember the last **two** words. Since English grammar often relies on pairs (Adjective-Noun-Verb), Trigrams make the poem feel much more "human" and logical, simply because they are copying larger chunks of successful human writing.

## Features

- **No External APIs**: Everything runs locally on your machine.
- **Pure Statistics**: A transparent, mathematical approach to creativity.
- **Web Studio**: A premium, modern web interface for interactive poetry generation.
- **Preprocessing**: Cleans the input text (lowercasing, tokenization).
- **Markov Chain Modeling**: 
  - **Unigram (Order 1)**: Predicts the next word based on the current word.
  - **Bigram (Order 2)**: Predicts the next word based on the previous two words, producing more coherent output.
  - **Trigram (Order 3)**: High-coherence modeling available in the web interface (Recommended).
- **Randomized Generation**: Starts with a random state and selects transitions statistically.
- **Customizable Output**: Formats the text into poetic structures with line breaks.
- **Interactive Muse**: Real-time TAB-to-fill recommendations using a back-off statistical model.

## Potential Improvements
- **Part-of-Speech Tagging**: Use NLTK or spaCy to ensure grammatical correctness (e.g., Noun-Verb agreement).
- **User Input**: Allow users to provide a custom starting word.
- **Rhythm and Rhyme**: Implement constraints to match specific poetic meters (like iambic pentameter) or rhyme schemes.

---
*Created as part of the Year 3 Semester 2 Specialist English NLP practice.*
