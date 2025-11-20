# Contributing to Terraform Analyzer

Thank you for your interest in contributing to Terraform Analyzer! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Git
- Python 3.11+
- Terraform CLI (optional)
- AWS CLI (for testing)
- GitHub account

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/Leapfrog-DevOps/terraform-analyzer.git
   cd terraform-analyzer
   ```

2. **Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install Dependencies**
   ```bash
   pip install openai python-hcl2
   ```

## 📝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide clear reproduction steps** for bugs
4. **Include relevant logs and screenshots**

### Suggesting Features

When suggesting new features:

1. **Check existing feature requests** first
2. **Explain the use case** and benefits
3. **Consider implementation complexity**
4. **Provide mockups or examples** if applicable

### Code Contributions

#### Areas for Contribution

- **AI Error Analysis**: Improve error detection and fix generation
- **Cost Analysis**: Enhance Infracost integration and reporting
- **Terraform Modules**: Add support for new AWS services
- **GitHub Actions**: Improve workflow automation
- **Documentation**: Enhance guides and examples
- **Testing**: Add test coverage and validation

#### Development Guidelines

1. **Follow existing code style** and patterns
2. **Write clear, descriptive commit messages**
3. **Add comments for complex logic**
4. **Update documentation** for new features
5. **Test your changes** thoroughly

#### Commit Message Format

```
type(scope): brief description

Detailed explanation of changes (if needed)

Fixes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(ai): add support for provider version conflicts
fix(cost): resolve infracost branch creation issue
docs(readme): update setup instructions for marketplace action
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Your Changes**
   - Follow coding standards
   - Add/update tests if applicable
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Test the Python analyzer
   python terraform-analyzer.py
   
   # Test GitHub Actions locally (if possible)
   # Validate Terraform configurations
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat(scope): your change description"
   git push origin feature/your-feature
   ```

5. **Create Pull Request**
   - Use the PR template
   - Link related issues
   - Provide clear description
   - Add screenshots if UI changes

### PR Review Process

- **Automated Checks**: All PRs run automated tests
- **Code Review**: Maintainers will review your code
- **Feedback**: Address any requested changes
- **Approval**: Once approved, maintainers will merge

## 🧪 Testing

### Manual Testing

1. **Test AI Analysis**
   ```bash
   # Create a Terraform error scenario
   # Run the analyzer
   python terraform-analyzer.py
   ```

2. **Test GitHub Actions**
   - Create test PR with Terraform changes
   - Verify workflow execution
   - Check auto-fix functionality

3. **Test Cost Analysis**
   - Ensure Infracost integration works
   - Verify cost reporting accuracy

### Test Scenarios

- **Error Detection**: Various Terraform error types
- **Auto-Fix Generation**: AI-generated fixes
- **Cost Analysis**: Different infrastructure scenarios
- **Workflow Integration**: End-to-end GitHub Actions

## 📚 Development Areas

### High Priority

- **Enhanced Error Detection**: Support for more error types
- **Improved AI Prompts**: Better fix generation accuracy
- **Multi-Cloud Support**: Beyond AWS (Azure, GCP)
- **Performance Optimization**: Faster analysis and processing

### Medium Priority

- **Advanced Cost Analysis**: Trend analysis and recommendations
- **Custom Rules**: User-defined error patterns
- **Integration Tests**: Automated testing framework
- **Documentation**: Video tutorials and guides

### Low Priority

- **UI Dashboard**: Web interface for analysis results
- **Slack/Teams Integration**: Notification systems
- **Advanced Reporting**: Detailed analytics and metrics

## 🔧 Project Architecture

### Key Components

1. **terraform-analyzer.py**: Core AI analysis engine
2. **GitHub Actions**: Workflow automation
3. **Terraform Modules**: Infrastructure components
4. **Cost Analysis**: Infracost integration

### File Structure

```
terraform-analyzer/
├── .github/workflows/     # GitHub Actions workflows
├── terraform/            # Terraform configurations
├── terraform-analyzer.py # Main analysis script
├── action.yml           # Composite action definition
└── docs/               # Documentation
```

## 📖 Resources

### Documentation

- [Terraform Documentation](https://www.terraform.io/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Infracost Documentation](https://www.infracost.io/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Learning Resources

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Python HCL2 Library](https://github.com/amplify-education/python-hcl2)

## 🤝 Community

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

### Getting Help

1. **Check Documentation**: README and guides
2. **Search Issues**: Existing questions and solutions
3. **Create Discussion**: For general questions
4. **Create Issue**: For specific bugs or features

## 📄 License

By contributing to Terraform Analyzer, you agree that your contributions will be licensed under the GNU General Public License v3.0.

## 🙏 Recognition

Contributors are recognized in:
- **README.md**: Contributors section
- **Release Notes**: Feature acknowledgments
- **GitHub**: Contributor graphs and statistics

---

**Thank you for contributing to Terraform Analyzer!** 🚀

Your contributions help make infrastructure automation more intelligent and accessible for everyone.