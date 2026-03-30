# I built an open-source tool to reverse-engineer Anthropic's opaque Claude usage limits

Anthropic doesn't publish what their usage percentages actually mean in tokens. If you're on Pro, Max 5x, or Max 20x, you have no way to know what "1%" of your weekly or session limit actually costs — or whether that number changed since last month.

Three times now, the same pattern:

1. Anthropic announces a generous temporary promotion (Christmas 2x, March off-peak 2x)
2. Baseline limits silently tighten during or immediately after the promotion
3. When users notice, complaints get attributed to "contrast effect" or "return to normal"

The March 2026 incident was the last straw for me. During the off-peak 2x promo (Mar 13-28), Anthropic simultaneously tightened peak-hour session limits. A $200/month Max subscriber posted screenshots showing session usage climbing from 52% to 68% to 91% within minutes. The explanation came days later — not as a blog post, but a tweet thread from one engineer: "about 7% of users would now hit limits they wouldn't have before."

**The problem isn't the limits. It's the opacity.** You can't plan around a number you can't see. You can't verify a promise you can't measure.

## ccmeter

I built [ccmeter](https://github.com/iteebz/ccmeter) — an open-source CLI that reads the same OAuth credentials Claude Code uses and polls Anthropic's usage API on a heartbeat. When your utilization percentage ticks up, it records the timestamp and the new value to a local sqlite database.

By cross-referencing those ticks against Claude Code's local JSONL session logs (which contain per-message token counts), you can calculate what 1% actually equals in tokens for each usage bucket. Track that number over time. If it shrinks, Anthropic tightened the cap.

**What it records**: bucket name, utilization percentage, timestamp, your subscription tier (read automatically from your credentials).

**What it doesn't touch**: no conversation content, no PII, no account identifiers. Everything stays local in `~/.ccmeter/meter.db`.

## Install and start collecting

```bash
pip install ccmeter
ccmeter poll
```

That's it. It polls every 2 minutes and only writes a row when something changes. Let it run in the background while you use Claude Code normally.

```bash
ccmeter history          # see what's been recorded
ccmeter calibrate        # see utilization tick windows
ccmeter status           # collection stats
```

## What I need from you

**Install it and start collecting.** The more people collecting data, the faster we can build a community picture of what these limits actually are — and detect when they change.

The long-term vision: optional anonymous contribution of calibration data (tier + bucket + tokens-per-percent-tick + timestamp) to a public dataset. No accounts, no PII. Just the numbers Anthropic won't publish.

If the caps are fair, the data will show it. If they're not, the data will show that too.

[GitHub](https://github.com/iteebz/ccmeter) | MIT Licensed

---

*Before anyone asks: yes, this uses the same OAuth token Claude Code stores in your OS keychain. It makes the same API call Claude Code makes. It doesn't bypass anything or violate ToS — it reads data Anthropic already exposes to your own client. The only difference is now you can see it too.*
