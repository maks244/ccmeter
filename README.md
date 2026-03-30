# ccmeter

Measure what Anthropic won't tell you: what your Claude subscription limits actually mean in tokens.

## Why

Anthropic charges $20-$200/month for Claude but doesn't publish what the usage limits actually are. The API reports utilization as a percentage — but a percentage of what? Nobody knows.

Twice in four months, Anthropic has run the same play: announce a temporary usage boost, silently tighten baseline limits during or after, then attribute complaints to "contrast effect." See [docs/evidence.md](docs/evidence.md) for the receipts.

ccmeter is a local instrument that figures out the actual numbers.

## How it works

1. Polls Anthropic's OAuth usage API every 2 minutes — records utilization percentages per bucket (`five_hour`, `seven_day`, `seven_day_sonnet`, etc.)
2. Scans Claude Code's local JSONL files for per-message token counts with timestamps
3. When utilization ticks from 15% to 16% and you used N tokens in that window: 1% = N tokens

That's the whole trick. Track that number over time. If it shrinks, the cap shrank.

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

One person's data is a sample. Hundreds of people's data is leverage.

The more users collecting data across different tiers (Pro, Max 5x, Max 20x) and models (Sonnet, Opus), the faster we can build a complete picture of what every plan actually gets you — and detect when it changes.

**Easiest way to help:** install it, let the daemon run, share your `ccmeter report` output.

**If you want to contribute code:** see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
