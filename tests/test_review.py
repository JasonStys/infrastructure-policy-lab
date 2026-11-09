"""Independent change-shape, stale-review, redaction and user workflow tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: proposed — line 58
# variable: changes — line 60
# variable: actions — line 61
# variable: name — line 61
# definition: decision — line 91
# parameter: address — line 91
# parameter: kind — line 91
# definition: test_change_work_and_redaction — line 102
# variable: result — line 104
# variable: indexed — line 105
# variable: row — line 105
# definition: test_partial_and_complete_receipts_never_override_policy — line 118
# variable: plan — line 120
# variable: result — line 121
# variable: value — line 122
# variable: partial — line 124
# variable: address — line 127
# variable: full — line 128
# definition: test_stale_or_ambiguous_decisions_refused — line 152
# parameter: bad — line 152
# variable: plan — line 154
# variable: value — line 155
# variable: row — line 156
# variable: changed — line 178
# definition: test_real_user_worklist_template_receipt — line 184
# parameter: capsys — line 185
# parameter: tmp_path — line 185
# variable: source — line 188
# variable: original — line 190
# variable: output — line 191
# variable: result — line 193
# variable: value — line 194
# variable: address — line 195
# variable: decisions — line 197
# variable: args — line 199
# variable: reviewed — line 208
# variable: page — line 213
# definition: test_passing_plan_still_has_proposal_review — line 220
# variable: plan — line 222
# variable: result — line 223
# variable: no_change — line 226
# END CODE MAP

import copy
import json
from pathlib import Path

import pytest

from assurance.cli import main
from assurance.io import read
from assurance.plan import load
from assurance.review import export, receipt, template, worklist


def proposed() -> dict[str, object]:
    """Independent small VPC proposal spanning known, unsupported, replacement and drift-only changes."""
    changes = []
    for name, actions in (
        ("created", ["create"]),
        ("updated", ["update"]),
        ("deleted", ["delete"]),
        ("replaced", ["delete", "create"]),
        ("rotated", ["create", "delete"]),
        ("stable", ["no-op"]),
        ("read", ["read"]),
    ):
        changes.append(
            {
                "address": f"aws_vpc.{name}",
                "type": "aws_vpc",
                "mode": "managed",
                "change": {
                    "actions": actions,
                    "after": None
                    if actions == ["delete"]
                    else {"enable_dns_support": True, "secret": "PRIVATE-SENTINEL"},
                    "after_sensitive": {"secret": True},
                },
            }
        )
    return {
        "format_version": "1.2",
        "resource_changes": changes,
        "resource_drift": [{"address": "aws_vpc.drift_only"}],
    }


def decision(address: str, kind: str = "acknowledged") -> dict[str, str]:
    """Record explicit reviewer context without presenting it as a signed identity or authorization."""
    return {
        "address": address,
        "decision": kind,
        "reviewer": "Fictional platform reviewer",
        "ticket": "CHG-201",
        "reason": "Reviewed the private plan with the service owner; separate deployment approval is required.",
    }


def test_change_work_and_redaction() -> None:
    """Replacement order and drift-only resources remain distinct; non-changing passing items need no receipt."""
    result = worklist(load(proposed()))
    indexed = {row["address"]: row for row in result["worklist"]}
    assert indexed["aws_vpc.replaced"]["change_kind"] == "replace-delete-first"
    assert indexed["aws_vpc.rotated"]["change_kind"] == "replace-create-first"
    assert indexed["aws_vpc.deleted"]["change_kind"] == "delete"
    assert indexed["aws_vpc.drift_only"]["resource_type"] is None
    assert indexed["aws_vpc.drift_only"]["change_kind"] == "drift-only"
    assert not indexed["aws_vpc.stable"]["review_required"]
    assert not indexed["aws_vpc.read"]["review_required"]
    assert len(result["required_addresses"]) == 6
    assert result["allowed"] is False
    assert "PRIVATE-SENTINEL" not in json.dumps(result)


def test_partial_and_complete_receipts_never_override_policy() -> None:
    """Review completeness is distinct from acknowledgement and both are distinct from the policy gate."""
    plan = load(proposed())
    result = worklist(plan)
    value = template(result)
    value["decisions"] = [decision(result["required_addresses"][0], "defer")]
    partial = receipt(plan, value)
    assert len(partial["unreviewed_addresses"]) == 5
    assert not partial["all_required_reviewed"]
    value["decisions"] = [decision(address) for address in result["required_addresses"]]
    full = receipt(plan, value)
    assert full["all_required_reviewed"] and full["all_required_acknowledged"]
    assert not full["allowed"]
    assert full["counts"] == result["counts"] and full["findings"] == result["findings"]
    value["decisions"][0]["decision"] = "reject"
    assert receipt(plan, value)["all_required_reviewed"]
    assert not receipt(plan, value)["all_required_acknowledged"]


@pytest.mark.parametrize(
    "bad",
    [
        "plan",
        "worklist",
        "schema",
        "duplicate",
        "unknown",
        "action",
        "reason",
        "fields",
        "type",
        "blank",
    ],
)
def test_stale_or_ambiguous_decisions_refused(bad: str) -> None:
    """An acknowledgement cannot be replayed onto a different proposal or fabricated address."""
    plan = load(proposed())
    value = template(worklist(plan))
    row = decision("aws_vpc.created")
    value["decisions"] = [row]
    if bad in ("plan", "worklist"):
        value[bad + "_digest"] = "0" * 64
    elif bad == "schema":
        value["schema"] = True
    elif bad == "duplicate":
        value["decisions"].append(row)
    elif bad == "unknown":
        row["address"] = "aws_vpc.not_here"
    elif bad == "action":
        row["decision"] = "approve-deploy"
    elif bad == "reason":
        row["reason"] = ""
    elif bad == "fields":
        row["extra"] = "ignored?"
    elif bad == "type":
        row["ticket"] = []
    else:
        row["reason"] = "   "
    with pytest.raises(ValueError):
        receipt(plan, value)
    changed = proposed()
    changed["resource_changes"][0]["change"]["after"]["enable_dns_support"] = False
    with pytest.raises(ValueError):
        receipt(load(changed), template(worklist(plan)))


def test_real_user_worklist_template_receipt(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The actual operator CLI exports a template and retains unresolved review while preserving original input."""
    source = tmp_path / "plan.json"
    source.write_text(json.dumps(proposed()))
    original = source.read_bytes()
    output = tmp_path / "work"
    assert main(["worklist", str(source), "--out", str(output)]) == 1
    result = json.loads(capsys.readouterr().out)
    value = read(output / "decisions-template.json")
    value["decisions"] = [decision(address) for address in result["required_addresses"]]
    value["decisions"][0]["reason"] = "<script>literal text</script>"
    decisions = tmp_path / "decisions.json"
    decisions.write_text(json.dumps(value))
    args = [
        "review",
        str(source),
        "--decisions",
        str(decisions),
        "--out",
        str(tmp_path / "receipt"),
    ]
    assert main(args) == 1
    reviewed = json.loads(capsys.readouterr().out)
    assert reviewed["all_required_acknowledged"] and not reviewed["allowed"]
    assert main(args) == 2
    assert "rejected" in capsys.readouterr().err
    assert source.read_bytes() == original
    page = (tmp_path / "receipt/review.html").read_text()
    assert "<script>" not in page and "&lt;script&gt;" in page and "PRIVATE-SENTINEL" not in page
    assert "Content-Security-Policy" in page and "Jason Stys" in page
    with pytest.raises(OSError):
        export(reviewed, tmp_path / "absent/new")


def test_passing_plan_still_has_proposal_review() -> None:
    """Passing selected controls does not prefill approvals for created resources."""
    plan = load(read(Path("examples/healthy.json")))
    result = worklist(plan)
    assert result["allowed"] and result["required_addresses"]
    assert not receipt(plan, template(result))["all_required_reviewed"]
    no_change = copy.deepcopy(proposed())
    no_change["resource_drift"] = []
    no_change["resource_changes"] = [no_change["resource_changes"][-2]]
    assert receipt(load(no_change), template(worklist(load(no_change))))[
        "all_required_acknowledged"
    ]
