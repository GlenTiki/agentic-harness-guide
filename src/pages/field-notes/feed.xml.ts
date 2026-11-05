import type { APIRoute } from 'astro';
import { notesFeed } from '../../../scripts/lib/notes.mjs';
import { publicNotes, notesSite, NOTES_BUILD_NOW } from '../../data/notes';

export const GET: APIRoute = async () => new Response(notesFeed(await publicNotes(), NOTES_BUILD_NOW, notesSite), { headers: { 'Content-Type': 'application/atom+xml; charset=utf-8' } });
