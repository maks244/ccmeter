# ccmeter

Open-source CLI that reverse-engineers Anthropic's opaque Claude subscription usage limits into hard numbers.

## What this is

A local daemon that polls `api.anthropic.com/api/oauth/usage` (requires `anthropic-beta: oauth-2025-04-20` header), records utilization samples to sqlite when values change, and cross-references against Claude Code's local JSONL session logs to calculate what 1% of each usage bucket actually equals in tokens.

## Architecture

```
ccmeter/
  auth.py      — reads OAuth creds from OS keychain (macOS Keychain, Linux libsecret)
  cli.py       — fncli-based CLI: poll, history, calibrate, status
  db.py        — sqlite schema and connection (~/.ccmeter/meter.db)
  poll.py      — usage API poller with change detection and backoff
  history.py   — display recorded samples
  calibrate.py — cross-reference utilization ticks against token counts
  status.py    — collection stats
```

Zero external dependencies beyond `fncli`. Uses stdlib `urllib` for HTTP.

## Key facts

- OAuth token lives in OS keychain under service name `Claude Code-credentials`, key `claudeAiOauth`
- The credential blob contains `subscriptionType` and `rateLimitTier` — tier detection is automatic
- Usage API returns integer-precision utilization percentages per bucket
- Known buckets: `five_hour`, `seven_day`, `seven_day_sonnet`, `seven_day_opus`, `seven_day_cowork`, `extra_usage`
- Null buckets (like `iguana_necktie`) are feature flags for future limits — we capture everything the API returns
- `extra_usage` uses `used_credits` instead of `utilization`
- Claude Code JSONL session logs: `~/.claude/projects/<project>/<session_id>.jsonl`
- Session metadata with token counts: `~/.claude/usage-data/session-meta/<session_id>.json` (tokens in thousands)
- Per-message token counts available in JSONL assistant messages under `.message.usage`

## Conventions

- fncli for CLI, not click/argparse
- stdlib over deps (urllib not httpx)
- sqlite for local storage
- print() for CLI output
- Deferred imports in CLI handlers for fast startup
- Ruff for lint+format (`just format`, `just lint`)

## Roadmap

- [ ] JSONL session parser — read per-message token counts from `~/.claude/projects/`
- [ ] Session correlation — match usage ticks against session token windows
- [ ] Full calibration — tokens-per-percent calculation with confidence intervals
- [ ] Anonymous contribution — export/submit calibration data points
- [ ] Community dataset — public aggregated data repo
- [ ] Windows support — Windows Credential Manager for auth
- [ ] Background daemon mode (launchd/systemd)
