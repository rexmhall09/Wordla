def pickandplaygame():
    print("Select a game mode:")
    print("1 - You input a word, and the AI guesses.")
    print("2 - AI guesses, and you give feedback until it gets it.")
    print("3 - Calculate the average number of tries for the AI.")
    print("Type 'exit' to quit the game.")
    
    game_mode = input("Enter the number of the game mode you want to play: ")

    if game_mode == "1":
        from knownword import play as knownword_play
        knownword_play()
    elif game_mode == "2":
        from helper import play as helper_play
        helper_play()
    elif game_mode == "3":
        from testaverage import calculate_average_tries as testaverage_play
        testaverage_play()
    elif game_mode.lower() == "exit":
        print("Shutting Down...")
        exit()
    else:
        print("Invalid input, please try again.")
        pickandplaygame()

while True:
    pickandplaygame()
    play_again = input("Do you want to play again (y/n)? ").lower()
    if play_again == "n":
        print("Shutting Down...")
        exit()
    elif play_again == "y":
        continue
    else:
        print("Invalid input. Exiting the game.")
        exit()