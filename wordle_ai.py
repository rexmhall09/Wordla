import random
import collections

filename = "words.txt"
word_list = []
with open(filename) as file:
    for line in file:
        word_list.append(line.rstrip())

alphabet = "abcdefghijklmnopqrstuvwxyz"

def has_duplicate_letters(word):
    return len(set(word)) != len(word)

def get_word_score(word, letter_freq):
    return sum(letter_freq[letter] for letter in word)

def get_most_frequent_words(word_list, letter_freq):
    valid_words = [word for word in word_list if not has_duplicate_letters(word)]
    most_freq_words = sorted(valid_words, key=lambda word: get_word_score(word, letter_freq), reverse=True)
    return most_freq_words

def result(word, guess):
    result = []
    for index in range(len(guess)):
        if guess[index] == word[index]:
            result.append("G")
        elif guess[index] in word:
            result.append("Y")
        else:
            result.append("N")
    return result

def initialize_knowledge(guess):
    return {
        "letters": {index: set(alphabet) for index in range(len(guess))},
        "must": [],
        "not_in_word": set(),
    }

def modifyKnowledge(chosen, guess, knowledge):
    if not knowledge:
        knowledge = initialize_knowledge(guess)

    results = result(chosen, guess)
    for index, res in enumerate(results):
        if res == "G":
            confirmed_letter = guess[index]
            knowledge["letters"][index] = set(confirmed_letter)
            if confirmed_letter not in knowledge["must"]:
                knowledge["must"].append(confirmed_letter)
            for idx in range(len(guess)):
                if idx != index and confirmed_letter in knowledge["letters"][idx]:
                    knowledge["letters"][idx].discard(confirmed_letter)
        elif res == "Y":
            knowledge["letters"][index].discard(guess[index])
            if guess[index] not in knowledge["must"]:
                knowledge["must"].append(guess[index])
        elif res == "N":
            excluded_letter = guess[index]
            for idx in range(len(guess)):
                if excluded_letter in knowledge["letters"][idx]:
                    knowledge["letters"][idx].discard(excluded_letter)
            knowledge["not_in_word"].add(excluded_letter)
    return knowledge, results

def modifyRemaining(chosen, guess, word_list, knowledge):
    remaining = []

    knowledge, results = modifyKnowledge(chosen, guess, knowledge)
    for word in word_list:
        possible = True
        for index, letter in enumerate(word):
            if letter not in knowledge["letters"][index] or letter in knowledge["not_in_word"]:
                possible = False
        for letter in knowledge["must"]:
            if letter not in word:
                possible = False
        if possible:
            remaining.append(word)
    return remaining, knowledge, results

def play():
    # Pre-compute letter frequencies.
    letter_freq = collections.Counter(''.join(word_list))

    most_freq_words = get_most_frequent_words(word_list, letter_freq)
    word = random.choice(most_freq_words)
    remaining_words = most_freq_words.copy()
    guess = most_freq_words[0] # start with most common word

    tries = 1
    triedWords = []
    knowledge = {}

    while True:
        remaining_words, knowledge, results = modifyRemaining(word, guess, remaining_words, knowledge)
        print(guess, ":", results)
        if results == ["G"] * len(guess):
            break
        else:
            # Recompute letter frequencies
            letter_freq = collections.Counter(''.join(remaining_words)) 

            guess = max(remaining_words, key=lambda word: get_word_score(word, letter_freq))
            while guess in triedWords:
                remaining_words.remove(guess)
                guess = max(remaining_words, key=lambda word: get_word_score(word, letter_freq))

            triedWords.append(guess)
            tries += 1

    print(f"It took {tries} tries to find '{word}'.\n")

if __name__ == "__main__":
    play()