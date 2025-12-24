# Lattice Lock Data Strategy v1.1

## Executive Summary

The Lattice Lock Framework currently operates primarily with in-memory processes and scattered file-based storage. This strategy defines a unified, durable, cloud-native database architecture using **AWS and GCP managed services** with automatic failover, enabling Lattice Lock to scale as the primary orchestration engine for complex multi-LLM workflows.

### Strategic Vision

Lattice Lock as the "primary organ" of a larger ecosystem where users manage complex local and cloud LLM interactions. This requires:

- **Complete observability** of all LLM interactions
- **Cost transparency** across providers and sessions
- **Session continuity** for complex multi-turn workflows
- **Audit trails** for compliance and debugging
- **Analytics foundation** for optimization
- **Cloud-native resilience** with multi-region failover

---

## Part 1: Current State Analysis

### 1.1 Existing Data Storage Locations

|Component|Current Storage|Durability|Issues|
|---|---|---|---|
|Cost Tracker|SQLite (`~/.lattice/cost.db`)|Persistent|Limited schema, no session linking|
|Admin API|SQLite (async, `lattice.db`)|Persistent|Basic project/error models only|
|Feedback|JSON file|Persistent|No indexing, race conditions possible|
|Rollback/Checkpoints|Compressed files|Persistent|No metadata DB, expensive listing|
|Dashboard Metrics|In-memory|**Volatile**|Lost on restart|
|Tracing/Spans|In-memory + logs|**Volatile**|No queryable history|
|Performance Metrics|In-memory|**Volatile**|Lost on restart|
|Sessions|Generated per-run|**Volatile**|No persistence|
|Authentication|In-memory|**Volatile**|Lost on restart|

### 1.2 Critical Data Gaps Identified

1. **No unified session management** - Sessions are ephemeral strings
2. **No chat/conversation persistence** - Multi-turn context lost
3. **No model performance history** - Can't analyze model effectiveness over time
4. **No authentication persistence** - Users must re-authenticate on restart
5. **No distributed tracing persistence** - Debugging complex workflows impossible
6. **No cloud-native resilience** - Single points of failure everywhere
7. **No analytics foundation** - Can't answer "which model performs best for code tasks?"

---

## Part 2: Cloud Database Options Comparison

### 2.1 AWS Database Options

|Service|Type|Best For|Pros|Cons|Cost Model|Lattice Lock Fit|
|---|---|---|---|---|---|---|
|**Amazon RDS PostgreSQL**|Relational|Primary transactional data, ACID compliance|Managed, Multi-AZ, read replicas, familiar SQL, JSONB support|Fixed provisioning, less elastic|Instance hours + storage + I/O|⭐⭐⭐⭐⭐ Primary choice|
|**Amazon Aurora PostgreSQL**|Relational|High-throughput, auto-scaling|5x faster than RDS, serverless option, 15 read replicas, auto-storage|Higher base cost, AWS lock-in|ACU hours (serverless) or instance|⭐⭐⭐⭐⭐ Production primary|
|**Amazon Aurora Serverless v2**|Relational|Variable/unpredictable workloads|Scales to zero, instant scaling, pay-per-use|Cold start latency, max 128 ACU|ACU-seconds consumed|⭐⭐⭐⭐ Dev/staging environments|
|**Amazon DynamoDB**|NoSQL Key-Value|High-scale writes, session data|Unlimited scale, single-digit ms latency, serverless|No complex queries, denormalization required|Read/Write capacity units|⭐⭐⭐ Session/cache layer|
|**Amazon Timestream**|Time-series|Metrics, performance data, logs|Purpose-built for time-series, automatic tiering, SQL-like|Limited query patterns, newer service|Data ingested + stored + queried|⭐⭐⭐⭐ Metrics & tracing|
|**Amazon DocumentDB**|Document (MongoDB-compatible)|Semi-structured data, flexibility|MongoDB API, managed, scalable|Not fully MongoDB compatible|Instance hours + I/O + storage|⭐⭐⭐ Alternative for flexibility|
|**Amazon Keyspaces**|Wide-column (Cassandra)|Massive write throughput|Serverless Cassandra, global tables|Complex data modeling, eventual consistency|Read/Write request units|⭐⭐ High-scale logging only|
|**Amazon ElastiCache Redis**|In-memory cache|Session cache, real-time leaderboards|Sub-ms latency, pub/sub, data structures|Volatile (unless clustered), memory cost|Node hours|⭐⭐⭐⭐ Caching layer|
|**Amazon Neptune**|Graph|Relationship-heavy queries|SPARQL/Gremlin, managed|Specialized use case, learning curve|Instance hours + I/O + storage|⭐⭐ Future agent relationships|
|**Amazon QLDB**|Ledger|Immutable audit logs|Cryptographic verification, immutable|Append-only, limited query|I/O requests + storage|⭐⭐⭐ Audit trail consideration|

### 2.2 GCP Database Options

|Service|Type|Best For|Pros|Cons|Cost Model|Lattice Lock Fit|
|---|---|---|---|---|---|---|
|**Cloud SQL PostgreSQL**|Relational|Primary transactional data|Managed, HA, read replicas, familiar|Fixed provisioning, regional|Instance hours + storage + network|⭐⭐⭐⭐⭐ Primary choice|
|**AlloyDB for PostgreSQL**|Relational|High-performance analytics + OLTP|4x faster than standard PostgreSQL, columnar engine|Higher cost, newer service|Instance + storage + network|⭐⭐⭐⭐⭐ Production primary|
|**Cloud Spanner**|Distributed relational|Global scale, strong consistency|Unlimited scale, global distribution, SQL|Expensive, complex pricing|Node hours + storage|⭐⭐⭐⭐ Multi-region deployments|
|**Firestore**|Document NoSQL|Real-time sync, mobile/web apps|Serverless, real-time listeners, offline|1MB doc limit, query limitations|Read/Write/Delete ops + storage|⭐⭐⭐ Real-time dashboard data|
|**Cloud Bigtable**|Wide-column|Massive time-series, analytics|Petabyte scale, low latency, HBase API|No secondary indexes, row-key design critical|Node hours + storage|⭐⭐⭐⭐ High-volume metrics|
|**Memorystore Redis**|In-memory cache|Session cache, pub/sub|Managed Redis, sub-ms latency|Memory-bound cost, regional|GB-hours|⭐⭐⭐⭐ Caching layer|
|**MongoDB Atlas on GCP**|Document|Flexible schema, aggregation|Full MongoDB, multi-cloud, Atlas Search|Third-party, additional cost|Cluster tier + storage + transfer|⭐⭐⭐ Cross-cloud flexibility|
|**BigQuery**|Analytics warehouse|Historical analytics, BI|Serverless, petabyte scale, ML integration|Not for OLTP, query cost|Query bytes processed + storage|⭐⭐⭐⭐ Analytics warehouse|
|**Datastore**|Document NoSQL|Simple key-value with indexes|Serverless, auto-scaling, strong consistency option|Legacy (prefer Firestore), limited queries|Entity reads/writes + storage|⭐⭐ Legacy compatibility|
|**Cloud SQL MySQL**|Relational|MySQL workloads|Managed, mature, wide tooling|Less feature-rich than PostgreSQL|Instance hours + storage|⭐⭐⭐ Alternative RDBMS|

### 2.3 Unified Comparison Matrix

|Requirement|AWS Primary|AWS Fallback|GCP Primary|GCP Fallback|Local Dev|
|---|---|---|---|---|---|
|**Transactional Data**|Aurora PostgreSQL|RDS PostgreSQL|AlloyDB|Cloud SQL PostgreSQL|SQLite|
|**Session/Cache**|ElastiCache Redis|DynamoDB|Memorystore Redis|Firestore|In-memory dict|
|**Time-series Metrics**|Timestream|DynamoDB (TTL)|Bigtable|BigQuery (streaming)|SQLite|
|**Audit Logs**|Aurora + QLDB|RDS + S3|AlloyDB + BigQuery|Cloud SQL + GCS|JSON files|
|**Analytics**|Timestream + Athena|RDS read replica|BigQuery|AlloyDB columnar|Pandas/DuckDB|
|**Full-text Search**|OpenSearch|RDS pg_trgm|Elasticsearch (GKE)|AlloyDB|SQLite FTS5|

---

## Part 3: Recommended Architecture

### 3.1 Multi-Cloud Database Topology

```mermaid
flowchart TB
    subgraph APP["APPLICATION LAYER"]
        direction LR
        ORCH[Orchestrator]
        DASH[Dashboard]
        ADMIN[Admin API]
        AGENTS[Agents]
    end

    subgraph DAL["DATABASE ABSTRACTION LAYER"]
        direction LR
        CM[ConnectionManager]
        RF[RepositoryFactory]
        MR[MigrationRunner]
    end

    subgraph CACHE["CACHE LAYER  •  Redis"]
        direction LR
        SESS[Sessions]
        RATE[Rate Limits]
        HOT[Hot Queries]
        RTM[Real-time Metrics]
    end

    subgraph INFRA["INFRASTRUCTURE"]
        direction LR
        
        subgraph AWS["AWS  •  PRIMARY  •  us-east-1"]
            direction TB
            AURORA[(Aurora PostgreSQL<br/>Primary)]
            AURORA_R[(Aurora Read<br/>Replicas x2)]
            ELASTI[(ElastiCache Redis<br/>Cluster Mode)]
            TS[(Timestream<br/>Metrics)]
            
            AURORA --> AURORA_R
        end

        subgraph GCP["GCP  •  FAILOVER  •  us-central1"]
            direction TB
            ALLOY[(AlloyDB PostgreSQL<br/>Standby)]
            ALLOY_R[(AlloyDB Read<br/>Replicas x2)]
            MEMSTORE[(Memorystore Redis<br/>HA)]
            BIGTABLE[(Bigtable<br/>Metrics Mirror)]
            
            ALLOY --> ALLOY_R
        end
    end

    %% Connections
    APP --> DAL
    DAL --> CACHE
    CACHE --> AWS
    CACHE --> GCP

    %% Cross-cloud replication
    AURORA <-.->|Async Replication| ALLOY
    ELASTI <-.->|Active-Active Sync| MEMSTORE
    TS <-.->|Dual Write| BIGTABLE

    %% Styling
    classDef appLayer fill:#4F46E5,stroke:#3730A3,color:#fff
    classDef dalLayer fill:#0891B2,stroke:#0E7490,color:#fff
    classDef cacheLayer fill:#DC2626,stroke:#B91C1C,color:#fff
    classDef awsDb fill:#FF9900,stroke:#CC7A00,color:#000
    classDef gcpDb fill:#4285F4,stroke:#3367D6,color:#fff

    class ORCH,DASH,ADMIN,AGENTS appLayer
    class CM,RF,MR dalLayer
    class SESS,RATE,HOT,RTM cacheLayer
    class AURORA,AURORA_R,ELASTI,TS awsDb
    class ALLOY,ALLOY_R,MEMSTORE,BIGTABLE gcpDb
    
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LATTICE LOCK DATA LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        APPLICATION LAYER                             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │    │
│  │  │ Orchestrator│  │  Dashboard  │  │  Admin API  │  │   Agents   │  │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘  │    │
│  └─────────┼────────────────┼────────────────┼───────────────┼─────────┘    │
│            │                │                │               │              │
│  ┌─────────▼────────────────▼────────────────▼───────────────▼─────────┐    │
│  │                    DATABASE ABSTRACTION LAYER                        │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  ConnectionManager  │  RepositoryFactory  │  MigrationRunner │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────┬────────────────┬────────────────┬───────────────┬─────────┘    │
│            │                │                │               │              │
│  ┌─────────▼────────────────▼────────────────▼───────────────▼─────────┐    │
│  │                      CACHE LAYER (Redis)                             │    │
│  │  Sessions │ Rate Limits │ Hot Queries │ Real-time Metrics            │    │
│  └─────────────────────────────┬───────────────────────────────────────┘    │
│                                │                                            │
├────────────────────────────────┼────────────────────────────────────────────┤
│           PRIMARY              │              FAILOVER                       │
│  ┌─────────────────────────────┼─────────────────────────────────────────┐  │
│  │                             │                                          │  │
│  │  ┌──────────────────┐      │      ┌──────────────────┐                │  │
│  │  │   AWS us-east-1  │      │      │   GCP us-central │                │  │
│  │  │                  │◄─────┼─────►│                  │                │  │
│  │  │ Aurora PostgreSQL│  Async│Repl │ AlloyDB PostgreSQL│                │  │
│  │  │   (Primary)      │      │      │   (Standby)      │                │  │
│  │  └────────┬─────────┘      │      └────────┬─────────┘                │  │
│  │           │                │               │                          │  │
│  │  ┌────────▼─────────┐      │      ┌────────▼─────────┐                │  │
│  │  │ Aurora Read      │      │      │ AlloyDB Read     │                │  │
│  │  │ Replicas (2)     │      │      │ Replicas (2)     │                │  │
│  │  └──────────────────┘      │      └──────────────────┘                │  │
│  │                             │                                          │  │
│  │  ┌──────────────────┐      │      ┌──────────────────┐                │  │
│  │  │ ElastiCache Redis│◄─────┼─────►│ Memorystore Redis│                │  │
│  │  │ (Cluster Mode)   │      │      │ (HA)             │                │  │
│  │  └──────────────────┘      │      └──────────────────┘                │  │
│  │                             │                                          │  │
│  │  ┌──────────────────┐      │      ┌──────────────────┐                │  │
│  │  │ Timestream       │      │      │ Bigtable         │                │  │
│  │  │ (Metrics)        │      │      │ (Metrics Mirror) │                │  │
│  │  └──────────────────┘      │      └──────────────────┘                │  │
│  │                             │                                          │  │
│  └─────────────────────────────┴─────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Database Selection by Workload

|Workload|Primary (AWS)|Failover (GCP)|Sync Strategy|RTO|RPO|
|---|---|---|---|---|---|
|**Users, Auth, Projects**|Aurora PostgreSQL|AlloyDB|Async logical replication|5 min|1 min|
|**Model Requests, Chats**|Aurora PostgreSQL|AlloyDB|Async logical replication|5 min|1 min|
|**Sessions, Cache**|ElastiCache Redis|Memorystore Redis|Active-active sync|30 sec|0|
|**Metrics, Traces**|Timestream|Bigtable|Dual-write|1 min|0|
|**Analytics**|Athena + S3|BigQuery + GCS|ETL pipeline|1 hour|15 min|
|**Audit Logs**|Aurora + S3 archive|AlloyDB + GCS|Write-through|5 min|0|

### 3.3 Environment-Specific Configuration

```python
# src/lattice_lock/database/config.py
from enum import Enum
from pydantic import BaseSettings, PostgresDsn, RedisDsn

class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseConfig(BaseSettings):
    """Multi-cloud database configuration."""
    
    environment: Environment = Environment.LOCAL
    
    # Primary Database (PostgreSQL-compatible)
    primary_db_url: PostgresDsn | str = "sqlite+aiosqlite:///./.lattice-lock/lattice.db"
    primary_db_pool_size: int = 20
    primary_db_max_overflow: int = 10
    
    # Failover Database
    failover_db_url: PostgresDsn | None = None
    failover_enabled: bool = False
    
    # Read Replicas
    read_replica_urls: list[PostgresDsn] = []
    read_replica_strategy: str = "round_robin"  # round_robin, random, latency
    
    # Cache Layer (Redis)
    redis_url: RedisDsn | str = "redis://localhost:6379/0"
    redis_failover_url: RedisDsn | None = None
    redis_cluster_mode: bool = False
    
    # Time-series (Timestream/Bigtable)
    timeseries_backend: str = "local"  # local, timestream, bigtable
    timestream_database: str = "lattice_lock"
    timestream_table: str = "metrics"
    bigtable_project: str | None = None
    bigtable_instance: str | None = None
    
    # Feature Flags
    enable_query_logging: bool = False
    enable_slow_query_log: bool = True
    slow_query_threshold_ms: int = 1000
    
    class Config:
        env_prefix = "LATTICE_DB_"
        env_file = ".env"

# Environment presets
ENVIRONMENT_CONFIGS = {
    Environment.LOCAL: {
        "primary_db_url": "sqlite+aiosqlite:///./.lattice-lock/lattice.db",
        "redis_url": "redis://localhost:6379/0",
        "timeseries_backend": "local",
    },
    Environment.DEV: {
        "primary_db_url": "postgresql+asyncpg://user:pass@dev-aurora.cluster-xxx.us-east-1.rds.amazonaws.com:5432/lattice_dev",
        "redis_url": "redis://dev-redis.xxx.cache.amazonaws.com:6379/0",
        "timeseries_backend": "timestream",
        "failover_enabled": False,
    },
    Environment.STAGING: {
        "primary_db_url": "postgresql+asyncpg://user:pass@staging-aurora.cluster-xxx.us-east-1.rds.amazonaws.com:5432/lattice_staging",
        "failover_db_url": "postgresql+asyncpg://user:pass@staging-alloydb.xxx.us-central1.alloydb.goog:5432/lattice_staging",
        "redis_url": "redis://staging-redis.xxx.cache.amazonaws.com:6379/0",
        "redis_failover_url": "redis://staging-redis.xxx.memorystore.goog:6379/0",
        "timeseries_backend": "timestream",
        "failover_enabled": True,
    },
    Environment.PRODUCTION: {
        "primary_db_url": "postgresql+asyncpg://user:pass@prod-aurora.cluster-xxx.us-east-1.rds.amazonaws.com:5432/lattice_prod",
        "failover_db_url": "postgresql+asyncpg://user:pass@prod-alloydb.xxx.us-central1.alloydb.goog:5432/lattice_prod",
        "read_replica_urls": [
            "postgresql+asyncpg://user:pass@prod-aurora-r1.xxx.us-east-1.rds.amazonaws.com:5432/lattice_prod",
            "postgresql+asyncpg://user:pass@prod-aurora-r2.xxx.us-east-1.rds.amazonaws.com:5432/lattice_prod",
        ],
        "redis_url": "rediss://prod-redis.xxx.cache.amazonaws.com:6379/0",
        "redis_failover_url": "rediss://prod-redis.xxx.memorystore.goog:6379/0",
        "redis_cluster_mode": True,
        "timeseries_backend": "timestream",
        "failover_enabled": True,
        "enable_slow_query_log": True,
    },
}
```

---

## Part 4: CI/CD Integration

### 4.1 CI/CD Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CI/CD DATABASE PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Commit    │───►│   Build &   │───►│  Database   │───►│   Deploy    │  │
│  │   Push      │    │   Test      │    │  Migrate    │    │   App       │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                            │                  │                  │          │
│                     ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐  │
│                     │   Unit &    │    │  Migration  │    │  Smoke &    │  │
│                     │Integration  │    │ Validation  │    │  Health     │  │
│                     │   Tests     │    │             │    │  Checks     │  │
│                     └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 GitHub Actions Workflow

```yaml
# .github/workflows/database-ci.yml
name: Database CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/lattice_lock/database/**'
      - 'alembic/**'
      - 'tests/database/**'
  pull_request:
    branches: [main]
    paths:
      - 'src/lattice_lock/database/**'
      - 'alembic/**'

env:
  PYTHON_VERSION: '3.12'

jobs:
  # ============================================
  # Stage 1: Validate Migrations
  # ============================================
  validate-migrations:
    name: Validate Database Migrations
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: lattice_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev,database]"
          pip install alembic asyncpg psycopg2-binary
      
      - name: Validate migration files
        run: |
          python scripts/validate_migrations.py
      
      - name: Check migration chain integrity
        run: |
          alembic check
      
      - name: Run migrations (fresh)
        env:
          LATTICE_DB_PRIMARY_DB_URL: postgresql+asyncpg://test:test@localhost:5432/lattice_test
        run: |
          alembic upgrade head
      
      - name: Verify schema matches models
        env:
          LATTICE_DB_PRIMARY_DB_URL: postgresql+asyncpg://test:test@localhost:5432/lattice_test
        run: |
          python scripts/verify_schema.py
      
      - name: Test migration rollback
        env:
          LATTICE_DB_PRIMARY_DB_URL: postgresql+asyncpg://test:test@localhost:5432/lattice_test
        run: |
          alembic downgrade -1
          alembic upgrade head

  # ============================================
  # Stage 2: Database Unit Tests
  # ============================================
  database-tests:
    name: Database Tests
    runs-on: ubuntu-latest
    needs: validate-migrations
    
    strategy:
      matrix:
        database: [postgresql, sqlite]
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: lattice_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -e ".[dev,database]"
      
      - name: Set database URL
        run: |
          if [ "${{ matrix.database }}" = "postgresql" ]; then
            echo "LATTICE_DB_PRIMARY_DB_URL=postgresql+asyncpg://test:test@localhost:5432/lattice_test" >> $GITHUB_ENV
          else
            echo "LATTICE_DB_PRIMARY_DB_URL=sqlite+aiosqlite:///./test_lattice.db" >> $GITHUB_ENV
          fi
      
      - name: Run database tests
        run: |
          pytest tests/database/ -v --cov=src/lattice_lock/database --cov-report=xml
      
      - name: Run repository tests
        run: |
          pytest tests/repositories/ -v --cov-append --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          flags: database-${{ matrix.database }}

  # ============================================
  # Stage 3: Integration Tests
  # ============================================
  integration-tests:
    name: Database Integration Tests
    runs-on: ubuntu-latest
    needs: database-tests
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: lattice_test
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: pip install -e ".[dev,database]"
      
      - name: Run integration tests
        env:
          LATTICE_DB_PRIMARY_DB_URL: postgresql+asyncpg://test:test@localhost:5432/lattice_test
          LATTICE_DB_REDIS_URL: redis://localhost:6379/0
        run: |
          pytest tests/integration/database/ -v --tb=short
      
      - name: Test failover scenarios
        env:
          LATTICE_DB_PRIMARY_DB_URL: postgresql+asyncpg://test:test@localhost:5432/lattice_test
          LATTICE_DB_FAILOVER_ENABLED: "true"
        run: |
          pytest tests/integration/failover/ -v

  # ============================================
  # Stage 4: Performance Tests
  # ============================================
  performance-tests:
    name: Database Performance Tests
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.ref == 'refs/heads/main'
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: lattice_test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: pip install -e ".[dev,database,benchmark]"
      
      - name: Run performance benchmarks
        env:
          LATTICE_DB_PRIMARY_DB_URL: postgresql+asyncpg://test:test@localhost:5432/lattice_test
        run: |
          python scripts/benchmark_database.py --output benchmark_results.json
      
      - name: Check performance regression
        run: |
          python scripts/check_performance_regression.py benchmark_results.json
      
      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark_results.json

  # ============================================
  # Stage 5: Deploy Migrations (Staging)
  # ============================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [integration-tests]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: pip install -e ".[database]" alembic
      
      - name: Get database credentials from Secrets Manager
        run: |
          DB_SECRET=$(aws secretsmanager get-secret-value --secret-id lattice-lock/staging/database --query SecretString --output text)
          echo "LATTICE_DB_PRIMARY_DB_URL=$(echo $DB_SECRET | jq -r .url)" >> $GITHUB_ENV
      
      - name: Create migration backup
        run: |
          python scripts/backup_before_migration.py --environment staging
      
      - name: Run database migrations
        run: |
          alembic upgrade head
      
      - name: Verify migration success
        run: |
          python scripts/verify_migration.py --environment staging
      
      - name: Run smoke tests
        run: |
          pytest tests/smoke/database/ -v

  # ============================================
  # Stage 6: Deploy Migrations (Production)
  # ============================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [integration-tests, performance-tests]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Configure GCP credentials
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: pip install -e ".[database]" alembic
      
      - name: Get AWS database credentials
        run: |
          DB_SECRET=$(aws secretsmanager get-secret-value --secret-id lattice-lock/production/database --query SecretString --output text)
          echo "LATTICE_DB_PRIMARY_DB_URL=$(echo $DB_SECRET | jq -r .primary_url)" >> $GITHUB_ENV
          echo "LATTICE_DB_FAILOVER_DB_URL=$(echo $DB_SECRET | jq -r .failover_url)" >> $GITHUB_ENV
      
      - name: Create production backup
        run: |
          python scripts/backup_before_migration.py --environment production --upload-to-s3
      
      - name: Enable maintenance mode
        run: |
          python scripts/maintenance_mode.py --enable --environment production
      
      - name: Run AWS Aurora migrations
        run: |
          alembic upgrade head
      
      - name: Sync to GCP AlloyDB
        run: |
          python scripts/sync_to_failover.py --environment production
      
      - name: Verify both databases
        run: |
          python scripts/verify_migration.py --environment production --verify-failover
      
      - name: Disable maintenance mode
        run: |
          python scripts/maintenance_mode.py --disable --environment production
      
      - name: Run production smoke tests
        run: |
          pytest tests/smoke/database/ -v --environment production
      
      - name: Notify on success
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Database migrations deployed to production successfully"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Rollback on failure
        if: failure()
        run: |
          python scripts/emergency_rollback.py --environment production
          python scripts/maintenance_mode.py --disable --environment production
```

### 4.3 Terraform Infrastructure

```hcl
# infrastructure/terraform/modules/database/main.tf

# ============================================
# AWS Aurora PostgreSQL
# ============================================
resource "aws_rds_cluster" "aurora_primary" {
  cluster_identifier     = "lattice-lock-${var.environment}"
  engine                 = "aurora-postgresql"
  engine_version         = "16.1"
  database_name          = "lattice_lock"
  master_username        = var.db_username
  master_password        = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.aurora.id]
  
  backup_retention_period = var.environment == "production" ? 35 : 7
  preferred_backup_window = "03:00-04:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"
  
  tags = {
    Environment = var.environment
    Project     = "lattice-lock"
  }
}

resource "aws_rds_cluster_instance" "aurora_instances" {
  count              = var.environment == "production" ? 3 : 1
  identifier         = "lattice-lock-${var.environment}-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora_primary.id
  instance_class     = var.environment == "production" ? "db.r6g.large" : "db.t4g.medium"
  engine             = aws_rds_cluster.aurora_primary.engine
  engine_version     = aws_rds_cluster.aurora_primary.engine_version
  
  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn
}

# ============================================
# AWS ElastiCache Redis
# ============================================
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "lattice-lock-${var.environment}"
  description                = "Lattice Lock Redis cluster"
  node_type                  = var.environment == "production" ? "cache.r6g.large" : "cache.t4g.micro"
  num_cache_clusters         = var.environment == "production" ? 3 : 1
  port                       = 6379
  
  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled           = var.environment == "production"
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token
  
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  
  snapshot_retention_limit   = var.environment == "production" ? 7 : 1
  snapshot_window            = "04:00-05:00"
  
  tags = {
    Environment = var.environment
    Project     = "lattice-lock"
  }
}

# ============================================
# AWS Timestream
# ============================================
resource "aws_timestreamwrite_database" "metrics" {
  database_name = "lattice_lock_${var.environment}"
  
  tags = {
    Environment = var.environment
    Project     = "lattice-lock"
  }
}

resource "aws_timestreamwrite_table" "model_metrics" {
  database_name = aws_timestreamwrite_database.metrics.database_name
  table_name    = "model_metrics"
  
  retention_properties {
    memory_store_retention_period_in_hours  = 24
    magnetic_store_retention_period_in_days = 365
  }
  
  magnetic_store_write_properties {
    enable_magnetic_store_writes = true
  }
}

resource "aws_timestreamwrite_table" "traces" {
  database_name = aws_timestreamwrite_database.metrics.database_name
  table_name    = "traces"
  
  retention_properties {
    memory_store_retention_period_in_hours  = 168  # 7 days
    magnetic_store_retention_period_in_days = 90
  }
}

# ============================================
# GCP AlloyDB (Failover)
# ============================================
resource "google_alloydb_cluster" "failover" {
  count      = var.environment == "production" ? 1 : 0
  cluster_id = "lattice-lock-${var.environment}"
  location   = var.gcp_region
  project    = var.gcp_project
  
  initial_user {
    user     = var.db_username
    password = var.db_password
  }
  
  automated_backup_policy {
    enabled = true
    backup_window = "04:00"
    
    weekly_schedule {
      days_of_week = ["MONDAY", "WEDNESDAY", "FRIDAY"]
    }
    
    quantity_based_retention {
      count = 14
    }
  }
}

resource "google_alloydb_instance" "primary" {
  count         = var.environment == "production" ? 1 : 0
  cluster       = google_alloydb_cluster.failover[0].name
  instance_id   = "lattice-lock-primary"
  instance_type = "PRIMARY"
  
  machine_config {
    cpu_count = 4
  }
}

resource "google_alloydb_instance" "read_pool" {
  count         = var.environment == "production" ? 2 : 0
  cluster       = google_alloydb_cluster.failover[0].name
  instance_id   = "lattice-lock-read-${count.index}"
  instance_type = "READ_POOL"
  
  read_pool_config {
    node_count = 2
  }
  
  machine_config {
    cpu_count = 2
  }
}

# ============================================
# GCP Memorystore Redis (Failover)
# ============================================
resource "google_redis_instance" "failover" {
  count          = var.environment == "production" ? 1 : 0
  name           = "lattice-lock-${var.environment}"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  region         = var.gcp_region
  
  redis_version  = "REDIS_7_0"
  
  auth_enabled   = true
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 4
        minutes = 0
      }
    }
  }
}

# ============================================
# Cross-Cloud Networking (AWS-GCP)
# ============================================
# Note: Requires VPN or Interconnect setup
# This is a simplified example

resource "aws_vpn_gateway" "gcp_interconnect" {
  count  = var.environment == "production" ? 1 : 0
  vpc_id = var.vpc_id
  
  tags = {
    Name = "lattice-lock-gcp-interconnect"
  }
}

# ============================================
# Secrets Management
# ============================================
resource "aws_secretsmanager_secret" "database" {
  name = "lattice-lock/${var.environment}/database"
  
  tags = {
    Environment = var.environment
    Project     = "lattice-lock"
  }
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    primary_url  = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_rds_cluster.aurora_primary.endpoint}:5432/lattice_lock"
    failover_url = var.environment == "production" ? "postgresql+asyncpg://${var.db_username}:${var.db_password}@${google_alloydb_instance.primary[0].ip_address}:5432/lattice_lock" : null
    redis_url    = "rediss://:${var.redis_auth_token}@${aws_elasticache_replication_group.redis.primary_endpoint_address}:6379/0"
  })
}

# ============================================
# Outputs
# ============================================
output "aurora_endpoint" {
  value = aws_rds_cluster.aurora_primary.endpoint
}

output "aurora_reader_endpoint" {
  value = aws_rds_cluster.aurora_primary.reader_endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "timestream_database" {
  value = aws_timestreamwrite_database.metrics.database_name
}

output "alloydb_endpoint" {
  value = var.environment == "production" ? google_alloydb_instance.primary[0].ip_address : null
}
```

### 4.4 Migration Scripts

```python
# scripts/validate_migrations.py
"""Validate Alembic migration files before deployment."""
import sys
from pathlib import Path
from alembic.config import Config
from alembic.script import ScriptDirectory

def validate_migrations():
    """Validate all migration files."""
    errors = []
    
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)
    
    # Check for head conflicts
    heads = script.get_heads()
    if len(heads) > 1:
        errors.append(f"Multiple heads detected: {heads}. Merge required.")
    
    # Validate each migration
    for rev in script.walk_revisions():
        # Check for down_revision
        if rev.down_revision is None and rev.revision != script.get_base():
            errors.append(f"Migration {rev.revision} missing down_revision")
        
        # Check for upgrade/downgrade functions
        module = rev.module
        if not hasattr(module, 'upgrade'):
            errors.append(f"Migration {rev.revision} missing upgrade()")
        if not hasattr(module, 'downgrade'):
            errors.append(f"Migration {rev.revision} missing downgrade()")
        
        # Check naming convention
        if not rev.revision.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            errors.append(f"Migration {rev.revision} should start with timestamp")
    
    if errors:
        print("❌ Migration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ All migrations validated successfully")

if __name__ == "__main__":
    validate_migrations()
```

```python
# scripts/backup_before_migration.py
"""Create database backup before running migrations."""
import argparse
import boto3
import subprocess
from datetime import datetime

def create_backup(environment: str, upload_to_s3: bool = False):
    """Create RDS snapshot before migration."""
    
    rds = boto3.client('rds')
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    snapshot_id = f"lattice-lock-{environment}-pre-migration-{timestamp}"
    
    # Get cluster identifier
    cluster_id = f"lattice-lock-{environment}"
    
    print(f"Creating snapshot: {snapshot_id}")
    
    response = rds.create_db_cluster_snapshot(
        DBClusterSnapshotIdentifier=snapshot_id,
        DBClusterIdentifier=cluster_id,
        Tags=[
            {'Key': 'Environment', 'Value': environment},
            {'Key': 'Purpose', 'Value': 'pre-migration-backup'},
            {'Key': 'CreatedBy', 'Value': 'ci-cd-pipeline'},
        ]
    )
    
    # Wait for snapshot to complete
    print("Waiting for snapshot to complete...")
    waiter = rds.get_waiter('db_cluster_snapshot_available')
    waiter.wait(DBClusterSnapshotIdentifier=snapshot_id)
    
    print(f"✅ Snapshot {snapshot_id} created successfully")
    
    return snapshot_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--environment', required=True)
    parser.add_argument('--upload-to-s3', action='store_true')
    args = parser.parse_args()
    
    create_backup(args.environment, args.upload_to_s3)
```

```python
# scripts/sync_to_failover.py
"""Sync AWS Aurora to GCP AlloyDB using logical replication."""
import argparse
import asyncio
import asyncpg
from google.cloud import alloydb_v1

async def sync_schema(primary_url: str, failover_url: str):
    """Sync schema from primary to failover database."""
    
    # Connect to both databases
    primary = await asyncpg.connect(primary_url)
    failover = await asyncpg.connect(failover_url)
    
    try:
        # Get schema DDL from primary
        schema_ddl = await primary.fetch("""
            SELECT 
                'CREATE TABLE IF NOT EXISTS ' || schemaname || '.' || tablename || 
                ' (' || string_agg(column_def, ', ') || ');' as ddl
            FROM (
                SELECT 
                    schemaname,
                    tablename,
                    column_name || ' ' || data_type || 
                    CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END as column_def
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY ordinal_position
            ) cols
            GROUP BY schemaname, tablename
        """)
        
        # Apply to failover
        for row in schema_ddl:
            await failover.execute(row['ddl'])
        
        print("✅ Schema synced to failover database")
        
    finally:
        await primary.close()
        await failover.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--environment', required=True)
    args = parser.parse_args()
    
    # Get URLs from environment or secrets manager
    import os
    primary_url = os.environ['LATTICE_DB_PRIMARY_DB_URL']
    failover_url = os.environ['LATTICE_DB_FAILOVER_DB_URL']
    
    asyncio.run(sync_schema(primary_url, failover_url))
```

---

## Part 5: Core Data Models

### 5.1 SQLAlchemy Models (PostgreSQL-Compatible)

```python
# src/lattice_lock/database/models/__init__.py
from .base import Base, TimestampMixin, SoftDeleteMixin
from .user import User, APIKey, RevokedToken, AuthEvent
from .session import Session, Chat, ChatTurn
from .model_request import ModelRequest, CostAggregation
from .observability import Trace, Span, AppLog, PerformanceMetric
from .project import Project, ProjectError, ValidationRun
from .feedback import FeedbackItem
from .checkpoint import Checkpoint, CheckpointFile, RollbackEvent
from .agent import AgentExecution, WorkflowDefinition, WorkflowRun

__all__ = [
    "Base", "TimestampMixin", "SoftDeleteMixin",
    "User", "APIKey", "RevokedToken", "AuthEvent",
    "Session", "Chat", "ChatTurn",
    "ModelRequest", "CostAggregation",
    "Trace", "Span", "AppLog", "PerformanceMetric",
    "Project", "ProjectError", "ValidationRun",
    "FeedbackItem",
    "Checkpoint", "CheckpointFile", "RollbackEvent",
    "AgentExecution", "WorkflowDefinition", "WorkflowRun",
]
```

```python
# src/lattice_lock/database/models/base.py
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

```python
# src/lattice_lock/database/models/model_request.py
"""Model request tracking - the core of LLM usage observability."""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Integer, Boolean, Text, Numeric, 
    ForeignKey, Index, Computed, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

class ModelRequest(Base, TimestampMixin):
    """Every LLM API call - the atomic unit of usage tracking."""
    __tablename__ = "model_requests"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Relationships
    session_id: Mapped[UUID | None] = mapped_column(ForeignKey("sessions.id"), nullable=True)
    chat_id: Mapped[UUID | None] = mapped_column(ForeignKey("chats.id"), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Tracing
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parent_span_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    span_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    # Model Information
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    task_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    # Timing
    requested_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Token Usage
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        Computed("input_tokens + output_tokens", persisted=True)
    )
    
    # Cost (using Numeric for precision)
    input_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 8), default=0)
    output_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 8), default=0)
    total_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 8),
        Computed("input_cost_usd + output_cost_usd", persisted=True)
    )
    
    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, error, timeout, fallback
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Function Calling
    function_calls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    function_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Request Parameters
    context_window_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Routing Metadata
    was_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    original_model_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    selection_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    selection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Raw Data (for debugging, nullable)
    raw_request: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Flexible metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Relationships
    session = relationship("Session", back_populates="model_requests")
    chat = relationship("Chat", back_populates="model_requests")
    user = relationship("User", back_populates="model_requests")
    
    __table_args__ = (
        Index("idx_model_requests_session", "session_id", "requested_at"),
        Index("idx_model_requests_chat", "chat_id", "requested_at"),
        Index("idx_model_requests_user", "user_id", "requested_at"),
        Index("idx_model_requests_model", "model_id", "requested_at"),
        Index("idx_model_requests_provider", "provider", "requested_at"),
        Index("idx_model_requests_task", "task_type", "requested_at"),
        Index("idx_model_requests_trace", "trace_id"),
        Index("idx_model_requests_date", func.date("requested_at")),
        Index("idx_model_requests_status", "status", "requested_at"),
    )


class CostAggregation(Base):
    """Pre-aggregated cost data for efficient reporting."""
    __tablename__ = "cost_aggregations"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    aggregation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily, weekly, monthly
    aggregation_date: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Dimensions
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    task_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Metrics
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=0)
    avg_latency_ms: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    p95_latency_ms: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_cost_agg_date", "aggregation_date"),
        Index("idx_cost_agg_user", "user_id", "aggregation_date"),
        Index("idx_cost_agg_unique", 
              "aggregation_type", "aggregation_date", "user_id", 
              "provider", "model_id", "task_type", 
              unique=True),
    )
```

---

## Part 6: Failover Strategy

### 6.1 Connection Manager with Automatic Failover

```python
# src/lattice_lock/database/connection.py
"""Database connection management with automatic failover."""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import NullPool

from .config import DatabaseConfig, get_config

logger = logging.getLogger("lattice_lock.database")


class DatabaseManager:
    """Manages database connections with failover support."""
    
    def __init__(self, config: DatabaseConfig | None = None):
        self.config = config or get_config()
        
        # Primary connection
        self._primary_engine: AsyncEngine | None = None
        self._primary_session_factory: async_sessionmaker | None = None
        
        # Failover connection
        self._failover_engine: AsyncEngine | None = None
        self._failover_session_factory: async_sessionmaker | None = None
        
        # Read replicas
        self._read_engines: list[AsyncEngine] = []
        self._read_index = 0
        
        # Health state
        self._primary_healthy = True
        self._failover_active = False
        self._health_check_task: asyncio.Task | None = None
    
    async def initialize(self):
        """Initialize all database connections."""
        logger.info(f"Initializing database connections for {self.config.environment}")
        
        # Primary engine
        self._primary_engine = create_async_engine(
            str(self.config.primary_db_url),
            pool_size=self.config.primary_db_pool_size,
            max_overflow=self.config.primary_db_max_overflow,
            pool_pre_ping=True,
            echo=self.config.enable_query_logging,
        )
        self._primary_session_factory = async_sessionmaker(
            self._primary_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        # Failover engine (if configured)
        if self.config.failover_enabled and self.config.failover_db_url:
            self._failover_engine = create_async_engine(
                str(self.config.failover_db_url),
                pool_size=self.config.primary_db_pool_size // 2,
                max_overflow=self.config.primary_db_max_overflow // 2,
                pool_pre_ping=True,
            )
            self._failover_session_factory = async_sessionmaker(
                self._failover_engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            logger.info("Failover database configured")
        
        # Read replicas
        for replica_url in self.config.read_replica_urls:
            engine = create_async_engine(
                str(replica_url),
                pool_size=5,
                max_overflow=5,
                pool_pre_ping=True,
            )
            self._read_engines.append(engine)
        
        if self._read_engines:
            logger.info(f"Configured {len(self._read_engines)} read replicas")
        
        # Start health check
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def close(self):
        """Close all database connections."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._primary_engine:
            await self._primary_engine.dispose()
        if self._failover_engine:
            await self._failover_engine.dispose()
        for engine in self._read_engines:
            await engine.dispose()
        
        logger.info("All database connections closed")
    
    async def _health_check_loop(self):
        """Periodic health check for primary database."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._check_primary_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _check_primary_health(self):
        """Check if primary database is healthy."""
        try:
            async with self._primary_engine.connect() as conn:
                await conn.execute("SELECT 1")
            
            if not self._primary_healthy:
                logger.info("Primary database recovered")
                self._primary_healthy = True
                self._failover_active = False
                
        except Exception as e:
            logger.error(f"Primary database health check failed: {e}")
            self._primary_healthy = False
            
            if self.config.failover_enabled and self._failover_engine:
                logger.warning("Activating failover database")
                self._failover_active = True
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic failover."""
        factory = self._get_active_session_factory()
        
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    @asynccontextmanager
    async def read_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a read-only session, preferring read replicas."""
        factory = self._get_read_session_factory()
        
        async with factory() as session:
            yield session
    
    def _get_active_session_factory(self) -> async_sessionmaker:
        """Get the currently active session factory."""
        if self._failover_active and self._failover_session_factory:
            return self._failover_session_factory
        return self._primary_session_factory
    
    def _get_read_session_factory(self) -> async_sessionmaker:
        """Get a session factory for read operations."""
        if not self._read_engines:
            return self._get_active_session_factory()
        
        # Round-robin through read replicas
        engine = self._read_engines[self._read_index % len(self._read_engines)]
        self._read_index += 1
        
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    @property
    def is_failover_active(self) -> bool:
        """Check if failover is currently active."""
        return self._failover_active
    
    @property
    def is_primary_healthy(self) -> bool:
        """Check if primary database is healthy."""
        return self._primary_healthy


# Global instance
_db_manager: DatabaseManager | None = None


async def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    return _db_manager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    manager = await get_db_manager()
    async with manager.session() as session:
        yield session
```

---

## Part 7: Implementation Roadmap

### 7.1 Phase Timeline

|Phase|Duration|Focus|Deliverables|
|---|---|---|---|
|**Phase 1**|Week 1-2|Foundation|Database abstraction layer, Alembic setup, CI/CD pipeline|
|**Phase 2**|Week 3-4|Auth & Sessions|User/APIKey migration, Session persistence, Redis cache|
|**Phase 3**|Week 5-6|Core Tracking|ModelRequest enhancement, Chat persistence, Cost tracking|
|**Phase 4**|Week 7-8|Observability|Traces/Spans persistence, Timestream integration, Logs|
|**Phase 5**|Week 9-10|Failover|GCP AlloyDB setup, Cross-cloud replication, Testing|
|**Phase 6**|Week 11-12|Analytics|Aggregation jobs, BigQuery/Athena integration, Dashboards|

### 7.2 Success Metrics

|Metric|Target|Measurement|
|---|---|---|
|Query latency P95|< 50ms|CloudWatch/Stackdriver|
|Failover RTO|< 5 minutes|Chaos testing|
|Data durability|99.999%|Backup verification|
|CI/CD migration time|< 10 minutes|Pipeline metrics|
|Test coverage|> 80%|Codecov|

---

## Part 8: Cost Estimation

### 8.1 Monthly Cost Breakdown (Production)

|Service|Configuration|Est. Monthly Cost|
|---|---|---|
|**AWS Aurora PostgreSQL**|db.r6g.large, 3 instances, 100GB|$800-1,200|
|**AWS ElastiCache Redis**|cache.r6g.large, 3 nodes|$400-600|
|**AWS Timestream**|10M writes/day, 90-day retention|$200-400|
|**GCP AlloyDB** (failover)|4 vCPU, 2 read pools|$600-900|
|**GCP Memorystore** (failover)|4GB HA|$150-250|
|**Cross-cloud networking**|VPN/Interconnect|$100-200|
|**Backups & Snapshots**|S3/GCS storage|$50-100|
|**Total**||**$2,300-3,650/month**|

### 8.2 Development/Staging Cost

| Service                      | Configuration   | Est. Monthly Cost |
| ---------------------------- | --------------- | ----------------- |
| **AWS Aurora Serverless v2** | 0.5-2 ACU       | $50-150           |
| **AWS ElastiCache**          | cache.t4g.micro | $15-30            |
| **Total (Dev)**              |                 | **$65-180/month** |