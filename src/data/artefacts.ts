import fs from 'node:fs';
import path from 'node:path';
import showcase from './showcase.json';

export type Artefact = (typeof showcase)[number] & { text: string };

export const artefacts = (): Artefact[] =>
  showcase.map((item) => ({ ...item, text: fs.readFileSync(path.join('src/data', item.textFile), 'utf8') }));

export const pngSize = (publicPath: string) => {
  const file = path.join('public', publicPath);
  if (!fs.existsSync(file)) return { width: 960, height: 540 };
  const png = fs.readFileSync(file);
  return { width: png.readUInt32BE(16), height: png.readUInt32BE(20) };
};
