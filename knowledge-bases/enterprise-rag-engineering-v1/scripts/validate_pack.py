from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

BASE = Path(__file__).resolve().parents[1]


def load(name: str):
    return json.loads((BASE / "data" / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    domain = load("domain.json")
    nodes = load("knowledge_nodes.json")
    edges = load("knowledge_edges.json")
    chunks = [json.loads(x) for x in (BASE / "data/rag_chunks.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    assets = {name: load(name) for name in ["concept_cards.json","faq.json","error_cases.json","question_bank.json","task_bank.json","rubrics.json","retrieval_eval_cases.json","generation_eval_cases.json"]}
    node_ids = {n["id"] for n in nodes}
    evidence_ids = {c["evidence_id"] for c in chunks}
    chunk_ids = {c["chunk_id"] for c in chunks}
    if len(nodes) != 32: errors.append(f"expected 32 nodes, got {len(nodes)}")
    if len(chunks) != 128: errors.append(f"expected 128 chunks, got {len(chunks)}")
    if len(node_ids) != len(nodes): errors.append("duplicate knowledge node id")
    if len(evidence_ids) != len(chunks): errors.append("duplicate evidence id")
    if len(chunk_ids) != len(chunks): errors.append("duplicate chunk id")
    for n in nodes:
        for p in n["prerequisites"]:
            if p not in node_ids: errors.append(f"missing prerequisite {p} for {n['id']}")
    for e in edges:
        if e["source_knowledge_node_id"] not in node_ids or e["target_knowledge_node_id"] not in node_ids:
            errors.append(f"edge references missing node: {e['edge_id']}")
    for c in chunks:
        if c["knowledge_node_id"] not in node_ids: errors.append(f"chunk missing node: {c['chunk_id']}")
        if not c["source_ids"]: errors.append(f"chunk without source: {c['chunk_id']}")
    counts = defaultdict(Counter)
    for name, rows in assets.items():
        for row in rows:
            nid = row.get("knowledge_node_id")
            if nid:
                counts[nid][name] += 1
            for ev in row.get("evidence_ids", []) + row.get("required_evidence_ids", []):
                if ev not in evidence_ids:
                    errors.append(f"{name} references missing evidence {ev}")
    for n in nodes:
        nid = n["id"]
        expected = {"concept_cards.json":1,"faq.json":3,"error_cases.json":2,"question_bank.json":4,"task_bank.json":1,"rubrics.json":1,"retrieval_eval_cases.json":3,"generation_eval_cases.json":1}
        for name, minimum in expected.items():
            if counts[nid][name] < minimum:
                errors.append(f"{nid} {name} count {counts[nid][name]} < {minimum}")
    schema_files = {
        "domain.json":"domain.schema.json","knowledge_nodes.json":"knowledge_node.schema.json","question_bank.json":"question.schema.json",
        "task_bank.json":"task.schema.json","rubrics.json":"rubric.schema.json","retrieval_eval_cases.json":"retrieval_eval_case.schema.json","generation_eval_cases.json":"generation_eval_case.schema.json"
    }
    checker = FormatChecker()
    for data_file, schema_file in schema_files.items():
        schema = json.loads((BASE / "contracts/jsonschema" / schema_file).read_text(encoding="utf-8"))
        rows = load(data_file)
        if isinstance(rows, list):
            for i, row in enumerate(rows):
                for err in Draft202012Validator(schema, format_checker=checker).iter_errors(row):
                    errors.append(f"{data_file}[{i}] schema: {err.message}")
        else:
            for err in Draft202012Validator(schema, format_checker=checker).iter_errors(rows):
                errors.append(f"{data_file} schema: {err.message}")
    chunk_schema = json.loads((BASE / "contracts/jsonschema/knowledge_chunk.schema.json").read_text(encoding="utf-8"))
    for i,c in enumerate(chunks):
        for err in Draft202012Validator(chunk_schema, format_checker=checker).iter_errors(c):
            errors.append(f"rag_chunks[{i}] schema: {err.message}")
    report = {
        "status":"PASS" if not errors else "FAIL",
        "errors":errors,
        "counts":{"nodes":len(nodes),"edges":len(edges),"chunks":len(chunks),**{k:len(v) for k,v in assets.items()}},
        "core_coverage_rate":sum(1 for n in nodes if n["core"] and counts[n["id"]]["question_bank.json"] >= 4) / max(1,sum(1 for n in nodes if n["core"]))
    }
    (BASE / "reports/validation_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
