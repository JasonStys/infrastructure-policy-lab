"""Independent gate decisions, unknown propagation, KMS/TLS scope and property oracles. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_labeled_scenarios — line 78
# parameter: expected — line 78
# parameter: name — line 78
# variable: report — line 80
# definition: test_private_subnet_oracle — line 86
# parameter: public — line 86
# variable: plan — line 88
# definition: test_exact_boolean — line 94
# parameter: plan — line 94
# parameter: value — line 94
# definition: test_sensitive_redaction — line 100
# parameter: plan — line 100
# variable: parsed — line 104
# definition: test_invalid_encryption_key — line 110
# parameter: plan — line 110
# parameter: value — line 110
# variable: resource — line 112
# variable: r — line 114
# definition: test_key_binding — line 124
# parameter: mutation — line 124
# parameter: plan — line 124
# variable: key — line 126
# variable: r — line 126
# definition: test_malformed_tls — line 147
# parameter: bucket — line 147
# parameter: value — line 147
# definition: test_tls_scope — line 162
# parameter: field — line 162
# parameter: plan — line 162
# parameter: value — line 162
# variable: r — line 164
# variable: resource — line 164
# variable: policy — line 165
# definition: test_missing_tls_bucket — line 171
# parameter: plan — line 171
# variable: r — line 173
# variable: resource — line 173
# definition: test_delete — line 178
# parameter: plan — line 178
# variable: result — line 181
# definition: test_comparison — line 187
# parameter: plan — line 187
# variable: before — line 189
# variable: after — line 191
# variable: fewer — line 196
# definition: test_invalid_reports — line 205
# parameter: report — line 205
# definition: test_duplicate_report — line 211
# parameter: plan — line 211
# variable: report — line 213
# END CODE MAP

import copy

import pytest
from hypothesis import given
from hypothesis import strategies as st

from assurance.io import canonical, parse, read
from assurance.plan import load
from assurance.policy import assess, compare, evidence, tls_deny
from scripts.fixtures import ROOT, fixture


@pytest.mark.parametrize(
    "name,expected",
    [
        ("healthy", {"PASS": 16, "FAIL": 0, "UNKNOWN": 0, "REVIEW": 0}),
        ("insecure", {"PASS": 14, "FAIL": 2, "UNKNOWN": 0, "REVIEW": 0}),
        ("unknown", {"PASS": 15, "FAIL": 0, "UNKNOWN": 1, "REVIEW": 0}),
        ("destructive", {"PASS": 16, "FAIL": 0, "UNKNOWN": 0, "REVIEW": 1}),
        ("drifted", {"PASS": 16, "FAIL": 0, "UNKNOWN": 0, "REVIEW": 1}),
        ("unsupported", {"PASS": 15, "FAIL": 0, "UNKNOWN": 1, "REVIEW": 0}),
    ],
)
def test_labeled_scenarios(name: str, expected: dict) -> None:
    """Hard-coded independent counts must match scenarios, not self-reported labels."""
    report = assess(load(read(ROOT / "examples" / f"{name}.json")))
    assert report["counts"] == expected
    assert report["allowed"] == (name == "healthy")


@given(st.booleans())
def test_private_subnet_oracle(public: bool) -> None:
    """Independent subnet oracle: exactly false public-IP assignment passes."""
    plan = fixture()
    plan["resource_changes"][1]["change"]["after"]["map_public_ip_on_launch"] = public
    assert assess(load(plan))["allowed"] is (not public)


@pytest.mark.parametrize("value", [1, 0, "true", "false", None, {}, []])
def test_exact_boolean(plan: dict, value: object) -> None:
    """No bool/int/string coercion can turn malformed settings into PASS."""
    plan["resource_changes"][0]["change"]["after"]["enable_dns_support"] = value
    assert not assess(load(plan))["allowed"]


def test_sensitive_redaction(plan: dict) -> None:
    """Masked secrets disappear from policy evidence and user reports."""
    plan["resource_changes"][0]["change"]["after"]["enable_dns_support"] = "PRIVATE-SENTINEL"
    plan["resource_changes"][0]["change"]["after_sensitive"] = {"enable_dns_support": True}
    parsed = load(plan)
    assert "PRIVATE-SENTINEL" not in canonical(evidence(parsed))
    assert "PRIVATE-SENTINEL" not in canonical(assess(parsed))


@pytest.mark.parametrize("value", [[], {}, True, "not-a-key"])
def test_invalid_encryption_key(plan: dict, value: object) -> None:
    """Malformed key fields are failed settings, never hash lookup crashes or PASS."""
    resource = next(
        r
        for r in plan["resource_changes"]
        if r["type"] == "aws_s3_bucket_server_side_encryption_configuration"
    )
    resource["change"]["after"]["rule"][0]["apply_server_side_encryption_by_default"][0][
        "kms_master_key_id"
    ] = value
    assert assess(load(plan))["counts"]["FAIL"] == 1


@pytest.mark.parametrize("mutation", ["wrong-key", "missing-key", "sensitive-key"])
def test_key_binding(plan: dict, mutation: str) -> None:
    """Encryption must reference a known selected key, not an opaque/missing ARN."""
    key = next(r for r in plan["resource_changes"] if r["type"] == "aws_kms_key")
    if mutation == "wrong-key":
        key["change"]["after"]["arn"] = "arn:aws:kms:other-key"
    elif mutation == "missing-key":
        del key["change"]["after"]["arn"]
    else:
        key["change"]["after_sensitive"] = {"arn": True}
    assert not assess(load(plan))["allowed"]


@pytest.mark.parametrize(
    "value,bucket",
    [
        (None, "x"),
        ("{}", "x"),
        ("bad", "x"),
        ('{"Statement":{}}', "x"),
        ('{"Statement":[null]}', "x"),
        ('{"Statement":[]}', None),
    ],
)
def test_malformed_tls(value: object, bucket: object) -> None:
    """Malformed JSON and statements cannot masquerade as HTTP denial."""
    assert not tls_deny(value, bucket)


@pytest.mark.parametrize(
    "field,value",
    [
        ("Effect", "Allow"),
        ("Principal", {"AWS": "*"}),
        ("Action", "s3:GetObject"),
        ("Resource", ["*"]),
        ("Condition", {"Bool": {"aws:SecureTransport": "true"}}),
    ],
)
def test_tls_scope(plan: dict, field: str, value: object) -> None:
    """A deny must cover all principals, HTTP and the selected bucket plus objects."""
    resource = next(r for r in plan["resource_changes"] if r["type"] == "aws_s3_bucket_policy")
    policy = parse(resource["change"]["after"]["policy"])
    policy["Statement"][0][field] = value
    resource["change"]["after"]["policy"] = canonical(policy)
    assert not assess(load(plan))["allowed"]


def test_missing_tls_bucket(plan: dict) -> None:
    """An unresolved bucket remains unknown rather than a passing deny."""
    resource = next(r for r in plan["resource_changes"] if r["type"] == "aws_s3_bucket_policy")
    resource["change"]["after_unknown"] = {"bucket": True}
    assert assess(load(plan))["counts"]["UNKNOWN"] == 1


def test_delete(plan: dict) -> None:
    """Deletion with no after creates both unknown and human-review findings."""
    plan["resource_changes"][0]["change"].update(actions=["delete"], after=None)
    result = assess(load(plan))
    assert result["counts"]["REVIEW"] == 1
    assert result["counts"]["UNKNOWN"] == 1
    assert not result["allowed"]


def test_comparison(plan: dict) -> None:
    """Plan comparison names status changes/removals; it is not live drift collection."""
    before = assess(load(plan))
    plan["resource_changes"][0]["change"]["after"]["enable_dns_support"] = False
    after = assess(load(plan))
    assert compare(before, after)["changes"] == [
        {"address": "aws_vpc.sample", "control": "vpc-dns", "before": "PASS", "after": "FAIL"}
    ]
    assert not compare(before, before)["changes"]
    fewer = copy.deepcopy(before)
    fewer["findings"].pop()
    assert compare(before, fewer)["changes"][0]["after"] is None


@pytest.mark.parametrize(
    "report",
    [{}, {"schema": 1, "findings": [None]}, {"schema": 1, "findings": [{"status": "BAD"}]}],
)
def test_invalid_reports(report: dict) -> None:
    """Comparison refuses malformed statuses."""
    with pytest.raises(ValueError):
        compare(report, report)


def test_duplicate_report(plan: dict) -> None:
    """Duplicate control identity cannot replace an earlier finding."""
    report = assess(load(plan))
    report["findings"].append(copy.deepcopy(report["findings"][0]))
    with pytest.raises(ValueError):
        compare(report, report)
