# Jason Stys: pinned Terraform and AWS provider; real operations require reviewed account identity.
# Functions: none. Variables: region/account_id select an explicitly approved AWS account, not CI credentials.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# symbol: required_version — line 15
# symbol: aws — line 17
# symbol: source — line 18
# symbol: version — line 19
# symbol: region — line 24
# reference: var.region — line 24
# symbol: allowed_account_ids — line 25
# reference: var.account_id — line 25
# symbol: tags — line 27
# END CODE MAP
terraform {
  required_version = "= 1.16.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.68.0"
    }
  }
}
provider "aws" {
  region              = var.region
  allowed_account_ids = [var.account_id]
  default_tags {
    tags = { Project = "infrastructure-policy-lab", Owner = "Jason Stys", Environment = "lab" }
  }
}
