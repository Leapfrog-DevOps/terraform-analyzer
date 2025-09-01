# Terraform Modular Infrastructure

This project creates AWS infrastructure using a modular Terraform approach with the following resources:
- S3 bucket with versioning and encryption
- Lambda function with IAM role
- EC2 t3.small instance with security group

## Usage

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your desired values (ensure S3 bucket name is globally unique)

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Plan the deployment:
   ```bash
   terraform plan
   ```

5. Apply the configuration:
   ```bash
   terraform apply
   ```

## Modules

- `modules/s3/` - S3 bucket configuration
- `modules/lambda/` - Lambda function with Python runtime
- `modules/ec2/` - EC2 instance with security group

## Outputs

The configuration outputs important resource information including bucket name, Lambda ARN, and EC2 instance details.