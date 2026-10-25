import review from './review.json';

export const SITE_ORIGIN = 'https://glentiki.dev';
export const BASE = '/agentic-harness-guide';
export const SITE_URL = `${SITE_ORIGIN}${BASE}/`;
export const SITE_NAME = 'The Agentic Harness Guide';
export const AUTHOR = 'Glen Keane';
export const AUTHOR_URL = 'https://glentiki.dev/';
export const LICENCE = 'Text CC BY 4.0, code MIT';
export const REPO_URL = 'https://github.com/GlenTiki/agentic-harness-guide';
export const LAST_REVIEWED: string = review.lastReviewed;
export const HOME_TITLE = 'Agentic harness guide: reliable work from AI assistants';
export const OG_IMAGE = `${SITE_URL}og.png`;
export const OG_ALT =
  'Title card reading Get dependable work from an AI assistant, with two cards for the same 40 bills: an observed assistant headline total of 7,414, wrong in 20 of 20 trials although every reply flagged the doubt, and a computed total of 7,281.';

export const pageUrl = (id: string) => (id === 'index' ? SITE_URL : `${SITE_URL}${id}/`);
export const twinUrl = (id: string) => `${SITE_URL}${id}.md`;
