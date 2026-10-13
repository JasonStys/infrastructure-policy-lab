"""Generate/check exact Python, Terraform, Rego, shell and workflow symbol positions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: BEGIN — line 80
# variable: END — line 81
# variable: ROOT — line 82
# definition: mapped — line 85
# parameter: source — line 85
# variable: start — line 88
# variable: finish — line 89
# variable: source — line 90
# variable: tree — line 91
# variable: first — line 92
# variable: insertion — line 93
# variable: records — line 100
# variable: node — line 101
# variable: count — line 108
# variable: header — line 109
# parameter: item — line 113
# variable: kind — line 113
# variable: line — line 113
# variable: name — line 113
# variable: lines — line 117
# definition: main — line 122
# variable: parser — line 124
# variable: arguments — line 126
# variable: stale — line 127
# variable: folder — line 128
# variable: path — line 129
# variable: original — line 130
# variable: expected — line 131
# variable: tree — line 133
# variable: node — line 134
# variable: path — line 145
# variable: original — line 154
# variable: expected — line 155
# definition: shell_mapped — line 164
# parameter: source — line 164
# parameter: suffix — line 164
# variable: prefix — line 166
# variable: begin — line 167
# variable: end — line 167
# variable: start — line 169
# variable: finish — line 170
# variable: source — line 171
# variable: lines — line 172
# variable: insertion — line 173
# variable: insertion — line 175
# variable: records — line 176
# variable: line — line 177
# variable: number — line 177
# variable: name — line 180
# variable: name — line 182
# variable: name — line 185
# variable: name — line 188
# variable: name — line 190
# variable: name — line 193
# variable: name — line 195
# variable: name — line 197
# variable: name — line 199
# variable: name — line 201
# variable: part — line 204
# variable: name — line 205
# variable: name — line 208
# variable: name — line 210
# variable: name — line 212
# variable: count — line 214
# variable: header — line 215
# variable: kind — line 219
# variable: name — line 219
# variable: number — line 219
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

BEGIN = "# BEGIN CODE MAP (generated; python scripts/code_map.py)"
END = "# END CODE MAP"
ROOT = Path(__file__).resolve().parents[1]


def mapped(source: str) -> str:
    """Build a self-consistent line map for definitions, parameters and assigned variables."""
    if "\n" + BEGIN + "\n" in source:
        start = source.index("\n" + BEGIN + "\n") + 1
        finish = source.index("\n" + END + "\n", start) + len(END) + 2
        source = source[:start] + source[finish:]
    tree = ast.parse(source)
    first = tree.body[0] if tree.body else None
    insertion = (
        first.end_lineno
        if isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
        else 0
    )
    records: set[tuple[str, str, int]] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            records.add(("definition", node.name, node.lineno))
        elif isinstance(node, ast.arg):
            records.add(("parameter", node.arg, node.lineno))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            records.add(("variable", node.id, node.lineno))
    count = len(records) + 2
    header = (
        [BEGIN]
        + [
            f"# {kind}: {name} — line {line + count if line > insertion else line}"
            for kind, name, line in sorted(records, key=lambda item: (item[2], item[0], item[1]))
        ]
        + [END]
    )
    lines = source.splitlines(keepends=True)
    lines.insert(insertion or 0, "\n".join(header) + "\n")
    return "".join(lines)


def main() -> int:
    """Update authored Python files, or fail if --check finds stale maps or missing contracts."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    stale = []
    for folder in ("assurance", "scripts", "tests"):
        for path in sorted((ROOT / folder).glob("*.py")):
            original = path.read_text(encoding="utf-8")
            expected = mapped(original)
            if arguments.check:
                tree = ast.parse(original)
                for node in ast.walk(tree):
                    if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    ) and not ast.get_docstring(node):
                        raise ValueError(
                            f"Missing function/class contract: {path.name}:{node.lineno}"
                        )
            if original != expected:
                stale.append(str(path.relative_to(ROOT)))
                if not arguments.check:
                    path.write_text(expected, encoding="utf-8", newline="\n")
    for path in [
        *(ROOT / "scripts").glob("*.ps1"),
        *(ROOT / "scripts").glob("*.sh"),
        *(ROOT / "policies").glob("*.yml"),
        *(ROOT / ".github/workflows").glob("*.yml"),
        *(ROOT / "infra").rglob("*.tf"),
        *(ROOT / "infra").rglob("*.tftest.hcl"),
        *(ROOT / "policies").glob("*.rego"),
    ]:
        original = path.read_text(encoding="utf-8")
        expected = shell_mapped(original, path.suffix)
        if original != expected:
            stale.append(str(path.relative_to(ROOT)))
            if not arguments.check:
                path.write_text(expected, encoding="utf-8", newline="\n")
    print("Code maps current" if not stale else "Code maps: " + ", ".join(stale))
    return 1 if arguments.check and stale else 0


def shell_mapped(source: str, suffix: str) -> str:
    """Map shell symbols, SQL columns/tables and YAML parameters/controls/expressions without execution."""
    prefix = "--" if suffix == ".sql" else "#"
    begin, end = BEGIN.replace("#", prefix, 1), END.replace("#", prefix, 1)
    if "\n" + begin + "\n" in source:
        start = source.index("\n" + begin + "\n") + 1
        finish = source.index("\n" + end + "\n", start) + len(end) + 2
        source = source[:start] + source[finish:]
    lines = source.splitlines(keepends=True)
    insertion = 1 if source.startswith("#!") else 0
    while insertion < len(lines) and lines[insertion].startswith(prefix):
        insertion += 1
    records = {}
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith(prefix):
            continue
        for name in re.findall(r"\$([A-Za-z_][A-Za-z_0-9]*)", line):
            records.setdefault(("variable", name), number)
        for name in re.findall(r"^function ([A-Za-z0-9_-]+)", line):
            records[("function", name)] = number
        if suffix == ".sh":
            for name in re.findall(r"^(?:export )?([A-Za-z_][A-Za-z_0-9]*)=", line):
                records.setdefault(("variable", name), number)
        if suffix == ".sql":
            for name in re.findall(r"\b([A-Za-z_][A-Za-z_0-9]*) (?:TEXT|INTEGER)\b", line):
                records.setdefault(("column", name), number)
            for name in re.findall(r"CREATE TABLE (\w+)", line):
                records[("table", name)] = number
        elif suffix in {".tf", ".hcl", ".rego"}:
            for name in re.findall(r"^\s*(\w+)(?:\([^)]*\))?\s+if\b", line):
                records.setdefault(("rule", name), number)
            for name in re.findall(r"\b(?:every|some)\s+(\w+)\b", line):
                records.setdefault(("variable", name), number)
            for name in re.findall(r"^\s*default\s+(\w+)\s*:=", line):
                records.setdefault(("default", name), number)
            for name in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(?:=|:=|if\b)", line):
                records.setdefault(("symbol", name), number)
            for name in re.findall(
                r'^\s*(?:variable|resource|run|mock_resource) "([^"]+)"(?: "([^"]+)")?', line
            ):
                records.setdefault(("block", ".".join(part for part in name if part)), number)
            for name in re.findall(r"\b(?:var|local|count|input)\.[A-Za-z0-9_.]+", line):
                records.setdefault(("reference", name), number)
        elif suffix == ".yml":
            for name in re.findall(r"^\s*(?:- )?([A-Za-z_][A-Za-z_0-9]*):", line):
                records.setdefault(("parameter", name), number)
            for name in re.findall(r"^\s*- id: ([A-Za-z0-9_-]+)", line):
                records[("control", name)] = number
            for name in re.findall(r"\$\{\{\s*([A-Za-z0-9_.]+)\s*\}\}", line):
                records.setdefault(("expression", name), number)
    count = len(records) + 2
    header = [
        begin,
        *(
            f"{prefix} {kind}: {name} — line {number + count if number > insertion else number}"
            for (kind, name), number in records.items()
        ),
        end,
    ]
    lines.insert(insertion, "\n".join(header) + "\n")
    return "".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
