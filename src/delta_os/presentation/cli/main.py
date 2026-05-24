"""DELTA OS command line entry point."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from delta_os.application.agents import (
    AlertAgent,
    ConfigAgent,
    DataAgent,
    FusionAgent,
    LiquidityConceptsAgent,
    ProbabilityAgent,
    RankingAgent,
    RiskAgent,
    StructuralGeometryAgent,
    TimeframeIntelligenceAgent,
    UiAgent,
    UniverseAgent,
    VoiceAssistantAgent,
)
from delta_os.application.ports.data_provider import CandleDataProvider
from delta_os.application.dto.voice import VoiceCommandDTO
from delta_os.application.dto.ui import SidebarSectionDTO
from delta_os.application.use_cases import (
    LoadTradableUniverseUseCase,
    ProcessVoiceCommandUseCase,
    ScanCsvDatasetUseCase,
)
from delta_os.infrastructure.config import YamlConfigLoader
from delta_os.infrastructure.data import (
    CsvCandleProvider,
    LocalUniverseProvider,
    YahooFinanceCandleProvider,
)
from delta_os.presentation.cli.terminal_view import (
    render_profiles_summary,
    render_scan_result,
    render_universe_result,
    render_voice_result,
)


def main() -> None:
    """Run the CLI."""

    parser = argparse.ArgumentParser(prog="delta-os")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan", help="Run market scan")
    scan.add_argument("--config", type=Path, default=Path("configs/app.yaml"))
    scan.add_argument("--scan-profiles", type=Path, default=Path("configs/scan_profiles.yaml"))
    scan.add_argument("--csv", type=Path, default=None)
    scan.add_argument("--provider", choices=("csv", "yahoo_finance"), default=None)
    scan.add_argument("--symbol", default=None)
    scan.add_argument("--profile", default=None)
    scan.add_argument("--timeframe", default=None)
    scan.add_argument("--output", choices=("json", "terminal"), default="json")
    universe = subparsers.add_parser("universe", help="Load a local watchlist universe")
    universe.add_argument("--config", type=Path, default=Path("configs/app.yaml"))
    universe.add_argument("--file", type=Path, default=None)
    universe.add_argument("--name", default=None)
    universe.add_argument("--output", choices=("json", "terminal"), default="json")
    profiles = subparsers.add_parser("profiles", help="Summarize checked-in profile sets")
    profiles.add_argument("--kind", choices=("scan", "trade", "risk"), required=True)
    profiles.add_argument("--file", type=Path, default=None)
    profiles.add_argument("--output", choices=("json", "terminal"), default="json")
    voice = subparsers.add_parser("voice", help="Run a deterministic Phase-1 text command")
    voice.add_argument("--config", type=Path, default=Path("configs/app.yaml"))
    voice.add_argument("--scan-profiles", type=Path, default=Path("configs/scan_profiles.yaml"))
    voice.add_argument("--csv", type=Path, default=None)
    voice.add_argument("--provider", choices=("csv", "yahoo_finance"), default=None)
    voice.add_argument("--symbol", default=None)
    voice.add_argument("--profile", default=None)
    voice.add_argument("--timeframe", default=None)
    voice.add_argument("--text", required=True)
    voice.add_argument("--output", choices=("json", "terminal"), default="json")
    args = parser.parse_args()

    if args.command == "scan":
        config = YamlConfigLoader().load(args.config)
        scan_profiles = YamlConfigLoader().load(args.scan_profiles)
        trade_profiles = YamlConfigLoader().load(Path("configs/trade_profiles.yaml"))
        provider_name = args.provider or str(config["data"]["provider"])
        use_case = _build_use_case(
            config,
            scan_profiles=scan_profiles,
            trade_profiles=trade_profiles,
            data_provider_name=provider_name,
        )
        csv_path = _resolve_data_source_path(config, provider_name, args.csv)
        selected_profile = args.profile
        target_timeframes, default_analysis_timeframe = _resolve_scan_profile_timeframes(
            config,
            scan_profiles,
            selected_profile,
        )
        symbol = args.symbol or config["app"].get("default_symbol")
        analysis_timeframe = args.timeframe or default_analysis_timeframe
        try:
            result = use_case.run(
                csv_path=csv_path,
                symbol=symbol,
                target_timeframes=target_timeframes,
                analysis_timeframe=analysis_timeframe,
            )
        except Exception as exc:
            _emit_scan_error(
                args.output,
                provider_name=provider_name,
                symbol=symbol,
                analysis_timeframe=analysis_timeframe,
                error=exc,
            )
            return
        if args.output == "terminal":
            print(render_scan_result(result))
        else:
            print(json.dumps(result.to_dict(), indent=2))
    elif args.command == "universe":
        config = YamlConfigLoader().load(args.config)
        catalog_path = args.file or Path(config["universe"]["sample_watchlist_path"])
        universe_name = args.name or config["universe"]["default_universe"]
        result = _build_universe_use_case().run(catalog_path, universe_name)
        if args.output == "terminal":
            print(render_universe_result(result))
        else:
            print(json.dumps(result.to_dict(), indent=2))
    elif args.command == "profiles":
        result = _load_profile_summary(args.kind, args.file)
        if args.output == "terminal":
            print(render_profiles_summary(result))
        else:
            print(json.dumps(result, indent=2))
    elif args.command == "voice":
        config = YamlConfigLoader().load(args.config)
        scan_profiles = YamlConfigLoader().load(args.scan_profiles)
        trade_profiles = YamlConfigLoader().load(Path("configs/trade_profiles.yaml"))
        provider_name = args.provider or str(config["data"]["provider"])
        scan_use_case = _build_use_case(
            config,
            scan_profiles=scan_profiles,
            trade_profiles=trade_profiles,
            data_provider_name=provider_name,
        )
        voice_use_case = _build_voice_use_case()
        csv_path = _resolve_data_source_path(config, provider_name, args.csv)
        target_timeframes, default_analysis_timeframe = _resolve_scan_profile_timeframes(
            config,
            scan_profiles,
            args.profile,
        )
        symbol = args.symbol or config["app"].get("default_symbol")
        analysis_timeframe = args.timeframe or default_analysis_timeframe
        try:
            context = scan_use_case.run(
                csv_path=csv_path,
                symbol=symbol,
                target_timeframes=target_timeframes,
                analysis_timeframe=analysis_timeframe,
            )
        except Exception as exc:
            _emit_voice_error(
                args.output,
                provider_name=provider_name,
                symbol=symbol,
                analysis_timeframe=analysis_timeframe,
                text=args.text,
                error=exc,
            )
            return
        command = VoiceCommandDTO(
            raw_text=args.text,
            audio_source="text",
            timestamp=_build_timestamp_provider(config.get("agents", {}))() if config.get("agents", {}).get("deterministic_mode", False) else datetime.now(),
            user_context=("phase_1", str(config["app"]["mode"])),
            active_symbol=context.candles.symbol,
            active_timeframe=context.structure.timeframe,
        )
        result = voice_use_case.run(command, context)
        if args.output == "terminal":
            print(render_voice_result(result))
        else:
            print(json.dumps(result.to_dict(), indent=2))


def _build_use_case(
    config: dict[str, Any],
    *,
    scan_profiles: dict[str, Any] | None = None,
    trade_profiles: dict[str, Any] | None = None,
    risk_profiles: dict[str, Any] | None = None,
    data_provider_name: str | None = None,
) -> ScanCsvDatasetUseCase:
    scan_profiles = scan_profiles or YamlConfigLoader().load(Path("configs/scan_profiles.yaml"))
    trade_profiles = trade_profiles or YamlConfigLoader().load(Path("configs/trade_profiles.yaml"))
    risk_profiles = risk_profiles or YamlConfigLoader().load(Path("configs/risk_profiles.yaml"))
    agent_config = config.get("agents", {})
    structure_config = agent_config.get("structural_geometry", {})
    liquidity_config = agent_config.get("liquidity_concepts", {})
    probability_config = agent_config.get("probability", {})
    risk_config = agent_config.get("risk", {})

    resolved_provider_name = str(data_provider_name or config["data"]["provider"])
    data_provider = _build_market_data_provider(config, resolved_provider_name)
    data_agent = DataAgent(data_provider)
    return ScanCsvDatasetUseCase(
        data_agent=data_agent,
        structural_agent=StructuralGeometryAgent(
            swing_left=int(structure_config.get("swing_left", 2)),
            swing_right=int(structure_config.get("swing_right", 2)),
            compression_threshold=float(structure_config.get("compression_threshold", 0.85)),
        ),
        liquidity_agent=LiquidityConceptsAgent(
            sweep_lookback=int(liquidity_config.get("sweep_lookback", 3))
        ),
        probability_agent=ProbabilityAgent(
            breakout_base=float(probability_config.get("breakout_base", 0.35)),
            fakeout_base=float(probability_config.get("fakeout_base", 0.25)),
        ),
        risk_agent=RiskAgent(
            max_fakeout_probability=float(risk_config.get("max_fakeout_probability", 0.7)),
            min_breakout_probability=float(risk_config.get("min_breakout_probability", 0.25)),
        ),
        fusion_agent=FusionAgent(),
        ranking_agent=RankingAgent(),
        alert_agent=AlertAgent(_build_timestamp_provider(agent_config)),
        timeframe_agent=TimeframeIntelligenceAgent(),
        ui_agent=UiAgent(
            sidebar_sections=_build_sidebar_sections(config, scan_profiles, trade_profiles, risk_profiles),
            app_mode=str(config["app"]["mode"]),
            data_provider=resolved_provider_name,
            provider_health="ready",
            provider_profile_summary=_provider_profile_summary(config, resolved_provider_name),
        ),
    )


def _build_market_data_provider(
    config: dict[str, Any],
    data_provider_name: str | None = None,
) -> CandleDataProvider:
    source_timeframe = str(config["timeframes"]["source"])
    data_config = config.get("data", {})
    provider_name = str(data_provider_name or data_config.get("provider", "csv"))
    if provider_name == "csv":
        return CsvCandleProvider(source_timeframe)
    if provider_name == "yahoo_finance":
        yahoo_config = data_config.get("yahoo_finance", {})
        if not isinstance(yahoo_config, dict):
            yahoo_config = {}
        timeout_seconds = float(yahoo_config.get("request_timeout_seconds", 10.0))
        default_range = str(yahoo_config.get("range", "5d"))
        interval = str(yahoo_config.get("interval", source_timeframe))
        suffix = str(yahoo_config.get("symbol_suffix", ""))
        symbol_map_loaded = yahoo_config.get("symbol_map", {})
        symbol_map = (
            {str(key): str(value) for key, value in symbol_map_loaded.items()}
            if isinstance(symbol_map_loaded, dict)
            else {}
        )
        return YahooFinanceCandleProvider(
            source_timeframe=source_timeframe,
            request_timeout_seconds=timeout_seconds,
            default_range=default_range,
            default_interval=interval,
            symbol_suffix=suffix,
            symbol_map=symbol_map,
        )
    raise ValueError(f"Unsupported data.provider: {provider_name}")


def _resolve_data_source_path(
    app_config: dict[str, Any],
    provider_name: str,
    csv_override: Path | None,
) -> Path | None:
    if provider_name != "csv":
        return None
    if csv_override is not None:
        return csv_override
    return Path(str(app_config["data"]["sample_csv_path"]))


def _provider_profile_summary(app_config: dict[str, Any], provider_name: str) -> str:
    data_config = app_config.get("data", {})
    if provider_name != "yahoo_finance":
        return "default"
    yahoo = data_config.get("yahoo_finance", {})
    if not isinstance(yahoo, dict):
        return "yahoo_finance"
    interval = str(yahoo.get("interval", app_config["timeframes"]["source"]))
    period_range = str(yahoo.get("range", "5d"))
    timeout = float(yahoo.get("request_timeout_seconds", 10.0))
    return f"yahoo interval={interval} range={period_range} timeout={timeout:.1f}s"


def _emit_scan_error(
    output_mode: str,
    *,
    provider_name: str,
    symbol: str | None,
    analysis_timeframe: str,
    error: Exception,
) -> None:
    payload = {
        "command": "scan",
        "status": "error",
        "provider": provider_name,
        "symbol": symbol or "UNKNOWN",
        "analysis_timeframe": analysis_timeframe,
        "dashboard": {"provider_health": "down", "provider_note": "load_failed"},
        "error": {"type": type(error).__name__, "message": str(error)},
    }
    if output_mode == "terminal":
        print("DELTA OS :: MARKET SCAN ERROR")
        print("=" * 72)
        print(
            f"provider={provider_name} symbol={symbol or 'UNKNOWN'} timeframe={analysis_timeframe}"
        )
        print(f"error={type(error).__name__}: {error}")
        return
    print(json.dumps(payload, indent=2))


def _emit_voice_error(
    output_mode: str,
    *,
    provider_name: str,
    symbol: str | None,
    analysis_timeframe: str,
    text: str,
    error: Exception,
) -> None:
    payload = {
        "command": "voice",
        "status": "error",
        "provider": provider_name,
        "symbol": symbol or "UNKNOWN",
        "analysis_timeframe": analysis_timeframe,
        "response": {
            "spoken_text": "Data provider error. Scan context unavailable.",
            "display_title": "Data Provider Error",
            "display_body": "Scan context could not be loaded. Retry the command after data recovery.",
        },
        "audit": {"veto_state": "data_unavailable", "error_state": "scan_context_unavailable"},
        "input": {"text": text},
        "error": {"type": type(error).__name__, "message": str(error)},
    }
    if output_mode == "terminal":
        print("DELTA OS :: VOICE COMMAND ERROR")
        print("=" * 72)
        print(
            f"provider={provider_name} symbol={symbol or 'UNKNOWN'} timeframe={analysis_timeframe}"
        )
        print(f"user:  {text}")
        print("delta: Data provider error. Scan context unavailable.")
        print(f"error={type(error).__name__}: {error}")
        return
    print(json.dumps(payload, indent=2))


def _build_universe_use_case() -> LoadTradableUniverseUseCase:
    return LoadTradableUniverseUseCase(UniverseAgent(LocalUniverseProvider()))


def _build_voice_use_case() -> ProcessVoiceCommandUseCase:
    return ProcessVoiceCommandUseCase(VoiceAssistantAgent())


def _build_timestamp_provider(agent_config: dict[str, Any]):
    deterministic_mode = bool(agent_config.get("deterministic_mode", False))
    if not deterministic_mode:
        return None
    timestamp_value = agent_config["deterministic_alert_timestamp_utc"]
    fixed_timestamp = (
        timestamp_value
        if isinstance(timestamp_value, datetime)
        else datetime.fromisoformat(str(timestamp_value))
    )
    return lambda: fixed_timestamp


def _resolve_scan_profile_timeframes(
    app_config: dict[str, Any],
    scan_profiles: dict[str, Any],
    selected_profile: str | None,
) -> tuple[tuple[str, ...], str]:
    source_timeframe = str(app_config["timeframes"]["source"])
    enabled = tuple(str(item) for item in app_config["timeframes"].get("enabled", ()))
    fallback = tuple(dict.fromkeys((source_timeframe, *enabled)))
    if not selected_profile:
        return fallback, source_timeframe

    profiles = scan_profiles.get("profiles", {})
    profile_config = profiles.get(selected_profile)
    if not isinstance(profile_config, dict):
        return fallback, source_timeframe

    profile_timeframes = profile_config.get("timeframes", ())
    if not isinstance(profile_timeframes, list) or not profile_timeframes:
        return fallback, source_timeframe

    ordered = tuple(dict.fromkeys(str(item) for item in profile_timeframes))
    return ordered, ordered[-1]


def _build_sidebar_sections(
    app_config: dict[str, Any],
    scan_profiles: dict[str, Any] | None,
    trade_profiles: dict[str, Any] | None,
    risk_profiles: dict[str, Any] | None,
) -> tuple[SidebarSectionDTO, ...]:
    watchlists = _watchlist_names(app_config)
    universe_selection = _universe_selection_items(app_config)
    filters = _filter_items(app_config, scan_profiles, risk_profiles)
    scan_items = _scan_profile_sidebar_items(scan_profiles)
    trade_items = _trade_profile_sidebar_items(trade_profiles)
    risk_items = _risk_profile_sidebar_items(risk_profiles)
    return (
        SidebarSectionDTO("Watchlists", watchlists),
        SidebarSectionDTO("Universe Selection", universe_selection),
        SidebarSectionDTO("Filters", filters),
        SidebarSectionDTO("Scan Profiles", scan_items or ("compression_scanner [1d,4h,1h]",)),
        SidebarSectionDTO("Trade Profiles", trade_items or ("swing | ctx 1M/1W | exec 1h/15m",)),
        SidebarSectionDTO("Risk Profiles", risk_items or ("normal | fakeout<=0.70 | veto=on",)),
    )


def _profile_names(loaded: dict[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(loaded, dict):
        return ()
    profiles = loaded.get("profiles")
    if not isinstance(profiles, dict):
        return ()
    return tuple(str(key) for key in profiles.keys())


def _watchlist_names(app_config: dict[str, Any]) -> tuple[str, ...]:
    catalog = _load_universe_catalog(app_config)
    if not isinstance(catalog, dict):
        return ("nifty_50", "fno_stocks", "custom_watchlist")
    universes = catalog.get("universes", {})
    if not isinstance(universes, dict):
        return ("nifty_50", "fno_stocks", "custom_watchlist")
    return tuple(str(key) for key in universes.keys())


def _universe_selection_items(app_config: dict[str, Any]) -> tuple[str, ...]:
    catalog = _load_universe_catalog(app_config)
    universes = catalog.get("universes", {}) if isinstance(catalog, dict) else {}
    if not isinstance(universes, dict):
        return ("NIFTY 50 | mixed | 5",)
    items: list[str] = []
    for name, payload in universes.items():
        if not isinstance(payload, dict):
            continue
        display_name = str(payload.get("display_name", name))
        sector = str(payload.get("sector", "mixed"))
        symbols = payload.get("symbols", ())
        member_count = len(symbols) if isinstance(symbols, list) else 0
        items.append(f"{display_name} | {sector} | {member_count}")
    return tuple(items)


def _filter_items(
    app_config: dict[str, Any],
    scan_profiles: dict[str, Any] | None,
    risk_profiles: dict[str, Any] | None,
) -> tuple[str, ...]:
    timeframes = [str(app_config["timeframes"]["source"]), *[str(item) for item in app_config["timeframes"].get("enabled", ())]]
    default_universe = str(app_config["universe"].get("default_universe", "nifty_50"))
    scan_profile_count = len(_profile_names(scan_profiles))
    risk_profile_count = len(_profile_names(risk_profiles))
    return (
        f"default_universe={default_universe}",
        f"timeframes={','.join(dict.fromkeys(timeframes))}",
        f"scan_profiles={scan_profile_count}",
        f"risk_profiles={risk_profile_count}",
    )


def _scan_profile_sidebar_items(scan_profiles: dict[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(scan_profiles, dict):
        return ()
    profiles = scan_profiles.get("profiles", {})
    if not isinstance(profiles, dict):
        return ()
    items: list[str] = []
    for name, payload in profiles.items():
        if not isinstance(payload, dict):
            continue
        timeframes = ",".join(str(item) for item in payload.get("timeframes", ()))
        items.append(f"{name} [{timeframes}]")
    return tuple(items)


def _trade_profile_sidebar_items(trade_profiles: dict[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(trade_profiles, dict):
        return ()
    profiles = trade_profiles.get("profiles", {})
    if not isinstance(profiles, dict):
        return ()
    items: list[str] = []
    for name, payload in profiles.items():
        if not isinstance(payload, dict):
            continue
        context = "/".join(str(item) for item in payload.get("context_timeframes", ()))
        execution = "/".join(str(item) for item in payload.get("execution_timeframes", ()))
        items.append(f"{name} | ctx {context} | exec {execution}")
    return tuple(items)


def _risk_profile_sidebar_items(risk_profiles: dict[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(risk_profiles, dict):
        return ()
    profiles = risk_profiles.get("profiles", {})
    if not isinstance(profiles, dict):
        return ()
    items: list[str] = []
    for name, payload in profiles.items():
        if not isinstance(payload, dict):
            continue
        fakeout = float(payload.get("max_fakeout_probability", 0.0))
        veto = "on" if bool(payload.get("allow_risk_veto", False)) else "off"
        items.append(f"{name} | fakeout<={fakeout:.2f} | veto={veto}")
    return tuple(items)


def _load_universe_catalog(app_config: dict[str, Any]) -> dict[str, Any]:
    watchlist_path = Path(str(app_config["universe"]["sample_watchlist_path"]))
    loaded = YamlConfigLoader().load(watchlist_path)
    return loaded if isinstance(loaded, dict) else {}


def _load_profile_summary(kind: str, path: Path | None) -> dict[str, Any]:
    defaults = {
        "scan": Path("configs/scan_profiles.yaml"),
        "trade": Path("configs/trade_profiles.yaml"),
        "risk": Path("configs/risk_profiles.yaml"),
    }
    resolved = path or defaults[kind]
    loaded = ConfigAgent(YamlConfigLoader()).load(resolved)
    profiles = loaded.get("profiles", {})
    summary: list[dict[str, Any]] = []
    for name, profile in profiles.items():
        if kind == "scan":
            summary.append(
                {
                    "name": name,
                    "description": profile.get("description", ""),
                    "timeframes": tuple(profile.get("timeframes", ())),
                }
            )
        elif kind == "trade":
            summary.append(
                {
                    "name": name,
                    "context_timeframes": tuple(profile.get("context_timeframes", ())),
                    "setup_timeframes": tuple(profile.get("setup_timeframes", ())),
                    "execution_timeframes": tuple(profile.get("execution_timeframes", ())),
                }
            )
        else:
            summary.append(
                {
                    "name": name,
                    "max_fakeout_probability": profile.get("max_fakeout_probability"),
                    "min_breakout_probability": profile.get("min_breakout_probability"),
                    "allow_risk_veto": profile.get("allow_risk_veto"),
                }
            )
    return {"kind": kind, "source_path": resolved.as_posix(), "profiles": summary}


if __name__ == "__main__":
    main()
