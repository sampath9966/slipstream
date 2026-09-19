---
name: report
description: Show token burn and dollar cost for this session. Works in desktop, mobile, any container — like /usage but deeper.
---

# /slipstream:report

Show the Slipstream burn report. Works on every surface, in every container, with no setup.

## Execution order — read each source in turn, use the first one that has data

### Source 1 — Repo-level session cache (works in any container for this repo)

Check for `.slipstream/last-session.json` in the current working directory. This file is written by the `Stop` hook after every session and travels with the repo — so any new container that opens the same repo has data immediately, no ledger needed.

```bash
python3 - <<'EOF'
import json, os, sys
from pathlib import Path

cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
cache = Path(cwd) / ".slipstream" / "last-session.json"
if cache.exists():
    print(cache.read_text())
else:
    print(json.dumps({"error": "no_cache"}))
EOF
```

If found, present it as:

```
Slipstream · last session · <model>
──────────────────────────────────────────────────────
  Input          :  XXX,XXX tokens
  Output         :   XX,XXX tokens
  Cache read     :  XXX,XXX tokens  ← cache saving you money
  Cache write    :   XX,XXX tokens
  Total          :  XXX,XXX tokens

  💰 Estimated session cost  :  $X.XXXX
     (at $3.00/MTok input · $15.00/MTok output · $0.30/MTok cache-read)

  Cache coverage : XX%  (tokens served from cache vs. total)
```

Then offer: "Want the 7-day history? I can pull that too if your local ledger is available."

---

### Source 2 — Local ledger (works on the user's own machine)

If Source 1 has no data, query `~/.local/share/slipstream/ledger.db`:

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

cost = (inp/1e6*rates["input"] + out/1e6*rates["output"] +
        cr/1e6*rates["cache_read"] + cw/1e6*rates["cache_write"])

print(json.dumps({
    "window": window, "days": days, "totals": t,
    "top_files": [dict(r) for r in top_files],
    "top_tools": [dict(r) for r in top_tools],
    "cost": round(cost, 4),
    "burn_pct": round(total_tok / window * 100, 1) if window else 0,
    "rates": rates,
}))
EOF
```

Format as the full 7-day report with tool breakdown, file reads, and dollar cost.

---

### Source 3 — Current session context (always works, everywhere, no files needed)

If both sources above have no data, Claude already knows the current session's token count from the conversation context. Use it:

> **Slipstream · current session** (from conversation context)
>
> This session has used approximately **[X tokens]** so far.
> At Claude Pro rates ($3.00/MTok input, $0.30/MTok cache-read):
> **Estimated cost: ~$X.XX**
>
> *Note: This is the current session only. Historical data will appear here after your first full session with the Stop hook active.*

---

### Source 4 — No data, no shell (mobile with no prior sessions)

> No session data yet for this repo. Here's what Slipstream will track once a session completes:
> - Tokens by type (input / output / cache read / cache write)
> - Dollar cost per session
> - Most-read files and their re-read waste
>
> All stored in `.slipstream/last-session.json` in this repo — available in any container, any device, next time you open it.
