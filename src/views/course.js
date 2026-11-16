import { state } from '../lib/store.js';
import { esc } from '../lib/util.js';
import { progress, hasContent } from '../lib/content.js';
import { MODULES, TAG_LABEL, inTrack, label } from '../data/curriculum.js';

export default function course(root) {
  const learner = state.settings.learner;
  const p = progress();
  const openModule = p.next ? p.next.module : 0;

  const row = (l) => {
    const done = !!state.done[l.id];
    const optional = !inTrack(l, learner);
    const written = hasContent(l.id);
    return `<a class="list-item lesson-row ${written ? '' : 'unwritten'}" href="#/lesson/${encodeURIComponent(l.id)}">
        <span class="dot ${done ? 'done' : ''}">${done ? '✓' : ''}</span>
        <span class="grow"><span class="muted small">${esc(label(l))}</span><br />${esc(l.title)}</span>
        ${l.tag ? `<span class="tag ${l.tag === 'bridge' ? 'warn' : 'gray'}">${TAG_LABEL[l.tag]}${optional ? ' · optional' : ''}</span>` : ''}
        ${written ? '' : '<span class="tag gray">soon</span>'}
      </a>`;
  };

  const modules = MODULES.map((m) => {
    const mine = m.lessons.filter((l) => inTrack(l, learner));
    const done = mine.filter((l) => state.done[l.id]).length;
    return `<details class="card module" ${m.n === openModule ? 'open' : ''}>
        <summary>
          <div class="row spread">
            <h3>Module ${m.n} · ${esc(m.title)}</h3>
            <span class="tag ${done === mine.length ? 'ok' : ''}">${done}/${mine.length}</span>
          </div>
          <div class="muted small">${esc(m.blurb)}</div>
        </summary>
        <div class="mt">${m.lessons.map(row).join('')}</div>
        ${m.note ? `<div class="note small">🔧 ${esc(m.note)}</div>` : ''}
      </details>`;
  }).join('');

  root.innerHTML = `
    <h1>Course</h1>
    <div class="row spread small muted"><span>${p.done} of ${p.total} lessons done</span><span>${p.written} written so far</span></div>
    <div class="progress"><i style="width:${p.total ? (p.done / p.total) * 100 : 0}%"></i></div>
    ${modules}`;
}
