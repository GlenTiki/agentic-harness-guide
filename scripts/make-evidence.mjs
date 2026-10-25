import fs from 'node:fs';
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

const rows = JSON.parse(fs.readFileSync(resultsFile, 'utf8'));
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

const templateOf = (r) => (r.wrong_k > 0 ? 'B' : r.headline_wrong_k > 0 ? 'C' : 'A');
const ident = (r) => `${r.models.join(', ')}, Claude Code ${r.claude_code.map(tool).join(', ')}, ${r.dates.join(', ')}`;
const wording = (r) => {
  const t = templateOf(r);
  if (t === 'B') {
    return `In ${r.wrong_k} of ${r.wrong_n} isolated trials (${ident(r)}) the wrong behaviour happened. That is a rate of ${pct(r.wrong_k / r.wrong_n)}, 95% interval ${pct(r.wilson95[0])} to ${pct(r.wilson95[1])}. Treat the rate as ${r.stability}.`;
  }
  if (t === 'C') {
    return `In ${r.headline_wrong_k} of ${r.wrong_n} isolated trials (${ident(r)}) the headline answer was wrong, and in each the reply also flagged the problem. The wrong behaviour without a flag happened in 0 of ${r.wrong_n}.`;
  }
  return `In ${r.wrong_n} isolated trials (${ident(r)}) the wrong behaviour did not happen. That does not show it never happens: the true rate could still be as high as about ${pct(r.rule_of_three_upper)} (rule of three).`;
};

const table = (caseRows) => {
  const showHeadline = caseRows.some((r) => r.headline_wrong_k > 0);
  const showDoi = caseRows.some((r) => r.unresolved_doi_k > 0);
  const head = ['Arm', 'Model', 'n', 'Pass / partial / fail', 'Mean (min to max)', 'Wrong k of n', '95% interval'];
  if (showHeadline) head.push('Headline wrong k of n');
  if (showDoi) head.push('Unresolved DOI k of n');
  head.push('Stability', 'Template');
  const lines = [`| ${head.join(' | ')} |`, `| ${head.map(() => '---').join(' | ')} |`];
  for (const r of caseRows) {
    const cells = [r.arm, r.models.join(', '), r.n, `${r.pass} / ${r.partial} / ${r.fail}`, `${score(r.mean)} (${score(r.min)} to ${score(r.max)})`, `${r.wrong_k} of ${r.wrong_n}`, `${pct(r.wilson95[0])} to ${pct(r.wilson95[1])}`];
    if (showHeadline) cells.push(`${r.headline_wrong_k} of ${r.n}`);
    if (showDoi) cells.push(`${r.unresolved_doi_k} of ${r.n}`);
    cells.push(r.stability, templateOf(r));
    lines.push(`| ${cells.join(' | ')} |`);
  }
  return lines.join('\n');
};

const caseSection = (id) => {
  const meta = cases.get(id);
  const caseRows = rows.filter((r) => r.case === id);
  return `### ${id}\n\n**${plainCanary(meta?.title ?? id)}**\n\nClaim tested: ${plainCanary(meta?.claim ?? 'not recorded')}\n\n${table(caseRows)}`;
};

const silent = rows.filter((r) => templateOf(r) === 'A');
const notRun = [...cases.values()].filter((c) => !caseIds.includes(c.id));

const generate = () =>
  `## What was tested

${trials} isolated trials ran across ${rows.length} arms of ${caseIds.length} cases on ${join(dates)}, with ${andJoin(models)} under Claude Code ${versions.map(tool).join(', ')}. Each trial sent one prompt to a new \`claude -p\` call in an empty folder, with no tools. A fixed script graded each reply. No model graded another model. Claude Code attaches the account identity to the session; the isolated runs loaded no instructions, memory, hooks, MCP servers, skills or tools (canary table in [runs/${dates[0]}/canary/](${GITHUB}/tree/main/examples/wrong-behaviour/runs/${dates[0]}/canary)).

The first canary record ([runs/${dates[0]}/canary/canary.json](${GITHUB}/blob/main/examples/wrong-behaviour/runs/${dates[0]}/canary/canary.json)) says NOT CLEAN. Its owner-word list held the account name, and the model read that name from the account identity that Claude Code attaches. No instruction file, memory, hook, MCP server, skill or tool was loaded. The canaries run at the start ([canary-start](${GITHUB}/blob/main/examples/wrong-behaviour/runs/${dates[0]}/canary-start/canary.json)) and at the end ([canary-end](${GITHUB}/blob/main/examples/wrong-behaviour/runs/${dates[0]}/canary-end/canary.json)) of the batch are clean.

Eleven earlier gradings of the same raw replies are kept in [runs/${dates[0]}/superseded/](${GITHUB}/tree/main/examples/wrong-behaviour/runs/${dates[0]}/superseded). I re-graded because the older graders gave false positives: they flagged a correct "Total (excluding June)" as an invented June, and a reply that refused to force a tie as a plug. For one arm (C04 v4-full) I also changed the grader so that it scores a stop-and-ask instruction. The re-grading moved results in both directions: the headline-wrong count for the long unlabelled list rose from 9 to 18 and then to 20 of 20, and the mis-add count for C04 v4-full rose from 0 to 10 of 20. The raw replies did not change.

A rate here is a rate for one model, one Claude Code version, one prompt and one day.

## How to read the tables

- **n**: graded trials in the arm.
- **Pass / partial / fail**: replies scoring 0.9 or more, 0.5 or more, and below 0.5.
- **Wrong k of n**: replies the grader flagged as the wrong behaviour the case looks for.
- **95% interval**: Wilson interval for that rate.
- **Headline wrong**: replies whose first stated answer was the wrong one, even if the reply also flagged it. Shown only for cases where it happened.
- **Unresolved DOI**: replies with at least one DOI that Crossref could not resolve. Shown only for cases where it happened.
- **Stability**: stable when scores differ by 0.25 or less and 90% of trials share a verdict; insufficient below 10 trials.
- **Template**: the wording template (A, B or C) in the next section that this row supports.

## Results by case

${caseIds.map(caseSection).join('\n\n')}

## What the guide may say

- **A.** The wrong behaviour did not happen in n isolated trials (model, tool version, date). That does not show it never happens: the true rate could still be as high as about 3 divided by n. The guide shows a Constructed example for this case and says so.
- **B.** The wrong behaviour happened in k of n isolated trials (model, tool version, date), a rate with a 95% interval. The guide gives the stability and shows an Observed example.
- **C.** The headline answer was wrong in h of n isolated trials and the reply flagged the problem each time. The guide says both facts and shows an Observed example.

## What did not trigger

Arms in template C also had 0 unflagged wrong replies, but they are not listed here because their headline answer was wrong. The bound is the rule of three: about 3 divided by n.

${silent.map((r) => `- ${r.case}, arm ${r.arm}: ${r.wrong_k} of ${r.wrong_n}, bound about ${pct(r.rule_of_three_upper)}.`).join('\n')}
${notRun.length ? `\nCases with no run:\n\n${notRun.map((c) => `- ${c.id}: ${plainCanary(c.title)} (status ${c.status}).`).join('\n')}\n` : ''}
## Where the data is

- [RESULTS.md](${GITHUB}/blob/main/examples/wrong-behaviour/RESULTS.md): the table this page is built from, with the exact wording per arm.
- [results.json](${GITHUB}/blob/main/examples/wrong-behaviour/results.json): the same numbers as data.
- [Runs folder](${GITHUB}/tree/main/examples/wrong-behaviour/runs): one record per trial and every raw reply, unedited.
- [Cases](${GITHUB}/tree/main/examples/wrong-behaviour/cases): the prompts, arms and what would falsify each claim.
- [Graders](${GITHUB}/tree/main/examples/wrong-behaviour/graders) and the [README](${GITHUB}/blob/main/examples/wrong-behaviour/README.md): how a reply is scored and what the tests do not prove.

## How to re-run

A run makes real model calls with your Claude Code login. Start with the unit tests and the canary. Do not start a batch unless the canary prints \`clean\`.

\`\`\`text
python3 -I -m unittest discover -s examples/wrong-behaviour/tests
HARNESS_BANNED_WORDS=word1,word2 python3 -I examples/wrong-behaviour/canary.py
python3 -I examples/wrong-behaviour/run.py --case C01-bills-total --arm sonnet --n 5 --max-calls 5
python3 -I examples/wrong-behaviour/summarise.py
npm run evidence
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
