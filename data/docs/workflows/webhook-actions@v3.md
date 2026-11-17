---
doc_id: workflows/webhook-actions
version: v3
published_at: 2026-06-01
superseded_by: null
area: workflows
source_type: help_doc
trust_level: trusted_internal
---

# Webhook actions

## Overview

Webhook actions let a FlowDesk workflow call an external HTTP endpoint when a
trigger fires.

## Timeouts

The webhook action timeout is **30 seconds**. If the remote server does not
respond within that window, the step fails with `WEBHOOK_TIMEOUT`.

## Retries

Failed webhook calls retry up to 3 times with exponential backoff.
