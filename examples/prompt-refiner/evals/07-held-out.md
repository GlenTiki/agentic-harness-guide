# Eval 7: a request that mixes two jobs (held out)

This case was written after the skill was tuned. It was never used to change the skill. Use it to check that the tuning did not only fit the other six.

## Input

```text
Write a project update and tell me whether the project is late.
```

## A good refinement must

- Not write the update and not say whether the project is late.
- Ask for the project, its plan dates and its current status, each with a recommended default, or mark them as [NEEDED].
- Treat the update and the lateness judgement as two outputs, and say so in the assumptions or the output format.
- Mark every date, name and status as [NEEDED], not as fact.
- Ask no more than three questions, each with a recommended default.
- Use all seven sections.
- Include a definition of done the user could check, for example that the lateness answer names the dates it compares.

## It fails if

- It writes an update or declares the project late or on time.
- It invents a date, a project name or a status.
- It merges the two jobs into one vague output.
- It asks four or more questions, or a question with no default.
- It leaves out a section.
