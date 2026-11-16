import { state, save, markDone, unmarkDone } from '../lib/store.js';
import { esc, toast } from '../lib/util.js';
import { getLesson } from '../lib/content.js';
import { renderLesson } from '../lib/md.js';
import { LESSONS, lessonById, moduleByN, TAG_LABEL, inTrack, label } from '../data/curriculum.js';

export default function lesson(root, [id]) {
  const meta = lessonById[id];
  if (!meta) {
    root.innerHTML = `<a href="#/course" class="small">‹ Course</a><h1>Lesson not found</h1>`;
    return;
  }
  const mod = moduleByN[meta.module];
  const data = getLesson(id);
  const learner = state.settings.learner;
  const href = (l) => `#/lesson/${encodeURIComponent(l.id)}`;

  // Previous / next within this learner's track (the current lesson is always included).
  const list = LESSONS.filter((l) => l.id === id || inTrack(l, learner));
  const at = list.findIndex((l) => l.id === id);
  const prev = list[at - 1];
  const next = list[at + 1];

  state.last = id;
  save();

  const head = `
    <a href="#/course" class="small">‹ Module ${mod.n} · ${esc(mod.title)}</a>
    <h1 style="margin-bottom:6px">${esc(label(meta))} · ${esc(meta.title)}</h1>
    <div class="row wrap" style="margin-bottom:14px">
      ${meta.tag ? `<span class="tag ${meta.tag === 'bridge' ? 'warn' : 'gray'}">${TAG_LABEL[meta.tag]}</span>` : ''}
      ${meta.tag === 'bridge' && learner === 'parent' ? '<span class="muted small">Optional for you: a math bridge lesson for the student.</span>' : ''}
      ${meta.tag === 'review' ? `<span class="muted small">${learner === 'student' ? 'New material for you. Take it slowly.' : 'A refresher of something you studied before.'}</span>` : ''}
    </div>`;

  const nav = `
    <div class="row mt">
      ${prev ? `<a class="btn grow" href="${href(prev)}">‹ ${esc(label(prev))}</a>` : '<span class="grow"></span>'}
      ${next ? `<a class="btn grow" href="${href(next)}">${esc(label(next))} ›</a>` : '<span class="grow"></span>'}
    </div>`;

  const fab = document.createElement('a');
  fab.className = 'fab';
  fab.href = `#/ask/${encodeURIComponent(id)}`;
  fab.textContent = '💬 Ask tutor';
  document.body.appendChild(fab);

  if (!data) {
    root.innerHTML = `${head}
      <div class="card">
        <h3>This lesson is not written yet</h3>
        <p class="muted">Lessons are being added module by module. In the meantime the tutor can teach you this topic directly.</p>
        <a class="btn primary block" href="#/ask/${encodeURIComponent(id)}">Ask the tutor about this topic</a>
      </div>${nav}`;
    return;
  }

  const answers = new Array(data.quiz.length).fill(null);
  const quizHtml = data.quiz
    .map(
      (q, i) => `<div class="card quiz" data-q="${i}">
        <div class="md"><b>${i + 1}.</b> ${renderLesson(q.q).replace(/^<p>/, '')}</div>
        ${q.opts.map((o, j) => `<button class="opt md" data-o="${j}">${renderLesson(o)}</button>`).join('')}
        <div class="why md small" hidden>${renderLesson(q.why)}</div>
      </div>`,
    )
    .join('');

  root.innerHTML = `${head}
    <article class="md lesson">${renderLesson(data.body)}</article>
    ${data.frc ? `<div class="callout frc"><div class="callout-h">🤖 FRC link</div><div class="md">${renderLesson(data.frc)}</div></div>` : ''}
    ${data.summary ? `<div class="callout"><div class="callout-h">📌 Key points</div><div class="md">${renderLesson(data.summary)}</div></div>` : ''}
    ${data.lab ? `<h2>💻 PC lab</h2><div class="card"><div class="md lesson">${renderLesson(data.lab)}</div></div>` : ''}
    ${data.quiz.length ? `<h2>Quiz</h2>${quizHtml}<p class="center muted small" id="score"></p>` : ''}
    <button class="primary block mt" id="done"></button>
    ${nav}`;

  const doneBtn = root.querySelector('#done');
  const paint = () => {
    const d = state.done[id];
    doneBtn.textContent = d ? '✓ Completed · tap to undo' : 'Mark lesson complete';
    doneBtn.classList.toggle('primary', !d);
  };
  paint();

  const quizScore = () => {
    if (!data.quiz.length || answers.some((a) => a === null)) return [null, null];
    return [answers.filter((a, i) => a === data.quiz[i].a).length, data.quiz.length];
  };

  doneBtn.onclick = () => {
    if (state.done[id]) {
      unmarkDone(id);
    } else {
      markDone(id, ...quizScore());
      toast('Lesson complete');
    }
    paint();
  };

  root.querySelectorAll('.quiz').forEach((card) => {
    const i = +card.dataset.q;
    const q = data.quiz[i];
    card.querySelectorAll('.opt').forEach((btn) => {
      btn.onclick = () => {
        if (answers[i] !== null) return;
        const pick = +btn.dataset.o;
        answers[i] = pick;
        card.querySelectorAll('.opt').forEach((b) => {
          const j = +b.dataset.o;
          if (j === q.a) b.classList.add('right');
          else if (j === pick) b.classList.add('wrong');
          else b.classList.add('dim');
        });
        if (q.why) card.querySelector('.why').hidden = false;
        const [score, total] = quizScore();
        if (score !== null) {
          root.querySelector('#score').textContent = `Quiz score: ${score} / ${total}`;
          if (state.done[id]) markDone(id, score, total);
        }
      };
    });
  });
}
