"""Reusable isolated synthetic plan fixtures; no real AWS credentials/state. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: plan — line 12
# END CODE MAP

import pytest

from scripts.fixtures import fixture


@pytest.fixture
def plan() -> dict:
    """Return a new mutable fictional plan per test to prevent mutation leakage between cases."""
    return fixture()
