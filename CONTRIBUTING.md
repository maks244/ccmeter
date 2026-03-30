# Contributing

## Share your data

The most valuable contribution is just running ccmeter and sharing your report:

```bash
pip install ccmeter
ccmeter install
# wait a few days
ccmeter report
```

Post your `ccmeter report` output in a GitHub issue or discussion. Include your tier — the numbers mean different things on Pro vs Max 5x vs Max 20x.

Clean data comes from sessions where you're only using Claude Code (not claude.ai simultaneously).

## Contribute code

```bash
git clone https://github.com/iteebz/ccmeter
cd ccmeter
just install
```

`just format` before committing. `just lint` to check.

### What we need

- **More tiers**: ccmeter has only been tested on Max 20x. Pro and Max 5x users running it would immediately tell us how limits scale across plans.
- **Windows support**: auth.py needs a Windows Credential Manager backend.
- **Aggregation**: a way for users to submit anonymized calibration data (tier + model + bucket + tokens_per_pct) to a public dataset. No PII, no conversation content, no tokens. Just the numbers.
- **Better calibration math**: confidence intervals, outlier detection, weighted averages for mixed-model windows.
- **Visualization**: plots of tokens_per_pct over time per bucket. If the number drops, the cap shrank.

### Adding a migration

Schema changes go in `ccmeter/migrations/`. Create `NNN_description.py` with an `up(conn)` function. Never modify a shipped migration.

### Style

- fncli for CLI, not click/argparse
- stdlib over external deps
- print() for output
- Keep it simple. This is 400 lines of python. Let's keep it close to that.
