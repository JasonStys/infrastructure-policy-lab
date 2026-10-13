"""Deterministic selected-control plan gate; unknown/deletion/unsupported resources cannot pass. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: CHECKS — line 81
# variable: key — line 91
# definition: tls_deny — line 124
# parameter: bucket — line 124
# parameter: value — line 124
# variable: document — line 129
# variable: statements — line 130
# variable: required — line 133
# variable: s — line 142
# definition: evidence — line 148
# parameter: plan — line 148
# variable: checks — line 150
# variable: key_values — line 151
# variable: r — line 151
# variable: key — line 152
# variable: keys — line 152
# variable: key — line 153
# variable: keys_uncertain — line 153
# variable: resource — line 154
# variable: _ — line 173
# variable: control — line 173
# variable: path — line 173
# variable: value — line 174
# variable: value — line 177
# variable: value — line 179
# variable: value — line 181
# variable: bucket — line 183
# variable: value — line 184
# variable: address — line 193
# definition: Finding — line 201
# variable: address — line 204
# variable: control — line 205
# variable: status — line 206
# variable: message — line 207
# definition: assess — line 210
# parameter: plan — line 210
# variable: findings — line 212
# variable: expected_values — line 213
# variable: _ — line 214
# variable: checks — line 214
# variable: control — line 214
# variable: expected — line 214
# variable: check — line 216
# variable: control — line 217
# variable: value — line 217
# variable: status — line 219
# variable: status — line 221
# variable: expected — line 223
# variable: status — line 224
# parameter: row — line 235
# variable: f — line 235
# variable: rows — line 235
# variable: counts — line 236
# variable: r — line 237
# variable: status — line 238
# variable: row — line 244
# definition: compare — line 251
# parameter: after — line 251
# parameter: before — line 251
# definition: index — line 254
# parameter: report — line 254
# variable: result — line 258
# variable: row — line 259
# variable: key — line 267
# variable: new — line 273
# variable: old — line 273
# variable: key — line 278
# END CODE MAP

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from assurance.io import parse
from assurance.plan import Plan, field

# Each tuple states a field path, exact expected value and stable review control ID.
CHECKS: dict[str, list[tuple[tuple[str | int, ...], Any, str]]] = {
    "aws_vpc": [(("enable_dns_support",), True, "vpc-dns")],
    "aws_subnet": [(("map_public_ip_on_launch",), False, "subnet-private")],
    "aws_security_group": [
        (("ingress",), [], "sg-ingress-deny"),
        (("egress",), [], "sg-egress-deny"),
    ],
    "aws_s3_bucket": [(("force_destroy",), False, "bucket-preserve")],
    "aws_s3_bucket_public_access_block": [
        ((key,), True, "s3-" + key)
        for key in (
            "block_public_acls",
            "block_public_policy",
            "ignore_public_acls",
            "restrict_public_buckets",
        )
    ],
    "aws_s3_bucket_versioning": [
        (("versioning_configuration", 0, "status"), "Enabled", "s3-versioning")
    ],
    "aws_s3_bucket_server_side_encryption_configuration": [
        (
            ("rule", 0, "apply_server_side_encryption_by_default", 0, "sse_algorithm"),
            "aws:kms",
            "s3-kms",
        ),
        (
            ("rule", 0, "apply_server_side_encryption_by_default", 0, "kms_master_key_id"),
            True,
            "s3-kms-key-scoped",
        ),
    ],
    "aws_s3_bucket_ownership_controls": [
        (("rule", 0, "object_ownership"), "BucketOwnerEnforced", "s3-owner")
    ],
    "aws_s3_bucket_policy": [(("policy",), True, "s3-tls-deny")],
    "aws_kms_key": [
        (("enable_key_rotation",), True, "kms-rotation"),
        (("deletion_window_in_days",), 30, "kms-deletion-window"),
    ],
}


def tls_deny(value: Any, bucket: Any) -> bool:
    """Recognize a scoped explicit all-principal HTTP deny covering this bucket and objects, not just any deny."""
    if not isinstance(value, str) or not isinstance(bucket, str) or not bucket:
        return False
    try:
        document = parse(value)
        statements = document["Statement"]
        if not isinstance(statements, list):
            return False
        required = {f"arn:aws:s3:::{bucket}", f"arn:aws:s3:::{bucket}/*"}
        return any(
            isinstance(s, dict)
            and s.get("Effect") == "Deny"
            and s.get("Principal") == "*"
            and s.get("Action") == "s3:*"
            and isinstance(s.get("Resource"), list)
            and set(s["Resource"]) == required
            and s.get("Condition") == {"Bool": {"aws:SecureTransport": "false"}}
            for s in statements
        )
    except (ValueError, TypeError, KeyError):
        return False


def evidence(plan: Plan) -> dict[str, Any]:
    """Produce narrow shared policy inputs: critical field values only; redact masked values before export."""
    checks = []
    key_values = [field(r, ("arn",)) for r in plan.resources if r.kind == "aws_kms_key"]
    keys = {key for key in key_values if isinstance(key, str)}
    keys_uncertain = any(key is None for key in key_values)
    for resource in plan.resources:
        if "delete" in resource.actions:
            checks.append(
                {
                    "address": resource.address,
                    "control": "destructive-change",
                    "known": True,
                    "value": True,
                }
            )
        if resource.kind not in CHECKS:
            checks.append(
                {
                    "address": resource.address,
                    "control": "unsupported-resource",
                    "known": False,
                    "value": None,
                }
            )
        for path, _, control in CHECKS.get(resource.kind, []):
            value = field(resource, path)
            if control == "s3-kms-key-scoped" and value is not None:
                if not isinstance(value, str) or not value.startswith("arn:aws:kms:"):
                    value = False
                elif value in keys:
                    value = True
                else:
                    value = None if keys_uncertain else False
            if control == "s3-tls-deny" and value is not None:
                bucket = field(resource, ("bucket",))
                value = tls_deny(value, bucket) if bucket is not None else None
            checks.append(
                {
                    "address": resource.address,
                    "control": control,
                    "known": value is not None,
                    "value": value,
                }
            )
    for address in plan.drift:
        checks.append(
            {"address": address, "control": "observed-drift", "known": True, "value": True}
        )
    return {"schema": 1, "checks": checks}


@dataclass(frozen=True)
class Finding:
    """Control status is PASS/FAIL/UNKNOWN/REVIEW with no raw resource values or credentials."""

    address: str
    control: str
    status: str
    message: str


def assess(plan: Plan) -> dict[str, Any]:
    """Assess selected paths and sort C findings in O(R+C log C); unknown/destructive changes cannot pass."""
    findings = []
    expected_values = {
        control: expected for checks in CHECKS.values() for _, expected, control in checks
    }
    for check in evidence(plan)["checks"]:
        control, value = check["control"], check["value"]
        if control in {"destructive-change", "observed-drift"}:
            status = "REVIEW"
        elif not check["known"] or control not in expected_values:
            status = "UNKNOWN"
        else:
            expected = expected_values[control]
            status = "PASS" if type(value) is type(expected) and value == expected else "FAIL"
        findings.append(
            Finding(
                check["address"],
                control,
                status,
                "Matches authored baseline."
                if status == "PASS"
                else "Requires private plan review: mismatched, unknown, sensitive, unsupported, destructive or drift evidence.",
            )
        )
    rows = sorted((asdict(f) for f in findings), key=lambda row: (row["address"], row["control"]))
    counts = {
        status: sum(r["status"] == status for r in rows)
        for status in ("PASS", "FAIL", "UNKNOWN", "REVIEW")
    }
    return {
        "schema": 1,
        "author": "Jason Stys",
        "plan_digest": plan.digest,
        "allowed": all(row["status"] == "PASS" for row in rows),
        "counts": counts,
        "findings": rows,
        "scope": "Selected authored controls; not deployment authorization or complete cloud assurance.",
    }


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compare reviewed reports by address/control; report added/removed/changed checks, never actual live drift."""

    def index(report: dict[str, Any]) -> dict[tuple[str, str], str]:
        """Validate an internal report index instead of trusting arbitrary caller report strings."""
        if report.get("schema") != 1 or not isinstance(report.get("findings"), list):
            raise ValueError("invalid report")
        result = {}
        for row in report["findings"]:
            if not isinstance(row, dict) or row.get("status") not in {
                "PASS",
                "FAIL",
                "UNKNOWN",
                "REVIEW",
            }:
                raise ValueError("invalid finding")
            key = (row["address"], row["control"])
            if key in result:
                raise ValueError("duplicate report finding")
            result[key] = row["status"]
        return result

    old, new = index(before), index(after)
    return {
        "schema": 1,
        "changes": [
            {"address": key[0], "control": key[1], "before": old.get(key), "after": new.get(key)}
            for key in sorted(old.keys() | new.keys())
            if old.get(key) != new.get(key)
        ],
        "scope": "Two plan assessments, not a live AWS inventory.",
    }
