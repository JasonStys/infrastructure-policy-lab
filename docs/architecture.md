# ADR-001: Offline plan assurance with actual provider-mocked IaC tests

Status: Accepted. Date: 2026-10-13. Decider/author: Jason Stys.

## Context and decision

The portfolio needs verifiable cloud infrastructure and policy engineering without an existing hosting account, spending authority, cloud credentials or changes to this PC. Build real Terraform/AWS configuration, test it through provider mocks, then inspect emitted plan changes in a dependency-free Python adapter and independent Rego gate. CI does not apply/destroy, reach real AWS APIs or retain artifacts/caches.

Data path: Terraform mocked plan → strict managed-change contract → selected known/non-sensitive facts → Python assessment + real OPA gate → deterministic reports. A separate user-supplied cost scenario produces exact-decimal arithmetic. Plan comparisons are not live drift collection; `resource_drift` represents Terraform's own reported evidence.

## Options considered

| Option | Complexity/cost | Reproducibility | Trade-off |
| --- | --- | --- | --- |
| Real disposable AWS account | High; credentials and resource charges | API/permission dependent | Best runtime evidence, but outside approved account/spending scope |
| Handwritten JSON alone | Low/free | Strong offline replay | Cannot prove Terraform/provider configuration works |
| Mocked Terraform + offline gates (selected) | Medium/no cloud resource cost | Locked provider/tools, repeatable plans | Real config/schema tests, but no actual AWS API/network/IAM guarantees |

Python suits bounded JSON contracts/reporting and exact-decimal arithmetic without runtime dependencies; HCL models infrastructure relationships and input validation; Rego provides an independently authored policy decision. Duplicated expected values are intentional cross-engine checks and require synchronized review/tests, not a claim of independent auditing.

## Performance and boundaries

For R resources, C selected fields and bounded masks: validation is O(R log R + input bytes); extraction/evaluation O(R+C) with hashed KMS membership; sorting findings/comparisons O(C log C). Space is O(input bytes+C). A benchmark excludes parsing, Terraform/provider init, OPA, reports and network, so cannot establish cloud deployment capacity. Limits: 8 MiB JSON, depth 32, 2,000 changes/drift entries and bounded strings/lists.

Consequences: runs need no credentials; missing/private evidence fails closed; development/runtime responsibilities remain small. Mocks cannot establish API authorization, backend locking, default VPC resources, completeness of architecture, runtime connectivity or durability. Revisit actual isolated-account tests, default-resource management, monitoring/retention, IAM/KMS review, complete topology/relationship checks, remote-state encryption/locking and real billing before production use.

Release actions: validate contracts/properties, real Terraform/OPA cases, supply-chain/security gates, exact file/symbol maps and current main CI; publish dated evidence/limits. No production deployment/approval is implied.
