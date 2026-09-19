---
name: report
description: Show token burn and dollar cost for the current or recent sessions. Works in desktop, mobile, and CLI — no setup needed.
---

# /slipstream:report

Show the slipstream burn report with dollar costs. Works on every surface — no setup needed.

## Zero-friction auto-setup

Before running, silently ensure config exists. If missing, create it with defaults — **do not ask the user anything**:

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
        "cost_per_mtok_output": 15.00,
        "cost_per_mtok_cache_read": 0.30,
        "cost_per_mtok_cache_write": 3.75
    }, indent=2))
AUTOSETUP
```

## How to run it

**Try the CLI first:**

```bash
slipstream report $ARGUMENTS
```

If found, show output verbatim, then append the dollar cost section.

**If CLI not found or Bash unavailable**, query inline:

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

totals = conn.execute("""
    SELECT COUNT(DISTINCT session_id) sessions,
           SUM(input_tokens) input, SUM(output_tokens) output,
           SUM(cache_read_tokens) cache_read, SUM(cache_write_tokens) cache_write,
           SUM(input_tokens+output_tokens+cache_read_tokens+cache_write_tokens) total
    FROM turns WHERE ts >= ?
""", (cutoff,)).fetchone()

top_files = conn.execute("""
    SELECT file_path, COUNT(*) reads FROM file_reads
    WHERE ts >= ? GROUP BY file_path ORDER BY reads DESC LIMIT 10
""", (cutoff,)).fetchall()

top_tools = conn.execute("""
    SELECT tool_name, COUNT(*) calls FROM tool_uses
    WHERE ts >= ? GROUP BY tool_name ORDER BY calls DESC LIMIT 8
""", (cutoff,)).fetchall()

cfg_path = Path(os.environ.get("SLIPSTREAM_CONFIG", f"{xdg}/slipstream/config.json"))
window = 1_000_000
rates = {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 3.75}
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    window = cfg.get("window_tokens", window)
    rates["input"] = cfg.get("cost_per_mtok_input", rates["input"])
    rates["output"] = cfg.get("cost_per_mtok_output", rates["output"])
    rates["cache_read"] = cfg.get("cost_per_mtok_cache_read", rates["cache_read"])
    rates["cache_write"] = cfg.get("cost_per_mtok_cache_write", rates["cache_write"])

t = dict(totals)
inp = t.get("input") or 0
out = t.get("output") or 0
cr  = t.get("cache_read") or 0
cw  = t.get("cache_write") or 0
total_tok = t.get("total") or 0

cost = (
    inp / 1e6 * rates["input"] +
    out / 1e6 * rates["output"] +
    cr  / 1e6 * rates["cache_read"] +
    cw  / 1e6 * rates["cache_write"]
)
cost_no_cache = (inp + cr) / 1e6 * rates["input"] + out / 1e6 * rates["output"] + cw / 1e6 * rates["cache_write"]
cache_savings = cost_no_cache - cost

print(json.dumps({
    "window": window, "days": days,
    "totals": t,
    "top_files": [dict(r) for r in top_files],
    "top_tools": [dict(r) for r in top_tools],
    "cost": round(cost, 4),
    "cost_no_cache": round(cost_no_cache, 4),
    "cache_savings": round(cache_savings, 4),
    "burn_pct": round(total_tok / window * 100, 1) if window else 0,
    "rates": rates,
}))
EOF
```

## Output format

```
Slipstream Burn Report · last 7 days · no telemetry · local only
─────────────────────────────────────────────────────────────────
  Total tokens   :    847,231  (84.7% of 1M window)
  Input          :    512,400
  Output         :     98,100
  Cache read     :    220,000   ← already saving you money
  Cache write    :     16,731
  Sessions       :         12

  💰 Estimated cost this week  :  $X.XX
     Without cache             :  $X.XX
     Cache saved you           :  $X.XX  (~XX%)

  Tool calls (last 7d):
    Read     312 calls
    Bash     204 calls
    Edit     156 calls

  Most-read files:
    ~/project/src/api/routes.py    28×
    ~/project/src/db/models.py     21×
```

After the report, add one sentence: the top finding (e.g. "routes.py was re-read 28 times — pinning it to CLAUDE.md could save ~$0.04/week.").

If cache savings > $0: "Your prompt cache is working — you're already paying X% less than you would without it."

## No ledger yet

> No data yet. Slipstream records usage starting from your next session.
>
> Quick tip while you wait: add your most-read files to CLAUDE.md — every re-read after the first will cost 90% less once tracking starts.

## No shell (desktop/mobile)

> I can't reach the ledger from this surface. To see your report, open Claude Code CLI and type `/slipstream:report` — or ask me "estimate my token cost" and I'll walk you through it based on what we've done this session.
