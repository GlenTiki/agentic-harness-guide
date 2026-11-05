import { levels } from './levels';
import { AUTHOR, AUTHOR_URL, OG_IMAGE, pageUrl, SITE_NAME, SITE_URL } from './site';

export interface PageFacts {
  id: string;
  title: string;
  description: string;
  datePublished: string;
  dateModified: string;
  status?: string;
  titleFor: (id: string) => string | null;
}

const author = { '@type': 'Person', name: AUTHOR, url: AUTHOR_URL };
const website = { '@type': 'WebSite', '@id': `${SITE_URL}#website`, name: SITE_NAME, url: SITE_URL, inLanguage: 'en' };

const breadcrumbs = (page: PageFacts) => {
  const parts = page.id.split('/');
  const trail = parts
    .slice(0, -1)
    .map((_, index) => parts.slice(0, index + 1).join('/'))
    .map((id) => ({ id, name: page.titleFor(id) }))
    .filter((crumb): crumb is { id: string; name: string } => crumb.name !== null);
  const items = [{ id: 'index', name: 'Home' }, ...trail, { id: page.id, name: page.title }];
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: pageUrl(item.id),
    })),
  };
};

const learningResource = (page: PageFacts) => ({
  '@type': 'LearningResource',
  name: page.title,
  description: page.description,
  url: pageUrl(page.id),
  inLanguage: 'en',
  author,
  isPartOf: { '@id': website['@id'] },
  learningResourceType: 'course',
  educationalLevel: 'beginner',
  teaches: 'How to get dependable, checkable work from an AI assistant',
  hasPart: levels.map((level, index) => ({
    '@type': 'LearningResource',
    name: `Level ${index}: ${level.title}`,
    url: pageUrl(`journey/${level.slug}`),
  })),
});

const article = (page: PageFacts) => ({
  '@type': 'TechArticle',
  headline: page.title.slice(0, 110),
  description: page.description,
  url: pageUrl(page.id),
  mainEntityOfPage: pageUrl(page.id),
  inLanguage: 'en',
  image: OG_IMAGE,
  author,
  isPartOf: { '@id': website['@id'] },
  datePublished: page.datePublished,
  dateModified: page.dateModified,
  ...(page.status ? { creativeWorkStatus: page.status } : {}),
});

export const jsonLdFor = (page: PageFacts) => {
  if (page.id === 'index') return [{ ...website, description: page.description, publisher: author }];
  const main = page.id === 'journey' ? learningResource(page) : article(page);
  return [main, breadcrumbs(page)];
};

export const jsonLdScript = (page: PageFacts) =>
  JSON.stringify({ '@context': 'https://schema.org', '@graph': jsonLdFor(page) }).replace(/</g, '\\u003c');
