# /slipstream:anchor

Manage the compaction anchor (Module 3).

## Usage

```
/slipstream:anchor
```

## What this skill does

The anchor module preserves continuity across Claude Code's automatic context
compaction. Before compaction fires (`PreCompact` hook) it snapshots:

- Key decisions extracted from the transcript (regex: "decided", "chose", "will", etc.)
- File hashes for the 20 most-recently touched files
- Active session metadata (session ID, timestamp, burn percentage)

After compaction fires (`PostCompact` hook) it re-injects a compact summary
(≤ 2 000 tokens) so Claude resumes with full situational awareness.

## Commands

```bash
# Manual snapshot (normally called by PreCompact hook)
slipstream anchor snapshot --session-id <id> --transcript-path <path>

# Manual inject (normally called by PostCompact hook)
slipstream anchor inject --session-id <id>

# Show current anchor for a session
slipstream anchor show --session-id <id>
```

## Snapshot format

The injected anchor block looks like:

```
=== SLIPSTREAM ANCHOR (restored after compaction) ===
Session: <id>  Captured: <ISO timestamp>  Burn: <pct>%

KEY DECISIONS
• <decision 1>
• <decision 2>
...

FILE STATE (sha256 prefix)
  /path/to/file.py  abc123
  ...
=== END ANCHOR ===
```

The block is kept under 2 000 tokens by truncating the decisions list and
abbreviating file paths with `~` for the home directory.
