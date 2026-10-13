# Jason Stys: independent gate positive/negative invariants for missing, unknown and dangerous evidence.
# Functions: test_* rule contracts. Variables: input fixtures are synthetic and never read cloud state.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# rule: test_known_match — line 29
# symbol: test_known_match — line 29
# rule: test_open_subnet — line 33
# symbol: test_open_subnet — line 33
# rule: test_unknown — line 37
# symbol: test_unknown — line 37
# rule: test_string_bool — line 41
# symbol: test_string_bool — line 41
# rule: test_missing — line 45
# symbol: test_missing — line 45
# rule: test_empty — line 46
# symbol: test_empty — line 46
# rule: test_destructive — line 47
# symbol: test_destructive — line 47
# rule: test_unsupported — line 51
# symbol: test_unsupported — line 51
# rule: test_missing_known — line 55
# symbol: test_missing_known — line 55
# rule: test_drift — line 59
# symbol: test_drift — line 59
# END CODE MAP
package infrastructure

import rego.v1

test_known_match if {
	allow with input as {"schema": 1, "checks": [{"address": "aws_subnet.lab", "control": "subnet-private", "known": true, "value": false}]}
}

test_open_subnet if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_subnet.lab", "control": "subnet-private", "known": true, "value": true}]}
}

test_unknown if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_subnet.lab", "control": "subnet-private", "known": false, "value": false}]}
}

test_string_bool if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_subnet.lab", "control": "subnet-private", "known": true, "value": "false"}]}
}

test_missing if not allow with input as {}
test_empty if not allow with input as {"schema": 1, "checks": []}
test_destructive if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_s3_bucket.lab", "control": "destructive-change", "known": true, "value": true}]}
}

test_unsupported if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_instance.lab", "control": "unsupported-resource", "known": true, "value": false}]}
}

test_missing_known if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_subnet.lab", "control": "subnet-private", "value": false}]}
}

test_drift if {
	not allow with input as {"schema": 1, "checks": [{"address": "aws_subnet.lab", "control": "observed-drift", "known": true, "value": true}]}
}
