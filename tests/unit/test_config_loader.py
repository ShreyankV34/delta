from __future__ import annotations

from pathlib import Path

import pytest

from delta_os.infrastructure.config import YamlConfigLoader


def test_yaml_config_loader_reads_app_config() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))

    assert config["app"]["mode"] == "offline_csv"
    assert config["data"]["provider"] == "csv"
    assert "5m" in config["timeframes"]["enabled"]
    assert config["universe"]["provider"] == "local_watchlist_file"
    assert config["universe"]["default_universe"] == "nifty_50"
    assert config["app"]["default_profile"] == "compression_scanner"
    assert "yahoo_finance" in config["data"]
    assert "execution" in config
    assert config["execution"]["mode"] in {"replay", "paper", "live"}


def test_yaml_config_loader_validates_checked_in_profile_files() -> None:
    loader = YamlConfigLoader()

    scan_profiles = loader.load(Path("configs/scan_profiles.yaml"))
    trade_profiles = loader.load(Path("configs/trade_profiles.yaml"))
    risk_profiles = loader.load(Path("configs/risk_profiles.yaml"))
    voice_profiles = loader.load(Path("configs/voice_profiles.yaml"))

    assert "profiles" in scan_profiles
    assert "profiles" in trade_profiles
    assert "profiles" in risk_profiles
    assert "voice" in voice_profiles


def test_yaml_config_loader_rejects_missing_required_app_sections(tmp_path: Path) -> None:
    broken = tmp_path / "app.yaml"
    broken.write_text(
        "app:\n  name: DELTA OS\n  mode: offline_csv\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required key"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_profiles_shape(tmp_path: Path) -> None:
    broken = tmp_path / "scan_profiles.yaml"
    broken.write_text(
        "profiles:\n  compression_scanner: not_a_mapping\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must be a mapping"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_scan_profile_missing_timeframes(tmp_path: Path) -> None:
    broken = tmp_path / "scan_profiles.yaml"
    broken.write_text(
        "profiles:\n"
        "  compression_scanner:\n"
        "    description: Offline scan\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="timeframes"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_trade_profile_shape(tmp_path: Path) -> None:
    broken = tmp_path / "trade_profiles.yaml"
    broken.write_text(
        "profiles:\n"
        "  swing:\n"
        "    context_timeframes: [1M, 1W]\n"
        "    setup_timeframes: [1d, 4h]\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="execution_timeframes"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_risk_profile_shape(tmp_path: Path) -> None:
    broken = tmp_path / "risk_profiles.yaml"
    broken.write_text(
        "profiles:\n"
        "  normal:\n"
        "    max_fakeout_probability: 0.7\n"
        "    min_breakout_probability: 0.25\n"
        "    allow_risk_veto: maybe\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="allow_risk_veto"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_voice_flag_types(tmp_path: Path) -> None:
    broken = tmp_path / "voice_profiles.yaml"
    broken.write_text(
        "voice:\n"
        "  phase_1_mode: text_command_stub\n"
        "  push_to_talk_enabled: false\n"
        "  wake_word_enabled: false\n"
        "  execution_commands_allowed: nope\n"
        "  audit_log_enabled: true\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must be a boolean"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_data_provider(tmp_path: Path) -> None:
    broken = tmp_path / "app.yaml"
    broken.write_text(
        "app:\n"
        "  name: DELTA OS\n"
        "  mode: offline_csv\n"
        "  default_symbol: RELIANCE\n"
        "  default_profile: compression_scanner\n"
        "data:\n"
        "  provider: bad_provider\n"
        "  sample_csv_path: data/sample/reliance_1m.csv\n"
        "  timestamp_timezone: Asia/Kolkata\n"
        "  required_columns: [timestamp, open, high, low, close, volume, symbol]\n"
        "timeframes:\n"
        "  source: 1m\n"
        "  enabled: [5m]\n"
        "universe:\n"
        "  provider: local_watchlist_file\n"
        "  sample_watchlist_path: data/sample/watchlists.yaml\n"
        "  default_universe: nifty_50\n"
        "agents:\n"
        "  deterministic_mode: true\n"
        "  deterministic_alert_timestamp_utc: 2024-01-01T00:00:00+00:00\n"
        "  structural_geometry:\n"
        "    swing_left: 1\n"
        "    swing_right: 1\n"
        "    compression_threshold: 0.85\n"
        "  liquidity_concepts:\n"
        "    sweep_lookback: 3\n"
        "  probability:\n"
        "    breakout_base: 0.35\n"
        "    fakeout_base: 0.25\n"
        "  risk:\n"
        "    max_fakeout_probability: 0.7\n"
        "    min_breakout_probability: 0.25\n"
        "presentation:\n"
        "  ui_mode: pyqt_skeleton\n"
        "  theme: dark_professional\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="data.provider"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_invalid_yahoo_symbol_map(tmp_path: Path) -> None:
    broken = tmp_path / "app.yaml"
    broken.write_text(
        "app:\n"
        "  name: DELTA OS\n"
        "  mode: offline_csv\n"
        "  default_symbol: RELIANCE\n"
        "  default_profile: compression_scanner\n"
        "data:\n"
        "  provider: csv\n"
        "  sample_csv_path: data/sample/reliance_1m.csv\n"
        "  timestamp_timezone: Asia/Kolkata\n"
        "  required_columns: [timestamp, open, high, low, close, volume, symbol]\n"
        "  yahoo_finance:\n"
        "    request_timeout_seconds: 10\n"
        "    range: 5d\n"
        "    interval: 1m\n"
        "    symbol_suffix: .NS\n"
        "    symbol_map: bad\n"
        "timeframes:\n"
        "  source: 1m\n"
        "  enabled: [5m]\n"
        "universe:\n"
        "  provider: local_watchlist_file\n"
        "  sample_watchlist_path: data/sample/watchlists.yaml\n"
        "  default_universe: nifty_50\n"
        "agents:\n"
        "  deterministic_mode: true\n"
        "  deterministic_alert_timestamp_utc: 2024-01-01T00:00:00+00:00\n"
        "  structural_geometry:\n"
        "    swing_left: 1\n"
        "    swing_right: 1\n"
        "    compression_threshold: 0.85\n"
        "  liquidity_concepts:\n"
        "    sweep_lookback: 3\n"
        "  probability:\n"
        "    breakout_base: 0.35\n"
        "    fakeout_base: 0.25\n"
        "  risk:\n"
        "    max_fakeout_probability: 0.7\n"
        "    min_breakout_probability: 0.25\n"
        "presentation:\n"
        "  ui_mode: pyqt_skeleton\n"
        "  theme: dark_professional\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="symbol_map"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_non_env_secret_reference(tmp_path: Path) -> None:
    broken = tmp_path / "app.yaml"
    broken.write_text(
        Path("configs/app.yaml").read_text(encoding="utf-8").replace(
            "api_key_env: ${DELTA_API_KEY}",
            "api_key_env: plain_secret",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="env indirection"):
        YamlConfigLoader().load(broken)


def test_yaml_config_loader_rejects_live_mode_without_kill_switch(tmp_path: Path) -> None:
    raw = Path("configs/app.yaml").read_text(encoding="utf-8")
    raw = raw.replace("mode: offline_csv", "mode: live")
    raw = raw.replace("enabled: false", "enabled: true")
    raw = raw.replace("kill_switch_enabled: true", "kill_switch_enabled: false")
    broken = tmp_path / "app.yaml"
    broken.write_text(raw, encoding="utf-8")
    with pytest.raises(ValueError, match="kill_switch_enabled=true"):
        YamlConfigLoader().load(broken)
