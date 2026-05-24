"""PySide6 dashboard skeleton.

The window renders DTO state only. Domain intelligence is computed by agents.
"""

from __future__ import annotations

import sys

from delta_os.application.dto.ui import (
    DashboardStateDTO,
    MultiTimeframeRowDTO,
    PanelSectionDTO,
    RankingRowDTO,
    SidebarSectionDTO,
    StatusItemDTO,
    VoiceStatusDTO,
)

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QListWidget,
        QMainWindow,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised only without GUI extra
    QApplication = None
    QMainWindow = object


if QApplication is not None:

    class DeltaMainWindow(QMainWindow):
        """DELTA OS Phase-1 dashboard shell."""

        def __init__(self, state: DashboardStateDTO) -> None:
            super().__init__()
            self.setWindowTitle("DELTA OS - Offline Structural Intelligence")
            self.resize(1560, 940)
            self._state = state
            self._apply_theme()
            self._build_layout()

        def _apply_theme(self) -> None:
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #0b1118;
                }
                QLabel#statusTitle {
                    color: #e6edf3;
                    font-size: 14px;
                    font-weight: 600;
                }
                QLabel#statusChip {
                    color: #b5c7d8;
                    background-color: #121c26;
                    border: 1px solid #223141;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 11px;
                }
                QFrame#panelFrame {
                    background-color: #0f1722;
                    border: 1px solid #223141;
                    border-radius: 6px;
                }
                QLabel#panelTitle {
                    color: #d8e4ef;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 4px 0 2px 0;
                }
                QListWidget, QTextEdit, QTableWidget {
                    background-color: #0a121b;
                    color: #c7d6e5;
                    border: 1px solid #1f2c3a;
                    border-radius: 4px;
                    selection-background-color: #1f3a52;
                    font-family: Consolas, "Cascadia Code", monospace;
                    font-size: 11px;
                }
                QTableWidget::item {
                    padding: 3px;
                }
                QHeaderView::section {
                    background-color: #121c26;
                    color: #d8e4ef;
                    border: none;
                    border-right: 1px solid #223141;
                    border-bottom: 1px solid #223141;
                    padding: 5px;
                    font-size: 11px;
                    font-weight: 600;
                }
                """
            )

        def _build_layout(self) -> None:
            root = QWidget()
            root_layout = QVBoxLayout(root)
            root_layout.setContentsMargins(10, 10, 10, 10)
            root_layout.setSpacing(8)

            status_bar = QFrame()
            status_layout = QHBoxLayout(status_bar)
            status_layout.setContentsMargins(8, 6, 8, 6)
            status_layout.setSpacing(6)
            title = QLabel(f"{self._state.symbol}  |  {self._state.status}")
            title.setObjectName("statusTitle")
            status_layout.addWidget(title)
            status_layout.addStretch(1)
            for item in status_item_values(self._state.status_items):
                chip = QLabel(item)
                chip.setObjectName("statusChip")
                status_layout.addWidget(chip)
            root_layout.addWidget(status_bar)

            top_split = QSplitter(Qt.Orientation.Horizontal)
            top_split.setChildrenCollapsible(False)

            sidebar_panel = self._panel("Universe / Profiles")
            sidebar = QListWidget()
            sidebar.addItems(sidebar_section_lines(self._state.sidebar_sections))
            sidebar_panel.layout().addWidget(sidebar)  # type: ignore[union-attr]
            top_split.addWidget(sidebar_panel)

            center_split = QSplitter(Qt.Orientation.Vertical)
            center_split.setChildrenCollapsible(False)
            chart_panel = self._panel("Chart / Structural Overlays")
            chart = QTextEdit()
            chart.setReadOnly(True)
            overlay_lines = build_overlay_lines(self._state)
            chart.setText("Market Structure Workspace\n\n" + "\n".join(overlay_lines))
            chart_panel.layout().addWidget(chart)  # type: ignore[union-attr]
            center_split.addWidget(chart_panel)

            table_panel = self._panel("Multi-Timeframe Intelligence")
            table = QTableWidget(len(self._state.timeframe_rows), 10)
            table.setHorizontalHeaderLabels(
                [
                    "Timeframe",
                    "Bias",
                    "Structure",
                    "Liquidity",
                    "Volatility",
                    "Breakout",
                    "Fakeout",
                    "Execution",
                    "Risk",
                    "Comment",
                ]
            )
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            for row_index, row in enumerate(self._state.timeframe_rows):
                values = timeframe_row_values(row)
                for column_index, value in enumerate(values):
                    table.setItem(row_index, column_index, QTableWidgetItem(value))
            table_panel.layout().addWidget(table)  # type: ignore[union-attr]
            center_split.addWidget(table_panel)
            top_split.addWidget(center_split)

            right_split = QSplitter(Qt.Orientation.Vertical)
            right_split.setChildrenCollapsible(False)
            intel_panel = self._panel("Intelligence Panel")
            right_panel = QTextEdit()
            right_panel.setReadOnly(True)
            right_panel.setText("\n\n".join(panel_section_lines(self._state.right_panel_sections)))
            intel_panel.layout().addWidget(right_panel)  # type: ignore[union-attr]
            right_split.addWidget(intel_panel)

            ranking_panel = self._panel("Ranking Dashboard")
            ranking = QTextEdit()
            ranking.setReadOnly(True)
            ranking.setText("\n".join(ranking_table_lines(self._state.ranking_rows)))
            ranking_panel.layout().addWidget(ranking)  # type: ignore[union-attr]
            right_split.addWidget(ranking_panel)
            top_split.addWidget(right_split)
            top_split.setSizes([260, 860, 440])
            root_layout.addWidget(top_split, 4)

            bottom_panel = self._panel("Voice / Alerts / Diagnostics")
            bottom = QTextEdit()
            bottom.setReadOnly(True)
            bottom.setText("\n".join(bottom_panel_lines(self._state)))
            bottom_panel.layout().addWidget(bottom)  # type: ignore[union-attr]
            root_layout.addWidget(bottom_panel, 2)
            self.setCentralWidget(root)

        def _panel(self, title: str) -> QFrame:
            frame = QFrame()
            frame.setObjectName("panelFrame")
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(8, 6, 8, 8)
            layout.setSpacing(6)
            label = QLabel(title)
            label.setObjectName("panelTitle")
            layout.addWidget(label)
            return frame

else:

    class DeltaMainWindow:  # type: ignore[no-redef]
        """Placeholder when the optional GUI dependency is not installed."""

        def __init__(self, state: DashboardStateDTO) -> None:
            raise RuntimeError("Install the gui extra to run the PySide6 dashboard")


def _default_voice_status() -> VoiceStatusDTO:
    return VoiceStatusDTO(
        state="idle",
        mode="text_stub",
        muted=False,
        last_intent="none",
        last_confidence=0.0,
        last_veto_state="clear",
    )


def main() -> None:
    """Launch a blank dashboard shell."""

    if QApplication is None:
        raise RuntimeError("Install the gui extra to run the PySide6 dashboard")
    app = QApplication(sys.argv)
    state = DashboardStateDTO(
        symbol="DEMO",
        status="CSV MODE ACTIVE",
        status_items=(),
        sidebar_sections=(),
        right_panel_sections=(),
        voice_status=_default_voice_status(),
        voice_transcript=(),
        overlays=(),
        timeframe_rows=(),
        ranking_rows=(),
        alerts=(),
        alert_timeline=(),
        scanner_activity=("no scan loaded",),
        diagnostics=("no scan loaded",),
    )
    window = DeltaMainWindow(state)
    window.show()
    sys.exit(app.exec())


def build_overlay_lines(state: DashboardStateDTO) -> list[str]:
    """Return display lines for chart overlays from DTO state only."""

    if not state.overlays:
        return ["(no overlays loaded)"]
    return [f"{item.label} | confidence={item.confidence:.2f} | points={item.points}" for item in state.overlays]


def timeframe_row_values(row: MultiTimeframeRowDTO) -> list[str]:
    """Return formatted table values for one multi-timeframe row."""

    return [
        row.timeframe,
        row.bias,
        row.structure,
        row.liquidity,
        row.volatility,
        f"{row.breakout_probability:.2f}",
        f"{row.fakeout_risk:.2f}",
        row.execution_quality,
        row.risk_state,
        row.comment,
    ]


def ranking_row_values(row: RankingRowDTO) -> list[str]:
    """Return formatted ranking-table values for one ranking row."""

    return [
        str(row.rank),
        row.symbol,
        row.timeframe,
        f"{row.score:.2f}",
        row.market_state,
        f"{row.breakout_probability:.2f}",
        f"{row.fakeout_probability:.2f}",
        row.risk_state,
        "veto" if row.risk_veto else "pass",
        row.comment,
    ]


def ranking_table_lines(rows: tuple[RankingRowDTO, ...]) -> list[str]:
    """Return formatted multi-row ranking lines from DTO state only."""

    return [" | ".join(ranking_row_values(row)) for row in rows]


def sidebar_section_lines(sections: tuple[SidebarSectionDTO, ...]) -> list[str]:
    """Return display lines for sidebar sections from DTO state only."""

    lines: list[str] = []
    for section in sections:
        lines.append(section.title)
        lines.extend(f"  - {item}" for item in section.items)
    return lines


def status_item_values(items: tuple[StatusItemDTO, ...]) -> list[str]:
    """Return formatted status-bar values from DTO state only."""

    return [f"{item.label}={item.value}" for item in items]


def panel_section_lines(sections: tuple[PanelSectionDTO, ...]) -> list[str]:
    """Return formatted right-panel lines from DTO state only."""

    lines: list[str] = []
    for section in sections:
        lines.append(section.title)
        lines.extend(f"  {item}" for item in section.lines)
    return lines


def bottom_panel_lines(state: DashboardStateDTO) -> list[str]:
    """Return grouped bottom-panel lines from DTO state only."""

    return [
        "Voice Status",
        *voice_status_lines(state),
        "",
        "Voice Transcript",
        *voice_transcript_lines(state),
        "",
        "Alerts",
        *state.alerts,
        "",
        "Alert Timeline",
        *state.alert_timeline,
        "",
        "Scanner Activity",
        *state.scanner_activity,
        "",
        "Diagnostics",
        *state.diagnostics,
    ]


def voice_status_lines(state: DashboardStateDTO) -> list[str]:
    """Return formatted voice-status lines from DTO state only."""

    return [
        f"state={state.voice_status.state}",
        f"mode={state.voice_status.mode}",
        f"muted={'on' if state.voice_status.muted else 'off'}",
        f"last_intent={state.voice_status.last_intent}",
        f"last_confidence={state.voice_status.last_confidence:.2f}",
        f"last_veto_state={state.voice_status.last_veto_state}",
    ]


def voice_transcript_lines(state: DashboardStateDTO) -> list[str]:
    """Return voice transcript lines from DTO state only."""

    if not state.voice_transcript:
        return ["(no transcript entries)"]
    return [
        (
            f"{item.timestamp} | {item.speaker} | {item.intent} | "
            f"conf={item.confidence:.2f} | veto={item.veto_state} | {item.text}"
        )
        for item in state.voice_transcript
    ]


# duplicate default voice status removed; entrypoint moved to file end


if __name__ == "__main__":
    main()
