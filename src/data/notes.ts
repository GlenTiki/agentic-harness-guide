import { getCollection, type CollectionEntry } from 'astro:content';
import { publishedNotes } from '../../scripts/lib/notes.mjs';
import { AUTHOR, AUTHOR_URL, OG_IMAGE, SITE_NAME, SITE_URL } from './site';
import { NOTES_BUILD_NOW } from './notes-clock';

export type Note = CollectionEntry<'notes'>;
export { NOTES_BUILD_NOW };
export const notesSite = { url: SITE_URL, name: SITE_NAME, author: AUTHOR, authorUrl: AUTHOR_URL, image: OG_IMAGE };
export const publicNotes = async (): Promise<Note[]> => publishedNotes(await getCollection('notes'), NOTES_BUILD_NOW);
