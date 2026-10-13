# Validation results

Measured 2026-10-13 by Jason Stys. Local Windows / CPython 3.14.6. This is synthetic/offline software verification and mocked IaC testing, not independent security audit or real AWS deployment verification.

Local contract/property/CLI/report/source-guard tests passed with warnings as errors: **129 passing, 1 OS-permission skip, 98.66% branch-inclusive core coverage**; 130 collected. Strict Ruff/type checks passed (8 core modules), exact symbol maps passed, and README describes all 60 tracked files. Exact committed source and hosted workflow links will be recorded after all release gates finish; no pending hosted gate is represented as passed.

Native evidence: Terraform 1.16.5, signed/checksum-locked AWS provider 6.68.0, OPA 1.21.2. Five mocked plan tests passed; ten Rego tests passed; six independently labeled cross-engine fixtures matched; the actual emitted baseline mock plan passed 17 selected checks. No AWS credentials, account API calls, resources, apply or destroy were used. Local isolated advisory audit found no known vulnerabilities in the complete hash-locked development graph.

The two bounded properties use Hypothesis default 100 examples each, not exhaustive fuzzing. Local symlink test is skipped only because Windows denies this process creating links; it remains enabled for hosted runners. Benchmarks exclude Terraform/init/OPA/file/network costs. See testing and scope docs for untested live-account/topology/IAM/restore limits.

The saved [benchmark](benchmark.json) measured 10,000 cached plan evaluations in 1.001089 seconds (9,989.12 plans/second) on local Windows/Python 3.14.6. This is a microbenchmark only, not a deployment latency, parser throughput, real OPA/cloud capacity or cost guarantee. CI repeats it without a hardware-dependent pass threshold.

Actions account inventory at 2026-10-13T20:24:33Z: 574,674,328 artifact bytes, 7,414,874,947 cache bytes under its separate allowance. GitHub billing meter verified 0.5 GB / 0.5 GB included Actions storage (100%). These measurements differ; byte counts are not billing percentages. New workflows intentionally retain zero artifacts/caches. No existing results were deleted; fresh approval is required for cleanup.
