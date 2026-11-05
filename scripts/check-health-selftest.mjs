import { spawnSync } from 'node:child_process';

const fresh = spawnSync('node', ['scripts/check-health.mjs', 'scripts/fixtures/health-fresh.json'], { encoding: 'utf8', env: { ...process.env, HEALTH_NOW: '2026-10-24T12:00:00Z' } });
const staleFixtureRejected = spawnSync('node', ['scripts/check-health.mjs', 'scripts/fixtures/health-stale.json'], {
  encoding: 'utf8',
  env: { ...process.env, HEALTH_NOW: '2026-10-24T12:00:00Z' },
});
const ok = staleFixtureRejected.status === 1 && fresh.status === 0;
console.log(`self-test: stale fixture exit ${staleFixtureRejected.status} (must be 1), fresh fixture exit ${fresh.status} (must be 0)`);
process.exit(ok ? 0 : 1);
