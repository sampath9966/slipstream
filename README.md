# Slipstream

> **"67% of your tokens this week came from re-reading 11 files."**

A Claude Code plugin for session economics. Know where your tokens go, pace your work against the rolling window, survive compaction, and make CLAUDE.md rules actually stick.

**No telemetry. Everything stays on your machine.** The ledger is SQLite at `~/.local/share/slipstream/ledger.db`. Nothing is ever uploaded or phoned home. This is a selling point, not a footnote.

## Install

```
/plugin marketplace add sampath9966/splitstream
/plugin install slipstream
```

Then configure your window size:

```
/slipstream:setup
```

## What you get

```
$ /slipstream:report

                    Slipstream Burn Report
                last 7 days · no telemetry · local only
──────────────────────────────────────────────────────────────
  Total tokens   :      847,231  (84.7% of 1,000,000 window)
  Input          :      512,400
  Output         :       98,100
  Cache read     :      220,000
  Cache write    :       16,731
  Sessions       :           12

  ★  67% of file reads this period came from re-reading 11 files.

  Tool calls (last 7d):
    Read                            312 calls
    Bash                            204 calls
    Edit                            156 calls
    Glob                             88 calls

  Most-read files (last 7d):
    ~/project/src/api/routes.py       28×
    ~/project/src/db/models.py        21×
    ~/project/tests/conftest.py       19×
```

## Modules

| Module | Status | What it does |
|--------|--------|--------------|
| **ledger** | ✅ v0.1.0 | Token burn ledger — per turn, per tool, per file |
| **queue** | 🚧 planned | Window-aware job queue with pacing governor |
| **anchor** | 🚧 planned | Compaction snapshot — survive context resets |
| **guard** | 🚧 planned | Enforce CLAUDE.md rules at tool-use time |

Each module is independently toggleable in plugin config.

## Module 1 — Burn Ledger

Every turn and every tool use is recorded to SQLite. You get:

- Per-session, per-tool, and per-file breakdowns
- The headline "X% of reads came from N files" number
- A live in-session budget monitor (warns at 70% and 90% by default)
- A statusline fragment: `▒ 71% ~2.3h left`
- `slipstream report --json` for scripting

### Statusline

Add to your shell prompt or tmux status line:

```bash
$(slipstream statusline)
```

Output: `▓ 91% ~0.4h left` (critical) / `▒ 71%` (warn) / `░ 43%` (normal)

### Scripting

```bash
slipstream report --json --days 1 | jq '.totals.total'
slipstream report --json | jq '.per_file[:5]'
```

## Configuration

Set via plugin `userConfig` or `~/.local/share/slipstream/config.json`:

```json
{
  "window_tokens": 1000000,
  "warn_threshold_pct": 70,
  "critical_threshold_pct": 90
}
```

Export the path: `export SLIPSTREAM_CONFIG=~/.local/share/slipstream/config.json`

Override DB path: `export SLIPSTREAM_DB=/path/to/ledger.db`

## Health check

```
/slipstream:doctor
```

or from a terminal:

```bash
slipstream doctor
```

## Architecture

```
slipstream/
├── .claude-plugin/plugin.json    # Plugin manifest
├── .claude-plugin/marketplace.json
├── hooks/hooks.json              # Stop → record, PostToolUse → record-tool
├── skills/report/                # /slipstream:report
├── skills/doctor/                # /slipstream:doctor
├── skills/setup/                 # /slipstream:setup
├── monitors/monitors.json        # In-session budget warnings
├── bin/slipstream                # Engine (Python 3.11+, stdlib + sqlite3)
└── tests/test_ledger.py          # Ledger math and parser tests
```

Design rule: **hooks do the capture, `bin/` does the work, skills are the human interface.** Hooks exit cleanly on any error — they never block or crash a session.

Token usage comes from parsing the transcript JSONL at `transcript_path` (provided by each `Stop` hook payload), not from the hook payload itself.

## Development

```bash
python3 -m pytest tests/ -v
slipstream doctor
slipstream report --days 1
```

## License

MIT — see [LICENSE](LICENSE).
