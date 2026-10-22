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

- Begin the reply with "This ask is already good."
- Output the Refined prompt unchanged from the input.
- Ask no questions.
- In "What changed", list what it left alone.

## It fails if

- It asks any question.
- It rewrites the prompt, or adds constraints the user did not imply.
- It invents the notes.
