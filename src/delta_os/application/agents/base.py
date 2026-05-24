"""Shared agent protocol."""

from __future__ import annotations

from typing import Protocol, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class Agent(Protocol[InputDTO, OutputDTO]):
    """Protocol for replaceable application agents."""

    def run(self, payload: InputDTO) -> OutputDTO:
        """Run the agent."""
