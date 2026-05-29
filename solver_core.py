from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

WORD_LENGTH = 5
STARTING_GUESSES = ("aeros", "arose", "soare")
WORDS_PATH = Path(__file__).with_name("words.txt")

with WORDS_PATH.open() as words_file:
    WORD_LIST = [line.strip().lower() for line in words_file if line.strip()]

WORD_SET = set(WORD_LIST)


@dataclass(frozen=True)
class GuessTurn:
    guess: str
    feedback: str



@dataclass
class KnownWordRun:
    secret_word: str
    turns: list[GuessTurn]
    used_random_word: bool
    replaced_invalid_word: bool

    @property
    def tries(self) -> int:
        return len(self.turns)


class HelperFeedbackError(ValueError):
    """Raised when feedback cannot produce a valid next guess."""


@dataclass
class HelperSession:
    rng: random.Random = field(default_factory=random.Random)
    current_guess: str = field(init=False)
    tried_words: set[str] = field(default_factory=set)
    history: list[GuessTurn] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.current_guess = pick_starting_guess(self.rng)

    @property
    def turn(self) -> int:
        return len(self.history) + 1

    def apply_feedback(self, feedback: str) -> dict[str, object]:
        normalized_feedback = normalize_feedback(feedback)
        self.history.append(GuessTurn(guess=self.current_guess, feedback=normalized_feedback))

        if normalized_feedback == "G" * WORD_LENGTH:
            return {
                "done": True,
                "tries": len(self.history),
                "history": serialize_turns(self.history),
            }

        self.tried_words.add(self.current_guess)
        self.current_guess = choose_next_guess(
            candidates=filter_remaining_words(self.history),
            tried_words=self.tried_words,
            rng=self.rng,
        )
        return self.snapshot()

    def skip_guess(self) -> dict[str, object]:
        self.tried_words.add(self.current_guess)
        self.current_guess = choose_next_guess(
            candidates=filter_remaining_words(self.history),
            tried_words=self.tried_words,
            rng=self.rng,
        )
        return self.snapshot()

    def snapshot(self) -> dict[str, object]:
        return {
            "done": False,
            "guess": self.current_guess,
            "turn": self.turn,
            "history": serialize_turns(self.history),
        }


ProgressCallback = Callable[[int, int], None]


def pick_starting_guess(rng: random.Random) -> str:
    return rng.choice(STARTING_GUESSES)


def score_guess(secret_word: str, guess: str) -> str:
    feedback = ["N"] * WORD_LENGTH
    remaining_letters: dict[str, int] = {}

    for index, letter in enumerate(guess):
        if letter == secret_word[index]:
            feedback[index] = "G"
        else:
            secret_letter = secret_word[index]
            remaining_letters[secret_letter] = remaining_letters.get(secret_letter, 0) + 1

    for index, letter in enumerate(guess):
        if feedback[index] == "G":
            continue

        remaining_count = remaining_letters.get(letter, 0)
        if remaining_count > 0:
            feedback[index] = "Y"
            remaining_letters[letter] = remaining_count - 1

    return "".join(feedback)


def normalize_secret_word(
    secret_word: str | None,
    rng: random.Random,
) -> tuple[str, bool, bool]:
    if secret_word is None:
        return rng.choice(WORD_LIST), True, False

    normalized_word = secret_word.strip().lower()
    if normalized_word in {"", "r"}:
        return rng.choice(WORD_LIST), True, False

    if normalized_word not in WORD_SET:
        return rng.choice(WORD_LIST), True, True

    return normalized_word, False, False


def normalize_feedback(feedback: str) -> str:
    normalized_feedback = feedback.strip().upper()
    if len(normalized_feedback) != WORD_LENGTH:
        raise HelperFeedbackError(f"Feedback must be exactly {WORD_LENGTH} letters long.")

    invalid_letters = sorted({letter for letter in normalized_feedback if letter not in {"G", "Y", "N"}})
    if invalid_letters:
        joined_letters = ", ".join(invalid_letters)
        raise HelperFeedbackError(f"Feedback can only use G, Y, or N. Invalid: {joined_letters}")

    return normalized_feedback


def filter_remaining_words(
    turns: Iterable[GuessTurn],
    words: Iterable[str] | None = None,
) -> list[str]:
    candidate_words = WORD_LIST if words is None else words
    turn_history = tuple(turns)

    return [
        word
        for word in candidate_words
        if all(score_guess(word, turn.guess) == turn.feedback for turn in turn_history)
    ]


def choose_next_guess(candidates: Iterable[str], tried_words: set[str], rng: random.Random) -> str:
    untried_candidates = [candidate for candidate in candidates if candidate not in tried_words]
    if not untried_candidates:
        raise HelperFeedbackError("No words remain. The feedback so far conflicts with the solver rules.")
    return rng.choice(untried_candidates)


def solve_known_word(secret_word: str | None = None, rng: random.Random | None = None) -> KnownWordRun:
    active_rng = rng or random.Random()
    chosen_word, used_random_word, replaced_invalid_word = normalize_secret_word(secret_word, active_rng)
    guess = pick_starting_guess(active_rng)
    turns: list[GuessTurn] = []
    tried_words: set[str] = set()

    while True:
        feedback = score_guess(chosen_word, guess)
        turns.append(GuessTurn(guess=guess, feedback=feedback))
        if feedback == "G" * WORD_LENGTH:
            break

        tried_words.add(guess)
        guess = choose_next_guess(
            candidates=filter_remaining_words(turns),
            tried_words=tried_words,
            rng=active_rng,
        )

    return KnownWordRun(
        secret_word=chosen_word,
        turns=turns,
        used_random_word=used_random_word,
        replaced_invalid_word=replaced_invalid_word,
    )


def calculate_average_tries(
    words: Iterable[str] | None = None,
    rng: random.Random | None = None,
    progress_callback: ProgressCallback | None = None,
) -> float:
    words_to_solve = list(WORD_LIST if words is None else words)
    if not words_to_solve:
        raise ValueError("At least one word is required to calculate an average.")

    active_rng = rng or random.Random()
    total_tries = 0

    for index, word in enumerate(words_to_solve, start=1):
        total_tries += solve_known_word(secret_word=word, rng=active_rng).tries
        if progress_callback is not None:
            progress_callback(index, len(words_to_solve))

    return total_tries / len(words_to_solve)


def serialize_turns(turns: Iterable[GuessTurn]) -> list[dict[str, str]]:
    return [{"guess": turn.guess, "feedback": turn.feedback} for turn in turns]
