import fs from 'node:fs';

const file = process.argv[2] ?? 'src/data/health.json';
const { maxAgeHours } = JSON.parse(fs.readFileSync('src/data/health-limit.json', 'utf8'));
const nowMs = process.env.HEALTH_NOW ? Date.parse(process.env.HEALTH_NOW) : Date.now();
const UTC_SECONDS = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;
const STATUSES = ['pass', 'fail', 'unknown'];
const problems = [];

const health = JSON.parse(fs.readFileSync(file, 'utf8'));
const checkTime = (label, value) => {
  if (!UTC_SECONDS.test(value ?? '')) return problems.push(`${label}: ${value} is not a UTC time with seconds and Z`);
  const ageHours = (nowMs - Date.parse(value)) / 3_600_000;
  if (ageHours > maxAgeHours) problems.push(`${label}: observed ${value}, ${Math.round(ageHours)} hours ago, limit is ${maxAgeHours}`);
};

checkTime('generated_at', health.generated_at);
if (!Array.isArray(health.rows) || health.rows.length === 0) problems.push('no rows');
for (const row of health.rows ?? []) {
  if (!STATUSES.includes(row.status)) problems.push(`${row.id}: status ${row.status} is not one of ${STATUSES}`);
  if (!row.source) problems.push(`${row.id}: no source`);
  if (row.status === 'unknown') {
    if (row.observed !== null) problems.push(`${row.id}: an unknown row must have no observation time`);
  } else checkTime(`${row.id}.observed`, row.observed);
}

console.log(`${file}: ${health.rows?.length ?? 0} rows, limit ${maxAgeHours} hours, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
