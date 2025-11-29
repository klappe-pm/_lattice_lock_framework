# Credentials Directory

⚠️ **SECURITY NOTICE**: This directory is excluded from Git via `.gitignore`

## Purpose

This directory stores sensitive credentials, API keys, and secrets that should **NEVER** be committed to version control.

## File Structure

```
credentials/
├── README.md              # This file (safe to commit)
├── .env                   # Environment variables (DO NOT COMMIT)
├── api_keys.json          # API keys in JSON format (DO NOT COMMIT)
├── aws_credentials.txt    # AWS credentials (DO NOT COMMIT)
└── service_accounts/      # Service account keys (DO NOT COMMIT)
```

## Supported Credentials

### 1. Environment Variables (.env)

Create a `.env` file in this directory:

```bash
# AI Model Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...

# Cloud Providers
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# Optional Providers
AZURE_OPENAI_KEY=...
BEDROCK_ACCESS_KEY=...
DIAL_API_KEY=...

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Other Services
GITHUB_TOKEN=ghp_...
LINEAR_API_KEY=lin_api_...
```

### 2. API Keys JSON (api_keys.json)

```json
{
  "openai": {
    "api_key": "sk-...",
    "organization": "org-..."
  },
  "anthropic": {
    "api_key": "sk-ant-..."
  },
  "google": {
    "api_key": "AIza..."
  },
  "xai": {
    "api_key": "xai-..."
  }
}
```

### 3. AWS Credentials (aws_credentials.txt)

```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
region = us-east-1

[production]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
region = us-west-2
```

## Loading Credentials

### Method 1: Source Environment File

```bash
source credentials/.env
```

### Method 2: Use in Scripts

```python
from dotenv import load_dotenv
import os

# Load from credentials directory
load_dotenv('credentials/.env')

openai_key = os.getenv('OPENAI_API_KEY')
```

### Method 3: Shell Script

```bash
#!/bin/bash
# scripts/setup_api_keys.sh

if [ -f credentials/.env ]; then
    export $(cat credentials/.env | grep -v '^#' | xargs)
    echo "✓ API keys loaded from credentials/.env"
else
    echo "✗ credentials/.env not found"
    exit 1
fi
```

## Security Best Practices

1. **Never commit credentials to Git**
   - The `.gitignore` file excludes the entire `credentials/` directory
   - Only `README.md` is allowed to be committed

2. **Use environment-specific files**
   - `.env.development`
   - `.env.staging`
   - `.env.production`

3. **Rotate keys regularly**
   - Set calendar reminders to rotate API keys every 90 days
   - Immediately rotate if credentials are compromised

4. **Use minimal permissions**
   - Only grant the minimum required API permissions
   - Use separate keys for development and production

5. **Encrypt at rest**
   - Consider using macOS Keychain or a password manager
   - Use `gpg` to encrypt sensitive files: `gpg -c api_keys.json`

6. **Backup securely**
   - Store backup copies in encrypted password managers
   - Never email or message credentials in plain text

## Checking for Exposed Secrets

Before committing, always run:

```bash
# Check for accidentally staged credentials
git status

# Verify .gitignore is working
git check-ignore -v credentials/*

# Scan for secrets in git history
git log --all --full-history -- "*credential*" "*secret*" "*api*key*"
```

## Emergency: Credential Leak

If credentials are accidentally committed:

1. **Immediately rotate all exposed credentials**
2. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch PATH/TO/FILE" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push:** `git push origin --force --all`
4. **Notify your team**

## Repository Integration

The orchestrator scripts automatically look for credentials in:
1. `credentials/.env` (first priority)
2. Environment variables (second priority)
3. `~/.env` (fallback)

See `scripts/model_orchestrator.py` for implementation details.
