import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const INBOX_FILE = path.join(ROOT, 'data', 'feedback-inbox.jsonl');
const REPO = 'GlenTiki/agentic-harness-guide';

const printEntry = (entry) => {
  const time = entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : 'Unknown';
  process.stdout.write(`\n------------------------------------------------------------\n`);
  process.stdout.write(`[NEW FEEDBACK] ${time} | Source: ${entry.id || 'direct'} | Page: ${entry.page}\n`);
  if (entry.section) process.stdout.write(`Section: ${entry.section}\n`);
  if (entry.category) process.stdout.write(`Category: ${entry.category}\n`);
  if (entry.quote) process.stdout.write(`Quote: "${entry.quote}"\n`);
  process.stdout.write(`Feedback: ${entry.feedback}\n`);
  if (entry.device) process.stdout.write(`Device: ${entry.device}\n`);
  if (entry.url) process.stdout.write(`URL: ${entry.url}\n`);
  process.stdout.write(`------------------------------------------------------------\n`);
};

const showCurrent = () => {
  if (!fs.existsSync(INBOX_FILE)) {
    process.stdout.write(`No feedback recorded yet in ${INBOX_FILE}\n`);
    return 0;
  }
  const lines = fs.readFileSync(INBOX_FILE, 'utf8').trim().split('\n').filter(Boolean);
  process.stdout.write(`Monitoring ${INBOX_FILE} (currently ${lines.length} items recorded)\n`);
  return lines.length;
};

let lastCount = showCurrent();
const seenIssues = new Set();

const extractField = (body, fieldName) => {
  if (!body) return '';
  const regex = new RegExp(`###\\s+${fieldName}\\s*\\n+([^#]+)`, 'i');
  const match = body.match(regex);
  return match ? match[1].trim() : '';
};

const checkGithubIssues = () => {
  execFile('gh', ['issue', 'list', '--repo', REPO, '--state', 'open', '--json', 'number,title,body,createdAt,url,labels'], (err, stdout) => {
    if (err || !stdout) return;
    try {
      const issues = JSON.parse(stdout);
      for (const issue of issues) {
        if (!seenIssues.has(issue.number)) {
          seenIssues.add(issue.number);
          const feedbackText = extractField(issue.body, 'What happened, and what did you expect?') || issue.body || issue.title;
          const entry = {
            id: `gh_${issue.number}`,
            timestamp: issue.createdAt,
            page: extractField(issue.body, 'Page') || 'GitHub Issue',
            section: extractField(issue.body, 'Section') || '',
            quote: extractField(issue.body, 'Text you selected') || '',
            category: issue.title,
            feedback: feedbackText,
            device: extractField(issue.body, 'Device') || 'Phone/Browser',
            url: issue.url,
          };
          printEntry(entry);
          // Also append to inbox file so local state stays consolidated
          fs.appendFileSync(INBOX_FILE, `${JSON.stringify(entry)}\n`, 'utf8');
        }
      }
    } catch {}
  });
};

if (process.argv.includes('--once')) {
  if (fs.existsSync(INBOX_FILE)) {
    const lines = fs.readFileSync(INBOX_FILE, 'utf8').trim().split('\n').filter(Boolean);
    for (const line of lines) {
      try {
        printEntry(JSON.parse(line));
      } catch {
        process.stdout.write(`Raw line: ${line}\n`);
      }
    }
  }
  checkGithubIssues();
  process.exit(0);
}

// Initial GitHub check
checkGithubIssues();

// Polling interval for local file and GitHub issues
setInterval(() => {
  if (fs.existsSync(INBOX_FILE)) {
    const lines = fs.readFileSync(INBOX_FILE, 'utf8').trim().split('\n').filter(Boolean);
    if (lines.length > lastCount) {
      const newItems = lines.slice(lastCount);
      for (const item of newItems) {
        try {
          printEntry(JSON.parse(item));
        } catch {
          process.stdout.write(`Raw line: ${item}\n`);
        }
      }
      lastCount = lines.length;
    }
  }
}, 2000);

// Poll GitHub issues every 10 seconds
setInterval(checkGithubIssues, 10000);

process.stdout.write(`Feedback monitor running in background. Polling local queue and GitHub issues...\n`);
