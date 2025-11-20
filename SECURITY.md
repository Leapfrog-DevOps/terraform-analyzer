# Security Policy

## Supported Versions

We actively support the following versions of Terraform Analyzer with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Terraform Analyzer, please report it responsibly.

### How to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security vulnerabilities by:

1. **Email**: Send details to [core-devops@lftechnology.com](mailto:core-devops@lftechnology.com)
2. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature
3. **Encrypted Communication**: Use our PGP key for sensitive information

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Reproduction**: Step-by-step reproduction instructions
- **Environment**: Affected versions and configurations
- **Proof of Concept**: Code or screenshots (if applicable)
- **Suggested Fix**: If you have ideas for remediation

### Response Timeline

- **Initial Response**: Within 24 hours
- **Vulnerability Assessment**: Within 72 hours
- **Fix Development**: 1-2 weeks (depending on severity)
- **Public Disclosure**: After fix is released and users have time to update

## Security Considerations

### API Keys and Secrets

**OpenAI API Keys:**
- Store securely in GitHub Secrets
- Use environment variables, never hardcode
- Rotate keys regularly
- Monitor usage for anomalies

**AWS Credentials:**
- Use OIDC/IAM roles instead of access keys
- Follow principle of least privilege
- Enable CloudTrail logging
- Regular access reviews

**Infracost API Keys:**
- Store in GitHub Secrets
- Monitor usage limits
- Rotate periodically

### Infrastructure Security

**Terraform State:**
- Use remote state with encryption
- Enable state locking with DynamoDB
- Restrict access to state files
- Regular state backups

**AWS Resources:**
- Follow AWS security best practices
- Enable VPC flow logs
- Use security groups restrictively
- Enable AWS Config for compliance

### Code Security

**Dependencies:**
- Regular dependency updates
- Vulnerability scanning with Dependabot
- Pin dependency versions
- Review third-party packages

**AI Integration:**
- Sanitize inputs to OpenAI API
- Validate AI-generated code before applying
- Log AI interactions for audit
- Rate limiting to prevent abuse

### GitHub Actions Security

**Workflow Security:**
- Use pinned action versions
- Minimize permissions (principle of least privilege)
- Secure secrets handling
- Environment protection rules

**Repository Security:**
- Branch protection rules
- Required status checks
- Signed commits (recommended)
- Regular access reviews

## Security Best Practices

### For Users

1. **Secrets Management**
   ```yaml
   # ✅ Good - Use GitHub Secrets
   openai-api-key: ${{ secrets.OPENAI_API_KEY }}
   
   # ❌ Bad - Never hardcode secrets
   openai-api-key: "sk-1234567890abcdef"
   ```

2. **IAM Permissions**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject"
         ],
         "Resource": "arn:aws:s3:::your-bucket/*"
       }
     ]
   }
   ```

3. **Network Security**
   - Use private subnets for resources
   - Implement proper security groups
   - Enable VPC endpoints where applicable

### For Contributors

1. **Code Review**
   - Review all code changes for security implications
   - Check for hardcoded secrets or credentials
   - Validate input sanitization

2. **Testing**
   - Test with minimal permissions
   - Validate error handling
   - Check for information disclosure

3. **Documentation**
   - Document security considerations
   - Provide secure configuration examples
   - Update security guidelines

## Vulnerability Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure practices:

1. **Private Reporting**: Initial report kept confidential
2. **Investigation**: We investigate and develop fixes
3. **Coordination**: Work with reporter on timeline
4. **Public Disclosure**: After fix is available and deployed

### Recognition

We acknowledge security researchers who responsibly report vulnerabilities:

- **Hall of Fame**: Recognition in our security acknowledgments
- **CVE Assignment**: For significant vulnerabilities
- **Coordination**: Work together on public disclosure

## Security Updates

### Notification Channels

Stay informed about security updates:

- **GitHub Security Advisories**: Automatic notifications
- **Release Notes**: Security fixes highlighted
- **Email Notifications**: For critical vulnerabilities

### Update Process

When security updates are released:

1. **Review Release Notes**: Understand the security impact
2. **Test in Non-Production**: Validate fixes in safe environment
3. **Deploy Quickly**: Apply security updates promptly
4. **Monitor**: Watch for any issues after deployment

## Compliance and Standards

### Security Frameworks

We align with industry security standards:

- **OWASP Top 10**: Web application security risks
- **NIST Cybersecurity Framework**: Risk management
- **CIS Controls**: Critical security controls
- **AWS Security Best Practices**: Cloud security guidelines

### Audit and Monitoring

Regular security practices:

- **Dependency Scanning**: Automated vulnerability detection
- **Code Analysis**: Static security analysis
- **Access Reviews**: Regular permission audits
- **Incident Response**: Documented response procedures

## Contact Information

### Security Team

- **Email**: [core-devops@lftechnology.com](mailto:core-devops@lftechnology.com)
- **Response Time**: 24 hours for initial response
- **Escalation**: For urgent issues, mark email as "URGENT SECURITY"

### PGP Key

For encrypted communications:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
[PGP Key would be here in real implementation]
-----END PGP PUBLIC KEY BLOCK-----
```

## Legal

### Safe Harbor

We provide safe harbor for security researchers who:

- Report vulnerabilities responsibly
- Do not access or modify user data
- Do not disrupt our services
- Follow coordinated disclosure practices

### Scope

This security policy covers:

- **Terraform Analyzer Core**: Main application and scripts
- **GitHub Actions**: Workflow and action definitions
- **Documentation**: Security-related guidance
- **Dependencies**: Third-party packages and integrations

---

**Security is a shared responsibility.** Thank you for helping keep Terraform Analyzer and our community safe! 🔒