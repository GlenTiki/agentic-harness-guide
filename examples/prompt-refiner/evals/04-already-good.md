# Eval 4: an ask that is already good

## Input

````text
Goal: Turn my meeting notes into a short update for my team.
Context: The team could not attend. They know the project but not today's discussion.
Inputs: My notes, pasted below.
Constraints: No more than five bullets. Each action names one owner. Do not add anything that is not in the notes.
Output format: A bulleted list, then one line saying what is still undecided.
Definition of done: Every action in the notes appears once, with an owner, or is marked "owner unknown".
What to do if unsure: Ask me. Do not guess an owner.

[notes pasted here]
````

## A good refinement must

- Say plainly that the ask is already strong.
- Change very little. Wording changes are small and each is explained.
- Ask no questions, or at most one.
- Leave the sections, limits and voice as the user wrote them.
- In the diff, list what it left alone.

## It fails if

- It rewrites the whole prompt.
- It adds constraints the user did not imply.
- It invents the notes.
- It asks three questions to look useful.
