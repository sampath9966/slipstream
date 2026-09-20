# Slipstream

**Session economics for Claude Code.** Know what your tokens cost, which files burn them, and exactly when to start fresh — on any surface, with zero setup.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-orange.svg)](https://github.com/sampath9966/slipstream)
[![No telemetry](https://img.shields.io/badge/telemetry-none-green.svg)](PRIVACY.md)
[![Privacy](https://img.shields.io/badge/data-local%20only-brightgreen.svg)](PRIVACY.md)

---

> *"67% of your tokens this week came from re-reading 11 files. Pinning them to CLAUDE.md would save you $4.20/week."*

---

## Why Slipstream?

`/usage` tells you how many tokens you spent. **Slipstream tells you what they cost, which files burned them, what you could have saved, and whether to keep going or start fresh.**

| Without Slipstream | With Slipstream |
|--------------------|-----------------|
| Blind to cost until the bill arrives | Dollar cost per session, live |
| No idea which files re-burn context | Top wasted files ranked by $/week |
| Compaction wipes your working state | Anchor snapshot survives any reset |
| Rules in CLAUDE.md get ignored | Guard enforces rules at tool-use time |
| Context runs out mid-task | Advisor tells you when to wrap up |

---

## Install

```
/plugin marketplace add sampath9966/slipstream
```

That's it. Works immediately in Claude desktop, mobile, CLI, and remote containers. No terminal, no config, no flags required.

---

## Skills — works everywhere Claude runs

Type any of these in Claude chat, on any surface:

| Command | What it does |
|---------|-------------|
| `/slipstream:advisor` | Burn %, runway estimate, and a one-line recommendation |
| `/slipstream:report` | Full session cost breakdown with cache savings |
| `/slipstream:coach` | Re-read waste ranked by dollars/week, with inline fix |
| `/slipstream:anchor` | Context snapshot before compaction — nothing lost |
| `/slipstream:guard` | Enforce CLAUDE.md rules at tool-use time |
| `/slipstream:queue` | Window-aware job queue with pacing governor |
| `/slipstream:doctor` | Health check — hooks, ledger, config |
| `/slipstream:setup` | First-run configuration |

**All skills work on desktop, mobile, and CLI.** No shell access required — each skill falls back to inline Python or pure conversation automatically.

---

## What it looks like

```
/slipstream:advisor

Slipstream Advisor · this session
──────────────────────────────────────────────────────
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  71% of window used · ~2.1h left

  Top waste this week
  ├─ src/api/routes.py      28 reads · ~$1.84/week wasted → pin it
  ├─ src/db/models.py       21 reads · ~$1.38/week wasted → pin it
  └─ tests/conftest.py      19 reads · ~$1.25/week wasted → pin it

  Recommendation
  You're mid-window. Pin routes.py and models.py to CLAUDE.md now.
  That one change recovers ~$3.22/week and extends your runway by ~18%.

  Quick actions (no terminal needed)
  · "Pin routes.py for me" → I'll update CLAUDE.md right now
  · "Snapshot my context" → Anchor block ready to paste next session
  · "Show full report" → Complete 7-day breakdown
```

---

## Modules

| Module | What it does |
|--------|-------------|
| **Burn Ledger** | Per-turn, per-tool, per-file token tracking in local SQLite |
| **Advisor** | Conversational burn report — works on desktop, mobile, CLI |
| **Coach** | ROI-ranked waste analysis with inline CLAUDE.md fix |
| **Anchor** | Compaction snapshot — re-injects context after any reset |
| **Guard** | Declarative tool-use rules enforced before Claude acts |
| **Queue** | Window-aware job queue with linear pacing governor |

Each module is independently toggleable via plugin config.

---

## Data & privacy

**No telemetry. All data stays local.**

- Burn ledger: `~/.local/share/slipstream/ledger.db` (SQLite, local)
- Session cache: `.slipstream/last-session.json` (travels with your repo)
- Config: `~/.local/share/slipstream/config.json`
- No conversation content is ever stored
- The `queue add` / `decide` commands optionally call the Anthropic API (requires `ANTHROPIC_API_KEY`); no other outbound connections are made

Full details: [PRIVACY.md](PRIVACY.md)

---

## Configuration

Zero-config by default. Override any setting:

```json
// ~/.local/share/slipstream/config.json
{
  "window_tokens": 1000000,
  "warn_threshold_pct": 70,
  "critical_threshold_pct": 90,
  "cost_per_mtok_input": 3.00,
  "cost_per_mtok_output": 15.00,
  "cost_per_mtok_cache_read": 0.30,
  "cost_per_mtok_cache_write": 3.75,
  "haiku_model": "claude-haiku-4-5"
}
```

To enable `queue add` / `decide` AI analysis, set `ANTHROPIC_API_KEY` in your environment.

Or set via plugin `userConfig` in Claude Code settings.

---

## CLI (optional, for power users)

```bash
slipstream report --days 7
slipstream report --json | jq '.per_file[:5]'
slipstream queue add --prompt "Refactor auth module"
slipstream anchor snapshot --session-id <id>
slipstream doctor
```

---

## How it works

```
hooks/          Stop, PostToolUse, PreCompact, PostCompact, PreToolUse
bin/slipstream  Engine — Python 3 stdlib only, no external packages
skills/         Human interface — one SKILL.md per command
.slipstream/    Repo-level cache and guard rules (travels with the repo)
```

**Design rule:** hooks capture, `bin/` processes, skills are the interface. Hooks exit cleanly on any error and never block a session.

---

## Development

```bash
python3 -m pytest tests/ -v
slipstream doctor
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

Copyright 2026 sampath9966
