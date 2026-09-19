---
name: report
description: Show a burn report — token usage by session, tool, and file — for the current or recent sessions.
---

Run the slipstream burn report for the user.

Execute this command and show the output verbatim:

```
slipstream report $ARGUMENTS
```

If `$ARGUMENTS` contains `--json`, pipe through a JSON formatter.

If the command is not found, tell the user that the slipstream plugin's `bin/` directory may not be on PATH yet — they can run `slipstream doctor` manually from a terminal to diagnose, or restart their Claude Code session.

Common useful invocations:
- `/slipstream:report` — last 7 days
- `/slipstream:report --days 1` — today only
- `/slipstream:report --json` — machine-readable
- `/slipstream:report --session <id>` — one session

After showing the output, offer a one-line interpretation of the top finding (e.g. which file is being re-read the most).
