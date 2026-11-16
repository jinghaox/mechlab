import { state, save, touchStreak } from '../lib/store.js';
import { esc, toast } from '../lib/util.js';
import { hasKey, ask as askClaude, errorText, textOf, tutorSystem } from '../lib/ai.js';
import { renderReply } from '../lib/md.js';
import { lessonById, label } from '../data/curriculum.js';
import { hasContent } from '../lib/content.js';

const LESSON_CHIPS = [
  'Explain the main idea of this lesson more simply',
  'Give me another worked example',
  'Ask me three questions to check my understanding',
  'Where is this used on a real robot?',
];
const GENERAL_CHIPS = [
  'What should I review before the next lesson?',
  'How does a PID controller work, intuitively?',
  'Help me debug my lab code',
];

export default function ask(root, [id = '']) {
  const lesson = lessonById[id];
  const key = lesson ? lesson.id : 'general';
  const title = lesson
    ? `<a href="#/lesson/${encodeURIComponent(lesson.id)}">‹ ${esc(label(lesson))} · ${esc(lesson.title)}</a>`
    : '<span class="muted">General questions</span>';

  if (!hasKey()) {
    root.innerHTML = `
      <div class="small">${title}</div>
      <h1>Tutor</h1>
      <div class="card">
        <h3>A Claude API key is needed</h3>
        <p class="muted">The tutor is powered by Claude. Add your own Anthropic API key in Settings; it is stored only in this browser.</p>
        <a class="btn primary block" href="#/settings">Open Settings</a>
      </div>`;
    return;
  }

  const thread = () => (state.chats[key] ||= []);
  let busy = false;

  root.innerHTML = `
    <div class="small">${title}</div>
    <div class="row spread">
      <h1>Tutor</h1>
      <button id="new" class="ghost small">New chat</button>
    </div>
    <div class="chat-log" id="log"></div>`;

  const composer = document.createElement('div');
  composer.className = 'composer';
  composer.innerHTML = `<div class="row">
      <textarea id="input" rows="1" class="grow" placeholder="Ask a question, or paste code or an error…"></textarea>
      <button class="primary" id="send">Send</button>
    </div>`;
  document.body.appendChild(composer);

  const log = root.querySelector('#log');
  const input = composer.querySelector('#input');
  const scrollDown = () => window.scrollTo(0, document.body.scrollHeight);
  const grow = () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 140) + 'px';
  };
  input.addEventListener('input', grow);

  function bubble(role, text) {
    const el = document.createElement('div');
    el.className = `bubble ${role}`;
    if (role === 'user') el.textContent = text;
    else el.innerHTML = `<div class="md">${renderReply(text)}</div>`;
    log.appendChild(el);
    return el;
  }

  function renderAll() {
    log.innerHTML = '';
    const msgs = thread();
    if (!msgs.length) {
      const chips = lesson && hasContent(lesson.id) ? LESSON_CHIPS : lesson ? [`Teach me: ${lesson.title}`, ...GENERAL_CHIPS.slice(1)] : GENERAL_CHIPS;
      log.innerHTML = `<p class="muted small">${lesson ? 'The tutor can see this lesson, its lab and its quiz.' : 'Open the tutor from a lesson to ask about that lesson specifically.'}</p>
        <div class="chips">${chips.map((c) => `<button class="chip">${esc(c)}</button>`).join('')}</div>`;
      log.querySelectorAll('.chip').forEach((b) => {
        b.onclick = () => send(b.textContent);
      });
      return;
    }
    msgs.forEach((m) => bubble(m.role, textOf(m.content)));
    scrollDown();
  }

  async function run() {
    busy = true;
    const el = bubble('assistant', '');
    const md = el.querySelector('.md');
    md.innerHTML = '<span class="spinner"></span>';
    scrollDown();
    // Re-render at most once per frame while the reply streams in.
    let latest = null;
    let scheduled = false;
    const paint = () => {
      scheduled = false;
      if (latest === null) return;
      const nearBottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 120;
      md.innerHTML = renderReply(latest);
      if (nearBottom) scrollDown();
    };
    try {
      const res = await askClaude({
        system: tutorSystem(lesson ? lesson.id : ''),
        messages: thread(),
        onText: (t) => {
          latest = t;
          if (!scheduled) {
            scheduled = true;
            requestAnimationFrame(paint);
          }
        },
      });
      latest = null;
      // Keep the full content blocks (thinking included); they must be sent back unchanged.
      thread().push({ role: 'assistant', content: res.content });
      save();
      md.innerHTML = renderReply(res.text);
      touchStreak();
    } catch (e) {
      latest = null;
      el.remove();
      toast(errorText(e));
      // Roll back the unanswered question so it can be edited and re-sent.
      const msgs = thread();
      const last = msgs[msgs.length - 1];
      if (last?.role === 'user') {
        msgs.pop();
        save();
        log.lastElementChild?.remove();
        input.value = textOf(last.content);
        grow();
        if (!msgs.length) renderAll();
      }
    }
    busy = false;
  }

  function send(preset) {
    const text = (typeof preset === 'string' ? preset : input.value).trim();
    if (!text || busy) return;
    if (!thread().length) log.innerHTML = '';
    if (typeof preset !== 'string') {
      input.value = '';
      grow();
    }
    thread().push({ role: 'user', content: text });
    save();
    bubble('user', text);
    run();
  }

  composer.querySelector('#send').onclick = send;
  root.querySelector('#new').onclick = () => {
    if (busy) return;
    if (thread().length && !confirm('Start a new chat? The current conversation will be cleared.')) return;
    state.chats[key] = [];
    save();
    renderAll();
  };

  renderAll();
}
