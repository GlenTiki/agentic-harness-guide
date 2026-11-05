---
name: secrets-handling
description: Never commit secrets.
type: rule
tags: security, config, deploy
updated: 2026-09-01T09:00:00Z
---
Read credentials from environment variables at start. Fail fast when one is missing. Rotate a leaked key at once.
