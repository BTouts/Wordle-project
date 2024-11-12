import requests
import random
from flask import Flask, render_template, jsonify, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Fetch words from the URL
def fetch_words():
    url = "https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt"
    response = requests.get(url)
    response.raise_for_status()  # Ensure a successful request
    return response.text.splitlines()

# Choose a random word
word_list = fetch_words()

@app.route('/')
def index():
    # Initialize the game state
    session['secret_word'] = random.choice(word_list).lower()
    session['hidden'] = list("-----")
    session['count'] = 0
    return render_template('index.html')

@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.json['guess'].lower()
    secret_word = session['secret_word']
    hidden = session['hidden']
    count = session['count']
    
    result = {}
    if user_guess == secret_word:
        result = {"correct": True}
        hidden = list(secret_word)  # Reveal the word if guessed correctly
    else:
        for i, char in enumerate(secret_word):
            if user_guess[i] == char:
                hidden[i] = secret_word[i]  # Keep track of correct letters

    count += 1

    # Update the session values
    session['hidden'] = hidden
    session['count'] = count
    result['hidden'] = ''.join(hidden)
    result['correct'] = False  # Default to incorrect, unless guessed word matches

    # Check if word is fully guessed
    if ''.join(hidden) == secret_word:
        result['correct'] = True

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)