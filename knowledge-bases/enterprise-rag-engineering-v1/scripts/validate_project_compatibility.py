from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

BASE = Path(__file__).resolve().parents[1]
SCHEMA_BASE = BASE / "contracts/compatibility/user-repo-v6"
CASES = BASE / "submission/learner_cases"

MAPPING = {
    "diagnosis_output.json": SCHEMA_BASE / "agents/diagnosis_output.schema.json",
    "path_plan_output.json": SCHEMA_BASE / "agents/path_plan_output.schema.json",
    "retrieval_request.json": SCHEMA_BASE / "services/retrieval_request.schema.json",
    "retrieval_response.json": SCHEMA_BASE / "services/retrieval_response.schema.json",
    "resource_output.json": SCHEMA_BASE / "agents/resource_output.schema.json",
    "assessment_output.json": SCHEMA_BASE / "agents/assessment_output.schema.json",
    "review_output.json": SCHEMA_BASE / "agents/review_output.schema.json",
    "arbitration_output.json": SCHEMA_BASE / "agents/arbitration_output.schema.json",
}


def main() -> int:
    errors: list[str] = []
    checked = 0
    for case_dir in sorted(p for p in CASES.iterdir() if p.is_dir()):
        for filename, schema_path in MAPPING.items():
            data_path = case_dir / filename
            if not data_path.exists():
                errors.append(f"{case_dir.name}: missing {filename}")
                continue
            if not schema_path.exists():
                errors.append(f"missing compatibility schema {schema_path.relative_to(BASE)}")
                continue
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            data = json.loads(data_path.read_text(encoding="utf-8"))
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for err in validator.iter_errors(data):
                path = "/".join(str(x) for x in err.absolute_path)
                errors.append(f"{case_dir.name}/{filename} {path}: {err.message}")
            checked += 1
    result = {
        "status": "PASS" if not errors else "FAIL",
        "learner_case_count": len([p for p in CASES.iterdir() if p.is_dir()]),
        "artifacts_checked": checked,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
