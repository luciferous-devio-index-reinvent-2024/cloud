SHELL = /usr/bin/env bash -xeuo pipefail

format: \
	fmt-terraform \
	fmt-python

fmt-terraform: \
	fmt-terraform-root \
	fmt-terraform-module-common \
	fmt-terraform-module-events-slack-webhook-destination \
	fmt-terraform-module-lambda-function \
	fmt-terraform-module-lambda-function-basic

fmt-terraform-root:
	terraform fmt

fmt-terraform-module-common:
	cd terraform_modules/common; \
	terraform fmt

fmt-terraform-module-events-slack-webhook-destination:
	cd terraform_modules/events_slack_webhook_destination; \
	terraform fmt

fmt-terraform-module-lambda-function:
	cd terraform_modules/lambda_function; \
	terraform fmt

fmt-terraform-module-lambda-function-basic:
	cd terraform_modules/lambda_function_basic; \
	terraform fmt

fmt-python:
	poetry run ruff check --select I --fix src/ tests/
	poetry run ruff format src/ tests/

lint: \
	lint-terraform \
	lint-python

lint-terraform: \
	lint-terraform-root \
	lint-terraform-module-common \
	lint-terraform-module-events-slack-webhook-destination \
	lint-terraform-module-lambda-function \
	lint-terraform-module-lambda-function-basic

lint-terraform-root:
	terraform fmt -check

lint-terraform-module-common:
	cd terraform_modules/common; \
	terraform fmt -check

lint-terraform-module-events-slack-webhook-destination:
	cd terraform_modules/events_slack_webhook_destination; \
	terraform fmt -check

lint-terraform-module-lambda-function:
	cd terraform_modules/lambda_function; \
	terraform fmt -check

lint-terraform-module-lambda-function-basic:
	cd terraform_modules/lambda_function_basic; \
	terraform fmt -check

lint-python:
	poetry run ruff check src/ tests/

test-unit:
	AWS_ACCESS_KEY_ID=dummy \
	AWS_SECRET_ACCESS_KEY=dummy \
	AWS_DEFAULT_REGION=ap-northeast-1 \
	PYTHONPATH=src \
	poetry run python -m pytest -vv tests/unit

compose-up:
	docker compose up -d
	sleep 5

compose-down:
	docker compose down

.PHONY: \
	format \
	fmt-terraform \
	fmt-terraform-root \
	fmt-terraform-module-common \
	fmt-python \
	lint \
	lint-terraform \
	lint-terraform-root \
	lint-terraform-module-common \
	lint-python \
	test-unit \
	compose-up \
	compose-down
