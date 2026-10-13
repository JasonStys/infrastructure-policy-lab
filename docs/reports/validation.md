# Validation results

Measured 2026-10-13 by Jason Stys. Local Windows / CPython 3.14.6. This is synthetic/offline software verification and mocked IaC testing, not independent security audit or real AWS deployment verification.

Measured functional source: `d71fb97b5697c076fbc0a390fbbd895c245b5496`. A subsequent report-only commit does not change that tested functional source and must independently pass both workflows before handoff.

## Local validation

Local contract/property/CLI/report/source-guard tests passed with warnings as errors: **130 passing, 1 OS-permission skip, 98.66% branch-inclusive core coverage**; 131 collected. Strict Ruff/type checks passed (8 core modules), exact symbol maps passed, and README describes all 60 tracked files. Staged Gitleaks checks found no leaks. Synthetic browser report exercise verified 14 PASS / 2 FAIL, readable findings and Jason Stys/contact links with no active script or remote content.

## Real native tool evidence

Native evidence: Terraform 1.16.5, signed/checksum-locked AWS provider 6.68.0, OPA 1.21.2. Five mocked plan tests passed; ten Rego tests passed; six independently labeled cross-engine fixtures matched; the actual emitted baseline mock plan passed 17 selected checks. No AWS credentials, account API calls, resources, apply or destroy were used. Local isolated advisory audit found no known vulnerabilities in the complete hash-locked development graph.

The two bounded properties use Hypothesis default 100 examples each, not exhaustive fuzzing. Local symlink test is skipped only because Windows denies this process creating links; it remains enabled for hosted runners. Benchmarks exclude Terraform/init/OPA/file/network costs. See testing and scope docs for untested live-account/topology/IAM/restore limits.

## Hosted evidence and initial failure

Initial source `32bbfd84de8e3d34cefb7b0f7d12396ce88e0b5c`: [Validate 38467044088](https://github.com/JasonStys/infrastructure-policy-lab/actions/runs/38467044088) passed all four core OS/Python lanes and security, but infrastructure failed at cached Linux AWS provider checksum validation. The Windows-generated lock needed a Linux unpacked-package h1 hash for read-only validation. [CodeQL 38467044014](https://github.com/JasonStys/infrastructure-policy-lab/actions/runs/38467044014) passed. Both signed origin-registry packages were verified and their hashes committed; no checksum/signature gate or read-only lock setting was disabled. A regression guard and maintenance guidance were added; the failure remains visible.

Final functional source `d71fb97b5697c076fbc0a390fbbd895c245b5496`: [Validate 38467733156](https://github.com/JasonStys/infrastructure-policy-lab/actions/runs/38467733156) passed **all six jobs**; [CodeQL 38467733204](https://github.com/JasonStys/infrastructure-policy-lab/actions/runs/38467733204) passed. Exact per-job logs showed:

| Hosted lane/gate | Observed result |
| --- | --- |
| Ubuntu / Python 3.12 | 131 passed, no skips; 99.11% branch-inclusive core coverage |
| Ubuntu / Python 3.14 | 131 passed, no skips; 99.11% branch-inclusive core coverage |
| Windows / Python 3.14 | 131 passed, no skips; 99.11% branch-inclusive core coverage |
| macOS 15 Intel / Python 3.14 | 131 passed, no skips; 99.11% branch-inclusive core coverage |
| Actual infrastructure tools on Linux | 5 mocked Terraform cases; 10/10 Rego tests; 6 cross-engine scenarios; actual mock plan 17 PASS, 0 FAIL/UNKNOWN/REVIEW |
| Security | Full locked advisory audit, history secret scan, HIGH/CRITICAL dependency vulnerability scan, actionlint/ShellCheck passed |
| CodeQL security-extended | Successful; zero open alerts returned at review |

Ruff/types/exact maps/file-guide/benchmarks also ran in all four core lanes. OPA is the selected IaC policy gate; Trivy checks dependencies, not full IaC misconfiguration/compliance coverage. No advisory suppressions or intentionally weakened tests were added.

## Performance, storage and limits

The saved [benchmark](benchmark.json) measured 10,000 cached plan evaluations in 1.001089 seconds (9,989.12 plans/second) on local Windows/Python 3.14.6. This is a microbenchmark only, not a deployment latency, parser throughput, real OPA/cloud capacity or cost guarantee. CI repeats it without a hardware-dependent pass threshold.

Read-only Actions account inventory at 2026-10-13T21:07:45Z: 578,457,513 artifact bytes, 7,677,170,223 cache bytes under its separate allowance. GitHub's refreshed billing meter verified 0.5 GB / 0.5 GB included Actions storage (100%). These measurements differ; byte counts are not billing percentages. This repository's API returned **0 artifacts / 0 bytes and 0 caches / 0 bytes**. All results are in logs/job summaries, not retained artifacts. Other repositories' activity can change the account totals. No existing results were deleted; fresh approval is required for cleanup.

Residual gaps: unsigned/partial plan evidence and forged masks, plaintext/address privacy, trusted-workspace races, complete topology/default-resource/IAM/key-policy/logging/retention/restore gaps, non-current illustrative cost rates and author self-review. No cloud resource was created, real account API permission tested, installer published, host setting changed or Docker repair attempted.
