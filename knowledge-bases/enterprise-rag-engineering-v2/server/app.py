from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from .retriever import BASE, DomainRetriever
from .adaptive_retriever import AdaptiveRetriever
from .router import plan_dict

app = FastAPI(title="Enterprise RAG Engineering Domain Pack API", version="2.0.0")
retriever = DomainRetriever()
adaptive = AdaptiveRetriever(retriever)
questions = json.loads((BASE / "data/question_bank.json").read_text(encoding="utf-8"))
tasks = json.loads((BASE / "data/task_bank.json").read_text(encoding="utf-8"))
node_map = {n["id"]: n for n in retriever.nodes}

class RetrievalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    retrieval_request_id: str
    knowledge_base_version_id: str
    query_text: str = Field(min_length=1)
    top_k: int = Field(ge=1, le=50)
    filters: dict[str, Any] = Field(default_factory=dict)

@app.get("/health")
def health() -> dict[str, Any]:
    return {"status":"ok","version":retriever.domain["version"],"chunk_count":len(retriever.chunks),"node_count":len(retriever.nodes)}

@app.get("/api/v1/domain")
def get_domain() -> dict[str, Any]:
    return retriever.domain

@app.get("/api/v1/content-layers")
def content_layers() -> dict[str, Any]:
    counts: dict[str, int] = {}
    for c in retriever.chunks:
        counts[c.get("content_status", "unknown")] = counts.get(c.get("content_status", "unknown"), 0) + 1
    return {"runtime_enabled": True, "layers": counts, "team_review_pending": sum(1 for c in retriever.chunks if c.get("review_status") == "pending_team_review")}

@app.get("/api/v1/review-queue")
def review_queue(status: str = "pending_team_review", limit: int = Query(100, ge=1, le=1000)) -> dict[str, Any]:
    pending = [c for c in retriever.chunks if c.get("review_status") == status]
    grouped: dict[str, dict[str, Any]] = {}
    for chunk in pending:
        node_id = chunk["knowledge_node_id"]
        item = grouped.setdefault(node_id, {
            "knowledge_node_id": node_id,
            "knowledge_node_name": node_map.get(node_id, {}).get("name", node_id),
            "content_status": chunk.get("content_status"),
            "review_status": status,
            "chunk_count": 0,
            "source_ids": set(),
        })
        item["chunk_count"] += 1
        item["source_ids"].update(chunk.get("source_ids", []))
    items = []
    for item in grouped.values():
        item["source_ids"] = sorted(item["source_ids"])
        items.append(item)
    items.sort(key=lambda x: (-x["chunk_count"], x["knowledge_node_id"]))
    return {"status": status, "total_nodes": len(items), "total_chunks": len(pending), "items": items[:limit]}

@app.get("/api/v1/knowledge/nodes")
def list_nodes(module_id: str | None = None, core_only: bool = False) -> list[dict[str, Any]]:
    values = retriever.nodes
    if module_id:
        values = [n for n in values if n["module_id"] == module_id]
    if core_only:
        values = [n for n in values if n["core"]]
    return values

@app.get("/api/v1/knowledge/nodes/{knowledge_node_id}")
def get_node(knowledge_node_id: str) -> dict[str, Any]:
    if knowledge_node_id not in node_map:
        raise HTTPException(404, "knowledge node not found")
    return node_map[knowledge_node_id]

@app.post("/api/v1/retrieval/plans")
def create_plan(body: RetrievalRequest) -> dict[str, Any]:
    return {"retrieval_plan_id": str(uuid.uuid4()), "retrieval_request_id": body.retrieval_request_id, **plan_dict(body.query_text, body.filters)}

@app.post("/api/v1/retrieval/search")
def compatible_search(body: RetrievalRequest) -> dict[str, Any]:
    try:
        return retriever.compatible_response(body.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/api/v1/retrieval/search:adaptive")
def adaptive_search(body: RetrievalRequest) -> dict[str, Any]:
    started = time.perf_counter()
    if body.knowledge_base_version_id != retriever.domain["knowledge_base_version_id"]:
        raise HTTPException(400, "knowledge_base_version_id is not active for this Domain Pack")
    result = adaptive.run(body.query_text, body.top_k, body.filters)
    return {"retrieval_request_id": body.retrieval_request_id, "knowledge_base_version_id": body.knowledge_base_version_id, "latency_ms": round((time.perf_counter()-started)*1000,3), **result}

@app.get("/api/v1/evidence/{evidence_id}")
def get_evidence(evidence_id: str) -> dict[str, Any]:
    item = retriever.evidence_map.get(evidence_id)
    if not item:
        raise HTTPException(404, "evidence not found")
    return item

@app.get("/api/v1/questions")
def list_questions(knowledge_node_id: str | None = None, difficulty_level: int | None = Query(None, ge=1, le=5)) -> list[dict[str, Any]]:
    result = questions
    if knowledge_node_id:
        result = [q for q in result if q["knowledge_node_id"] == knowledge_node_id]
    if difficulty_level:
        result = [q for q in result if q["difficulty_level"] == difficulty_level]
    return result

@app.get("/api/v1/tasks")
def list_tasks(knowledge_node_id: str | None = None) -> list[dict[str, Any]]:
    return tasks if not knowledge_node_id else [t for t in tasks if t["knowledge_node_id"] == knowledge_node_id or knowledge_node_id in t.get("related_knowledge_node_ids", [])]

@app.post("/api/v1/evaluations/retrieval")
def run_retrieval_evaluation() -> dict[str, Any]:
    from scripts.run_retrieval_eval import evaluate
    return evaluate(write_files=False)
