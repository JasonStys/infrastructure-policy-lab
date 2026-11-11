# Infrastructure Policy Lab

[![Validate](https://github.com/JasonStys/infrastructure-policy-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/infrastructure-policy-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/infrastructure-policy-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/infrastructure-policy-lab/actions/workflows/codeql.yml)

Credential-free infrastructure-as-code testing and offline change assurance. Created by [Jason Stys](https://github.com/JasonStys) · [LinkedIn/contact](https://www.linkedin.com/in/jason-stys-31b30b351/).

This defensive DevOps/cloud-security portfolio project asks **what a proposed infrastructure change proves, what it cannot prove, and which changes need review**. It is an authored educational lab, not cloud deployment authorization, a full vulnerability/compliance scanner or a security certification.

## Native graphical application

A genuine one-file Windows workbench now exposes the existing analysis core through supported file selectors, relevant settings, literal findings/detail, durable private history and exact bundle exports. Prepared scenarios are optional inputs within this same application. End users need no Python/Node installation. See [native workflows, profile safety and package acceptance](docs/native-application.md); public download/desktop installation remains a separate reviewed step.

## Features

- Real Terraform configuration for an isolated AWS VPC, two private subnets, a sealed deny-all security group and versioned/private S3 evidence storage using a rotating KMS key, ownership enforcement and HTTP deny policy. No workloads, NAT or internet gateway are provisioned by the example.
- Five real Terraform provider-mocked plan tests: positive baseline and rejected account/name/region/network parameters. No AWS credentials, cloud account, apply or destroy are used by validation.
- Typed offline plan analysis with selected network/storage/KMS controls; unresolved or sensitive evidence is UNKNOWN, not a guessed PASS. Key binding and TLS-deny scope are checked explicitly.
- Deletion/replacement and reported out-of-band drift require REVIEW; unsupported resource types block the gate. Decisions do not automatically approve deployment.
- Independent Rego/OPA gate with ten tests, plus cross-engine agreement on six independently labeled scenarios and the actual emitted Terraform mock plan.
- Plan-assessment comparison, exact-decimal illustrative cost scenarios, new-directory-only JSON and inert HTML reports. No raw configuration values or credentials appear in findings.
- [Digest-bound change review](docs/change-review.md): per-resource create/update/delete/replacement worklists, reasoned reviewer/ticket receipts and explicit unreviewed work. Receipts preserve the original policy gate and cannot approve blocked changes or authorize deployment.
- Dependency-free Python runtime; pinned/hashes-verified Terraform, OPA, AWS provider and development/scanner tools. Cross-platform tests, security-extended CodeQL, reproducible benchmark and comprehensive docs.

## Safe five-minute demo

Python 3.12–3.14 is enough for the offline CLI. No IDE, activation, administrator rights, Docker or AWS account is needed.

```bash
python -m assurance assess examples/healthy.json
python -m assurance assess examples/insecure.json
python -m assurance compare examples/healthy.json examples/insecure.json
python -m assurance cost examples/cost.json
```

Healthy has **16 PASS**; insecure has **14 PASS / 2 FAIL** and the comparison identifies two changed controls. The synthetic monthly cost is **$1.55**, using deliberately illustrative supplied rates—not current AWS prices or a complete bill. Terraform's actual mocked configuration has a second subnet and produces **17 PASS**. Fixtures have no real cloud data.

Exit 0: selected checks pass/no comparison changes/cost success; 1: blocked plan or comparison changes; 2: rejected input/output. No CLI command runs Terraform, a shell or AWS.

Generate a new report directory (its parent must exist):

```bash
python -m assurance assess examples/insecure.json --out out/demo
```

Open `out/demo/report.html`; reruns refuse overwrites. [Synthetic HTML](docs/reports/demo.html) and [JSON](docs/reports/demo.json) are included. Treat real Terraform plans/state as private: their exports can contain secrets even if Terraform marks them sensitive. Never upload real plans to this repository.

## Real Terraform/OPA verification, still no deployment

For x64 Windows/Linux, the explicit bootstrap downloads official tools into ignored `.tools`, verifies their pinned SHA-256 before use and does not install globally:

```bash
python -m scripts.bootstrap terraform
python -m scripts.bootstrap opa
python -m scripts.infra_checks
```

AWS provider initialization uses the checked-in vendor checksum lock. The runner executes only formatting, init with no backend, validation and **mocked plan** test operations; it evaluates actual OPA policies locally. Python/JSON reports expose counts, not provider credentials. macOS users can run the Python CLI/tests; this bootstrap supports only x64 Windows/Linux, not all native tool architectures.

The example is deliberately **not production-ready**: default VPC security resources, complete routing, access/logging/lifecycle policies, IAM/KMS authorization and organizational controls need separate design/review. No live account, real API permissions, effective network filtering, data durability or restore has been validated. The cost calculator is not budget enforcement.

## Testing, operations and documentation

```bash
python -m venv .venv
# Use .venv/Scripts/python.exe on Windows or .venv/bin/python on Linux/macOS.
python -m pip install --require-hashes -r requirements-dev.lock
bash scripts/validate.sh
```

See [test strategy](docs/testing.md), [measured validation](docs/reports/validation.md), [architecture/ADR](docs/architecture.md), [contracts/control scope](docs/contracts.md), [operator runbook](docs/runbook.md), [threat model](docs/security.md), [coding guidelines](docs/development.md) and [primary research](docs/research.md).

GitHub Actions keep results in logs and job summaries only: **no retained artifact/cache uploads**. No AWS deployment, credentials, paid cloud resources, host settings changes or automatic teardown is included. Human authorization and isolated account/state management are prerequisites before any real deployment. [Security reporting](SECURITY.md).

## Native profile storage correction

Version 1.1.1 rejects pre-existing linked/nonregular fixed profile and SQLite
sidecar entries before initialization can write through an alias. Ordinary
recovery files and existing profile schemas remain supported; no data is reset.
See the [confirmed fixture, recovery tests and scope](docs/reports/profile-admission-2026-11-11.md).
Earlier native releases and documentation retain their own dated evidence.

## File guide

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.gitattributes](.gitattributes) | Portable LF text handling. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: four core OS/Python lanes plus actual mocked Terraform/OPA and security supply-chain gates. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: least-privilege Python security-extended static analysis; no Actions artifact/cache uploads. |
| [.gitignore](.gitignore) | Keeps tools, private plans/state/credentials and generated outputs out of Git. |
| [LICENSE](LICENSE) | MIT terms for authored code, not third-party tool licenses. |
| [README.md](README.md) | Infrastructure Policy Lab. |
| [SECURITY.md](SECURITY.md) | Security reporting. |
| [assurance/\_\_init\_\_.py](assurance/__init__.py) | Offline, non-deploying Terraform assurance package. Created by Jason Stys. |
| [assurance/\_\_main\_\_.py](assurance/__main__.py) | Module CLI entry point; does not invoke Terraform, AWS or a shell. Jason Stys. |
| [assurance/cli.py](assurance/cli.py) | Read-only assess/compare/cost command-line workflows; no deployment or arbitrary shell. Jason Stys. |
| [assurance/cost.py](assurance/cost.py) | Exact-decimal scenario cost calculation with explicit exclusions; no pricing API or AWS calls. Jason Stys. |
| [assurance/desktop.py](assurance/desktop.py) | Native offline workbench: real project inputs, analysis, searchable evidence, history and export. Jason Stys. |
| [assurance/desktop\_io.py](assurance/desktop_io.py) | Bounded regular descriptor reads and strict finite JSON for owner-local desktop state. Jason Stys. |
| [assurance/desktop\_project.py](assurance/desktop_project.py) | Native selected-control, plan-comparison, exact-cost and digest-bound resource-review workflows. Jason Stys. |
| [assurance/desktop\_state.py](assurance/desktop_state.py) | Owner-local desktop profile, bounded durable bundles and non-overwriting export. Jason Stys. |
| [assurance/io.py](assurance/io.py) | Bounded strict JSON reads and new-directory-only evidence writes. Created by Jason Stys. |
| [assurance/plan.py](assurance/plan.py) | Validate Terraform plan changes and retain only selected non-sensitive evidence. Jason Stys. |
| [assurance/policy.py](assurance/policy.py) | Deterministic selected-control plan gate; unknown/deletion/unsupported resources cannot pass. Jason Stys. |
| [assurance/report.py](assurance/report.py) | Escaped scriptless offline assurance reports with no raw plan values. Created by Jason Stys. |
| [assurance/review.py](assurance/review.py) | Digest-bound resource change worklists and asserted reviewer receipts. Created by Jason Stys. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: Offline plan assurance with actual provider-mocked IaC tests. |
| [docs/change-review.md](docs/change-review.md) | Digest-bound infrastructure change review. |
| [docs/contracts.md](docs/contracts.md) | Plan, policy, cost and report contracts. |
| [docs/development.md](docs/development.md) | Coding, documentation and dependency maintenance. |
| [docs/handbook.md](docs/handbook.md) | Infrastructure Policy Lab handbook. |
| [docs/licenses/tcl-9.0.4.txt](docs/licenses/tcl-9.0.4.txt) | Verbatim reference SDK Tcl9.0.4 license; builds independently collect actual embedded runtime notices. |
| [docs/licenses/tk-9.0.4.txt](docs/licenses/tk-9.0.4.txt) | Verbatim reference SDK Tk9.0.4 license; builds independently collect actual embedded runtime notices. |
| [docs/native-application.md](docs/native-application.md) | Infrastructure Policy Workbench native application. |
| [docs/reports/benchmark.json](docs/reports/benchmark.json) | Measured offline gate throughput with environment/scope caveats. |
| [docs/reports/change-review-2026-11-09.md](docs/reports/change-review-2026-11-09.md) | Change review workflow validation — 2026-11-09. |
| [docs/reports/demo.html](docs/reports/demo.html) | Inert synthetic plan report, never real cloud evidence. |
| [docs/reports/demo.json](docs/reports/demo.json) | Synthetic selected-control assessment, counts and semantic digest. |
| [docs/reports/documentation-refresh-2026-11-09.md](docs/reports/documentation-refresh-2026-11-09.md) | Documentation refresh — 2026-11-09. |
| [docs/reports/installed-windows-1.1.1-2026-11-11.md](docs/reports/installed-windows-1.1.1-2026-11-11.md) | Installed Windows 1.1.1 validation · 11 November 2026. |
| [docs/reports/installed-windows-2026-11-10.md](docs/reports/installed-windows-2026-11-10.md) | Installed Windows application validation 10 November 2026. |
| [docs/reports/native-application-2026-11-10.md](docs/reports/native-application-2026-11-10.md) | Native application validation — 2026-11-10. |
| [docs/reports/portfolio-sync-2026-10-22.md](docs/reports/portfolio-sync-2026-10-22.md) | <!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->. |
| [docs/reports/profile-admission-2026-11-11.md](docs/reports/profile-admission-2026-11-11.md) | Fixed profile entry admission — November 11, 2026. |
| [docs/reports/project-guide.docx](docs/reports/project-guide.docx) | Reviewed Word project guide with source revision and dated validation scope. |
| [docs/reports/publications.json](docs/reports/publications.json) | Exact reviewed Office file identities, immutable source baseline and workflow observations. |
| [docs/reports/review.md](docs/reports/review.md) | Author review and release checklist. |
| [docs/reports/validation.md](docs/reports/validation.md) | Validation results. |
| [docs/reports/windows-application-guide-1.1.0.docx](docs/reports/windows-application-guide-1.1.0.docx) | Individually reviewed four-page installed application guide with actual screenshots, worked workflow, immutable source excerpts and limits. |
| [docs/reports/windows-application-guide-1.1.0.json](docs/reports/windows-application-guide-1.1.0.json) | Exact Word, actual screenshot and reviewed page digests plus observed source-specific validation results. |
| [docs/reports/windows-application-guide-1.1.1.docx](docs/reports/windows-application-guide-1.1.1.docx) | Reviewed current 1.1.1 installed-app guide: actual screenshots, workflow, immutable code and measured limits. |
| [docs/reports/windows-application-guide-1.1.1.json](docs/reports/windows-application-guide-1.1.1.json) | Current Word, screenshot, source and individually reviewed rendered-page hashes. |
| [docs/research.md](docs/research.md) | Primary-source research and design choices. |
| [docs/runbook.md](docs/runbook.md) | Operator runbook and safe change/teardown procedure. |
| [docs/screenshots/installed-1.1.0/destructive-change-review.png](docs/screenshots/installed-1.1.0/destructive-change-review.png) | Actual installed application synthetic-profile screenshot: Destructive resource change worklist. |
| [docs/screenshots/installed-1.1.0/reasoned-resource-receipt.png](docs/screenshots/installed-1.1.0/reasoned-resource-receipt.png) | Actual installed application synthetic-profile screenshot: Plan bound resource review receipt. |
| [docs/security.md](docs/security.md) | Threat model, privacy and known assurance gaps. |
| [docs/testing.md](docs/testing.md) | Risk-based test strategy and reproducibility. |
| [examples/cost.json](examples/cost.json) | Fictional cost plan/scenario; not cloud state, credentials or current AWS pricing. |
| [examples/destructive.json](examples/destructive.json) | Fictional destructive plan/scenario; not cloud state, credentials or current AWS pricing. |
| [examples/drifted.json](examples/drifted.json) | Fictional drifted plan/scenario; not cloud state, credentials or current AWS pricing. |
| [examples/healthy.json](examples/healthy.json) | Fictional healthy plan/scenario; not cloud state, credentials or current AWS pricing. |
| [examples/insecure.json](examples/insecure.json) | Fictional insecure plan/scenario; not cloud state, credentials or current AWS pricing. |
| [examples/unknown.json](examples/unknown.json) | Fictional unknown plan/scenario; not cloud state, credentials or current AWS pricing. |
| [examples/unsupported.json](examples/unsupported.json) | Fictional unsupported plan/scenario; not cloud state, credentials or current AWS pricing. |
| [infra/.terraform.lock.hcl](infra/.terraform.lock.hcl) | Vendor-generated signed AWS provider package checksums and exact version. |
| [infra/main.tf](infra/main.tf) | Jason Stys: isolated network plus private encrypted evidence storage; deliberately no workloads or internet gateway. |
| [infra/tests/baseline.tftest.hcl](infra/tests/baseline.tftest.hcl) | Jason Stys: provider-mocked plan assertions; no live AWS APIs, credentials, apply or destroy. |
| [infra/variables.tf](infra/variables.tf) | Jason Stys: validated non-secret inputs; no real credentials or deployment defaults. |
| [infra/versions.tf](infra/versions.tf) | Jason Stys: pinned Terraform and AWS provider; real operations require reviewed account identity. |
| [policies/gate.rego](policies/gate.rego) | Jason Stys: independent Rego gate over adapter evidence; selected baseline, not authorization to deploy. |
| [policies/gate\_test.rego](policies/gate_test.rego) | Jason Stys: independent gate positive/negative invariants for missing, unknown and dangerous evidence. |
| [pyproject.toml](pyproject.toml) | Dependency-free runtime metadata, strict type/lint/test coverage settings. |
| [requirements-dev.in](requirements-dev.in) | Reviewed direct validation dependencies. |
| [requirements-dev.lock](requirements-dev.lock) | Complete hash-locked cross-platform validation graph. |
| [requirements-native.lock](requirements-native.lock) | Exact SHA256-locked native-build tools; runtime dependencies remain separately reviewed. |
| [scripts/\_\_init\_\_.py](scripts/__init__.py) | Repository-owned reproducibility and validation utilities. Created by Jason Stys. |
| [scripts/benchmark.py](scripts/benchmark.py) | Measure bounded in-memory plan-policy cost, not Terraform/AWS latency. Created by Jason Stys. |
| [scripts/bootstrap.py](scripts/bootstrap.py) | Install hash-verified official Terraform/OPA into this repo only, never globally. Jason Stys. |
| [scripts/build\_native.py](scripts/build_native.py) | Build the complete real offline workbench as one Windows portable executable. Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Generate/check exact Python, Terraform, Rego, shell and workflow symbol positions. Created by Jason Stys. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Maintain exhaustive tracked-file README summaries without reading ignored private plans. Jason Stys. |
| [scripts/fixtures.py](scripts/fixtures.py) | Generate independently labeled, strictly fictional Terraform-like plans and cost scenarios. Jason Stys. |
| [scripts/infra\_checks.py](scripts/infra_checks.py) | Real Terraform mocked plans and OPA cross-engine checks, never apply/live AWS. Created by Jason Stys. |
| [scripts/native\_acceptance.py](scripts/native_acceptance.py) | Exercise the same real frozen Tk controls/core on an explicit synthetic profile; no arbitrary scripts. Jason Stys. |
| [scripts/native\_entry.py](scripts/native_entry.py) | Launch the actual bundled offline project workbench; no setup shell commands. Jason Stys. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/test\_native\_app.py](scripts/test_native_app.py) | Run the real frozen workbench twice with an owned synthetic profile and exact bundle persistence. Jason Stys. |
| [scripts/validate.sh](scripts/validate.sh) | Jason Stys: portable fail-fast quality, contracts, negative/property tests and measured policy throughput. |
| [tests/conftest.py](tests/conftest.py) | Reusable isolated synthetic plan fixtures; no real AWS credentials/state. Created by Jason Stys. |
| [tests/test\_cli\_report.py](tests/test_cli_report.py) | End-to-end command exits, report escaping/no-overwrite, cost and comparison flows. Jason Stys. |
| [tests/test\_desktop\_gui.py](tests/test_desktop_gui.py) | Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys. |
| [tests/test\_desktop\_project.py](tests/test_desktop_project.py) | Independent graphical plan/cost/worklist oracles, stale receipts and cumulative actual review. Jason Stys. |
| [tests/test\_desktop\_state.py](tests/test_desktop_state.py) | Independent offline desktop ownership, byte-bound, SQLite and non-overwrite regressions. Jason Stys. |
| [tests/test\_io\_cost.py](tests/test_io_cost.py) | Strict JSON filesystem boundaries and exact-decimal cost oracles. Created by Jason Stys. |
| [tests/test\_maintenance.py](tests/test_maintenance.py) | Documentation map and offline tool archive integrity regression tests. Created by Jason Stys. |
| [tests/test\_plan.py](tests/test_plan.py) | Strict plan input, sensitive masks, bounds and malformed-data negative tests. Created by Jason Stys. |
| [tests/test\_policy.py](tests/test_policy.py) | Independent gate decisions, unknown propagation, KMS/TLS scope and property oracles. Jason Stys. |
| [tests/test\_profile\_admission.py](tests/test_profile_admission.py) | Actual pre-existing alias refusal and ordinary SQLite recovery continuity. Jason Stys. |
| [tests/test\_reader\_races.py](tests/test_reader_races.py) | Actual opened-device and POSIX regular-to-FIFO replacement regressions for bounded readers. Jason Stys. |
| [tests/test\_review.py](tests/test_review.py) | Independent change-shape, stale-review, redaction and user workflow tests. Created by Jason Stys. |
| [tools.lock.json](tools.lock.json) | Official Terraform/OPA/scanner URLs, versions and SHA-256 pins. |

<!-- END FILE GUIDE -->

## Documentation editions

Start with the [organized handbook](docs/handbook.md) for current usage, design, security and test guidance. Reviewed downloadable editions: [project-guide.docx](docs/reports/project-guide.docx).

[Publication identities and source scope](docs/reports/publications.json) · [Documentation validation record](docs/reports/documentation-refresh-2026-11-09.md). Historical results retain their own tested revision and date.

## Historical Windows application guide (1.1.0)

The [version 1.1.0 illustrated guide](docs/reports/windows-application-guide-1.1.0.docx) explains the actual
installed application with two real screenshots, a worked user workflow, important
source excerpts and observed validation. Read the [dated delivery report](docs/reports/installed-windows-2026-11-10.md)
and [byte and page review](docs/reports/windows-application-guide-1.1.0.json) for exact scope. Historical Office
editions remain available with their original baselines.

New documentation files:

- [docs/reports/windows-application-guide-1.1.0.docx](docs/reports/windows-application-guide-1.1.0.docx): Individually reviewed four-page installed application guide with actual screenshots, worked workflow, immutable source excerpts and limits.
- [docs/reports/windows-application-guide-1.1.0.json](docs/reports/windows-application-guide-1.1.0.json): Exact Word, actual screenshot and reviewed page digests plus observed source-specific validation results.
- [docs/screenshots/installed-1.1.0/destructive-change-review.png](docs/screenshots/installed-1.1.0/destructive-change-review.png): Actual installed application synthetic-profile screenshot: Destructive resource change worklist.
- [docs/screenshots/installed-1.1.0/reasoned-resource-receipt.png](docs/screenshots/installed-1.1.0/reasoned-resource-receipt.png): Actual installed application synthetic-profile screenshot: Plan bound resource review receipt.

## Current Windows application guide

The published **1.1.1** app has a [four-page illustrated guide](docs/reports/windows-application-guide-1.1.1.docx) with actual installed screenshots, a worked user journey, important source excerpts and practical limits. Read the [installed-app and upgrade results](docs/reports/installed-windows-1.1.1-2026-11-11.md) and [byte/page review manifest](docs/reports/windows-application-guide-1.1.1.json) for exact scope. Earlier Office editions remain historical and unchanged.
