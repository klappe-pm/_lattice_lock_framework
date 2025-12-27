"""
Data models for the API service.

These models are generated from the lattice.yaml schema
and validated by the Lattice Lock governance system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """Order status workflow states."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    """Payment transaction status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    """Supported payment methods."""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class Currency(Enum):
    """Supported currencies."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"


@dataclass
class User:
    """User account model."""

    id: int
    email: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if "@" not in self.email or "." not in self.email:
            raise ValueError("Invalid email format")
        if len(self.password_hash) != 60:
            raise ValueError("Password hash must be 60 characters (bcrypt)")


@dataclass
class Product:
    """Product catalog model."""

    id: int
    sku: str
    name: str
    description: str
    price_cents: int
    quantity_in_stock: int
    category: str
    is_available: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.price_cents < 0:
            raise ValueError("Price cannot be negative")
        if self.quantity_in_stock < 0:
            raise ValueError("Quantity cannot be negative")
        if len(self.sku) < 3:
            raise ValueError("SKU must be at least 3 characters")


@dataclass
class Order:
    """Customer order model."""

    id: int
    user_id: int
    status: OrderStatus
    total_cents: int
    shipping_address: str
    billing_address: str
    notes: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.total_cents < 0:
            raise ValueError("Total cannot be negative")


@dataclass
class OrderItem:
    """Order line item model."""

    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price_cents: int
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price_cents < 0:
            raise ValueError("Unit price cannot be negative")


@dataclass
class Payment:
    """Payment transaction model."""

    id: int
    order_id: int
    amount_cents: int
    currency: Currency
    status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: str
    created_at: datetime | None = None
    processed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.amount_cents <= 0:
            raise ValueError("Amount must be positive")


__all__ = [
    "User",
    "Product",
    "Order",
    "OrderItem",
    "Payment",
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    "Currency",
]
