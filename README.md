# Wordla

Wordla is a Python Wordle solver with both a terminal interface and a local website.
It can solve a word you provide, help with feedback from a live game, or benchmark the solver across the full word list.

## Features

- Solve a target word from the terminal
- Step through feedback from a live game
- Run a full benchmark over `words.txt`
- Open a local website for the same workflows
- Keep the project lightweight with plain Python, HTML, CSS, and JavaScript

## Requirements

- Python 3.8+
- `tqdm` for benchmark progress output

## Installation

```bash
git clone https://github.com/rexmhall09/Wordla.git
cd Wordla
pip install tqdm
```

## Run

```bash
python main.py
```

## Modes

1. **Solve a word you enter**
   - Enter a five-letter word
   - Enter `r` for a random word
   - If the word is not in `words.txt`, Wordla falls back to a random one

2. **Enter feedback for a live game**
   - Wordla suggests a guess
   - Enter feedback with `G`, `Y`, and `N`
   - Enter any other five letters to skip a guess that the game rejects

3. **Benchmark the solver**
   - Runs the solver across the full word list
   - Prints the average number of guesses

4. **Open the website**
   - Starts a local server on `127.0.0.1`
   - Opens the browser UI for solver, helper, and benchmark modes
   - Stop the server with `Ctrl+C`

## Website

The website is served locally from `website.py` and static files under `web/`.
There is no separate web build step.

## Project Layout

- `main.py` — terminal menu
- `solver_core.py` — shared solver logic
- `knownword.py` — terminal mode for solving a known target word
- `helper.py` — terminal mode for entering feedback from a live game
- `testaverage.py` — terminal benchmark mode
- `website.py` — local HTTP server and API
- `web/` — website assets
- `tests/` — regression tests
- `words.txt` — word list

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests -p 'test*.py'
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
