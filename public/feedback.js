import { buildFeedbackUrl, MAX_QUOTE_LENGTH } from './feedback-url.mjs';

const HEADINGS = '.sl-markdown-content h1, .sl-markdown-content h2, .sl-markdown-content h3, .sl-markdown-content h4';
let held = '';
let heldAt = 0;
const PRESS_MS = 1000;

const liveSelection = () => (getSelection()?.toString() ?? '').trim();

const selectedText = () => liveSelection() || (Date.now() - heldAt < PRESS_MS * 3 ? held : '');

const referenceY = () => {
  const selection = getSelection();
  if (selection && selection.rangeCount && selection.toString().trim()) return selection.getRangeAt(0).getBoundingClientRect().top;
  return innerHeight * 0.3;
};

const nearestHeading = () => {
  const y = referenceY();
  const above = [...document.querySelectorAll(HEADINGS)].filter((h) => h.getBoundingClientRect().top <= y + 1);
  return above.at(-1) ?? document.querySelector('h1');
};

const upgrade = (link) => {
  const heading = nearestHeading();
  const scheme = document.documentElement.dataset.theme ?? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const page = location.pathname + (heading?.id && heading.matches('h2, h3, h4') ? `#${heading.id}` : '');
  link.href = buildFeedbackUrl({
    page,
    section: heading?.textContent ?? '',
    quote: selectedText(),
    device: `${innerWidth}x${innerHeight}, ${scheme}, guide ${link.dataset.build ?? ''}`,
  });
};

for (const link of document.querySelectorAll('a[data-feedback]')) {
  for (const type of ['pointerdown', 'touchstart']) {
    link.addEventListener(
      type,
      () => {
        const live = liveSelection();
        if (live || Date.now() - heldAt > PRESS_MS) held = live;
        if (live) heldAt = Date.now();
        upgrade(link);
      },
      { passive: true },
    );
  }
  link.addEventListener('focus', () => upgrade(link));
  link.addEventListener('click', () => {
    upgrade(link);
    held = '';
  });
}
