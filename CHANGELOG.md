# Changelog

All notable changes to Slipstream are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-09-19

### Added
- **`/slipstream:advisor`** — conversational burn advisor that works on Claude desktop, mobile, CLI, and remote containers without any terminal or CLI flags
- **`/slipstream:coach`** — ROI-ranked waste analysis with dollar amounts per file per week; inline "pin for me" action updates CLAUDE.md directly
- **`/slipstream:onboard`** — zero-friction first-run setup triggered by natural language ("install slipstream", "get started")
- **YAML frontmatter** (`name`, `description`) on all skill files — every skill now appears in the Claude slash command autocomplete picker
- **Three-tier execution fallback** on every skill: CLI → inline Python/SQLite → pure conversation; no surface is ever blocked
- **Repo-level session cache** (`.slipstream/last-session.json`) — written by Stop hook after every session, travels with the repo; skills read it first so any new container has data immediately
- **Dollar cost visibility** across report, advisor, and coach — token counts now paired with `$X.XX/week` figures
- **Auto-setup block** in every skill — silently creates `~/.local/share/slipstream/config.json` with smart defaults on first run, no questions asked
- **`PRIVACY.md`** — comprehensive privacy policy covering data collection, storage, GDPR/CCPA compliance, security disclosure

### Changed
- `skills/report/SKILL.md` — rewrote with four-source data waterfall and dollar cost breakdown
- `skills/doctor/SKILL.md` — added inline Python health check fallback; conversational path for no-shell surfaces
- `skills/setup/SKILL.md` — added conversational config-writing path with copy-paste instructions for mobile
- `skills/anchor/SKILL.md` — added inline anchor-block generation from conversation context
- `plugin.json` — corrected license field to `Apache-2.0`
- `LICENSE` — filled in copyright year and author

### Fixed
- Hooks args, queue list, redundant regex, CI branch trigger, test suite

---

## [0.1.0] — 2026-09-01

### Added
- Initial release: burn ledger, window-aware queue, compaction anchor, rule guard
- SQLite ledger at `~/.local/share/slipstream/ledger.db`
- `bin/slipstream` CLI engine (Python 3 stdlib only, no external packages)
- Stop, PostToolUse, PreCompact, PostCompact, PreToolUse hooks
- Skills: report, doctor, setup, queue, anchor, guard, decide
- In-session budget monitor with warn (70%) and critical (90%) thresholds
- Statusline fragment: `▒ 71% ~2.3h left`
- `slipstream report --json` for scripting
- `slipstream queue` with linear pacing governor
- Declarative guard rules via `.slipstream/rules.yaml`
- `python3 -m pytest tests/` test suite for ledger math and pacing governor
