from __future__ import annotations

import json
import sys
from pathlib import Path

import delta_os.infrastructure.data.yahoo_finance_candle_provider as yahoo_finance_candle_provider
from delta_os.infrastructure.config import YamlConfigLoader
from delta_os.presentation.cli.main import _build_use_case, _resolve_scan_profile_timeframes, main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLE_CSV = FIXTURES / "sample_candles.csv"


def _run_cli_json(monkeypatch, capsys, argv: list[str]) -> dict[str, object]:
    monkeypatch.setattr(sys, "argv", argv)
    main()
    captured = capsys.readouterr()
    return json.loads(captured.out)


def test_cli_scan_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--timeframe",
            "1m",
        ],
    )

    main()
    captured = capsys.readouterr()

    actual = json.loads(captured.out)
    expected = json.loads((FIXTURES / "scan_cli_output.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_scan_use_case_serialization_matches_cli_fixture() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    use_case = _build_use_case(config)
    source_timeframe = config["timeframes"]["source"]
    enabled = tuple(config["timeframes"]["enabled"])
    target_timeframes = tuple(dict.fromkeys((source_timeframe, *enabled)))

    result = use_case.run(
        csv_path=SAMPLE_CSV,
        symbol="RELIANCE",
        target_timeframes=target_timeframes,
        analysis_timeframe="1m",
    )

    expected = json.loads((FIXTURES / "scan_cli_output.json").read_text(encoding="utf-8"))

    assert result.to_dict() == expected


def test_ranking_payload_matches_fixture() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    use_case = _build_use_case(config)
    source_timeframe = config["timeframes"]["source"]
    enabled = tuple(config["timeframes"]["enabled"])
    target_timeframes = tuple(dict.fromkeys((source_timeframe, *enabled)))

    result = use_case.run(
        csv_path=SAMPLE_CSV,
        symbol="RELIANCE",
        target_timeframes=target_timeframes,
        analysis_timeframe="1m",
    )

    expected = json.loads((FIXTURES / "ranking_cli_output.json").read_text(encoding="utf-8"))

    assert result.ranking.to_dict() == expected


def test_cli_universe_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "delta-os",
            "universe",
            "--config",
            "configs/app.yaml",
            "--file",
            "data/sample/watchlists.yaml",
            "--name",
            "custom_watchlist",
        ],
    )

    main()
    captured = capsys.readouterr()

    actual = json.loads(captured.out)
    expected = json.loads((FIXTURES / "universe_cli_output.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_profile_driven_scan_cli_summary_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--profile",
            "compression_scanner",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
        ],
    )

    summary = {
        "profile": "compression_scanner",
        "analysis_timeframe": "1h",
        "result_timeframe": actual["structure"]["timeframe"],
        "target_timeframes": [item["timeframe"] for item in actual["candles"]["series"]],
        "alert_type": actual["alert"]["alert_type"],
        "alert_message": actual["alert"]["message"],
        "ranking_timeframe": actual["ranking"]["timeframe"],
        "dashboard_ranking_timeframe": actual["dashboard"]["ranking_rows"][0]["timeframe"],
        "dashboard_alert_timeline": actual["dashboard"]["alert_timeline"],
        "dashboard_scanner_activity": actual["dashboard"]["scanner_activity"],
    }
    expected = json.loads(
        (FIXTURES / "scan_profile_compression_summary.json").read_text(encoding="utf-8")
    )

    assert summary == expected


def test_scan_profile_override_and_fallback_summary_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    default_result = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
        ],
    )
    override_result = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--profile",
            "breakout_probability",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
        ],
    )
    unknown_result = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--profile",
            "unknown_profile",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
        ],
    )

    summary = {
        "default": {
            "analysis_timeframe": default_result["structure"]["timeframe"],
            "scanner_activity": default_result["dashboard"]["scanner_activity"],
        },
        "override": {
            "profile": "breakout_probability",
            "analysis_timeframe": override_result["structure"]["timeframe"],
            "scanner_activity": override_result["dashboard"]["scanner_activity"],
        },
        "unknown_profile_fallback": {
            "profile": "unknown_profile",
            "analysis_timeframe": unknown_result["structure"]["timeframe"],
            "scanner_activity": unknown_result["dashboard"]["scanner_activity"],
        },
    }
    expected = json.loads(
        (FIXTURES / "scan_profile_override_fallback_summary.json").read_text(encoding="utf-8")
    )

    assert summary == expected


def test_scan_profile_timeframes_resolve_from_profile_config() -> None:
    app_config = YamlConfigLoader().load(Path("configs/app.yaml"))
    scan_profiles = YamlConfigLoader().load(Path("configs/scan_profiles.yaml"))

    target_timeframes, analysis_timeframe = _resolve_scan_profile_timeframes(
        app_config,
        scan_profiles,
        "compression_scanner",
    )

    assert target_timeframes == ("1d", "4h", "1h")
    assert analysis_timeframe == "1h"


def test_trade_profiles_cli_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["delta-os", "profiles", "--kind", "trade"],
    )

    main()
    captured = capsys.readouterr()

    actual = json.loads(captured.out)
    expected = json.loads((FIXTURES / "trade_profiles_summary.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_scan_profiles_cli_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["delta-os", "profiles", "--kind", "scan"],
    )

    main()
    captured = capsys.readouterr()

    actual = json.loads(captured.out)
    expected = json.loads((FIXTURES / "scan_profiles_summary.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_risk_profiles_cli_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["delta-os", "profiles", "--kind", "risk"],
    )

    main()
    captured = capsys.readouterr()

    actual = json.loads(captured.out)
    expected = json.loads((FIXTURES / "risk_profiles_summary.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_voice_cli_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "voice",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--text",
            "Show top compression candidates.",
        ],
    )
    expected = json.loads((FIXTURES / "voice_cli_output.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_voice_cli_blocked_execution_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "voice",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--text",
            "Buy RELIANCE now.",
        ],
    )
    expected = json.loads(
        (FIXTURES / "voice_cli_blocked_execution_output.json").read_text(encoding="utf-8")
    )

    assert actual == expected


def test_voice_cli_alert_explanation_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "voice",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--text",
            "Explain alert.",
        ],
    )
    expected = json.loads(
        (FIXTURES / "voice_cli_alert_explanation_output.json").read_text(encoding="utf-8")
    )

    assert actual == expected


def test_voice_cli_mute_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "voice",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--text",
            "Mute voice responses.",
        ],
    )
    expected = json.loads((FIXTURES / "voice_cli_mute_output.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_cli_nifty50_universe_output_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "delta-os",
            "universe",
            "--config",
            "configs/app.yaml",
            "--file",
            "data/sample/watchlists.yaml",
            "--name",
            "nifty_50",
        ],
    )

    main()
    captured = capsys.readouterr()

    actual = json.loads(captured.out)
    expected = json.loads((FIXTURES / "universe_nifty50_cli_output.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_scan_cli_terminal_output_has_professional_summary(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--timeframe",
            "1m",
            "--output",
            "terminal",
        ],
    )

    main()
    captured = capsys.readouterr()
    output = captured.out

    assert "DELTA OS :: MARKET SCAN SUMMARY" in output
    assert "TOP INTELLIGENCE ROWS" in output
    assert '"symbol"' not in output


def test_voice_cli_terminal_output_has_professional_summary(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "delta-os",
            "voice",
            "--config",
            "configs/app.yaml",
            "--scan-profiles",
            "configs/scan_profiles.yaml",
            "--csv",
            str(SAMPLE_CSV),
            "--symbol",
            "RELIANCE",
            "--text",
            "Show top compression candidates.",
            "--output",
            "terminal",
        ],
    )

    main()
    captured = capsys.readouterr()
    output = captured.out

    assert "DELTA OS :: VOICE COMMAND RESULT" in output
    assert "VOICE STATE" in output
    assert "AUDIT HISTORY" in output
    assert "trader" in output
    assert '"command"' not in output


def test_cli_scan_supports_online_provider_with_mocked_transport(
    monkeypatch,
    capsys,
) -> None:
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1704090600, 1704090660, 1704090720, 1704090780, 1704090840],
                    "indicators": {
                        "quote": [
                            {
                                "open": [100.0, 100.5, 101.0, 101.2, 101.4],
                                "high": [101.0, 101.5, 101.8, 102.0, 102.2],
                                "low": [99.8, 100.2, 100.9, 101.0, 101.1],
                                "close": [100.7, 101.1, 101.4, 101.8, 102.0],
                                "volume": [1000, 1100, 1200, 1300, 1400],
                            }
                        ]
                    },
                }
            ]
        }
    }
    monkeypatch.setattr(yahoo_finance_candle_provider, "_http_get_json", lambda _u, _t: payload)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--provider",
            "yahoo_finance",
            "--symbol",
            "RELIANCE",
            "--timeframe",
            "1m",
        ],
    )

    main()
    captured = capsys.readouterr()
    actual = json.loads(captured.out)

    assert actual["candles"]["symbol"] == "RELIANCE"
    assert actual["candles"]["source_timeframe"] == "1m"
    status = {item["label"]: item["value"] for item in actual["dashboard"]["status_items"]}
    assert status["data_provider"] == "yahoo_finance"
    assert status["provider_health"] == "ready"


def test_cli_scan_online_timeout_error_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        yahoo_finance_candle_provider,
        "_http_get_json",
        lambda _u, _t: (_ for _ in ()).throw(TimeoutError("provider timeout")),
    )
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "scan",
            "--config",
            "configs/app.yaml",
            "--provider",
            "yahoo_finance",
            "--symbol",
            "RELIANCE",
            "--timeframe",
            "1m",
        ],
    )
    expected = json.loads(
        (FIXTURES / "scan_online_timeout_error_output.json").read_text(encoding="utf-8")
    )
    assert actual == expected


def test_cli_voice_online_timeout_error_matches_fixture(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        yahoo_finance_candle_provider,
        "_http_get_json",
        lambda _u, _t: (_ for _ in ()).throw(TimeoutError("provider timeout")),
    )
    actual = _run_cli_json(
        monkeypatch,
        capsys,
        [
            "delta-os",
            "voice",
            "--config",
            "configs/app.yaml",
            "--provider",
            "yahoo_finance",
            "--symbol",
            "RELIANCE",
            "--timeframe",
            "1m",
            "--text",
            "Show top compression candidates.",
        ],
    )
    expected = json.loads(
        (FIXTURES / "voice_online_timeout_error_output.json").read_text(encoding="utf-8")
    )
    assert actual == expected
