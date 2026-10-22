# Style guide and writer contract

This file is the contract for everyone who writes a page in `src/content/docs/`. It is not published on the site. Read it all before you write. If a rule here conflicts with your taste, the rule wins. If a rule is wrong, change this file in its own commit and tell the lead.

The site teaches one skill: how to design and run agent systems you can trust. A reader starts at "I have used a chatbot once" and finishes able to design a multi-part system for a job they have never seen. The nine journey levels (0 to 8) walk that path. The workflows shelf, the appendix and the reference shelf support it.

## 1. Scope and neutrality

1. The site is vendor-neutral and generic. Teach the idea first. Name a tool category before a product.
2. Use categories first: chat assistant, spreadsheet, notes app, team chat, calendar, email, design tool, ticket tracker, automation tool, code editor, terminal agent. After the category, give well-known examples so the reader can place it, for example "a spreadsheet such as Sheets or Excel".
3. Never name a private person, employer, client, product codename or local file path. The cast in section 5 is the only set of people.
4. Never invent statistics, quotes, benchmarks or study results. If a number matters, work it out on the page so the reader can check it, or leave it out.
5. A tool-specific fact (a setting name, a file name a product reads, a price, a limit) needs one of two treatments. Either verify it against the official documentation and add a verification line (section 9), or remove it and stay generic.

## 2. Voice

1. Simple English. Short sentences. Aim for under 20 words. One idea per sentence.
2. Active voice. Name who acts: "the assistant reads the file", not "the file is read".
3. Use the same word for the same thing every time. Take the word from the glossary. Do not rotate synonyms for style.
4. British English: organise, behaviour, colour, programme (for a plan of work, use "plan"), whilst is banned (use "while"), judgement, licence (noun).
5. No em dashes and no en dashes used as dashes. Use a full stop, a comma, a colon or brackets. A hyphen in a compound word is fine.
6. Never hard-wrap prose. One paragraph is one line in the file. The renderer wraps. Code blocks and tables keep their own shape.
7. Humour: dry and light. At most one joke per section (a section is one `##` heading). A joke must make a point. It never mocks the reader. It never relies on a meme, a trend or a name that will age. If a joke needs explaining, cut it. Clarity beats a joke every time.
8. Be concrete. Show the actual prompt and the actual output in a code block. Do not describe them. Example outputs are illustrative, so say "an example reply" and never imply a tool always replies this way.
9. Address the reader as "you". The assistant is always "the assistant". Do not call it "AI", "the bot", "the model" (unless the text is about the model itself), or give it a name.
10. Do not use these: "delve", "leverage", "unlock", "game-changer", "supercharge", "in today's world", "it is important to note". Do not write a closing paragraph that repeats the page.
11. Lists: use them for steps and for parallel items. Use a numbered list for steps in order. Use prose for reasoning.

## 3. Chapter anatomy

Every journey chapter uses exactly these `##` headings, in this order, with these exact names. Workflow and appendix pages use the same headings unless the lead says otherwise.

````mdx
---
title: "Level N: Title"
description: One sentence saying what the reader can do after this chapter.
---

## Scene

*Last time: two lines replaying the previous checkpoint.* (Level 0 has no callback.) Then two or three sentences of a relatable problem, lightly funny.

## The idea

One sentence that states the idea. Then a short plain explanation. At most three new ideas in the whole chapter. Link a glossary term on first use.

## Try it

A five-minute exercise. Any chat tool. Free. No setup. Show the exact prompt to paste and an example reply.

## Under the bonnet

What is really happening, for the curious. Still plain English. No tool-specific claims without a verification line.

## Expert corner

:::caution[Expert corner]
The trade-off, the failure mode or the edge case. Written for a principal engineer or a specialist. Be precise. No jokes needed.
:::

## Agent note

:::note[Agent note]
The rule, in imperative form, for an agent reading the page. No jokes. No metaphors. Short sentences. Say what to do, what not to do and how to check.
:::

## Mistakes people make

Three mistakes. For each: the mistake in bold, why it happens, the fix.

## Checkpoint

You can now:

- Three to five outcomes, each starting with a verb the reader can test.

**Self-test**

1. Question one.
2. Question two.
3. Question three.

<details>
<summary>Answers</summary>

1. Answer one.
2. Answer two.
3. Answer three.

</details>

## Bridge

One line on what breaks next. That break is why the next chapter exists.
````

Rules for the anatomy:

1. Use the exact heading text above. Other pages and the check scripts rely on it.
2. A chapter may have extra `###` headings inside a section. It may not add or reorder `##` headings.
3. "Try it" must work with any current chat tool for free. If a step needs a paid or installed tool, move it to "Expert corner" or mark it optional.
4. The Checkpoint answers go inside `<details>`. Leave a blank line after `<summary>` and before `</details>` so the list renders.
5. The quiz has exactly three questions. Each tests understanding, not recall of a term. At least one asks the reader to apply the idea to a new case.
6. The Bridge is one line.

## 4. Callouts

Use Starlight asides with these exact titles. Do not invent other titles. A reader skips what is not theirs, so each callout speaks to one reader.

| Syntax | Reader | Use it for |
| --- | --- | --- |
| `:::tip[New to this]` | A beginner | A plain restatement or a first step. Define any word they might not know. |
| `:::note[Want consistency]` | Someone who wants repeatable results | How to make the result the same every time, or what to write down once. |
| `:::caution[Expert corner]` | A principal or specialist | The trade-off, failure mode or edge case. |
| `:::note[Agent note]` | An agent reading the page | Imperative rules. No jokes, no metaphors. |

Close every aside with `:::` on its own line. Keep an aside under 120 words. Do not nest asides.

## 5. Cast and running thread

One task grows with the reader: the monthly money admin. The cast is fixed. Do not add names.

| Name | Role | Appears |
| --- | --- | --- |
| Sam | The reader's stand-in. Lives in a shared flat. Does the money admin. Later does the books for Mina on the side. | All levels |
| Priya | Sam's flatmate. Pays her share on time and wants to see the working. | Levels 0 to 4 |
| Tom | Sam's flatmate. Pays late and says "roughly" a lot. | Levels 0 to 4 |
| Mina | Owns a small shop that sells candles online and at markets. Sam's side-hustle client. | Levels 3 to 8 |

The assistant has no name. Other one-off scenes (a birthday dinner, a CV, a dentist booking, a house move, a wedding) may use unnamed people ("a friend", "the caterer").

The thread, by level:

| Level | The monthly money admin becomes |
| --- | --- |
| 0 | "Split the bills", asked in one line. The assistant answers, and the answer changes between tries. |
| 1 | The same ask refined in four passes: goal, constraints, examples, a check step. |
| 2 | The rules saved once as a standing brief (an instruction file). |
| 3 | The assistant reads the bank export and the shared sheet itself. |
| 4 | Payments need a human yes. A suspicious email is treated as data, not orders. |
| 5 | The total is checked against the bank by a separate reviewer. |
| 6 | Separate helpers read, calculate, check and report. |
| 7 | Mina's month-end run logs every step and caps its spend. |
| 8 | A new job is designed from a blank page, then compared with a worked answer. |

The pro thread is the same task seen by a finance team's month-end close or an engineering team's release. Use it only inside `Expert corner` asides, in one or two sentences.

### The recurring bug

In every level the assistant confidently adds February twice, so the yearly total is one month too high. It is the same slip at each level, and each level fixes more of it with that level's tool. By level 5 the reader should spot it before the text points at it.

| Level | What happens | Tool that deals with it |
| --- | --- | --- |
| 0 | Planted. The assistant totals twelve payments and lists February twice. It sounds sure. | None. The reader only sees it. |
| 1 | A constraint names it: "list each month once". It helps. It does not prove anything. | Constraints and a check step in the prompt |
| 2 | The rule "count each month once, and say how many months you counted" goes into the instruction file. | Instruction file |
| 3 | The assistant reads the bank export itself, so no hand-pasted duplicate rows enter. The slip can still appear in its own sums. | Tool access (read-only) |
| 4 | A draft payment carries the wrong total. The human yes at the checkpoint catches it. | Human checkpoint |
| 5 | Fixed properly. A test says "twelve distinct months, no repeats", and a separate reviewer runs it. | Definition of done, test, independent reviewer |
| 6 | A dedicated checker helper owns the months check. | Delegation, bounded brief |
| 7 | The audit log shows which step produced the duplicate. A rate check shows how often it happens. | Audit trail, reliability counting |
| 8 | The reader spots it in a design drill without a prompt, and places a check where it belongs. | Design method |

Never say a level "solves" the bug. Say what that level adds and what is left.

## 6. Links: one home per idea

1. Every core idea has exactly one home page. The home page states its purpose once. Other pages link to the home page and do not restate it.
2. Journey ideas have their home in the level that introduces them (see the map in `journey/index.mdx`). Reference-shelf pages are deep dives for those ideas. A deep dive may restate detail the journey omits, but not the purpose.
3. Link to a home page the first time the idea appears on a page. Later in the same page, use plain text.
4. Use relative links with a trailing slash, as the existing pages do. From a page at `/journey/<page>/`, `/workflows/<page>/` or `/appendix/<page>/`, a sibling in another section is `../../workflows/<page>/`. From a shelf page at `/shelf/<group>/<page>/`, a journey page is `../../../journey/<page>/`. The `npm run check:links` script catches mistakes.
5. Link text says where the link goes: "see [instruction files](../02-house-rules/)", never "click here".

## 7. Glossary on first use

1. The glossary lives at `src/content/docs/glossary.mdx`. Each entry has an anchor made from its heading: lowercase, spaces to hyphens, punctuation dropped.
2. The first time a term appears on a page, link it to its entry: `[context window](../../glossary/#context-window)`. Explain it in the sentence as well. A reader should not need to click.
3. After the first use on a page, write the term plain.
4. Do not use a term before the chapter that defines it, unless you link it and say "more on this in level N".
5. If you introduce a term the glossary lacks, add the entry in the same commit. Entries are alphabetical, with one beginner sentence and an optional "For experts" sentence.

Anchors that exist today: `agent`, `audit-log`, `connector-mcp`, `context-window`, `eval`, `hallucination`, `hook`, `instruction-file`, `ledger`, `memory`, `model`, `permission`, `prompt`, `prompt-injection`, `reviewer`, `sandbox`, `skill`, `spec`, `sub-agent`, `test`, `token`, `tool`. Check the file for additions.

## 8. Voice for the four reader types

1. A beginner must never stall. Define every new word where it appears. Give the exact words to type.
2. A reader who wants consistency needs a repeatable habit. Show what to write down once.
3. An expert must not wince. State trade-offs honestly. Do not oversimplify in the main text in a way that is false. Put the nuance in `Expert corner`.
4. An agent needs rules. The `Agent note` is short, imperative and testable.

## 9. Citing tool-specific facts

1. Prefer the generic form: "many chat tools let you save standing instructions in their settings".
2. If you must name a product setting, file name or limit, open the official documentation, confirm the fact, and add a line directly under the claim: `*Verified against the official docs on 2026-10-22: <page title and URL>.*` Use the real date you checked.
3. If you cannot verify it in this session, do not write it. Do not rely on memory.
4. Products change. Keep named examples to category illustrations. Never build a lesson that only works in one product.

## 10. Quality bar

Every chapter passes all four checks:

1. A reader with only the previous checkpoint can follow it.
2. No term is used before it is defined.
3. The Try it works with any current chat tool and costs nothing.
4. One expert would not wince, and one beginner would not stall.

## 11. Definition of done (per chapter)

Tick all of these before you hand a chapter back.

- [ ] The `##` headings match section 3 exactly, in order, and no `TODO(writer)` remains.
- [ ] `title` reads "Level N: Title" and `description` is one sentence.
- [ ] It opens with the two-line callback to the previous checkpoint (not Level 0).
- [ ] It adds at most three new ideas, each with one home on this page.
- [ ] Every new term is linked to the glossary on first use and has an entry.
- [ ] Try it shows the exact prompt and an example reply, needs no paid tool, and takes about five minutes.
- [ ] The running task and the February bug appear as section 5 says for this level.
- [ ] It has one `Expert corner` and one `Agent note` in the exact aside syntax. Beginner and consistency callouts appear where they help.
- [ ] There are exactly three mistakes, each with a fix.
- [ ] The checkpoint has a "You can now" list and three questions with answers inside `<details>`.
- [ ] The Bridge is one line and names what breaks next.
- [ ] No more than one joke per `##` section, each making a point.
- [ ] No em dashes, no hard-wrapped prose, British English, no invented statistics or quotes.
- [ ] No private name, employer, client, codename or local path.
- [ ] Any named tool fact has a verification line or was removed.
- [ ] `npm run build` has zero warnings and `npm run check:links` reports 0 problems.

## 12. Gates and checks

Run these from the repository root before every commit.

| Check | Command | Passes when |
| --- | --- | --- |
| Build | `npm run build` | Zero warnings |
| Links | `npm run check:links` | Reports 0 problems (run after a build) |
| Draft status | `npm run check:todos` | Lists remaining `TODO(writer)` markers. It exits non-zero while any remain. Completion means it reports none. It is not wired into CI as a blocking step yet. |
| Em dash | `grep -rnP '\x{2014}' src STYLE.md README.md` | Prints nothing |

Run npm with `nice -n 10`. Make atomic commits that each build. Never push. Never add a remote.

## 13. Reader routes (for the how-to-read page)

The how-to-read page offers these personas and routes. Keep it in step with this table.

| Persona | Route |
| --- | --- |
| Complete beginner | The journey, levels 0 to 8 in order |
| Used a chatbot, gets mixed results | Start at level 1 |
| Daily user who repeats themselves | Start at level 2 |
| Wants to connect tools safely | Levels 3 and 4, then the workflows |
| Engineer or team lead | Skim each Expert corner, then the reference shelf |
| An agent | Each Agent note, then the reference shelf baseline |
