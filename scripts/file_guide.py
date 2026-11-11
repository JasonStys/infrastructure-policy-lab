"""Maintain exhaustive tracked-file README summaries without reading ignored private plans. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# variable: BEGIN — line 33
# variable: END — line 33
# variable: SPECIAL — line 34
# definition: description — line 58
# parameter: path — line 58
# variable: content — line 68
# variable: line — line 74
# definition: main — line 78
# variable: parser — line 80
# variable: args — line 82
# variable: files — line 83
# variable: rows — line 91
# variable: path — line 92
# variable: label — line 93
# variable: destination — line 95
# variable: original — line 96
# variable: first — line 97
# variable: last — line 97
# variable: expected — line 98
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    "docs/reports/windows-application-guide-1.1.0.docx": "Individually reviewed four-page installed application guide with actual screenshots, worked workflow, immutable source excerpts and limits.",
    "docs/reports/windows-application-guide-1.1.0.json": "Exact Word, actual screenshot and reviewed page digests plus observed source-specific validation results.",
    "docs/screenshots/installed-1.1.0/destructive-change-review.png": "Actual installed application synthetic-profile screenshot: Destructive resource change worklist.",
    "docs/screenshots/installed-1.1.0/reasoned-resource-receipt.png": "Actual installed application synthetic-profile screenshot: Plan bound resource review receipt.",
    "requirements-native.lock": "Exact SHA256-locked native-build tools; runtime dependencies remain separately reviewed.",
    "docs/licenses/tcl-9.0.4.txt": "Verbatim reference SDK Tcl9.0.4 license; builds independently collect actual embedded runtime notices.",
    "docs/licenses/tk-9.0.4.txt": "Verbatim reference SDK Tk9.0.4 license; builds independently collect actual embedded runtime notices.",
    "docs/reports/project-guide.docx": "Reviewed Word project guide with source revision and dated validation scope.",
    "docs/reports/publications.json": "Exact reviewed Office file identities, immutable source baseline and workflow observations.",
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
