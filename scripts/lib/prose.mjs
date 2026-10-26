export const prose = (source) =>
  source
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/^```[\s\S]*?^```/gm, ' ')
    .replace(/^(import|export)\s.*$/gm, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\]\([^)]*\)/g, ']')
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, ' ');

export const WORD = /[\p{L}\p{N}][\p{L}\p{N}'’.,%/-]*/gu;

export const countWords = (source) => (prose(source).match(WORD) ?? []).length;
