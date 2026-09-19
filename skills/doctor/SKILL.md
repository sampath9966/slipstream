---
name: doctor
description: Check slipstream installation health — hooks, DB, config, and service status.
---

Run the slipstream health check and show the results:

```
slipstream doctor
```

Show the full output. If there are errors, diagnose and fix them:

- "NOT executable": run `chmod +x <path to bin/slipstream>` and retry.
- "cannot open DB": check that the data directory is writable; the default is `~/.local/share/slipstream/`.
- "not set" for CLAUDE_PLUGIN_ROOT: this is expected outside a Claude Code session; the hooks won't run but the CLI still works.

After showing doctor output, summarize in one sentence whether slipstream is healthy.
