"""
Tests for API service data models.

Validates that models enforce Lattice Lock schema constraints.
"""

import pytest

from src.models import (
    Currency,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Product,
    User,
)


class TestUserModel:
    """Tests for User model constraints."""

    def test_valid_user(self) -> None:
        """Test creating a valid user."""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$" + "a" * 53,
            first_name="John",
            last_name="Doe",
        )
        assert user.email == "test@example.com"

    def test_invalid_email_missing_at(self) -> None:
        """Test that email must contain @."""
        with pytest.raises(ValueError, match="Invalid email"):
            User(
                id=1,
                email="testexample.com",
                password_hash="$2b$12$" + "a" * 53,
                first_name="John",
                last_name="Doe",
            )

    def test_invalid_email_missing_dot(self) -> None:
        """Test that email must contain a dot."""
        with pytest.raises(ValueError, match="Invalid email"):
            User(
                id=1,
                email="test@examplecom",
                password_hash="$2b$12$" + "a" * 53,
                first_name="John",
                last_name="Doe",
            )

    def test_invalid_password_hash_length(self) -> None:
        """Test that password hash must be 60 characters."""
        with pytest.raises(ValueError, match="60 characters"):
            User(
                id=1,
                email="test@example.com",
                password_hash="short",
                first_name="John",
                last_name="Doe",
            )


class TestProductModel:
    """Tests for Product model constraints."""

    def test_valid_product(self) -> None:
        """Test creating a valid product."""
        product = Product(
            id=1,
            sku="PROD-001",
            name="Test Product",
            description="A test product",
            price_cents=1999,
            quantity_in_stock=100,
            category="Electronics",
        )
        assert product.price_cents == 1999

    def test_negative_price_rejected(self) -> None:
        """Test that negative prices are rejected."""
        with pytest.raises(ValueError, match="negative"):
            Product(
                id=1,
                sku="PROD-001",
                name="Test Product",
                description="A test product",
                price_cents=-100,
                quantity_in_stock=100,
                category="Electronics",
            )

    def test_negative_quantity_rejected(self) -> None:
        """Test that negative quantities are rejected."""
        with pytest.raises(ValueError, match="negative"):
            Product(
                id=1,
                sku="PROD-001",
                name="Test Product",
                description="A test product",
                price_cents=1999,
                quantity_in_stock=-10,
                category="Electronics",
            )

    def test_short_sku_rejected(self) -> None:
        """Test that SKU must be at least 3 characters."""
        with pytest.raises(ValueError, match="3 characters"):
            Product(
                id=1,
                sku="AB",
                name="Test Product",
                description="A test product",
                price_cents=1999,
                quantity_in_stock=100,
                category="Electronics",
            )


class TestOrderModel:
    """Tests for Order model constraints."""

    def test_valid_order(self) -> None:
        """Test creating a valid order."""
        order = Order(
            id=1,
            user_id=1,
            status=OrderStatus.PENDING,
            total_cents=5000,
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )
        assert order.status == OrderStatus.PENDING

    def test_negative_total_rejected(self) -> None:
        """Test that negative totals are rejected."""
        with pytest.raises(ValueError, match="negative"):
            Order(
                id=1,
                user_id=1,
                status=OrderStatus.PENDING,
                total_cents=-100,
                shipping_address="123 Main St",
                billing_address="123 Main St",
            )


class TestOrderItemModel:
    """Tests for OrderItem model constraints."""

    def test_valid_order_item(self) -> None:
        """Test creating a valid order item."""
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=1,
            quantity=2,
            unit_price_cents=1999,
        )
        assert item.quantity == 2

    def test_zero_quantity_rejected(self) -> None:
        """Test that zero quantity is rejected."""
        with pytest.raises(ValueError, match="positive"):
            OrderItem(
                id=1,
                order_id=1,
                product_id=1,
                quantity=0,
                unit_price_cents=1999,
            )

    def test_negative_quantity_rejected(self) -> None:
        """Test that negative quantity is rejected."""
        with pytest.raises(ValueError, match="positive"):
            OrderItem(
                id=1,
                order_id=1,
                product_id=1,
                quantity=-1,
                unit_price_cents=1999,
            )


class TestPaymentModel:
    """Tests for Payment model constraints."""

    def test_valid_payment(self) -> None:
        """Test creating a valid payment."""
        payment = Payment(
            id=1,
            order_id=1,
            amount_cents=5000,
            currency=Currency.USD,
            status=PaymentStatus.PENDING,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id="txn_123456",
        )
        assert payment.amount_cents == 5000

    def test_zero_amount_rejected(self) -> None:
        """Test that zero amount is rejected."""
        with pytest.raises(ValueError, match="positive"):
            Payment(
                id=1,
                order_id=1,
                amount_cents=0,
                currency=Currency.USD,
                status=PaymentStatus.PENDING,
                payment_method=PaymentMethod.CREDIT_CARD,
                transaction_id="txn_123456",
            )

    def test_negative_amount_rejected(self) -> None:
        """Test that negative amount is rejected."""
        with pytest.raises(ValueError, match="positive"):
            Payment(
                id=1,
                order_id=1,
                amount_cents=-100,
                currency=Currency.USD,
                status=PaymentStatus.PENDING,
                payment_method=PaymentMethod.CREDIT_CARD,
                transaction_id="txn_123456",
            )
