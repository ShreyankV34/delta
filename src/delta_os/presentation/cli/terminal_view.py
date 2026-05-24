"""Professional terminal renderers for Phase-1 CLI commands."""

from __future__ import annotations

from typing import Any

from delta_os.application.dto.scan import ScanResultDTO
from delta_os.application.dto.universe import TradableUniverseDTO
from delta_os.application.dto.voice import VoiceCommandResultDTO
from delta_os.application.use_cases import VoiceAuditHistoryProjection


def render_scan_result(result: ScanResultDTO) -> str:
    """Render a concise terminal summary for scan results."""

    lines = [
        "DELTA OS :: MARKET SCAN SUMMARY",
        "=" * 72,
        f"symbol={result.candles.symbol} timeframe={result.structure.timeframe} market_state={result.fusion.market_state}",
        f"prob_breakout={result.probability.breakout_probability:.2f} prob_fakeout={result.probability.fakeout_probability:.2f}",
        f"risk_state={result.risk.risk_state} veto={'on' if result.risk.veto else 'off'}",
        f"ranking_score={result.ranking.score:.2f} alert={result.alert.alert_type}",
        "",
        "TOP INTELLIGENCE ROWS",
    ]
    if not result.timeframe_intelligence:
        lines.append("  (none)")
    else:
        for row in result.timeframe_intelligence[:6]:
            lines.append(
                "  "
                + f"{row.timeframe:>4} | bias={row.bias:<8} | structure={row.structure_state:<12} | "
                + f"breakout={row.breakout_probability:.2f} fakeout={row.fakeout_probability:.2f} "
                + f"| risk={row.risk_state:<8} | exec={row.execution_quality}"
            )
    lines.extend(
        [
            "",
            "ALERT REASONING",
        ]
    )
    if result.alert.reasoning:
        for reason in result.alert.reasoning:
            lines.append(f"  - {reason}")
    else:
        lines.append("  - (none)")
    return "\n".join(lines)


def render_universe_result(result: TradableUniverseDTO) -> str:
    """Render a concise terminal summary for universe loading."""

    lines = [
        "DELTA OS :: UNIVERSE SUMMARY",
        "=" * 72,
        f"name={result.name} source={result.source_path} members={len(result.members)}",
        "",
        "MEMBERS",
    ]
    if not result.members:
        lines.append("  (none)")
    else:
        for member in result.members:
            lines.append(f"  - {member.symbol} | {member.sector} | weight={member.weight:.2f}")
    return "\n".join(lines)


def render_profiles_summary(summary: dict[str, Any]) -> str:
    """Render compact terminal output for profile summaries."""

    kind = str(summary.get("kind", "unknown"))
    source = str(summary.get("source_path", "unknown"))
    profiles = summary.get("profiles", [])
    lines = [
        f"DELTA OS :: {kind.upper()} PROFILE SUMMARY",
        "=" * 72,
        f"source={source} count={len(profiles) if isinstance(profiles, list) else 0}",
        "",
        "PROFILES",
    ]
    if not isinstance(profiles, list) or not profiles:
        lines.append("  (none)")
        return "\n".join(lines)
    for item in profiles:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "unknown"))
        fields = ", ".join(f"{key}={value}" for key, value in item.items() if key != "name")
        lines.append(f"  - {name}: {fields}")
    return "\n".join(lines)


def render_voice_result(result: VoiceCommandResultDTO) -> str:
    """Render command-and-response terminal output for voice command results."""

    audit_lines = VoiceAuditHistoryProjection().project(result)
    lines = [
        "DELTA OS :: VOICE COMMAND RESULT",
        "=" * 72,
        f"symbol={result.context_symbol} timeframe={result.context_timeframe} market_status={result.market_status}",
        f"intent={result.audit.parsed_intent.intent_name} confidence={result.audit.parsed_intent.confidence:.2f} veto={result.audit.veto_state}",
        "",
        f"user:  {result.command.raw_text}",
        f"delta: {result.response.spoken_text}",
        "",
        "VOICE STATE",
        f"  state={result.dashboard.voice_status.state}",
        f"  muted={'on' if result.dashboard.voice_status.muted else 'off'}",
        f"  last_intent={result.dashboard.voice_status.last_intent}",
        f"  transcript_entries={len(result.dashboard.voice_transcript)}",
        "",
        "AUDIT HISTORY",
        *[f"  {item}" for item in audit_lines],
    ]
    return "\n".join(lines)
