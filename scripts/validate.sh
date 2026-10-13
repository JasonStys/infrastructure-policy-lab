#!/usr/bin/env bash
# Jason Stys: portable fail-fast quality, contracts, negative/property tests and measured policy throughput.
# Functions: none. Variables: PYTHONPATH imports local modules, all evidence is synthetic or owned test output.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: PYTHONPATH — line 8
# END CODE MAP
set -euo pipefail
export PYTHONPATH=.
python -m ruff check .
python -m ruff format --check .
python -m mypy
python scripts/code_map.py --check
python scripts/file_guide.py --check
python -m pytest -q -W error --cov=assurance --cov-report=term-missing --cov-report=json:out/coverage.json --junitxml=out/junit.xml
python -m scripts.benchmark
