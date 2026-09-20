# Contributing to Slipstream

## Ground rules

- **No telemetry, ever.** Any code that phones home will be rejected immediately.
- **Stdlib-first.** New dependencies require strong justification — the core engine has zero external packages.
- **Tests are mandatory** for ledger math, pacing governor, and any dollar-cost calculation — these are the places a bug silently costs users money.
- **All skills must have YAML frontmatter** (`name`, `description`) so they appear in the Claude slash command picker.

## Dev setup

```bash
git clone https://github.com/sampath9966/splitstream
cd splitstream
python3 -m pytest tests/ -v
slipstream doctor
```

No virtualenv required — stdlib + sqlite3 only.

## Architecture

```
hooks/          Capture layer — Stop, PostToolUse, PreCompact, PostCompact, PreToolUse
bin/slipstream  Engine — all processing, SQLite reads/writes, CLI
skills/         Human interface — one SKILL.md per /slipstream:* command
.slipstream/    Repo-level cache and guard rules
```

**Design rule:** hooks capture, `bin/` processes, skills are the interface. Hooks must exit cleanly on any error — they never block or crash a session.

## Modules

| Module | Status | Accepting |
|--------|--------|-----------|
| **Burn Ledger** | ✅ Shipped v0.1.0 | Bug fixes, parser improvements |
| **Queue** | ✅ Shipped v0.2.0 | Bug fixes, pacing improvements |
| **Anchor** | ✅ Shipped v0.2.0 | Bug fixes, snapshot quality |
| **Guard** | ✅ Shipped v0.2.0 | New match keys, rule improvements |
| **Advisor** | ✅ Shipped v0.2.0 | New stances, surface improvements |
| **Coach** | ✅ Shipped v0.2.0 | New waste metrics, cost improvements |

## Submitting changes

1. Fork, branch from `main`
2. Tests must pass: `python3 -m pytest tests/ -v`
3. Run `slipstream doctor` and confirm healthy
4. Open a PR — the template will guide you
5. One PR per concern; keep diffs focused

## Reporting issues

Use GitHub Issues with the bug report template. For ledger inaccuracies, always include:
- `slipstream report --json` output
- Your OS and Python version (`python3 --version`)
- `slipstream doctor` output

## Security issues

Do **not** use GitHub Issues for security vulnerabilities. See [SECURITY.md](SECURITY.md).

## Code of conduct

Be direct, be respectful, stay on topic. The goal is to give developers accurate token economics with zero friction — contributions that serve that goal are welcome.
