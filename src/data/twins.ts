import fs from 'node:fs';
import health from './health.json';
import limit from './health-limit.json';
import run from './runs/hook-sample-run.json';
import { artefacts } from './artefacts';
import { SITE_URL } from './site';

const frontMatter = (title: string, description: string, path: string, lastModified: string) =>
  `---\ntitle: ${JSON.stringify(title)}\ndescription: ${JSON.stringify(description)}\nurl: ${SITE_URL}${path}\nlast_modified: ${lastModified}\n---\n\n`;

const fenced = (text: string) => {
  const longest = Math.max(2, ...(text.match(/`+/g) ?? []).map((ticks) => ticks.length));
  const fence = '`'.repeat(longest + 1);
  return `${fence}text\n${text.trimEnd()}\n${fence}`;
};

const HEALTH_LABELS = { pass: 'Pass', fail: 'Fail', unknown: 'Unknown', stale: 'Stale' } as const;

export const healthRows = (nowMs: number) =>
  health.rows.map((row) => {
    const stale = row.observed !== null && (nowMs - Date.parse(row.observed)) / 3_600_000 > limit.maxAgeHours;
    return { ...row, state: (stale ? 'stale' : row.status) as keyof typeof HEALTH_LABELS };
  });

export const healthMarkdown = (nowMs = Date.now()) => {
  const rows = healthRows(nowMs);
  const sections = rows.map((row) =>
    [
      `## ${row.label}: ${HEALTH_LABELS[row.state]}`,
      row.covers,
      [`- Source: \`${row.source}\``, `- Observed (UTC): ${row.observed ?? 'Never observed'}`, `- Result: ${row.detail}`].join('\n'),
    ].join('\n\n'),
  );
  return (
    frontMatter(
      'Guide health',
      "The results of the guide's own checks, each with its source and the time it was observed.",
      'health/',
      health.generated_at,
    ) +
    [
      `Each row names its source and the time it was observed. A row with no source of measurement says Unknown. It never says Pass. Results were recorded at ${health.generated_at} on commit ${health.commit}. A result older than ${limit.maxAgeHours} hours shows as Stale.`,
      ...sections,
      "The page covers the checks named above. It does not cover wording quality, factual accuracy of tool settings, or real-device behaviour.",
    ].join('\n\n') +
    '\n'
  );
};

const PROVENANCE_TEXT: Record<string, string> = {
  'guide-owned': 'Made by the guide',
  'observed-prompt-not-kept': 'Observed, prompt not kept',
};

export const provenanceText = (provenance: string) => PROVENANCE_TEXT[provenance] ?? provenance;

export const showcaseMarkdown = () => {
  const items = artefacts();
  const sections = items.map((item) =>
    [
      `## ${item.title}`,
      `${item.kind}. ${provenanceText(item.provenance)}. Prepared ${item.preparedAt}. Explained on ${SITE_URL}${item.learnMore}`,
      item.summary,
      `Picture: ${item.imageAlt}`,
      fenced(item.text),
    ].join('\n\n'),
  );
  const rows = run.events.map(
    (event) => `| ${event.seq} | ${event.event_type} | ${event.tool_name} | ${event.offset_ms} | ${event.duration_ms} | ${event.exit_code} | ${event.decision} |`,
  );
  const latest = items.map((item) => item.preparedAt).sort().at(-1) ?? run.recorded_at;
  return (
    frontMatter(
      'Showcase',
      'Real outputs from the guide: a hook test run, eval results, a recorded reply and the prompt refiner, each with a text version.',
      'showcase/',
      latest,
    ) +
    [
      'Each item has a picture on the HTML page and the text version below. None holds personal or client data.',
      ...sections,
      `## A recorded hook run\n\n${run.title}. Recorded ${run.recorded_at} with ${run.environment}. ${run.fields}`,
      ['| Seq | Event | Tool | Offset ms | Duration ms | Exit code | Decision |', '| --- | --- | --- | --- | --- | --- | --- |', ...rows].join('\n'),
    ].join('\n\n') +
    '\n'
  );
};

export const kitDownloads = () =>
  fs
    .readFileSync('public/downloads/SHA256SUMS', 'utf8')
    .split('\n')
    .filter(Boolean)
    .map((line) => {
      const [digest, name] = line.split(/ {2}/);
      return { digest, name, id: name.replace(/\.zip$/, '') };
    });
