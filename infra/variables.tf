# Jason Stys: validated non-secret inputs; no real credentials or deployment defaults.
# Functions: validation built-ins only. Variables: account_id, region, name and CIDRs describe owned lab scope.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# block: account_id — line 18
# symbol: description — line 19
# symbol: type — line 20
# symbol: condition — line 22
# reference: var.account_id — line 22
# symbol: error_message — line 23
# block: region — line 26
# symbol: default — line 29
# reference: var.region — line 31
# block: name — line 35
# reference: var.name — line 39
# block: vpc_cidr — line 43
# reference: var.vpc_cidr — line 48
# END CODE MAP
variable "account_id" {
  description = "Approved 12-digit account ID; tests use fictional 123456789012, never real credentials."
  type        = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.account_id))
    error_message = "Use one explicit 12-digit account ID."
  }
}
variable "region" {
  description = "Pinned commercial AWS region; changing regions requires price/provider review."
  type        = string
  default     = "us-west-2"
  validation {
    condition     = var.region == "us-west-2"
    error_message = "This authored lab is reviewed only for us-west-2."
  }
}
variable "name" {
  description = "Globally unique non-sensitive bucket/lab name, 3–40 lowercase characters."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,38}[a-z0-9]$", var.name))
    error_message = "Use a lowercase DNS-safe 3–40 character name."
  }
}
variable "vpc_cidr" {
  description = "Isolated lab IPv4 /16, restricted to private 10.0.0.0/8."
  type        = string
  default     = "10.42.0.0/16"
  validation {
    condition     = can(cidrnetmask(var.vpc_cidr)) && can(regex("^10\\.[0-9]+\\.0\\.0/16$", var.vpc_cidr))
    error_message = "Use a canonical 10.x.0.0/16 private IPv4 network."
  }
}
