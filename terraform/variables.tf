variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name"
  type        = string
  default     = "sample-s3-bucket"
}

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "sample-lambda"
}

variable "ec2_instance_name" {
  description = "EC2 instance name"
  type        = string
  default     = "sample-ec2"
}

