# How to run these evals by hand

An eval is a small test for a prompt. You give the skill a fixed input and check the output against a list. These five tests need no code and no paid tool. Any chat assistant that can follow a long instruction will do.

## Run one

1. Open a new chat. Use a new chat each time, so earlier answers cannot leak in.
2. Paste the whole of `../SKILL.md`. Add: "Use this as your instructions for this chat." If your tool supports skills, install the skill there instead.
3. Open one eval file. Copy the text under "Input" into the chat as your message.
4. Read the reply. Compare it with the two lists in the eval file.
5. Write down one of: pass, partial or fail. Add a note on which line failed.

## Read the results

- Pass: every "must" is met and no "fails if" is true.
- Partial: one or two "must" items are missed, with no "fails if" true.
- Fail: any "fails if" is true, or the reply holds no goal.

The skill expects tools to read the repository and write the anchor. A chat with no tools cannot write the anchor file. The skill then should show the anchor text in the reply and say that the file is not written. A reply that claims it wrote the file, with no tools, fails eval 1. In the recorded runs with no tools, most replies held no goal at all.

## What these evals do not prove

- Four cases were in view while the skill was written. The fifth, `05-vague-evidence.md`, was held out.
- A pass shows that the goal text met a list. It does not show that a long session run from that goal finishes, recovers or stops in the right place. Only a real run shows that.
- Results depend on the tool and model you use. Record the tool, the model and the date.
- The `runs/2026-11-17-tools/` folder holds the main runs: one throwaway git repository per eval, built by `make-fixtures.sh`, with read-only tools and writes allowed only under `goals/`. It keeps every reply, transcript and anchor, with local paths redacted, and a graded `RESULTS.md`. The input there drops the pasted repository state, because the assistant reads the real repository.
- The `runs/2026-11-17/` folder holds an earlier round with no tools. Most of those replies held no goal. It is kept as a finding: the skill needs tools.
- One run per eval is a smoke result, not a measurement.
