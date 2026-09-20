---
name: coach
description: Analyze token waste and get ROI-ranked savings in dollars. Works in desktop, mobile, and CLI — no setup needed.
---

# /slipstream:coach

Analyze token waste and show dollar savings. Works on every surface — no terminal, no setup needed.

## Zero-friction auto-setup

Before anything else, silently ensure config exists. If `~/.local/share/slipstream/config.json` is missing, create it with smart defaults — **do not ask the user anything**:

```bash
python3 - <<'AUTOSETUP'
import json, os
from pathlib import Path

xdg = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
cfg_dir = Path(f"{xdg}/slipstream")
cfg_dir.mkdir(parents=True, exist_ok=True)
cfg_path = cfg_dir / "config.json"

if not cfg_path.exists():
    cfg_path.write_text(json.dumps({
        "window_tokens": 1000000,
        "warn_threshold_pct": 70,
        "critical_threshold_pct": 90,
        "plan": "pro",
        "cost_per_mtok_input": 3.00,
        "cost_per_mtok_cache_read": 0.30
    }, indent=2))
AUTOSETUP
```

## How to run it

**Try the CLI first:**

```bash
slipstream coach $ARGUMENTS
```

If found, show output verbatim, then append the dollar savings section below.

**If CLI not found or Bash unavailable**, run inline:

```bash
python3 - <<'EOF'
import sqlite3, json, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

xdg = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
db = Path(os.environ.get("SLIPSTREAM_DB", f"{xdg}/slipstream/ledger.db"))

if not db.exists():
    print(json.dumps({"error": "no_ledger"}))
    exit(0)

conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
days = 7
cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

files = conn.execute("""
    SELECT file_path, COUNT(*) reads FROM file_reads
    WHERE ts >= ? GROUP BY file_path ORDER BY reads DESC LIMIT 15
""", (cutoff,)).fetchall()

total_reads = conn.execute(
    "SELECT COUNT(*) FROM file_reads WHERE ts >= ?", (cutoff,)
).fetchone()[0]

cfg_path = Path(os.environ.get("SLIPSTREAM_CONFIG", f"{xdg}/slipstream/config.json"))
window = 1_000_000
cost_per_mtok_input = 3.00
cost_per_mtok_cache_read = 0.30
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    window = cfg.get("window_tokens", window)
    cost_per_mtok_input = cfg.get("cost_per_mtok_input", cost_per_mtok_input)
    cost_per_mtok_cache_read = cfg.get("cost_per_mtok_cache_read", cost_per_mtok_cache_read)

avg_file_tokens = 520
results = []
for row in files:
    wasted_reads = max(0, row["reads"] - 1)
    wasted_tokens = wasted_reads * avg_file_tokens
    # Cost without caching: full input price
    cost_without = (wasted_tokens / 1_000_000) * cost_per_mtok_input
    # Cost with caching: cache-read price (10% of input)
    cost_with = (wasted_tokens / 1_000_000) * cost_per_mtok_cache_read
    savings = cost_without - cost_with
    results.append({
        "file": row["file_path"],
        "reads": row["reads"],
        "wasted_reads": wasted_reads,
        "wasted_tokens": wasted_tokens,
        "cost_without": round(cost_without, 4),
        "cost_with": round(cost_with, 4),
        "savings": round(savings, 4),
    })

total_savings = sum(r["savings"] for r in results)
total_wasted_tok = sum(r["wasted_tokens"] for r in results)

print(json.dumps({
    "total_reads": total_reads,
    "files": results,
    "total_savings_week": round(total_savings, 2),
    "total_savings_month": round(total_savings * 4.33, 2),
    "total_wasted_tokens": total_wasted_tok,
    "window": window,
    "cost_per_mtok_input": cost_per_mtok_input,
}))
EOF
```

## Output format

Present the result as:

```
Slipstream Coach · token waste & dollar savings · last 7 days
──────────────────────────────────────────────────────────────
  Estimated waste this week :  ~$X.XX  →  ~$XX/month if unaddressed
  Fix: pin top files to CLAUDE.md → save ~90% of that cost

  1. ~/path/to/routes.py
     28× reads · 27 wasted · ~14k tokens
     This week: $0.042 wasted → $0.004 if pinned  (save $0.038)

  2. ~/path/to/models.py
     21× reads · 20 wasted · ~10k tokens
     This week: $0.031 wasted → $0.003 if pinned  (save $0.028)

  ...

  ★ Pinning all top files saves ~$X.XX/week · ~$XX.XX/year
    on a 1M-token window at $3.00/MTok input
```

If savings > $0.50/month, add:
> That's real money. Want me to pin these files to CLAUDE.md right now? Just say "pin them" and I'll do it in one step — no terminal needed.

## Inline actions (no terminal needed)

- **"Pin them" / "Pin all"** → Use the Edit tool to add each file to CLAUDE.md under `## Context files` with a `@path` reference. Confirm what was added.
- **"Pin just the top 3"** → Same, top 3 only.
- **"How does pinning save money?"** → Explain: pinned files are served from Claude's prompt cache at ~10% of normal input cost on every re-read after the first.
- **"What's my plan rate?"** → Tell them the default is $3.00/MTok (Claude Pro) and they can override it in config.

## No ledger yet

> No usage data yet — Slipstream starts recording after your first session with the plugin active.
> 
> Here's what I can tell you now: if you re-read any file more than once per session, you're paying full price each time. Pin your most-used files to CLAUDE.md and every re-read after the first costs 90% less.
>
> Want me to look at your current project and suggest which files to pin based on their size and likely re-read frequency?

## No shell (desktop/mobile)

> I can't read the ledger from this surface, but I can still coach you right now.
>
> Tell me which files you find yourself asking about most often (e.g. "I keep looking at routes.py and auth.py"). I'll estimate the dollar waste and tell you exactly what to add to CLAUDE.md to fix it — one step, no terminal.
