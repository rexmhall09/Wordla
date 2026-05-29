# Wordla

Wordla is a Wordle solver with a static browser UI and a Python terminal/local-server interface.
It can solve a word you provide, help with feedback from a live game, or benchmark the solver across the full word list.
[deployed here](https://rexmhall09.github.io/Wordla/)

## Features

- Use the static web UI on GitHub Pages with no Python backend
- Solve a target word from the browser or terminal
- Step through feedback from a live game
- Run a full benchmark over `words.txt`
- Keep the project lightweight with plain Python, HTML, CSS, and JavaScript

## Static Web UI

The static web UI lives in `web/` and loads `words.txt` directly in the browser.
It uses relative asset paths, so it works from GitHub Pages project URLs such as `/Wordla/`.

GitHub Pages deployment should use GitHub Actions as its source. The workflow in `.github/workflows/pages.yml` publishes only the static site artifact:

- all files from `web/`
- `words.txt` copied to the artifact root

The repository root also has `index.html` for branch-based Pages setups. That prevents GitHub Pages from rendering this README as the site while still loading the shared assets from `web/`.

## Requirements

- Python 3.8+ for the terminal interface and local server
- `tqdm` for terminal benchmark progress output

## Installation

```bash
git clone https://github.com/rexmhall09/Wordla.git
cd Wordla
pip install tqdm
```

## Run the Python Interface

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

4. **Open the local website**
   - Starts a local server on `127.0.0.1`
   - Serves the same static browser UI plus the local API endpoints
   - Stop the server with `Ctrl+C`

## Project Layout

- `main.py`: terminal menu
- `solver_core.py`: shared Python solver logic
- `knownword.py`: terminal mode for solving a known target word
- `helper.py`: terminal mode for entering feedback from a live game
- `testaverage.py`: terminal benchmark mode
- `website.py`: local HTTP server and API
- `web/`: static browser UI assets
- `web/solver.js`: browser solver logic for GitHub Pages
- `tests/`: regression tests
- `words.txt`: word list used by both Python and browser modes

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests -p 'test*.py'
```

To preview the Pages artifact locally, serve a directory containing `web/` contents and `words.txt` at the same root.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
