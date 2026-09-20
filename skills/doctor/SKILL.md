---
name: doctor
description: Check slipstream installation health. Works in desktop, mobile, and CLI.
---

# /slipstream:doctor

Health-check the slipstream installation. Works on every surface.

## How to run it

**Try the CLI first:**

```bash
slipstream doctor
```

Show the full output. If there are errors, diagnose and fix:
- "NOT executable" → `chmod +x <path>/bin/slipstream`
- "cannot open DB" → check `~/.local/share/slipstream/` is writable
- "not set" for CLAUDE_PLUGIN_ROOT → expected outside Claude Code; hooks won't run but the CLI still works

**If the CLI is not found or Bash is unavailable**, run the inline check:

```bash
python3 - <<'EOF'
import os, sys, sqlite3
from pathlib import Path

results = []

# Check ledger
xdg = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
db = Path(os.environ.get("SLIPSTREAM_DB", f"{xdg}/slipstream/ledger.db"))
if db.exists():
    try:
        conn = sqlite3.connect(str(db))
        n = conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
        results.append(f"✅ Ledger OK — {n} turns recorded at {db}")
    except Exception as e:
        results.append(f"❌ Ledger error: {e}")
else:
    results.append(f"⚠️  No ledger yet at {db} — will be created on first session")

# Check config
cfg = Path(os.environ.get("SLIPSTREAM_CONFIG", f"{xdg}/slipstream/config.json"))
if cfg.exists():
    results.append(f"✅ Config found at {cfg}")
else:
    results.append(f"ℹ️  No config file — using defaults (window=1,000,000 tokens)")

# Check plugin env
root = os.environ.get("CLAUDE_PLUGIN_ROOT")
if root:
    results.append(f"✅ CLAUDE_PLUGIN_ROOT={root}")
else:
    results.append("ℹ️  CLAUDE_PLUGIN_ROOT not set — normal outside a CLI session")

for r in results:
    print(r)
EOF
```

Show the inline check results and summarise in one sentence whether slipstream is healthy.

**If Python and Bash are both unavailable**, respond conversationally:

> I can't run a health check directly from this surface, but here's what to verify manually:
> 1. **Ledger** — does `~/.local/share/slipstream/ledger.db` exist? (It appears after the first session.)
> 2. **Config** — is there a `~/.local/share/slipstream/config.json`? (Optional; defaults are used if absent.)
> 3. **Hooks** — are the slipstream hooks listed in your Claude Code settings? Check Settings → Hooks.
>
> If anything looks wrong, tell me what you see and I'll help diagnose it.
