"""Maintain exhaustive tracked-file README summaries without reading ignored private plans. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# variable: BEGIN — line 33
# variable: END — line 33
# variable: SPECIAL — line 34
# definition: description — line 49
# parameter: path — line 49
# variable: content — line 59
# variable: line — line 65
# definition: main — line 69
# variable: parser — line 71
# variable: args — line 73
# variable: files — line 74
# variable: rows — line 82
# variable: path — line 83
# variable: label — line 84
# variable: destination — line 86
# variable: original — line 87
# variable: first — line 88
# variable: last — line 88
# variable: expected — line 89
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    ".gitattributes": "Portable LF text handling.",
    ".gitignore": "Keeps tools, private plans/state/credentials and generated outputs out of Git.",
    "LICENSE": "MIT terms for authored code, not third-party tool licenses.",
    "pyproject.toml": "Dependency-free runtime metadata, strict type/lint/test coverage settings.",
    "requirements-dev.in": "Reviewed direct validation dependencies.",
    "requirements-dev.lock": "Complete hash-locked cross-platform validation graph.",
    "tools.lock.json": "Official Terraform/OPA/scanner URLs, versions and SHA-256 pins.",
    "infra/.terraform.lock.hcl": "Vendor-generated signed AWS provider package checksums and exact version.",
    "docs/reports/demo.html": "Inert synthetic plan report, never real cloud evidence.",
    "docs/reports/demo.json": "Synthetic selected-control assessment, counts and semantic digest.",
    "docs/reports/benchmark.json": "Measured offline gate throughput with environment/scope caveats.",
}


def description(path: str) -> str:
    """Require a meaningful description for every tracked file; unknown formats fail maintenance checks."""
    if path in SPECIAL:
        return SPECIAL[path]
    if path.startswith("examples/"):
        return (
            "Fictional "
            + Path(path).stem
            + " plan/scenario; not cloud state, credentials or current AWS pricing."
        )
    content = (ROOT / path).read_text(encoding="utf-8")
    if path.endswith(".py"):
        return (ast.get_docstring(ast.parse(content)) or "").splitlines()[0]
    if path.endswith(".md"):
        return content.splitlines()[0].lstrip("# ") + "."
    if path.endswith((".tf", ".hcl", ".rego", ".sh", ".yml")):
        return next(line.lstrip("# ") for line in content.splitlines() if line.startswith("# "))
    raise ValueError(f"missing tracked-file purpose: {path}")


def main() -> int:
    """Generate/check the README inventory using intended Git-tracked files only; stage before generating."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    if files == [""]:
        raise ValueError("stage intended files first")
    rows = ["| File | Purpose |", "| --- | --- |"]
    for path in sorted(files):
        label = path.replace("_", "\\_")
        rows.append(f"| [{label}]({path}) | {description(path).replace('|', '/')} |")
    destination = ROOT / "README.md"
    original = destination.read_text(encoding="utf-8")
    first, last = original.index(BEGIN) + len(BEGIN), original.index(END)
    expected = original[:first] + "\n\n" + "\n".join(rows) + "\n\n" + original[last:]
    if args.check and expected != original:
        raise ValueError("README inventory stale")
    if not args.check:
        destination.write_text(expected, encoding="utf-8", newline="\n")
    print(f"README inventory current: {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
