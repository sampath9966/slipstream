---
name: setup
description: First-time slipstream setup — configure window size, thresholds, and verify the installation.
---

Walk the user through slipstream initial setup.

1. Run `slipstream doctor` to check current state.
2. Ask the user for their usage window size (tokens per rolling period). Default is 1,000,000. They can find this in their Claude plan details.
3. Ask for warn threshold (default 70%) and critical threshold (default 90%).
4. Write a config file at `~/.local/share/slipstream/config.json`:

```json
{
  "window_tokens": <their value>,
  "warn_threshold_pct": <their value>,
  "critical_threshold_pct": <their value>
}
```

   Then set `SLIPSTREAM_CONFIG=~/.local/share/slipstream/config.json` in their shell profile, or tell them to set it.

5. Run `slipstream doctor` again to confirm healthy.

Tell the user: no data ever leaves their machine. The ledger is at `~/.local/share/slipstream/ledger.db` (or `$SLIPSTREAM_DB`) and is never uploaded anywhere.
