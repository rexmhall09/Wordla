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

const helperState = {
  sessionId: null,
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
  element.className = 'status-card muted';
  element.innerHTML = `<span class="loader">${message}</span>`;
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

async function postJson(url, payload = {}) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const rawText = await response.text();
  let data = {};

  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch {
      throw new Error('Invalid server response.');
    }
  }

  if (!response.ok) {
    throw new Error(data.error || 'Request failed.');
  }

  return data;
}

solverForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  setLoading(solverStatus, 'Running');

  try {
    const secretWord = solverSecretWord.value.trim().toLowerCase();
    const data = await postJson('/api/mode1/solve', { secretWord });
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
    setStatus(solverStatus, error.message, 'error');
    solverBoard.innerHTML = '';
  }
});

helperStart.addEventListener('click', async () => {
  setLoading(helperStatus, 'Starting');

  try {
    const data = await postJson('/api/mode2/start');
    helperState.sessionId = data.sessionId;
    helperState.currentGuess = data.guess;
    helperState.history = data.history;
    helperState.feedback = Array(5).fill('N');

    helperSubmit.disabled = false;
    helperSkip.disabled = false;
    setStatus(helperStatus, `Turn ${data.turn}: ${data.guess.toUpperCase()}`, 'success');
    renderFeedbackRow();
    renderBoard(helperBoard, helperState.history, {
      currentGuess: helperState.currentGuess,
      pendingFeedback: helperState.feedback,
    });
  } catch (error) {
    setStatus(helperStatus, error.message, 'error');
  }
});

helperSubmit.addEventListener('click', async () => {
  if (!helperState.sessionId) {
    return;
  }

  setLoading(helperStatus, 'Submitting');

  try {
    const feedback = helperState.feedback.join('');
    const data = await postJson('/api/mode2/feedback', {
      sessionId: helperState.sessionId,
      feedback,
    });

    helperState.history = data.history;

    if (data.done) {
      helperState.sessionId = null;
      helperState.currentGuess = null;
      helperState.feedback = Array(5).fill('N');
      helperSubmit.disabled = true;
      helperSkip.disabled = true;
      setStatus(helperStatus, `Solved in ${formatGuessCount(data.tries)}.`, 'success');
      renderFeedbackRow();
      renderBoard(helperBoard, helperState.history, {
        summary: 'Complete',
      });
      return;
    }

    helperState.currentGuess = data.guess;
    helperState.feedback = Array(5).fill('N');
    setStatus(helperStatus, `Turn ${data.turn}: ${data.guess.toUpperCase()}`, 'success');
    renderFeedbackRow();
    renderBoard(helperBoard, helperState.history, {
      currentGuess: helperState.currentGuess,
      pendingFeedback: helperState.feedback,
    });
  } catch (error) {
    setStatus(helperStatus, error.message, 'error');
  }
});

helperSkip.addEventListener('click', async () => {
  if (!helperState.sessionId) {
    return;
  }

  setLoading(helperStatus, 'Skipping');

  try {
    const data = await postJson('/api/mode2/skip', {
      sessionId: helperState.sessionId,
    });
    helperState.currentGuess = data.guess;
    helperState.history = data.history;
    helperState.feedback = Array(5).fill('N');
    setStatus(helperStatus, `Turn ${data.turn}: ${data.guess.toUpperCase()}`, 'success');
    renderFeedbackRow();
    renderBoard(helperBoard, helperState.history, {
      currentGuess: helperState.currentGuess,
      pendingFeedback: helperState.feedback,
    });
  } catch (error) {
    setStatus(helperStatus, error.message, 'error');
  }
});

averageRun.addEventListener('click', async () => {
  averageRun.disabled = true;
  setLoading(averageStatus, 'Running benchmark');

  try {
    const data = await postJson('/api/mode3/average');
    setStatus(averageStatus, `Average: ${data.average.toFixed(3)} over ${data.wordsTested} words.`, 'success');
  } catch (error) {
    setStatus(averageStatus, error.message, 'error');
  } finally {
    averageRun.disabled = false;
  }
});

renderFeedbackRow();
renderBoard(solverBoard, []);
renderBoard(helperBoard, []);
