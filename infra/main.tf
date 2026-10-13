# Jason Stys: isolated network plus private encrypted evidence storage; deliberately no workloads or internet gateway.
# Functions: cidrsubnet/jsonencode built-ins. Variables: var inputs and resource references carry no user secrets.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# block: aws_vpc.lab — line 51
# symbol: cidr_block — line 52
# reference: var.vpc_cidr — line 52
# symbol: enable_dns_support — line 53
# symbol: enable_dns_hostnames — line 54
# block: aws_subnet.private — line 56
# symbol: count — line 57
# symbol: vpc_id — line 58
# reference: count.index — line 59
# symbol: availability_zone — line 60
# reference: var.region — line 60
# symbol: map_public_ip_on_launch — line 61
# block: aws_security_group.sealed — line 63
# symbol: name — line 64
# reference: var.name — line 64
# symbol: description — line 65
# symbol: ingress — line 67
# symbol: egress — line 68
# block: aws_kms_key.evidence — line 70
# symbol: enable_key_rotation — line 72
# symbol: deletion_window_in_days — line 73
# symbol: policy — line 74
# symbol: Version — line 75
# symbol: Statement — line 76
# symbol: Sid — line 77
# symbol: Effect — line 78
# symbol: Principal — line 79
# reference: var.account_id — line 79
# symbol: Action — line 80
# symbol: Resource — line 81
# block: aws_s3_bucket.evidence — line 86
# symbol: bucket — line 87
# symbol: force_destroy — line 88
# block: aws_s3_bucket_public_access_block.evidence — line 91
# symbol: block_public_acls — line 93
# symbol: block_public_policy — line 94
# symbol: ignore_public_acls — line 95
# symbol: restrict_public_buckets — line 96
# block: aws_s3_bucket_ownership_controls.evidence — line 98
# block: aws_s3_bucket_versioning.evidence — line 102
# block: aws_s3_bucket_server_side_encryption_configuration.evidence — line 106
# symbol: bucket_key_enabled — line 109
# symbol: sse_algorithm — line 111
# symbol: kms_master_key_id — line 112
# block: aws_s3_bucket_policy.evidence — line 116
# symbol: Condition — line 126
# END CODE MAP
resource "aws_vpc" "lab" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
}
resource "aws_subnet" "private" {
  count                   = 2
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = "${var.region}${count.index == 0 ? "a" : "b"}"
  map_public_ip_on_launch = false
}
resource "aws_security_group" "sealed" {
  name        = "${var.name}-sealed"
  description = "Explicit deny-all attached group; opt-in application connectivity requires separate review."
  vpc_id      = aws_vpc.lab.id
  ingress     = []
  egress      = []
}
resource "aws_kms_key" "evidence" {
  description             = "Lab evidence key; human-reviewed account root delegates IAM authority."
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AccountKeyAdministration"
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::${var.account_id}:root" }
      Action    = "kms:*"
      Resource  = "*"
    }]
  })
  lifecycle { prevent_destroy = true }
}
resource "aws_s3_bucket" "evidence" {
  bucket        = var.name
  force_destroy = false
  lifecycle { prevent_destroy = true }
}
resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule { object_ownership = "BucketOwnerEnforced" }
}
resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evidence.arn
    }
  }
}
resource "aws_s3_bucket_policy" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [aws_s3_bucket.evidence.arn, "${aws_s3_bucket.evidence.arn}/*"]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}
