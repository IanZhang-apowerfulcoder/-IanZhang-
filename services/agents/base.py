from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

@dataclass(frozen=True)
class AgentContext:
    workflow_run_id: str
    session_id: str
    organization_id: str
    learner_id: str
    correlation_id: str
    tools: Mapping[str, Any]

class AgentModule(ABC):
    name: str
    input_schema_path: str
    output_schema_path: str
    @abstractmethod
    async def run(self, input_payload: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        raise NotImplementedError
