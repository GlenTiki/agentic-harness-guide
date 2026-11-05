import fs from 'node:fs';
import path from 'node:path';

const ROOT_DIR = process.cwd();
const TARGET_DIRS = ['src', 'examples', 'fixtures', 'scripts', 'public'];
const TEXT_EXTS = new Set(['.md', '.mdx', '.astro', '.js', '.mjs', '.ts', '.json', '.html', '.css', '.txt']);

const BANNED_METAPHORS = [
  /\bsupercharge\b/i,
  /\bdelve\b/i,
  /\bgame-changer\b/i,
  /\bsynergy\b/i,
  /\bparadigm shift\b/i,
  /\brecipe for (success|failure|disaster)\b/i,
];

const SECRET_PATTERNS = [
  /AKIA[0-9A-Z]{16}/,
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
  /ghp_[0-9a-zA-Z]{36}/,
  /xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}/,
];

let totalFilesChecked = 0;
const errors = [];

function scanDir(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = path.relative(ROOT_DIR, fullPath);

    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist') continue;
      scanDir(fullPath);
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name);
      if (!TEXT_EXTS.has(ext)) continue;
      checkFile(fullPath, relPath);
    }
  }
}

function checkFile(fullPath, relPath) {
  totalFilesChecked++;
  const content = fs.readFileSync(fullPath, 'utf8');
  const lines = content.split('\n');

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;

    // 1. Dash check: zero em dashes and zero en dashes in authored source files
    // (Exempt raw immutable model run logs in examples/wrong-behaviour/runs/)
    if (!relPath.startsWith('examples/wrong-behaviour/runs/')) {
      if (line.includes('\u2014')) {
        errors.push(`${relPath}:${lineNum} contains forbidden em dash (\\u2014). Use comma, colon, brackets, or full stop.`);
      }
      if (line.includes('\u2013')) {
        errors.push(`${relPath}:${lineNum} contains forbidden en dash (\\u2013). Use hyphen or rewrite.`);
      }
    }

    // 2. Portable paths check: no /Users/ in src/ (except explicit test comments/fixtures)
    if (relPath.startsWith('src/') && line.includes('/Users/')) {
      errors.push(`${relPath}:${lineNum} contains non-portable host path /Users/`);
    }

    // 3. Banned buzzwords check (only in user-facing src/content/docs/)
    if (relPath.startsWith('src/content/docs/')) {
      for (const pattern of BANNED_METAPHORS) {
        if (pattern.test(line)) {
          errors.push(`${relPath}:${lineNum} contains banned word matching ${pattern}`);
        }
      }
    }

    // 4. Secret / Sentinel scan
    for (const secretPat of SECRET_PATTERNS) {
      if (secretPat.test(line)) {
        errors.push(`${relPath}:${lineNum} contains potential live secret matching ${secretPat}`);
      }
    }
  });
}

for (const dir of TARGET_DIRS) {
  scanDir(path.join(ROOT_DIR, dir));
}

if (errors.length > 0) {
  console.error(`\nMako Standards Audit failed with ${errors.length} error(s):`);
  for (const err of errors) {
    console.error(`  - ${err}`);
  }
  process.exit(1);
} else {
  console.log(`Mako Standards Audit: ${totalFilesChecked} files checked across ${TARGET_DIRS.join(', ')}. 0 errors found.`);
}
