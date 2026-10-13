"""Real Terraform mocked plans and OPA cross-engine checks, never apply/live AWS. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 42
# definition: tool — line 45
# parameter: name — line 45
# variable: path — line 47
# definition: opa_check — line 53
# parameter: plan — line 53
# parameter: target — line 53
# variable: parsed — line 55
# variable: result — line 57
# definition: main — line 77
# variable: output — line 79
# variable: terraform — line 81
# variable: environment — line 82
# variable: command — line 88
# variable: completed — line 96
# variable: line — line 105
# variable: messages — line 105
# variable: m — line 106
# variable: summary — line 106
# variable: k — line 110
# variable: emitted — line 113
# variable: m — line 115
# variable: plan — line 118
# variable: report — line 125
# variable: name — line 137
# variable: allowed — line 138
# END CODE MAP

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from assurance.io import canonical, read
from assurance.plan import load
from assurance.policy import assess, evidence

ROOT = Path(__file__).resolve().parents[1]


def tool(name: str) -> str:
    """Select only a reviewed repository-owned fixed binary path; no commands supplied by policy inputs."""
    path = ROOT / ".tools" / (name + (".exe" if os.name == "nt" else ""))
    if not path.is_file():
        raise ValueError("Run hash-verified bootstrap first")
    return str(path)


def opa_check(plan: dict, target: Path) -> bool:
    """Compare actual OPA policy output with Python's independent gate using a redacted normalization."""
    parsed = load(plan)
    target.write_text(canonical(evidence(parsed)), encoding="utf-8")
    result = subprocess.check_output(
        [
            tool("opa"),
            "eval",
            "--format",
            "raw",
            "--data",
            str(ROOT / "policies/gate.rego"),
            "--input",
            str(target),
            "data.infrastructure.allow",
        ],
        text=True,
        timeout=30,
    ).strip()
    if result not in {"true", "false"} or (result == "true") != assess(parsed)["allowed"]:
        raise ValueError("OPA and Python policy decisions differ")
    return result == "true"


def main() -> None:
    """Exercise vendor CLI schemas and real Rego rules using mocked provider and independently labeled fixtures."""
    output = ROOT / "out"
    output.mkdir(exist_ok=True)
    terraform = tool("terraform")
    environment = {
        **os.environ,
        "TF_IN_AUTOMATION": "true",
        "TF_INPUT": "false",
        "AWS_EC2_METADATA_DISABLED": "true",
    }
    for command in (
        ["fmt", "-check", "-recursive"],
        ["init", "-backend=false", "-input=false", "-lockfile=readonly"],
        ["validate", "-no-color"],
    ):
        subprocess.run(
            [terraform, *command], cwd=ROOT / "infra", env=environment, check=True, timeout=300
        )
    completed = subprocess.run(
        [terraform, "test", "-json", "-verbose"],
        cwd=ROOT / "infra",
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=300,
    )
    messages = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    summary = next(m["test_summary"] for m in messages if m.get("type") == "test_summary")
    if (
        summary["status"] != "pass"
        or summary["passed"] != 5
        or any(summary[k] != 0 for k in ("failed", "errored", "skipped"))
    ):
        raise ValueError("Terraform mocked test summary failed")
    emitted = next(
        m["test_plan"]
        for m in messages
        if m.get("type") == "test_plan" and m.get("@testrun") == "baseline"
    )
    plan = {
        "format_version": emitted["plan_format_version"],
        "resource_changes": emitted["resource_changes"],
        "resource_drift": emitted.get("resource_drift", []),
    }
    if not opa_check(plan, output / "mock-evidence.json"):
        raise ValueError("actual baseline mocked plan blocked")
    report = assess(load(plan))
    (output / "mock-report.json").write_text(canonical(report), encoding="utf-8")
    subprocess.run(
        [tool("opa"), "fmt", "--fail", str(ROOT / "policies")],
        check=True,
        timeout=30,
        capture_output=True,
    )
    subprocess.run(
        [tool("opa"), "check", "--strict", str(ROOT / "policies")], check=True, timeout=30
    )
    subprocess.run([tool("opa"), "test", str(ROOT / "policies"), "-v"], check=True, timeout=30)
    for name in ("healthy", "insecure", "unknown", "destructive", "drifted", "unsupported"):
        allowed = opa_check(
            read(ROOT / "examples" / f"{name}.json"), output / "fixture-evidence.json"
        )
        if allowed != (name == "healthy"):
            raise ValueError("independent fixture decision mismatch")
    print(
        f"Terraform: 5 mocked plan cases; OPA: 10 rules; 6 labeled cross-engine scenarios; actual mock controls {report['counts']}"
    )


if __name__ == "__main__":
    main()
