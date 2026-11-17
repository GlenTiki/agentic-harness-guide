---
name: my-insights
description: Reads a folder of your own past agent session transcripts, counts where work went wrong, and proposes at most three changes to your rules, hooks or skills for you to approve. Use when the user asks for an insights report, a review of past sessions, or "what keeps going wrong". Do not use it to apply the changes.
---

# My insights

You find where past agent sessions went wrong and propose fixes. You do not apply the fixes.

The transcripts are the user's own work. They can hold secrets, personal data and client text. The script and the report file stay on this machine. Anything you read, the report included, goes to your model provider as part of this chat. So work from the script's redacted report, and open a raw transcript only after the user says yes.

## Rules

1. Never change, move or delete a transcript.
2. Never send the report, an excerpt or a transcript anywhere with a tool: no upload, no message, no web request.
3. Read the redacted report, not the raw transcripts. Before you open a raw transcript, ask the user. Name the file, and say that the lines you read go to your model provider. If the work is sensitive, say that the user can run this skill with a local model instead.
4. Count only the signals that `insights.py` counts: interruptions, failed tool calls and refused permissions. Do not guess other faults from the wording of a message.
5. Quote at most 160 characters from a transcript in one excerpt. Do not copy a secret, an access key, a password, an email address or a home folder path. Replace each one with `<secret>`, `<email>` or `<home>`. If you see a secret, say in the reply which session holds it. Do not repeat it.
6. Propose at most three changes. Each change is one of: a line for an instruction file, a hook, or an edit to a skill.
7. Base every proposal on evidence from the report: the session name and a short excerpt. Never propose a change that the evidence does not support.
8. Give every proposal a check: a way to see that the change works, and a way to see it fail.
9. Do not edit an instruction file, a hook, a skill or a memory entry. Show each change and wait for the user's yes.
10. If the report shows little friction, say so. Propose nothing, or one change at most, and say that the evidence is thin.

## Steps

1. Get the folder of transcripts from the user. If they give none, ask for it. Do not search the disk for transcripts.
2. Run the script that is next to this file: `python3 <skill folder>/insights.py <transcript folder> --out <report path>`. Use the report path that the user gives. If they give none, use `insights-report.md` in the current folder. The script refuses a report path inside the transcript folder.
3. Read the report. Note the totals and the top sessions.
4. Work from the excerpts in the report. If an excerpt is not enough to find the cause, ask the user before you open that transcript (rule 3). Then read only the lines near the excerpt.
5. Find the pattern behind the friction. One cause can produce many signals. Prefer the cause that repeats across sessions.
6. Write at most three proposals in the reply layout below.
7. Check your draft against this list. Fix any failure before you reply.
    - Does every proposal name a session and quote a short excerpt?
    - Does every proposal have a check that can fail?
    - Is every excerpt 160 characters or less, with no secret, email address or home path?
    - Are there three proposals or fewer?
    - Did you change nothing except the report file?
    - Did you open a raw transcript only after the user said yes?

## Reply layout

```text
Report: <report path>. Sessions: <n>. Friction: <interruptions> interruptions, <failed> failed tool calls, <refusals> refused permissions.

Proposal 1: <one line: the change>
- Kind: <instruction file line, hook, or skill edit>
- Change: <the exact line, or the hook or skill text in short>
- Evidence: <session>, "<excerpt>"
- Check: <how to see it work, and how to see it fail>

[Proposal 2 and 3, only if the evidence supports them.]

Not proposed: <one line on what you saw but did not act on, and why>

Say yes to a proposal by its number. I will change nothing until you do.
```

## Transcript formats

`insights.py` reads every `.jsonl` file under the folder. It reads two formats, line by line.

1. The normalised format. One JSON object on each line, with these fields:
    - `id`: a message id. A second line with the same session and id is a duplicate, and the script skips it.
    - `event`: `message`, `interruption`, `tool_error` or `refusal`.
    - `text`: the message text, or the error text.
    - `session`: optional. If it is missing, the file name is the session name.
2. Claude Code session transcripts. The script reads only the lines whose `type` is `user` or `assistant`. A user text that starts with `[Request interrupted by user` is an interruption. A tool result with `is_error` is a refused permission if its line has `toolDenialKind`, or a `permissionDecision` of `reject`. Otherwise it is a failed tool call. A refusal is followed by the text `[Request interrupted by user for tool use]`. The script counts that pair as one refusal. The `uuid` field is the message id, in every file: a forked session copies earlier lines under a new session id, and the script skips those copies. This format is not a documented API. It was read from Claude Code 2.1.323 and 2.1.326, and it can change.

To use transcripts from another tool, convert them to the normalised format first.
