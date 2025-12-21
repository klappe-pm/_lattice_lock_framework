# Production Deployment Guide

Deploying Lattice Lock in a production environment requires attention to configuration, security, and monitoring.

## Production Configuration

Use environment variables to override configuration settings for different environments.

### Environment Variables

Lattice Lock respects the `LATTICE_` prefix for configuration overrides.

```bash
export LATTICE_ENV=production
export LATTICE_LOG_LEVEL=INFO
export LATTICE_DB_CONNECTION=postgresql://user:pass@prod-db:5432/lattice
```

### Configuration File Precedence

1. Environment Variables
2. `lattice.local.yaml` (should be gitignored)
3. `lattice.yaml` (checked into version control)
4. Default defaults

## Security Hardening

### API Keys and Secrets

Never commit API keys or secrets to your repository. Use a secrets manager or environment variables.

```yaml
llm:
  provider: openai
  api_key: ${OPENAI_API_KEY}  # Interpolated from env var
```

### Role-Based Access Control (RBAC)

If you are exposing the Lattice Lock API or Dashboard, ensure proper authentication and authorization.

- **Dashboard**: Put behind a reverse proxy (e.g., Nginx) with Basic Auth or OAuth if not using the built-in auth.
- **API**: Use API tokens for service-to-service communication.

### Input Sanitization

While Lattice Lock validates data types, always sanitize inputs to prevent injection attacks, especially when using custom SQL validators.

## Monitoring and Alerting

### Prometheus Metrics

Lattice Lock exposes metrics at `/metrics` if enabled.

- `lattice_validation_requests_total`: Total validation requests.
- `lattice_validation_errors_total`: Total validation failures.
- `lattice_orchestrator_latency_seconds`: Latency of LLM calls.

### Logging

Configure structured logging for easier parsing by log aggregators (e.g., ELK, Splunk).

```yaml
logging:
  format: json
  level: info
```

## Scaling Considerations

### Stateless Validators

The validation engine is stateless. You can scale it horizontally by adding more worker nodes behind a load balancer.

### Caching Layer

Use Redis or Memcached for caching schema lookups and validation results to reduce load on your primary database.

```yaml
cache:
  backend: redis
  url: redis://cache-cluster:6379/0
```

### Worker Queues

For asynchronous tasks like batch validation or heavy LLM orchestration, use a worker queue (e.g., Celery, BullMQ).
