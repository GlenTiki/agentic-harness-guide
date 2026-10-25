import fs from 'node:fs';

const file = process.argv[2] ?? 'src/styles/tokens.css';
const css = fs.readFileSync(file, 'utf8');
const AA_TEXT = 4.5;
const AA_UI = 3;

const blockOf = (selectorPattern) => {
  const match = css.match(new RegExp(`${selectorPattern}\\s*\\{([^}]*)\\}`));
  if (!match) throw new Error(`${file}: no block matching ${selectorPattern}`);
  return Object.fromEntries([...match[1].matchAll(/--ahg-([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;/g)].map((m) => [m[1], m[2]]));
};
const themes = {
  light: blockOf(String.raw`:root,\s*:root\[data-theme='light'\]`),
  dark: blockOf(String.raw`:root\[data-theme='dark'\]`),
};

const channel = (value) => {
  const c = value / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};
const luminance = (hex) => {
  const [r, g, b] = [1, 3, 5].map((i) => channel(parseInt(hex.slice(i, i + 2), 16)));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const ratio = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

const surfaces = ['bg', 'panel', 'code-bg', 'accent-soft'];
const callouts = ['agent', 'atwork', 'consistency', 'expert', 'newbie', 'whichapp', 'wrong', 'right'];
const textPairs = [
  ...surfaces.map((s) => ['text', s]),
  ...['bg', 'panel', 'code-bg'].map((s) => ['muted', s]),
  ...['bg', 'panel'].map((s) => ['accent', s]),
  ...['bg', 'panel', 'accent-soft'].map((s) => ['accent-strong', s]),
  ['accent-ink', 'accent'],
  ['accent', 'accent-soft'],
  ...callouts.flatMap((c) => [[c, `${c}-soft`], ['text', `${c}-soft`], ['muted', `${c}-soft`]]),
];
const uiPairs = [['accent', 'bg'], ['accent', 'panel'], ...callouts.map((c) => [c, `${c}-soft`])];

const failures = [];
let minimum = Infinity;
for (const [theme, tokens] of Object.entries(themes)) {
  const check = (pairs, floor, kind) => {
    for (const [fg, bg] of pairs) {
      if (!tokens[fg] || !tokens[bg]) {
        failures.push(`${theme}: token missing for ${fg} on ${bg}`);
        continue;
      }
      const value = ratio(tokens[fg], tokens[bg]);
      if (kind === 'text') minimum = Math.min(minimum, value);
      if (process.env.CONTRAST_VERBOSE) console.log(`${theme} ${kind} ${fg} on ${bg}: ${value.toFixed(2)}`);
      if (value < floor) failures.push(`${theme}: ${kind} ${fg} ${tokens[fg]} on ${bg} ${tokens[bg]} is ${value.toFixed(2)}:1, needs ${floor}:1`);
    }
  };
  check(textPairs, AA_TEXT, 'text');
  check(uiPairs, AA_UI, 'ui');
}

console.log(`${file}: ${textPairs.length * 2 + uiPairs.length * 2} pairs checked, lowest text ratio ${minimum.toFixed(2)}:1, ${failures.length} failures`);
for (const failure of failures) console.log(`  failure: ${failure}`);
process.exit(failures.length ? 1 : 0);
