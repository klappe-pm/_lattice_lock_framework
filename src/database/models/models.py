"""Model and provider configuration models.

This module defines models for:
- AI model definitions and capabilities
- Provider credentials (encrypted)
- Organization and user quotas
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from lattice_lock.database.models.base import Base, TimestampMixin, UUIDMixin
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from lattice_lock.database.models.user import Organization, User


class Model(Base, UUIDMixin, TimestampMixin):
    """AI model definition and capabilities."""

    __tablename__ = "models"

    # Identity
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Actual API identifier
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'openai', 'anthropic', etc.
    provider_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'cloud', 'local', 'self_hosted'

    # Versioning
    version: Mapped[str | None] = mapped_column(String(50))
    release_date: Mapped[date | None] = mapped_column(Date)

    # Capabilities
    context_window: Mapped[int] = mapped_column(Integer, nullable=False)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer)
    supports_vision: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_function_calling: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_streaming: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_json_mode: Mapped[bool] = mapped_column(Boolean, default=False)

    # Classification
    category: Mapped[str | None] = mapped_column(String(50))  # 'reasoning', 'coding', 'creative', etc.
    best_for: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    limitations: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    # Cost (per 1K tokens)
    input_cost_per_1k: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    output_cost_per_1k: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # 'active', 'deprecated', 'beta'
    deprecation_date: Mapped[date | None] = mapped_column(Date)

    # Flexible metadata
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    __table_args__ = (
        UniqueConstraint("provider", "api_name", name="uq_model_provider_api"),
        Index("idx_models_provider", "provider"),
        Index("idx_models_category", "category"),
        Index("idx_models_status", "status"),
    )

    @property
    def is_available(self) -> bool:
        """Check if the model is currently available for use."""
        return self.status in ("active", "beta")

    def __repr__(self) -> str:
        return f"<Model {self.provider}/{self.api_name}>"


class ProviderCredential(Base, UUIDMixin, TimestampMixin):
    """Encrypted provider credentials per organization."""

    __tablename__ = "provider_credentials"

    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)

    # Encrypted credentials (use Cloud KMS)
    api_key_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    api_base_url: Mapped[str | None] = mapped_column(Text)

    # AWS Bedrock specific
    aws_region: Mapped[str | None] = mapped_column(String(50))
    aws_access_key_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    aws_secret_key_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)

    # Azure specific
    azure_endpoint: Mapped[str | None] = mapped_column(Text)
    azure_deployment_name: Mapped[str | None] = mapped_column(String(255))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validation_status: Mapped[str | None] = mapped_column(String(20))  # 'valid', 'invalid', 'pending'

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="provider_credentials")

    __table_args__ = (
        UniqueConstraint("organization_id", "provider", name="uq_org_provider"),
        Index("idx_provider_creds_org", "organization_id"),
    )

    def __repr__(self) -> str:
        return f"<ProviderCredential {self.provider}>"


class OrganizationQuota(Base, UUIDMixin, TimestampMixin):
    """Organization-level quotas and limits."""

    __tablename__ = "organization_quotas"

    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Token limits
    monthly_token_limit: Mapped[int | None] = mapped_column(BigInteger)
    daily_token_limit: Mapped[int | None] = mapped_column(BigInteger)

    # Request limits
    requests_per_minute: Mapped[int] = mapped_column(Integer, default=100)
    requests_per_day: Mapped[int | None] = mapped_column(Integer)

    # Cost limits
    monthly_cost_limit: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    daily_cost_limit: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Model access control
    allowed_models: Mapped[list[str] | None] = mapped_column(ARRAY(Text))  # NULL = all models
    blocked_models: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    # Current usage counters (reset periodically)
    current_month_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    current_day_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    current_month_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    period_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<OrganizationQuota org={self.organization_id}>"


class UserQuota(Base, UUIDMixin, TimestampMixin):
    """User-level quota overrides within an organization."""

    __tablename__ = "user_quotas"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Token limits (override org defaults)
    monthly_token_limit: Mapped[int | None] = mapped_column(BigInteger)
    daily_token_limit: Mapped[int | None] = mapped_column(BigInteger)
    requests_per_minute: Mapped[int | None] = mapped_column(Integer)

    # Model access (user-specific)
    allowed_models: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    blocked_models: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    # Relationships
    user: Mapped[User] = relationship(back_populates="quotas")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_org_quota"),
    )

    def __repr__(self) -> str:
        return f"<UserQuota user={self.user_id}>"
