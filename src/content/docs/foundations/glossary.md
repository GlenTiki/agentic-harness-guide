---
title: Glossary
description: The terms this guide uses, each with one meaning.
---

**Recommendation:** use these terms the same way in your own instruction files. A term with two meanings produces two behaviours.

## Terms

**Agent.** A model running in a loop that can call tools until it decides it is done.

**Harness.** Everything around the model: the loop, tools, permissions, hooks, instruction loading, memory and logging. This guide uses "harness" for the whole system and "agent" for the model inside it.

**Instruction file.** A text file the harness loads into context at the start of a session, such as `AGENTS.md` or `CLAUDE.md`.

**Context window.** The text the model can see in one request. It is finite and the harness may shorten it by compaction.

**Compaction.** Replacing older conversation with a summary to free space. Detail is lost.

**Hook.** A script the harness runs at a fixed lifecycle event, for example before or after a tool call. A hook runs whether or not the model agrees.

**Permission rule.** A harness setting that allows, asks about or denies a tool call by pattern.

**Sandbox.** An operating system boundary around commands that limits the files and network hosts they can reach.

**Capability.** A named power the agent may use, such as "send email" or "write to the calendar". A capability can be on or off independently of the others.

**Sub-agent.** An agent started by another agent, with its own context and a task brief. It returns a summary.

**Brief.** The written task a lead agent gives a sub-agent. It is the only context the sub-agent receives.

**Ledger.** A durable file that records intent, decisions, failures and findings. It survives compaction and session restarts.

**Skill.** A packaged set of instructions, and optionally scripts, that the harness loads on demand.

**MCP server.** A process that exposes tools to the agent over the Model Context Protocol.

**Worktree.** A second checkout of the same repository in another directory, on its own branch.

**Digest.** A hash of an exact diff or file set. Approval recorded against a digest applies to that content only.

**Eval.** A repeatable test of a model-driven step, scored against fixed expectations.

**Prompt injection.** Text in data that tries to act as an instruction to the agent.

## Start here

Add four of these terms to your instruction file with your own definitions: brief, ledger, capability and digest. They are the ones teams most often use loosely.
