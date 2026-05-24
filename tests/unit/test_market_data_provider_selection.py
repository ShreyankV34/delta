from __future__ import annotations

from pathlib import Path

import pytest

from delta_os.infrastructure.config import YamlConfigLoader
from delta_os.infrastructure.data import CsvCandleProvider, YahooFinanceCandleProvider
from delta_os.presentation.cli.main import (
    _build_market_data_provider,
    _provider_profile_summary,
    _resolve_data_source_path,
)


def test_build_market_data_provider_defaults_to_csv_from_config() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    provider = _build_market_data_provider(config)
    assert isinstance(provider, CsvCandleProvider)


def test_build_market_data_provider_supports_yahoo_override() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    provider = _build_market_data_provider(config, data_provider_name="yahoo_finance")
    assert isinstance(provider, YahooFinanceCandleProvider)


def test_build_market_data_provider_rejects_unknown_provider() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    with pytest.raises(ValueError, match="Unsupported data.provider"):
        _build_market_data_provider(config, data_provider_name="unknown")


def test_resolve_data_source_path_returns_none_for_online_provider() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    assert _resolve_data_source_path(config, "yahoo_finance", None) is None


def test_resolve_data_source_path_uses_config_default_for_csv() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    path = _resolve_data_source_path(config, "csv", None)
    assert path is not None
    assert path.as_posix() == "data/sample/reliance_1m.csv"


def test_provider_profile_summary_reflects_yahoo_settings() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    summary = _provider_profile_summary(config, "yahoo_finance")
    assert summary == "yahoo interval=1m range=5d timeout=10.0s"
