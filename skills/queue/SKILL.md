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
# Add a job to the queue (higher --priority runs first; --after waits for another job)
slipstream add "Refactor auth module" [--priority 5] [--files a.py b.py] [--after <job_id>]

# List jobs
slipstream queue list [--status pending_review|approved|running|done|failed]

# Review Haiku rewrites interactively (needs a terminal)
slipstream approve

# Run the dispatcher in the foreground (respects pacing delay)
slipstream dispatch

# Install / uninstall / check the background dispatcher service
slipstream service install
slipstream service uninstall
slipstream service status
```

`slipstream approve` is interactive, so run it in a terminal rather than through
Claude's Bash tool.

## Pacing governor

When the session burn reaches `pacing_threshold_pct` (default 60%), the dispatcher
begins inserting delays before each job, ramping linearly from 0 s at the threshold
to `pacing_max_delay` seconds (default 300 s) at 100% burn. This prevents the
queue from burning the remaining window before a human can review.

Configure in `~/.local/share/slipstream/config.json` (or the plugin's settings):
```json
{
  "pacing_threshold_pct": 60,
  "pacing_max_delay": 300
}
```

## Haiku pre-flight

Before a job is queued, `slipstream add` sends the prompt to Claude Haiku, which
checks for vague scope, unresolved references and missing acceptance criteria.
If Haiku rewrites the prompt, the job waits in `pending_review` until you run
`slipstream approve`; otherwise it is approved straight away. Set
`ANTHROPIC_API_KEY` in your environment; if unset, the pre-flight is skipped and
the raw prompt is approved as-is. The pre-flight sends the prompt to the
Anthropic API.
