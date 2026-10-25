---
name: retry-policy
description: Retry failed network calls with backoff.
type: procedure
tags: reliability, network, errors
updated: 2026-09-01T09:00:00Z
---
Retry only idempotent calls. Wait longer after each failure, add jitter and cap the attempts.
