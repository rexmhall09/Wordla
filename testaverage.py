import random
from tqdm import tqdm

filename = "words.txt"
word_list = []
with open(filename) as file:
    while line := file.readline():
        word_list.append(line.rstrip())

alphabet = "abcdefghijklmnopqrstuvwxyz"

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

def modifyKnowledge(chosen, guess, knowledge):
    if knowledge == {}:
        knowledge["letters"] = {}
        knowledge["must"] = []
        for _ in range(len(guess)):
            knowledge["letters"][_] = set(alphabet)

    results = result(chosen, guess)
    for index in range(len(results)):
        if results[index] == "G":
            knowledge["letters"][index] = set([guess[index]])
            if guess[index] not in knowledge["must"]:
                knowledge["must"].append(guess[index])
        elif results[index] == "Y":
            knowledge["letters"][index].discard(guess[index])
            if guess[index] not in knowledge["must"]:
                knowledge["must"].append(guess[index])
        elif results[index] == "N":
            for _ in range(len(guess)):
                if guess[index] in knowledge["letters"][_]:
                    knowledge["letters"][_].discard(guess[index])
    return knowledge, results

def modifyRemaining(chosen, guess, knowledge):
    remaining = []

    knowledge, results = modifyKnowledge(chosen, guess, knowledge)
    for word in word_list:
        possible = True
        for index in range(len(word)):
            letter = word[index]
            if letter not in knowledge["letters"][index]:
                possible = False
        for letter in knowledge["must"]:
            if letter not in word:
                possible = False
        if possible:
            remaining.append(word)
    return remaining, knowledge, results

def calculate_average_tries():
    total_tries = 0
    total_words = len(word_list)

    for word in tqdm(word_list):
        guess = random.choice(["adieu", "orate", "audio"])
        tries = 1
        triedWords = []
        knowledge = {}

        while True:
            guesslist, knowledge, results = modifyRemaining(word, guess, knowledge)
            if results == ["G", "G", "G", "G", "G"]:
                break
            else:
                guess = random.choice(guesslist)
                while guess in triedWords:
                    guesslist.remove(guess)
                    guess = random.choice(guesslist)
                triedWords.append(guess)
                tries += 1

        total_tries += tries

    average_tries = total_tries / total_words
    print("average"+str(average_tries))
    return average_tries

if __name__ == "__main__":
    average_tries = calculate_average_tries()
    print(f"Average number of tries: {average_tries}")
