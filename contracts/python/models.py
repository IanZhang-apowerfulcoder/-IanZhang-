from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
RetrievalStrategy = Literal["metadata_filtered","hybrid","graph_assisted","parent_child","agentic_decomposition"]
ExecutionMode = Literal["sequential","parallel","agentic","refuse"]
ReviewOutcome = Literal["pass","revise","reject","human_review"]
@dataclass(frozen=True)
class QueryAnalysis:
    query_type: str
    complexity: Literal["low","medium","high"]
    risk_level: Literal["low","medium","high"]
    execution_mode: ExecutionMode
    selected_strategies: list[RetrievalStrategy]
    reason_summary: str
@dataclass(frozen=True)
class WorkflowEvent:
    event_id: str
    sequence_no: int
    workflow_run_id: str
    session_id: str
    event_type: str
    payload: dict[str, Any]
    correlation_id: str
    created_at: str
