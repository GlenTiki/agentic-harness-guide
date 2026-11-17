# Insights report

Files read: 2. Lines read: 14. Duplicate messages skipped: 0. Unreadable lines: 0.

## Totals

| Signal | Count |
| --- | --- |
| interruption | 1 |
| failed tool call | 1 |
| refused permission | 1 |
| all friction | 3 |

## Sessions

| Session | Messages | Interruptions | Failed tool calls | Refusals | Friction |
| --- | --- | --- | --- | --- | --- |
| e5f6a7b8-0000-4000-8000-000000000001 | 7 | 1 | 1 | 1 | 3 |
| e5f6a7b8-0000-4000-8000-000000000002 | 4 | 0 | 0 | 0 | 0 |

## Top sessions by friction

### 1. e5f6a7b8-0000-4000-8000-000000000001 (friction 3)

- failed tool call: "Exit code 1 AuthError: key rejected for STRIPE_KEY=<secret>"
- refused permission: "Claude requested permissions to use Bash, but you haven't granted it yet."
- next user message after an interruption: "Do not read .env or call the API with the key. Tell me which setting is wrong instead."

## Not counted

Corrections in the wording of a message are not counted. A rule that guesses them from words has not been checked against real examples.
