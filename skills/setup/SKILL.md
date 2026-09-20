---
name: setup
description: First-time slipstream setup — configure window size and thresholds. Works in desktop, mobile, and CLI.
---

# /slipstream:setup

Walk the user through first-time slipstream configuration. Works on every surface — no terminal needed.

## How to run it

Ask the user three questions conversationally (don't dump them all at once):

1. **Window size** — "What's your rolling token window? Check your Claude plan — it's usually 1,000,000 tokens for Pro or 5× that for Team/Enterprise. Press Enter to keep the default of 1,000,000."

2. **Warn threshold** — "At what % burn do you want a heads-up? Default is 70%. This is when Slipstream will say 'you're getting low'."

3. **Critical threshold** — "At what % should I escalate to a critical warning? Default is 90%."

Once you have their answers, write the config:

**Try writing via CLI first:**

```bash
python3 - <<'SETUP'
import json, os
from pathlib import Path

xdg = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
cfg_dir = Path(f"{xdg}/slipstream")
cfg_dir.mkdir(parents=True, exist_ok=True)
cfg_path = cfg_dir / "config.json"

config = {
    "window_tokens": $WINDOW,
    "warn_threshold_pct": $WARN,
    "critical_threshold_pct": $CRITICAL
}

cfg_path.write_text(json.dumps(config, indent=2))
print(f"✅ Config written to {cfg_path}")
SETUP
```

(Replace `$WINDOW`, `$WARN`, `$CRITICAL` with the user's values.)

**If Bash is unavailable** (desktop/mobile), show the user exactly what to save:

> Here's your config. Save this to `~/.local/share/slipstream/config.json` (create the folder if it doesn't exist):
>
> ```json
> {
>   "window_tokens": 1000000,
>   "warn_threshold_pct": 70,
>   "critical_threshold_pct": 90
> }
> ```
>
> On Mac you can do this in Terminal:
> ```bash
> mkdir -p ~/.local/share/slipstream
> cat > ~/.local/share/slipstream/config.json <<'EOF'
> { "window_tokens": 1000000, "warn_threshold_pct": 70, "critical_threshold_pct": 90 }
> EOF
> ```
>
> The config takes effect immediately — no restart needed.

After setup, confirm: "No data ever leaves your machine. The ledger stays at `~/.local/share/slipstream/ledger.db` and is never uploaded."

Then offer to run `/slipstream:doctor` to confirm the installation is healthy.
