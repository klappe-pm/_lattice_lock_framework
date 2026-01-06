---
title: "Troubleshooting Guide"
type: guide
status: stable
categories: [Guides, Support]
sub_categories: [Troubleshooting]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [guide-troubleshoot-001]
tags: [guide, troubleshooting, errors, help]
author: DevOps Agent
---

# Troubleshooting Guide

This guide addresses common issues encountered during installation and configuration of the Lattice Lock Framework.

## Installation Issues

### `pip install` fails with "No matching distribution found"

**Cause:** You may be using an unsupported Python version.
**Solution:** Ensure you are using Python 3.10 or higher. Check your version with `python3 --version`.

### Permission denied errors

**Cause:** Installing globally without sufficient permissions.
**Solution:** Use a virtual environment (recommended) or add the `--user` flag: `pip install --user lattice-lock`.

## Configuration Problems

### "API Key not found" error

**Cause:** The required environment variable (e.g., `OPENAI_API_KEY`) is not set.
**Solution:**
1.  Check your environment variables: `echo $OPENAI_API_KEY`.
2.  Ensure they are exported in your shell profile (`.bashrc`, `.zshrc`) or defined in a `.env` file.

### `lattice.yaml` validation errors

**Cause:** Incorrect syntax or missing required fields in `lattice.yaml`.
**Solution:**
- Run `lattice-lock validate` to see specific error messages.
- Compare your file with the example in the [Configuration Guide](docs/getting_started/configuration.md).

## Network and Firewall

### Connection timeouts

**Cause:** Corporate firewalls or proxy settings blocking API requests.
**Solution:**
- Configure your proxy settings in your environment variables (`HTTP_PROXY`, `HTTPS_PROXY`).
- Whitelist the API endpoints for your LLM providers (e.g., `api.openai.com`).

## FAQ

**Q: Can I use Lattice Lock offline?**
A: Yes, by configuring [local models](docs/getting_started/configuration.md#local-models-ollama) via Ollama.

**Q: How do I update Lattice Lock?**
A: Run `pip install --upgrade lattice-lock`.

**Q: Where can I get more help?**
A: Open an issue on our [GitHub repository](https://github.com/lattice-lock/lattice-lock-framework/issues).
