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
      Creator = "Team 5 Opensource"
      Project = "DevOps_OpenSource"
      Name    = "Team 5"
    }
  }
}

terraform {
  backend "s3" {
    bucket  = "terraform-state-bucket-team5-opensource"
    key     = "terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-locks"
  }
}

# module "vpc" {
#   source   = "./modules/vpc"
#   vpc_name = "team-5-vpc"
# }

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.s3_bucket_name
}
module "s3-dev" {
  source      = "./modules/s3"
  bucket_name = "test-team-5"
}

module "lambda" {
  source         = "./modules/lambda"
  function_name  = var.lambda_function_name
  s3_bucket_name = module.s3.bucket_name
}

# module "ec2" {
#   source        = "./modules/ec2"
#   instance_name = var.ec2_instance_name
#   instance_type = "t3.small"
#   vpc_id        = module.vpc.vpc_id
#   subnet_id     = module.vpc.subnet_id
# }