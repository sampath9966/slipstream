---
name: onboard
description: Zero-friction first-run setup for Slipstream — auto-configures everything, no questions asked.
trigger: install
---

# /slipstream:onboard

Zero-friction onboarding. Runs automatically after install (or manually any time). No questions, no flags, no terminal required.

## What this does

In one step, silently:
1. Creates config with smart defaults
2. Creates the data directory
3. Detects if the ledger already has data and shows a first insight if so
4. Shows a one-sentence confirmation — then gets out of the way

**Never ask the user to do anything before this runs.**

## How to run it

```bash
python3 - <<'EOF'
import json, os, sqlite3
from pathlib import Path

xdg = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
data_dir = Path(f"{xdg}/slipstream")
data_dir.mkdir(parents=True, exist_ok=True)

cfg_path = data_dir / "config.json"
already_configured = cfg_path.exists()

if not already_configured:
    cfg_path.write_text(json.dumps({
        "window_tokens": 1000000,
        "warn_threshold_pct": 70,
        "critical_threshold_pct": 90,
        "plan": "pro",
        "cost_per_mtok_input": 3.00,
        "cost_per_mtok_output": 15.00,
        "cost_per_mtok_cache_read": 0.30,
        "cost_per_mtok_cache_write": 3.75
    }, indent=2))

db_path = Path(os.environ.get("SLIPSTREAM_DB", str(data_dir / "ledger.db")))
has_data = False
sessions = 0
if db_path.exists():
    try:
        conn = sqlite3.connect(str(db_path))
        sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM turns").fetchone()[0]
        has_data = sessions > 0
    except Exception:
        pass

print(json.dumps({
    "already_configured": already_configured,
    "data_dir": str(data_dir),
    "cfg_path": str(cfg_path),
    "has_data": has_data,
    "sessions": sessions,
}))
EOF
```

## Response format

**If this is a fresh install (no prior config, no data):**

> ✅ **Slipstream is ready.** Tracking starts now — no setup needed.
>
> Your token usage will be recorded automatically in the background. After your next session, try `/slipstream:report` to see where your tokens went, or `/slipstream:coach` to get dollar savings recommendations.
>
> Everything stays on your machine. Nothing is ever uploaded.

**If already had data (returning user or re-install):**

> ✅ **Slipstream re-configured.** Your existing data at `~/.local/share/slipstream/` is intact.
>
> You have N sessions recorded. Run `/slipstream:coach` to see your savings opportunities.

**If Bash is unavailable (desktop/mobile)**, respond with this single message and stop — no further prompting:

> ✅ **Slipstream is active.** Token tracking runs automatically in the background.
>
> Ask me anything: "how are my tokens doing?", "what's burning my context?", or "show me my burn report" — I'll answer conversationally without needing a terminal.
>
> Nothing leaves your machine. You're all set.

## Trigger: natural language install phrases

This skill should also be invoked when the user says any of:
- "install slipstream"
- "set up slipstream"  
- "get started with slipstream"
- "use slipstream"
- "activate slipstream"
- "I just installed slipstream"

In all cases: run onboard silently, show one confirmation line, done. No wizard. No questions. No hoops.
