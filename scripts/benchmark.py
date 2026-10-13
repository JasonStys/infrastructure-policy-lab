"""Measure bounded in-memory plan-policy cost, not Terraform/AWS latency. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 22
# variable: plan — line 24
# variable: started — line 25
# variable: _ — line 26
# variable: elapsed — line 28
# variable: result — line 29
# variable: output — line 38
# END CODE MAP

import json
import platform
import time
from pathlib import Path

from assurance.plan import load
from assurance.policy import assess
from scripts.fixtures import fixture


def main() -> None:
    """Evaluate 10,000 cached validated synthetic plans; log measured scope with no flaky speed threshold."""
    plan = load(fixture())
    started = time.perf_counter()
    for _ in range(10000):
        assert assess(plan)["allowed"]
    elapsed = time.perf_counter() - started
    result = {
        "date": "2026-10-13",
        "os": platform.system(),
        "python": platform.python_version(),
        "plans": 10000,
        "seconds": round(elapsed, 6),
        "plans_per_second": round(10000 / elapsed, 2),
        "scope": "Cached validated synthetic plan policy only; excludes parsing, Terraform, provider download, OPA, export and AWS network.",
    }
    output = Path("out")
    output.mkdir(exist_ok=True)
    (output / "benchmark.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
