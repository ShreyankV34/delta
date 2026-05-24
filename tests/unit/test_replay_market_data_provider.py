from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.dto.live_market import MarketTickDTO
from delta_os.infrastructure.live import ReplayMarketDataProvider


def _tick(symbol: str, sequence: int, last: float) -> MarketTickDTO:
    return MarketTickDTO(
        symbol=symbol,
        timestamp=datetime.now(tz=UTC),
        bid=last - 0.1,
        ask=last + 0.1,
        last=last,
        size=100.0,
        sequence=sequence,
        venue="NSE",
    )


def test_replay_provider_filters_by_subscription() -> None:
    provider = ReplayMarketDataProvider(
        provider_name="replay",
        bootstrap_by_symbol={"RELIANCE": (_tick("RELIANCE", 1, 100.0), None)},
        events=(_tick("RELIANCE", 2, 101.0), _tick("TCS", 1, 3500.0)),
    )
    provider.subscribe(("RELIANCE",))
    events = provider.poll_events(max_events=10)
    assert len(events) == 1
    assert events[0].symbol == "RELIANCE"


def test_replay_provider_bootstrap_missing_symbol_raises() -> None:
    provider = ReplayMarketDataProvider(
        provider_name="replay",
        bootstrap_by_symbol={"RELIANCE": (_tick("RELIANCE", 1, 100.0), None)},
        events=(),
    )
    try:
        provider.bootstrap_snapshot("TCS")
    except KeyError as exc:
        assert "TCS" in str(exc)
    else:
        raise AssertionError("Expected KeyError for missing symbol")

