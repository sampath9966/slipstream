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
# Generate a starter rules.yaml from CLAUDE.md constraints
slipstream guard init [--force]

# Test a tool call against the rules (this is what the PreToolUse hook runs)
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force"},"cwd":"'"$PWD"'"}' \
  | slipstream guard-check; echo "exit=$?"
```

To show the loaded rules, read `.slipstream/rules.yaml` in the project root.

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
| `command_contains` | Case-insensitive substring match on the `command` input field |
| `command_regex` | Python regex searched in the `command` input field (single-quote it in YAML) |
| `path_prefix` | file_path / cwd starts with this prefix |

### Actions

| Action | Behaviour |
|--------|-----------|
| `block` | Exit 2 with the reason on stderr — Claude sees the reason and the tool does not run |
| `warn`  | Log the violation and show a warning to the user; the tool still runs |

All keys under `match` must match for a rule to fire. Set `enabled: "false"` on a rule to turn it off.

### Legacy check rules

`slipstream guard init` writes rules in the older check form: when a Bash command
contains `on`, the shell command in `check` runs in the project root and a non-zero
exit blocks the call with `message`. Both forms can live in the same file.

## Initialising from CLAUDE.md

`slipstream guard init` reads the project's `CLAUDE.md`, extracts constraint
sentences (lines containing "never", "always", "must", "do not", …) as comments, and
writes a starter `rules.yaml` with check rules disabled. Review and edit before committing.
