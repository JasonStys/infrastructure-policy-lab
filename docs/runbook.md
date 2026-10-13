# Operator runbook and safe change/teardown procedure

Use this lab for offline review and learning, never as sole authority for a deployment. Contact author [Jason Stys](https://www.linkedin.com/in/jason-stys-31b30b351/). Python CLI works offline from the root; native Terraform/OPA checks additionally download pinned official tools/provider dependencies and require network to vendor registries, not AWS credentials.

## Demonstrate and review

1. Read README and scope/threat model. Run healthy/insecure fixtures and confirm documented counts/exits. Use a new output directory under an existing private parent; open report.html locally.
2. Review FAIL/UNKNOWN/REVIEW rather than treating them as automatic findings to remediate. Check the actual private plan, source identity, applicability, drift, account scope and human approval. Unknowns are not waived.
3. Compare only same-account/scope reviewed plans. Investigate every added/removed check; fewer findings are not necessarily improvement. Reported Terraform drift is evidence, not an active scanner.
4. Enter your own cost workload/rates/exclusions; verify current region/tiers/usage with AWS Pricing Calculator before any purchase/deployment. The illustrative $1.55 sample is not a promise.

## Native validation

Bootstrap Terraform then OPA once into ignored .tools; if existing tools are present the installer refuses overwriting. Inspect pinned hashes/version before maintaining tools, never bypass checksum/TLS errors. Run `python -m scripts.infra_checks`. On Windows use `.venv\Scripts\python.exe` if an isolated environment is installed. The runner executes five mock-provider plan cases plus real Rego/fixture checks. A timeout/version/provider schema failure is a failed check; inspect logs rather than skip it. No AWS account login is needed.

## Real deployment is a separate, unvalidated workflow

This release does not deploy. Before using the Terraform source with a real account, obtain explicit owner/spending/change authorization, use a dedicated least-privilege sandbox identity and isolated encrypted/locked state, check allowed account ID and region, and design missing defaults/routes/identity/logging/retention/recovery. Never use production credentials, broad administrator secrets or real state in public CI. Read plan JSON only in private storage; Terraform sensitive flags do not encrypt it.

Have a human review the full plan and policy findings, estimated total costs and exact deletions/replacements. Protect existing buckets/keys; source prevents destroying these by default. A gate PASS is not an approval to apply; mocks do not test real IAM/API calls. Deployment credentials and actual apply are intentionally absent from this repo's automation.

## Safe teardown and rollback, no automated deletion

No lab resources were created by these tests, so no cloud teardown is needed. For a separately approved real sandbox, first identify the exact account/state/workspace and all owned resources. Save/recover evidence and **all object versions**, verify restore requirements and retention/legal holds, then have the owner approve any destructive plan. Bucket/KMS `prevent_destroy` must remain until deliberate source review permits teardown; force_destroy remains false. Do not empty/delete buckets, bypass lifecycle guards, disable keys or run an unreviewed destroy command. A destroy plan is not proof safe-to-delete data. Handle default VPC resources, billing and retained versions separately and verify final account inventory/costs.

Rollback during this build is source revert only; tools never mutate host/cloud settings. Existing report directories are preserved, not overwritten. Public repo updates can be reverted to a reviewed commit; do not reset/remove user changes. Security findings can be privately reported through LinkedIn without sharing credentials/state.
