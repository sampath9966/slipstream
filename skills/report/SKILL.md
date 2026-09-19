---
name: report
description: Show a burn report — token usage by session, tool, and file — for the current or recent sessions. Works in desktop, mobile, and CLI.
---

# /slipstream:report

Show the slipstream burn report. Works on every surface — no terminal needed.

## How to run it

**Try the CLI first** (works in Claude Code CLI and remote containers):

```bash
slipstream report $ARGUMENTS
```

If the command is found, show the output verbatim, then offer a one-line interpretation of the top finding.

**If the CLI is not found or Bash is unavailable** (desktop app, mobile), query the ledger directly:

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
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    window = cfg.get("window_tokens", window)

print(json.dumps({
    "window": window, "days": days,
    "totals": dict(totals),
    "top_files": [dict(r) for r in top_files],
    "top_tools": [dict(r) for r in top_tools],
}))
EOF
```

Then format the result as a clean report:

```
Slipstream Burn Report · last 7 days · local only
──────────────────────────────────────────────────
  Total tokens   :  XXX,XXX  (XX% of window)
  Input          :  XXX,XXX
  Output         :   XX,XXX
  Cache read     :  XXX,XXX
  Cache write    :   XX,XXX
  Sessions       :       NN

  Tool calls:
    Read     NNN calls
    Bash     NNN calls
    Edit     NNN calls

  Most-read files:
    ~/path/to/file.py   NN×
    ...
```

Then add the top finding as one sentence (e.g. "67% of file reads came from re-reading 5 files — consider pinning them to CLAUDE.md.").

**If the ledger does not exist yet**, respond:

> No data yet. Slipstream records usage starting from your next session. Come back then for your first report.

**If Python and Bash are both unavailable** (some mobile surfaces), respond:

> I can't read the ledger from this surface. To see your report:
> - In the Claude Code CLI or desktop terminal: run `/slipstream:report`
> - Or ask me "how do I read my token usage without a terminal?" and I'll walk you through it.
