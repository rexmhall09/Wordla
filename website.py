from __future__ import annotations

import json
import random
import threading
import uuid
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from typing import cast

from solver_core import (
    WORD_LIST,
    WORDS_PATH,
    GuessTurn,
    HelperFeedbackError,
    HelperSession,
    calculate_average_tries,
    solve_known_word,
)

WEB_DIR = Path(__file__).with_name("web")


class WordlaWebApi:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._sessions: dict[str, HelperSession] = {}
        self._lock = threading.Lock()

    def solve_mode_one(self, secret_word: str | None) -> dict[str, object]:
        with self._lock:
            run = solve_known_word(secret_word=secret_word, rng=self._rng)
            return {
                "secretWord": run.secret_word,
                "tries": run.tries,
                "usedRandomWord": run.used_random_word,
                "replacedInvalidWord": run.replaced_invalid_word,
                "turns": [serialize_turn(turn) for turn in run.turns],
            }

    def start_helper_session(self) -> dict[str, object]:
        with self._lock:
            session_id = str(uuid.uuid4())
            session = HelperSession(rng=self._rng)
            self._sessions[session_id] = session
            return {"sessionId": session_id, **session.snapshot()}

    def submit_helper_feedback(self, session_id: str, feedback: str) -> dict[str, object]:
        with self._lock:
            session = self._get_session(session_id)
            response = session.apply_feedback(feedback)
            if response["done"]:
                self._sessions.pop(session_id, None)
            return {"sessionId": session_id, **response}

    def skip_helper_guess(self, session_id: str) -> dict[str, object]:
        with self._lock:
            session = self._get_session(session_id)
            return {"sessionId": session_id, **session.skip_guess()}

    def calculate_average(self) -> dict[str, object]:
        with self._lock:
            average_tries = calculate_average_tries(rng=self._rng)
            return {
                "average": round(average_tries, 3),
                "wordsTested": len(WORD_LIST),
            }

    def _get_session(self, session_id: str) -> HelperSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError("Session not found. Start again.") from exc


class WordlaServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], api: WordlaWebApi) -> None:
        super().__init__(server_address, WordlaRequestHandler)
        self.api = api


class WordlaRequestHandler(SimpleHTTPRequestHandler):
    server_version = "WordlaHTTP/1.0"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    @property
    def api(self) -> WordlaWebApi:
        return cast(WordlaServer, self.server).api

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/words.txt":
            self.send_words()
            return

        self.path = "/index.html" if parsed_path.path == "/" else parsed_path.path
        super().do_GET()

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path)
        try:
            if parsed_path.path == "/api/mode1/solve":
                payload = self.read_json_body()
                self.send_json(
                    HTTPStatus.OK,
                    self.api.solve_mode_one(secret_word=payload.get("secretWord")),
                )
                return

            if parsed_path.path == "/api/mode2/start":
                self.send_json(HTTPStatus.OK, self.api.start_helper_session())
                return

            if parsed_path.path == "/api/mode2/feedback":
                payload = self.read_json_body()
                session_id = self.require_string(payload, "sessionId")
                feedback = self.require_string(payload, "feedback")
                self.send_json(
                    HTTPStatus.OK,
                    self.api.submit_helper_feedback(session_id=session_id, feedback=feedback),
                )
                return

            if parsed_path.path == "/api/mode2/skip":
                payload = self.read_json_body()
                session_id = self.require_string(payload, "sessionId")
                self.send_json(HTTPStatus.OK, self.api.skip_helper_guess(session_id=session_id))
                return

            if parsed_path.path == "/api/mode3/average":
                self.send_json(HTTPStatus.OK, self.api.calculate_average())
                return

            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown route."})
        except HelperFeedbackError as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except ValueError as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except KeyError as exc:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": str(exc)})

    def list_directory(self, path: str):
        self.send_error(HTTPStatus.NOT_FOUND, "File not found")
        return None

    def log_message(self, format: str, *args) -> None:
        return

    def read_json_body(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            parsed_body = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Body must be valid JSON.") from exc

        if not isinstance(parsed_body, dict):
            raise ValueError("Body must be a JSON object.")

        return parsed_body

    def require_string(self, payload: dict[str, object], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} is required.")
        return value.strip()

    def send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        response_body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)


    def send_words(self) -> None:
        response_body = WORDS_PATH.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)
def serialize_turn(turn: GuessTurn) -> dict[str, str]:
    return {"guess": turn.guess, "feedback": turn.feedback}


def launch_website(port: int = 0, open_browser: bool = True) -> None:
    if not WEB_DIR.exists():
        raise FileNotFoundError(f"Website assets directory not found: {WEB_DIR}")

    with WordlaServer(("127.0.0.1", port), api=WordlaWebApi()) as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Opening Wordla at {url}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open_new_tab(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    launch_website()
