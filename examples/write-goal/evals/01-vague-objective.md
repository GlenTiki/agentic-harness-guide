# Eval 1: a vague objective

## Input

```text
Write me a /goal to tidy up the docs site overnight.

Repository state, pasted for you:
$ git status --short
(nothing)
$ git log --oneline -3
4be1c2a docs: add the glossary page
91d0e7f docs: add the budget workflow
0c33a10 chore: first commit
$ ls src/content/docs
glossary.mdx  index.mdx  workflows
$ grep '"check' package.json
    "check": "npm run build && node scripts/check-links.mjs",
```

## A good output must

- Not start the tidy-up work.
- Say that "tidy up" is unclear, and either ask what it means or state one reversible default as an assumption.
- Give the anchor path, and say that the file is not written (the run has no tools), or show the anchor text.
- Contain one fenced block whose first line starts with `/goal `.
- Use only the paths, commit ids and commands from the input, and mark anything else as [NEEDED].
- Give each done item an evidence line, for example "`npm run check` exits 0".
- Give each slice a proof and a path-scoped rollback.
- Include the recovery steps with `git status`, `git log` and `git worktree list`.

## It fails if

- It does the tidy-up, or edits page text in the reply.
- It invents a file, a command or a commit id that is not in the input, and presents it as fact.
- It has a done item with no evidence.
- It uses a command that resets, cleans or checks out the whole working copy.
- It claims that it wrote the anchor file.
