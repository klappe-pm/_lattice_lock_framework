# Database Plan

## Lattice Lock Framework - Database Design and Implementation Review

This document outlines the database schema assessment, migration strategy, security hardening, and recommended improvements.

## Current State

### Database Technologies

| Database | Type | Purpose | Location |
|----------|------|---------|----------|
| SQLite | Relational | Default local database | `DATABASE_URL=sqlite:///lattice.db` |
| PostgreSQL | Relational | Production (GCP Cloud SQL) | Terraform |
| Firestore | Document | Session storage (GCP) | Terraform |
| BigQuery | Analytics | Request logs, audit events | Terraform |
| Redis | Cache | Response caching | Terraform (Memorystore) |

### SQLAlchemy Models

**Location:** `src/lattice_lock/admin/models.py`

```python
# Enums
class ProjectStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    NOT_RUN = "not_run"

# Models
class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        SQLAlchemyEnum(ProjectStatus), 
        default=ProjectStatus.UNKNOWN
    )
    schema_status: Mapped[ValidationStatus]
    sheriff_status: Mapped[ValidationStatus]
    gauntlet_status: Mapped[ValidationStatus]
    last_validated: Mapped[Optional[datetime]]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    
    errors: Mapped[List["ProjectError"]] = relationship(back_populates="project")

class ProjectError(Base):
    __tablename__ = "project_errors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    error_type: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024))
    line_number: Mapped[Optional[int]] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime]
    
    project: Mapped["Project"] = relationship(back_populates="errors")

class RollbackCheckpoint(Base):
    __tablename__ = "rollback_checkpoints"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    created_at: Mapped[datetime]
    description: Mapped[Optional[str]] = mapped_column(Text)
    state_data: Mapped[str] = mapped_column(Text)  # JSON blob
```

### Connection Management

**Location:** `src/lattice_lock/database/connection.py`

```python
# Current implementation has type errors
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Identified Issues

### Issue 1: Type Errors in Connection Manager (P2)

**Location:** `src/lattice_lock/database/connection.py:54-60`

**Problem:** Async context manager return type incorrect
```
error: Argument 1 to "asynccontextmanager" has incompatible type
```

**Fix:**
```python
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Issue 2: Missing Migration Tool (P3)

**Location:** `src/lattice_lock/database/`

**Problem:** No Alembic or similar migration tool configured

**Impact:** Schema changes require manual database updates

**Fix:** Add Alembic configuration (see Migration Strategy below)

### Issue 3: No Connection Pooling Configuration (P3)

**Location:** `src/lattice_lock/database/connection.py`

**Problem:** Default connection pool settings may not be optimal for production

**Fix:**
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)
```

### Issue 4: No Soft Delete Support (P4)

**Location:** `src/lattice_lock/admin/models.py`

**Problem:** Hard deletes lose audit trail

**Fix:** Add soft delete mixin:
```python
class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

## Schema Improvements

### 1. Add Indexes

```python
class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_status", "status"),
        Index("ix_projects_updated_at", "updated_at"),
        Index("ix_projects_name", "name"),
    )

class ProjectError(Base):
    __tablename__ = "project_errors"
    __table_args__ = (
        Index("ix_project_errors_project_id", "project_id"),
        Index("ix_project_errors_severity", "severity"),
        Index("ix_project_errors_created_at", "created_at"),
    )
```

### 2. Add Audit Fields

```python
class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
```

### 3. Add Version Column for Optimistic Locking

```python
class Project(Base):
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    __mapper_args__ = {
        "version_id_col": version
    }
```

## Migration Strategy

### Setup Alembic

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init migrations

# Configure alembic.ini
sqlalchemy.url = sqlite:///lattice.db
```

### Configure `migrations/env.py`

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from lattice_lock.admin.models import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Create Initial Migration

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## Security Hardening

### 1. Parameterized Queries

**Current:** Using SQLAlchemy ORM (safe by default)

**Verification:** Ensure no raw SQL with string interpolation:
```python
# BAD - SQL injection risk
session.execute(f"SELECT * FROM projects WHERE name = '{name}'")

# GOOD - Parameterized
session.execute(text("SELECT * FROM projects WHERE name = :name"), {"name": name})

# BEST - ORM
session.query(Project).filter(Project.name == name).all()
```

### 2. Connection String Security

```python
# Use environment variables
import os
from urllib.parse import quote_plus

DATABASE_URL = os.getenv("DATABASE_URL")

# For passwords with special characters
password = quote_plus(os.getenv("DB_PASSWORD", ""))
DATABASE_URL = f"postgresql+asyncpg://user:{password}@host/db"
```

### 3. Encryption at Rest

**GCP Cloud SQL:**
```hcl
# infrastructure/terraform/gcp/main.tf
resource "google_sql_database_instance" "main" {
  settings {
    disk_encryption_configuration {
      kms_key_name = google_kms_crypto_key.database.id
    }
  }
}
```

### 4. Row-Level Security (PostgreSQL)

```sql
-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY project_isolation ON projects
    USING (organization_id = current_setting('app.current_org')::uuid);
```

### 5. Audit Logging

```python
from sqlalchemy import event

@event.listens_for(Project, "after_insert")
def log_project_insert(mapper, connection, target):
    audit_log.info(f"Project created: {target.id} by {target.created_by}")

@event.listens_for(Project, "after_update")
def log_project_update(mapper, connection, target):
    audit_log.info(f"Project updated: {target.id} by {target.updated_by}")

@event.listens_for(Project, "after_delete")
def log_project_delete(mapper, connection, target):
    audit_log.info(f"Project deleted: {target.id}")
```

## GCP Infrastructure Review

### Cloud SQL Configuration

**Location:** `infrastructure/terraform/gcp/main.tf:71-128`

**Current Settings:**
- PostgreSQL 15
- Private IP only (good)
- Point-in-time recovery enabled for production
- 30-day backup retention for production
- Query insights enabled
- Maintenance window: Sunday 4 AM

**Recommendations:**
1. Add read replicas for production
2. Enable deletion protection
3. Add connection limits per user

### Firestore Configuration

**Location:** `infrastructure/terraform/gcp/main.tf:164-173`

**Current Settings:**
- Native mode
- Optimistic concurrency
- Default database

**Recommendations:**
1. Add TTL policies for session data
2. Add composite indexes for common queries
3. Enable export to BigQuery for analytics

### BigQuery Tables

**Location:** `infrastructure/terraform/gcp/main.tf:214-327`

**Tables:**
- `request_logs` - LLM request tracking
- `audit_events` - Security audit trail
- `daily_usage` - Aggregated usage metrics

**Recommendations:**
1. Add partitioning expiration for cost control
2. Add authorized views for data access
3. Add scheduled queries for aggregation

## Implementation Roadmap

### Phase 1: Fix Critical Issues (1 day)
1. Fix type errors in connection manager
2. Add connection pooling configuration
3. Add indexes to existing tables

### Phase 2: Add Migrations (2 days)
4. Install and configure Alembic
5. Create initial migration
6. Document migration workflow

### Phase 3: Security Hardening (1 week)
7. Audit all queries for SQL injection
8. Add audit logging
9. Configure encryption at rest
10. Add row-level security (if multi-tenant)

### Phase 4: Schema Improvements (1 week)
11. Add soft delete support
12. Add audit fields
13. Add optimistic locking
14. Add read replicas (production)

## Verification Checklist

- [ ] Connection manager type errors fixed
- [ ] Alembic configured and initial migration created
- [ ] All tables have appropriate indexes
- [ ] No raw SQL with string interpolation
- [ ] Connection pooling configured for production
- [ ] Audit logging enabled
- [ ] Encryption at rest enabled (production)
- [ ] Backup and recovery tested
