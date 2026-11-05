import type { APIRoute, GetStaticPaths } from 'astro';
import { noteMarkdown } from '../../../scripts/lib/notes.mjs';
import { publicNotes, notesSite, type Note } from '../../data/notes';

export const getStaticPaths: GetStaticPaths = async () => (await publicNotes()).map(note => ({ params: { id: note.id }, props: { note } }));
export const GET: APIRoute = ({ props }) => new Response(noteMarkdown(props.note as Note, notesSite), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
