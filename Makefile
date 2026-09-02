PYTHON ?= python3

.PHONY: check lint test fixtures mac-app performance notarize

check:
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) fixtures
	$(MAKE) performance

lint:
	$(PYTHON) -m ruff check src tests scripts
	$(PYTHON) -m ruff format --check src tests scripts

test:
	$(PYTHON) -m pytest -q -m "not performance"

fixtures:
	$(PYTHON) scripts/validate_fixtures.py

performance:
	$(PYTHON) -m pytest -q -m performance

mac-app:
	bash tools/package_app.sh

notarize:
	bash tools/notarize_app.sh
