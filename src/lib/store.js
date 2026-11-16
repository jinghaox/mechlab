import { dayKey } from './util.js';

const KEY = 'mechalab_v1';
const DAY = 86400000;

const defaults = () => ({
  // learner: '' until chosen, then 'parent' or 'student'
  settings: { apiKey: '', model: 'claude-opus-5-5', learner: '' },
  done: {}, // lesson id -> { at, score, total }
  chats: {}, // lesson id or 'general' -> messages[]
  stats: { lastDay: '', streak: 0 },
  last: '', // last opened lesson id
});

function load() {
  const base = defaults();
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    for (const k of Object.keys(base)) {
      if (saved[k] && typeof base[k] === 'object' && base[k] !== null && !Array.isArray(base[k]))
        base[k] = { ...base[k], ...saved[k] };
      else if (saved[k] !== undefined) base[k] = saved[k];
    }
  } catch {
    /* corrupt save: fall back to defaults */
  }
  return base;
}

export const state = load();

export function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* storage full or unavailable */
  }
}

export function resetProgress() {
  const keep = state.settings;
  Object.assign(state, defaults(), { settings: keep });
  save();
}

// Record that the learner studied today, for the day streak.
export function touchStreak() {
  const today = dayKey();
  const s = state.stats;
  if (s.lastDay === today) return;
  const yesterday = dayKey(new Date(Date.now() - DAY));
  s.streak = s.lastDay === yesterday ? s.streak + 1 : 1;
  s.lastDay = today;
  save();
}

// A streak only counts if the learner studied today or yesterday.
export function currentStreak() {
  const s = state.stats;
  const yesterday = dayKey(new Date(Date.now() - DAY));
  return s.lastDay === dayKey() || s.lastDay === yesterday ? s.streak : 0;
}

export function markDone(id, score = null, total = null) {
  const prev = state.done[id];
  state.done[id] = { at: prev?.at || Date.now(), score, total };
  touchStreak();
  save();
}

export function unmarkDone(id) {
  delete state.done[id];
  save();
}
