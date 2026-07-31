PYTHON ?= python
.PHONY: validate compatibility eval test serve dry-import all
all: validate compatibility eval test dry-import
validate:
	PYTHONPATH=. $(PYTHON) scripts/validate_pack.py
compatibility:
	PYTHONPATH=. $(PYTHON) scripts/validate_project_compatibility.py
eval:
	PYTHONPATH=. $(PYTHON) scripts/run_retrieval_eval.py
test:
	PYTHONPATH=. pytest -q
serve:
	PYTHONPATH=. uvicorn server.app:app --reload --port 8090
dry-import:
	PYTHONPATH=. $(PYTHON) scripts/import_to_postgres.py --dsn postgresql://unused --dry-run
