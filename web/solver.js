const WORD_LENGTH = 5;
const STARTING_GUESSES = ['aeros', 'arose', 'soare'];
const SOLVED_FEEDBACK = 'G'.repeat(WORD_LENGTH);
const VALID_FEEDBACK = new Set(['G', 'Y', 'N']);
const YIELD_EVERY_WORDS = 25;

const wordSetCache = new WeakMap();
let wordsPromise = null;

export function loadWords() {
  if (!wordsPromise) {
    wordsPromise = fetch('./words.txt')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Could not load words.txt (${response.status}).`);
        }

        return response.text();
      })
      .then(parseWords);
  }

  return wordsPromise;
}

export function scoreGuess(secretWord, guess) {
  const feedback = Array(WORD_LENGTH).fill('N');
  const remainingLetters = new Map();

  for (let index = 0; index < guess.length; index += 1) {
    if (guess[index] === secretWord[index]) {
      feedback[index] = 'G';
    } else {
      const letter = secretWord[index];
      remainingLetters.set(letter, (remainingLetters.get(letter) || 0) + 1);
    }
  }

  for (let index = 0; index < guess.length; index += 1) {
    if (feedback[index] === 'G') {
      continue;
    }

    const letter = guess[index];
    const remainingCount = remainingLetters.get(letter) || 0;

    if (remainingCount > 0) {
      feedback[index] = 'Y';
      remainingLetters.set(letter, remainingCount - 1);
    }
  }

  return feedback.join('');
}

export function normalizeSecretWord(secretWord, words, rng = Math.random) {
  const normalizedWord = typeof secretWord === 'string' ? secretWord.trim().toLowerCase() : '';

  if (normalizedWord === '' || normalizedWord === 'r') {
    return randomWordResult(words, rng, false);
  }

  if (!getWordSet(words).has(normalizedWord)) {
    return randomWordResult(words, rng, true);
  }

  return {
    secretWord: normalizedWord,
    usedRandomWord: false,
    replacedInvalidWord: false,
  };
}

export function solveKnownWord(secretWord, words, rng = Math.random) {
  const normalized = normalizeSecretWord(secretWord, words, rng);
  const triedWords = new Set();
  const turns = [];
  let guess = pickStartingGuess(rng);

  for (;;) {
    const feedback = scoreGuess(normalized.secretWord, guess);
    turns.push({ guess, feedback });

    if (feedback === SOLVED_FEEDBACK) {
      return {
        secretWord: normalized.secretWord,
        tries: turns.length,
        usedRandomWord: normalized.usedRandomWord,
        replacedInvalidWord: normalized.replacedInvalidWord,
        turns,
      };
    }

    triedWords.add(guess);
    guess = chooseNextGuess(filterRemainingWords(turns, words), triedWords, rng);
  }
}

export class HelperSession {
  constructor(words, rng = Math.random) {
    this.words = words;
    this.rng = rng;
    this.currentGuess = pickStartingGuess(rng);
    this.triedWords = new Set();
    this.history = [];
  }

  get turn() {
    return this.history.length + 1;
  }

  applyFeedback(feedback) {
    const normalizedFeedback = normalizeFeedback(feedback);
    const nextHistory = [
      ...this.history,
      { guess: this.currentGuess, feedback: normalizedFeedback },
    ];

    if (normalizedFeedback === SOLVED_FEEDBACK) {
      this.history = nextHistory;

      return {
        done: true,
        tries: this.history.length,
        history: serializeTurns(this.history),
      };
    }

    const nextTriedWords = new Set(this.triedWords);
    nextTriedWords.add(this.currentGuess);
    const nextGuess = chooseNextGuess(filterRemainingWords(nextHistory, this.words), nextTriedWords, this.rng);

    this.history = nextHistory;
    this.triedWords = nextTriedWords;
    this.currentGuess = nextGuess;

    return this.snapshot();
  }

  skipGuess() {
    const nextTriedWords = new Set(this.triedWords);
    nextTriedWords.add(this.currentGuess);
    const nextGuess = chooseNextGuess(filterRemainingWords(this.history, this.words), nextTriedWords, this.rng);

    this.triedWords = nextTriedWords;
    this.currentGuess = nextGuess;

    return this.snapshot();
  }

  snapshot() {
    return {
      done: false,
      guess: this.currentGuess,
      turn: this.turn,
      history: serializeTurns(this.history),
    };
  }

  nextGuess() {
    return chooseNextGuess(filterRemainingWords(this.history, this.words), this.triedWords, this.rng);
  }
}

export async function calculateAverageTries(words, rng = Math.random, onProgress = null) {
  if (!words.length) {
    throw new Error('At least one word is required to calculate an average.');
  }

  let totalTries = 0;

  for (let index = 0; index < words.length; index += 1) {
    totalTries += solveKnownWord(words[index], words, rng).tries;

    if (onProgress) {
      onProgress(index + 1, words.length);
    }

    if ((index + 1) % YIELD_EVERY_WORDS === 0) {
      await yieldToBrowser();
    }
  }

  return totalTries / words.length;
}

function parseWords(rawText) {
  const words = rawText
    .split(/\r?\n/)
    .map((word) => word.trim().toLowerCase())
    .filter((word) => word.length === WORD_LENGTH);

  if (!words.length) {
    throw new Error('words.txt did not contain any five-letter words.');
  }

  return words;
}

function randomWordResult(words, rng, replacedInvalidWord) {
  return {
    secretWord: pickRandom(words, rng),
    usedRandomWord: true,
    replacedInvalidWord,
  };
}

function getWordSet(words) {
  let wordSet = wordSetCache.get(words);

  if (!wordSet) {
    wordSet = new Set(words);
    wordSetCache.set(words, wordSet);
  }

  return wordSet;
}


function normalizeFeedback(feedback) {
  const normalizedFeedback = String(feedback).trim().toUpperCase();

  if (normalizedFeedback.length !== WORD_LENGTH) {
    throw new Error(`Feedback must be exactly ${WORD_LENGTH} letters long.`);
  }

  const invalidLetters = Array.from(new Set(normalizedFeedback))
    .filter((letter) => !VALID_FEEDBACK.has(letter))
    .sort();

  if (invalidLetters.length) {
    throw new Error(`Feedback can only use G, Y, or N. Invalid: ${invalidLetters.join(', ')}`);
  }

  return normalizedFeedback;
}

function filterRemainingWords(turns, words) {
  const remainingWords = [];

  wordLoop:
  for (const word of words) {
    for (const turn of turns) {
      if (scoreGuess(word, turn.guess) !== turn.feedback) {
        continue wordLoop;
      }
    }

    remainingWords.push(word);
  }

  return remainingWords;
}

function chooseNextGuess(candidates, triedWords, rng) {
  let untriedCount = 0;

  for (const candidate of candidates) {
    if (!triedWords.has(candidate)) {
      untriedCount += 1;
    }
  }

  if (!untriedCount) {
    throw new Error('No words remain. The feedback so far conflicts with the solver rules.');
  }

  let targetIndex = randomIndex(untriedCount, rng);

  for (const candidate of candidates) {
    if (!triedWords.has(candidate)) {
      if (targetIndex === 0) {
        return candidate;
      }

      targetIndex -= 1;
    }
  }

  throw new Error('No words remain. The feedback so far conflicts with the solver rules.');
}

function pickStartingGuess(rng) {
  return pickRandom(STARTING_GUESSES, rng);
}

function pickRandom(items, rng) {
  return items[randomIndex(items.length, rng)];
}

function randomIndex(length, rng) {
  return Math.min(Math.floor(randomFloat(rng) * length), length - 1);
}

function randomFloat(rng) {
  if (typeof rng === 'function') {
    return rng();
  }

  if (rng && typeof rng.random === 'function') {
    return rng.random();
  }

  return Math.random();
}

function serializeTurns(turns) {
  return turns.map((turn) => ({ guess: turn.guess, feedback: turn.feedback }));
}

function yieldToBrowser() {
  return new Promise((resolve) => {
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(resolve);
    } else {
      setTimeout(resolve, 0);
    }
  });
}
