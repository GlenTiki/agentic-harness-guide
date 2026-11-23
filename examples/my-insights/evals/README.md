# How to run these evals

An eval is a small test for a prompt. You give the skill a fixed input and check the output against a list. These four evals need a terminal agent that can run Python 3, because the skill runs `insights.py`.

## Run one

1. Build the fixture folders: `python3 -I runs/2026-11-17/make-fixtures.py <empty folder>`. Every transcript in them is invented.
2. Open a new session of your agent inside one fixture folder, for example `<empty folder>/01`.
3. Give it the skill. The skill folder is `my-insights/` in that folder.
4. Open the eval file with the same number. Send the text under "Input" as your message.
5. Read the reply and `report/insights.md`. Compare them with the two lists in the eval file.
6. Check that no file outside `report/` changed, for example with `git status`.
7. Write down one of: pass, partial or fail. Add a note on which line failed.

`runs/2026-11-17/run.sh` does steps 2 to 6 with Claude Code, for one eval at a time.

## Read the results

- Pass: every "must" is met and no "fails if" is true.
- Partial: one or two "must" items are missed, with no "fails if" true.
- Fail: any "fails if" is true, or the reply holds no proposals in the layout.

## What these evals do not prove

- Eval 4 was held out: it was written before any run and never used to shape the skill.
- A pass shows that the reply and the report met a list. It does not show that a proposed change fixes anything. Only later sessions show that.
- Results depend on the tool and model you use. Record the tool, the model and the date.
- One run per eval is a smoke result, not a measurement.
