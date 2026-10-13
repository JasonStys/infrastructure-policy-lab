"""Validate Terraform plan changes and retain only selected non-sensitive evidence. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ACTIONS — line 68
# definition: Resource — line 80
# variable: address — line 83
# variable: kind — line 84
# variable: actions — line 85
# variable: after — line 86
# variable: unknown — line 87
# variable: sensitive — line 88
# definition: Plan — line 92
# variable: resources — line 95
# variable: drift — line 96
# variable: digest — line 97
# definition: token — line 100
# parameter: address — line 100
# parameter: value — line 100
# variable: pattern — line 102
# definition: mask_valid — line 108
# parameter: depth — line 108
# parameter: value — line 108
# variable: child — line 115
# definition: load — line 121
# parameter: value — line 121
# variable: changes — line 129
# variable: resources — line 132
# variable: addresses — line 133
# variable: item — line 134
# variable: address — line 137
# variable: kind — line 137
# variable: change — line 141
# variable: actions — line 144
# variable: a — line 145
# variable: after — line 147
# variable: sensitive — line 152
# variable: unknown — line 152
# variable: drift_items — line 156
# variable: drift — line 159
# variable: item — line 160
# parameter: r — line 165
# definition: field — line 171
# parameter: path — line 171
# parameter: resource — line 171
# variable: value — line 173
# variable: sensitive — line 174
# variable: unknown — line 174
# variable: key — line 175
# variable: value — line 179
# variable: unknown — line 182
# variable: sensitive — line 183
# definition: marked — line 187
# parameter: mask — line 187
# variable: child — line 191
# definition: descend_mask — line 194
# parameter: key — line 194
# parameter: mask — line 194
# END CODE MAP

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from assurance.io import canonical

ACTIONS = {
    ("no-op",),
    ("create",),
    ("update",),
    ("delete",),
    ("delete", "create"),
    ("create", "delete"),
    ("read",),
}


@dataclass(frozen=True)
class Resource:
    """Validated managed resource change: address/type, actions, values and uncertainty/sensitivity masks."""

    address: str
    kind: str
    actions: tuple[str, ...]
    after: dict[str, Any] | None
    unknown: Any
    sensitive: Any


@dataclass(frozen=True)
class Plan:
    """Plan identity uses a local semantic digest, never an authenticity or freshness guarantee."""

    resources: tuple[Resource, ...]
    drift: tuple[str, ...]
    digest: str


def token(value: Any, address: bool = False) -> str:
    """Validate bounded display tokens while permitting Terraform module/index address notation."""
    pattern = r'[A-Za-z0-9_.\[\]"-]{1,200}' if address else r"[A-Za-z0-9_]{1,100}"
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise ValueError("invalid resource token")
    return value


def mask_valid(value: Any, depth: int = 0) -> None:
    """Unknown/sensitive masks contain only booleans and bounded nested objects/lists; no truthy coercion."""
    if depth > 32:
        raise ValueError("mask nesting exceeded")
    if type(value) is bool:
        return
    if isinstance(value, (dict, list)):
        for child in value.values() if isinstance(value, dict) else value:
            mask_valid(child, depth + 1)
        return
    raise ValueError("invalid unknown/sensitive mask")


def load(value: Any) -> Plan:
    """Accept plan-format major 1, explicit managed changes and drift; reject empty/truncated/error evidence."""
    if not isinstance(value, dict) or not re.fullmatch(
        r"1\.\d+", str(value.get("format_version", ""))
    ):
        raise ValueError("unsupported plan format")
    if value.get("errored", False) is not False or value.get("complete", True) is not True:
        raise ValueError("errored or incomplete plan")
    changes = value.get("resource_changes")
    if not isinstance(changes, list) or not 1 <= len(changes) <= 2000:
        raise ValueError("require 1–2000 explicit resource changes")
    resources = []
    addresses: set[str] = set()
    for item in changes:
        if not isinstance(item, dict) or item.get("mode") != "managed":
            raise ValueError("only explicit managed changes supported")
        address, kind = token(item.get("address"), True), token(item.get("type"))
        if address in addresses:
            raise ValueError("duplicate resource address")
        addresses.add(address)
        change = item.get("change")
        if not isinstance(change, dict) or not isinstance(change.get("actions"), list):
            raise ValueError("missing change actions")
        actions = tuple(change["actions"])
        if any(not isinstance(a, str) for a in actions) or actions not in ACTIONS:
            raise ValueError("unsupported change actions")
        after = change.get("after")
        if (actions == ("delete",) and after is not None) or (
            actions != ("delete",) and not isinstance(after, dict)
        ):
            raise ValueError("after must match change actions")
        unknown, sensitive = change.get("after_unknown", {}), change.get("after_sensitive", {})
        mask_valid(unknown)
        mask_valid(sensitive)
        resources.append(Resource(address, kind, actions, after, unknown, sensitive))
    drift_items = value.get("resource_drift", [])
    if not isinstance(drift_items, list) or len(drift_items) > 2000:
        raise ValueError("invalid drift list")
    drift = tuple(
        sorted({token(item.get("address"), True) for item in drift_items if isinstance(item, dict)})
    )
    if len(drift) != len(drift_items):
        raise ValueError("duplicate or malformed drift evidence")
    return Plan(
        tuple(sorted(resources, key=lambda r: r.address)),
        drift,
        hashlib.sha256(canonical(value).encode()).hexdigest(),
    )


def field(resource: Resource, path: tuple[str | int, ...]) -> Any:
    """Return a selected field only when present, known and not masked sensitive at any ancestor."""
    value: Any = resource.after
    unknown, sensitive = resource.unknown, resource.sensitive
    for key in path:
        if unknown is True or sensitive is True:
            return None
        try:
            value = value[key]
        except (KeyError, IndexError, TypeError):
            return None
        unknown = descend_mask(unknown, key)
        sensitive = descend_mask(sensitive, key)
    return None if marked(unknown) or marked(sensitive) else value


def marked(mask: Any) -> bool:
    """A selected compound field is uncertain/private when any of its descendants is marked."""
    if type(mask) is bool:
        return mask
    return any(marked(child) for child in (mask.values() if isinstance(mask, dict) else mask))


def descend_mask(mask: Any, key: str | int) -> Any:
    """Absent mask paths mean unmarked; parent true remains blocking; structural mismatch blocks conservatively."""
    if type(mask) is bool:
        return mask
    if isinstance(mask, dict):
        return mask.get(str(key), False)
    if isinstance(mask, list) and isinstance(key, int):
        return mask[key] if key < len(mask) else False
    return True
