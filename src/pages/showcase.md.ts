import type { APIRoute } from 'astro';
import { showcaseMarkdown } from '../data/twins';

export const GET: APIRoute = () => new Response(showcaseMarkdown(), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
