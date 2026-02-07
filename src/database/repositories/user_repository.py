"""User repository with user-specific queries.

This module provides the data access layer for user management.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from lattice_lock.database.models.user import (
    APIKey,
    Organization,
    OrganizationMember,
    User,
)
from lattice_lock.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email address.

        Args:
            email: User email (case-insensitive).

        Returns:
            User or None if not found.
        """
        stmt = select(User).where(User.email.ilike(email))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_external_id(
        self,
        provider: str,
        external_id: str,
    ) -> User | None:
        """Find a user by OAuth provider ID.

        Args:
            provider: Auth provider name (e.g., 'google', 'github').
            external_id: Provider's user ID.

        Returns:
            User or None if not found.
        """
        return await self.find_one(auth_provider=provider, external_id=external_id)

    async def find_with_organizations(self, user_id: str) -> User | None:
        """Find a user with their organization memberships eagerly loaded.

        Args:
            user_id: User ID.

        Returns:
            User with organizations loaded.
        """
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.organization_memberships))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_organizations(self, user_id: str) -> Sequence[Organization]:
        """Get all organizations a user belongs to.

        Args:
            user_id: User ID.

        Returns:
            Sequence of organizations.
        """
        stmt = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)

    async def find_by_slug(self, slug: str) -> Organization | None:
        """Find an organization by slug.

        Args:
            slug: Organization URL slug.

        Returns:
            Organization or None.
        """
        return await self.find_one(slug=slug)

    async def get_members(
        self,
        organization_id: str,
        role: str | None = None,
    ) -> Sequence[OrganizationMember]:
        """Get organization members, optionally filtered by role.

        Args:
            organization_id: Organization ID.
            role: Optional role filter.

        Returns:
            Sequence of organization members.
        """
        stmt = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .options(selectinload(OrganizationMember.user))
        )

        if role:
            stmt = stmt.where(OrganizationMember.role == role)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_member(
        self,
        organization_id: str,
        user_id: str,
        role: str = "member",
        invited_by: str | None = None,
    ) -> OrganizationMember:
        """Add a user to an organization.

        Args:
            organization_id: Organization ID.
            user_id: User ID.
            role: Member role (default: 'member').
            invited_by: User ID of the inviter.

        Returns:
            The created membership.
        """
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )
        self.session.add(member)
        await self.session.flush()
        return member

    async def is_member(self, organization_id: str, user_id: str) -> bool:
        """Check if a user is a member of an organization.

        Args:
            organization_id: Organization ID.
            user_id: User ID.

        Returns:
            True if user is a member.
        """
        stmt = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .where(OrganizationMember.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository for API key operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(APIKey, session)

    async def find_by_prefix(self, prefix: str) -> APIKey | None:
        """Find an API key by its prefix.

        Args:
            prefix: First 10 characters of the API key.

        Returns:
            APIKey or None.
        """
        return await self.find_one(key_prefix=prefix)

    async def find_valid_keys_for_user(self, user_id: str) -> Sequence[APIKey]:
        """Find all valid (non-expired, non-revoked) API keys for a user.

        Args:
            user_id: User ID.

        Returns:
            Sequence of valid API keys.
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        stmt = (
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .where(APIKey.revoked_at.is_(None))
            .where((APIKey.expires_at.is_(None)) | (APIKey.expires_at > now))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def revoke(self, key_id: str) -> bool:
        """Revoke an API key.

        Args:
            key_id: API key ID.

        Returns:
            True if revoked, False if not found.
        """
        from datetime import datetime, timezone

        key = await self.get(key_id)
        if key is None:
            return False

        key.revoked_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def update_last_used(self, key_id: str) -> None:
        """Update the last_used_at timestamp.

        Args:
            key_id: API key ID.
        """
        from datetime import datetime, timezone

        key = await self.get(key_id)
        if key:
            key.last_used_at = datetime.now(timezone.utc)
            await self.session.flush()
