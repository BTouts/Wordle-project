import requests
import random
import sys

# URL of the text file
url = "https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt"

try:
    # Fetch the content from the URL
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Split the content into a list of words
    words = response.text.splitlines()

    # Choose a random word
    random_word = random.choice(words)

    print(f"Random Word: {random_word}")

except requests.RequestException as e:
    print(f"An error occurred: {e}")

hidden = list("-----")
count = 0
while count < 5:
    print(hidden)
    guess = input("Please guess a 5 letter word: ")
    for i, char in enumerate(random_word):
        if guess[i] == char:
            hidden[i] = random_word[i]
            count = count + 1
            if count == 5:
                print(hidden)
                break
