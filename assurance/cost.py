"""Exact-decimal scenario cost calculation with explicit exclusions; no pricing API or AWS calls. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: amount — line 25
# parameter: value — line 25
# variable: c — line 31
# variable: result — line 35
# definition: estimate — line 43
# parameter: value — line 43
# variable: s — line 58
# variable: items — line 61
# variable: rows — line 64
# variable: seen — line 64
# variable: total — line 65
# variable: item — line 66
# variable: subtotal — line 78
# variable: total — line 79
# END CODE MAP

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any


def amount(value: Any) -> Decimal:
    """Accept bounded nonnegative decimal strings only; refuse booleans, exponent/NaN and hidden float rounding."""
    if (
        not isinstance(value, str)
        or len(value) > 20
        or not value
        or any(c not in "0123456789." for c in value)
    ):
        raise ValueError("decimal string required")
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("invalid decimal") from error
    if not result.is_finite() or not 0 <= result <= Decimal("1000000"):
        raise ValueError("decimal outside allowed range")
    return result


def estimate(value: Any) -> dict[str, Any]:
    """Multiply explicit scenario quantities/prices exactly; round only final total, distinguish estimate from bill."""
    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "currency", "label", "items", "exclusions"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
        or value["currency"] != "USD"
    ):
        raise ValueError("invalid cost scenario")
    if not isinstance(value["label"], str) or not 1 <= len(value["label"]) <= 120:
        raise ValueError("invalid scenario label")
    if (
        not isinstance(value["exclusions"], list)
        or not value["exclusions"]
        or any(not isinstance(s, str) or not 1 <= len(s) <= 200 for s in value["exclusions"])
    ):
        raise ValueError("explicit exclusions required")
    items = value["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= 50:
        raise ValueError("invalid cost items")
    rows, seen = [], set()
    total = Decimal(0)
    for item in items:
        if (
            not isinstance(item, dict)
            or set(item) != {"name", "quantity", "unit_price", "unit"}
            or not isinstance(item["name"], str)
            or not 1 <= len(item["name"]) <= 80
            or not isinstance(item["unit"], str)
            or not 1 <= len(item["unit"]) <= 80
            or item["name"] in seen
        ):
            raise ValueError("invalid or duplicate cost item")
        seen.add(item["name"])
        subtotal = amount(item["quantity"]) * amount(item["unit_price"])
        total += subtotal
        rows.append({**item, "subtotal_usd": str(subtotal)})
    return {
        "schema": 1,
        "label": value["label"],
        "currency": "USD",
        "items": rows,
        "total_usd": str(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "exclusions": value["exclusions"],
        "scope": "User-supplied illustrative rates, not current AWS prices, a complete bill or budget enforcement.",
    }
