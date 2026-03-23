def print_menu() -> None:
    print("Select a mode:")
    print("1 - Solve a word you enter.")
    print("2 - Enter feedback for a live game.")
    print("3 - Benchmark the solver.")
    print("4 - Open the website.")
    print("Type 'exit' to quit.")


def run_selected_mode(game_mode: str) -> bool:
    if game_mode == "1":
        from knownword import play as knownword_play

        knownword_play()
        return True

    if game_mode == "2":
        from helper import play as helper_play

        helper_play()
        return True

    if game_mode == "3":
        from testaverage import calculate_average_tries_with_progress

        calculate_average_tries_with_progress()
        return True

    if game_mode == "4":
        from website import launch_website

        launch_website()
        return False

    if game_mode.lower() == "exit":
        print("Shutting down...")
        return False

    print("Invalid input. Please try again.")
    return True


def main() -> None:
    while True:
        print_menu()
        game_mode = input("Choose a mode: ").strip()
        should_prompt_replay = run_selected_mode(game_mode)
        if not should_prompt_replay:
            return

        play_again = input("Run another mode? (y/n): ").strip().lower()
        if play_again == "y":
            continue
        if play_again == "n":
            print("Shutting down...")
            return

        print("Invalid input. Exiting.")
        return


if __name__ == "__main__":
    main()
