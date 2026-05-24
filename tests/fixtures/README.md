# Phase-1 Fixtures

These fixtures are deterministic Phase-1 datasets and serialized outputs for
the offline CSV pipeline.

CSV geometry fixtures:

- `noisy_wedge.csv`: noisy but compressing upper/lower boundaries.
- `channel_like.csv`: parallel rising boundaries with strong angular similarity.
- `false_breakout_sweep.csv`: high sweep that closes back inside the prior range.
- `imperfect_trendline_respect.csv`: wedge-like structure with interior candles
  that deliberately do not sit perfectly on either boundary.

Serialized output fixtures:

- `ui_dashboard_state.json`: rendering-only dashboard DTO fixture.
- `scan_cli_output.json`: deterministic CLI scanner JSON output for the sample
  multi-timeframe offline scan path.
- `scan_profile_compression_summary.json`: deterministic profile-driven scan
  summary for the `compression_scanner` CLI variant.
- `ranking_cli_output.json`: deterministic ranking block extracted from the
  offline scan result.
- `trade_profiles_summary.json`: deterministic CLI summary for trade profiles.
- `risk_profiles_summary.json`: deterministic CLI summary for risk profiles.
- `universe_cli_output.json`: deterministic CLI universe-loading JSON output.
- `universe_nifty50_cli_output.json`: deterministic CLI universe-loading JSON
  output for a non-custom built-in watchlist.
- `universe_watchlist_summary.json`: deterministic summary projection for the
  normalized custom watchlist universe.

All fixtures use local data only. They must not depend on live feeds, broker
APIs, WebSockets, or external market services.
