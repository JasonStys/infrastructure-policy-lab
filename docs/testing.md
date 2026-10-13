# Risk-based test strategy and reproducibility

Highest risks: false PASS from unknown/masked/missing data, destructive cloud plans, leaked private values, malformed/unbounded parsing, mismatched TLS/KMS scope, wrong cost arithmetic and unsafe output. Test these before throughput.

| Layer | Tests and gate |
| --- | --- |
| Unit/contracts | Exact input types, formats/action arrays, masks, bounds, finite/duplicate-safe JSON, metadata/unknown propagation |
| Independent scenarios | Hard-coded counts for healthy/insecure/unknown/replacement/drift/unsupported fixtures; expected approvals not read from implementation output |
| Properties | Private-subnet bool oracle and integer-cent cost oracle, bounded Hypothesis default 100 examples each with shrinking/replay |
| Security | Sensitive sentinel absent, nested masks, scoped HTTP denial/KMS binding, linked file/output refusal, escaped inert HTML, prior output preservation |
| CLI/E2E | Actual python module subprocess, all three commands, 0/1/2 exits, sanitized errors, deterministic JSON and output files |
| Native infrastructure | Terraform fmt/init locked provider/validate + 5 mock-provider plan assertions; no credentials/deployment |
| Real policy engine | OPA fmt/strict check, 10 Rego tests, six cross-engine scenarios, actual emitted baseline mock plan (17 controls) |
| Performance | 10,000 cached validated plan assessments with measured timing, no flaky hardware-dependent speed threshold |
| Supply chain/CI | Full hash locks, advisory/history/vulnerability scan, strict lint/types, exact line maps/file guide, actionlint/ShellCheck, security-extended CodeQL |

Run from root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m ruff format --check .
.venv\Scripts\python.exe -m mypy
.venv\Scripts\python.exe scripts/code_map.py --check
.venv\Scripts\python.exe scripts/file_guide.py --check
.venv\Scripts\python.exe -m pytest -q -W error --cov=assurance --cov-report=term-missing
.venv\Scripts\python.exe -m scripts.benchmark
.venv\Scripts\python.exe -m scripts.infra_checks
```

Native tests need the separately bootstrapped .tools binaries; Linux/macOS Python path is .venv/bin/python. Minimum branch-inclusive core coverage 90%; warnings are errors. Symlink test skips only when OS denies creating a link; hosted Linux/macOS must execute it. Core CI covers Ubuntu Python 3.12/3.14, Windows 3.14, standard macOS 15 Intel 3.14; real Terraform/OPA also run on Linux. Local Windows exercises the actual vendor binaries too.

Measured outcomes and exact source/run links belong in [validation](reports/validation.md), not invented forecasts. Mock tests don't validate live AWS, all infrastructure types, full topology, IAM/backend semantics, disaster recovery, penetration resistance or a complete compliance baseline. Test code/input reports are synthetic and only logs/summaries are retained by CI. No test relaxations or advisory suppressions are permitted merely to make CI pass.
