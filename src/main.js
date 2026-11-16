import './style.css';
import 'highlight.js/styles/github-dark.css';
import home from './views/home.js';
import course from './views/course.js';
import lesson from './views/lesson.js';
import ask from './views/ask.js';
import settings from './views/settings.js';

const routes = { home, course, lesson, ask, settings };
const tabOf = { lesson: 'course' };
const app = document.getElementById('app');

function route() {
  const [name = 'home', ...rest] = location.hash.replace(/^#\/?/, '').split('/');
  const key = routes[name] ? name : 'home';
  document.querySelectorAll('.composer, .fab').forEach((el) => el.remove());
  app.innerHTML = '';
  window.scrollTo(0, 0);
  routes[key](app, rest.map(decodeURIComponent));
  const tab = tabOf[key] || key;
  document.querySelectorAll('#tabbar a').forEach((a) => a.classList.toggle('on', a.dataset.tab === tab));
}

window.addEventListener('hashchange', route);
route();

if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js').catch(() => {});
}
