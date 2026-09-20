# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | ✅ Yes    |
| 0.1.x   | ❌ No — upgrade to 0.2.0 |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

Email **sampath@vmwareadmin.in** with subject line:

```
[SECURITY] Slipstream — <brief description>
```

Include:
- Description of the vulnerability and potential impact
- Steps to reproduce
- Affected version(s)
- Any suggested fix if you have one

**Response SLA:**
- Acknowledgement: within 2 business days
- Assessment and severity rating: within 5 business days
- Fix timeline communicated: within 10 business days

## Scope

Slipstream runs entirely locally with no network access. The meaningful attack surface is:

| Area | Notes |
|------|-------|
| **Transcript JSONL parsing** | Malformed JSONL in `~/.claude/projects/` could affect ledger accuracy |
| **SQLite ledger** | World-readable by default — report if a code path creates it with unsafe permissions |
| **Hook exit codes** | A hook returning exit code 2 blocks a Claude tool call — report if this can be triggered by crafted input |
| **`.slipstream/rules.yaml`** | Rule files are read from the repo; report if a crafted rule file can escape intended scope |
| **`bin/slipstream` CLI** | Report command injection, path traversal, or privilege escalation |

Out of scope: issues in Python stdlib, SQLite, or Claude Code itself (report those to Anthropic).

## Security design principles

- **No network access** — Slipstream never initiates outbound connections
- **No eval or exec on external input** — all rule matching uses string comparison, not code execution
- **Hooks exit cleanly on errors** — no hook blocks or crashes a Claude session on unexpected input
- **Files written with default OS permissions** — no world-writable paths created

## Disclosure policy

We follow coordinated disclosure. Once a fix is available, we will:
1. Release a patched version
2. Credit the reporter in CHANGELOG.md (unless anonymity is requested)
3. File a GitHub Security Advisory if the severity warrants it
