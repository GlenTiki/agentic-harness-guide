---
name: migration-safety
description: Schema migrations must be reversible.
type: rule
tags: database, release, safety
updated: 2026-09-01T09:00:00Z
---
Every migration has a tested way back. Deploy the code that reads the new column before the one that writes it.
