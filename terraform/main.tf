terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Creator = "sample-creator"
      Project = "sample-project"
      Name    = "sample-name"
    }
  }
}

terraform {
  backend "s3" {
    bucket  = "sample-bucket"
    key     = "sample.tfstate"
    region  = "us-east-1"
    encrypt = true
    dynamodb_table = "sample-locks-table"
  }
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.s3_bucket_name
}
module "s3_sample_test" {
  source      = "./modules/s3"
  bucket_name = "sample-test-bucket"
}

module "lambda" {
  source         = "./modules/lambda"
  function_name  = var.lambda_function_name
  s3_bucket_name = module.s3.bucket_name
}
