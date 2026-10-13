# Jason Stys: independent Rego gate over adapter evidence; selected baseline, not authorization to deploy.
# Functions: allow/check_ok. Variables: check, expected and input.checks; unknown/empty/destructive evidence blocks.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# symbol: expected — line 20
# default: allow — line 39
# rule: allow — line 41
# symbol: allow — line 41
# symbol: input.schema — line 42
# reference: input.schema — line 42
# reference: input.checks — line 43
# variable: check — line 45
# rule: check_ok — line 50
# symbol: check.known — line 51
# symbol: check.value — line 54
# END CODE MAP
package infrastructure

import rego.v1

expected := {
	"vpc-dns": true,
	"subnet-private": false,
	"sg-ingress-deny": [],
	"sg-egress-deny": [],
	"bucket-preserve": false,
	"s3-block_public_acls": true,
	"s3-block_public_policy": true,
	"s3-ignore_public_acls": true,
	"s3-restrict_public_buckets": true,
	"s3-versioning": "Enabled",
	"s3-kms": "aws:kms",
	"s3-kms-key-scoped": true,
	"s3-owner": "BucketOwnerEnforced",
	"s3-tls-deny": true,
	"kms-rotation": true,
	"kms-deletion-window": 30,
}

default allow := false

allow if {
	input.schema == 1
	is_array(input.checks)
	count(input.checks) > 0
	every check in input.checks {
		check_ok(check)
	}
}

check_ok(check) if {
	check.known == true
	is_string(check.address)
	count(check.address) > 0
	check.value == expected[check.control]
}
