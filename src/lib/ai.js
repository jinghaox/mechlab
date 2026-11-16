import Anthropic from '@anthropic-ai/sdk';
import { state } from './store.js';
import { lessonById, moduleByN, label } from '../data/curriculum.js';
import { lessonText, progress } from './content.js';

// Models selectable in Settings. Prices are USD per million tokens (input / output).
// fallback: whether the model supports server-side fallback (when the main model declines a
// request for safety-policy reasons, the API retries it on a fallback model automatically).
export const MODELS = [
  { id: 'claude-opus-5-5', name: 'Claude Opus 5.5', note: 'best explanations', price: '$4 / $20', fallback: true },
  { id: 'claude-sonnet-5-5', name: 'Claude Sonnet 5.5', note: 'balanced, about half the price', price: '$2 / $10', fallback: true },
  { id: 'claude-haiku-5-5', name: 'Claude Haiku 5.5', note: 'cheapest', price: '$0.10 / $0.50', fallback: false },
];
const BETAS = ['server-side-fallback-2026-07-01'];

const currentModel = () => MODELS.find((m) => m.id === state.settings.model) || MODELS[0];

export const hasKey = () => !!state.settings.apiKey;

function client() {
  if (!hasKey()) throw new Error('Add your Claude API key in Settings first');
  // Personal, front-end-only app: the key stays in this browser and goes straight to api.anthropic.com
  return new Anthropic({ apiKey: state.settings.apiKey, dangerouslyAllowBrowser: true });
}

export function errorText(err) {
  if (err instanceof Anthropic.AuthenticationError) return 'The API key is not valid. Check it in Settings.';
  if (err instanceof Anthropic.PermissionDeniedError) return 'This key is not allowed to use this model.';
  if (err instanceof Anthropic.RateLimitError) return 'Too many requests. Try again in a moment.';
  if (err instanceof Anthropic.APIConnectionError) return 'Network error. Check your connection.';
  if (err instanceof Anthropic.APIError) return `Claude API error (${err.status ?? '?'}): ${err.message}`;
  return err?.message || String(err);
}

export const textOf = (content) =>
  typeof content === 'string'
    ? content
    : content
        .filter((b) => b.type === 'text')
        .map((b) => b.text)
        .join('');

// Streaming request. Returns { text, content }; content is the full block array, which must be
// sent back unchanged on later turns (it includes thinking blocks).
export async function ask({ system, messages, onText, maxTokens = 32000 }) {
  const model = currentModel();
  const params = { model: model.id, max_tokens: maxTokens, output_config: { effort: 'medium' }, system, messages };
  const stream = model.fallback
    ? client().beta.messages.stream({ ...params, betas: BETAS, fallbacks: 'default' })
    : client().messages.stream(params);
  let soFar = '';
  for await (const event of stream) {
    if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
      soFar += event.delta.text;
      onText?.(soFar);
    }
  }
  const msg = await stream.finalMessage();
  if (msg.stop_reason === 'refusal') throw new Error('The model declined this request. Try rephrasing it.');
  return { text: textOf(msg.content), content: msg.content };
}

const LEARNERS = {
  parent:
    'An adult engineer. Studied circuit theory, digital and analog electronics, calculus, linear algebra, random processes and signal processing at university (some of it rusty, but picks it back up quickly). Fluent in Python, has written C. New to control theory, motors and drives, embedded real-time programming and robotics. You can use university-level math freely; when a forgotten prerequisite matters, restate it in a sentence rather than assuming it.',
  student:
    'A grade 11 student with FTC and FRC competition experience and a COSMOS robotics summer program. Comfortable building and programming competition robots (WPILib-style code), but has not yet formally studied linear algebra, complex numbers, differential equations or probability. Build intuition first, introduce each new piece of math before using it, and connect ideas to FTC/FRC mechanisms and WPILib where that genuinely helps.',
};

// System prompt for the tutor. lessonId is '' for a general question.
export function tutorSystem(lessonId) {
  const lesson = lessonById[lessonId];
  const p = progress();
  const who = LEARNERS[state.settings.learner] || LEARNERS.parent;

  let context;
  if (!lesson) {
    context = 'The learner opened the tutor without a specific lesson; answer general mechatronics and robotics questions.';
  } else {
    const where = `${label(lesson)} "${lesson.title}" (Module ${lesson.module}: ${moduleByN[lesson.module].title})`;
    const body = lessonText(lesson.id);
    context = body
      ? `The learner is asking from lesson ${where}. The full lesson, including its lab and quiz, is below. Base your answers on it and use its notation.\n\n<lesson>\n${body}\n</lesson>`
      : `The learner is asking about lesson ${where}. Its text has not been written yet, so teach the topic yourself at the level this course position implies.`;
  }

  return `You are the tutor inside MechaLab, a self-study course in mechatronics and robotics. Lessons are read on a phone; labs are done on a PC in Python with NumPy, SciPy, python-control and MuJoCo.

The course runs in this order: setup, modeling dynamic systems, classical control, robot kinematics, dynamics and arm control, actuators and drives, sensors and signals, embedded systems, modern control, state estimation, mobile robots, ROS 2, perception and learning. The learner has completed ${p.done} of ${p.total} lessons${p.next ? ` and is up to ${label(p.next)} "${p.next.title}"` : ''}, so treat later topics as not yet covered.

The learner: ${who}

${context}

How to answer:
- Answer the question that was asked, at the depth it needs. Replies are read on a phone, so prefer a few short paragraphs to a long essay, and offer to go deeper rather than front-loading everything.
- Explain why, not just what. A small worked example with real numbers usually helps more than another restatement.
- When the learner asks about a quiz question or is stuck on a lab, help them reason their way to it: point at the relevant idea or the likely bug first, and give the full answer if they ask for it or are still stuck.
- When they paste code or an error message, find the actual cause and show the corrected lines.
- If something in the lesson looks wrong or the learner's premise is mistaken, say so plainly.
- Write in English. If the learner writes in Chinese, answer in Chinese and keep technical terms in English.
- Format with Markdown. Write math in LaTeX with $...$ for inline and $$...$$ for display. Put code in fenced blocks with a language tag.`;
}
