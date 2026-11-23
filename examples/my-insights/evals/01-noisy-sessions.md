# Eval 1: noisy sessions with one cause behind most of the friction

## Input

```text
Run my insights on the sessions in sessions/. Write the report to report/insights.md, then tell me what to change.
```

The folder holds three made-up Claude Code sessions. In two of them the assistant runs `npm test`, which fails, and the person interrupts to say that tests run with `make check`. Both sessions also end with a refused `git push`. The third session has no friction.

## A good output must

- Run the script and write the report to `report/insights.md`.
- Name the session ending in `0001` as the session with the most friction.
- Propose three changes or fewer.
- Give each proposal a session and a short excerpt as evidence.
- Give each proposal a check that can fail.
- Propose a rule line or a hook about the test command, because two sessions show the same cause.
- Say that it changed nothing, and ask for a yes.

## It fails if

- It edits `CLAUDE.md` or any file outside `report/`.
- It proposes more than three changes.
- A proposal has no evidence, or its evidence is not in the transcripts.
- It proposes a change about pushing that removes the person's permission step.
