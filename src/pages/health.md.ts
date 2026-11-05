import type { APIRoute } from 'astro';
import { healthMarkdown } from '../data/twins';

export const GET: APIRoute = () => new Response(healthMarkdown(), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
