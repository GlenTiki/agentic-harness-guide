import { buildFeedbackUrl, LOCAL_HOSTNAME, MAX_QUOTE_LENGTH } from './feedback-url.mjs';

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

const ISSUE_KIND = { improvement: 'Idea', correction: 'Wrong', unclear: 'Confusing', praise: 'Worked well' };
const LOOPBACK_HOST = /^(?:localhost$|127\.|\[::1\]$)/;

const localReceiver = () => {
  const { hostname } = location;
  if (!LOCAL_HOSTNAME.test(hostname)) return null;
  return `http://${LOOPBACK_HOST.test(hostname) ? '127.0.0.1' : hostname}:4328/api/feedback`;
};

const sendToLocalReceiver = async (endpoint, payload) => {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.ok;
  } catch {
    return false;
  }
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

const setupModal = () => {
  const dialog = document.getElementById('feedback-modal');
  if (!dialog) return;

  const form = document.getElementById('feedback-form');
  const pageSpan = dialog.querySelector('[data-feedback-page]');
  const sectionSpan = dialog.querySelector('[data-feedback-section]');
  const quotePreview = dialog.querySelector('[data-feedback-quote]');
  const statusEl = dialog.querySelector('[data-feedback-status]');
  const textarea = dialog.querySelector('#feedback-text');
  const categorySelect = dialog.querySelector('#feedback-category');
  const fallbackLink = dialog.querySelector('[data-github-fallback]');
  const closeBtn = dialog.querySelector('[data-action="close-feedback"]');
  const submitBtn = form?.querySelector('[type="submit"]');
  if (submitBtn && !localReceiver()) submitBtn.textContent = 'Prepare GitHub issue';
  let context = {};

  const openModal = (e) => {
    if (e) e.preventDefault();
    const heading = nearestHeading();
    const quote = selectedText();
    held = '';
    const scheme = document.documentElement.dataset.theme ?? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const pageWithHash = location.pathname + (heading?.id && heading.matches('h2, h3, h4') ? `#${heading.id}` : '');
    const currentSection = heading?.textContent?.trim() ?? '';
    context = { page: pageWithHash, section: currentSection, quote, device: `${innerWidth}x${innerHeight}, ${scheme}` };

    if (pageSpan) pageSpan.textContent = location.pathname;
    if (sectionSpan) sectionSpan.textContent = currentSection ? ` • ${currentSection}` : '';
    if (quotePreview) {
      if (quote) {
        quotePreview.textContent = `"${quote.slice(0, 160)}${quote.length > 160 ? '...' : ''}"`;
        quotePreview.hidden = false;
      } else {
        quotePreview.hidden = true;
      }
    }

    if (fallbackLink) {
      fallbackLink.href = buildFeedbackUrl(context);
    }

    if (statusEl) {
      statusEl.textContent = '';
      statusEl.className = 'feedback-status';
    }

    if (typeof dialog.showModal === 'function') {
      dialog.showModal();
    } else {
      dialog.setAttribute('open', '');
    }
    textarea?.focus();
  };

  const closeModal = () => {
    if (typeof dialog.close === 'function') {
      dialog.close();
    } else {
      dialog.removeAttribute('open');
    }
  };

  closeBtn?.addEventListener('click', closeModal);
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) closeModal();
  });

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const comment = textarea?.value?.trim() ?? '';
    if (!comment) return;

    const payload = {
      ...context,
      category: categorySelect?.value ?? 'improvement',
      feedback: comment,
      timestamp: new Date().toISOString(),
    };

    const receiver = localReceiver();
    if (receiver) {
      if (statusEl) {
        statusEl.textContent = 'Sending feedback to receiver...';
        statusEl.className = 'feedback-status sending';
      }
      if (await sendToLocalReceiver(receiver, payload)) {
        if (statusEl) {
          statusEl.textContent = 'Received! Stored in backend queue for review and iteration.';
          statusEl.className = 'feedback-status success';
        }
        if (textarea) textarea.value = '';
        setTimeout(() => {
          closeModal();
        }, 1600);
        return;
      }
    }

    const issueUrl = buildFeedbackUrl({
      page: payload.page,
      section: payload.section,
      quote: payload.quote,
      comment: payload.feedback,
      kind: ISSUE_KIND[payload.category] ?? 'Idea',
      device: payload.device,
    });

    if (statusEl) {
      statusEl.innerHTML = `<span>Not sent yet. Review the public issue draft on GitHub before posting. The link carries at most 600 characters of your feedback; copy longer text from this box.</span><br/><a href="${issueUrl}" target="_blank" rel="noopener" style="display:inline-block; margin-top:8px; padding:8px 14px; background:#4f46e5; color:#ffffff; border-radius:6px; font-weight:600; text-decoration:none;">Review draft on GitHub &rarr;</a>`;
      statusEl.className = 'feedback-status fallback';
    }
  });

  const floatingBtn = document.querySelector('a.feedback-button[data-feedback]');
  if (floatingBtn) {
    floatingBtn.addEventListener('click', (e) => {
      openModal(e);
    });
  }
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
    if (!link.matches('.feedback-button')) held = '';
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setupModal);
} else {
  setupModal();
}
