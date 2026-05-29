from __future__ import annotations

import random
import unittest

from solver_core import HelperFeedbackError, HelperSession, score_guess, solve_known_word
from website import WordlaWebApi


class SolverCoreTests(unittest.TestCase):
    def test_score_guess_marks_expected_feedback(self) -> None:
        self.assertEqual(score_guess("crane", "soare"), "NNGYG")
        self.assertEqual(score_guess("clang", "llama"), "NGGNN")
        self.assertEqual(score_guess("clang", "chaap"), "GNGNN")

    def test_solve_known_word_finishes_on_secret(self) -> None:
        run = solve_known_word(secret_word="crane", rng=random.Random(7))

        self.assertGreaterEqual(run.tries, 1)
        self.assertEqual(run.secret_word, "crane")
        self.assertEqual(run.turns[-1].guess, "crane")
        self.assertEqual(run.turns[-1].feedback, "GGGGG")

    def test_helper_session_rejects_invalid_feedback(self) -> None:
        session = HelperSession(rng=random.Random(3))

        with self.assertRaises(HelperFeedbackError):
            session.apply_feedback("abcde")

    def test_helper_session_accepts_immediate_solve(self) -> None:
        session = HelperSession(rng=random.Random(4))
        response = session.apply_feedback("GGGGG")

        self.assertTrue(response["done"])
        self.assertEqual(response["tries"], 1)
        self.assertEqual(len(response["history"]), 1)

    def test_helper_session_handles_duplicate_letter_feedback(self) -> None:
        session = HelperSession(rng=random.Random(0))

        for _ in range(10):
            feedback = score_guess("clang", session.current_guess)
            response = session.apply_feedback(feedback)
            if response["done"]:
                self.assertEqual(response["history"][-1]["guess"], "clang")
                self.assertEqual(response["history"][-1]["feedback"], "GGGGG")
                return

        self.fail("Helper did not solve clang with duplicate-letter feedback.")

    def test_helper_session_keeps_state_after_conflicting_feedback(self) -> None:
        session = HelperSession(rng=random.Random(0))
        current_guess = session.current_guess

        with self.assertRaises(HelperFeedbackError):
            session.apply_feedback("GGGGN")

        self.assertEqual(session.current_guess, current_guess)
        self.assertEqual(session.history, [])
        response = session.apply_feedback(score_guess("clang", current_guess))

        self.assertFalse(response["done"])
        self.assertEqual(response["history"][0]["guess"], current_guess)


class WebsiteApiTests(unittest.TestCase):
    def test_mode_one_response_contains_turns(self) -> None:
        api = WordlaWebApi(rng=random.Random(11))
        response = api.solve_mode_one("crane")

        self.assertEqual(response["secretWord"], "crane")
        self.assertGreaterEqual(response["tries"], 1)
        self.assertEqual(response["turns"][-1]["feedback"], "GGGGG")

    def test_helper_session_is_removed_after_completion(self) -> None:
        api = WordlaWebApi(rng=random.Random(13))
        session = api.start_helper_session()
        response = api.submit_helper_feedback(session["sessionId"], "GGGGG")

        self.assertTrue(response["done"])
        with self.assertRaises(KeyError):
            api.submit_helper_feedback(session["sessionId"], "GGGGG")


if __name__ == "__main__":
    unittest.main()
