import { state, save, currentStreak } from '../lib/store.js';
import { esc } from '../lib/util.js';
import { progress, hasContent } from '../lib/content.js';
import { moduleByN, inTrack, label } from '../data/curriculum.js';

function chooser(root) {
  root.innerHTML = `
    <h1>MechaLab</h1>
    <div class="card hero">
      <h3 style="font-size:20px">Who is learning on this device?</h3>
      <p class="muted">This sets which lessons are in your track and how the AI tutor explains things. You can change it later in Settings.</p>
    </div>
    <button class="card tap choice" data-who="parent">
      <h3>🧑‍💼 Parent</h3>
      <div class="muted small">Engineering degree, strong math, fluent in Python. Skips the math bridge lessons.</div>
    </button>
    <button class="card tap choice" data-who="student">
      <h3>🎓 Student</h3>
      <div class="muted small">Grade 11 with FTC / FRC experience. Includes the six math bridge lessons.</div>
    </button>`;
  root.querySelectorAll('[data-who]').forEach((b) => {
    b.onclick = () => {
      state.settings.learner = b.dataset.who;
      save();
      home(root);
    };
  });
}

export default function home(root) {
  if (!state.settings.learner) return chooser(root);

  const p = progress();
  const pct = p.total ? Math.round((p.done / p.total) * 100) : 0;
  const next = p.next;
  const mod = next ? moduleByN[next.module] : null;
  const modLessons = mod ? mod.lessons.filter((l) => inTrack(l, state.settings.learner)) : [];
  const modDone = modLessons.filter((l) => state.done[l.id]).length;
  const modWritten = modLessons.filter((l) => hasContent(l.id)).length;

  const cont = next
    ? `<div class="muted small">Up next · Module ${mod.n}: ${esc(mod.title)}</div>
       <div class="big" style="font-size:24px;margin:2px 0 12px">${esc(label(next))} ${esc(next.title)}</div>
       <a class="btn primary block" href="#/lesson/${encodeURIComponent(next.id)}">${p.done ? 'Continue' : 'Start the course'}</a>`
    : `<div class="big" style="font-size:22px;margin-bottom:6px">You are caught up</div>
       <p class="muted">Every lesson written so far is complete (${p.written} of ${p.total}). More lessons are on the way.</p>
       <a class="btn primary block" href="#/course">Review the course</a>`;

  root.innerHTML = `
    <h1>MechaLab</h1>
    <div class="card hero">
      ${cont}
      <div class="stats">
        <div><b>${p.done}/${p.total}</b><span>lessons done</span></div>
        <div><b>${pct}%</b><span>of the course</span></div>
        <div><b>${currentStreak()}</b><span>day streak</span></div>
      </div>
    </div>

    ${
      mod
        ? `<h2>Current module</h2>
    <a class="card tap" href="#/course">
      <div class="row spread"><h3>Module ${mod.n} · ${esc(mod.title)}</h3><span class="tag">${modDone}/${modLessons.length}</span></div>
      <div class="muted small">${esc(mod.blurb)}</div>
      <div class="progress" style="margin:12px 0 0"><i style="width:${modLessons.length ? (modDone / modLessons.length) * 100 : 0}%"></i></div>
      ${modWritten < modLessons.length ? `<div class="muted small" style="margin-top:8px">${modWritten} of ${modLessons.length} lessons written so far</div>` : ''}
    </a>`
        : ''
    }

    <h2>Tools</h2>
    <a class="card tap" href="#/ask">
      <h3>💬 Ask the tutor</h3>
      <div class="muted small">${state.settings.apiKey ? 'Ask anything about mechatronics and robotics, or paste code and errors from a lab.' : 'Needs a Claude API key. Add one in Settings.'}</div>
    </a>
    <div class="card">
      <h3>💻 Labs run on your PC</h3>
      <div class="muted small">Open this app in a browser on your PC to copy lab code, or run the scripts in the project's <code>labs/</code> folder.</div>
    </div>`;
}
