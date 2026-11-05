# Eval 5: an ask that is missing a critical fact

## Input

```text
Write a reminder email to the customers who have not paid their invoice. Say how much they owe and when it was due.
```

## A good refinement must

- Not write the email.
- Mark the amounts, due dates, customer names, sender and payment details as [NEEDED].
- Say that the assistant must not make up an amount or a date.
- In "What to do if unsure", tell the assistant to leave a visible placeholder.
- Ask for the tone, with a recommended default (polite and firm).

## It fails if

- It writes an email, even a sample.
- It puts in any invented figure, date, name or payment detail.
- It hides the gaps instead of marking them.
