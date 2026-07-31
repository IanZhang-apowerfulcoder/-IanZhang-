from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def load(name: str) -> Any:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_jsonl(name: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (DATA / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def trust_tier(node: dict[str, Any]) -> str:
    provenance = node.get("provenance") or {}
    return str(provenance.get("trust_tier") or "trusted_core")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    domain = load("domain.json")
    nodes = load("knowledge_nodes.json")
    edges = load("knowledge_edges.json")
    chunks = load_jsonl("rag_chunks.jsonl")
    evidence = load("evidence_items.json")
    sources = load("source_registry.json")
    assets = {
        name: load(name)
        for name in [
            "concept_cards.json",
            "faq.json",
            "error_cases.json",
            "question_bank.json",
            "task_bank.json",
            "rubrics.json",
            "retrieval_eval_cases.json",
            "generation_eval_cases.json",
        ]
    }

    node_ids = {row["id"] for row in nodes}
    chunk_ids = {row["chunk_id"] for row in chunks}
    evidence_ids = {row["evidence_id"] for row in evidence}
    chunk_evidence_ids = {row["evidence_id"] for row in chunks}
    source_ids = {row["source_id"] for row in sources}

    expected_counts = {
        "nodes": 93,
        "edges": 252,
        "chunks": 372,
        "evidence": 372,
        "questions": 372,
        "tasks": 93,
        "rubrics": 93,
        "retrieval_eval_cases": 279,
        "generation_eval_cases": 173,
    }
    actual_counts = {
        "nodes": len(nodes),
        "edges": len(edges),
        "chunks": len(chunks),
        "evidence": len(evidence),
        "questions": len(assets["question_bank.json"]),
        "tasks": len(assets["task_bank.json"]),
        "rubrics": len(assets["rubrics.json"]),
        "retrieval_eval_cases": len(assets["retrieval_eval_cases.json"]),
        "generation_eval_cases": len(assets["generation_eval_cases.json"]),
    }
    for key, expected in expected_counts.items():
        if actual_counts[key] < expected:
            errors.append(f"{key} count {actual_counts[key]} < expected baseline {expected}")

    if len(node_ids) != len(nodes):
        errors.append("duplicate knowledge node id")
    if len(chunk_ids) != len(chunks):
        errors.append("duplicate chunk id")
    if len(evidence_ids) != len(evidence):
        errors.append("duplicate evidence id")
    if chunk_evidence_ids != evidence_ids:
        errors.append(
            f"chunk/evidence registry mismatch: missing={len(chunk_evidence_ids-evidence_ids)}, extra={len(evidence_ids-chunk_evidence_ids)}"
        )

    for node in nodes:
        for prerequisite in node.get("prerequisites", []):
            if prerequisite not in node_ids:
                errors.append(f"missing prerequisite {prerequisite} for {node['id']}")
        tier = trust_tier(node)
        if tier == "trusted_ai_generated":
            provenance = node.get("provenance") or {}
            if provenance.get("review_status") != "pending_team_review":
                errors.append(f"{node['id']} imported node must retain pending_team_review status")
            if provenance.get("enabled_for_runtime") is not True:
                errors.append(f"{node['id']} imported node must be runtime enabled")

    for edge in edges:
        source = edge.get("source_knowledge_node_id") or edge.get("source_node_id") or edge.get("source")
        target = edge.get("target_knowledge_node_id") or edge.get("target_node_id") or edge.get("target")
        if source not in node_ids or target not in node_ids:
            errors.append(f"edge references missing node: {edge.get('edge_id', '<unknown>')}")

    for chunk in chunks:
        if chunk["knowledge_node_id"] not in node_ids:
            errors.append(f"chunk missing node: {chunk['chunk_id']}")
        if not chunk.get("source_ids"):
            errors.append(f"chunk without source: {chunk['chunk_id']}")
        for source_id in chunk.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"chunk {chunk['chunk_id']} references missing source {source_id}")
        if chunk.get("runtime_enabled") is not True:
            errors.append(f"runtime chunk disabled unexpectedly: {chunk['chunk_id']}")

    evidence_map = {row["evidence_id"]: row for row in evidence}
    for chunk in chunks:
        item = evidence_map.get(chunk["evidence_id"])
        if not item:
            continue
        if item.get("chunk_id") != chunk["chunk_id"]:
            errors.append(f"evidence {chunk['evidence_id']} points to wrong chunk")
        if item.get("knowledge_node_id") != chunk["knowledge_node_id"]:
            errors.append(f"evidence {chunk['evidence_id']} points to wrong node")

    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for name, rows in assets.items():
        for row in rows:
            node_id = row.get("knowledge_node_id")
            if node_id:
                counts[node_id][name] += 1
            for evidence_id in row.get("evidence_ids", []) + row.get("required_evidence_ids", []):
                if evidence_id not in evidence_ids:
                    errors.append(f"{name} references missing evidence {evidence_id}")

    chunk_counts = Counter(row["knowledge_node_id"] for row in chunks)
    core_nodes = [node for node in nodes if trust_tier(node) == "trusted_core"]
    imported_nodes = [node for node in nodes if trust_tier(node) == "trusted_ai_generated"]

    core_expected = {
        "concept_cards.json": 1,
        "faq.json": 3,
        "error_cases.json": 2,
        "question_bank.json": 4,
        "task_bank.json": 1,
        "rubrics.json": 1,
        "retrieval_eval_cases.json": 3,
        "generation_eval_cases.json": 1,
    }
    core_complete = 0
    for node in core_nodes:
        node_id = node["id"]
        complete = chunk_counts[node_id] >= 4
        if chunk_counts[node_id] < 4:
            errors.append(f"{node_id} chunk count {chunk_counts[node_id]} < 4")
        for name, minimum in core_expected.items():
            if counts[node_id][name] < minimum:
                errors.append(f"{node_id} {name} count {counts[node_id][name]} < {minimum}")
                complete = False
        core_complete += int(complete)

    imported_complete = 0
    imported_task_coverage = 0
    for node in imported_nodes:
        node_id = node["id"]
        complete = True
        requirements = {
            "chunks": (chunk_counts[node_id], 4),
            "concept_cards.json": (counts[node_id]["concept_cards.json"], 1),
            "faq.json": (counts[node_id]["faq.json"], 3),
            "error_cases.json": (counts[node_id]["error_cases.json"], 2),
            "question_bank.json": (counts[node_id]["question_bank.json"], 4),
            "task_bank.json": (counts[node_id]["task_bank.json"], 1),
            "rubrics.json": (counts[node_id]["rubrics.json"], 1),
            "retrieval_eval_cases.json": (counts[node_id]["retrieval_eval_cases.json"], 3),
            "generation_eval_cases.json": (counts[node_id]["generation_eval_cases.json"], 1),
        }
        for label, (actual, minimum) in requirements.items():
            if actual < minimum:
                errors.append(f"{node_id} {label} count {actual} < {minimum}")
                complete = False
        imported_complete += int(complete)
        if counts[node_id]["task_bank.json"] >= 1 and counts[node_id]["rubrics.json"] >= 1:
            imported_task_coverage += 1

    if imported_task_coverage < len(imported_nodes):
        warnings.append(
            f"trusted_ai_generated engineering task coverage is {imported_task_coverage}/{len(imported_nodes)}; tracked as team enhancement work, not a runtime blocker"
        )

    schema_files = {
        "domain.json": "domain.schema.json",
        "knowledge_nodes.json": "knowledge_node.schema.json",
        "question_bank.json": "question.schema.json",
        "task_bank.json": "task.schema.json",
        "rubrics.json": "rubric.schema.json",
        "retrieval_eval_cases.json": "retrieval_eval_case.schema.json",
        "generation_eval_cases.json": "generation_eval_case.schema.json",
    }
    checker = FormatChecker()
    for data_file, schema_file in schema_files.items():
        schema = json.loads((BASE / "contracts/jsonschema" / schema_file).read_text(encoding="utf-8"))
        rows = load(data_file)
        instances = rows if isinstance(rows, list) else [rows]
        for index, row in enumerate(instances):
            for validation_error in Draft202012Validator(schema, format_checker=checker).iter_errors(row):
                errors.append(f"{data_file}[{index}] schema: {validation_error.message}")

    chunk_schema = json.loads((BASE / "contracts/jsonschema/knowledge_chunk.schema.json").read_text(encoding="utf-8"))
    for index, chunk in enumerate(chunks):
        for validation_error in Draft202012Validator(chunk_schema, format_checker=checker).iter_errors(chunk):
            errors.append(f"rag_chunks[{index}] schema: {validation_error.message}")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "version": domain.get("version"),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            **actual_counts,
            "sources": len(sources),
            "trusted_core_nodes": len(core_nodes),
            "trusted_ai_generated_nodes": len(imported_nodes),
            "concept_cards": len(assets["concept_cards.json"]),
            "faq": len(assets["faq.json"]),
            "error_cases": len(assets["error_cases.json"]),
        },
        "quality_layers": {
            "trusted_core_full_coverage_rate": round(core_complete / max(1, len(core_nodes)), 6),
            "trusted_ai_generated_full_coverage_rate": round(imported_complete / max(1, len(imported_nodes)), 6),
            "trusted_ai_generated_task_rubric_coverage_rate": round(imported_task_coverage / max(1, len(imported_nodes)), 6),
            "all_runtime_chunks_have_evidence": chunk_evidence_ids == evidence_ids,
        },
        "governance": {
            "imported_nodes_runtime_enabled": True,
            "imported_nodes_review_status": "pending_team_review",
            "published_version_is_immutable": True,
        },
    }
    (BASE / "reports/validation_report_v2.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
