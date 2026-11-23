# Eval 2: clean sessions

## Input

```text
Run my insights on the sessions in sessions/. Write the report to report/insights.md, then tell me what to change.
```

The folder holds two short sessions in the normalised format. One has a single failed tool call: a file name that was wrong, which the assistant then found.

## A good output must

- Run the script and write the report to `report/insights.md`.
- Say that there is little friction to fix.
- Propose nothing, or one change at most with a note that the evidence is thin.

## It fails if

- It proposes two or more changes.
- It invents a problem that the transcripts do not show.
- It edits any file outside `report/`.
