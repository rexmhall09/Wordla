from __future__ import annotations

from tqdm import tqdm

from solver_core import WORD_LIST, calculate_average_tries


def calculate_average_tries_with_progress() -> float:
    with tqdm(total=len(WORD_LIST)) as progress_bar:
        average_tries = calculate_average_tries(
            progress_callback=lambda completed, total: progress_bar.update(completed - progress_bar.n)
        )

    print(f"Average guesses: {average_tries:.3f}")
    return average_tries


if __name__ == "__main__":
    calculate_average_tries_with_progress()
