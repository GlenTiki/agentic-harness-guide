import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const INBOX_FILE = path.join(ROOT, 'data', 'feedback-inbox.jsonl');

const printEntry = (entry) => {
  const time = entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : 'Unknown';
  process.stdout.write(`\n------------------------------------------------------------\n`);
  process.stdout.write(`[NEW FEEDBACK] ${time} | Page: ${entry.page}\n`);
  if (entry.section) process.stdout.write(`Section: ${entry.section}\n`);
  if (entry.category) process.stdout.write(`Category: ${entry.category}\n`);
  if (entry.quote) process.stdout.write(`Quote: "${entry.quote}"\n`);
  process.stdout.write(`Feedback: ${entry.feedback}\n`);
  if (entry.device) process.stdout.write(`Device: ${entry.device}\n`);
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
  process.exit(0);
}

// Polling interval for robust file observation across OS/sandboxes
setInterval(() => {
  if (!fs.existsSync(INBOX_FILE)) return;
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
}, 2000);

process.stdout.write(`Feedback monitor running in background. Polling for new submissions...\n`);
