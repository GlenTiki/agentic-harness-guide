# Insights report

Files read: 3. Lines read: 35. Duplicate messages skipped: 0. Unreadable lines: 0.

## Totals

| Signal | Count |
| --- | --- |
| interruption | 2 |
| failed tool call | 4 |
| refused permission | 2 |
| all friction | 8 |

## Sessions

| Session | Messages | Interruptions | Failed tool calls | Refusals | Friction |
| --- | --- | --- | --- | --- | --- |
| a1b2c3d4-0000-4000-8000-000000000001 | 14 | 1 | 3 | 1 | 5 |
| a1b2c3d4-0000-4000-8000-000000000002 | 7 | 1 | 1 | 1 | 3 |
| a1b2c3d4-0000-4000-8000-000000000003 | 6 | 0 | 0 | 0 | 0 |

## Top sessions by friction

### 1. a1b2c3d4-0000-4000-8000-000000000001 (friction 5)

- failed tool call: "Exit code 1 npm ERR! Missing script: "test""
- failed tool call: "Exit code 1 npm ERR! Missing script: "test""
- next user message after an interruption: "No. This repo uses make check for tests. Do not install anything."

### 2. a1b2c3d4-0000-4000-8000-000000000002 (friction 3)

- failed tool call: "Exit code 1 npm ERR! Missing script: "test""
- next user message after an interruption: "Again: tests run with make check, not npm."
- refused permission: "Claude requested permissions to use Bash, but you haven't granted it yet."

## Not counted

Corrections in the wording of a message are not counted. A rule that guesses them from words has not been checked against real examples.
