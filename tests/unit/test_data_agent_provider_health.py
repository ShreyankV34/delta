from __future__ import annotations

from pathlib import Path

import pytest

from delta_os.application.agents.data_agent import DataAgent
from delta_os.infrastructure.data import CsvCandleProvider

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_candles.csv"


def test_data_agent_provider_health_ready_on_success() -> None:
    agent = DataAgent(CsvCandleProvider())
    bundle = agent.load(FIXTURE, "RELIANCE", ("1m",))

    assert bundle.symbol == "RELIANCE"
    assert agent.last_provider_health == "ready"
    assert agent.last_provider_note == "ok"


def test_data_agent_provider_health_down_on_failure(tmp_path: Path) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("timestamp,open\n2024-01-01 09:15:00,100\n", encoding="utf-8")
    agent = DataAgent(CsvCandleProvider())

    with pytest.raises(ValueError):
        agent.load(broken, "RELIANCE", ("1m",))

    assert agent.last_provider_health == "down"
    assert agent.last_provider_note == "load_failed"
