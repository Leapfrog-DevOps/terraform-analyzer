# Terraform Analyzer

An intelligent Terraform automation tool that combines infrastructure deployment with AI-powered error analysis and cost optimization. This project provides automated Terraform workflows with built-in error detection, automatic fixes, and cost analysis using OpenAI and Infracost.

## 🚀 Features

### Core Capabilities
- **Automated Terraform Operations**: Plan and apply infrastructure changes via GitHub Actions
- **AI-Powered Error Analysis**: Automatically analyzes Terraform failures using OpenAI GPT-4
- **Intelligent Auto-Fix**: Generates and applies code fixes for common Terraform errors
- **Cost Analysis**: Integrates with Infracost for infrastructure cost estimation and tracking
- **Pull Request Integration**: Provides detailed plan summaries and cost breakdowns in PR comments

### Infrastructure Components
- **AWS S3**: Bucket creation and management
- **AWS Lambda**: Function deployment with S3 integration
- **AWS EC2**: Instance provisioning (modular)
- **AWS VPC**: Network infrastructure (modular)
- **Remote State**: S3 backend with DynamoDB locking

## 📁 Project Structure

```
terraform-analyzer/
├── .github/workflows/
│   ├── terraform-analyzer.yml    # Main Terraform workflow
│   └── cost-analyzer.yml         # Cost analysis workflow
├── terraform/
│   ├── modules/                  # Reusable Terraform modules
│   │   ├── s3/                  # S3 bucket module
│   │   ├── lambda/              # Lambda function module
│   │   ├── ec2/                 # EC2 instance module
│   │   ├── vpc/                 # VPC networking module
│   │   └── remote-state/        # State management module
│   ├── main.tf                  # Main Terraform configuration
│   ├── variables.tf             # Input variables
│   └── outputs.tf               # Output values
├── terraform-analyzer.py        # AI error analysis script
└── README.md
```

## 🛠️ Setup & Configuration

Choose your preferred deployment method:

## 🚀 Option 1: GitHub Marketplace Action (Recommended)

**Perfect for**: Quick setup, existing projects, minimal configuration

### ⚡ Quick Start

```yaml
name: Terraform AI Analyzer
on:
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      action:
        type: choice
        options: [plan, apply]
        default: plan

permissions:
  id-token: write
  contents: write
  pull-requests: write

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Terraform AI Analyzer
        uses: Leapfrog-DevOps/terraform-analyzer@v0.3
        with:
          deployment-role: ${{ secrets.AWS_DEPLOYMENT_ROLE }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          infracost-api-key: ${{ secrets.INFRACOST_API_KEY }}
          action: ${{ github.event.inputs.action || 'plan' }}
```

### 📋 Prerequisites

- **AWS Account** with OIDC provider configured
- **OpenAI API Key** ([Get here](https://platform.openai.com/api-keys))
- **Infracost API Key** ([Get here](https://dashboard.infracost.io/)) - Optional, 1,000 free runs/month
- **GitHub repository** with Actions enabled

### 🔧 Required Secrets

Add these to your repository secrets:

| Secret | Description | Example |
|--------|-------------|----------|
| `AWS_DEPLOYMENT_ROLE` | AWS IAM role ARN for OIDC | `arn:aws:iam::123456789:role/deployment-role` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `INFRACOST_API_KEY` | Infracost API key (optional) | `ico-...` |

### ⚙️ Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|----------|
| `terraform-version` | Terraform version | No | `1.11.4` |
| `terraform-directory` | Directory with Terraform files | No | `./terraform` |
| `action` | Terraform action (plan/apply) | No | `plan` |
| `aws-region` | AWS region | No | `us-east-1` |
| `deployment-role` | AWS IAM role ARN | **Yes** | - |
| `openai-api-key` | OpenAI API key | **Yes** | - |
| `infracost-api-key` | Infracost API key | No | - |
| `enable-cost-analysis` | Enable cost analysis | No | `true` |
| `comment-pr` | Comment on PRs | No | `true` |

### 📤 Action Outputs

| Output | Description |
|--------|--------------|
| `plan-exitcode` | Terraform plan exit code |
| `apply-exitcode` | Terraform apply exit code |
| `has-changes` | Whether plan detected changes |
| `cost-analysis` | Cost analysis results |

---

## 🏗️ Option 2: Full Repository Setup

**Perfect for**: Custom workflows, advanced configuration, learning the internals

### 📋 Prerequisites
- **AWS Account** with appropriate permissions
- **GitHub repository** with Actions enabled  
- **OpenAI API key** for error analysis
- **Infracost API key** for cost analysis (optional)
- **Git** installed locally
- **Terraform CLI** (optional for local testing)

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Leapfrog-DevOps/terraform-analyzer.git
cd terraform-analyzer
```

#### 2. Add Your Terraform Code
> ⚠️ **IMPORTANT**: The current Terraform code in this repository is just a placeholder for demonstration purposes. **DO NOT run it directly** as it may create unwanted AWS resources or fail due to missing dependencies.

Replace the placeholder code with your actual Terraform infrastructure:

**Custom Directory Setup (Optional):**
If you prefer a different directory structure:
1. Create your custom folder (e.g., `infrastructure/`)
2. Update `CODE_PATH` variable in `terraform-analyzer.py`
3. Update working directory paths in `.github/workflows/terraform-analyzer.yml`
```bash
# Remove existing placeholder files
rm -rf terraform/*

# Add your .tf files to terraform/ directory
# Example structure:
terraform/
├── main.tf          # Your main configuration
├── variables.tf     # Input variables
├── outputs.tf       # Output values
└── modules/         # Custom modules (optional)
```

#### 3. Setup API Keys

**Get OpenAI API Key:**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy the key (starts with `sk-`)

**Get Infracost API Key:**
1. Visit [Infracost Dashboard](https://dashboard.infracost.io/)
2. Sign up/login and get API key
3. Copy the key (starts with `ico-`)

#### 4. Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

**Add Repository Secrets:**
```yaml
DEPLOYMENT_ROLE: arn:aws:iam::<your-account>:role/deployment-role
OPENAI_API_KEY: sk-your-openai-key-here
INFRACOST_API_KEY: ico-your-infracost-key-here
# GITHUB_TOKEN is automatically provided
```

**Add Repository Variables:**
```yaml
AWS_REGION: us-east-1
ENVIRONMENT: dev
DEPLOY_LAMBDA: true
```

#### 5. Setup AWS Deployment Role

**Create IAM Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<your-account>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:<your-org-name>/<your-repo-name>:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

**Attach Required Policies:**
- S3 bucket operations
- Lambda function management
- EC2 instance management
- DynamoDB table access (for state locking)
- IAM permissions for resource creation

#### 6. Setup Remote State (First Time Only)
Create S3 bucket and DynamoDB table for Terraform state:
```bash
# Create S3 bucket for state
aws s3 mb s3://terraform-state-bucket-team5-opensource --region us-east-1

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## 🚦 Running the Project

### Method 1: Automatic Triggers
The workflow automatically runs on:
- **Pull Requests** to `final_test` branch → Runs `terraform plan`
- **Manual Dispatch** → Choose between `plan` or `apply`

### Method 2: Manual Execution
1. Go to Actions tab in your repository
2. Select "Terraform - Plan & Apply" workflow
3. Click "Run workflow"
4. Choose action: `plan` or `apply`
5. Click "Run workflow" button

### Method 3: Create Pull Request
1. Create a new branch:
   ```bash
   git checkout -b feature/my-infrastructure
   ```
2. Make changes to Terraform files
3. Commit and push:
   ```bash
   git add .
   git commit -m "Add new infrastructure"
   git push origin feature/my-infrastructure
   ```
4. Create PR to `final_test` branch
5. Workflow automatically runs `terraform plan`

### First Run Setup
> ⚠️ **WARNING**: Make sure you have replaced the placeholder Terraform code with your actual infrastructure code before running any workflows.

1. Ensure all secrets and variables are configured
2. Replace placeholder Terraform code with your actual infrastructure
3. Run manual workflow with `plan` action first
4. Review the plan output in GitHub Actions
5. If plan looks good, run with `apply` action
6. Monitor logs for any errors or AI auto-fixes

### Workflow Behavior

#### On Pull Request
1. Runs `terraform plan`
2. Posts plan summary as PR comment
3. **If plan fails**: Triggers AI error analysis and creates auto-fix branch ![Plan Fail](screenshots/failed_pipeline.png) ![Terraform Fix](screenshots/terraform_fix.png)
4. **If plan succeeds**: Uploads plan artifacts and triggers cost analyzer workflow ![Cost Analysis](screenshots/infracost.png)

#### On Manual Apply
1. Runs `terraform apply`
2. If successful, create infrastructure
3. If errors occur, runs the analyzer and attempts and push to auto-fix branch.

## 🤖 AI Error Analysis

### How It Works
When Terraform operations fail, the analyzer:

1. **Extracts Context**: Parses error logs and identifies relevant files
2. **AI Analysis**: Sends complete code context to OpenAI GPT-4
3. **Generates Fixes**: Creates corrected Terraform code blocks
4. **Applies Changes**: Automatically updates files with fixes
5. **Creates PR**: Pushes fixes to `auto-tf-fix` branch

### Supported Error Types
- Resource configuration errors
- Provider version conflicts
- Variable reference issues
- Module configuration problems
- AWS resource conflicts

### Auto-Fix Features
- Preserves original code structure
- Only modifies problematic sections
- Creates backup files before changes
- Generates detailed fix explanations
- Maintains code formatting and style

## 💰 Cost Analysis

### Infracost Integration
- Analyzes infrastructure costs before deployment
- Compares costs between different plan versions
- Tracks cost changes over time
- Stores cost data in dedicated `infracost` branch
- **Cost Baseline**: Uses `infracost` branch as cost state reference for drift detection
- **Free Tier**: Up to 1,000 runs per month at no cost

### Cost Tracking
- Baseline costs stored per environment
- Diff analysis for PR changes
- Historical cost data retention
- Integration with GitHub step summaries

## 🔧 Configuration

### Terraform Variables
Customize infrastructure in `terraform/variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name"
  type        = string
  default     = "sample-open-source"
}

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "sample-lambda"
}
```

### Workflow Customization
Modify `.github/workflows/terraform-analyzer.yml` to:
- Change trigger branches
- Adjust Terraform version
- Modify auto-fix branch names
- Configure additional AWS regions

## 📊 Monitoring & Debugging

### Logs & Artifacts
- Terraform logs stored in `logs/terraform.log`
- Plan files uploaded as GitHub artifacts
- Cost analysis results in step summaries
- Auto-fix results in GitHub summaries

### Troubleshooting
1. Check workflow logs for detailed error information
2. Review AI analysis output in failed runs
3. Examine auto-fix branch for proposed changes
4. Verify AWS permissions and credentials

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Create Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For issues and questions:
- Create GitHub Issues for bugs and feature requests
- Check workflow logs for deployment issues
- Review AI analysis output for Terraform errors
- Consult AWS documentation for permission issues

## 🔮 Plan for Future

We are planning to build our own AI-powered open source cost analyzer.

---

**Built with ❤️ by Terraform Analyzer Team**