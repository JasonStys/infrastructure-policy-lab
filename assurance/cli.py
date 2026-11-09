"""Read-only assess/compare/cost command-line workflows; no deployment or arbitrary shell. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 38
# parameter: argv — line 38
# variable: parser — line 40
# variable: commands — line 43
# variable: check — line 44
# variable: diff — line 47
# variable: costs — line 50
# variable: name — line 52
# variable: workflow — line 53
# variable: args — line 58
# variable: report — line 61
# variable: code — line 64
# variable: report — line 66
# variable: code — line 67
# variable: plan — line 69
# variable: report — line 70
# variable: code — line 77
# variable: code — line 82
# variable: report — line 82
# END CODE MAP

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assurance import review
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
    for name in ("worklist", "review"):
        workflow = commands.add_parser(name)
        workflow.add_argument("plan", type=Path)
        workflow.add_argument("--out", type=Path)
        if name == "review":
            workflow.add_argument("--decisions", type=Path, required=True)
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
        elif args.command in ("worklist", "review"):
            plan = load(read(args.plan))
            report = (
                review.worklist(plan)
                if args.command == "worklist"
                else review.receipt(plan, read(args.decisions))
            )
            if args.out:
                review.export(report, args.out)
            code = int(
                not report["allowed"]
                or (args.command == "review" and not report["all_required_acknowledged"])
            )
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
