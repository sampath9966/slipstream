# /slipstream:coach

Analyze token waste and surface ROI-ranked savings recommendations.

## Usage

```
/slipstream:coach
```

## What this skill does

Slipstream tracks every file read in every session. Most engineers re-read the
same 10–15 files dozens of times per week. Each re-read costs the same token
budget as the first read — unless the file is pinned in CLAUDE.md, where it
gets served from the prompt cache at ~10% of the fresh-read cost.

`slipstream coach` quantifies this waste and ranks files by ROI:

```
  1. ~/project/src/api/routes.py
     28× reads → 27 wasted → ~14,040 tok  (1.4% window)
     Fix: pin to CLAUDE.md (cache-read on subsequent turns)

  ► Run `slipstream optimize` to generate CLAUDE.md pins → target -47% usage
```

## How it drives the 45% token saving target

When the top 10 re-read files are pinned to CLAUDE.md:
- First read: normal input tokens (unavoidable)
- Every subsequent read: served from prompt cache at ~10% cost
- For a typical session where 11 files account for 67% of reads:
  **saving = 67% × 90% = ~60% of re-read tokens ≈ 40–50% of total session spend**

## Commands

```bash
slipstream coach            # human-readable report
slipstream coach --days 30  # longer lookback
slipstream coach --json     # machine-readable for scripting

slipstream optimize         # apply the fixes → update CLAUDE.md
slipstream optimize --dry-run   # preview output only
slipstream optimize --top 5     # pin only top 5 files
```
