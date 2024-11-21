from flask import Flask, render_template, jsonify, request, session
import datetime
import os
import requests
import random
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a random secret key for sessions

def create_db():
    conn = sqlite3.connect('words.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_words (
        date TEXT PRIMARY KEY,
        word TEXT
    )
    ''')
    conn.commit()
    conn.close()

create_db()

def fetch_words():
    url = "https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt"
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

word_list = fetch_words()

def get_today_word():
    conn = sqlite3.connect('words.db')
    cursor = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT word FROM daily_words WHERE date = ?', (today,))
    result = cursor.fetchone()
    
    if result:
        return result[0]  
    else:
        word = random.choice(word_list)
        cursor.execute('INSERT INTO daily_words (date, word) VALUES (?, ?)', (today, word))
        conn.commit()
        return word

@app.route('/get_word', methods=['GET'])
def get_daily_word():
    word = get_today_word()
    return jsonify({'word': word})

@app.route('/')
def index():
    session['secret_word'] = get_today_word()  # Get the word for today
    session['guesses'] = []  # Clear the guesses for a new session
    return render_template('index.html')

@app.route('/guess', methods=['POST'])
def guess():
    data = request.json
    user_guess = data['guess']

    # Only check if secret word is in session
    if 'secret_word' not in session:
        return jsonify({'error': 'Game not initialized.'}), 400

    secret_word = session['secret_word']
    
    # Call the evaluation method
    result = evaluate_guess(secret_word, user_guess)

    # Store the guess and its result in the session
    session['guesses'].append({"guess": user_guess, "result": result})
    session.modified = True
    print(session['guesses'])  # This will print all previous guesses.
    # Return all previous guesses with their results
    return jsonify(session['guesses'])

def evaluate_guess(secret_word, user_guess):
    result = []
    secret_word_list = list(secret_word)
    user_guess_list = list(user_guess)

    # Checking for correct letters in correct position
    for i in range(len(user_guess_list)):
        if user_guess_list[i] == secret_word_list[i]:
            result.append({"letter": user_guess_list[i], "color": "green"})
            secret_word_list[i] = None  # Mark this letter as processed
        else:
            result.append({"letter": user_guess_list[i], "color": "gray"})  # Default color

    # Checking for correct letters in wrong positions
    for i in range(len(user_guess_list)):
        if result[i]["color"] == "gray" and user_guess_list[i] in secret_word_list:
            result[i]["color"] = "yellow"
            secret_word_list[secret_word_list.index(user_guess_list[i])] = None

    return result

if __name__ == '__main__':
    app.run(debug=True)