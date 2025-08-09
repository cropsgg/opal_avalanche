from __future__ import annotations

from typing import Protocol, TypedDict, List, Dict, Any


class AgentOutput(TypedDict):
    reasoning: str
    sources: List[Dict[str, Any]]
    confidence: float


class Agent(Protocol):
    name: str

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput: ...  # noqa: E701


