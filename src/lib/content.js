// Loads lesson files (src/content/<id>.md) and lab scripts (labs/**/*.py) at build time.
//
// Lesson file format: Markdown with LaTeX. Lines of the form "=== name ===" start a section:
//   (top)        lesson body
//   === summary ===   key formulas / takeaways
//   === frc ===       link to FTC/FRC experience
//   === lab ===       PC lab; a line "@lab m0/file.py" inlines that script from labs/
//   === quiz ===      "? question", "- wrong option", "* correct option", "> explanation"

import { state } from './store.js';
import { track } from '../data/curriculum.js';

const files = import.meta.glob('../content/*.md', { query: '?raw', import: 'default', eager: true });
const labFiles = import.meta.glob('../../labs/**/*.py', { query: '?raw', import: 'default', eager: true });

const raw = {};
for (const [path, text] of Object.entries(files)) raw[path.split('/').pop().replace(/\.md$/, '')] = text;

const labs = {};
for (const [path, text] of Object.entries(labFiles)) labs[path.split('/labs/')[1]] = text;

export const hasContent = (id) => id in raw;

function parseQuiz(text) {
  const out = [];
  let cur = null;
  for (const line of text.split('\n')) {
    const body = line.slice(2).trim();
    if (line.startsWith('? ')) {
      cur = { q: body, opts: [], a: -1, why: '' };
      out.push(cur);
    } else if (!cur) {
      continue;
    } else if (line.startsWith('* ')) {
      cur.a = cur.opts.length;
      cur.opts.push(body);
    } else if (line.startsWith('- ')) {
      cur.opts.push(body);
    } else if (line.startsWith('> ')) {
      cur.why = body;
    }
  }
  return out.filter((q) => q.a >= 0 && q.opts.length > 1);
}

const inlineLabs = (text) =>
  text.replace(/^@lab\s+(\S+)\s*$/gm, (_, path) =>
    labs[path]
      ? `**\`labs/${path}\`**\n\n\`\`\`python\n${labs[path].replace(/\r\n/g, '\n').trimEnd()}\n\`\`\``
      : `*(missing lab file: ${path})*`,
  );

const cache = {};
export function getLesson(id) {
  if (!(id in raw)) return null;
  if (cache[id]) return cache[id];
  const sec = { body: [], summary: [], frc: [], lab: [], quiz: [] };
  let cur = 'body';
  for (const line of raw[id].replace(/\r\n/g, '\n').split('\n')) {
    const m = line.match(/^=== (\w+) ===\s*$/);
    if (m && m[1] in sec) cur = m[1];
    else sec[cur].push(line);
  }
  const text = (k) => sec[k].join('\n').trim();
  return (cache[id] = {
    body: text('body'),
    summary: text('summary'),
    frc: text('frc'),
    lab: inlineLabs(text('lab')),
    quiz: parseQuiz(text('quiz')),
  });
}

// The lesson as plain text, used as context for the AI tutor.
export function lessonText(id) {
  const l = getLesson(id);
  if (!l) return '';
  const quiz = l.quiz
    .map((q, i) => `${i + 1}. ${q.q}\n${q.opts.map((o, j) => `   ${j === q.a ? '(correct)' : '-'} ${o}`).join('\n')}`)
    .join('\n');
  return [
    l.body,
    l.summary && `## Summary\n${l.summary}`,
    l.frc && `## FRC link\n${l.frc}`,
    l.lab && `## PC lab\n${l.lab}`,
    quiz && `## Quiz\n${quiz}`,
  ]
    .filter(Boolean)
    .join('\n\n');
}

// Lessons in this learner's track, and the first one not yet completed.
export function progress() {
  const list = track(state.settings.learner);
  const written = list.filter((l) => hasContent(l.id));
  const done = list.filter((l) => state.done[l.id]).length;
  const next = written.find((l) => !state.done[l.id]) || null;
  return { list, total: list.length, done, written: written.length, next };
}
