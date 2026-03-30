"""Contract tests for cost weighting — the headline metric."""

from ccmeter.report import PRICING, _cost_usd, _pricing_for


def test_known_models_resolve_to_pricing():
    """Every model prefix in PRICING must resolve via _pricing_for."""
    for model in PRICING:
        assert _pricing_for(model) is PRICING[model]


def test_unknown_model_falls_back_to_opus():
    """Unknown models default to opus pricing (most expensive = conservative)."""
    rates = _pricing_for("claude-unknown-99")
    assert rates is PRICING["claude-opus-4-6"]


def test_cost_usd_pure_input():
    """1M input tokens on opus = $5.00."""
    tokens = {"input": 1_000_000, "output": 0, "cache_read": 0, "cache_create": 0}
    assert _cost_usd(tokens, "claude-opus-4-6") == 5.00


def test_cost_usd_pure_output():
    """1M output tokens on opus = $25.00."""
    tokens = {"input": 0, "output": 1_000_000, "cache_read": 0, "cache_create": 0}
    assert _cost_usd(tokens, "claude-opus-4-6") == 25.00


def test_cost_usd_cache_read_is_cheap():
    """Cache reads are 10x cheaper than input. 1M cache_read on opus = $0.50."""
    tokens = {"input": 0, "output": 0, "cache_read": 1_000_000, "cache_create": 0}
    cost = _cost_usd(tokens, "claude-opus-4-6")
    assert cost == 0.50


def test_cache_read_ratio_matters():
    """A session that's 99% cache reads should cost ~10x less than raw input."""
    heavy_cache = {"input": 10_000, "output": 10_000, "cache_read": 1_000_000, "cache_create": 0}
    heavy_input = {"input": 1_000_000, "output": 10_000, "cache_read": 10_000, "cache_create": 0}
    cache_cost = _cost_usd(heavy_cache, "claude-opus-4-6")
    input_cost = _cost_usd(heavy_input, "claude-opus-4-6")
    assert input_cost > cache_cost * 5  # at least 5x more expensive


def test_sonnet_cheaper_than_opus():
    """Same token profile on sonnet must cost less than opus."""
    tokens = {"input": 100_000, "output": 50_000, "cache_read": 500_000, "cache_create": 10_000}
    opus_cost = _cost_usd(tokens, "claude-opus-4-6")
    sonnet_cost = _cost_usd(tokens, "claude-sonnet-4-6")
    assert sonnet_cost < opus_cost
