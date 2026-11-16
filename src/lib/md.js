// Markdown + LaTeX + code highlighting, shared by lessons and tutor replies.
import { Marked } from 'marked';
import markedKatex from 'marked-katex-extension';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import c from 'highlight.js/lib/languages/c';
import cpp from 'highlight.js/lib/languages/cpp';
import java from 'highlight.js/lib/languages/java';
import xml from 'highlight.js/lib/languages/xml';
import bash from 'highlight.js/lib/languages/bash';
import DOMPurify from 'dompurify';
import 'katex/dist/katex.min.css';
import { esc, toast } from './util.js';

hljs.registerLanguage('python', python);
hljs.registerLanguage('c', c);
hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('java', java);
hljs.registerLanguage('xml', xml);
hljs.registerLanguage('bash', bash);

const marked = new Marked({ gfm: true });
// output:'html' skips MathML, so the result survives sanitizing unchanged
marked.use(markedKatex({ throwOnError: false, nonStandard: true, output: 'html' }));
marked.use({
  renderer: {
    code({ text, lang }) {
      const language = (lang || '').trim().split(/\s+/)[0];
      const html = hljs.getLanguage(language) ? hljs.highlight(text, { language }).value : esc(text);
      return `<div class="code"><button class="copy" type="button">Copy</button><pre><code class="hljs">${html}</code></pre></div>`;
    },
  },
});

// Trusted content (our own lesson files): inline SVG figures are allowed.
export const renderLesson = (text) => marked.parse(text || '');

// Untrusted content (model output): normalize \( \) and \[ \] math, then sanitize.
export function renderReply(text) {
  const src = String(text || '')
    .replace(/\\\[([\s\S]+?)\\\]/g, (_, m) => `\n$$\n${m.trim()}\n$$\n`)
    .replace(/\\\(([\s\S]+?)\\\)/g, (_, m) => `$${m.trim()}$`);
  return DOMPurify.sanitize(marked.parse(src));
}

// One delegated handler for every "Copy" button on a code block.
document.addEventListener('click', async (e) => {
  const btn = e.target.closest?.('.code .copy');
  if (!btn) return;
  const text = btn.parentElement.querySelector('code').textContent;
  try {
    await navigator.clipboard.writeText(text);
    toast('Code copied');
  } catch {
    toast('Could not copy; select the code manually');
  }
});
