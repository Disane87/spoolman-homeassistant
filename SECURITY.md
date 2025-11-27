# 🔒 Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

We recommend always using the latest version of the integration to ensure you have all security patches.

## Reporting a Vulnerability

We take the security of our integration seriously. If you've discovered a security vulnerability, we appreciate your help in disclosing it to us responsibly.

### 🚨 Please DO NOT:
- Open a public GitHub issue for security vulnerabilities
- Discuss the vulnerability in public forums, chat rooms, or social media

### ✅ Please DO:
**Report security vulnerabilities privately using one of these methods:**

1. **GitHub Security Advisories (Preferred)**
   - Go to https://github.com/Disane87/spoolman-homeassistant/security/advisories
   - Click "Report a vulnerability"
   - Fill out the form with as much detail as possible

2. **Email**
   - Send an email to the maintainers via GitHub
   - Include "SECURITY" in the subject line
   - Provide detailed information about the vulnerability

### 📝 What to Include in Your Report

To help us understand and fix the issue quickly, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker do with this vulnerability?
- **Reproduction Steps**: Step-by-step instructions to reproduce the issue
- **Affected Versions**: Which versions are affected?
- **Suggested Fix**: If you have ideas on how to fix it (optional)
- **Your Environment**:
  - Home Assistant version
  - Integration version
  - Python version
  - Any relevant configuration details

### 🔄 What Happens Next?

1. **Acknowledgment**: We'll acknowledge receipt of your report within 48 hours
2. **Assessment**: We'll investigate and assess the severity of the issue
3. **Fix Development**: We'll work on a fix and may ask for your input
4. **Disclosure**: Once fixed, we'll:
   - Release a patched version
   - Publish a security advisory
   - Credit you for the discovery (unless you prefer to remain anonymous)

### ⏱️ Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Release**: Depends on severity
  - Critical: As soon as possible (usually within days)
  - High: Within 2 weeks
  - Medium/Low: In the next scheduled release

### 🏆 Recognition

We're grateful for security researchers who help keep our users safe! Contributors who responsibly disclose security issues will be:
- Credited in the security advisory (if desired)
- Mentioned in the release notes
- Added to our security hall of fame (coming soon!)

## Security Best Practices for Users

To keep your Home Assistant installation secure when using this integration:

1. **Keep Updated**: Always use the latest version of the integration
2. **Network Security**:
   - Use HTTPS for Home Assistant
   - Don't expose Home Assistant directly to the internet without proper security
   - Consider using a VPN or Nabu Casa for remote access
3. **Spoolman Security**:
   - Keep your Spoolman instance updated
   - Use authentication if exposing Spoolman to network
   - Consider running Spoolman on a separate network segment
4. **Credentials**:
   - Use strong passwords
   - Don't share your Home Assistant credentials
   - Regularly review integration permissions

## Known Security Considerations

- This integration communicates with a Spoolman server via HTTP/HTTPS
- Ensure your Spoolman server is properly secured
- API credentials (if used) are stored in Home Assistant's configuration
- No user data is transmitted to external services by this integration

## Questions?

If you have questions about security but don't have a vulnerability to report, feel free to:
- Open a regular GitHub issue
- Start a discussion in the GitHub Discussions tab
- Reach out to the maintainers

Thank you for helping keep our community safe! 🙏
