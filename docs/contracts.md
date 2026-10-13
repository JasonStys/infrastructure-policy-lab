# Plan, policy, cost and report contracts

## Accepted plan input

Offline JSON equivalent to `terraform show -json` plan output: `format_version` major 1 (`1.<minor>`), 1–2,000 explicit managed `resource_changes`, unique bounded resource addresses/types, recognized action arrays, `after` consistent with deletion and typed unknown/sensitive masks. Data-source entries, empty inventories, unsupported action kinds and `complete=false`/`errored=true` are rejected. A missing complete flag remains supported for older/test plan schemas; no freshness or completeness of the real account is inferred. Unknown root/provider fields are not interpreted.

Actions supported: no-op/create/update/delete/read and either delete-create replacement order. Any delete blocks for REVIEW. `read` is parsed but does not independently authorize a managed resource read. `resource_drift` lists unique addresses; any entry blocks for REVIEW. The native test adapter maps `test_plan.plan_format_version` to `format_version` and extracts only changes/drift, not large provider schemas. Source/mock evidence is unsigned.

JSON: at most 8 MiB, 32 nested levels, 10,000 elements per collection, strings <=262,144 characters, exact types, duplicate-key/nonfinite rejection, UTF-8 BOM accepted. Embedded control characters/DEL/lone surrogates are conservatively rejected even in otherwise valid JSON strings. Inputs must be regular final files, not links/junctions; trusted non-concurrent parent workspace is required. Missing/wrong critical field types cannot become PASS. Masks accept booleans or nested dict/list structures only; any marked ancestor/descendant blocks selected values.

## Selected authored baseline

| Type | Checks |
| --- | --- |
| VPC | DNS support true (operational baseline, not filtering proof) |
| Subnet | Automatic public-IP mapping false |
| Attached example security group | Explicit empty ingress and egress |
| S3 bucket | force_destroy false; lifecycle prevent_destroy tested in authored source, not recoverable from arbitrary plans |
| S3 public-access block | All four switches true |
| S3 ownership/versioning | BucketOwnerEnforced / Enabled |
| S3 encryption | aws:kms and known ARN matching a selected KMS resource in this plan |
| S3 policy | Strict recognized all-principal HTTP deny covering exactly its bucket and objects |
| KMS | Automatic rotation true; 30-day deletion window |

These are **selected checks, not graph completeness**: absence of an entire resource type, provider defaults, source/module integrity, bucket attachment relationships beyond TLS/KMS checks, KMS key-policy and effective IAM permissions, public network routes/default security groups, resource lifecycle guards and logging/retention are not generally inferred from plans. A partial supported inventory can pass selected checks; it is not approved infrastructure. Unknown future types are explicitly UNKNOWN rather than ignored.

Statuses: PASS exact match; FAIL observed mismatch/malformed field; UNKNOWN missing/unresolved/sensitive/unsupported evidence; REVIEW deletion/replacement/reported drift. `allowed=true` means every selected finding is PASS only, never approval to apply. Missing selected key ARN yields UNKNOWN when unresolved; observed mismatched known key yields FAIL. Findings retain resource address/control/status/guidance but no raw settings or secret payload. Addresses can themselves reveal private names and must remain private for real inputs. Semantic input SHA-256 identifies bytes' parsed meaning (including list order), not signer/authenticity; it is not a secret anonymizer.

Rego expects normalized `{schema:1,checks:[{address,control,known,value}]}` from the trusted adapter. It denies empty/unknown/unsupported/destructive/drift evidence; it is not safe to treat a hand-written normalized JSON document as authentic or complete. The fixed expected map is authored in Rego, not supplied by the caller. Native CI compares actual OPA and Python decisions.

## Cost and reports

Cost schema 1: USD, nonempty label/exclusions, 1–50 unique named items with decimal-string `quantity`/`unit_price`, nonnegative <=1,000,000 and <=20 characters, explicit units. No signs/exponents/floats/booleans. Decimal products accumulate exactly; final total rounds half-up to cents. Supplied rates are illustrative—not a current AWS quote. Taxes, transfer, API requests, version retention, logs/support and other services can dominate a real bill. No network prices, deployment, budget enforcement or purchases occur.

Assessment comparison re-assesses two plans and indexes address/control/status, yielding added/removed/changed selected checks. It has no live AWS identity, acquisition timestamp or same-account verification. Only compare plans from the same reviewed scope/account. Exports require a new directory with existing trusted parent; links/junctions/overwrite are refused. Partial output remains for review after failures. Files are plaintext; Windows mode bits do not enforce Windows ACLs. HTML is escaped, scriptless, no remote assets/ads/analytics, deny-default meta CSP; no production web-service guarantee is implied.
