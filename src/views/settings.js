import { state, save, resetProgress } from '../lib/store.js';
import { esc, toast } from '../lib/util.js';
import { MODELS } from '../lib/ai.js';

export default function settings(root) {
  const s = state.settings;
  root.innerHTML = `
    <h1>Settings</h1>

    <div class="card">
      <h3>Learner</h3>
      <p class="small muted">Sets which lessons are in your track and how the tutor explains things.</p>
      <div class="seg" id="learner">
        <button data-who="parent" class="${s.learner === 'parent' ? 'on' : ''}">Parent</button>
        <button data-who="student" class="${s.learner === 'student' ? 'on' : ''}">Student</button>
      </div>
    </div>

    <div class="card">
      <h3>Claude API key</h3>
      <p class="small muted">Used by the tutor. The key is stored only in this browser and is sent only to api.anthropic.com. Create one at console.anthropic.com; usage is billed to your account.</p>
      <input type="password" id="key" placeholder="sk-ant-…" autocomplete="off" value="${esc(s.apiKey)}" />
      <div class="row mt">
        <button class="primary grow" id="savekey">Save</button>
        <button class="grow" id="clearkey">Clear</button>
      </div>
      <label for="model">Tutor model</label>
      <select id="model">${MODELS.map((m) => `<option value="${m.id}" ${m.id === s.model ? 'selected' : ''}>${esc(m.name)} · ${esc(m.note)}</option>`).join('')}</select>
      <p class="small muted" id="modelnote" style="margin:8px 0 0"></p>
    </div>

    <div class="card">
      <h3>Progress</h3>
      <p class="small muted">Completed lessons, quiz scores and tutor chats are stored on this device only. Clearing the browser's data removes them.</p>
      <button class="block danger" id="reset">Reset progress and chats</button>
    </div>
    <p class="small muted center">MechaLab · version 0.1</p>`;

  root.querySelectorAll('#learner button').forEach((b) => {
    b.onclick = () => {
      s.learner = b.dataset.who;
      save();
      root.querySelectorAll('#learner button').forEach((x) => x.classList.toggle('on', x === b));
    };
  });
  root.querySelector('#savekey').onclick = () => {
    s.apiKey = root.querySelector('#key').value.trim();
    save();
    toast(s.apiKey ? 'Key saved' : 'Key is empty');
  };
  root.querySelector('#clearkey').onclick = () => {
    s.apiKey = '';
    root.querySelector('#key').value = '';
    save();
    toast('Key cleared');
  };
  const showModelNote = () => {
    const m = MODELS.find((x) => x.id === s.model) || MODELS[0];
    root.querySelector('#modelnote').textContent = `Price per million tokens (input / output): ${m.price}. Cheaper models give less careful derivations and debugging.`;
  };
  showModelNote();
  root.querySelector('#model').onchange = (e) => {
    s.model = e.target.value;
    save();
    showModelNote();
  };
  root.querySelector('#reset').onclick = () => {
    if (!confirm('Reset all completed lessons, quiz scores and tutor chats on this device? This cannot be undone.')) return;
    resetProgress();
    toast('Progress reset');
  };
}
