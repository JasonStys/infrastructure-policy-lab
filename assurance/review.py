"""Digest-bound resource change worklists and asserted reviewer receipts. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: KINDS — line 54
# definition: worklist — line 65
# parameter: plan — line 65
# variable: assessment — line 67
# variable: findings — line 68
# variable: finding — line 69
# variable: resource — line 71
# variable: resources — line 71
# variable: rows — line 72
# variable: address — line 73
# variable: resource — line 74
# variable: checks — line 75
# variable: kind — line 76
# variable: finding — line 77
# variable: reasons — line 77
# variable: result — line 91
# variable: row — line 95
# definition: template — line 102
# parameter: result — line 102
# definition: receipt — line 112
# parameter: plan — line 112
# parameter: value — line 112
# variable: result — line 115
# variable: required — line 127
# variable: decisions — line 128
# variable: row — line 129
# variable: key — line 142
# variable: address — line 145
# variable: address — line 156
# variable: row — line 160
# definition: export — line 165
# parameter: output — line 165
# parameter: result — line 165
# variable: rows — line 167
# variable: key — line 171
# variable: row — line 180
# variable: text — line 182
# variable: page — line 183
# END CODE MAP

from __future__ import annotations

import hashlib
import html
from pathlib import Path
from typing import Any

from assurance.io import bounded, canonical, new_directory
from assurance.plan import Plan
from assurance.policy import assess

KINDS = {
    ("create",): "create",
    ("update",): "update",
    ("delete",): "delete",
    ("delete", "create"): "replace-delete-first",
    ("create", "delete"): "replace-create-first",
    ("no-op",): "no-op",
    ("read",): "read",
}


def worklist(plan: Plan) -> dict[str, Any]:
    """Build O(resources+findings) metadata-only work; raw Terraform values never enter the result."""
    assessment = assess(plan)
    findings: dict[str, list[dict[str, Any]]] = {}
    for finding in assessment["findings"]:
        findings.setdefault(finding["address"], []).append(finding)
    resources = {resource.address: resource for resource in plan.resources}
    rows = []
    for address in sorted(resources.keys() | findings.keys()):
        resource = resources.get(address)
        checks = findings.get(address, [])
        kind = KINDS[resource.actions] if resource else "drift-only"
        reasons = sorted({finding["status"] for finding in checks if finding["status"] != "PASS"})
        if kind not in ("no-op", "read"):
            reasons.append("proposed-change" if resource else "reported-drift")
        rows.append(
            {
                "address": address,
                "resource_type": resource.kind if resource else None,
                "change_kind": kind,
                "actions": list(resource.actions) if resource else [],
                "findings": checks,
                "review_required": bool(reasons),
                "review_reasons": reasons,
            }
        )
    result = {
        **assessment,
        "kind": "change_review_worklist",
        "worklist": rows,
        "required_addresses": [row["address"] for row in rows if row["review_required"]],
        "scope": "Local selected-control review metadata; no authentication, cloud calls, apply or deployment authorization.",
    }
    result["worklist_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def template(result: dict[str, Any]) -> dict[str, Any]:
    """Bind an empty editable receipt to the exact semantic plan and worklist; no prefilled approvals."""
    return {
        "schema": 1,
        "plan_digest": result["plan_digest"],
        "worklist_digest": result["worklist_digest"],
        "decisions": [],
    }


def receipt(plan: Plan, value: Any) -> dict[str, Any]:
    """Accept unique reasoned decisions only for current required work; never override the original gate."""
    bounded(value)
    result = worklist(plan)
    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "plan_digest", "worklist_digest", "decisions"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
        or value["plan_digest"] != result["plan_digest"]
        or value["worklist_digest"] != result["worklist_digest"]
        or not isinstance(value["decisions"], list)
        or len(value["decisions"]) > 4000
    ):
        raise ValueError("receipt does not match current plan/worklist")
    required = set(result["required_addresses"])
    decisions = {}
    for row in value["decisions"]:
        if not isinstance(row, dict) or set(row) != {
            "address",
            "decision",
            "reviewer",
            "ticket",
            "reason",
        }:
            raise ValueError("invalid decision fields")
        if not all(
            isinstance(row[key], str)
            and row[key].strip()
            and 1 <= len(row[key]) <= (500 if key == "reason" else 200)
            for key in row
        ):
            raise ValueError("decision fields must be bounded nonempty text")
        address = row["address"]
        if (
            address not in required
            or address in decisions
            or row["decision"] not in ("acknowledged", "defer", "reject")
        ):
            raise ValueError("unknown, duplicate or invalid decision")
        decisions[address] = row
    return {
        **result,
        "kind": "asserted_change_review_receipt",
        "decisions": [decisions[address] for address in sorted(decisions)],
        "unreviewed_addresses": sorted(required - decisions.keys()),
        "all_required_reviewed": required <= decisions.keys(),
        "all_required_acknowledged": required <= decisions.keys()
        and all(row["decision"] == "acknowledged" for row in decisions.values()),
        "identity_limit": "Reviewer/ticket/reason are local assertions, not signatures. Original allowed status is unchanged; acknowledgement cannot authorize deployment.",
    }


def export(result: dict[str, Any], output: Path) -> None:
    """Create a new private immutable bundle with escaped resource work and full decision context."""
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row[key]))}</td>"
            for key in (
                "address",
                "resource_type",
                "change_kind",
                "review_required",
                "review_reasons",
            )
        )
        + "</tr>"
        for row in result["worklist"]
    )
    text = canonical(result)
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; base-uri 'none'; form-action 'none'\">"
        "<title>Infrastructure change review — Jason Stys</title><main><h1>Infrastructure change worklist</h1>"
        "<p>Created by Jason Stys. Assertions only; not deployment authorization.</p>"
        f"<p>Original selected-control gate allowed: {result['allowed']}. Required resources: {len(result['required_addresses'])}.</p>"
        "<table><caption>Metadata-only resource changes</caption><thead><tr><th>Address</th><th>Type</th><th>Change</th><th>Review required</th><th>Reasons</th></tr></thead><tbody>"
        + rows
        + "</tbody></table><details><summary>Exact digests, findings and decisions</summary><pre>"
        + html.escape(text)
        + "</pre></details></main></html>"
    )
    new_directory(output)
    (output / "review.json").write_text(text + "\n", encoding="utf-8")
    (output / "review.html").write_text(page, encoding="utf-8")
    (output / "decisions-template.json").write_text(
        canonical(template(result)) + "\n", encoding="utf-8"
    )
