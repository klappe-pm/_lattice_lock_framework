# Rollback Criteria for Refactoring Chunks

Each work chunk must define explicit rollback criteria. If ANY criteria is met,
immediately revert the chunk and investigate.

## Template

For each chunk, document:

```
## Chunk N Rollback Criteria

REVERT IF ANY OF THE FOLLOWING OCCUR:

1. [ ] Test suite pass rate drops below 95%
2. [ ] Any CRITICAL-level log messages in production
3. [ ] Token aggregation tests fail
4. [ ] Security configuration tests fail
5. [ ] Performance regression >20% on benchmarks
6. [ ] [Chunk-specific criteria]

ROLLBACK PROCEDURE:

1. git revert <commit-hash>
2. Deploy previous version
3. Notify team in #lattice-alerts
4. Create incident ticket
```

## Chunk-Specific Criteria

### Chunk 0 (Dependencies & Config)
- `pip check` fails
- Any import errors for new modules
- Config validation raises unexpected exceptions

### Chunk 1 (Provider Architecture)
- Provider availability tracking returns false positives
- Credential validation breaks existing integrations
- Any provider health checks time out

### Chunk 2 (Analysis & Scoring)
- Performance benchmark regression >15%
- Task analysis returns incorrect classifications
- Memory usage increases >50%

### Chunk 3 (Orchestrator) ⚠️ BILLING-CRITICAL
- Any `BillingIntegrityError` exceptions in logs
- Token counts in responses don't match expected aggregation
- Cost tracking shows anomalies vs baseline
- **Requires second engineer review**

### Chunk 4 (Auth)
- Any `SecurityConfigurationError` in production
- JWT validation failures spike
- Authentication success rate drops below 99%

### Chunk 5 (Error Handling)
- Background task completion rate drops
- Any tasks orphaned beyond timeout
- Graceful shutdown fails to complete

### Chunk 6 (Testing)
- State leakage detected between tests
- Test isolation validation fails
- CI test runs show inconsistent results

### Chunk 7 (Cleanup)
- Integration tests fail
- Coverage drops below 70%
- Any breaking changes to public API
