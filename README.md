# ccmeter

Measure what Anthropic won't tell you: what your Claude subscription limits actually mean in tokens.

## Why

Anthropic charges $20-$200/month for Claude but won't say what the limits actually are. The API reports utilization as a percentage — but a percentage of *what*? Nobody knows.

Twice in four months, Anthropic announced temporary usage boosts, then silently tightened baseline limits after. When users complained, the response was "contrast effect." See [docs/evidence.md](docs/evidence.md) for the receipts.

Without hard numbers, users can't tell the difference between "I'm using more" and "they gave me less." ccmeter fixes that. If limits shrink, you'll see it — tokens-per-percent goes down, cost-per-percent goes down, and there's no way to hand-wave calibrated data.

One person's data is a sample. Hundreds of people's data is leverage.

## How it works

1. **Poll**: records utilization percentages from Anthropic's OAuth usage API every 2 minutes per bucket (`five_hour`, `seven_day`, etc.)
2. **Scan**: reads per-message token counts from Claude Code's local JSONL session logs
3. **Calibrate**: when utilization ticks from 15% to 16% and you used N tokens in that window — 1% = N tokens, 1% = $X at API rates

Track those numbers over time. If tokens-per-percent drops, the cap shrank. Cost-per-percent gives you the dollar value of what each plan actually buys — comparable across users regardless of cache hit ratio.

## Install

```bash
pip install ccmeter
```

Or clone and run directly:

```bash
git clone https://github.com/iteebz/ccmeter && cd ccmeter && uv sync
```

Requires Python 3.12+, Claude Code installed and signed in. macOS and Linux. Zero dependencies beyond [fncli](https://pypi.org/project/fncli/).

## Usage

```bash
# Install as background daemon (survives restarts)
ccmeter install

# Or run in foreground
ccmeter poll

# What does 1% actually cost?
ccmeter report

# Structured output for sharing
ccmeter report --json

# Raw usage tick history
ccmeter history

# Collection health
ccmeter status

# Remove daemon
ccmeter uninstall
```

## What it collects

**From Anthropic's API** (polled every 2 min, recorded on change):
- Utilization percentage per bucket
- Reset timestamps
- Your subscription tier (detected automatically from credentials)

**From Claude Code's local JSONL files** (scanned on `report`):
- Per-message token counts: input, output, cache_read, cache_create
- Timestamps, model, Claude Code version, session ID

**Everything stays local** in `~/.ccmeter/meter.db`. Your OAuth token is only sent to Anthropic's own API — the same call Claude Code already makes.

## Known confounds

- **Multi-surface usage**: claude.ai, Claude Code, and Cowork share limits but only Claude Code has local token logs. If you use multiple surfaces simultaneously, token counts will be inflated relative to the utilization tick.
- **1% granularity**: The API reports whole percentages only. More samples over longer periods = better accuracy.
- **Bucket overlap**: Some buckets may share underlying quotas in ways the API doesn't surface.

## Help

The more users collecting data across different tiers (Pro, Max 5x, Max 20x) and models (Sonnet, Opus), the faster we can detect when limits change and map what every plan actually gets you.

**Easiest way to help:** install it, let the daemon run, share your `ccmeter report` output.

**If you want to contribute code:** see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
