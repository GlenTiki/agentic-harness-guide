import fs from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';

const args = process.argv.slice(2);
const flag = (name) => args.includes(name);
const value = (name, fallback) => (args.includes(name) ? args[args.indexOf(name) + 1] : fallback);
const resultsFile = value('--results', 'examples/wrong-behaviour/results.json');
const pageFile = value('--page', 'src/content/docs/evidence/index.mdx');
const casesDir = 'examples/wrong-behaviour/cases';
const GITHUB = 'https://github.com/GlenTiki/agentic-harness-guide';
const BEGIN = '{/* BEGIN GENERATED: scripts/make-evidence.mjs. Do not edit by hand. */}';
const END = '{/* END GENERATED */}';

const snapshot = fs.readFileSync(resultsFile);
if (createHash('sha256').update(snapshot).digest('hex') !== '638bb051b71b6f5443ea6fa5278a689df44a58232ac24a96b12e21af5410c5d8') {
  console.error('This publisher accepts only the preserved historical aggregate. Changed or future runs need a separately reviewed report; the page was not changed.');
  process.exit(1);
}
const rows = JSON.parse(snapshot.toString('utf8'));
const cases = new Map(
  fs.readdirSync(casesDir).filter((f) => f.endsWith('.json')).sort().map((f) => {
    const data = JSON.parse(fs.readFileSync(path.join(casesDir, f), 'utf8'));
    return [data.id, data];
  }),
);

const pct = (x) => `${Math.round(100 * x)}%`;
const score = (x) => (Number.isInteger(x) ? x.toFixed(1) : String(x));
const join = (items) => [...new Set(items)].sort().join(', ');
const andJoin = (items) => [...new Set(items)].sort().join(' and ');
const plainCanary = (text) => text.replaceAll('BANANA', 'canary word');
const tool = (text) => text.replace(/ \(Claude Code\)$/, '');
const ofRows = (key) => rows.flatMap((r) => r[key]);
const caseIds = [...new Set(rows.map((r) => r.case))];
const trials = rows.reduce((sum, r) => sum + r.n, 0);
const dates = [...new Set(ofRows('dates'))].sort();
const versions = [...new Set(ofRows('claude_code'))].sort();
const models = [...new Set(ofRows('models'))].sort();

const templateOf = (r) => (r.wrong_n === 0 ? 'Pending' : r.wrong_k > 0 ? 'B' : r.headline_wrong_k > 0 ? 'C' : 'A');
const table = (caseRows) => {
  const showPending = caseRows.some((r) => r.pending > 0);
  const showHeadline = caseRows.some((r) => r.headline_wrong_k > 0);
  const showDoi = caseRows.some((r) => r.unresolved_doi_k > 0);
  const head = ['Arm', 'Model', 'n', 'Pass / partial / fail', 'Mean (min to max)', 'Wrong k of n', '95% interval'];
  if (showPending) head.push('Pending verification');
  if (showHeadline) head.push('Headline wrong k of n (legacy)');
  if (showDoi) head.push('Unresolved DOI k of n (legacy)');
  head.push('Stability', 'Template');
  const lines = [`| ${head.join(' | ')} |`, `| ${head.map(() => '---').join(' | ')} |`];
  for (const r of caseRows) {
    const cells = [r.arm === 'same-context' ? 'simulated same-context' : r.arm, r.models.join(', '), r.n, `${r.pass} / ${r.partial} / ${r.fail}`, `${score(r.mean)} (${score(r.min)} to ${score(r.max)})`, `${r.wrong_k} of ${r.wrong_n}`, r.wilson95 ? `${pct(r.wilson95[0])} to ${pct(r.wilson95[1])}` : 'Not measured'];
    if (showPending) cells.push(r.pending ?? 0);
    if (showHeadline) cells.push(r.headline_wrong_n > 0 ? `${r.headline_wrong_k} of ${r.headline_wrong_n}` : 'Not measured');
    if (showDoi) cells.push(`${r.unresolved_doi_k} of ${r.n}`);
    cells.push(r.stability, templateOf(r));
    lines.push(`| ${cells.join(' | ')} |`);
  }
  return lines.join('\n');
};

const SIMULATION_NOTE = "The same-context arm is simulated: the author's reasoning is pasted into a new prompt. It is not a second turn in the original chat.";

const caseSection = (id) => {
  const meta = cases.get(id);
  const caseRows = rows.filter((r) => r.case === id);
  const title = plainCanary(meta?.title ?? id).replace('same-context reviewer', 'simulated same-context reviewer');
  const note = caseRows.some((r) => r.arm === 'same-context') ? `\n\n${SIMULATION_NOTE}` : '';
  return `### ${id}\n\n**${title}**\n\nOriginal hypothesis: ${plainCanary(meta?.claim ?? 'not recorded')}\n\n${table(caseRows)}${note}`;
};

const silent = rows.filter((r) => templateOf(r) === 'A');
const notRun = [...cases.values()].filter((c) => !caseIds.includes(c.id));

const generate = () =>
  `## What was tested

${trials} isolated trials ran across ${rows.length} arms of ${caseIds.length} cases on ${join(dates)}, with ${andJoin(models)} under Claude Code ${versions.map(tool).join(', ')}. Each trial sent one prompt to a new \`claude -p\` call in an empty folder, with no tools. A fixed script graded each reply. No model graded another model. Claude Code attaches the account identity to the session; the isolated runs loaded no instructions, memory, hooks, MCP servers, skills or tools (canary table in [runs/${dates[0]}/canary/](${GITHUB}/tree/main/examples/wrong-behaviour/runs/${dates[0]}/canary)).

The first canary record ([runs/${dates[0]}/canary/canary.json](${GITHUB}/blob/main/examples/wrong-behaviour/runs/${dates[0]}/canary/canary.json)) says NOT CLEAN. Its owner-word list held the account name, and the model read that name from the account identity that Claude Code attaches. No instruction file, memory, hook, MCP server, skill or tool was loaded. The canaries run at the start ([canary-start](${GITHUB}/blob/main/examples/wrong-behaviour/runs/${dates[0]}/canary-start/canary.json)) and at the end ([canary-end](${GITHUB}/blob/main/examples/wrong-behaviour/runs/${dates[0]}/canary-end/canary.json)) of the batch are clean.

Eleven earlier gradings of the same raw replies are kept in [runs/${dates[0]}/superseded/](${GITHUB}/tree/main/examples/wrong-behaviour/runs/${dates[0]}/superseded). I re-graded because the older graders gave false positives: they flagged a correct "Total (excluding June)" as an invented June, and a reply that refused to force a tie as a plug. For one arm (C04 v4-full) I also changed the grader so that it scores a stop-and-ask instruction. The re-grading moved results in both directions: the headline-wrong count for the long unlabelled list rose from 9 to 18 and then to 20 of 20, and the mis-add count for C04 v4-full rose from 0 to 10 of 20. That re-grading did not change the reply text. Stored email-shaped strings were redacted; these files are not unedited originals.

A rate here describes a recorded grader outcome for one model, one Claude Code version, one prompt and one day. A precise interval cannot repair an invalid outcome definition.

## Legacy labels and corrected interpretation

**C01 bills, long-unlabelled.** 7,414 is the correct sum of all 40 supplied amounts. All 20 replies gave that sum and flagged the count mismatch with the stated 39 months. Some warned before the sum, including trials 01 and 10. The author inserted an extra 133, but the prompt did not identify it or require a stop. Equal amounts alone do not prove duplication. The reference total of 7,281 requires confirmation that one 133 should be removed. The original silent-error hypothesis was not observed. This is an exploratory count-mismatch and stop-policy lesson, not a 20-of-20 arithmetic failure or an observed duplicate-detection result.

The retained \`wrong_headline\`, pass/fail and score fields compare replies with that author reference. They are legacy labels, not newly measured outcomes. The original prompts, grades and aggregate JSON remain unchanged. A future stop-policy experiment needs an explicit stop rule and a separate result record.

**C02 DOI citations.** The legacy “Unresolved DOI” count records unsuccessful Crossref lookups in 16 of 20 as-is replies and 8 of 10 only-if-certain replies. The old resolver returned the same value for missing records, transport errors and invalid responses. The unknown service-error contribution means these are not proven fabrication counts. It also awarded metadata-match credit without comparing the claimed title or year. The legacy scores and “wrong” flag therefore cannot establish citation accuracy or whether the extra instruction helped.

The corrected resolver distinguishes found, not found and unknown, records a UTC check timestamp when explicitly called, and leaves title/year agreement unknown unless a separate comparison runs. No live lookup runs during the site build; no historical result was silently regraded. A Crossref 404 leaves DOI validity unknown and cannot alone set the wrong-citation flag: [Crossref documents that non-Crossref DOIs also return 404](https://github.com/CrossRef/rest-api-doc). New lookup records name the provider and limit their scope to that provider's metadata. An actual metadata comparison that finds a mismatch can set the flag.

## How to read the tables

- **n**: graded trials in the arm.
- **Pass / partial / fail**: legacy replies scoring 0.9 or more, 0.5 or more, and below 0.5. Read the C01 and C02 limitations above.
- **Wrong k of n**: replies the historical grader flagged under its original definition; this is not a general error rate.
- **95% interval**: Wilson interval for that rate.
- **Headline wrong (legacy)**: first totals different from the author reference. For C01 long-unlabelled, the supplied-row sum is correct; this label does not prove arithmetic failure.
- **Unresolved DOI (legacy)**: replies with an unsuccessful lookup. Missing records and service errors cannot be separated in these historical counts.
- **Stability**: stable when scores differ by 0.25 or less and 90% of trials share a verdict; insufficient below 10 trials.
- **Template**: the historical reporting category (A, B or C), retained for traceability.

## Results by case

${caseIds.map(caseSection).join('\n\n')}

## Historical reporting categories

- **A.** The grader recorded no wrong-behaviour flags. The rule-of-three bound describes that flag, subject to the grader's validity.
- **B.** The grader recorded a wrong-behaviour flag in k of n trials. C02 flags include the resolver defects described above.
- **C.** The grader recorded a headline differing from its reference while the reply also flagged a problem. C01 long-unlabelled uses an undisclosed author reference; this category does not establish arithmetic failure.

## What did not trigger

Arms in legacy category C also had 0 unflagged wrong replies; they remain in that historical category. The bound is the rule of three: about 3 divided by n. It describes the grader flag, not all possible failures.

${silent.map((r) => `- ${r.case}, arm ${r.arm}: ${r.wrong_k} of ${r.wrong_n}, bound about ${pct(r.rule_of_three_upper)}.`).join('\n')}
${notRun.length ? `\nCases with no run:\n\n${notRun.map((c) => `- ${c.id}: ${plainCanary(c.title)} (status ${c.status}).`).join('\n')}\n${notRun.some((c) => c.id === 'C12-retrieval') ? '\nC12-retrieval has stored outputs in examples/retrieval-eval/outputs. The setup pages use them. They are re-runnable results, not part of the graded counts above.\n' : ''}` : ''}
## Where the data is

- [RESULTS.md](${GITHUB}/blob/main/examples/wrong-behaviour/RESULTS.md): the historical table and original wording. Read the C01/C02 corrections above before reusing that wording.
- [results.json](${GITHUB}/blob/main/examples/wrong-behaviour/results.json): the historical aggregate numbers used to build this page.
- [Runs folder](${GITHUB}/tree/main/examples/wrong-behaviour/runs): one record per trial and stored replies; email-shaped strings were redacted before storage.
- [Cases](${GITHUB}/tree/main/examples/wrong-behaviour/cases): the prompts, arms and what would falsify each claim.
- [Graders](${GITHUB}/tree/main/examples/wrong-behaviour/graders) and the [README](${GITHUB}/blob/main/examples/wrong-behaviour/README.md): how a reply is scored and what the tests do not prove.

## How to re-run

A run makes real model calls with your Claude Code login. Start with the unit tests and the canary. Do not start a batch unless the canary prints \`clean\`. Replace \`new-run\` below with a fresh unused run label. The commands write a separate report for review, not an update to this historical page.

\`\`\`text
python3 -I -m unittest discover -s examples/wrong-behaviour/tests
HARNESS_BANNED_WORDS=word1,word2 python3 -I examples/wrong-behaviour/canary.py
python3 -I examples/wrong-behaviour/run.py --case C01-bills-total --arm sonnet --n 5 --max-calls 5 --date new-run
python3 -I examples/wrong-behaviour/summarise.py --runs examples/wrong-behaviour/runs/new-run --out /tmp/wrong-behaviour-report
\`\`\``;

const block = `${BEGIN}\n\n${generate()}\n\n${END}`;
const page = fs.readFileSync(pageFile, 'utf8');
const start = page.indexOf(BEGIN);
const end = page.indexOf(END);
if (start === -1 || end === -1 || end < start) {
  console.error(`${pageFile}: BEGIN or END marker not found`);
  process.exit(1);
}
const next = `${page.slice(0, start)}${block}${page.slice(end + END.length)}`;

if (flag('--check')) {
  const fresh = next === page;
  console.log(`${pageFile}: ${fresh ? 'up to date with' : 'OUT OF DATE against'} ${resultsFile}${fresh ? '' : ' (run npm run evidence)'}`);
  process.exit(fresh ? 0 : 1);
}
fs.writeFileSync(pageFile, next);
console.log(`${pageFile}: written from ${rows.length} rows, ${trials} trials`);
