import random

filename = "words.txt"
word_list = []
with open(filename) as file:
    while line := file.readline():
        word_list.append(line.rstrip())

alphabet=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

def modifyKnowledge(guess, feedback, knowledge):
    if knowledge=={}:
        knowledge["letters"]={}
        knowledge["must"]=[]
        for _ in range(len(guess)):
                knowledge["letters"][_]=alphabet.copy()
    for index in range(len(feedback)):
        if feedback[index]=="G":
            knowledge["letters"][index]=[guess[index]]
            if guess[index] not in knowledge["must"]:
                knowledge["must"].append(guess[index])
        elif feedback[index]=="Y":
            knowledge["letters"][index].remove(guess[index])
            if guess[index] not in knowledge["must"]:
                knowledge["must"].append(guess[index])
        elif feedback[index]=="N":
            for _ in range(len(guess)):
                if guess[index] in knowledge["letters"][_]:
                    knowledge["letters"][_].remove(guess[index])
    return knowledge

def modifyRemaining(guess, knowledge, feedback):
    remaining = []

    knowledge = modifyKnowledge(guess, feedback, knowledge)
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
    return remaining, knowledge


def play():
    guess = random.choice(["aeros", "arose", "soare"])
    results = []
    tries = 1
    triedWords = []
    knowledge = {}
    working = True
    while working:
        print("Current guess:", guess)
        feedback = input("Please enter feedback (G for Green, Y for Yellow, N for None, and any letter for no data(if you cant enter the word type aaaaa)): ").upper()
        guesslist, knowledge = modifyRemaining(guess, knowledge, feedback)
        if feedback == "GGGGG":
            working = False
        else:
            guess = random.choice(guesslist)
            while guess in triedWords:
                guesslist.remove(guess)
                guess = random.choice(guesslist)
            triedWords.append(guess)
            tries += 1
    print("It took " + str(tries) + " tries to find the word.\n")
