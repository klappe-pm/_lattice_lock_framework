"""Lattice Lock Database Package.

This package provides database connectivity and models for the Lattice Lock framework
using a multi-tier GCP architecture:
- Cloud SQL (PostgreSQL) for transactional data
- Firestore for real-time preferences and sessions
- BigQuery for analytics and audit logs
- Memorystore (Redis) for caching
"""

from lattice_lock.database.connection import (
    get_async_session,
    get_sync_session,
    init_database,
)
from lattice_lock.database.gcp_clients import (
    get_bigquery_client,
    get_firestore_client,
    get_redis_client,
)

__all__ = [
    "get_async_session",
    "get_sync_session",
    "init_database",
    "get_firestore_client",
    "get_bigquery_client",
    "get_redis_client",
]
