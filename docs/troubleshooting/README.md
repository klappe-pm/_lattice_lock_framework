---
title: readme
type: guide
status: stable
categories: [guides, support]
sub_categories: [troubleshooting]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [guide-troubleshoot-001]
tags: [guide, troubleshooting, errors, help]
---

# Troubleshooting Guide

This guide addresses common issues encountered with the Lattice Lock Framework.

## Contents

- [Basic Issues](#basic-issues) - Installation, configuration, and network problems
- [Advanced Troubleshooting](#advanced-troubleshooting) - Debugging, orchestrator, and performance

---

## Basic Issues

Common problems and quick fixes for getting started.

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

---

## Advanced Troubleshooting

For complex issues in production deployments, use these diagnostic techniques.

### Debugging Validation Errors

### Verbose Logging

Enable verbose logging to see the exact constraints being checked.

```bash
export LATTICE_LOG_LEVEL=DEBUG
lattice validate
```

### Inspecting the AST

If Sheriff is flagging false positives, inspect the Abstract Syntax Tree (AST) of your code to understand how it's being parsed.

```bash
lattice sheriff inspect src/my_file.py
```

### Tracing Cross-Entity Checks

For validation errors involving multiple entities, check the database query logs to ensure the correct data is being fetched.

### Orchestrator Issues

### Request Timeouts

If LLM requests are timing out:

1. **Check Network**: Ensure your server can reach the LLM provider's API.
2. **Increase Timeout**: Adjust the timeout setting in `lattice.yaml`.

```yaml
orchestrator:
  timeout: 60  # seconds
```

3. **Simplify Prompts**: Large prompts take longer to process.

### Unexpected Model Output

If the model returns invalid JSON or hallucinates:

1. **Use Structured Output**: Enforce JSON mode if supported by the provider.
2. **Adjust Temperature**: Lower the temperature for more deterministic outputs.

```yaml
orchestrator:
  temperature: 0.1
```

### Common Configuration Mistakes

### Incorrect Schema Path

**Symptom**: "Schema not found" or validation passes unexpectedly (empty schema).

**Fix**: Verify the `models` path in `lattice.yaml` is relative to the configuration file or an absolute path.

### Circular Dependencies

**Symptom**: Infinite recursion or stack overflow during validation.

**Fix**: Break circular dependencies in your models or use lazy evaluation for references.

### Performance Bottlenecks

### Slow Validation

**Cause**: N+1 query problem in cross-entity validation.

**Fix**: Use batch loading or caching (see [Advanced Validation Guide](advanced_validation.md)).

### High Memory Usage

**Cause**: Loading too many large files into memory for analysis.

**Fix**: Process files in streams or chunks. Increase the worker count but limit memory per worker.
