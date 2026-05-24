"""Schema validation for checked-in Phase-1 YAML configs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_APP_COLUMNS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
)


def validate_config_shape(path: Path, loaded: dict[str, Any]) -> dict[str, Any]:
    """Validate the config shape for known Phase-1 config files."""

    validators = {
        "app.yaml": _validate_app_config,
        "scan_profiles.yaml": _validate_profiles_root_config,
        "trade_profiles.yaml": _validate_profiles_root_config,
        "risk_profiles.yaml": _validate_profiles_root_config,
        "voice_profiles.yaml": _validate_voice_config,
    }
    validator = validators.get(path.name)
    if validator is None:
        return loaded
    validator(loaded, path)
    return loaded


def _validate_app_config(config: dict[str, Any], path: Path) -> None:
    _require_mapping(config, path, "root")
    for key in ("app", "data", "timeframes", "universe", "agents", "presentation"):
        _require_key(config, key, path, "root")
        _require_mapping(config[key], path, key)

    app = config["app"]
    _require_str(app, "name", path, "app")
    _require_str(app, "mode", path, "app")
    _require_str(app, "default_symbol", path, "app")
    _require_str(app, "default_profile", path, "app")

    data = config["data"]
    _require_str(data, "provider", path, "data")
    if data["provider"] not in {"csv", "yahoo_finance"}:
        raise ValueError(f"{path.name}: 'data.provider' must be one of: csv, yahoo_finance")
    _require_str(data, "sample_csv_path", path, "data")
    _require_str(data, "timestamp_timezone", path, "data")
    _require_list_of_strings(data, "required_columns", path, "data")
    if tuple(data["required_columns"]) != REQUIRED_APP_COLUMNS:
        raise ValueError(
            f"{path.name}: data.required_columns must match the Phase-1 OHLCV schema"
        )
    if "yahoo_finance" in data:
        _validate_yahoo_config(data["yahoo_finance"], path)

    timeframes = config["timeframes"]
    _require_str(timeframes, "source", path, "timeframes")
    _require_list_of_strings(timeframes, "enabled", path, "timeframes")
    if not timeframes["enabled"]:
        raise ValueError(f"{path.name}: timeframes.enabled must not be empty")

    universe = config["universe"]
    _require_str(universe, "provider", path, "universe")
    _require_str(universe, "sample_watchlist_path", path, "universe")
    _require_str(universe, "default_universe", path, "universe")

    agents = config["agents"]
    _require_bool(agents, "deterministic_mode", path, "agents")
    _require_key(agents, "deterministic_alert_timestamp_utc", path, "agents")
    _require_iso_datetime(
        agents["deterministic_alert_timestamp_utc"],
        path,
        "agents.deterministic_alert_timestamp_utc",
    )
    for key in ("structural_geometry", "liquidity_concepts", "probability", "risk"):
        _require_key(agents, key, path, "agents")
        _require_mapping(agents[key], path, f"agents.{key}")

    structural = agents["structural_geometry"]
    _require_int(structural, "swing_left", path, "agents.structural_geometry")
    _require_int(structural, "swing_right", path, "agents.structural_geometry")
    _require_number(structural, "compression_threshold", path, "agents.structural_geometry")

    liquidity = agents["liquidity_concepts"]
    _require_int(liquidity, "sweep_lookback", path, "agents.liquidity_concepts")

    probability = agents["probability"]
    _require_number(probability, "breakout_base", path, "agents.probability")
    _require_number(probability, "fakeout_base", path, "agents.probability")

    risk = agents["risk"]
    _require_number(risk, "max_fakeout_probability", path, "agents.risk")
    _require_number(risk, "min_breakout_probability", path, "agents.risk")

    presentation = config["presentation"]
    _require_str(presentation, "ui_mode", path, "presentation")
    _require_str(presentation, "theme", path, "presentation")

    if "live_data" in config:
        _validate_live_data_config(config["live_data"], path)
    if "execution" in config:
        _validate_execution_config(config["execution"], path)
    if "risk_limits" in config:
        _validate_risk_limits_config(config["risk_limits"], path)
    if "connectivity" in config:
        _validate_connectivity_config(config["connectivity"], path)
    if "latency_slo" in config:
        _validate_latency_slo_config(config["latency_slo"], path)
    _validate_live_mode_safety(config, path)


def _validate_profiles_root_config(config: dict[str, Any], path: Path) -> None:
    _require_mapping(config, path, "root")
    _require_key(config, "profiles", path, "root")
    profiles = config["profiles"]
    _require_mapping(profiles, path, "profiles")
    if not profiles:
        raise ValueError(f"{path.name}: profiles must not be empty")
    for profile_name, profile in profiles.items():
        if not isinstance(profile_name, str) or not profile_name:
            raise ValueError(f"{path.name}: profile names must be non-empty strings")
        _require_mapping(profile, path, f"profiles.{profile_name}")
        if path.name == "scan_profiles.yaml":
            _require_str(profile, "description", path, f"profiles.{profile_name}")
            _require_list_of_strings(profile, "timeframes", path, f"profiles.{profile_name}")
        elif path.name == "trade_profiles.yaml":
            _require_list_of_strings(profile, "context_timeframes", path, f"profiles.{profile_name}")
            _require_list_of_strings(profile, "setup_timeframes", path, f"profiles.{profile_name}")
            _require_list_of_strings(profile, "execution_timeframes", path, f"profiles.{profile_name}")
        elif path.name == "risk_profiles.yaml":
            _require_number(profile, "max_fakeout_probability", path, f"profiles.{profile_name}")
            _require_number(profile, "min_breakout_probability", path, f"profiles.{profile_name}")
            _require_bool(profile, "allow_risk_veto", path, f"profiles.{profile_name}")


def _validate_voice_config(config: dict[str, Any], path: Path) -> None:
    _require_mapping(config, path, "root")
    _require_key(config, "voice", path, "root")
    voice = config["voice"]
    _require_mapping(voice, path, "voice")
    _require_str(voice, "phase_1_mode", path, "voice")
    _require_bool(voice, "push_to_talk_enabled", path, "voice")
    _require_bool(voice, "wake_word_enabled", path, "voice")
    _require_bool(voice, "execution_commands_allowed", path, "voice")
    _require_bool(voice, "audit_log_enabled", path, "voice")


def _validate_yahoo_config(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: 'data.yahoo_finance' must be a mapping")
    _require_number(value, "request_timeout_seconds", path, "data.yahoo_finance")
    _require_str(value, "range", path, "data.yahoo_finance")
    _require_str(value, "interval", path, "data.yahoo_finance")
    _require_str(value, "symbol_suffix", path, "data.yahoo_finance")
    symbol_map = value.get("symbol_map")
    if symbol_map is not None and not isinstance(symbol_map, dict):
        raise ValueError(f"{path.name}: 'data.yahoo_finance.symbol_map' must be a mapping")
    if isinstance(symbol_map, dict):
        for key, mapped in symbol_map.items():
            if not isinstance(key, str) or not key:
                raise ValueError(
                    f"{path.name}: 'data.yahoo_finance.symbol_map' keys must be non-empty strings"
                )
            if not isinstance(mapped, str) or not mapped:
                raise ValueError(
                    f"{path.name}: 'data.yahoo_finance.symbol_map' values must be non-empty strings"
                )


def _validate_live_data_config(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: 'live_data' must be a mapping")
    _require_str(value, "stream_provider", path, "live_data")
    _require_list_of_strings(value, "symbols", path, "live_data")
    _require_str(value, "bootstrap_source", path, "live_data")
    _require_bool(value, "websocket_enabled", path, "live_data")


def _validate_execution_config(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: 'execution' must be a mapping")
    _require_bool(value, "enabled", path, "execution")
    _require_str(value, "mode", path, "execution")
    if value["mode"] not in {"replay", "paper", "live"}:
        raise ValueError(f"{path.name}: 'execution.mode' must be one of replay|paper|live")
    _require_str(value, "broker", path, "execution")
    _require_bool(value, "live_armed", path, "execution")
    _require_bool(value, "require_runtime_arming", path, "execution")
    _require_bool(value, "kill_switch_enabled", path, "execution")
    for key in ("account_id_env", "api_key_env", "api_secret_env"):
        _require_str(value, key, path, "execution")
        _require_env_ref(value[key], path, f"execution.{key}")


def _validate_risk_limits_config(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: 'risk_limits' must be a mapping")
    for key in (
        "max_order_notional",
        "max_position_notional",
        "max_daily_loss",
        "max_slippage_bps",
        "max_spread_bps",
    ):
        _require_number(value, key, path, "risk_limits")


def _validate_connectivity_config(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: 'connectivity' must be a mapping")
    _require_int(value, "heartbeat_max_age_ms", path, "connectivity")
    _require_key(value, "reconnect", path, "connectivity")
    reconnect = value["reconnect"]
    if not isinstance(reconnect, dict):
        raise ValueError(f"{path.name}: 'connectivity.reconnect' must be a mapping")
    for key in ("base_delay_ms", "max_delay_ms", "jitter_ms", "max_attempts"):
        _require_int(reconnect, key, path, "connectivity.reconnect")


def _validate_latency_slo_config(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: 'latency_slo' must be a mapping")
    _require_int(value, "end_to_end_target_ms", path, "latency_slo")
    _require_str(value, "breach_action", path, "latency_slo")


def _validate_live_mode_safety(config: dict[str, Any], path: Path) -> None:
    app_mode = str(config["app"]["mode"])
    if app_mode != "live":
        return
    execution = config.get("execution")
    risk_limits = config.get("risk_limits")
    if not isinstance(execution, dict):
        raise ValueError(f"{path.name}: live mode requires execution config")
    if not isinstance(risk_limits, dict):
        raise ValueError(f"{path.name}: live mode requires risk_limits config")
    if not bool(execution.get("enabled", False)):
        raise ValueError(f"{path.name}: live mode requires execution.enabled=true")
    if not bool(execution.get("kill_switch_enabled", False)):
        raise ValueError(f"{path.name}: live mode requires execution.kill_switch_enabled=true")


def _require_env_ref(value: str, path: Path, section: str) -> None:
    if not (value.startswith("${") and value.endswith("}")):
        raise ValueError(f"{path.name}: '{section}' must use env indirection like ${'{ENV_VAR}'}")


def _require_key(mapping: dict[str, Any], key: str, path: Path, section: str) -> None:
    if key not in mapping:
        raise ValueError(f"{path.name}: missing required key '{section}.{key}'")


def _require_mapping(value: Any, path: Path, section: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: '{section}' must be a mapping")


def _require_str(mapping: dict[str, Any], key: str, path: Path, section: str) -> None:
    _require_key(mapping, key, path, section)
    value = mapping[key]
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path.name}: '{section}.{key}' must be a non-empty string")


def _require_bool(mapping: dict[str, Any], key: str, path: Path, section: str) -> None:
    _require_key(mapping, key, path, section)
    if not isinstance(mapping[key], bool):
        raise ValueError(f"{path.name}: '{section}.{key}' must be a boolean")


def _require_int(mapping: dict[str, Any], key: str, path: Path, section: str) -> None:
    _require_key(mapping, key, path, section)
    value = mapping[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{path.name}: '{section}.{key}' must be an integer")


def _require_number(mapping: dict[str, Any], key: str, path: Path, section: str) -> None:
    _require_key(mapping, key, path, section)
    value = mapping[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{path.name}: '{section}.{key}' must be a number")


def _require_list_of_strings(
    mapping: dict[str, Any],
    key: str,
    path: Path,
    section: str,
) -> None:
    _require_key(mapping, key, path, section)
    value = mapping[key]
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{path.name}: '{section}.{key}' must be a non-empty list of strings")


def _require_iso_datetime(value: Any, path: Path, section: str) -> None:
    if isinstance(value, datetime):
        return
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{path.name}: '{section}' must be a non-empty ISO datetime string or datetime"
        )
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{path.name}: '{section}' must be a valid ISO datetime string") from exc
