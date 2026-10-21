---
name: anchor
description: Snapshot your session context before compaction — or recover it after. Works in desktop, mobile, and CLI with no terminal needed.
---

# /slipstream:anchor

Manage the compaction anchor — snapshot context before it's lost. Works in desktop, mobile, and CLI.

## Usage

```
/slipstream:anchor
```

Or say: "Snapshot my context" / "Save my progress before compaction"

## How to run it

**Try the CLI first:**

```bash
slipstream anchor $ARGUMENTS
```

**If the CLI is not found or Bash is unavailable** (desktop/mobile), produce the anchor inline:

When the user asks to snapshot their context, generate an anchor block directly from the current conversation — no file system access needed:

```
=== SLIPSTREAM ANCHOR ===
Captured: <current timestamp>

KEY DECISIONS
• <extract 5–10 decisions from the conversation: things decided, chosen, ruled out>

CURRENT TASK
<one sentence: what we are in the middle of right now>

FILES IN PLAY
<list any file paths mentioned or edited in this session>

NEXT STEPS
• <the immediate next action we were about to take>
• <any pending items the user mentioned>

CONTEXT NOTES
<any constraints, rules, or preferences the user stated>
=== END ANCHOR ===
```

Tell the user: "Paste this block at the start of your next session's first message and I'll pick up exactly where we left off."

## Manual CLI commands (for terminal users)

```bash
# Show the latest saved anchor (most recent session, or a specific one)
slipstream anchor
slipstream anchor --session-id <id>
```

## What the anchor block is used for

The `PreCompact` hook runs `slipstream anchor-snapshot` automatically before Claude Code compacts the context. After compaction, a `SessionStart` hook (matcher `compact`) runs `slipstream anchor-inject`, which adds the saved summary back into Claude's context.

On desktop/mobile where hooks aren't available, you can trigger the same effect manually: ask me "save my anchor" at any point and I'll produce the block above. Paste it into the next session to restore context.
