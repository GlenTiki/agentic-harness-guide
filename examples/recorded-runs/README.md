# Recorded runs

These are raw replies kept unedited. Pages in the guide cite a folder here when they quote a result.

- Tool: Claude Code 2.1.308, run as `claude -p --tools "" --setting-sources "" --no-session-persistence`.
- Model: `claude-sonnet-5-5`.
- Date: 2026-10-22.

The runs used Claude Code 2.1.308, and the guide text was checked against Claude Code 2.1.309.

## Folders

- `l1/`: the level 1 bills list. `v0.txt` is the loose ask and `v4.txt` is the full ask. Replies are `v0_1.out` to `v0_5.out` and `v4_1.out` to `v4_5.out`. Five runs each.
- `l0/`: three runs each of five short prompts. `bills_*` is the level 0 bills total. `ban_*` is a document with a planted line. `syc_*` is a wrong total offered for agreement. `plug_*` and `plug2_*` are the month-end residual with and without a "must tie to zero" line. `cite_*` is a request for two studies with DOIs. The prompt text for the `l0/` prompts is not stored in this folder, so a reader cannot re-run them exactly.

## Limits

- Three or five runs show what happened on those runs. They do not give a rate.
- Other tools and other days can differ.
