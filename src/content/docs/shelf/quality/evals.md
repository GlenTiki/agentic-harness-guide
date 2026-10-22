---
title: Evals for LLM-driven steps
description: Test every step that a model decides, using real output as fixtures and a rubric you do not move.
---

*Deep dive for [level 5: Check the work](../../../journey/05-check-the-work/).*

**Recommendation:** give every step where a model makes a decision its own eval. Build the fixtures from real model output. Before you trust a check, make it fail on purpose. Score new runs against the old rubric.

## Why it matters

Unit tests cover code that returns the same answer each time. A model step varies from run to run, so a single passing run proves little. A step with no eval is a step you cannot change safely, because you cannot tell whether a change helped.

## What to enable

**1. One eval per decision point.** List every place a model chooses something: a router picks a tool, a classifier picks a label, a reviewer picks a verdict, a parser reads model text. Give each a small set of cases with expected outcomes. A stub that returns a canned answer tests your wiring and not the model, so do not count it as an eval.

**2. Use real output as fixtures.** If your code parses model output, capture actual replies and test against those. Hand-written examples are tidier than real replies and hide the quirks that break parsers, such as extra prose, code fences and missing fields.

**3. Repeat runs.** Run each case several times. Report the pass count out of the total. A step that passes two of three runs is not reliable, and a single run would not show that.

**4. Prove the check can go red.** Before you rely on a green result, change the input or the code so that it must fail, and confirm it does. A grader with a typo in its pattern reports "no failures" for everything. Include a known-positive control in each run.

**5. Hold the rubric still.** When you change a prompt or a model, score the new output with the old rubric and the old cases. If you change the rubric at the same time, you cannot attribute the difference. Change one thing, then re-baseline deliberately.

**6. Keep graders deterministic where you can.** Prefer an executable check, such as "does this output parse" or "does this command exit 0", over another model's opinion. When you must use a model as a grader, give it a narrow question and spot-check its grades by hand.

**7. Record the baseline.** Store the cases, the raw outputs and the scores. A later run can then be compared and replayed without calling the model again.

**8. Pilot before scale.** On a long run, try five samples first. Dump the parsed output. Confirm that nothing is filtered by a hard-coded list and no placeholder is unresolved. Then run everything.

## Failure modes it prevents

- A prompt change quietly lowers quality and nobody notices.
- A parser works on tidy fixtures and fails on real replies.
- A green dashboard hides a grader that never fails.
- A before/after comparison is meaningless because the rubric moved.

## Start here

Choose the one model-driven step you worry about most. Collect ten real inputs, write the expected outcome for each, and run them three times. That table is your first baseline.
