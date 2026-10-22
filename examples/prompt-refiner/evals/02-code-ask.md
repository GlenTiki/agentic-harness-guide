# Eval 2: a code ask

## Input

````text
Make this function better.

def total(items):
    t = 0
    for i in items:
        t = t + i[1] * i[2]
    return t
````

## A good refinement must

- Not rewrite the function.
- Keep the code in the Inputs section exactly as the user gave it.
- Ask what "better" means, with a recommended default such as readability without changing behaviour.
- State the assumption that behaviour must not change unless the user says otherwise.
- Ask for tests, or a check that old and new versions give the same results.
- Mark the language version and the meaning of each tuple position as [NEEDED] or as a stated assumption, and not as fact.
- Name a way to know it is done, for example "the same outputs on the same inputs".

## It fails if

- It returns improved code.
- It changes or "tidies" the pasted code in the prompt.
- It states what `i[1]` and `i[2]` mean as if it knew.
