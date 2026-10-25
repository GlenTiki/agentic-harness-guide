import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const utcSeconds = (iso) => new Date(iso).toISOString().replace(/\.\d+Z$/, 'Z');

const gitDate = (extraArgs, file) => {
  try {
    const first = execFileSync('git', ['log', '--format=%cI', ...extraArgs, '--', file], { encoding: 'utf8' })
      .trim()
      .split('\n')[0];
    return first ? utcSeconds(first) : null;
  } catch {
    return null;
  }
};

export const lastCommitDate = (file) => gitDate(['-1'], file);
export const firstCommitDate = (file) => gitDate(['--reverse'], file);

const docsRoot = 'src/content/docs';
export const sourceFileFor = (id) =>
  [`${id}.md`, `${id}.mdx`, `${id}/index.md`, `${id}/index.mdx`]
    .map((name) => path.join(docsRoot, name))
    .find((candidate) => fs.existsSync(candidate)) ?? null;
