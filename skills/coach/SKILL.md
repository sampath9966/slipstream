---
name: coach
description: Analyze token waste and get ROI-ranked savings recommendations. Works in desktop, mobile, and CLI — no terminal needed.
---

# /slipstream:coach

Analyze token waste and give ROI-ranked savings recommendations. Works in desktop, mobile, and CLI.

## Usage

```
/slipstream:coach
```

## How to run it

**Try the CLI first:**

```bash
slipstream coach $ARGUMENTS
```

Show the output verbatim, then offer to apply the fixes inline.

**If the CLI is not found or Bash is unavailable**, query the ledger directly:

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
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    window = cfg.get("window_tokens", window)

avg_file_tokens = 520
results = []
for row in files:
    wasted_reads = max(0, row["reads"] - 1)
    wasted_tokens = wasted_reads * avg_file_tokens
    pct_window = (wasted_tokens / window) * 100
    results.append({
        "file": row["file_path"],
        "reads": row["reads"],
        "wasted_reads": wasted_reads,
        "wasted_tokens": wasted_tokens,
        "pct_window": round(pct_window, 2),
    })

top_reads = sum(r["reads"] for r in results[:5])
pct_top = round((top_reads / total_reads * 100) if total_reads else 0, 1)

print(json.dumps({
    "total_reads": total_reads,
    "pct_top5": pct_top,
    "files": results,
    "window": window,
}))
EOF
```

Format the result as a coaching report:

```
Slipstream Coach · token waste analysis
──────────────────────────────────────────────
  ★ Top 5 files account for XX% of all reads

  1. ~/path/to/file.py
     28× reads → 27 wasted → ~14k tok (1.4% window)
     Fix: pin to CLAUDE.md → 90% cost reduction on re-reads

  2. ...
```

After the list, offer these **inline actions** (no terminal needed):

- **"Pin all to CLAUDE.md"** → Use the Edit tool to add each file to the project CLAUDE.md under a `## Always read these files` section.
- **"Pin just the top 3"** → Same, limited to top 3.
- **"Explain what pinning does"** → Explain prompt caching: pinned files are cache-read at ~10% of normal token cost on subsequent turns.

**If the ledger does not exist yet**, respond:

> No data yet — Slipstream will start tracking file reads from your next session. Run `/slipstream:coach` again after a few sessions to see your waste analysis.

**If Python and Bash are both unavailable**, respond:

> I can't read the ledger from this surface. However, I can still coach you right now:
>
> Tell me which files you find yourself re-reading most often in your sessions (e.g. "I keep re-reading routes.py and models.py"). I'll calculate the approximate token waste and tell you exactly what to add to CLAUDE.md to fix it.
