---
title: "Token Storage Design"
type: design
status: draft
categories: [Architecture, Design]
sub_categories: [Security]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [token-storage-001]
tags: [design, security, auth]
author: Security Agent
---

# Production Token Storage Design

## Problem Statement
The current in-memory token storage (revocation list and session tracking) is lost on server restart and doesn't scale for multi-instance deployments.

## Proposed Solution: Redis-backed Storage
Redis is the recommended backend for production token storage due to:
- High performance for lookup operations.
- Native TTL support for token expiration.
- Atomic operations for race condition prevention.
- Easy scaling across multiple application instances.

## Architecture
1. **Interface**: Create a `TokenStorageBackend` abstract base class.
2. **Implementations**:
   - `InMemoryBackend`: Current implementation for dev/test.
   - `RedisBackend`: New implementation for production.
3. **Configuration**: Use an environment variable `LATTICE_LOCK_STORAGE_URL` to specify the backend.

## Implementation Details
- Tokens should be stored with an expiration time matching the JWT expiry.
- Use Redis SETS or HASHES depending on the metadata required.
- Implement a cleanup worker or rely on Redis TTL.
