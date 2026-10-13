"""Strict JSON filesystem boundaries and exact-decimal cost oracles. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_json_rejection — line 49
# parameter: source — line 49
# definition: test_json_bounds — line 55
# variable: value — line 57
# definition: test_read_and_bom — line 67
# parameter: monkeypatch — line 67
# parameter: tmp_path — line 67
# variable: file — line 69
# definition: test_link_refusal — line 79
# parameter: tmp_path — line 79
# variable: target — line 81
# variable: linked — line 83
# definition: test_new_output — line 94
# parameter: tmp_path — line 94
# variable: output — line 96
# definition: test_decimal_rejection — line 107
# parameter: value — line 107
# definition: test_cost_scenario — line 113
# variable: scenario — line 115
# definition: test_integer_cost_oracle — line 125
# parameter: cents — line 125
# parameter: quantity — line 125
# variable: scenario — line 127
# variable: expected — line 141
# definition: test_cost_contract — line 159
# parameter: change — line 159
# variable: scenario — line 161
# definition: test_duplicate_cost_item — line 167
# variable: scenario — line 169
# END CODE MAP

import copy
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from assurance.cost import amount, estimate
from assurance.io import bounded, canonical, new_directory, parse, read
from scripts.fixtures import ROOT


@pytest.mark.parametrize(
    "source", ['{"x":1,"x":2}', "[NaN]", "[Infinity]", "{", '"\\ud800"', '"\\u0000"', '"\\u007f"']
)
def test_json_rejection(source: str) -> None:
    """Duplicate, malformed, nonfinite and unsafe Unicode/control input fails before plan assessment."""
    with pytest.raises(ValueError):
        parse(source)


def test_json_bounds() -> None:
    """Depth, text and collection sizes are enforced without evaluating source."""
    for value in ("x" * 262145, [0] * 10001):
        with pytest.raises(ValueError):
            bounded(value)
    with pytest.raises(ValueError):
        bounded({}, 33)
    with pytest.raises(ValueError):
        parse("[" * 2000 + "0" + "]" * 2000)
    assert parse(canonical({"value": [1, True, None, 1.25]}))["value"] == [1, True, None, 1.25]


def test_read_and_bom(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """UTF-8 BOM is supported; byte bounds and non-files remain explicit failures."""
    file = tmp_path / "plan.json"
    file.write_bytes(b'\xef\xbb\xbf{"a":1}')
    assert read(file) == {"a": 1}
    monkeypatch.setattr("assurance.io.MAX_BYTES", 2)
    with pytest.raises(ValueError):
        read(file)
    with pytest.raises(ValueError):
        read(tmp_path)


def test_link_refusal(tmp_path: Path) -> None:
    """Linked input/output paths are refused when the OS grants test symlink creation."""
    target = tmp_path / "real.json"
    target.write_text("{}")
    linked = tmp_path / "link.json"
    try:
        linked.symlink_to(target)
    except OSError:
        pytest.skip("OS does not grant test process symbolic-link creation")
    with pytest.raises(ValueError):
        read(linked)
    with pytest.raises(ValueError):
        new_directory(linked)


def test_new_output(tmp_path: Path) -> None:
    """New output creates one directory only; earlier evidence is preserved."""
    output = tmp_path / "new"
    new_directory(output)
    with pytest.raises(FileExistsError):
        new_directory(output)
    with pytest.raises(FileNotFoundError):
        new_directory(tmp_path / "missing" / "new")


@pytest.mark.parametrize(
    "value", [True, -1, 1.2, "-1", "NaN", "Infinity", "1e3", "", "1.2.3", "1000001", "0" * 21, None]
)
def test_decimal_rejection(value: object) -> None:
    """Decimal contracts reject float ambiguity, infinity, sign/exponent tricks and excessive amounts."""
    with pytest.raises(ValueError):
        amount(value)


def test_cost_scenario() -> None:
    """Known synthetic scenario totals exactly 1.55 USD; rounding occurs only at final total."""
    scenario = read(ROOT / "examples/cost.json")
    assert estimate(scenario)["total_usd"] == "1.55"
    scenario["items"] = [
        {"name": "one", "unit": "item", "quantity": "1", "unit_price": "0.005"},
        {"name": "two", "unit": "item", "quantity": "1", "unit_price": "0.005"},
    ]
    assert estimate(scenario)["total_usd"] == "0.01"


@given(st.integers(0, 1000), st.integers(0, 1000))
def test_integer_cost_oracle(quantity: int, cents: int) -> None:
    """Independent integer-cent multiplication proves decimal output for bounded generated workloads."""
    scenario = {
        "schema": 1,
        "currency": "USD",
        "label": "oracle",
        "exclusions": ["all other usage"],
        "items": [
            {
                "name": "item",
                "unit": "each",
                "quantity": str(quantity),
                "unit_price": f"{cents // 100}.{cents % 100:02d}",
            }
        ],
    }
    expected = quantity * cents
    assert estimate(scenario)["total_usd"] == f"{expected // 100}.{expected % 100:02d}"


@pytest.mark.parametrize(
    "change",
    [
        {"currency": "EUR"},
        {"schema": True},
        {"items": []},
        {"items": {}},
        {"items": [None]},
        {"exclusions": []},
        {"exclusions": [False]},
        {"label": ""},
        {"unknown": 1},
    ],
)
def test_cost_contract(change: dict) -> None:
    """No estimate silently ignores wrong currency, missing exclusions or unknown fields."""
    scenario = read(ROOT / "examples/cost.json")
    scenario.update(change)
    with pytest.raises(ValueError):
        estimate(scenario)


def test_duplicate_cost_item() -> None:
    """Duplicate line-item names cannot hide or double-count an ambiguous workload."""
    scenario = read(ROOT / "examples/cost.json")
    scenario["items"].append(copy.deepcopy(scenario["items"][0]))
    with pytest.raises(ValueError):
        estimate(scenario)
