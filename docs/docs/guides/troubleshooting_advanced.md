# Advanced Troubleshooting Guide

This guide helps you diagnose and resolve complex issues in Lattice Lock deployments.

## Debugging Validation Errors

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

## Orchestrator Issues

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

## Common Configuration Mistakes

### Incorrect Schema Path

**Symptom**: "Schema not found" or validation passes unexpectedly (empty schema).

**Fix**: Verify the `models` path in `lattice.yaml` is relative to the configuration file or an absolute path.

### Circular Dependencies

**Symptom**: Infinite recursion or stack overflow during validation.

**Fix**: Break circular dependencies in your models or use lazy evaluation for references.

## Performance Bottlenecks

### Slow Validation

**Cause**: N+1 query problem in cross-entity validation.

**Fix**: Use batch loading or caching (see [Advanced Validation Guide](./advanced_validation.md)).

### High Memory Usage

**Cause**: Loading too many large files into memory for analysis.

**Fix**: Process files in streams or chunks. Increase the worker count but limit memory per worker.
