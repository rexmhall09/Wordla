# Wordla

**Wordla** is a Python-based solver and helper for the popular Wordle word-guessing game. It provides a command-line interface with multiple modes to either automatically solve a Wordle puzzle or assist you in guessing the word. This project implements the Wordle-solving algorithm, allowing developers and enthusiasts to run the solver, analyze its strategy, or even improve it.

## Features

- **Multiple Game Modes**: Wordla can operate in different modes:
  - **Automated Solver** – Give it a secret word (or choose a random one) and watch the AI guess the word step by step.
  - **Interactive Helper** – Let the AI suggest guesses for an unknown word while you provide feedback (Green/Yellow/Gray) from an actual Wordle game.
  - **Batch Solver for Averages** – Run the solver on a list of words to calculate the average number of guesses the algorithm needs.
- **Logical Elimination Algorithm**: Uses feedback from each guess to eliminate impossible words. It keeps track of confirmed letters and positions (greens), present-but-misplaced letters (yellows), and absent letters (grays) to narrow down the solution space.
- **Heuristic Guess Selection**: Incorporates a strategy to choose guesses. By default, it can pick the next guess randomly from remaining possibilities, but an advanced logic (see `wordle_ai.py`) ranks candidate words by letter frequency to maximize information gain.
- **Word List**: Includes a built-in dictionary of five-letter English words (`words.txt`) to validate guesses and limit the solution space (approximately 4,200 words).
- **Pure Python Implementation**: Written in Python 3 with no heavy external dependencies (uses only the standard library and `tqdm` for the progress bar). This makes it easy to run and modify.

## Technologies Used

- **Language**: Python 3 (>= 3.8 recommended).  
- **Frameworks/Libraries**: 
  - Standard Python libraries (`collections`, etc.) for implementing the algorithm.
  - [`tqdm`](https://pypi.org/project/tqdm/) for showing a progress bar in batch simulation mode.
- **Data**: Uses a static word list (`words.txt`) as the source of valid Wordle words. This list can be modified or extended as needed.
- The project follows a straightforward procedural style, making it easy to understand the solving logic without any specialized frameworks.

## Installation

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/rexmhall09/Wordla.git
   cd Wordla
   ```
2. **Ensure Python is installed**: Wordla requires Python 3.8+ (for newer syntax like the walrus operator `:=`). You can check your version with `python --version`.
3. **Install dependencies**: The only external dependency is `tqdm` (for the average-calculation mode). Install it via pip:  
   ```bash
   pip install tqdm
   ``` 
   *Note:* You may want to use a virtual environment (venv) to avoid affecting your global packages.
4. **(Optional) Verify contents**: The repository includes the Python source files and a word list. No additional build steps are needed.

## Usage

To start Wordla, run the `main.py` script in a terminal:

```bash
python main.py
```

You will be presented with a menu to select one of the game modes. Choose an option by entering the corresponding number:

1. **You input a word, and the AI guesses** – *Mode 1:* The solver will prompt you for a secret word (the answer). You can enter any 5-letter word or type "`r`" to let the program pick a random secret word from the list. Wordla will then automatically make guesses and display the feedback for each guess until it finds the correct word. This mode is fully automated; the program knows the secret and calculates the Green/Yellow/Gray feedback on its own.  
   - *Example:*  
     ```text
     Select a game mode:
     1 - You input a word, and the AI guesses.
     2 - AI guesses, and you give feedback.
     3 - Calculate the average number of tries for the AI.
     Enter the number of the game mode you want to play: 1

     Word we're looking for (r for random): crane
     soare : ['N', 'G', 'G', 'Y', 'G']
     It took 3 tries to find 'crane'.
     ```  
     In the above example, the secret word was "**crane**". The AI’s first guess was "**soare**", which resulted in the feedback `['N', 'G', 'G', 'Y', 'G']` (indicating **s** is not in the word, **o** is correct in position 2, **a** is correct in position 3, **r** is in the word but a different position, **e** is correct in position 5). The solver continued guessing until it got the word in 3 tries.

2. **AI guesses, and you give feedback** – *Mode 2:* This mode turns Wordla into an interactive assistant for solving a Wordle puzzle you don’t know. The program itself does **not** know the secret word; instead, it will suggest a guess and then ask you for the feedback. You should provide the feedback exactly as the Wordle game gives it to you:
   - Use `G` for each green letter (correct letter in correct position).
   - Use `Y` for each yellow letter (correct letter in wrong position).
   - Use `N` for letters that are gray (not in the word at all).  
   For example, if the AI guesses "SOARE" and the secret word (unknown to the AI) is "plane", you might enter feedback like `NNGNG` (indicating S and O are not in the word, A and E are correct in those positions, and R is not in the word). Wordla will then refine its internal knowledge and suggest another guess. Continue this process until Wordla outputs `GGGGG`, meaning the word has been found.  
   - *Tip:* If the AI suggests a word that the actual Wordle game doesn’t accept as a valid guess, you can enter any placeholder (for example, `aaaaa`) as feedback. The program will interpret this as "no information" and pick a different word next time.
   - *Example session:*  
     ```text
     Select a game mode: 2
     Current guess: SOARE
     Please enter feedback (G/Y/N for each letter): NNGNY
     Current guess: PLANT
     Please enter feedback (G/Y/N for each letter): GGYNG
     Current guess: PRUNE
     Please enter feedback (G/Y/N for each letter): GGGGG
     It took 3 tries to find the word.
     ```  
     In this hypothetical session, the secret word was "**PRUNE**". The user provided feedback for each guess and the solver arrived at the correct answer in 3 guesses.

3. **Calculate the average number of tries for the AI** – *Mode 3:* This mode runs the solver against a series of words to evaluate performance. Wordla will iterate through the entire `words.txt` list (or a defined set of words) and attempt to solve each one, tracking the number of guesses taken. It then computes and displays the average number of guesses the AI needed.  
   - This mode is useful for analyzing the efficiency of the algorithm. It will display a progress bar (thanks to `tqdm`) because it may involve solving thousands of words. 
   - Once completed, it prints the average tries. For example:  
     ```text
     Average number of tries: 3.721
     ```  
     (The above number is just an example; the actual result depends on the algorithm and word list.)

**Note:** By default, Wordla always uses 5-letter words as in the original Wordle. The game modes assume a 5-letter secret. Also, the program will terminate when you type "exit" at the menu or after finishing a mode (it will prompt if you want to play again).

## How It Works (Algorithm Details)

Wordla implements the classic Wordle solving strategy by progressively narrowing down the possible words based on feedback:

- **Knowledge Representation**: The solver maintains a data structure (`knowledge`) tracking:
  - Possible letters for each position (initialized to all letters `A-Z` and pruned as guesses are made).
  - A list of letters that must appear in the word (from any green or yellow feedback).
  - A list (or set) of letters confirmed not to be in the word at all.
- **Feedback Processing**: After each guess, the feedback is used to update the knowledge:
  - Green (`G`): The guessed letter is correct for that position. The solver fixes that position to the letter and marks it as a required letter.
  - Yellow (`Y`): The letter is in the word but in a different position. The solver removes that letter from the current guessed position’s possibilities, but marks the letter as required somewhere else.
  - Gray (`N`): The letter is not in the word. The solver eliminates that letter from **all** positions’ possibilities (unless it’s known to appear elsewhere from other feedback).
- **Candidate Filtering**: The program keeps a list of all candidate words that could still be the answer. After each guess’s feedback, it filters this list to remove any word that conflicts with the updated knowledge (e.g., any word that doesn’t contain a required letter, or has a letter in a position that it shouldn’t).
- **Next Guess Selection**: 
  - In the basic implementation (modes 1 and 2), Wordla picks the next guess randomly from the remaining possible words. (It also avoids repeating any guess it already tried.)
  - The file `wordle_ai.py` contains a more advanced approach where the next guess is chosen based on a scoring function. This heuristic scores each candidate word by summing the frequencies of its letters (in the remaining pool of possible words). The word with the highest score (meaning it has common letters that would give the most information) is chosen as the next guess. This typically leads to solving the puzzle in fewer guesses on average.
- **Typical Performance**: Using logical elimination, Wordla usually finds the secret word within 3-5 guesses. The provided average-calculation mode can be used to measure its exact performance over the entire word list or to compare different strategies (random pick vs. frequency-based picks).

This algorithm isn’t guaranteed to be the absolute optimal solver, but it mirrors a reasonable strategy similar to how humans play the game, and it’s easily extensible for improvements.

## Contributing

Contributions are welcome! If you are a developer who wants to improve Wordla or adapt it:

- **Bug Reports & Feature Requests**: Please open an issue on GitHub if you find a bug or have an idea for a new feature or enhancement (e.g. support for different word lengths, a GUI, improved algorithms, etc.).
- **Development**: Fork the repository and create a new branch for your contributions. Follow common Python style guidelines (PEP 8) for consistency. Include docstrings or comments in the code where useful, especially if introducing complex logic.
- **Testing**: Try out your changes in all three modes to ensure the solver still works correctly. If possible, add new test cases or assert statements (for example, you might create a small test function to verify the solver can find known words).
- **Pull Requests**: Submit a pull request with a clear description of your changes. Explain the rationale (why the change is beneficial) and any impacts on performance or compatibility. The maintainers will review your PR and merge it if it aligns with the project goals.

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details. This means you are free to use, modify, and distribute the code, but attribution to the original author is appreciated.

---

*Wordla is an independent open-source project. It is not affiliated with the official **Wordle** game by Josh Wardle (now owned by The New York Times). This tool is for educational and research purposes, demonstrating algorithms for solving word puzzles.*
