---
title: Capability gating
description: Give each power its own switch, default it to off, and gate every path that leaves your machine.
---

**Recommendation:** model every power the agent can use as a named capability with its own on/off switch in one registry file. Default new capabilities to off. Require explicit consent per surface, and run redaction before anything leaves your machine.

## Why it matters

Permission rules answer "may this tool call run?". Capabilities answer a coarser question: "is the agent allowed to do this kind of thing at all?" Reading the calendar, sending email and calling a paid API are different risks. When they share one switch, enabling one enables all.

## What to enable

**1. A registry.** One declarative file lists each capability, its state and a reason. A reviewer can read it in a minute:

```yaml
capabilities:
  calendar.read:   { status: enabled,  reason: "Daily planning" }
  calendar.write:  { status: disabled, reason: "No approved use yet" }
  email.send:      { status: disabled, reason: "Always drafted, never sent" }
  web.fetch:       { status: enabled,  reason: "Docs lookup", domains: ["docs.example.com"] }
```

**2. Fail closed.** If the registry is missing, malformed or lacks an entry, the capability is off. A gate that fails open on a typo is not a gate.

**3. Gate at the seam.** Check the capability in one place, where the call leaves your code, not in every caller. One check is easy to test and hard to forget.

**4. Consent per surface.** Treat each surface as its own decision: each mailbox, each repository, each chat channel, each device. Granting access to one does not grant the next.

**5. Redact before egress.** Strip personal data and secrets before text goes to a model provider, a search service or a log shipper. Replace values with stable placeholders and restore them locally after the response returns. Put the redaction step in the same seam as the capability check so no path skips it.

**6. Record the subprocessors.** Keep a list of every external service that can receive data, with what it receives. If a service is not on the list, the agent cannot call it.

**7. Log changes.** A capability change is a security event. Write it to the audit trail with the actor and a timestamp.

## Failure modes it prevents

- A new integration ships enabled and nobody notices it can send messages.
- A fix for one connector accidentally enables access to another.
- Customer data reaches a provider you never approved.
- A registry typo silently turns a gate off.

## Start here

Write the registry with every external action the agent can take today. Set all but the read-only ones to `disabled`. Add one test that proves a disabled capability makes the call fail.
