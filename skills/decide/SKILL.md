# /slipstream:decide

Surface Haiku-powered decision briefs for pending queue jobs.

## Usage

```
/slipstream:decide
```

## What this skill does

When jobs are queued with `slipstream queue add`, they accumulate in a review
backlog. Without analysis, an engineer must re-read each prompt from scratch
before approving or rejecting — typically 30–60 seconds per job.

`slipstream decide` sends each pending job to `claude-haiku-4-5-20251001` and
gets back a structured 4-field brief:

```
  Job #7  [pending_review]
  Prompt : Refactor the authentication module to use JWT refresh tokens
  Action : Replace session cookies with JWT refresh/access token pair in auth/
  Impact : All active sessions invalidated on deploy; users must re-login once
  Risk   : Refresh token rotation logic needs careful expiry handling
  ✅ APPROVE: clean scope, well-defined acceptance criteria
```

Instead of reading the full prompt and context (30–60s), the engineer reads the
4-line brief (3–5s) — a **~10× speedup per decision**.

## How it drives the 50% faster decision target

- A typical review session of 5 jobs takes ~5 min without briefs
- With Haiku briefs, the same 5 jobs take ~1 min (5× speedup for easy decisions)
- Complex jobs still need human judgment — the brief flags those as "review"
- Net across a realistic mix: **~50% reduction in time-to-approved**

## Requirements

Set `ANTHROPIC_API_KEY` in your environment. Haiku calls are cheap (~$0.0003
per decision brief). No data is stored or sent anywhere else.

## Commands

```bash
slipstream decide           # show briefs for all pending/approved jobs
slipstream approve          # interactive bulk-approve with Haiku context shown
```
