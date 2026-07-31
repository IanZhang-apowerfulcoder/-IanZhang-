#!/usr/bin/env python3
"""Validate the v7.0 project baseline.

The validator intentionally checks cross-file consistency instead of only parsing
individual files. It is safe to run locally and in GitHub Actions.
"""
from __future__ import annotations

import csv
import json
import py_compile
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []
STATS: dict[str, Any] = {}


def error(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        error(f"JSON parse failed: {path.relative_to(ROOT)}: {exc}")
        return None


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        error(f"YAML parse failed: {path.relative_to(ROOT)}: {exc}")
        return None


def iter_refs(value: Any):
    if isinstance(value, dict):
        if isinstance(value.get("$ref"), str):
            yield value["$ref"]
        for child in value.values():
            yield from iter_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_refs(child)


def resolve_json_pointer(document: Any, ref: str) -> bool:
    if not ref.startswith("#/"):
        return False
    current = document
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            return False
    return True


def check_yaml_json_parse() -> None:
    json_files = list(ROOT.rglob("*.json"))
    yaml_files = list(ROOT.rglob("*.yaml")) + list(ROOT.rglob("*.yml"))
    for path in json_files:
        load_json(path)
    for path in yaml_files:
        load_yaml(path)
    STATS["json_files"] = len(json_files)
    STATS["yaml_files"] = len(yaml_files)


def check_openapi(path: Path) -> set[str]:
    document = load_yaml(path)
    if not isinstance(document, dict):
        return set()
    if not str(document.get("openapi", "")).startswith("3."):
        error(f"Not OpenAPI 3.x: {path.relative_to(ROOT)}")
    refs = list(iter_refs(document))
    external = [ref for ref in refs if not ref.startswith("#/")]
    if external:
        error(f"External OpenAPI refs are not allowed in baseline: {path.relative_to(ROOT)}: {external[:5]}")
    for ref in refs:
        if ref.startswith("#/") and not resolve_json_pointer(document, ref):
            error(f"Broken OpenAPI ref in {path.relative_to(ROOT)}: {ref}")

    operation_ids: list[str] = []
    paths = document.get("paths", {})
    if not isinstance(paths, dict):
        error(f"OpenAPI paths must be an object: {path.relative_to(ROOT)}")
        return set()
    for route, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete", "options", "head"):
            operation = item.get(method)
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                error(f"Missing operationId: {path.relative_to(ROOT)} {method.upper()} {route}")
            else:
                operation_ids.append(str(operation_id))
            responses = operation.get("responses")
            if not isinstance(responses, dict) or not responses:
                error(f"Missing responses: {path.relative_to(ROOT)} {method.upper()} {route}")
    duplicates = [key for key, count in Counter(operation_ids).items() if count > 1]
    if duplicates:
        error(f"Duplicate operationIds in {path.relative_to(ROOT)}: {duplicates}")
    STATS[f"operations:{path.name}"] = len(operation_ids)
    return set(operation_ids)


def check_openapis_and_http_mocks() -> None:
    public_ops = check_openapi(ROOT / "api/openapi.yaml")
    internal_ops = check_openapi(ROOT / "api/internal_openapi.yaml")
    check_openapi(ROOT / "api/knowledge_domain_api.yaml")
    kb_api = ROOT / "knowledge-bases/enterprise-rag-engineering-v2/contracts/knowledge-api.yaml"
    if kb_api.exists():
        check_openapi(kb_api)

    expected = public_ops | internal_ops
    mock_root = ROOT / "mocks/http"
    found = {p.name for p in mock_root.iterdir() if p.is_dir()} if mock_root.exists() else set()
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    if missing:
        error(f"Missing HTTP mock directories for operationIds: {missing}")
    if extra:
        warn(f"HTTP mock directories without current operationId: {extra}")
    for operation_id in found:
        folder = mock_root / operation_id
        for name in ("request.json", "response.json", "error_response.json"):
            if not (folder / name).is_file():
                error(f"Missing mock file: mocks/http/{operation_id}/{name}")
            else:
                load_json(folder / name)
    STATS["http_mock_operations"] = len(found)

    ownership = load_yaml(ROOT / "project/api_ownership.yaml")
    if isinstance(ownership, dict):
        ownership_ids: set[str] = set()
        def collect(obj: Any) -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in {"operation_id", "operationId"} and isinstance(v, str):
                        ownership_ids.add(v)
                    else:
                        collect(v)
            elif isinstance(obj, list):
                for x in obj:
                    collect(x)
        collect(ownership)
        unknown = sorted(ownership_ids - expected)
        if unknown:
            error(f"API ownership references unknown operationIds: {unknown}")


def check_json_schemas_and_agent_mocks() -> None:
    schema_root = ROOT / "contracts/jsonschema"
    schema_paths = sorted(schema_root.rglob("*.schema.json"))
    schemas: dict[str, Any] = {}
    for path in schema_paths:
        schema = load_json(path)
        if schema is None:
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            error(f"Invalid JSON Schema: {path.relative_to(ROOT)}: {exc}")
        schemas[path.stem.replace(".schema", "")] = schema
    STATS["json_schemas"] = len(schema_paths)

    mappings = {
        "diagnosis": ("diagnosis_input", "diagnosis_output"),
        "path_planning": ("path_plan_input", "path_plan_output"),
        "rag_router": ("rag_router_input", "rag_router_output"),
        "resource_coordinator": ("resource_input", "resource_output"),
        "explanation_generator": ("resource_input", "explanation_output"),
        "practice_generator": ("resource_input", "practice_output"),
        "quiz_draft_generator": ("resource_input", "quiz_draft_output"),
        "assessment_evaluation": ("assessment_input", "assessment_output"),
        "review_coordinator": ("review_input", "review_output"),
        "factuality_reviewer": ("review_input", "factuality_review_output"),
        "difficulty_reviewer": ("review_input", "difficulty_review_output"),
        "assessment_quality_reviewer": ("review_input", "assessment_review_output"),
        "safety_reviewer": ("review_input", "safety_review_output"),
        "arbitration": ("arbitration_input", "arbitration_output"),
    }
    format_checker = FormatChecker()
    mock_root = ROOT / "mocks/internal/agents"
    found_agents = {p.name for p in mock_root.iterdir() if p.is_dir()} if mock_root.exists() else set()
    if found_agents != set(mappings):
        error(f"Agent mock set mismatch. Missing={sorted(set(mappings)-found_agents)}, extra={sorted(found_agents-set(mappings))}")
    validated = 0
    for agent, (input_name, output_name) in mappings.items():
        for side, schema_name in (("input", input_name), ("output", output_name)):
            schema = schemas.get(schema_name)
            instance_path = mock_root / agent / f"{side}.json"
            if schema is None:
                error(f"Missing schema {schema_name} for {agent}/{side}")
                continue
            instance = load_json(instance_path)
            if instance is None:
                continue
            validator = Draft202012Validator(schema, format_checker=format_checker)
            failures = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
            if failures:
                excerpts = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in failures[:8]]
                error(f"Agent mock validation failed {agent}/{side}: " + " | ".join(excerpts))
            else:
                validated += 1
    STATS["agent_mock_documents_validated"] = validated


def check_team_and_tasks() -> None:
    member_root = ROOT / "members"
    members = sorted([p.name for p in member_root.iterdir() if p.is_dir()]) if member_root.exists() else []
    if len(members) != 9:
        error(f"Expected 9 member directories, found {len(members)}: {members}")
    required_member_files = {"00_开始这里.md", "00_完整开发文件.md", "openapi_scope.yaml", "internal_scope.yaml", "mock_index.yaml"}
    for member in members:
        missing = sorted(required_member_files - {p.name for p in (member_root/member).iterdir() if p.is_file()})
        if missing:
            error(f"Member {member} missing files: {missing}")

    task_paths = sorted((ROOT / "tasks").glob("S[0-7]/P*.md"))
    if len(task_paths) != 72:
        error(f"Expected 72 stage task cards, found {len(task_paths)}")
    for stage in range(8):
        count = len(list((ROOT / "tasks" / f"S{stage}").glob("P*.md")))
        if count != 9:
            error(f"Stage S{stage} expected 9 task cards, found {count}")
    matrix_path = ROOT / "project/member_stage_matrix.csv"
    if matrix_path.exists():
        with matrix_path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) != 72:
            error(f"member_stage_matrix.csv expected 72 rows, found {len(rows)}")
    else:
        error("Missing project/member_stage_matrix.csv")
    STATS["members"] = len(members)
    STATS["stage_task_cards"] = len(task_paths)


def check_workflows() -> None:
    blueprint = load_yaml(ROOT / "project/agent_blueprint.yaml")
    if not isinstance(blueprint, dict):
        return
    core = set(blueprint.get("core_agents", []))
    parallel = set()
    for value in (blueprint.get("parallel_groups") or {}).values():
        if isinstance(value, dict):
            parallel.update(value.get("members", []) or [])
            coordinator = value.get("coordinator")
            if coordinator:
                core.add(coordinator)
    all_agents = core | parallel
    if len(all_agents) != 14:
        error(f"Expected 14 agent modules in blueprint, found {len(all_agents)}: {sorted(all_agents)}")

    for filename in ("learning_workflow.yaml", "qa_workflow.yaml", "knowledge_maintenance_workflow.yaml"):
        workflow = load_yaml(ROOT / "project" / filename)
        if not isinstance(workflow, dict):
            continue
        states = workflow.get("states")
        if states is not None:
            state_set = set(states)
            initial = workflow.get("initial_state")
            if initial and initial not in state_set:
                error(f"{filename}: initial_state {initial} not in states")
            for terminal in workflow.get("terminal_states", []) or []:
                if terminal not in state_set:
                    error(f"{filename}: terminal state {terminal} not in states")
            for transition in workflow.get("transitions", []) or []:
                if transition.get("from") not in state_set or transition.get("to") not in state_set:
                    error(f"{filename}: transition references unknown state: {transition}")

    registry = load_yaml(ROOT / "project/tool_catalog.yaml")
    if not isinstance(registry, dict):
        error("project/tool_catalog.yaml must parse to an object")
    STATS["agent_modules"] = len(all_agents)


def read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        rows = []
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
                else:
                    error(f"Expected object in {path.relative_to(ROOT)} line {index}")
            except Exception as exc:
                error(f"JSONL parse failed {path.relative_to(ROOT)} line {index}: {exc}")
        return rows
    value = load_json(path)
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        for key in ("items", "data", "nodes", "edges", "chunks", "sources", "questions", "tasks", "rubrics", "cases"):
            if isinstance(value.get(key), list):
                return [x for x in value[key] if isinstance(x, dict)]
    return []


def find_first_key(obj: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in obj:
            return obj[key]
    return None


def check_knowledge_base() -> None:
    kb = ROOT / "knowledge-bases/enterprise-rag-engineering-v2"
    required = [
        "data/domain.json", "data/knowledge_nodes.json", "data/knowledge_edges.json",
        "data/rag_chunks.jsonl", "data/source_registry.json", "data/evidence_items.json",
        "data/question_bank.json", "data/task_bank.json", "data/rubrics.json",
        "data/retrieval_eval_cases.json", "data/generation_eval_cases.json",
        "data/retrieval_strategy_catalog.json", "data/rag_policy.json",
        "indexes/knowledge_graph.json", "indexes/parent_child_index.json", "indexes/metadata_catalog.json",
        "server/router.py", "server/adaptive_retriever.py", "contracts/knowledge-api.yaml",
    ]
    for rel in required:
        if not (kb / rel).exists():
            error(f"Knowledge base missing {rel}")

    nodes = read_json_or_jsonl(kb / "data/knowledge_nodes.json")
    edges = read_json_or_jsonl(kb / "data/knowledge_edges.json")
    chunks = read_json_or_jsonl(kb / "data/rag_chunks.jsonl")
    sources = read_json_or_jsonl(kb / "data/source_registry.json")
    evidence = read_json_or_jsonl(kb / "data/evidence_items.json")
    questions = read_json_or_jsonl(kb / "data/question_bank.json")
    tasks = read_json_or_jsonl(kb / "data/task_bank.json")
    rubrics = read_json_or_jsonl(kb / "data/rubrics.json")
    retrieval_cases = read_json_or_jsonl(kb / "data/retrieval_eval_cases.json")
    generation_cases = read_json_or_jsonl(kb / "data/generation_eval_cases.json")

    def ids(rows: list[dict[str, Any]], keys: tuple[str, ...], label: str) -> set[str]:
        values = [str(v) for row in rows if (v := find_first_key(row, keys)) is not None]
        dup = [k for k, c in Counter(values).items() if c > 1]
        if dup:
            error(f"Duplicate {label} ids: {dup[:10]}")
        return set(values)

    node_ids = ids(nodes, ("knowledge_node_id", "node_id", "id"), "knowledge node")
    source_ids = ids(sources, ("source_id", "id"), "source")
    chunk_ids = ids(chunks, ("chunk_id", "id"), "chunk")
    evidence_ids = ids(evidence, ("evidence_id", "id"), "evidence")
    question_ids = ids(questions, ("question_id", "id"), "question")
    task_ids = ids(tasks, ("task_id", "id"), "task")
    rubric_ids = ids(rubrics, ("rubric_id", "id"), "rubric")

    for edge in edges:
        source = find_first_key(edge, ("source_node_id", "source", "from_node_id", "from"))
        target = find_first_key(edge, ("target_node_id", "target", "to_node_id", "to"))
        if source is not None and str(source) not in node_ids:
            error(f"Edge references missing source node: {source}")
        if target is not None and str(target) not in node_ids:
            error(f"Edge references missing target node: {target}")
    for chunk in chunks:
        node = find_first_key(chunk, ("knowledge_node_id", "node_id"))
        if node is not None and str(node) not in node_ids:
            error(f"Chunk references missing node: {find_first_key(chunk, ('chunk_id','id'))} -> {node}")
        source = find_first_key(chunk, ("source_id",))
        if source is not None and str(source) not in source_ids:
            error(f"Chunk references missing source: {find_first_key(chunk, ('chunk_id','id'))} -> {source}")
    for ev in evidence:
        chunk = find_first_key(ev, ("chunk_id",))
        node = find_first_key(ev, ("knowledge_node_id", "node_id"))
        source = find_first_key(ev, ("source_id",))
        if chunk is not None and str(chunk) not in chunk_ids:
            error(f"Evidence references missing chunk: {find_first_key(ev, ('evidence_id','id'))} -> {chunk}")
        if node is not None and str(node) not in node_ids:
            error(f"Evidence references missing node: {find_first_key(ev, ('evidence_id','id'))} -> {node}")
        if source is not None and str(source) not in source_ids:
            error(f"Evidence references missing source: {find_first_key(ev, ('evidence_id','id'))} -> {source}")

    minimums = {
        "nodes": (len(nodes), 90), "edges": (len(edges), 240), "chunks": (len(chunks), 350),
        "sources": (len(sources), 40), "evidence": (len(evidence), 350),
        "questions": (len(questions), 300), "tasks": (len(tasks), 45), "rubrics": (len(rubrics), 45),
        "retrieval_eval_cases": (len(retrieval_cases), 200), "generation_eval_cases": (len(generation_cases), 160),
    }
    for label, (actual, minimum) in minimums.items():
        if actual < minimum:
            error(f"Knowledge base {label} below minimum: {actual} < {minimum}")
        STATS[f"kb_{label}"] = actual

    domain = load_json(kb / "data/domain.json")
    if isinstance(domain, dict):
        version = str(domain.get("version", domain.get("domain_version", "")))
        if not version.startswith("2"):
            error(f"Knowledge base domain version is not v2: {version}")


def check_python_compile() -> None:
    paths = [p for p in ROOT.rglob("*.py") if ".venv" not in p.parts and ".pytest_cache" not in p.parts]
    compiled = 0
    for path in paths:
        try:
            py_compile.compile(str(path), doraise=True)
            compiled += 1
        except Exception as exc:
            error(f"Python compile failed: {path.relative_to(ROOT)}: {exc}")
    STATS["python_files_compiled"] = compiled


def check_required_docs() -> None:
    docs = [
        "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "VERSION",
        "docs/00_总索引.md", "docs/01_项目重点与范围.md", "docs/02_团队总分工.md",
        "docs/03_成员必读文件矩阵.md", "docs/04_阶段开发计划.md", "docs/05_九人分阶段任务.md",
        "docs/06_系统模块边界.md", "docs/07_七核心智能体与平行Agent职责.md",
        "docs/08_联合决策状态机.md", "docs/09_数据流与调用链.md",
        "docs/10_命名与字段契约.md", "docs/11_接口所有权与变更流程.md",
        "docs/12_前端页面接口依赖.md", "docs/13_数据库与持久化约束.md",
        "docs/14_测试与验收标准.md", "docs/15_AI辅助开发约束.md",
        "docs/16_任务卡与PR规则.md", "docs/17_风险与降级.md",
        "docs/18_演示与评测指标.md", "docs/19_成员入门步骤.md",
        "docs/20_开发启动清单.md", "docs/21_端到端用户流程与接口审计.md",
        "docs/35_自适应多策略RAG与路由Agent.md", "docs/36_平行Agent生产与审核架构.md",
        "docs/37_知识库持续维护与版本发布.md", "docs/38_RetrievalTrace与Event事件规范.md",
        "docs/39_九人角色长期目标与阶段验收.md", "docs/40_比赛提交映射与最终交付清单.md",
    ]
    for rel in docs:
        path = ROOT / rel
        if not path.is_file():
            error(f"Missing required document: {rel}")
        elif rel != "VERSION" and path.stat().st_size < 200:
            error(f"Required document is unexpectedly small: {rel}")
    STATS["required_docs_checked"] = len(docs)


def main() -> int:
    check_required_docs()
    check_yaml_json_parse()
    check_openapis_and_http_mocks()
    check_json_schemas_and_agent_mocks()
    check_team_and_tasks()
    check_workflows()
    check_knowledge_base()
    check_python_compile()

    print("V7 CONTRACT VALIDATION")
    print("=" * 72)
    for key in sorted(STATS):
        print(f"{key}: {STATS[key]}")
    print(f"warnings: {len(WARNINGS)}")
    for item in WARNINGS:
        print(f"WARNING: {item}")
    print(f"errors: {len(ERRORS)}")
    for item in ERRORS:
        print(f"ERROR: {item}")
    if ERRORS:
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
