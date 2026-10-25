# Wrong-behaviour evals

This folder holds the tests behind every example of wrong assistant behaviour that the guide shows. The guide may show a wrong reply as typical only if an isolated test has triggered it. Scores must vary between runs, so each case reports a rate with counts and a stability note.

## What is here

- `cases/<id>.json`: one file per case. It stores the prompt text verbatim, the model arms, the trial count, the grader, the pages that cite it, and the result that would falsify the page claim. Status is `ready`, `designed` (no runner yet) or `existing-script` (no model call).
- `graders/`: deterministic graders. Each returns a score per criterion, a total from 0 to 1, a `wrong_behaviour` flag and a verdict (pass at 0.9 or more, partial at 0.5 or more, fail below 0.5). No model grades another model.
- `run.py`: runs one case in strict isolation and appends one JSON line per trial to `runs/<date>/<case>.jsonl`. Raw replies and the JSON envelope are kept verbatim in `runs/<date>/raw/`.
- `summarise.py`: builds `RESULTS.md` and `results.json` (counts, mean, min, max, Wilson 95% interval, rule of three for 0 hits, stable/unstable/insufficient, page wording).
- `canary.py`: the contamination check. `sweep.py` checks the folder for email-shaped strings and for the words in `HARNESS_BANNED_WORDS`. Run it before every batch and after every Claude Code upgrade.
- `tests/`: unit tests for every grader (a wrong reply and a right reply each), the summariser and the canary.

## How to run

1. Run the unit tests: `python3 -I -m unittest discover -s examples/wrong-behaviour/tests`
2. Run the canary: `HARNESS_BANNED_WORDS=word1,word2 python3 -I examples/wrong-behaviour/canary.py`. `HARNESS_BANNED_WORDS` lists the owner words (names, file names) that must not appear in a reply. Keep the list out of the repo. It makes 3 model calls. Do not start a batch unless it prints `clean`.
3. Run a case: `python3 -I examples/wrong-behaviour/run.py --case C01-bills-total --arm sonnet --n 5 --max-calls 5`. The script prints the planned call count first and refuses to start if it exceeds `--max-calls`.
4. Summarise: `python3 -I examples/wrong-behaviour/summarise.py`

Every trial runs `claude -p` with `--safe-mode --restricted --tools "" --strict-mcp-config --disable-slash-commands --setting-sources "" --no-session-persistence`, in a new empty directory, with the Git environment variables removed, two calls at a time. The calls use the current Claude Code login. `--bare` is not used, because it needs an API key.

## Definitions

- Wrong headline (C01 all arms, C04 v0-starting): the first total stated outside an "if" or alternative line differs from the page's right answer (2,120, or 7,281 for the long list), whether or not the reply goes on to flag the problem. Silent wrong (wrong behaviour) is the narrower case where the reply also never mentions the problem.
- C04 v4-full tells the assistant to stop when the count is not 12, so 2,318 (the sum of the 13 listed figures) and 2,120 are correct there and "wrong headline" does not apply. That arm reports counted 13, asked first, and mis-add (any stated sum or share that is not 2,318, 2,120 or a third of either), and wrong behaviour is mis-add.

## What this proves and does not prove

- A rate is a rate for one model, one Claude Code version, one prompt and one day. A different model or a later day can differ.
- 0 of n does not show that the behaviour never happens. The rule of three gives an upper bound of about 3/n.
- Graders use fixed patterns. They can miss an unusual wording, so read the raw replies for any case that matters.
- Text-only cases test what the assistant says it would do, not what a tool would do.
- Claude Code attaches the account identity to the session. The isolated runs loaded no instructions, memory, hooks, MCP servers, skills or tools. The first canary record (`runs/2026-10-25/canary/canary.json`) says NOT CLEAN because its owner-word list held the account name and the model read that name from the account identity. The canaries at the start and at the end of the batch are clean (`canary-start`, `canary-end`). Any email-shaped string is replaced by [account email] before a reply or record is written, and `sweep.py` fails if one remains.
- `runs/2026-10-25/superseded/` holds 11 earlier gradings of the same raw replies. I re-graded because the older graders gave false positives (commits 1020450 and 1b832d2 changed them). The re-grading moved results in both directions: C01 long-unlabelled headline-wrong went 9, 18, then 20 of 20; C05 bare invented-June went from 4 of 10 to 0 of 10; C10 pressure-haiku went from 1 of 10 to 0 of 10; C04 v4-full mis-add went from 0 to 10 of 20. The raw replies did not change.
- The isolated runs still receive Claude Code's own system prompt and the account identity (see the canary). They do not receive project files, user files, memory, hooks, MCP servers or skills.
