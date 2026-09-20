# Slipstream — CLAUDE.md

## Architecture

```
hooks/          Capture layer  — Stop, PostToolUse, PreCompact, PostCompact, PreToolUse, SessionStart
bin/slipstream  Engine         — all processing, SQLite reads/writes, CLI (pure Python stdlib)
skills/         Interface      — one SKILL.md per /slipstream:* command
monitors/       Budget monitor — long-running process that emits threshold warnings
.slipstream/    Repo-level     — last-session.json cache, rules.yaml guard rules
```

**Design invariant:** hooks capture, `bin/` processes, skills are the user interface.
Hooks must always exit 0 on errors — they must never block or crash a Claude session.
Exit code 2 from a hook is the only intentional non-zero (PreToolUse rule block).

## Key constraints

- **Zero external dependencies** — engine uses only Python stdlib + sqlite3. Never add pip packages.
- **No telemetry** — no outbound connections except the Anthropic API for `queue add` / `decide`, gated by user's `ANTHROPIC_API_KEY`.
- **Three-surface fallback** — every skill must work on CLI, desktop (no shell), and mobile (no filesystem). Pattern: CLI → inline Python/SQLite → pure conversation.
- **Hooks are silent on errors** — wrap everything in try/except and return 0. Never print to stdout from a hook unless it's a deliberate user-visible message (warmup, guard block).
- **Model IDs via config** — never hardcode a dated model ID (e.g. `claude-haiku-4-5-20251001`). Read `haiku_model` from config; default to the undated alias `claude-haiku-4-5`.

## Testing

```bash
python3 -m pytest tests/ -v    # all 35 unit tests
bin/slipstream doctor          # smoke-test engine + DB
bin/slipstream report --json   # verify JSON output shape
```

Tests live in `tests/test_ledger.py`. Every change to ledger math, pacing governor, or dollar-cost calculation requires a test. Hook changes do not require tests (they are integration-only).

## Skill frontmatter

All `skills/*/SKILL.md` files must have YAML frontmatter:

```yaml
---
name: <skill-name>
description: <one-line description shown in autocomplete>
---
```

## Guard rules

`.slipstream/rules.yaml` ships safe defaults. Rule matching uses exact string comparison (`command_contains`), never eval or regex on untrusted input. New match keys must use the same approach.

## Dollar cost rates

Default rates ($/MTok): input 3.00, output 15.00, cache_read 0.30, cache_write 3.75.
Users override via `~/.local/share/slipstream/config.json` (`cost_per_mtok_input`, etc.).
Never hardcode rates outside `cmd_record` defaults — they change with Anthropic pricing.

## File paths written by the engine

| Path | Written by | Purpose |
|------|-----------|---------|
| `~/.local/share/slipstream/ledger.db` | `open_db()` | Rolling 7-day SQLite ledger |
| `~/.local/share/slipstream/config.json` | skills (setup/onboard/coach) | User config |
| `<cwd>/.slipstream/last-session.json` | `cmd_record` (Stop hook) | Per-repo session cache |
| `<cwd>/.slipstream/rules.yaml` | ships in repo | Guard rules |
