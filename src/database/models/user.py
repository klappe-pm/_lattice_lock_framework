"""User and organization models.

This module defines the core identity and access control models:
- Users
- Organizations
- Organization memberships
- Roles and permissions
- API keys
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lattice_lock.database.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from lattice_lock.database.models.models import ProviderCredential, UserQuota


class User(Base, UUIDMixin, TimestampMixin):
    """User account model."""
    
    __tablename__ = "users"
    
    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    
    # OAuth/SSO
    auth_provider: Mapped[Optional[str]] = mapped_column(String(50))  # 'local', 'google', 'github'
    external_id: Mapped[Optional[str]] = mapped_column(String(255))  # Provider's user ID
    
    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # 'active', 'suspended', 'pending'
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Flexible metadata
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    quotas: Mapped[list["UserQuota"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_users_auth_provider", "auth_provider", "external_id"),
        Index("idx_users_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Organization(Base, UUIDMixin, TimestampMixin):
    """Organization/tenant model."""
    
    __tablename__ = "organizations"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Billing
    plan: Mapped[str] = mapped_column(String(50), default="free")  # 'free', 'pro', 'enterprise'
    billing_email: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Configuration
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    roles: Mapped[list["Role"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    provider_credentials: Mapped[list["ProviderCredential"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Organization {self.slug}>"


class OrganizationMember(Base, UUIDMixin):
    """User membership in an organization."""
    
    __tablename__ = "organization_members"
    
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'owner', 'admin', 'member', 'viewer'
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
    )
    invited_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(
        back_populates="organization_memberships",
        foreign_keys=[user_id],
    )
    
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
        Index("idx_org_members_org", "organization_id"),
        Index("idx_org_members_user", "user_id"),
    )


class Permission(Base, UUIDMixin, TimestampMixin):
    """Permission definition."""
    
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))  # 'models', 'admin', 'billing', 'api'
    
    # Relationships
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


class Role(Base, UUIDMixin, TimestampMixin):
    """Role definition (can be system-wide or organization-specific)."""
    
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
    )
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="roles")
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        UniqueConstraint("name", "organization_id", name="uq_role_name_org"),
    )
    
    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class RolePermission(Base):
    """Many-to-many relationship between roles and permissions."""
    
    __tablename__ = "role_permissions"
    
    role_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    # Relationships
    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")


class UserRole(Base):
    """User role assignment within an organization."""
    
    __tablename__ = "user_roles"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
    )
    granted_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="user_roles",
        foreign_keys=[user_id],
    )
    role: Mapped["Role"] = relationship(back_populates="user_roles")
    
    __table_args__ = (
        Index("idx_user_roles_user", "user_id"),
        Index("idx_user_roles_org", "organization_id"),
    )


class APIKey(Base, UUIDMixin, TimestampMixin):
    """API key for programmatic access."""
    
    __tablename__ = "api_keys"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # For identification
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Hashed key
    
    scopes: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=100)
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="api_keys")
    
    __table_args__ = (
        Index("idx_api_keys_prefix", "key_prefix"),
        Index("idx_api_keys_user", "user_id"),
        Index("idx_api_keys_org", "organization_id"),
    )
    
    @property
    def is_valid(self) -> bool:
        """Check if the API key is currently valid."""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and self.expires_at < now:
            return False
        return True
    
    def __repr__(self) -> str:
        return f"<APIKey {self.key_prefix}...>"
