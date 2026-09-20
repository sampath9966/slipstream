---
name: queue
description: Manage the window-aware job queue — list, approve, and dispatch pending jobs. Works in desktop, mobile, and CLI.
---

# /slipstream:queue

Manage the window-aware job queue (Module 2).

## Usage

```
/slipstream:queue
```

Invoked automatically or by the user to inspect and control pending jobs.

## What this skill does

1. Lists all pending and approved jobs in the queue (`slipstream queue list`)
2. Shows pacing status — current burn % and any active delay
3. For pending jobs, explains the Haiku pre-flight summary that was generated
4. Prompts the user to approve or skip each batch

## Commands

```bash
# Add a job to the queue
slipstream queue add --prompt "Refactor auth module" [--priority high]

# List pending jobs
slipstream queue list

# Approve jobs for dispatch
slipstream queue approve <job_id> [<job_id> ...]

# Dispatch approved jobs (respects pacing delay)
slipstream queue dispatch

# Install / uninstall OS background service
slipstream service install
slipstream service uninstall
```

## Pacing governor

When the session burn reaches `pacing_threshold_pct` (default 60%), the dispatcher
begins inserting delays before each job, ramping linearly from 0 s at the threshold
to `pacing_max_delay` seconds (default 300 s) at 100% burn. This prevents the
queue from burning the remaining window before a human can review.

Configure in `~/.slipstream/config.json`:
```json
{
  "pacing_threshold_pct": 60,
  "pacing_max_delay": 300
}
```

## Haiku pre-flight

Before a job is queued, `slipstream queue add` sends the prompt to
`Claude Haiku` for a one-sentence summary and cost estimate.
Set `ANTHROPIC_API_KEY` in your environment; if unset, the pre-flight is skipped
and the raw prompt is stored as-is.
