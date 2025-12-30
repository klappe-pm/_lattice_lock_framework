"""
Generated types for Lattice Lock Framework.

NOTE: This file was generated and manually fixed. If regenerating,
ensure the generator template includes proper imports.
"""

from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    """Order model with proper type annotations."""

    id: UUID
    amount: Decimal
    status: OrderStatus


class Customer(BaseModel):
    """Customer model with proper type annotations."""

    id: UUID
    email: str
    rating: int
