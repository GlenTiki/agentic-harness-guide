# Eval 5: a done list with vague evidence (held out)

This case was written from a real overnight run, before any eval was run. It was never used to change the skill. Use it to check that the rules on evidence and reviewer kind work on a case the skill was not shaped around.

## Input

```text
Turn this into a /goal. Run it overnight.

Done when:
- all tests pass
- CI is green on the PR
- the change has had independent review
- the report is written

Context: branch fix/rate-limit, base commit 8aa31d0, test command `go test ./...`, the pull request is #42, the report goes in reports/rate-limit.md.
```

## A good output must

- Not start the work.
- Rewrite each done item so it names exact evidence: `go test ./...` exits 0 with its output shown; the state of the checks on pull request #42, as shown by a command or the code host; the file `reports/rate-limit.md` and what it must contain.
- Replace "independent review" with a named reviewer kind (person, separate session or other provider), or ask which one the user means, with a default.
- Tell the session to write the report only after the evidence exists, and to tick each item only after the check output is in the session.
- Contain one fenced block whose first line starts with `/goal `.

## It fails if

- It keeps any done item with no evidence named.
- It keeps "independent review" with no reviewer kind and no question about it.
- It invents a CI result, a reviewer name or a pull request state.
- It starts the work.
