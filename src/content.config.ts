import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { notesSchema } from '../scripts/lib/notes.mjs';
import { NOTES_BUILD_NOW } from './data/notes-clock';
import { z } from 'astro/zod';
import { docsLoader, i18nLoader } from '@astrojs/starlight/loaders';
import { docsSchema, i18nSchema } from '@astrojs/starlight/schema';

export const pageStatuses = ['runs', 'built', 'design', 'mixed'] as const;

export const collections = {
  notes: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/notes' }),
    schema: notesSchema(z, NOTES_BUILD_NOW),
  }),
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({ extend: z.object({ status: z.enum(pageStatuses).optional() }) }),
  }),
  i18n: defineCollection({ loader: i18nLoader(), schema: i18nSchema() }),
};
