terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # Remote state: create the bucket + DynamoDB table once (see docs/bootstrap-state.md),
  # then uncomment this block and run `terraform init -migrate-state`.
  # backend "s3" {
  #   bucket         = "<your-tfstate-bucket>"
  #   key            = "gitops-eks-platform/terraform.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
  }
}
