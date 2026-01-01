"""Database models package.

Exports all SQLAlchemy models for the Lattice Lock database.
"""

from lattice_lock.database.models.base import Base, TimestampMixin, UUIDMixin
from lattice_lock.database.models.models import (
    Model,
    OrganizationQuota,
    ProviderCredential,
    UserQuota,
)
from lattice_lock.database.models.user import (
    APIKey,
    Organization,
    OrganizationMember,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # User & Identity
    "User",
    "Organization",
    "OrganizationMember",
    "Permission",
    "Role",
    "RolePermission",
    "UserRole",
    "APIKey",
    # Models & Providers
    "Model",
    "ProviderCredential",
    "OrganizationQuota",
    "UserQuota",
]
