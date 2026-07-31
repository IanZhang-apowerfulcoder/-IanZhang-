.PHONY: validate validate-root test-kb validate-kb build-member-packs all

validate-root:
	python scripts/validate_v7_contracts.py

test-kb:
	PYTHONPATH=knowledge-bases/enterprise-rag-engineering-v2 pytest -q knowledge-bases/enterprise-rag-engineering-v2/tests

validate-kb:
	$(MAKE) -C knowledge-bases/enterprise-rag-engineering-v2 all

build-member-packs:
	python scripts/build_member_packs.py

validate: validate-root test-kb

all: validate-root validate-kb
