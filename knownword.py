from __future__ import annotations

from solver_core import solve_known_word


PROMPT = "Enter target word (r for random): "


def play() -> None:
    word = input(PROMPT).lower()
    run = solve_known_word(secret_word=word)

    if run.replaced_invalid_word:
        print("Word not in list. Using a random word instead.")

    for turn in run.turns:
        print(turn.guess, ":", list(turn.feedback))

    print(f"Solved '{run.secret_word}' in {run.tries} guesses.\n")


if __name__ == "__main__":
    play()
