PYTHON ?= python3

.PHONY: check lint test fixtures mac-app performance notarize deferred-contracts

check:
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) fixtures
	$(MAKE) performance

lint:
	$(PYTHON) -m ruff check src tests scripts
	$(PYTHON) -m ruff format --check src tests scripts

test:
	$(PYTHON) -m pytest -q -m "not performance and not deferred_contract"

# Revision-3 whole-form continuity remains an explicit future-feature contract.
# Preserve its assertions and run it independently of the supported release gate.
deferred-contracts:
	$(PYTHON) -m pytest -q -m deferred_contract

fixtures:
	$(PYTHON) scripts/validate_fixtures.py

performance:
	$(PYTHON) -m pytest -q -m "performance and not deferred_contract"

mac-app:
	bash tools/package_app.sh

notarize:
	bash tools/notarize_app.sh
