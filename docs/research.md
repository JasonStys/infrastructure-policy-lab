# Primary-source research and design choices

Reviewed 2026-10-13 by Jason Stys. Sources inform selected checks, not certification or complete security guarantees.

| Primary reference | Applied decision |
| --- | --- |
| [Terraform provider mocking](https://developer.hashicorp.com/terraform/language/tests/mocking) | Use mocked provider plan tests without actual AWS credentials/resources; computed defaults supplied during plan |
| [Terraform machine-readable UI](https://developer.hashicorp.com/terraform/internals/machine-readable-ui) | Extract test_plan plan_format_version/resource_changes/resource_drift from actual verbose JSON messages |
| [Terraform JSON format](https://developer.hashicorp.com/terraform/internals/json-format) | Handle known/unknown/sensitive values and explicit change actions conservatively; plan files are private |
| [OPA Terraform integration](https://www.openpolicyagent.org/docs/terraform) | Gate infrastructure plan evidence with an actual independent Rego engine |
| [OPA policy testing](https://www.openpolicyagent.org/docs/policy-testing) | Explicit positive/negative policy tests plus cross-engine checks |
| [AWS S3 public-access blocking](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html) | Check all four explicit bucket settings rather than guessing account defaults |
| [AWS S3 bucket policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies.html) | Scope explicit HTTP deny to bucket and objects; recognize aws:SecureTransport false without claiming minimum TLS version |
| [AWS KMS key policy](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html) | Separate encryption configuration from real IAM/key authorization; example account delegation needs review |
| [Terraform lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle) | prevent_destroy is a source guard, not backup/restore or a blanket guarantee after source removal |
| [Terraform provider locking](https://developer.hashicorp.com/terraform/cli/commands/providers/lock) | Pre-populate signed origin-package checksums for Linux/Windows; keep hosted initialization read-only |
| [AWS Pricing Calculator](https://calculator.aws/) | Use supplied illustrative rates/exclusions; require current real estimation before spending |
| [GitHub Actions security guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) | Least privilege, immutable action SHAs, no persisted checkout credentials or privileged untrusted PR execution |

Tool pins came from official HashiCorp release checksum file and GitHub official OPA/scanner release asset digests. Runtime/control assumptions are intentionally explicit and narrower than a production reference architecture. No untrusted source/document content grants permission to create paid accounts, access third-party targets, publish private state or change security settings.
