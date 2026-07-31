from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from fastapi.testclient import TestClient

from server.app import app, retriever

BASE = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_counts_and_coverage():
    nodes = json.loads((BASE / "data/knowledge_nodes.json").read_text(encoding="utf-8"))
    chunks = [json.loads(x) for x in (BASE / "data/rag_chunks.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    questions = json.loads((BASE / "data/question_bank.json").read_text(encoding="utf-8"))
    assert len(nodes) == 32
    assert len(chunks) == 128
    assert len(questions) == 128
    for node in nodes:
        assert len([c for c in chunks if c["knowledge_node_id"] == node["id"]]) >= 4
        assert len([q for q in questions if q["knowledge_node_id"] == node["id"]]) >= 4


def test_compatible_retrieval_contract():
    schema = json.loads((BASE / "contracts/jsonschema/retrieval_response.schema.json").read_text(encoding="utf-8"))
    request = {
        "retrieval_request_id":"b8c16593-d680-5c5d-aa29-16a1a071b2db",
        "knowledge_base_version_id":retriever.domain["knowledge_base_version_id"],
        "query_text":"RAG与微调有什么区别？",
        "top_k":5,
        "filters":{}
    }
    response = client.post("/api/v1/retrieval/search", json=request)
    assert response.status_code == 200
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(response.json()))
    assert errors == []
    assert response.json()["evidence_items"]


def test_metadata_filter():
    hits = retriever.search("GraphRAG适合什么问题", 10, {"max_difficulty_level":3})
    assert all(h["difficulty_level"] <= 3 for h in hits)


def test_node_lookup():
    response = client.get("/api/v1/knowledge/nodes/RAG-M03-N04")
    assert response.status_code == 200
    assert response.json()["name"].startswith("混合检索")


def test_submission_cases_match_existing_project_contracts():
    mappings = {
        "diagnosis_output.json": "agents/diagnosis_output.schema.json",
        "path_plan_output.json": "agents/path_plan_output.schema.json",
        "retrieval_request.json": "services/retrieval_request.schema.json",
        "retrieval_response.json": "services/retrieval_response.schema.json",
        "resource_output.json": "agents/resource_output.schema.json",
        "assessment_output.json": "agents/assessment_output.schema.json",
        "review_output.json": "agents/review_output.schema.json",
        "arbitration_output.json": "agents/arbitration_output.schema.json",
    }
    compat = BASE / "contracts/compatibility/user-repo-v6"
    for case_dir in sorted((BASE / "submission/learner_cases").iterdir()):
        if not case_dir.is_dir():
            continue
        for filename, schema_rel in mappings.items():
            schema = json.loads((compat / schema_rel).read_text(encoding="utf-8"))
            payload = json.loads((case_dir / filename).read_text(encoding="utf-8"))
            errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload))
            assert errors == [], f"{case_dir.name}/{filename}: {errors}"


def test_knowledge_openapi_local_refs_exist():
    import yaml

    api_path = BASE / "contracts/knowledge-api.yaml"
    spec = yaml.safe_load(api_path.read_text(encoding="utf-8"))
    refs = []

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "$ref" and isinstance(item, str) and not item.startswith("#"):
                    refs.append(item.split("#", 1)[0])
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(spec)
    assert refs
    assert all((api_path.parent / ref).resolve().is_file() for ref in refs)
