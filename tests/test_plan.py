"""Strict plan input, sensitive masks, bounds and malformed-data negative tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_plan_rejects_root — line 53
# parameter: change — line 53
# parameter: plan — line 53
# definition: test_nonobject — line 61
# parameter: value — line 61
# definition: test_resource_rejection — line 83
# parameter: change — line 83
# parameter: plan — line 83
# definition: test_duplicate_and_size — line 90
# parameter: plan — line 90
# definition: test_masked_fields — line 109
# parameter: mask — line 109
# parameter: plan — line 109
# variable: name — line 111
# variable: r — line 113
# variable: resource — line 113
# definition: test_nested_paths — line 117
# parameter: plan — line 117
# variable: r — line 119
# variable: resource — line 119
# definition: test_mask_and_token_bounds — line 129
# definition: test_plan_identity — line 140
# parameter: plan — line 140
# variable: before — line 142
# variable: after — line 144
# END CODE MAP

import copy

import pytest

from assurance.plan import descend_mask, field, load, mask_valid, token


@pytest.mark.parametrize(
    "change",
    [
        {"format_version": "2.0"},
        {"format_version": 1},
        {"complete": False},
        {"complete": 1},
        {"errored": True},
        {"resource_changes": []},
        {"resource_changes": {}},
        {"resource_changes": [None]},
        {"resource_drift": {}},
        {"resource_drift": [None]},
        {"resource_drift": [{"address": "x"}, {"address": "x"}]},
    ],
)
def test_plan_rejects_root(plan: dict, change: dict) -> None:
    """Incomplete, malformed, unsupported-version and empty evidence cannot pass."""
    plan.update(change)
    with pytest.raises(ValueError):
        load(plan)


@pytest.mark.parametrize("value", [None, [], "plan", 1])
def test_nonobject(value: object) -> None:
    """Root must be a JSON object, not a scalar/list."""
    with pytest.raises(ValueError):
        load(value)


@pytest.mark.parametrize(
    "change",
    [
        {"mode": "data"},
        {"address": "../../escape"},
        {"type": None},
        {"change": None},
        {"change": {"actions": "create"}},
        {"change": {"actions": ["other"]}},
        {"change": {"actions": [[]]}},
        {"change": {"actions": ["create"], "after": None}},
        {"change": {"actions": ["delete"], "after": {}}},
        {"change": {"actions": ["create"], "after": {}, "after_unknown": 1}},
        {"change": {"actions": ["create"], "after": {}, "after_sensitive": "false"}},
    ],
)
def test_resource_rejection(plan: dict, change: dict) -> None:
    """Identity, action vocabulary, after shape and masks are exact contracts."""
    plan["resource_changes"][0].update(change)
    with pytest.raises(ValueError):
        load(plan)


def test_duplicate_and_size(plan: dict) -> None:
    """Duplicate identity and oversized inventories are rejected before evaluation."""
    plan["resource_changes"].append(copy.deepcopy(plan["resource_changes"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        load(plan)
    plan["resource_changes"] *= 2001
    with pytest.raises(ValueError, match="2000"):
        load(plan)


@pytest.mark.parametrize(
    "mask",
    [
        True,
        {"enable_dns_support": True},
        {"enable_dns_support": [True]},
        {"enable_dns_support": {"nested": True}},
    ],
)
def test_masked_fields(plan: dict, mask: object) -> None:
    """Parent or descendant privacy/uncertainty never discloses the selected value."""
    for name in ("after_unknown", "after_sensitive"):
        plan["resource_changes"][0]["change"][name] = mask
        resource = next(r for r in load(plan).resources if r.kind == "aws_vpc")
        assert field(resource, ("enable_dns_support",)) is None


def test_nested_paths(plan: dict) -> None:
    """List indexes and missing nested paths cannot trigger guessed defaults."""
    resource = next(r for r in load(plan).resources if r.kind == "aws_s3_bucket_versioning")
    assert field(resource, ("versioning_configuration", 0, "status")) == "Enabled"
    assert field(resource, ("versioning_configuration", 1, "status")) is None
    assert field(resource, ("missing",)) is None
    assert descend_mask([True], 0) is True
    assert descend_mask([], 1) is False
    assert descend_mask([], "bad") is True
    assert descend_mask(False, "x") is False


def test_mask_and_token_bounds() -> None:
    """Direct helper boundaries match the loader contract."""
    with pytest.raises(ValueError):
        mask_valid(False, 33)
    with pytest.raises(ValueError):
        token("x" * 201, True)
    with pytest.raises(ValueError):
        token(1)
    mask_valid({"a": [False, {"b": True}]})


def test_plan_identity(plan: dict) -> None:
    """Resource order does not change decisions; digest identifies input, not authenticity."""
    before = load(plan)
    plan["resource_changes"].reverse()
    after = load(plan)
    assert before.resources == after.resources
    assert before.digest != after.digest
    plan["resource_drift"] = [{"address": "aws_subnet.sample"}]
    assert load(plan).drift == ("aws_subnet.sample",)
