"""GCP client management for Firestore, BigQuery, and Redis.

This module provides singleton clients for GCP services used by Lattice Lock.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.cloud import bigquery, firestore
    from redis.asyncio import Redis


# Firestore Client
_firestore_client = None


def get_firestore_client() -> "firestore.AsyncClient":
    """Get the Firestore async client.
    
    Returns:
        firestore.AsyncClient: Async Firestore client instance.
        
    Note:
        Uses GOOGLE_CLOUD_PROJECT environment variable or default credentials.
    """
    global _firestore_client
    
    if _firestore_client is None:
        from google.cloud.firestore import AsyncClient
        
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        database = os.getenv("FIRESTORE_DATABASE", "(default)")
        
        _firestore_client = AsyncClient(project=project, database=database)
    
    return _firestore_client


# BigQuery Client
_bigquery_client = None


def get_bigquery_client() -> "bigquery.Client":
    """Get the BigQuery client.
    
    Returns:
        bigquery.Client: BigQuery client instance.
    """
    global _bigquery_client
    
    if _bigquery_client is None:
        from google.cloud import bigquery
        
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        _bigquery_client = bigquery.Client(project=project)
    
    return _bigquery_client


@lru_cache(maxsize=1)
def get_bigquery_dataset() -> str:
    """Get the BigQuery dataset ID.
    
    Returns:
        str: Dataset ID for Lattice Lock analytics.
    """
    return os.getenv("BIGQUERY_DATASET", "lattice_lock")


# Redis Client
_redis_client: "Redis | None" = None


async def get_redis_client() -> "Redis":
    """Get the Redis async client.
    
    Returns:
        Redis: Async Redis client instance.
        
    Note:
        Uses REDIS_HOST and REDIS_PORT environment variables.
    """
    global _redis_client
    
    if _redis_client is None:
        from redis.asyncio import Redis
        
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        password = os.getenv("REDIS_PASSWORD")
        
        _redis_client = Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
    
    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis connection."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# Health Checks

async def check_firestore_health() -> dict:
    """Check Firestore connectivity.
    
    Returns:
        dict: Health status.
    """
    try:
        client = get_firestore_client()
        # Try to get a non-existent document (fast operation)
        doc = await client.collection("_health").document("check").get()
        return {"status": "healthy", "service": "firestore"}
    except Exception as e:
        return {"status": "unhealthy", "service": "firestore", "error": str(e)}


async def check_redis_health() -> dict:
    """Check Redis connectivity.
    
    Returns:
        dict: Health status.
    """
    try:
        client = await get_redis_client()
        await client.ping()
        return {"status": "healthy", "service": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "service": "redis", "error": str(e)}


def check_bigquery_health() -> dict:
    """Check BigQuery connectivity.
    
    Returns:
        dict: Health status.
    """
    try:
        client = get_bigquery_client()
        # Run a simple query
        query = "SELECT 1"
        job = client.query(query)
        list(job.result())
        return {"status": "healthy", "service": "bigquery"}
    except Exception as e:
        return {"status": "unhealthy", "service": "bigquery", "error": str(e)}
