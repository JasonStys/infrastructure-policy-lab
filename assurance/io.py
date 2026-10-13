"""Bounded strict JSON reads and new-directory-only evidence writes. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_BYTES — line 44
# definition: pairs — line 47
# parameter: items — line 47
# variable: result — line 49
# variable: key — line 50
# variable: value — line 50
# definition: bounded — line 57
# parameter: depth — line 57
# parameter: value — line 57
# variable: c — line 63
# variable: children — line 69
# variable: key — line 71
# variable: children — line 73
# variable: children — line 75
# variable: child — line 76
# definition: parse — line 82
# parameter: source — line 82
# variable: value — line 85
# definition: read — line 92
# parameter: path — line 92
# variable: info — line 94
# variable: descriptor — line 102
# variable: stream — line 103
# variable: source — line 104
# definition: canonical — line 110
# parameter: value — line 110
# definition: new_directory — line 117
# parameter: path — line 117
# variable: parent — line 119
# END CODE MAP

from __future__ import annotations

import json
import math
import os
import stat
from collections.abc import Iterable
from pathlib import Path
from typing import Any

MAX_BYTES = 8 * 1024 * 1024


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate object keys rather than silently replacing earlier security evidence."""
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def bounded(value: Any, depth: int = 0) -> None:
    """Validate finite UTF-8-safe JSON with bounded depth/collections before contract evaluation."""
    if depth > 32:
        raise ValueError("JSON nesting limit exceeded")
    if isinstance(value, str):
        if len(value) > 262144 or any(
            ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or ord(c) == 127 for c in value
        ):
            raise ValueError("invalid JSON text")
    elif isinstance(value, (dict, list)):
        if len(value) > 10000:
            raise ValueError("JSON collection limit exceeded")
        children: Iterable[Any]
        if isinstance(value, dict):
            for key in value:
                bounded(key, depth + 1)
            children = value.values()
        else:
            children = value
        for child in children:
            bounded(child, depth + 1)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite JSON number")


def parse(source: str) -> Any:
    """Decode strict JSON; errors disclose no input content or filesystem path."""
    try:
        value = json.loads(source, object_pairs_hook=pairs)
        bounded(value)
        return value
    except (json.JSONDecodeError, RecursionError) as error:
        raise ValueError("invalid or deeply nested JSON") from error


def read(path: Path) -> Any:
    """Read a regular, non-linked final file, bounded even if its size changes; trusted parent required."""
    info = path.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or path.is_symlink()
        or path.is_junction()
        or info.st_size > MAX_BYTES
    ):
        raise ValueError("input must be a bounded regular non-linked file")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as stream:
        source = stream.read(MAX_BYTES + 1)
    if len(source) > MAX_BYTES:
        raise ValueError("input size limit exceeded")
    return parse(source.decode("utf-8-sig"))


def canonical(value: Any) -> str:
    """Encode deterministic finite semantic JSON for digests and evidence exports."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def new_directory(path: Path) -> None:
    """Create private new output only; reject linked ancestors and preserve all existing evidence."""
    for parent in (path, *path.parents):
        if parent.is_symlink() or parent.is_junction():
            raise ValueError("linked output path refused")
    path.mkdir(mode=0o700)
