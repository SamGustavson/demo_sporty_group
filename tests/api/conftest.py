"""JSON schemas used to validate API responses."""

import json
from pathlib import Path

import pytest

SCHEMAS = Path(__file__).parent / "schemas"


def _load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text())


@pytest.fixture(scope="session")
def place_bet_success_schema() -> dict:
    return _load("place_bet_success.json")


@pytest.fixture(scope="session")
def error_schema() -> dict:
    return _load("error.json")
