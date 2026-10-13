"""Generate independently labeled, strictly fictional Terraform-like plans and cost scenarios. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 42
# definition: fixture — line 45
# variable: changes — line 47
# variable: checks — line 48
# variable: kind — line 48
# variable: after — line 49
# variable: _ — line 50
# variable: expected — line 50
# variable: path — line 50
# variable: target — line 51
# variable: current — line 52
# variable: following — line 52
# variable: target — line 56
# variable: target — line 58
# variable: last — line 59
# variable: after — line 68
# definition: main — line 111
# variable: directory — line 113
# variable: healthy — line 115
# variable: insecure — line 116
# variable: resource — line 117
# variable: unknown — line 122
# variable: destructive — line 124
# variable: drifted — line 126
# variable: unsupported — line 128
# variable: name — line 130
# variable: plan — line 130
# variable: scenario — line 139
# END CODE MAP

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from assurance.io import canonical
from assurance.policy import CHECKS

ROOT = Path(__file__).resolve().parents[1]


def fixture() -> dict[str, Any]:
    """Build a small plan with all authored controls; source is synthetic, never exported cloud state."""
    changes = []
    for kind, checks in CHECKS.items():
        after: dict[str, Any] = {}
        for path, expected, _ in checks:
            target: Any = after
            for current, following in zip(path[:-1], path[1:], strict=False):
                if isinstance(current, int):
                    while len(target) <= current:
                        target.append({})
                    target = target[current]
                else:
                    target = target.setdefault(current, [] if isinstance(following, int) else {})
            last = path[-1]
            target[last] = copy.deepcopy(expected)
        if kind == "aws_kms_key":
            after["arn"] = "arn:aws:kms:us-west-2:123456789012:key/fictional-key"
        if kind == "aws_s3_bucket_server_side_encryption_configuration":
            after["rule"][0]["apply_server_side_encryption_by_default"][0]["kms_master_key_id"] = (
                "arn:aws:kms:us-west-2:123456789012:key/fictional-key"
            )
        if kind == "aws_s3_bucket_policy":
            after = {
                "bucket": "fictional-evidence-lab",
                "policy": canonical(
                    {
                        "Statement": [
                            {
                                "Effect": "Deny",
                                "Principal": "*",
                                "Action": "s3:*",
                                "Resource": [
                                    "arn:aws:s3:::fictional-evidence-lab",
                                    "arn:aws:s3:::fictional-evidence-lab/*",
                                ],
                                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
                            }
                        ]
                    }
                ),
            }
        changes.append(
            {
                "address": f"{kind}.sample",
                "mode": "managed",
                "type": kind,
                "change": {
                    "actions": ["create"],
                    "before": None,
                    "after": after,
                    "after_unknown": {},
                    "after_sensitive": {},
                },
            }
        )
    return {
        "format_version": "1.2",
        "terraform_version": "1.16.5",
        "complete": True,
        "errored": False,
        "resource_changes": changes,
        "resource_drift": [],
    }


def main() -> None:
    """Write public fictional examples only; deliberately insecure/unknown/destructive cases are labeled."""
    directory = ROOT / "examples"
    directory.mkdir(exist_ok=True)
    healthy = fixture()
    insecure = copy.deepcopy(healthy)
    for resource in insecure["resource_changes"]:
        if resource["type"] == "aws_subnet":
            resource["change"]["after"]["map_public_ip_on_launch"] = True
        if resource["type"] == "aws_s3_bucket_public_access_block":
            resource["change"]["after"]["block_public_policy"] = False
    unknown = copy.deepcopy(healthy)
    unknown["resource_changes"][0]["change"]["after_sensitive"] = True
    destructive = copy.deepcopy(healthy)
    destructive["resource_changes"][0]["change"]["actions"] = ["delete", "create"]
    drifted = copy.deepcopy(healthy)
    drifted["resource_drift"] = [{"address": "aws_subnet.sample"}]
    unsupported = copy.deepcopy(healthy)
    unsupported["resource_changes"][0]["type"] = "aws_instance"
    for name, plan in {
        "healthy": healthy,
        "insecure": insecure,
        "unknown": unknown,
        "destructive": destructive,
        "drifted": drifted,
        "unsupported": unsupported,
    }.items():
        (directory / f"{name}.json").write_text(canonical(plan) + "\n", encoding="utf-8")
    scenario = {
        "schema": 1,
        "currency": "USD",
        "label": "Illustrative synthetic monthly workload; rates are not an AWS quote",
        "items": [
            {"name": "key-month", "quantity": "1", "unit_price": "1.00", "unit": "key-month"},
            {"name": "storage", "quantity": "20", "unit_price": "0.025", "unit": "GB-month"},
            {"name": "requests", "quantity": "10", "unit_price": "0.005", "unit": "1000 requests"},
        ],
        "exclusions": [
            "Taxes, regional/tier changes, version retention, KMS requests, transfer, logs, support and all unlisted usage.",
            "Illustrative supplied rates are not verified current AWS rates.",
        ],
    }
    (directory / "cost.json").write_text(canonical(scenario) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
