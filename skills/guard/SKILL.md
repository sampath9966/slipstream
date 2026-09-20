---
name: guard
description: Manage tool-use rules — view, add, or test guard rules that block unsafe commands. Works in desktop, mobile, and CLI.
---

# /slipstream:guard

Manage the rule guard (Module 4).

## Usage

```
/slipstream:guard
```

## What this skill does

The guard module intercepts tool calls via the `PreToolUse` hook and blocks
any that match rules declared in `.slipstream/rules.yaml`. Exit code 2 causes
Claude Code to show the block reason to the assistant before the tool runs.

## Commands

```bash
# Check a tool call against rules (called automatically by PreToolUse hook)
slipstream guard check --tool-name <name> --tool-input-json '<json>'

# Generate rules.yaml from CLAUDE.md constraints
slipstream guard init

# Show loaded rules
slipstream guard show
```

## rules.yaml format

```yaml
rules:
  - name: no-force-push
    match:
      tool: Bash
      command_contains: "push --force"
    action: block
    reason: "Force-push is not allowed. Use --force-with-lease or open a PR."

  - name: no-rm-rf-src
    match:
      tool: Bash
      command_contains: "rm -rf"
      path_prefix: "src/"
    action: block
    reason: "Destructive removal inside src/ requires manual confirmation."

  - name: warn-prod-deploy
    match:
      tool: Bash
      command_contains: "deploy --env prod"
    action: warn
    reason: "Production deploy detected — confirm this is intentional."
```

### Supported match keys

| Key | Description |
|-----|-------------|
| `tool` | Tool name (e.g. `Bash`, `Edit`, `Write`) |
| `command_contains` | Substring match on `command` input field |
| `path_prefix` | file_path / cwd starts with this prefix |

### Actions

| Action | Behaviour |
|--------|----------|
| `block` | Exit 2 — Claude Code surfaces the reason and does not run the tool |
| `warn`  | Log the violation; tool still runs |

## Initialising from CLAUDE.md

`slipstream guard init` reads the project's `CLAUDE.md`, extracts constraint
sentences (lines containing "never", "always", "do not", "must not"), and
produces a starter `rules.yaml`. Review and edit before committing.
