# Terraform AI Analyzer Action

Automatically analyze and fix Terraform errors using AI, with optional cost analysis.

## Features

- 🤖 AI-powered Terraform error analysis using OpenAI
- 🔧 Automatic fix generation and application

- 🔄 Auto-creates PR with fixes
- 📝 Detailed analysis reports

## Usage

```yaml
name: Terraform CI/CD
on: [push, pull_request]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.11.4
      
      - name: Terraform Init
        run: terraform init
        continue-on-error: true
      
      - name: Terraform Plan
        run: terraform plan -out=tfplan 2>&1 | tee terraform.log
        continue-on-error: true
      
      - name: Analyze Terraform Errors
        if: failure()
        uses: your-username/terraform-ai-analyzer@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          terraform-directory: './terraform'
          auto-fix: 'true'
          run-cost-analysis: 'true'
          infracost-api-key: ${{ secrets.INFRACOST_API_KEY }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `openai-api-key` | OpenAI API key for AI analysis | Yes | - |
| `github-token` | GitHub token for creating PRs | Yes | - |
| `terraform-directory` | Directory containing Terraform files | No | `./terraform` |
| `auto-fix` | Automatically apply fixes and create PR | No | `true` |
| `branch-name` | Branch name for auto-fixes | No | `auto-tf-fix` |


## Outputs

| Output | Description |
|--------|-------------|
| `fixes-applied` | Number of fixes applied |
| `analysis-summary` | AI analysis summary |


## How it Works

1. **Error Detection**: Analyzes Terraform logs for errors
2. **AI Analysis**: Uses OpenAI to understand and generate fixes
3. **Code Fixing**: Automatically applies fixes to Terraform files
4. **PR Creation**: Creates a pull request with the fixes


## Prerequisites

- OpenAI API key with access to GPT-4
- GitHub token with repository write permissions


## Supported Terraform Resources

- All AWS resources (EC2, S3, RDS, Lambda, etc.)
- Preserves original code structure and formatting
- Handles complex nested configurations
- Maintains all existing attributes and tags

## License

MIT License - see LICENSE file for details