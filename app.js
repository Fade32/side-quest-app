/**
 * Side Quest App — app.js
 *
 * Manages quest data (add / accept / complete / delete) with
 * localStorage persistence so quests survive page refreshes.
 */

// ─── Data Layer ──────────────────────────────────────────────

const STORAGE_KEY = 'sideQuests';

/** @typedef {{ id: string, title: string, prompt: string, reward: string, status: 'available'|'accepted'|'completed', createdAt: number }} Quest */

/** @returns {Quest[]} */
function loadQuests() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

/** @param {Quest[]} quests */
function saveQuests(quests) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(quests));
}

function generateId() {
  return `quest-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

// ─── DOM Helpers ─────────────────────────────────────────────

const listAvailable  = document.getElementById('list-available');
const listAccepted   = document.getElementById('list-accepted');
const listCompleted  = document.getElementById('list-completed');
const emptyAvailable = document.getElementById('empty-available');
const emptyAccepted  = document.getElementById('empty-accepted');
const emptyCompleted = document.getElementById('empty-completed');
const cardTemplate   = document.getElementById('quest-card-template');

const STATUS_CONFIG = {
  available:  { label: 'Available',  badgeClass: 'badge-available'  },
  accepted:   { label: 'Accepted',   badgeClass: 'badge-accepted'   },
  completed:  { label: 'Completed',  badgeClass: 'badge-completed'  },
};

/**
 * Build the action buttons for a quest based on its current status.
 * @param {Quest} quest
 * @returns {HTMLElement[]}
 */
function buildActionButtons(quest) {
  const buttons = [];

  if (quest.status === 'available') {
    const acceptBtn = document.createElement('button');
    acceptBtn.className = 'btn btn-accept';
    acceptBtn.textContent = 'Accept Quest';
    acceptBtn.addEventListener('click', () => changeStatus(quest.id, 'accepted'));
    buttons.push(acceptBtn);
  }

  if (quest.status === 'accepted') {
    const completeBtn = document.createElement('button');
    completeBtn.className = 'btn btn-complete';
    completeBtn.textContent = 'Complete Quest';
    completeBtn.addEventListener('click', () => changeStatus(quest.id, 'completed'));
    buttons.push(completeBtn);
  }

  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'btn btn-delete';
  deleteBtn.textContent = 'Delete';
  deleteBtn.addEventListener('click', () => deleteQuest(quest.id));
  buttons.push(deleteBtn);

  return buttons;
}

/**
 * Create a quest card DOM node from a Quest object.
 * @param {Quest} quest
 * @returns {HTMLLIElement}
 */
function createQuestCard(quest) {
  const fragment = cardTemplate.content.cloneNode(true);
  const card = fragment.querySelector('.quest-card');

  card.dataset.id = quest.id;

  const title   = card.querySelector('.quest-card-title');
  const badge   = card.querySelector('.quest-status-badge');
  const prompt  = card.querySelector('.quest-card-prompt');
  const reward  = card.querySelector('.quest-card-reward');
  const actions = card.querySelector('.quest-card-actions');

  const config = STATUS_CONFIG[quest.status];

  title.textContent  = quest.title;
  badge.textContent  = config.label;
  badge.className    = `quest-status-badge ${config.badgeClass}`;
  prompt.textContent = quest.prompt;

  if (quest.reward) {
    reward.textContent = quest.reward;
    reward.classList.remove('hidden');
  }

  buildActionButtons(quest).forEach(btn => actions.appendChild(btn));

  return card;
}

// ─── Render ───────────────────────────────────────────────────

function render() {
  const quests = loadQuests();

  // Clear lists
  listAvailable.innerHTML  = '';
  listAccepted.innerHTML   = '';
  listCompleted.innerHTML  = '';

  const byStatus = { available: [], accepted: [], completed: [] };
  quests.forEach(q => byStatus[q.status]?.push(q));

  // Sort newest first within each column
  Object.values(byStatus).forEach(arr => arr.sort((a, b) => b.createdAt - a.createdAt));

  byStatus.available.forEach(q  => listAvailable.appendChild(createQuestCard(q)));
  byStatus.accepted.forEach(q   => listAccepted.appendChild(createQuestCard(q)));
  byStatus.completed.forEach(q  => listCompleted.appendChild(createQuestCard(q)));

  // Show/hide empty messages
  emptyAvailable.classList.toggle('hidden', byStatus.available.length > 0);
  emptyAccepted.classList.toggle('hidden',  byStatus.accepted.length  > 0);
  emptyCompleted.classList.toggle('hidden', byStatus.completed.length > 0);
}

// ─── Mutations ────────────────────────────────────────────────

/**
 * Add a new quest with status 'available'.
 * @param {string} title
 * @param {string} prompt
 * @param {string} reward
 */
function addQuest(title, prompt, reward) {
  const quests = loadQuests();
  /** @type {Quest} */
  const newQuest = {
    id: generateId(),
    title: title.trim(),
    prompt: prompt.trim(),
    reward: reward.trim(),
    status: 'available',
    createdAt: Date.now(),
  };
  quests.push(newQuest);
  saveQuests(quests);
  render();
}

/**
 * Transition a quest to a new status.
 * @param {string} id
 * @param {'accepted'|'completed'} newStatus
 */
function changeStatus(id, newStatus) {
  const quests = loadQuests();
  const quest = quests.find(q => q.id === id);
  if (!quest) return;
  quest.status = newStatus;
  saveQuests(quests);
  render();
}

/**
 * Remove a quest permanently.
 * @param {string} id
 */
function deleteQuest(id) {
  const confirmed = window.confirm('Are you sure you want to delete this quest?');
  if (!confirmed) return;
  const quests = loadQuests().filter(q => q.id !== id);
  saveQuests(quests);
  render();
}

// ─── Form Handling ────────────────────────────────────────────

const questForm   = document.getElementById('quest-form');
const titleInput  = document.getElementById('quest-title');
const promptInput = document.getElementById('quest-prompt');
const rewardInput = document.getElementById('quest-reward');

questForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const title  = titleInput.value.trim();
  const prompt = promptInput.value.trim();
  const reward = rewardInput.value.trim();

  if (!title || !prompt) {
    alert('Please fill in both the Quest Title and Description before posting.');
    return;
  }

  addQuest(title, prompt, reward);

  // Reset form
  questForm.reset();
  titleInput.focus();
});

// ─── Bootstrap ───────────────────────────────────────────────

render();
