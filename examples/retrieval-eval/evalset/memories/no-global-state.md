---
name: no-global-state
description: Avoid module level mutable state.
type: preference
tags: design, testing, python
updated: 2026-09-01T09:00:00Z
---
Pass collaborators in as arguments with defaults. Tests then pass fakes and never patch internals.
