# Contributing to Slipstream

## Ground rules

- No telemetry additions, ever. Any code that phones home will be rejected.
- Stdlib-first. New dependencies need a strong justification.
- Tests for ledger math and the pacing governor (module 2) are mandatory — these are the two places a bug silently costs users money.

## Dev setup

```bash
git clone https://github.com/sampath9966/splitstream
cd splitstream
python3 -m pytest tests/ -v
```

No virtualenv required — stdlib + sqlite3 only for the core engine.

## Module status

- **Module 1 (ledger)**: shipped as v0.1.0, accepting bug fixes and parser improvements
- **Module 2 (queue)**: not yet started — see build brief
- **Module 3 (anchor)**: not yet started
- **Module 4 (guard)**: not yet started

## Submitting changes

1. Fork, branch from `main`
2. Tests must pass: `python3 -m pytest tests/ -v`
3. Run `slipstream doctor` and confirm healthy
4. Open a PR with a clear description of what changed and why

## Reporting issues

Use GitHub Issues. For ledger inaccuracies, include:
- `slipstream report --json` output
- The actual token count from `/context` or the Claude UI
- Your OS and Python version (`python3 --version`)
