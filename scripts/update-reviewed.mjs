import fs from 'node:fs';

const file = 'src/data/review.json';
const lastReviewed = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
fs.writeFileSync(file, `${JSON.stringify({ lastReviewed }, null, 2)}\n`);
console.log(`${file}: lastReviewed ${lastReviewed}`);
