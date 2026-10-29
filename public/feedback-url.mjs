export const FEEDBACK_REPO = 'GlenTiki/agentic-harness-guide';
export const FEEDBACK_TEMPLATE = 'feedback.yml';
export const PREFILLED_FIELDS = ['page', 'section', 'quote', 'device'];
export const READER_FIELDS = ['kind', 'comment'];
export const MAX_URL_LENGTH = 1900;
export const MAX_QUOTE_LENGTH = 500;
const ELLIPSIS = '…';
const LIMITS = { page: 300, section: 150, device: 120 };

const clean = (text, limit) => {
  const flat = String(text ?? '').replace(/\s+/g, ' ').trim();
  return flat.length > limit ? `${flat.slice(0, limit - 1)}${ELLIPSIS}` : flat;
};

const build = (fields) => {
  const query = [`template=${FEEDBACK_TEMPLATE}`];
  for (const name of PREFILLED_FIELDS) if (fields[name]) query.push(`${name}=${encodeURIComponent(fields[name])}`);
  if (fields.kind) query.push(`kind=${encodeURIComponent(fields.kind)}`);
  if (fields.comment) query.push(`comment=${encodeURIComponent(fields.comment)}`);
  return `https://github.com/${FEEDBACK_REPO}/issues/new?${query.join('&')}`;
};

export const buildFeedbackUrl = ({ page, section = '', quote = '', device = '', comment = '', kind = '' }) => {
  const fields = {
    page: clean(page, LIMITS.page),
    section: clean(section, LIMITS.section),
    device: clean(device, LIMITS.device),
    quote: clean(quote, MAX_QUOTE_LENGTH),
    comment: clean(comment, 600),
    kind: clean(kind, 50),
  };
  let url = build(fields);
  while (url.length > MAX_URL_LENGTH && fields.quote) {
    const excess = url.length - MAX_URL_LENGTH;
    const keep = Math.max(0, Array.from(fields.quote).length - Math.max(1, Math.ceil(excess / 9)) - 1);
    const shorter = Array.from(fields.quote).slice(0, keep).join('').trimEnd();
    fields.quote = shorter ? `${shorter}${ELLIPSIS}` : '';
    url = build(fields);
  }
  return url;
};
