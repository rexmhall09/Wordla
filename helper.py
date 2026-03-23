from __future__ import annotations

from solver_core import HelperFeedbackError, HelperSession


PROMPT = "Enter feedback (G/Y/N). Use any other 5 letters to skip this guess: "


def play() -> None:
    session = HelperSession()

    while True:
        print("Current guess:", session.current_guess.upper())
        feedback = input(PROMPT).upper()

        if len(feedback) == 5 and any(letter not in {"G", "Y", "N"} for letter in feedback):
            response = session.skip_guess()
        else:
            try:
                response = session.apply_feedback(feedback)
            except HelperFeedbackError as exc:
                print(exc)
                continue

        if response["done"]:
            print(f"Solved in {response['tries']} guesses.\n")
            return


if __name__ == "__main__":
    play()
