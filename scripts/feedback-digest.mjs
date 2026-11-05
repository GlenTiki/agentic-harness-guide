import { execFileSync } from 'node:child_process';
import { FEEDBACK_REPO } from '../public/feedback-url.mjs';
import { buildDigest, formatDigest } from './lib/feedback-parse.mjs';

const FIELDS = 'number,title,body,createdAt,state,labels,url';

const withoutToken = (env) => Object.fromEntries(Object.entries(env).filter(([name]) => name !== 'GITHUB_TOKEN'));

const listIssues = (run = execFileSync) =>
  JSON.parse(
    run('gh', ['issue', 'list', '--repo', FEEDBACK_REPO, '--label', 'feedback', '--state', 'all', '--limit', '200', '--json', FIELDS], {
      encoding: 'utf8',
      env: withoutToken(process.env),
    }),
  );

const args = new Set(process.argv.slice(2));
const digest = buildDigest(listIssues(), { openOnly: args.has('--open') });
process.stdout.write(args.has('--json') ? `${JSON.stringify(digest, null, 2)}\n` : formatDigest(digest));
