# Author review and release checklist

Review: author self-review, not independent audit. Author Jason Stys. Scope: bounded plan reader/masks, selected-control assessment, policy engine agreement, cost arithmetic, inert reports, Terraform source/mocks and Actions supply chain.

Architecture/testing guidance kept the implementation non-deploying, unknown/private evidence blocking and tests explicit about scope. Review added selected KMS key binding and nested-mask protection, exact boolean comparisons, strict scoped TLS deny recognition and safe new report directories. Exact decimal costs avoid floating-point rounding. Terraform's emitted mock plan, not only hand-authored samples, is gated by real OPA and Python.

Release gates: complete local tests/lint/types, native provider/schema/mock checks, real Rego rules/independent fixtures, dependency/history scans, strict workflow/shell checks, exact file/symbol maps, security-extended CodeQL, dated reports and latest main CI. Final measured evidence is in validation; uncompleted gates are not claimed here.

Important residual risks: unauthenticated/partial/mask-forged evidence, secret-bearing addresses/real plans, filesystem race/trusted-parent assumptions, plaintext outputs, missing whole-resource/topology/IAM/default-resource/logging/restore assessments, illustrative—not live—prices and self-review. No production approval or complete compliance scan claimed. No scan suppressions or weakened tests added.

Rollback: revert reviewed source; evidence writes never overwrite earlier directories and no host/cloud deployment occurred. Production migration/state/teardown/on-call steps are not applicable to source publication. Any later live account use requires owner/spending/change authorization and separate testing. GitHub billing/storage cleanup is outside this release and requires fresh approval.

## Debug record: cross-platform provider integrity

Expected: the locally passing Terraform/OPA suite also passes on Linux. Actual: [initial Validate run 38467044088](https://github.com/JasonStys/infrastructure-policy-lab/actions/runs/38467044088) passed all core/security lanes, but infrastructure failed during Terraform validate after read-only init because the cached Linux provider did not match an unpacked hash in the lock. Root cause: the initial lock was generated on Windows and had only its h1 hash; signed archive zh hashes allowed package retrieval, but immutable cached-package validation needed the Linux h1 too. CodeQL passed separately. Fix: origin-registry `providers lock` for linux_amd64 and windows_amd64, both retrieved signed by HashiCorp, then commit the additional verified hash. Prevention: explicit maintenance command, multiple-platform/hash regression guard and fresh full CI. No checksum/signature check, read-only lock setting, native gate or test was disabled; the failed attempt remains visible.
