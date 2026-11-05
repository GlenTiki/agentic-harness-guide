import review from './review.json';

export const SITE_ORIGIN = 'https://glentiki.dev';
export const BASE = '/agentic-harness-guide';
export const SITE_URL = `${SITE_ORIGIN}${BASE}/`;
export const SITE_NAME = 'Judgement First';
export const AUTHOR = 'Glen Keane';
export const AUTHOR_URL = 'https://glentiki.dev/';
export const LICENCE = 'Text CC BY 4.0, code MIT';
export const REPO_URL = 'https://github.com/GlenTiki/agentic-harness-guide';
export const LAST_REVIEWED: string = review.lastReviewed;
export const HOME_TITLE = 'Judgement First: A guide to working with AI';
export const OG_IMAGE = `${SITE_URL}og.png`;
export const OG_ALT = 'Judgement First. A guide to working with AI. Set the task. Check the work. Decide what is worth using. Glen Keane.';

export const pageUrl = (id: string) => (id === 'index' ? SITE_URL : `${SITE_URL}${id}/`);
export const twinUrl = (id: string) => `${SITE_URL}${id}.md`;
