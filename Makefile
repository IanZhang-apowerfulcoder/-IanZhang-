.PHONY: validate infra-up infra-down
validate:
	python3 scripts/validate_repo.py
infra-up:
	docker compose --env-file infra/.env.example -f infra/compose.dev.yaml up -d
infra-down:
	docker compose --env-file infra/.env.example -f infra/compose.dev.yaml down
