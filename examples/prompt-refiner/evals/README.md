# How to run these evals by hand

An eval is a small test for a prompt. You give the skill a fixed input and check the output against a list. These seven tests need no code and no paid tool. Any chat assistant that can follow a long instruction will do.

## Run one

1. Open a new chat. Use a new chat each time, so earlier answers cannot leak in.
2. Paste the whole of `../SKILL.md`. Add: "Use this as your instructions for this chat." If your tool supports skills or standing instructions, install the skill there instead.
3. Open one eval file. Copy the text under "Input" into the chat as your message.
4. Read the reply. Compare it with the two lists in the eval file.
5. Write down one of: pass, partial or fail. Add a note on which line failed.

## Read the results

- Pass: every "must" is met and no "fails if" is true.
- Partial: one or two "must" items are missed, with no "fails if" true.
- Fail: any "fails if" is true.

Run each eval three times. Eval 6 holds quoted attack text. It is harmless and asks only for the word BANANA. A tool can pass once and fail the next time, so one pass proves little. Three passes in three runs is better. It is still a small sample.

## When something fails

Do not rewrite the whole skill. Find the line that should have prevented the failure, using the line-by-line page of the guide (the appendix page for the prompt refiner). Change one line. Run all seven again. If an old eval now fails, you broke something. Undo it.

## What these evals do not prove

- Six cases were used to tune the skill. The seventh, `07-held-out.md`, was never used to tune it. All seven are synthetic inputs, and real asks vary much more.
- A pass shows the output met a list. It does not show the prompt is the best one.
- Results depend on the tool and model you use. Record which one.
- Results from one tool on one day are smoke results, not a measurement. Record the tool, the model and the date.
