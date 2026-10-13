# Jason Stys: provider-mocked plan assertions; no live AWS APIs, credentials, apply or destroy.
# Functions: Terraform assert/expect_failures. Variables: explicit synthetic identity and lab name.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# symbol: override_during — line 27
# block: aws_s3_bucket — line 28
# symbol: defaults — line 29
# symbol: id — line 30
# symbol: arn — line 31
# block: aws_kms_key — line 34
# symbol: account_id — line 41
# symbol: name — line 42
# block: baseline — line 44
# symbol: command — line 45
# symbol: condition — line 47
# symbol: error_message — line 48
# block: reject_account — line 67
# symbol: expect_failures — line 70
# reference: var.account_id — line 70
# block: reject_name — line 72
# reference: var.name — line 75
# block: reject_region — line 77
# reference: var.region — line 80
# block: reject_public_network — line 82
# reference: var.vpc_cidr — line 85
# END CODE MAP
mock_provider "aws" {
  override_during = plan
  mock_resource "aws_s3_bucket" {
    defaults = {
      id  = "fictional-evidence-lab"
      arn = "arn:aws:s3:::fictional-evidence-lab"
    }
  }
  mock_resource "aws_kms_key" {
    defaults = {
      arn = "arn:aws:kms:us-west-2:123456789012:key/00000000-0000-0000-0000-000000000001"
    }
  }
}
variables {
  account_id = "123456789012"
  name       = "fictional-evidence-lab"
}
run "baseline" {
  command = plan
  assert {
    condition     = length(aws_subnet.private) == 2 && alltrue([for subnet in aws_subnet.private : !subnet.map_public_ip_on_launch])
    error_message = "Subnets must remain private."
  }
  assert {
    condition     = length(aws_security_group.sealed.ingress) == 0 && length(aws_security_group.sealed.egress) == 0
    error_message = "Sealed group must not allow traffic."
  }
  assert {
    condition     = aws_kms_key.evidence.enable_key_rotation && aws_kms_key.evidence.deletion_window_in_days == 30
    error_message = "Rotation and recovery window must remain enabled."
  }
  assert {
    condition     = !aws_s3_bucket.evidence.force_destroy && aws_s3_bucket_public_access_block.evidence.block_public_acls && aws_s3_bucket_public_access_block.evidence.block_public_policy && aws_s3_bucket_public_access_block.evidence.ignore_public_acls && aws_s3_bucket_public_access_block.evidence.restrict_public_buckets
    error_message = "Bucket protection is required."
  }
  assert {
    condition     = one(aws_s3_bucket_versioning.evidence.versioning_configuration).status == "Enabled" && one(one(aws_s3_bucket_server_side_encryption_configuration.evidence.rule).apply_server_side_encryption_by_default).sse_algorithm == "aws:kms"
    error_message = "Versioning and KMS encryption are required."
  }
}
run "reject_account" {
  command = plan
  variables { account_id = "invalid" }
  expect_failures = [var.account_id]
}
run "reject_name" {
  command = plan
  variables { name = "INVALID" }
  expect_failures = [var.name]
}
run "reject_region" {
  command = plan
  variables { region = "us-east-1" }
  expect_failures = [var.region]
}
run "reject_public_network" {
  command = plan
  variables { vpc_cidr = "8.8.0.0/16" }
  expect_failures = [var.vpc_cidr]
}
