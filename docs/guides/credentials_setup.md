---
title: credentials_setup
type: guide
status: stable
categories: [guides, configuration]
sub_categories: [credentials]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [guide-credentials-001]
tags: [guide, credentials, api_keys, setup]
---

# API Keys Setup Guide

All API keys for this project are securely stored in your macOS Keychain and accessible globally from any project on your system.

## Quick Start

### Option 1: Use Individual Keys
```bash
# Get a single API key
OPENAI_KEY=$(get-keychain-credential OPENAI_API_KEY)
```

### Option 2: Load All Keys (Recommended)
```bash
# Load all API keys into your current shell session
eval "$(load-keychain-credentials)"

# Verify they're loaded
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

## Available Keys

| Service | Environment Variable |
|---------|---------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` |
| Google (Gemini) | `GOOGLE_API_KEY` |
| xAI (Grok) | `XAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| GitHub | `GITHUB_TOKEN` |
| AWS Default | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| AWS MCP Profile | `AWS_MCP_ACCESS_KEY_ID`, `AWS_MCP_SECRET_ACCESS_KEY` |

## Usage Examples

### Python
```python
import os
import subprocess

# Load credentials
subprocess.run('eval "$(load-keychain-credentials)"', shell=True)

# Use them
openai_key = os.environ.get('OPENAI_API_KEY')
```

### Bash Script
```bash
#!/bin/bash

# Load all credentials
eval "$(load-keychain-credentials)"

# Use in API calls
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Add to Project Setup
```bash
# In your project's setup.sh or initialization script
eval "$(load-keychain-credentials)"
```

## Troubleshooting

**"command not found: load-keychain-credentials"**
- Ensure `~/.local/bin` is in your PATH
- Run: `export PATH="$HOME/.local/bin:$PATH"`

**"The specified item could not be found in the keychain"**
- Check that the credential exists: `security find-generic-password -s "OPENAI_API_KEY"`
- If missing, it needs to be added to your Keychain (contact system admin)

## Security
- ✅ All credentials are encrypted in macOS Keychain
- ✅ Never committed to version control
- ✅ Accessible only to your user account
- ✅ Works across all projects without duplication

## More Information
See `~/global-credentials-guide.md` for advanced usage and detailed documentation.
