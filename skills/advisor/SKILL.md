---
name: advisor
description: Let Claude consult a strong token advisor — burn status, waste analysis, and inline fixes. Works in desktop, mobile, and CLI without any terminal flags.
---

# /slipstream:advisor

A conversational token advisor that works in Claude desktop, mobile, and any surface — no terminal, no CLI flags needed.

## Usage

```
/slipstream:advisor
```

Or ask naturally:
- "How are my tokens doing?"
- "What's burning my context?"
- "Should I keep going or start a new session?"
- "What files should I pin?"

## What this skill does

This skill is the **no-CLI equivalent** of the full slipstream toolkit. It reads the SQLite ledger directly (no shell commands) and gives you a conversational briefing. It works identically in:

- Claude desktop app
- Claude mobile app
- Claude Code CLI
- Claude on the web (remote container)

---

## How to run it

### Step 0 — Silent auto-setup (always first)

Before anything else, silently ensure config exists — **no questions**:

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
        "window_tokens": 1000000, "warn_threshold_pct": 70, "critical_threshold_pct": 90,
        "cost_per_mtok_input": 3.00, "cost_per_mtok_cache_read": 0.30
    }, indent=2))
AUTOSETUP
```

### Step 1 — Try to read the ledger

Attempt this Bash command (skip silently if Bash is unavailable):

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
cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

totals = conn.execute("""
    SELECT
        COUNT(DISTINCT session_id) sessions,
        SUM(input_tokens) input,
        SUM(output_tokens) output,
        SUM(cache_read_tokens) cache_read,
        SUM(cache_write_tokens) cache_write,
        SUM(input_tokens+output_tokens+cache_read_tokens+cache_write_tokens) total
    FROM turns WHERE ts >= ?
""", (cutoff,)).fetchone()

top_files = conn.execute("""
    SELECT file_path, COUNT(*) reads
    FROM file_reads
    WHERE ts >= ?
    GROUP BY file_path ORDER BY reads DESC LIMIT 10
""", (cutoff,)).fetchall()

top_tools = conn.execute("""
    SELECT tool_name, COUNT(*) calls
    FROM tool_uses
    WHERE ts >= ?
    GROUP BY tool_name ORDER BY calls DESC LIMIT 8
""", (cutoff,)).fetchall()

cfg_path = Path(os.environ.get("SLIPSTREAM_CONFIG",
    f"{xdg}/slipstream/config.json"))
window = 1_000_000
if cfg_path.exists():
    import json as _j
    cfg = _j.loads(cfg_path.read_text())
    window = cfg.get("window_tokens", window)

result = {
    "window": window,
    "totals": dict(totals),
    "top_files": [dict(r) for r in top_files],
    "top_tools": [dict(r) for r in top_tools],
}
print(json.dumps(result))
EOF
```

### Step 2 — Interpret the data and respond conversationally

**If the ledger was read successfully**, produce a response in this format:

---

**Slipstream Advisor** · last 7 days

> **[burn bar]** ░▒▓ X% of window used · ~Y hours left at current pace

**Where your tokens went**
- Top re-read file: `<path>` — Xk tokens, read N×, wasting ~$X.XX/week → pin it to CLAUDE.md to cut that 90%
- Most-called tool: `<tool>` (N calls)
- Sessions this week: N · estimated cost: ~$X.XX

**My recommendation**
[One of the three advisor stances below, based on burn %:]

- **< 50% burn** → "You have plenty of runway. Keep going — no changes needed."
- **50–80% burn** → "You're mid-window. Consider pinning `<top file>` to CLAUDE.md now. That one change could recover ~X% of your remaining budget."
- **> 80% burn** → "You're in the red zone. Finish your current thought, then start a fresh session. Before you do: run `/slipstream:anchor` (or ask me to snapshot your context) so nothing is lost."

**Quick actions you can do right here (no terminal needed)**
- "Pin `<top file>` to CLAUDE.md for me" → I'll add the CLAUDE.md entry now.
- "Snapshot my context" → I'll write an anchor summary you can paste into the next session.
- "Show me the full report" → I'll format the complete breakdown.

---

**If the ledger does not exist yet** (no sessions recorded), respond:

> No ledger found yet — Slipstream starts recording after your first session with the plugin active. Come back after your next conversation and I'll have data for you.
>
> In the meantime, I can still help you set up CLAUDE.md pins or explain how the burn tracking works. Just ask.

**If Bash is unavailable** (desktop/mobile with no shell access), respond:

> I can't reach the ledger directly from this surface, but I can still help you as an advisor. Tell me:
> 1. Roughly how far into your context window do you feel you are? (early / halfway / running low)
> 2. What are you working on right now?
>
> I'll give you a concrete recommendation based on your answer — no data needed.

Then when the user answers, give the same three-stance recommendation (keep going / pin files / wrap up and anchor), tailored to what they described.

---

## Advisor stances (reference)

| Burn | Stance | Action |
|------|--------|--------|
| < 50% | Green | Keep going |
| 50–80% | Amber | Pin top re-read files; consider compacting non-essential context |
| > 80% | Red | Wrap up; run anchor; start fresh session |

## What the advisor can do inline (no CLI)

- **Pin a file to CLAUDE.md** — edit the file directly via the Edit tool
- **Write an anchor summary** — produce a structured snapshot the user pastes into the next session's first message
- **Explain any metric** — interpret burn %, cache hit rate, re-read waste
- **Suggest a CLAUDE.md rule** — draft a guard rule to prevent a pattern the user describes

The advisor never needs the terminal. Everything it can do, it does through conversation or direct file edits.
