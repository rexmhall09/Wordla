import { HelperSession, calculateAverageTries, loadWords, solveKnownWord } from './solver.js';

const modeTabs = Array.from(document.querySelectorAll('.mode-tab'));
const panels = Array.from(document.querySelectorAll('.panel'));
const solverForm = document.getElementById('solver-form');
const solverSecretWord = document.getElementById('solver-secret-word');
const solverStatus = document.getElementById('solver-status');
const solverBoard = document.getElementById('solver-board');
const helperStart = document.getElementById('helper-start');
const helperSkip = document.getElementById('helper-skip');
const helperSubmit = document.getElementById('helper-submit');
const helperStatus = document.getElementById('helper-status');
const helperBoard = document.getElementById('helper-board');
const feedbackRow = document.getElementById('feedback-row');
const averageRun = document.getElementById('average-run');
const averageStatus = document.getElementById('average-status');

const feedbackCycle = ['N', 'Y', 'G'];
const feedbackLabels = { N: 'Gray', Y: 'Yellow', G: 'Green' };

let words = [];
let helperSession = null;

const helperState = {
  currentGuess: null,
  history: [],
  feedback: Array(5).fill('N'),
};

modeTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    modeTabs.forEach((button) => {
      button.classList.toggle('is-active', button === tab);
    });
    panels.forEach((panel) => {
      panel.classList.toggle('is-active', panel.id === tab.dataset.panel);
    });
  });
});

function formatGuessCount(count) {
  return `${count} ${count === 1 ? 'guess' : 'guesses'}`;
}

function setStatus(element, message, tone = 'muted') {
  element.className = `status-card ${tone}`;
  element.textContent = message;
}

function setLoading(element, message) {
  const loader = document.createElement('span');
  loader.className = 'loader';
  loader.textContent = message;

  element.className = 'status-card muted';
  element.replaceChildren(loader);
}

function buildTile(letter = '', feedback = '', extraClass = '') {
  const tile = document.createElement('div');
  tile.className = ['tile', feedback ? `tile--${feedback.toLowerCase()}` : '', extraClass]
    .filter(Boolean)
    .join(' ');
  tile.textContent = letter;
  return tile;
}

function renderBoard(container, turns, options = {}) {
  const { currentGuess = null, pendingFeedback = null, summary = '' } = options;
  container.innerHTML = '';

  const board = document.createElement('div');
  board.className = 'board-grid';

  turns.forEach((turn) => {
    const row = document.createElement('div');
    row.className = 'board-row';
    turn.guess.toUpperCase().split('').forEach((letter, index) => {
      row.appendChild(buildTile(letter, turn.feedback[index]));
    });
    board.appendChild(row);
  });

  if (currentGuess) {
    const row = document.createElement('div');
    row.className = 'board-row';
    currentGuess.toUpperCase().split('').forEach((letter, index) => {
      const feedback = pendingFeedback ? pendingFeedback[index] : '';
      row.appendChild(buildTile(letter, feedback, 'tile--active'));
    });
    board.appendChild(row);
  }

  if (!turns.length && !currentGuess) {
    const emptyState = document.createElement('div');
    emptyState.className = 'board-summary';
    emptyState.textContent = 'No guesses yet.';
    container.appendChild(emptyState);
    return;
  }

  container.appendChild(board);

  if (summary) {
    const boardSummary = document.createElement('p');
    boardSummary.className = 'board-summary';
    boardSummary.textContent = summary;
    container.appendChild(boardSummary);
  }
}

function renderFeedbackRow() {
  feedbackRow.innerHTML = '';

  helperState.feedback.forEach((feedback, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `feedback-tile feedback-tile--${feedback.toLowerCase()}`;
    button.textContent = helperState.currentGuess ? helperState.currentGuess[index].toUpperCase() : '';
    button.setAttribute('aria-label', `Letter ${index + 1}: ${feedbackLabels[feedback]}`);
    button.disabled = !helperState.currentGuess;
    button.addEventListener('click', () => {
      const currentIndex = feedbackCycle.indexOf(helperState.feedback[index]);
      helperState.feedback[index] = feedbackCycle[(currentIndex + 1) % feedbackCycle.length];
      renderFeedbackRow();
      renderBoard(helperBoard, helperState.history, {
        currentGuess: helperState.currentGuess,
        pendingFeedback: helperState.feedback,
      });
    });
    feedbackRow.appendChild(button);
  });
}

function setControlsReady(isReady) {
  solverForm.querySelector('button[type="submit"]').disabled = !isReady;
  helperStart.disabled = !isReady;
  averageRun.disabled = !isReady;
}

function updateHelperFromSnapshot(snapshot) {
  helperState.currentGuess = snapshot.guess;
  helperState.history = snapshot.history;
  helperState.feedback = Array(5).fill('N');

  helperSubmit.disabled = false;
  helperSkip.disabled = false;
  setStatus(helperStatus, `Turn ${snapshot.turn}: ${snapshot.guess.toUpperCase()}`, 'success');
  renderFeedbackRow();
  renderBoard(helperBoard, helperState.history, {
    currentGuess: helperState.currentGuess,
    pendingFeedback: helperState.feedback,
  });
}

function completeHelper(response) {
  helperSession = null;
  helperState.currentGuess = null;
  helperState.history = response.history;
  helperState.feedback = Array(5).fill('N');
  helperSubmit.disabled = true;
  helperSkip.disabled = true;
  setStatus(helperStatus, `Solved in ${formatGuessCount(response.tries)}.`, 'success');
  renderFeedbackRow();
  renderBoard(helperBoard, helperState.history, {
    summary: 'Complete',
  });
}

function handleError(statusElement, error) {
  setStatus(statusElement, error instanceof Error ? error.message : String(error), 'error');
}

solverForm.addEventListener('submit', (event) => {
  event.preventDefault();
  setLoading(solverStatus, 'Running');

  try {
    const secretWord = solverSecretWord.value;
    const data = solveKnownWord(secretWord, words);
    const statusBits = [`Solved ${data.secretWord.toUpperCase()} in ${formatGuessCount(data.tries)}.`];

    if (data.replacedInvalidWord) {
      statusBits.push('Word not in list. Used a random word instead.');
    } else if (data.usedRandomWord) {
      statusBits.push('Random word selected.');
    }

    setStatus(solverStatus, statusBits.join(' '), 'success');
    renderBoard(solverBoard, data.turns, {
      summary: formatGuessCount(data.turns.length),
    });
  } catch (error) {
    handleError(solverStatus, error);
    solverBoard.innerHTML = '';
  }
});

helperStart.addEventListener('click', () => {
  setLoading(helperStatus, 'Starting');

  try {
    helperSession = new HelperSession(words);
    updateHelperFromSnapshot(helperSession.snapshot());
  } catch (error) {
    helperSession = null;
    helperSubmit.disabled = true;
    helperSkip.disabled = true;
    handleError(helperStatus, error);
  }
});

helperSubmit.addEventListener('click', () => {
  if (!helperSession) {
    return;
  }

  setLoading(helperStatus, 'Submitting');

  try {
    const response = helperSession.applyFeedback(helperState.feedback.join(''));

    if (response.done) {
      completeHelper(response);
      return;
    }

    updateHelperFromSnapshot(response);
  } catch (error) {
    handleError(helperStatus, error);
  }
});

helperSkip.addEventListener('click', () => {
  if (!helperSession) {
    return;
  }

  setLoading(helperStatus, 'Skipping');

  try {
    updateHelperFromSnapshot(helperSession.skipGuess());
  } catch (error) {
    handleError(helperStatus, error);
  }
});

averageRun.addEventListener('click', async () => {
  averageRun.disabled = true;
  setLoading(averageStatus, 'Running benchmark');

  try {
    const average = await calculateAverageTries(words, Math.random, (completed, total) => {
      if (completed === total || completed % 100 === 0) {
        setStatus(averageStatus, `Running benchmark: ${completed.toLocaleString()} of ${total.toLocaleString()} words...`);
      }
    });
    setStatus(averageStatus, `Average: ${average.toFixed(3)} over ${words.length.toLocaleString()} words.`, 'success');
  } catch (error) {
    handleError(averageStatus, error);
  } finally {
    averageRun.disabled = false;
  }
});

async function initialize() {
  setControlsReady(false);
  setLoading(solverStatus, 'Loading word list');
  setStatus(helperStatus, 'Loading word list...');
  setStatus(averageStatus, 'Loading word list...');
  renderFeedbackRow();
  renderBoard(solverBoard, []);
  renderBoard(helperBoard, []);

  try {
    words = await loadWords();
    setControlsReady(true);
    setStatus(solverStatus, `Ready with ${words.length.toLocaleString()} words.`);
    setStatus(helperStatus, 'Press Start to get the first guess.');
    setStatus(averageStatus, 'No benchmark yet.');
  } catch (error) {
    handleError(solverStatus, error);
    handleError(helperStatus, error);
    handleError(averageStatus, error);
  }
}

initialize();
