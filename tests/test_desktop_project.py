"""Independent graphical plan/cost/worklist oracles, stale receipts and cumulative actual review. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: state — line 87
# parameter: tmp_path — line 87
# variable: value — line 89
# definition: run — line 94
# parameter: parameters — line 94
# parameter: state — line 94
# parameter: tmp_path — line 94
# variable: stage — line 96
# variable: files — line 98
# variable: kind — line 98
# variable: summary — line 98
# variable: identity — line 99
# definition: test_assessment_comparison_decimal_cost_and_unknowns — line 103
# parameter: state — line 103
# parameter: tmp_path — line 103
# variable: _ — line 105
# variable: files — line 105
# variable: views — line 105
# variable: report — line 106
# variable: _ — line 109
# variable: files — line 109
# variable: _ — line 111
# variable: files — line 111
# variable: views — line 111
# variable: row — line 114
# variable: _ — line 115
# variable: files — line 115
# definition: test_selected_cumulative_reasoned_review_keeps_original_gate_and_evidence — line 119
# parameter: state — line 119
# parameter: tmp_path — line 119
# variable: parameters — line 121
# variable: original — line 122
# variable: original_id — line 122
# variable: views — line 122
# variable: work — line 123
# variable: required — line 125
# variable: row — line 125
# variable: row — line 127
# variable: _ — line 139
# variable: first — line 139
# variable: first_report — line 140
# variable: _ — line 145
# variable: second — line 145
# variable: views — line 145
# variable: report — line 146
# variable: row — line 152
# definition: test_review_errors_cannot_be_guessed_or_override_evidence — line 168
# parameter: defect — line 168
# parameter: state — line 168
# parameter: tmp_path — line 168
# variable: parameters — line 170
# variable: _ — line 171
# variable: original — line 171
# variable: views — line 171
# variable: count — line 196
# variable: stage — line 197
# definition: test_external_receipt_requires_current_digest_and_excludes_raw_plan_secrets — line 204
# parameter: state — line 204
# parameter: tmp_path — line 204
# variable: value — line 206
# variable: source — line 208
# variable: parameters — line 210
# variable: _ — line 211
# variable: files — line 211
# variable: raw — line 212
# variable: template — line 213
# variable: external — line 214
# variable: _ — line 217
# variable: receipt — line 217
# definition: test_literal_cells_and_safe_comparison_markup — line 229
# variable: row — line 231
# variable: files — line 238
# END CODE MAP

import json

import pytest

from assurance import desktop_project as project
from assurance.desktop_io import Rejected, canonical, json_value
from assurance.desktop_state import Workspace


@pytest.fixture
def state(tmp_path):
    """Use a fresh marked profile, never actual accounts, cloud state or the default workspace."""
    value = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    yield value
    value.close()


def run(state, tmp_path, parameters):
    """Retain actual core outputs only after the adapter completes, matching the normal GUI worker."""
    stage = tmp_path / f"stage-{len(state.history())}"
    stage.mkdir()
    kind, summary, files = project.analyze(state, parameters, stage)
    identity = state.save(kind, summary, parameters, files)
    return identity, files, project.views(files)


def test_assessment_comparison_decimal_cost_and_unknowns(state, tmp_path):
    """The authored independent fixtures retain16/14PASS, two differences and the exact $1.55 scenario total."""
    _, files, views = run(state, tmp_path, project.scenario(project.SCENARIOS[1]))
    report = json_value(files["report.json"])
    assert report["counts"] == {"PASS": 14, "FAIL": 2, "UNKNOWN": 0, "REVIEW": 0}
    assert report["allowed"] is False and len(views["Selected-control findings"]) == 16
    _, files, _ = run(state, tmp_path, project.scenario(project.SCENARIOS[2]))
    assert len(json_value(files["result.json"])["changes"]) == 2
    _, files, views = run(state, tmp_path, project.scenario(project.SCENARIOS[4]))
    assert json_value(files["result.json"])["total_usd"] == "1.55"
    assert len(views["Supplied cost items (not a bill)"]) > 0
    assert all(project.cells(row)[-1] == "EXCLUDED" for row in views["Explicit cost exclusions"])
    _, files, _ = run(state, tmp_path, project.scenario(project.SCENARIOS[5]))
    assert json_value(files["report.json"])["counts"]["UNKNOWN"] > 0


def test_selected_cumulative_reasoned_review_keeps_original_gate_and_evidence(state, tmp_path):
    """Two user decisions accumulate against the same actual worklist without rewriting the original blocked plan."""
    parameters = project.scenario(project.SCENARIOS[3])
    original_id, original, views = run(state, tmp_path, parameters)
    work = json_value(original["review.json"])
    assert work["allowed"] is False and len(work["required_addresses"]) == 10
    required = [row for row in views["Resource change worklist"] if row["review_required"]]
    assert (
        next(row for row in required if row["address"] == "aws_vpc.sample")["change_kind"]
        == "replace-delete-first"
    )
    parameters.update(
        mode=project.REVIEW_MODE,
        _run=str(original_id),
        _row=canonical(required[0]).decode(),
        reviewer="fictional-owner",
        ticket="LAB-101",
        decision="acknowledged",
        reason="Independently reviewed fictional dependency/recovery evidence; no deployment authorized.",
    )
    _, first, _ = run(state, tmp_path, parameters)
    first_report = json_value(first["review.json"])
    assert len(first_report["decisions"]) == 1 and len(first_report["unreviewed_addresses"]) == 9
    assert first_report["allowed"] is False
    parameters["_row"] = canonical(required[1]).decode()
    parameters["decision"] = "defer"
    _, second, views = run(state, tmp_path, parameters)
    report = json_value(second["review.json"])
    assert len(report["decisions"]) == 2 and len(report["unreviewed_addresses"]) == 8
    assert report["all_required_acknowledged"] is False and report["allowed"] is False
    assert len(views["Asserted resource decisions"]) == 2
    assert state.files(original_id) == original and state.files(2) == first
    assert all(
        "acknowledged" not in project.cells(row)[-1] for row in views["Selected-control findings"]
    )


@pytest.mark.parametrize(
    "defect",
    [
        "stale-plan",
        "made-up-row",
        "no-selected-run",
        "wrong-source-kind",
        "bad-decision",
        "missing-reviewer",
        "missing-reason",
    ],
)
def test_review_errors_cannot_be_guessed_or_override_evidence(state, tmp_path, defect):
    """Stale bindings, selection mistakes and missing justification never produce an apparently approved receipt."""
    parameters = project.scenario(project.SCENARIOS[0])
    _, original, views = run(state, tmp_path, parameters)
    parameters.update(
        mode=project.REVIEW_MODE,
        _run="1",
        _row=canonical(views["Resource change worklist"][0]).decode(),
        reviewer="fictional-owner",
        ticket="LAB-101",
        decision="acknowledged",
        reason="Reviewed fictional resource evidence.",
    )
    if defect == "stale-plan":
        parameters["plan"] = str(project.ROOT / "examples/insecure.json")
    elif defect == "made-up-row":
        parameters["_row"] = '{"address":"aws_vpc.made_up","review_required":true}'
    elif defect == "no-selected-run":
        parameters["_run"] = "NaN"
    elif defect == "wrong-source-kind":
        run(state, tmp_path, project.scenario(project.SCENARIOS[4]))
        parameters["_run"] = "2"
    elif defect == "bad-decision":
        parameters["decision"] = "deploy-now"
    elif defect == "missing-reviewer":
        parameters["reviewer"] = ""
    else:
        parameters["reason"] = ""
    count = len(state.history())
    stage = tmp_path / "rejected-stage"
    stage.mkdir()
    with pytest.raises((Rejected, ValueError)):
        project.analyze(state, parameters, stage)
    assert len(state.history()) == count and state.files(1) == original


def test_external_receipt_requires_current_digest_and_excludes_raw_plan_secrets(state, tmp_path):
    """An independently editable template must remain source-bound; ignored sensitive raw fields never enter exports."""
    value = json.loads((project.ROOT / "examples/healthy.json").read_text())
    value["resource_changes"][0]["change"]["after"]["secret"] = "SYNTHETIC-PRIVATE-SENTINEL"
    source = tmp_path / "authorized-plan.json"
    source.write_text(json.dumps(value))
    parameters = {**project.scenario(project.SCENARIOS[0]), "plan": str(source)}
    _, files, _ = run(state, tmp_path, parameters)
    assert all(b"SYNTHETIC-PRIVATE-SENTINEL" not in raw for raw in files.values())
    template = json_value(files["decisions-template.json"])
    external = tmp_path / "decisions.json"
    external.write_bytes(canonical(template))
    parameters.update(mode=project.MODES[5], receipt=str(external))
    _, receipt, _ = run(state, tmp_path, parameters)
    assert json_value(receipt["review.json"])["all_required_acknowledged"] is False
    template["worklist_digest"] = "0" * 64
    external.write_bytes(canonical(template))
    with pytest.raises(ValueError):
        project.analyze(state, parameters, tmp_path)
    with pytest.raises(Rejected):
        project.scenario("unknown")
    with pytest.raises(Rejected):
        project.analyze(state, {**parameters, "mode": "unknown"}, tmp_path)


def test_literal_cells_and_safe_comparison_markup():
    """No user-controlled label becomes executable markup or a command; exact decimal strings stay readable."""
    row = {
        "address": "<script>fictional</script>",
        "control": "gate",
        "before": "PASS",
        "after": "FAIL",
    }
    assert project.cells(row)[-1] == "PASS → FAIL"
    files = project.text_bundle({"changes": [row]}, "<script>fictional</script>")
    assert b"<script>fictional</script>" not in files["result.html"]
    assert b"&lt;script&gt;fictional&lt;/script&gt;" in files["result.html"]
