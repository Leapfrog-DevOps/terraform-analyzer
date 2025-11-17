variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name"
  type        = string
  default     = "team-5-bucket-sample-open-source"
}

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "team-5-lambda"
}

variable "ec2_instance_name" {
  description = "EC2 instance name"
  type        = string
  default     = "team-5-ec2"
}

