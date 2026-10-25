import { defineRouteMiddleware } from '@astrojs/starlight/route-data';
import { getCollection } from 'astro:content';
import { jsonLdScript } from './data/jsonld';
import { dateModified, datePublished, type STATUS_LABELS } from './data/pages';
import { HOME_TITLE, OG_ALT, OG_IMAGE, pageUrl, SITE_URL, twinUrl } from './data/site';

type HeadTag = { tag: string; attrs?: Record<string, string | boolean | undefined>; content?: string };

const setMeta = (head: HeadTag[], key: 'property' | 'name', name: string, content: string) => {
  const existing = head.find((tag) => tag.tag === 'meta' && tag.attrs?.[key] === name);
  if (existing) existing.attrs = { ...existing.attrs, content };
  else head.push({ tag: 'meta', attrs: { [key]: name, content } });
};

let titles: Map<string, string> | undefined;
const docTitles = async () => {
  titles ??= new Map((await getCollection('docs')).map((doc) => [doc.id, doc.data.title]));
  return titles;
};

const STUB_GLOSSARY = 'shelf/foundations/glossary';

export const onRequest = defineRouteMiddleware(async (context, next) => {
  await next();
  const route = context.locals.starlightRoute;
  const entry = route.entry as { id: string; data: { title: string; description?: string; status?: keyof typeof STATUS_LABELS }; filePath?: string };
  if (!entry.filePath || entry.id === '404') return;
  const head = route.head as HeadTag[];
  const id = entry.id || 'index';
  const isHome = id === 'index';

  if (isHome) {
    const title = head.find((tag) => tag.tag === 'title');
    if (title) title.content = HOME_TITLE;
  }
  setMeta(head, 'property', 'og:type', isHome ? 'website' : 'article');
  setMeta(head, 'property', 'og:image', OG_IMAGE);
  setMeta(head, 'property', 'og:image:width', '1200');
  setMeta(head, 'property', 'og:image:height', '630');
  setMeta(head, 'property', 'og:image:alt', OG_ALT);
  setMeta(head, 'name', 'twitter:image', OG_IMAGE);
  setMeta(head, 'name', 'twitter:image:alt', OG_ALT);

  head.push({ tag: 'link', attrs: { rel: 'alternate', type: 'text/markdown', href: twinUrl(id) } });
  head.push({ tag: 'link', attrs: { rel: 'alternate', type: 'application/atom+xml', href: `${SITE_URL}feed.xml`, title: 'Recently changed pages' } });
  head.push({ tag: 'link', attrs: { rel: 'describedby', type: 'text/plain', href: `${SITE_URL}llms.txt` } });

  if (id === STUB_GLOSSARY) {
    head.push({ tag: 'meta', attrs: { name: 'robots', content: 'noindex' } });
    const canonical = head.find((tag) => tag.tag === 'link' && tag.attrs?.rel === 'canonical');
    if (canonical) canonical.attrs = { ...canonical.attrs, href: pageUrl('glossary') };
    return;
  }

  const known = await docTitles();
  head.push({
    tag: 'script',
    attrs: { type: 'application/ld+json' },
    content: jsonLdScript({
      id,
      title: entry.data.title,
      description: entry.data.description ?? '',
      status: entry.data.status,
      datePublished: datePublished(entry as never),
      dateModified: dateModified(entry as never),
      titleFor: (ancestor) => known.get(ancestor) ?? null,
    }),
  });
});
