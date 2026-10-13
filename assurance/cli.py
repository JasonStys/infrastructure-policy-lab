"""Read-only assess/compare/cost command-line workflows; no deployment or arbitrary shell. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 32
# parameter: argv — line 32
# variable: parser — line 34
# variable: commands — line 37
# variable: check — line 38
# variable: diff — line 41
# variable: costs — line 44
# variable: args — line 46
# variable: report — line 49
# variable: code — line 52
# variable: report — line 54
# variable: code — line 55
# variable: code — line 57
# variable: report — line 57
# END CODE MAP

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assurance.cost import estimate
from assurance.io import canonical, read
from assurance.plan import load
from assurance.policy import assess, compare
from assurance.report import export


def main(argv: list[str] | None = None) -> int:
    """Return 0 for allowed/no drift/cost success, 1 for blocked/changed evidence, 2 for rejected input/output."""
    parser = argparse.ArgumentParser(
        description="Offline infrastructure plan assurance — Jason Stys"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("assess")
    check.add_argument("plan", type=Path)
    check.add_argument("--out", type=Path)
    diff = commands.add_parser("compare")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    costs = commands.add_parser("cost")
    costs.add_argument("scenario", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "assess":
            report = assess(load(read(args.plan)))
            if args.out:
                export(report, args.out)
            code = 0 if report["allowed"] else 1
        elif args.command == "compare":
            report = compare(assess(load(read(args.before))), assess(load(read(args.after))))
            code = 1 if report["changes"] else 0
        else:
            report, code = estimate(read(args.scenario)), 0
        print(canonical(report))
        return code
    except (ValueError, OSError, UnicodeError, KeyError, TypeError):
        print(
            "Input/output rejected; inspect private inputs against the documented contract.",
            file=sys.stderr,
        )
        return 2
