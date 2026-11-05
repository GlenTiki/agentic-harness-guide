import fs from 'node:fs';
import path from 'node:path';

const DOCS_DIR = path.resolve('src/content/docs');
const TEXT_EXTS = new Set(['.md', '.mdx']);

const TROPES = [
  // 1. Negative Parallelism & Contrived Reframes
  {
    category: 'Negative Parallelism',
    id: 'not-x-but-y',
    regex: /\b(it's|it is) not [^.,;]+(,| --| -) it('s| is)\b/i,
    description: "Negative parallelism ('It is not X, it is Y')",
  },
  {
    category: 'Negative Parallelism',
    id: 'not-because-but',
    regex: /\bnot because [^.,;]+, but because\b/i,
    description: "Causal negative parallelism ('not because X, but because Y')",
  },
  {
    category: 'Negative Parallelism',
    id: 'not-x-just-z',
    regex: /\bnot [^.,;]+\.\s*not [^.,;]+\.\s*(just|only)\s+[^.,;]+\b/i,
    description: "Dramatic countdown negation ('Not X. Not Y. Just Z.')",
  },
  {
    category: 'Negative Parallelism',
    id: 'cross-sentence-reframe',
    regex: /\b(the question|the problem|the challenge|the secret) isn't [^.,;]+\.\s*(it's|it is|the \w+ is)\b/i,
    description: "Cross-sentence reframe negation",
  },
  {
    category: 'Negative Parallelism',
    id: 'negated-solution',
    regex: /\b(the solution|the answer) is not [^.,;]+(\.|\:)\s*(the \w+ is|it is|it comes from)\b/i,
    description: "Negated solution reframe ('The solution is not X. It is Y')",
  },

  // 2. Banned / Overused AI Buzzwords
  {
    category: 'AI Vocabulary',
    id: 'delve',
    regex: /\bdelv(e|es|ed|ing)\b/i,
    description: "AI tell word 'delve'",
  },
  {
    category: 'AI Vocabulary',
    id: 'leverage',
    regex: /\bleverag(e|es|ed|ing)\b/i,
    description: "Corporate buzzword 'leverage'",
  },
  {
    category: 'AI Vocabulary',
    id: 'utilize',
    regex: /\butiliz(e|es|ed|ing)\b/i,
    description: "Pompous vocabulary 'utilize'",
  },
  {
    category: 'AI Vocabulary',
    id: 'robust',
    regex: /\brobust\b/i,
    description: "Vague adjective 'robust'",
  },
  {
    category: 'AI Vocabulary',
    id: 'streamline',
    regex: /\bstreamlin(e|es|ed|ing)\b/i,
    description: "Corporate verb 'streamline'",
  },
  {
    category: 'AI Vocabulary',
    id: 'tapestry',
    regex: /\btapestr(y|ies)\b/i,
    description: "Grandiose noun 'tapestry'",
  },
  {
    category: 'AI Vocabulary',
    id: 'landscape',
    regex: /\b(modern|evolving|complex|ai|tech|threat|corporate|software)\s+landscape\b/i,
    description: "Grandiose domain metaphor 'landscape'",
  },
  {
    category: 'AI Vocabulary',
    id: 'supercharge',
    regex: /\bsupercharg(e|es|ed|ing)\b/i,
    description: "Hype buzzword 'supercharge'",
  },
  {
    category: 'AI Vocabulary',
    id: 'game-changer',
    regex: /\bgame[- ]changer\b/i,
    description: "Hype buzzword 'game-changer'",
  },
  {
    category: 'AI Vocabulary',
    id: 'paradigm-shift',
    regex: /\bparadigm[- ]shift\b/i,
    description: "Hype buzzword 'paradigm shift'",
  },
  {
    category: 'AI Vocabulary',
    id: 'revolutionize',
    regex: /\brevolutioni[sz](e|es|ed|ing)\b/i,
    description: "Hype verb 'revolutionize'",
  },
  {
    category: 'AI Vocabulary',
    id: 'seamlessly',
    regex: /\bseamless(ly)?\b/i,
    description: "Tech marketing cliché 'seamless(ly)'",
  },
  {
    category: 'AI Vocabulary',
    id: 'transformative',
    regex: /\b(deeply\s+)?transformativ(e|ely)\b/i,
    description: "Vague inflation 'transformative'",
  },

  // 3. Magic Adverbs & Stakes Inflation
  {
    category: 'Magic Adverbs',
    id: 'quietly-magic',
    regex: /\bquietly\s+(orchestrat|transform|power|revolut|chang|manag|suffocat|driv|redefin)/i,
    description: "Magic adverb 'quietly' inflating mundane tasks",
  },
  {
    category: 'Magic Adverbs',
    id: 'fundamentally',
    regex: /\bfundamentally\s+(transform|reshap|chang|alter|different|flawed)/i,
    description: "Stakes inflation with 'fundamentally'",
  },
  {
    category: 'Magic Adverbs',
    id: 'remarkably',
    regex: /\bremarkably\s+(well|simple|effective|fast|easy|capable)/i,
    description: "Synthetic praise adverb 'remarkably'",
  },

  // 4. Tone, Patronising Voice & False Suspense
  {
    category: 'Tone & Patronising',
    id: 'think-of-it-as',
    regex: /\bthink of it (as|like)\b/i,
    description: "Patronising analogy 'Think of it as...'",
  },
  {
    category: 'Tone & Patronising',
    id: 'pedagogical-breakdown',
    regex: /\blet's (break this down|unpack|dive in|explore this)\b/i,
    description: "Pedagogical voice 'Let's break this down / unpack'",
  },
  {
    category: 'Tone & Patronising',
    id: 'false-suspense',
    regex: /\bhere's (the kicker|the thing|where it gets interesting|what most people miss|the deal)\b/i,
    description: "False suspense transition 'Here's the kicker / thing'",
  },
  {
    category: 'Tone & Patronising',
    id: 'rhetorical-q-and-a',
    regex: /\b(the result\?|the worst part\?|the scary part\?|the catch\?|why\?)\s+[A-Z]/,
    description: "Self-posed rhetorical question immediately answered",
  },
  {
    category: 'Tone & Patronising',
    id: 'the-truth-is-simple',
    regex: /\b(the truth is simple|the reality is simple|history is unambiguous)\b/i,
    description: "Asserting simplicity instead of demonstrating it",
  },

  // 5. Pompous Copula Dodges & Superficial Analysis
  {
    category: 'Pompous Construction',
    id: 'serves-as',
    regex: /\b(serves as|stands as|marks a pivotal)\b/i,
    description: "Pompous copula dodge 'serves as / stands as'",
  },
  {
    category: 'Pompous Construction',
    id: 'superficial-participle',
    regex: /,\s+(highlighting|underscoring|accentuating)\s+the\s+(importance|need|critical|enduring)\b/i,
    description: "Superficial participle tack-on",
  },
  {
    category: 'Pompous Construction',
    id: 'false-range',
    regex: /\bfrom [^.,;\n]+ to [^.,;\n]+ to [^.,;\n]+\b/i,
    description: "False unscaled range ('from X to Y to Z')",
  },

  // 6. Filler Transitions & Formulaic Endings
  {
    category: 'Filler Transitions',
    id: 'worth-noting',
    regex: /\b(it's worth noting|it is worth noting|it bears mentioning|it is notable that)\b/i,
    description: "Filler transition 'It is worth noting'",
  },
  {
    category: 'Filler Transitions',
    id: 'importantly',
    regex: /^(importantly|interestingly|notably),/i,
    description: "Filler transition 'Importantly / Interestingly'",
  },
  {
    category: 'Signposted Conclusions',
    id: 'signposted-conclusion',
    regex: /\b(in conclusion,|to sum up,|in summary,)\b/i,
    description: "Signposted conclusion 'In conclusion / To sum up'",
  },
  {
    category: 'Formulaic Acknowledgment',
    id: 'despite-challenges',
    regex: /\bdespite (its|these|their) challenges\b/i,
    description: "Formulaic dismissal 'Despite its challenges...'",
  },
];

const findings = [];
let totalFiles = 0;
const filesScanned = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath);
    } else if (TEXT_EXTS.has(path.extname(entry.name))) {
      totalFiles++;
      checkFile(fullPath);
    }
  }
}

function checkFile(fullPath) {
  const relPath = path.relative(DOCS_DIR, fullPath);
  filesScanned.push(relPath);
  const content = fs.readFileSync(fullPath, 'utf8');
  const lines = content.split('\n');

  let inCodeBlock = false;
  let boldFirstCount = 0;
  let consecutiveListCount = 0;

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    const trimmed = line.trim();

    if (trimmed.startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      return;
    }
    if (inCodeBlock) return;

    // Check bold-first list density
    if (/^(\d+\.|\-|\*)\s+\*\*[^*]+\*\*:/.test(trimmed)) {
      boldFirstCount++;
      consecutiveListCount++;
    } else if (trimmed.startsWith('-') || trimmed.startsWith('*') || /^\d+\./.test(trimmed)) {
      consecutiveListCount++;
    } else if (trimmed === '') {
      // blank line in list
    } else {
      consecutiveListCount = 0;
    }

    // Check tropes
    for (const trope of TROPES) {
      const match = line.match(trope.regex);
      if (match) {
        // Exclude legitimate numeric progressions ("from 9 to 18 and then to 20")
        if (trope.id === 'false-range' && /\bfrom \d+ to \d+/.test(line)) continue;
        // Exclude legitimate workflow start-to-finish descriptions
        if (trope.id === 'false-range' && line.includes('proving sales to the bank to')) continue;
        if (relPath.includes('glossary') && trope.id === 'serves-as') continue;

        findings.push({
          file: relPath,
          line: lineNum,
          match: match[0],
          trope: trope.description,
          category: trope.category,
          context: trimmed,
        });
      }
    }
  });

  if (boldFirstCount >= 5 && boldFirstCount === consecutiveListCount && consecutiveListCount >= 5) {
    findings.push({
      file: relPath,
      line: 1,
      match: `${boldFirstCount} bold-first bullets`,
      trope: "Excessive bold-first listicle formatting (5+ items starting with '**Term**: ')",
      category: 'Formatting Tells',
      context: `Found ${boldFirstCount} consecutive bold-first items`,
    });
  }
}

walk(DOCS_DIR);

if (findings.length > 0) {
  console.error(`\nAnti-Slop Audit failed with ${findings.length} finding(s):`);
  for (const f of findings) {
    console.error(`  - ${f.file}:${f.line} [${f.category}] ${f.trope}: "${f.match}"`);
    console.error(`    Context: ${f.context}`);
  }
  process.exit(1);
} else {
  console.log(`Anti-Slop Audit: ${totalFiles} markdown pages checked across ${TROPES.length} trope rules. 0 slop findings.`);
  process.exit(0);
}
