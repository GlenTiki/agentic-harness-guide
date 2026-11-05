import type { APIRoute } from 'astro';
import { notesMarkdown } from '../../scripts/lib/notes.mjs';
import { publicNotes, notesSite, NOTES_BUILD_NOW } from '../data/notes';

export const GET: APIRoute = async () => new Response(notesMarkdown(await publicNotes(), NOTES_BUILD_NOW, notesSite), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
